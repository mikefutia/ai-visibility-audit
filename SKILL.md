---
name: ai-visibility-audit
description: >
  Audit whether AI recommends a brand. Runs a category's buyer questions through Google
  AI Overview, ChatGPT, and Perplexity, detects if the brand is mentioned/cited, shows
  which competitors AI recommends instead, and scores overall AI visibility. Trigger on
  "run the ai visibility audit", "does AI recommend my brand", "am I showing up in
  ChatGPT / AI search", "AI search visibility", "GEO audit", "AEO audit".
allowed-tools: Bash(python3 *) Read Write
---

# AI Visibility Audit

When invoked, run this pipeline. Scripts are Python 3 **stdlib only**. Output → `./ai-visibility/`. It queries live AI engines, so a run takes **5–10 minutes** (more queries = longer) — tell the user that up front so the wait isn't a surprise.

**Ask the user two questions first (wait for answers):**
1. **What's your brand name and website?** (e.g. "Primally Pure — primallypure.com")
2. **What category are you in?** (e.g. "natural deodorant", "project management software") — used to generate the buyer questions people actually ask AI.

(Default market is US; default engines are Google AI Overview + ChatGPT + Perplexity.)

## 0 — Token check (and first-run setup)
Uses Apify. Token from `APIFY_TOKEN` env var, this skill's `.env`, or `./.env`. If missing, walk the user through it (don't just point at a file): get their token at console.apify.com/settings/integrations → create `${CLAUDE_SKILL_DIR}/.env` with `APIFY_TOKEN=`, tell them to paste it into that file (never into chat), then continue.

## 1 — Generate the buyer questions
Write **20–25 real buyer-intent queries** for the category to `./ai-visibility/queries.txt` (one per line) — more queries = a truer visibility score and a fuller competitor leaderboard. If the user asks for more/fewer, follow that. Mix these shapes:
- `best {category}`, `best {category} for {use case}`, `top {category} brands`
- `most effective {category}`, `{category} reviews`, `is {brand} worth it`
- `{brand} vs {top competitor}`, `{category} for {specific audience}`
Make them the questions a real buyer would type into ChatGPT — not keywords.

## 2 — Run the audit
```
python3 ${CLAUDE_SKILL_DIR}/scripts/run_audit.py --brand "<brand>" --domain <domain> --queries-file ./ai-visibility/queries.txt --country us
```
Runs every query through Google AI Overview + ChatGPT + Perplexity, detects if the brand is **mentioned** (named in the answer) or **cited** (its domain in the sources), and writes `./ai-visibility/audit.json` + `.csv`. (Add `--engines aioverview,chatgpt` to go faster/cheaper, or add `gemini`.)

## 3 — Mine (the analysis step)
Read `./ai-visibility/audit.json`. For each query + engine, read the AI `answer` and:
- **Extract the competitor brands the AI recommends** (the named brands in the answer). Build a **leaderboard** of who shows up most across all queries/engines — that's who's winning AI search in this category.
- Note **where the brand is invisible** (which engines/queries) and **what AI recommends instead** there.
- Write a one-line **verdict** (e.g. "Strong on Perplexity, nearly invisible on ChatGPT").
- Write 3–5 **fixes** grounded in the data (e.g. "ChatGPT pulls from Good Housekeeping / Byrdie roundups you're not in — get placed there").

Write `./ai-visibility/mined.json`:
```json
{ "stats": {"brand":"","category":"","overall_pct":0,"queries":0,
    "per_engine":{"aioverview":{"seen":0,"of":0},"chatgpt":{"seen":0,"of":0},"perplexity":{"seen":0,"of":0}}},
  "verdict":"",
  "competitors":[{"brand":"","count":0}],
  "queries":[{"query":"","aioverview":true,"chatgpt":false,"perplexity":true,"recommends_instead":"Native, Lume"}],
  "fixes":[""] }
```
(Carry the per-engine seen/of counts and overall_pct straight from audit.json's `summary`.)

## 4 — Render
```
python3 ${CLAUDE_SKILL_DIR}/scripts/render_dashboard.py
```
Writes `./ai-visibility/dashboard.html` (visibility score, per-engine bars, competitor leaderboard, per-query grid, fixes) and opens it.

## 5 — Report
The overall visibility %, the engine where they're weakest, the top 3 competitors AI recommends instead, and the #1 fix.

## Notes
- "Mentioned" (named in the answer) matters more than "cited" — being *recommended by name* is the goal.
- Runs are slow because AI engines are slow; ~12 queries × 3 engines ≈ a few minutes.
- Token setup is inline in step 0 — self-contained, no separate doc needed.
