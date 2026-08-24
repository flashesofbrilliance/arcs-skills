# arcs-skills

A Claude Code **plugin marketplace** for the ARCS / flashesofbrilliance family.
Each plugin installs one skill and references its own upstream repo (single
source of truth), so the skill repos stay canonical and this catalog just points
at them.

## Prerequisite

You need **Claude Code**, installed and updated:

```
npm install -g @anthropic-ai/claude-code
# or see docs.claude.com/claude-code
```

## Install (once)

```
# add the marketplace (accept the trust prompt when it appears)
/plugin marketplace add flashesofbrilliance/arcs-skills
# install a plugin
/plugin install rca@arcs
# verify (the plugin should be listed)
/plugin
```

Then run a skill with `/<plugin>:<skill>`, e.g. `/rca:rca`. Some skills (like
`resume-tailor`) trigger on describing the task, not a slash command: just say
what you want and attach your inputs.

## Skills in this marketplace

| Install | What it does | Upstream |
|---|---|---|
| `/plugin install resume-tailor@arcs` | Honest, ATS-safe resumes and cover letters, tailored to a role and graded by how checkable each claim is. | [resume-tailor-skill](https://github.com/flashesofbrilliance/resume-tailor-skill) · [site](https://resume-tailor.arcs.care) |
| `/plugin install rca@arcs` | On-demand root-cause analysis for a specific error: cause, not symptom. | [rca-skill](https://github.com/flashesofbrilliance/rca-skill) |
| `/plugin install state-sync@arcs` | Scaffolds a committed `snapshot.json` so sessions restore ground-truth state cheaply. | [state-sync-skill](https://github.com/flashesofbrilliance/state-sync-skill) |
| `/plugin install token-savings-bank@arcs` | Deliberate model-tier / batching / checkpointing on large or cost-metered tasks. | [token-savings-bank](https://github.com/flashesofbrilliance/token-savings-bank) |
| `/plugin install fix-toolbar-comments@arcs` | Resolve Vercel Toolbar feedback threads end to end (fix, deploy, resolve). | [fix-toolbar-comments-skill](https://github.com/flashesofbrilliance/fix-toolbar-comments-skill) |

## No plugin? Self-service DIY

Every skill's method is MIT and public. You do not need the marketplace:

- **Any Claude.** Skills like `resume-tailor` work from a plain prompt in Claude.ai or Claude Code. Describe the task and attach your inputs; the plugin just automates the full method every time, with nothing to paste.
- **Read it first.** Each upstream repo's `SKILL.md` is the whole method in the open. Read it before you install anything.
- **Run it yourself.** Clone the skill and use it without the marketplace:

```
git clone https://github.com/flashesofbrilliance/resume-tailor-skill
# then, in Claude Code from that folder:
#   "follow ./SKILL.md to tailor my resume for <job link>"
# or drop it into your project so it loads automatically:
cp -r resume-tailor-skill .claude/skills/resume-tailor
```

## If something's off

- **`/plugin` not recognized:** you're on an older Claude Code build. Update it (re-run the install command above), then retry.
- **Marketplace not found:** check the name (`flashesofbrilliance/arcs-skills`) and that you're online. It's a public repo.
- **A skill didn't trigger:** the trigger is describing the task, not a keyword. Describe it, or name the skill, e.g. `use resume-tailor`.
- **You're on Claude.ai, not Claude Code:** plugins are Claude Code only. Use the skill's paste-and-go prompt instead, same method, no install.

## Notes

- Plugins track each upstream repo's `main` branch, so improvements flow to
  installed users on `/plugin marketplace update`.
- Part of the ARCS family. The skills are open; the animating priors stay private.
