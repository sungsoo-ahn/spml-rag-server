# Research Project Template

A research repository designed for AI-assisted development workflows.

## Workflow

This repo is designed to be used with an AI coding agent (e.g., Claude Code). The typical workflow:

1. **Start a session**: Ask the AI to read `docs/start.txt` and everything mentioned in it
2. **Do research**: Talk to the AI to run experiments, write code, analyze results
3. **End a session**: Ask the AI to do `docs/closing_tasks.md`

This maintains reasonable context across conversations.

## Project Structure

| Folder | Purpose |
|--------|---------|
| `src/` | All Python source code lives here |
| `src/scripts/` | Entry point scripts that orchestrate experiments |
| `configs/` | YAML configuration files for experiments |
| `scripts/` | Minimal bash wrappers that call Python scripts |
| `data/` | Experiment outputs (gitignored) |
| `scratch/` | Temporary work directory (gitignored) |
| `resources/` | Reference materials: papers, external repos, docs (gitignored) |
| `docs/` | Documentation and development logs |

## Setup

```bash
uv venv
source .venv/bin/activate
uv sync
```

## Key Files

- `CLAUDE.md` - Development guidelines for the AI agent
- `docs/repo_usage.md` - Detailed development practices
- `docs/research_context.md` - Current research state and context