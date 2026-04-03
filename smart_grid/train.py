"""
Smart Grid RL Training Script
==============================

A standalone training loop that runs the SmartGridEnvironment *locally*
(no server needed) and trains a simple policy-gradient agent using only
numpy.  This serves as the baseline you can later swap for PPO / SAC via
stable-baselines3, CleanRL, or any other framework.

Usage:
    python -m smart_grid.train              # default 500 episodes
    python -m smart_grid.train --episodes 2000 --seed 42
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import numpy as np

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smart_grid.models import SmartGridAction, SmartGridObservation
from smart_grid.server.smart_grid_environment import SmartGridEnvironment, GridConfig


# ── observation → flat vector ───────────────────────────────────────────────

def obs_to_vec(obs: SmartGridObservation) -> np.ndarray:
    """Convert an observation to a flat float32 numpy array for the agent."""
    return np.array([
        obs.hour_of_day / 23.0,
        obs.day_of_year / 365.0,
        obs.solar_available / GridConfig.SOLAR_PEAK_MW,
        obs.wind_available / GridConfig.WIND_PEAK_MW,
        obs.demand / GridConfig.PEAK_DEMAND_MW,
        obs.battery_soc,
        obs.grid_buy_price / 150.0,   # rough normalisation
        obs.grid_sell_price / 150.0,
    ], dtype=np.float32)

OBS_DIM = 8
ACT_DIM = 4   # solar_dispatch, wind_dispatch, battery_action, grid_exchange


# ── simple linear policy ────────────────────────────────────────────────────

@dataclass
class LinearPolicy:
    """A tiny linear-Gaussian policy: μ = Wx + b, fixed σ."""
    W: np.ndarray = field(default_factory=lambda: np.zeros((ACT_DIM, OBS_DIM), dtype=np.float32))
    b: np.ndarray = field(default_factory=lambda: np.zeros(ACT_DIM, dtype=np.float32))
    log_std: np.ndarray = field(default_factory=lambda: np.full(ACT_DIM, -0.5, dtype=np.float32))

    def forward(self, x: np.ndarray) -> np.ndarray:
        return self.W @ x + self.b

    def sample(self, x: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
        mu = self.forward(x)
        std = np.exp(self.log_std)
        raw = mu + std * rng.standard_normal(ACT_DIM).astype(np.float32)
        return raw, mu

    def log_prob(self, x: np.ndarray, a: np.ndarray) -> float:
        mu = self.forward(x)
        std = np.exp(self.log_std)
        return float(-0.5 * np.sum(((a - mu) / std) ** 2 + 2 * self.log_std + np.log(2 * math.pi)))

    def get_params(self) -> np.ndarray:
        return np.concatenate([self.W.ravel(), self.b, self.log_std])

    def set_params(self, flat: np.ndarray) -> None:
        w_size = ACT_DIM * OBS_DIM
        self.W = flat[:w_size].reshape(ACT_DIM, OBS_DIM).copy()
        self.b = flat[w_size:w_size + ACT_DIM].copy()
        self.log_std = flat[w_size + ACT_DIM:].copy()


def action_from_raw(raw: np.ndarray) -> SmartGridAction:
    """Clamp raw policy output into valid action ranges."""
    s = float(np.clip(raw[0], 0, 1))
    w = float(np.clip(raw[1], 0, 1))
    ba = float(np.clip(raw[2], -1, 1))
    ge = float(np.clip(raw[3], -1, 1))
    return SmartGridAction(
        solar_dispatch=s,
        wind_dispatch=w,
        battery_action=ba,
        grid_exchange=ge,
    )


# ── REINFORCE training loop ────────────────────────────────────────────────

def run_episode(env: SmartGridEnvironment, policy: LinearPolicy, rng: np.random.Generator):
    obs = env.reset()
    states, actions_raw, rewards = [], [], []

    while True:
        x = obs_to_vec(obs)
        raw, _ = policy.sample(x, rng)
        act = action_from_raw(raw)

        obs = env.step(act)

        states.append(x)
        actions_raw.append(raw)
        rewards.append(obs.reward)

        if obs.done:
            break

    return states, actions_raw, rewards


def compute_returns(rewards: List[float], gamma: float = 0.99) -> np.ndarray:
    G = np.zeros(len(rewards), dtype=np.float32)
    running = 0.0
    for t in reversed(range(len(rewards))):
        running = rewards[t] + gamma * running
        G[t] = running
    # Normalise
    G = (G - G.mean()) / (G.std() + 1e-8)
    return G


def train(
    episodes: int = 500,
    lr: float = 3e-4,
    gamma: float = 0.99,
    seed: int = 0,
    log_every: int = 20,
    save_dir: str = "checkpoints",
):
    rng = np.random.default_rng(seed)
    env = SmartGridEnvironment()
    policy = LinearPolicy()

    # Initialise weights with small random values
    flat = rng.standard_normal(policy.get_params().shape).astype(np.float32) * 0.01
    policy.set_params(flat)

    best_return = -float("inf")
    history: list[dict] = []
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    print(f"{'ep':>6} | {'avg_R':>10} | {'cost':>10} | {'carbon':>10} | {'unmet':>10}")
    print("-" * 66)

    for ep in range(1, episodes + 1):
        states, actions, rewards = run_episode(env, policy, rng)
        returns = compute_returns(rewards, gamma)
        ep_return = sum(rewards)

        # REINFORCE gradient update
        grad = np.zeros_like(policy.get_params())
        for t, (x, a, G_t) in enumerate(zip(states, actions, returns)):
            # ∂ log π / ∂ θ  (for linear-Gaussian)
            mu = policy.forward(x)
            std = np.exp(policy.log_std)
            diff = (a - mu) / (std ** 2)
            # Gradient w.r.t. W: outer product
            dW = np.outer(diff, x).ravel()
            db = diff
            dlog_std = ((a - mu) ** 2 / (std ** 2) - 1)
            g = np.concatenate([dW, db, dlog_std])
            grad += G_t * g

        grad /= len(states)
        flat = policy.get_params() + lr * grad
        policy.set_params(flat)

        # Get last obs for episode stats
        last_obs_cost = -sum(rewards)  # approx — actual is tracked inside env
        record = {
            "episode": ep,
            "return": float(ep_return),
            "total_cost": float(env._total_cost),
            "total_carbon": float(env._total_carbon),
            "total_unmet": float(env._total_unmet),
            "steps": len(states),
        }
        history.append(record)

        if ep % log_every == 0 or ep == 1:
            avg_r = np.mean([h["return"] for h in history[-log_every:]])
            print(
                f"{ep:6d} | {avg_r:10.2f} | "
                f"{record['total_cost']:10.2f} | "
                f"{record['total_carbon']:10.4f} | "
                f"{record['total_unmet']:10.4f}"
            )

        if ep_return > best_return:
            best_return = ep_return
            np.save(save_path / "best_policy.npy", policy.get_params())

    # Save final
    np.save(save_path / "final_policy.npy", policy.get_params())
    with open(save_path / "training_history.json", "w") as f:
        json.dump(history, f, indent=2)

    print(f"\n[OK] Training complete. Best return: {best_return:.2f}")
    print(f"  Checkpoints saved to: {save_path.resolve()}")
    return policy, history


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Train Smart Grid RL agent")
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--log-every", type=int, default=20)
    parser.add_argument("--save-dir", type=str, default="checkpoints")
    args = parser.parse_args()

    train(
        episodes=args.episodes,
        lr=args.lr,
        gamma=args.gamma,
        seed=args.seed,
        log_every=args.log_every,
        save_dir=args.save_dir,
    )


if __name__ == "__main__":
    main()
