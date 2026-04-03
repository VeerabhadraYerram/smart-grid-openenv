# OpenEnv CLI Reference

OpenEnv (`openenv`) is an end-to-end framework for creating, deploying, and using isolated execution environments for agentic RL training.

## Installation
```bash
pip install openenv-core[core]
```

## Global Options
- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell.
- `--help`: Show the help message and exit.

---

## Commands

### `init`
Initialize a new OpenEnv environment from a template.
**Usage:** `openenv init [OPTIONS] ENV_NAME`
- `ENV_NAME`: Name of the environment to create (snake_case).
- `--output-dir`, `-o`: Output directory (defaults to CWD).

### `validate`
Validate environment structure and deployment readiness.
**Usage:** `openenv validate [OPTIONS] [TARGET]`
- `TARGET`: Path to directory or a running OpenEnv URL (e.g., http://localhost:8000).
- `--url`: Validate a running OpenEnv server by base URL.
- `--json`: Output local validation report as JSON.
- `--timeout`: HTTP timeout in seconds for runtime validation (default: 5.0).
- `--verbose`, `-v`: Show detailed information.

### `build`
Build Docker images for OpenEnv environments.
**Usage:** `openenv build [OPTIONS] [ENV_PATH]`
- `ENV_PATH`: Path to the environment directory.
- `--tag`, `-t`: Docker image tag (default: `openenv-<env_name>`).
- `--context`, `-c`: Build context path (default: `<env_path>/server`).
- `--dockerfile`, `-f`: Path to Dockerfile (default: `<context>/Dockerfile`).
- `--no-cache`: Build without using cache.
- `--build-arg`: Build arguments (format: KEY=VALUE).

### `push`
Push an OpenEnv environment to Hugging Face Spaces or a custom registry.
**Usage:** `openenv push [OPTIONS] [DIRECTORY]`
- `DIRECTORY`: Directory containing the OpenEnv environment.
- `--repo-id`, `-r`: Repository ID in format `username/repo-name`.
- `--base-image`, `-b`: Base Docker image to use.
- `--interface` / `--no-interface`: Enable/Disable web interface (Gradio).
- `--registry`: Custom registry URL (e.g., docker.io/username).
- `--private`: Deploy the space as private.
- `--create-pr`: Create a Pull Request instead of pushing to the default branch.
- `--exclude`: Additional ignore file for uploads.

### `serve`
Serve environments locally.
**Usage:** `openenv serve [OPTIONS] [ENV_PATH]`
- `ENV_PATH`: Path to the environment directory.
- `--port`, `-p`: Port to serve on (default: 8000).
- `--host`: Host to bind to (default: 0.0.0.0).
- `--reload`: Enable auto-reload on code changes.

### `fork`
Fork (duplicate) a Hugging Face Space to your account.
**Usage:** `openenv fork [OPTIONS] SOURCE_SPACE`
- `SOURCE_SPACE`: Source Space ID in format `owner/space-name`.
- `--repo-id`, `-r`: Target repo ID for the fork.
- `--private`: Create the forked Space as private.
- `--set-env`, `-e`: Set Space variable (public).
- `--set-secret`, `-s`: Set Space secret.
- `--hardware`, `-H`: Request hardware (e.g., t4-medium, cpu-basic).

### `skills`
Manage OpenEnv skills for AI assistants (like me!).
**Usage:** `openenv skills [OPTIONS] COMMAND [ARGS]...`
- `preview`: Print generated SKILL.md content.
- `add`: Install OpenEnv CLI skill for AI assistants.
  - `--claude`: Install for Claude.
  - `--codex`: Install for Codex.
  - `--cursor`: Install for Cursor.
  - `--opencode`: Install for OpenCode.
  - `--global`, `-g`: Install globally.
  - `--dest`: Custom destination path.
  - `--force`: Overwrite existing skills.
