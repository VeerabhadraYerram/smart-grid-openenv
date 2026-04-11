"""
FastAPI Server Entry Point
===========================
Exposes the SmartGridEnv over HTTP/WebSocket for the OpenEnv CLI and agents.
"""

import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# Force web interface to be enabled
os.environ["ENABLE_WEB_INTERFACE"] = "true"

from openenv.core.env_server.http_server import create_app
from .grid_env import SmartGridEnv
from models import Action, Observation

import gradio as gr

def custom_gradio_ui(web_manager, action_fields, metadata, is_chat_env, title, quick_start_md):
    """Professional Control Room dashboard for human judges."""

    with gr.Blocks(css="""
        .freq-green { color: #22c55e; font-weight: bold; font-size: 1.3em; }
        .freq-yellow { color: #eab308; font-weight: bold; font-size: 1.3em; }
        .freq-red { color: #ef4444; font-weight: bold; font-size: 1.3em; }
        .metric-box { text-align: center; padding: 8px; border-radius: 8px; background: #1e293b; }
        .grade-green { color: #22c55e; font-size: 1.5em; font-weight: bold; }
        .grade-yellow { color: #eab308; font-size: 1.5em; font-weight: bold; }
        .grade-red { color: #ef4444; font-size: 1.5em; font-weight: bold; }
    """) as custom:
        # ── Header ──
        gr.Markdown("""
# ⚡ Smart Grid Control Room
**The first demand response RL environment designed for LLM agents.**  
Select a scenario, click Reset, then Step through the crisis. Watch the AI situation report update in real-time.
        """)
        
        # ── Live Metrics Dashboard ──
        with gr.Row(equal_height=True):
            freq_display = gr.Markdown(
                value="**🔵 Frequency:** -- Hz",
                elem_classes=["metric-box"]
            )
            battery_display = gr.Markdown(
                value="**🔋 Battery:** --%",
                elem_classes=["metric-box"]
            )
            step_display = gr.Markdown(
                value="**📊 Step:** 0 / --",
                elem_classes=["metric-box"]
            )
            weather_display = gr.Markdown(
                value="**🌤️ Weather:** --",
                elem_classes=["metric-box"]
            )

        gr.Markdown("---")

        with gr.Row():
            # ── LEFT: Situation Report ──
            with gr.Column(scale=3):
                gr.Markdown("### 📋 Situation Report")
                situation_md = gr.Markdown(
                    "*(Select a scenario and click **Initialize** to begin)*",
                    elem_id="situation-report",
                    line_breaks=True
                )
                
                # ── Grade display (hidden until episode ends) ──
                grade_display = gr.Markdown(visible=False)
            
            # ── RIGHT: Controls ──
            with gr.Column(scale=1):
                gr.Markdown("### 🎯 Scenario")
                task_choice = gr.Dropdown(
                    choices=[
                        ("⚡ Peak Survival (Easy — 12 steps)", "peak_survival"),
                        ("📊 Daily Balance (Medium — 24 steps)", "daily_balance"),
                        ("🔥 Extreme Heatwave (Hard — 48 steps)", "extreme_event"),
                        ("🌧️ Monsoon Crisis (Medium-Hard — 24 steps)", "monsoon_crisis"),
                        ("🌱 Renewable Transition (Expert — 72 steps)", "renewable_transition"),
                    ],
                    value="peak_survival",
                    label="Select Task"
                )
                init_btn = gr.Button("🔄 Initialize / Reset", variant="secondary", size="lg")
                
                gr.Markdown("---")
                gr.Markdown("### ⚙️ Agent Actions")
                curtail_input = gr.Code(
                    label="Curtailments (JSON)",
                    language="json",
                    value='{\n  "steel_plant": 0.0\n}'
                )
                bat_action = gr.Radio(
                    ["idle", "charge", "discharge"],
                    value="idle",
                    label="Battery Action"
                )
                bat_mw = gr.Slider(0, 25, value=0, step=1, label="Battery MW")
                
                with gr.Row():
                    step_btn = gr.Button("▶ Step (1 Hour)", variant="primary", size="lg")
                    auto_btn = gr.Button("⏩ Auto ×5", variant="secondary")
                
                gr.Markdown("---")
                status_box = gr.Textbox(label="System Log", value="Ready. Select a scenario and click Initialize.", lines=2)

        # ── Handlers ──
        all_outputs = [status_box, situation_md, freq_display, battery_display, step_display, weather_display, grade_display]

        def _format_metrics(obs):
            """Format live metric displays from observation."""
            freq = obs.grid_frequency_hz
            if freq >= 49.5:
                freq_md = f"**🟢 Frequency:** {freq:.2f} Hz"
            elif freq >= 49.2:
                freq_md = f"**🟡 Frequency:** {freq:.2f} Hz"
            else:
                freq_md = f"**🔴 Frequency:** {freq:.2f} Hz"
            
            soc = obs.battery_soc_pct
            if soc >= 50:
                bat_md = f"**🔋 Battery:** {soc:.0f}%"
            elif soc >= 20:
                bat_md = f"**🪫 Battery:** {soc:.0f}%"
            else:
                bat_md = f"**⚠️ Battery:** {soc:.0f}%"
            
            step_md = f"**📊 Step:** {obs.step_number}"
            
            weather_emojis = {"clear": "☀️", "cloudy": "☁️", "heatwave": "🔥", "storm": "⛈️", "monsoon": "🌧️"}
            w_emoji = weather_emojis.get(obs.weather, "🌤️")
            weather_md = f"**{w_emoji} Weather:** {obs.weather.title()} ({obs.temperature_c:.0f}°C)"
            
            return freq_md, bat_md, step_md, weather_md

        async def do_init(task):
            try:
                import asyncio
                from openenv.core.env_server.serialization import serialize_observation
                loop = asyncio.get_event_loop()
                obs = await loop.run_in_executor(None, lambda: web_manager.env.reset(task_name=task))
                # Sync web manager
                web_manager.episode_state.episode_id = web_manager.env.state.episode_id
                web_manager.episode_state.step_count = 0
                web_manager.episode_state.current_observation = serialize_observation(obs)["observation"]
                web_manager.episode_state.action_logs = []
                web_manager.episode_state.is_reset = True
                
                report = obs.situation_report
                freq_md, bat_md, step_md, weather_md = _format_metrics(obs)
                
                task_labels = {
                    "peak_survival": "Peak Survival",
                    "daily_balance": "Daily Balance", 
                    "extreme_event": "Extreme Heatwave",
                    "monsoon_crisis": "Monsoon Crisis",
                    "renewable_transition": "Renewable Transition"
                }
                label = task_labels.get(task, task)
                
                return (
                    f"✅ Loaded '{label}'. Click Step to begin.",
                    report,
                    freq_md, bat_md, step_md, weather_md,
                    gr.update(visible=False)
                )
            except Exception as e:
                return (f"❌ Error: {str(e)}", "Error loading.", 
                        "**🔵 Frequency:** -- Hz", "**🔋 Battery:** --%",
                        "**📊 Step:** 0 / --", "**🌤️ Weather:** --",
                        gr.update(visible=False))

        async def do_step(curtails_json, b_action, b_mw):
            try:
                import json
                import asyncio
                from openenv.core.env_server.serialization import serialize_observation
                
                c_dict = json.loads(curtails_json) if curtails_json.strip() else {}
                action = Action(curtailments=c_dict, battery_action=b_action, battery_mw=b_mw)
                
                loop = asyncio.get_event_loop()
                obs = await loop.run_in_executor(None, lambda: web_manager.env.step(action))
                
                # Sync web manager
                web_manager.episode_state.step_count = web_manager.env.state.step_count
                web_manager.episode_state.current_observation = serialize_observation(obs)["observation"]
                
                report = obs.situation_report
                freq_md, bat_md, step_md, weather_md = _format_metrics(obs)
                status = f"Step {obs.step_number} | Reward: {obs.reward:.3f} | Freq: {obs.grid_frequency_hz:.2f}Hz"
                
                grade_update = gr.update(visible=False)
                if obs.done:
                    final_grade = await loop.run_in_executor(None, lambda: web_manager.env.grade())
                    if final_grade >= 0.5:
                        grade_md = f"## ✅ Episode Complete — Grade: **{final_grade:.4f}**\n*Great performance!*"
                    elif final_grade >= 0.2:
                        grade_md = f"## ⚠️ Episode Complete — Grade: **{final_grade:.4f}**\n*Passable but room for improvement.*"
                    else:
                        grade_md = f"## ❌ Episode Complete — Grade: **{final_grade:.4f}**\n*Poor performance. The grid suffered.*"
                    grade_update = gr.update(value=grade_md, visible=True)
                    status = f"🛑 DONE | Final Grade: {final_grade:.4f}"
                    
                return status, report, freq_md, bat_md, step_md, weather_md, grade_update
            except Exception as e:
                return (f"❌ Error: {str(e)}", "Error.",
                        "**🔴 Frequency:** ERR", "**🔋 Battery:** ERR",
                        "**📊 Step:** ERR", "**🌤️ Weather:** ERR",
                        gr.update(visible=False))

        async def do_auto_step(curtails_json, b_action, b_mw):
            """Run 5 steps automatically so judges don't have to click 50 times."""
            result = None
            for _ in range(5):
                result = await do_step(curtails_json, b_action, b_mw)
                # If episode ended, stop
                if "DONE" in str(result[0]):
                    break
            return result

        init_btn.click(fn=do_init, inputs=[task_choice], outputs=all_outputs)
        step_btn.click(fn=do_step, inputs=[curtail_input, bat_action, bat_mw], outputs=all_outputs)
        auto_btn.click(fn=do_auto_step, inputs=[curtail_input, bat_action, bat_mw], outputs=all_outputs)
        
    return custom


# Create the FastAPI app using the OpenEnv helper
# This automatically creates /reset, /step, /state, /ws, and /web endpoints
app = create_app(
    SmartGridEnv,
    Action,
    Observation,
    env_name="smart-grid-demand-response",
    max_concurrent_envs=10,  # Allow multiple parallel sessions for training
    gradio_builder=custom_gradio_ui,
)


@app.get("/")
async def root_redirect():
    """Redirect root to the interactive web interface."""
    return RedirectResponse(url="/web/")


def main():
    """Entry point for the server."""
    import uvicorn
    import sys
    
    port = int(os.environ.get("PORT", 7860))
    if "--port" in sys.argv:
        p_idx = sys.argv.index("--port")
        if p_idx + 1 < len(sys.argv):
            port = int(sys.argv[p_idx + 1])
            
    print(f"--- Starting Smart Grid Demand Response Server on port {port} ---")
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
