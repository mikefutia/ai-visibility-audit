#!/usr/bin/env python3
"""
AI Visibility Audit — run a category's buyer questions through Google AI Overview,
ChatGPT, and Perplexity, and detect whether a brand is recommended (vs its competitors).
Python 3 stdlib only. Token: APIFY_TOKEN from env var, <skill>/.env, or ./.env.

Usage:
  python3 run_audit.py --brand "Primally Pure" --domain primallypure.com --queries-file queries.txt [--country us] [--engines aiOverview,chatgpt,perplexity]

Output (./ai-visibility/): audit.json, audit.csv
"""
import os, sys, json, csv, time, argparse
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.getcwd(), "ai-visibility")
ACTOR = "nFJndFXA5zjCTuudP"  # apify/google-search-scraper (AI Overview + ChatGPT + Perplexity add-ons)


def load_token():
    t = os.environ.get("APIFY_TOKEN", "").strip()
    if t:
        return t
    for p in (os.path.join(SKILL_DIR, ".env"), os.path.join(os.getcwd(), ".env")):
        if os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if line.startswith("APIFY_TOKEN="):
                    v = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
    return ""


TOKEN = load_token()


def _get(url):
    try:
        with urlopen(url, timeout=90) as r:
            return json.loads(r.read().decode("utf-8"))
    except HTTPError as e:
        raise SystemExit(f"Apify HTTP {e.code}: {e.read().decode('utf-8')[:200]}")
    except URLError as e:
        raise SystemExit(f"network error: {e.reason}")


def run_actor(queries, country, engines):
    inp = {"queries": "\n".join(queries), "maxPagesPerQuery": 1, "countryCode": country}
    if "aioverview" in engines:
        inp["aiOverview"] = {"scrapeFullAiOverview": True}
    if "chatgpt" in engines:
        inp["chatGptSearch"] = {"enableChatGpt": True}
    if "perplexity" in engines:
        inp["perplexitySearch"] = {"enablePerplexity": True}
    if "gemini" in engines:
        inp["geminiSearch"] = {"enableGemini": True}
    body = json.dumps(inp).encode("utf-8")
    req = Request(f"https://api.apify.com/v2/acts/{ACTOR}/runs?token={TOKEN}",
                  data=body, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=60) as r:
            run = json.loads(r.read().decode("utf-8"))["data"]
    except HTTPError as e:
        raise SystemExit(f"Apify start error {e.code}: {e.read().decode('utf-8')[:200]}")
    rid, dsid, st = run["id"], run["defaultDatasetId"], None
    print(f"Asking {len(queries)} buyer questions across {', '.join(engines)} (AI engines are slow — 5-10 min)...")
    for _ in range(400):  # up to ~20 min for larger query sets
        time.sleep(3)
        st = _get(f"https://api.apify.com/v2/actor-runs/{rid}?token={TOKEN}")["data"]["status"]
        if st in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
    if st != "SUCCEEDED":
        raise SystemExit(f"Apify run ended: {st}")
    return _get(f"https://api.apify.com/v2/datasets/{dsid}/items?token={TOKEN}&clean=true")


def domain_of(url):
    try:
        d = urlparse(url).netloc.lower()
        return d[4:] if d.startswith("www.") else d
    except Exception:
        return ""


ENGINE_FIELDS = {  # engine key -> (result field, source field)
    "aioverview": ("aiOverview", None),
    "chatgpt": ("chatGptSearchResult", None),
    "perplexity": ("perplexitySearchResult", None),
    "gemini": ("geminiSearchResult", None),
}


def parse(items, brand, domain, engines):
    bl = brand.lower()
    dl = (domain or "").lower().replace("www.", "")
    per_query = []
    eng_counts = {e: {"asked": 0, "seen": 0} for e in engines}
    for it in items:
        q = (it.get("searchQuery") or {}).get("term", "")
        row = {"query": q, "engines": {}}
        for e in engines:
            fld = ENGINE_FIELDS[e][0]
            block = it.get(fld) or {}
            text = block.get("content") or block.get("text") or ""
            if not text:
                continue
            eng_counts[e]["asked"] += 1
            srcs = block.get("sources") or []
            src_domains = sorted({domain_of(s.get("url", "")) for s in srcs if s.get("url")} - {""})
            mentioned = bl in text.lower()
            cited = bool(dl) and any(dl in (s.get("url", "") or "").lower() for s in srcs)
            if mentioned or cited:
                eng_counts[e]["seen"] += 1
            row["engines"][e] = {"mentioned": mentioned, "cited": cited,
                                 "answer": text[:700], "source_domains": src_domains[:12]}
        if row["engines"]:
            per_query.append(row)
    summary = {"brand": brand, "domain": domain,
               "per_engine": {e: {"visible_in": eng_counts[e]["seen"], "of": eng_counts[e]["asked"]} for e in engines}}
    total_asked = sum(c["asked"] for c in eng_counts.values())
    total_seen = sum(c["seen"] for c in eng_counts.values())
    summary["overall_visibility_pct"] = round(100 * total_seen / total_asked) if total_asked else 0
    return per_query, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("--domain", default="")
    ap.add_argument("--queries-file", required=True)
    ap.add_argument("--country", default="us")
    ap.add_argument("--engines", default="aioverview,chatgpt,perplexity")
    a = ap.parse_args()
    if not TOKEN:
        sys.exit("APIFY_TOKEN not set — add it to this skill's .env (see PLAYBOOK.md).")
    engines = [e.strip().lower() for e in a.engines.split(",") if e.strip()]
    queries = [q.strip() for q in open(a.queries_file, encoding="utf-8") if q.strip()]
    if not queries:
        sys.exit("No queries found in --queries-file.")

    items = run_actor(queries, a.country, engines)
    per_query, summary = parse(items, a.brand, a.domain, engines)

    os.makedirs(OUT, exist_ok=True)
    json.dump({"summary": summary, "queries": per_query},
              open(os.path.join(OUT, "audit.json"), "w"), indent=2)
    with open(os.path.join(OUT, "audit.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["query", "engine", "mentioned", "cited"])
        for r in per_query:
            for e, d in r["engines"].items():
                w.writerow([r["query"], e, d["mentioned"], d["cited"]])

    print(f"\nOK  {a.brand} visibility: {summary['overall_visibility_pct']}% across {len(per_query)} queries → {OUT}/audit.json")
    for e in engines:
        pe = summary["per_engine"][e]
        print(f"  {e:12} seen in {pe['visible_in']}/{pe['of']} answers")


if __name__ == "__main__":
    main()
