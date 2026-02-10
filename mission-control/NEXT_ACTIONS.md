# Next Actions: AI Empire

Sorted by Priority: **Revenue > Stability > Scaling**

## Revenue (Immediate)

1. **[Urgent] Outreach Sprint**: Send the first 20 DMs using `docs/outreach_dm.md`. Goal: 1 discovery call within 48h.
2. **[Urgent] Offer Polish**: Turn `docs/offer.md` into a PDF or Notion page to send to interested leads.
3. **[High] Demo Setup**: Record a 2-min loom showing your "Mission Control" dashboard as a proof of competence.

## Stability (Core)

4. **[High] Docker Fix**: Investigate why Docker is down (`failed to connect`). This blocks containerized deployments.
2. **[Medium] Auto-Start**: Configure `launchd` to automatically run `n8n` and `ollama` on boot, instead of manual starts.
3. **[Medium] Backup**: Set up a cron job to backup `registry/services.yaml` and `docs/` to a cloud drive (or git repo).
4. **[Low] Secret Management**: Move any hardcoded keys (if any) from scripts to a `.env` file (currently none detected in new scripts, but check legacy).

## Scaling (Growth)

8. **[Future] Orchestrator**: Expand `mc_status.sh` to actually *fix* broken services (auto-restart) instead of just reporting.
2. **[Future] Public Dashboard**: Securely expose a version of `dashboard/index.html` to clients (auth required).
3. **[Future] Agent Swarm**: Reactivate `kimi_mega_swarm.py` once Docker is stable, to run tasks in parallel containers.
