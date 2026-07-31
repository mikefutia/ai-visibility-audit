# AI Visibility Audit (Claude skill)

When people ask AI for the best product in your category, does it recommend **you** — or your
competitors? This skill runs your category's buyer questions through **Google AI Overview,
ChatGPT, and Perplexity**, detects whether your brand is named/cited, shows **who AI recommends
instead**, and scores your overall AI visibility — in a dashboard. Python stdlib only; one key (Apify).

## Install

**Claude Code**
```bash
git clone https://github.com/mikefutia/ai-visibility-audit.git ~/.claude/skills/ai-visibility-audit
```

**Claude Desktop**
1. Download this repo as a ZIP (**Code → Download ZIP**).
2. Settings → Capabilities → Skills → **Upload skill** → drop the zip.

Then do the one-time token setup: follow **PLAYBOOK.md** (an Apify API token in a `.env`).
Copy `.env.example` to `.env` and paste your token there — `.env` is gitignored, so it stays local.

## Use
> **run the ai visibility audit**

It asks two questions — your **brand + website** and your **category** — then generates the
buyer questions, queries the AI engines, and opens a dashboard with your visibility score,
per-engine breakdown, the competitor leaderboard, and how to fix the gaps.
Output lands in `./ai-visibility/`.

## What's inside
```
ai-visibility-audit/
├── SKILL.md                 the runbook Claude follows
├── PLAYBOOK.md              one-time Apify token setup
├── .env.example             copy to .env, add your Apify token
├── .gitignore               keeps .env and run output out of git
└── scripts/
    ├── run_audit.py         queries the AI engines, detects brand presence (Apify, stdlib)
    └── render_dashboard.py  renders the dark dashboard (stdlib)
```

## Notes
- Being **named in the answer** is the goal (that's a recommendation) — stronger than just being cited in the sources.
- Runs take a few minutes (AI engines are slow). ~$0.30–0.60 per audit.
- Requires an Apify token (PLAYBOOK.md) + Python 3.
