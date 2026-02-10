# Inventory Summary

## Overview

- **Date**: 2026-02-10
- **System**: macOS (Darwin 25.2.0)
- **Docker**: DOWN / Not Accessible
- **Orchestration**: Launchd (native macOS), manual Python scripts.

## Active Services

| Service | Type | Port | Status | PID | Start Method |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **n8n** | Process (Node) | 5678 | UP | 24350 | Manual / Launchd? |
| **Ollama** | Process (App) | 11434 | UP | 72309 | App / Launchd |
| **Redis** | Process (Brew) | 6379 | UP | 1154, 40748 | Brew Service |
| **Postgres** | Process (Brew) | 5432 | UP | 1166 | Brew Service |
| **Stripe Webhook** | Process (Python) | 8080 | UP | 18360 | Manual |
| **Server.py** | Process (Python) | 8090 | UP | 29744 | Manual |
| **Kimi Swarm** | Process (Python) | N/A | UP (Dry Run) | 55515 | Manual |

## Issues / Warnings

- **Docker** is not running.
- **AI Empire Launch Agents** (`com.ai-empire.autopipeline`, `n8n`, `autonomy`) are exiting with code 78 (Configuration Error).
- **Homebrew Ollama** (`homebrew.mxcl.ollama`) exited with code 1 (Potential conflict with Ollama.app).

## Observations

- Many services are running as manual background processes or via `brew services`.
- A dry-run of `kimi_mega_swarm.py` is active and consuming CPU.
