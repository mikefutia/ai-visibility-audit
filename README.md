# AI Visibility Audit (Claude skill)

By **[Mike Futia](https://www.skool.com/scale-ai/about)** · more Claude Code systems like this inside **[SCALE AI](https://www.skool.com/scale-ai/about)**

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

## Example run

Run against **HexClad** (24 buyer questions, US, July 2026):

| | Result |
|---|---|
| Overall visibility | **28%** |
| Queries containing "HexClad" | **100%** (12/12) |
| Queries that don't name the brand | **12%** (7/59) |
| `hexclad.com` cited as a source | 4 of 71 answers |
| Named most instead | All-Clad, Tramontina, GreenPan |

A brand that spends heavily on ads was named every time a buyer already knew it, and almost never in the
questions that *start* a purchase — which is the gap this skill is built to find.

## Who built this

Made by **Mike Futia**.

I build production-grade Claude Code systems for ecommerce brands, creative agencies, and performance
marketers, and I drop new workflows like this one every week inside my community.

**[Join 600+ brands and agencies in SCALE AI →](https://www.skool.com/scale-ai/about)**
