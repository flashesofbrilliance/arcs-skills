# arcs-skills

A Claude Code **plugin marketplace** for the ARCS / flashesofbrilliance family.
Each plugin installs one skill and references its own upstream repo (single
source of truth) — so the skill repos stay canonical and this catalog just points
at them.

## Use it

```
/plugin marketplace add flashesofbrilliance/arcs-skills
/plugin install rca@arcs
```

Then run a skill with `/<plugin>:<skill>`, e.g. `/rca:rca`.

## Skills in this marketplace

| Install | What it does | Upstream |
|---|---|---|
| `/plugin install rca@arcs` | On-demand root-cause analysis for a specific error — cause, not symptom. | [rca-skill](https://github.com/flashesofbrilliance/rca-skill) |
| `/plugin install state-sync@arcs` | Scaffolds a committed `snapshot.json` so sessions restore ground-truth state cheaply. | [state-sync-skill](https://github.com/flashesofbrilliance/state-sync-skill) |
| `/plugin install token-savings-bank@arcs` | Deliberate model-tier / batching / checkpointing on large or cost-metered tasks. | [token-savings-bank](https://github.com/flashesofbrilliance/token-savings-bank) |
| `/plugin install fix-toolbar-comments@arcs` | Resolve Vercel Toolbar feedback threads end to end (fix → deploy → resolve). | [fix-toolbar-comments-skill](https://github.com/flashesofbrilliance/fix-toolbar-comments-skill) |

## Notes

- Plugins track each upstream repo's `main` branch, so improvements flow to
  installed users on `/plugin marketplace update`.
- Part of the ARCS family. The skills are open; the animating priors stay private.
