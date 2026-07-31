#!/usr/bin/env python3
"""
Render ./ai-visibility/mined.json -> ./ai-visibility/dashboard.html (dark, stdlib).

mined.json (written by Claude after reading audit.json + extracting competitors):
{
  "stats": {"brand":"", "category":"", "overall_pct":56, "queries":12,
            "per_engine": {"aioverview":{"seen":8,"of":12},"chatgpt":{"seen":2,"of":12},"perplexity":{"seen":10,"of":12}}},
  "verdict": "One-line read on where the brand stands.",
  "competitors": [{"brand":"Native","count":9}, ...],           // who AI recommends most, across all queries
  "queries": [{"query":"best natural deodorant","aioverview":true,"chatgpt":false,"perplexity":true,
               "recommends_instead":"Native, Lume, Salt & Stone"}],
  "fixes": ["Get cited on the roundup sites ChatGPT pulls from (Good Housekeeping...).", ...]
}
"""
import os, sys, json, webbrowser

OUT = os.path.join(os.getcwd(), "ai-visibility")
SRC = os.path.join(OUT, "mined.json")
ENGINE_LABEL = {"aioverview": "Google AI Overview", "chatgpt": "ChatGPT", "perplexity": "Perplexity", "gemini": "Gemini"}

TEMPLATE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>AI Visibility Audit</title>
<style>
:root{--bg:#0a0b0f;--panel:#13151c;--panel2:#181b24;--line:#262b38;--ink:#eef0f6;--muted:#969cad;--accent:#6c8cff;--accent2:#a06cff;--good:#54d1a0;--bad:#ff6b6b;--warn:#ffb86b;--chip:#1f2430}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(1200px 600px at 70% -10%,#1a1430 0,transparent 60%),var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:40px 22px 90px}
.eyebrow{letter-spacing:.14em;text-transform:uppercase;font-size:11px;color:var(--accent);font-weight:700;margin:0 0 8px}
h1{font-size:30px;margin:0 0 6px;letter-spacing:-.02em;background:linear-gradient(90deg,#fff,#b9c2ff);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.verdict{color:var(--ink);margin:0 0 24px;font-size:15px;background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:10px;padding:12px 16px}
.grid{display:grid;grid-template-columns:200px 1fr;gap:22px;align-items:start}
.big{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:16px;padding:20px;text-align:center}
.big .n{font-size:46px;font-weight:800;line-height:1}
.big .l{font-size:12px;color:var(--muted);margin-top:4px}
h2{font-size:15px;margin:0 0 12px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.bar{display:flex;align-items:center;gap:10px;margin:0 0 9px}
.bar .name{width:150px;font-size:13.5px}
.track{flex:1;height:14px;background:var(--chip);border-radius:8px;overflow:hidden}
.fill{height:100%;border-radius:8px;background:linear-gradient(90deg,var(--accent),var(--accent2))}
.bar .v{width:52px;text-align:right;font-size:12px;color:var(--muted)}
.comp{display:flex;align-items:center;gap:10px;margin:0 0 8px}
.comp .rank{color:var(--muted);width:20px}
.comp .name{width:170px;font-weight:600}
.comp .ct{flex:1;height:12px;background:var(--chip);border-radius:6px;overflow:hidden}
.comp .ct span{display:block;height:100%;background:linear-gradient(90deg,#ff7a7a,#a06cff)}
table{width:100%;border-collapse:collapse;margin-top:6px;font-size:13.5px}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:600;font-size:12px}
td.q{max-width:280px}
.yes{color:var(--good);font-weight:700}.no{color:var(--bad);font-weight:700}
.inst{color:var(--muted);font-size:12.5px}
.sec{margin-top:34px}
.fix{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:11px 14px;margin:0 0 9px;font-size:13.5px}
footer{color:var(--muted);font-size:12px;border-top:1px solid var(--line);padding-top:18px;margin-top:36px}
</style></head><body><div class="wrap">
<p class="eyebrow" id="eyebrow">AI Visibility Audit</p>
<h1 id="title">Does AI recommend you?</h1>
<div class="verdict" id="verdict"></div>
<div class="grid">
  <div class="big"><div class="n" id="pct">0%</div><div class="l">of AI answers mention you</div></div>
  <div><h2>Visibility by engine</h2><div id="engines"></div></div>
</div>
<div class="sec"><h2 id="comp-h">Who AI recommends instead of you</h2><div id="competitors"></div></div>
<div class="sec"><h2>Every query — are you in the answer?</h2>
  <table><thead><tr><th class="q">Buyer question</th><th id="th">engines</th><th>AI recommends instead</th></tr></thead>
  <tbody id="rows"></tbody></table></div>
<div class="sec" id="fixes-sec"><h2>How to fix it</h2><div id="fixes"></div></div>
<footer>ai-visibility-audit · Google Search Scraper (AI Overview + ChatGPT + Perplexity) + Claude. Verbatim AI answers, nothing invented.</footer>
</div>
<script>
const M=__MINED__;
const esc=s=>String(s==null?"":s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const EL={aioverview:"Google AI Overview",chatgpt:"ChatGPT",perplexity:"Perplexity",gemini:"Gemini"};
const S=M.stats||{};
document.getElementById('eyebrow').textContent=`AI Visibility Audit · ${esc(S.brand||"")}`;
document.getElementById('title').textContent=`Does AI recommend ${esc(S.brand||"you")}?`;
document.getElementById('verdict').textContent=M.verdict||"";
document.getElementById('pct').textContent=(S.overall_pct||0)+"%";
const engs=Object.keys(S.per_engine||{});
document.getElementById('engines').innerHTML=engs.map(e=>{const p=S.per_engine[e];const pct=p.of?Math.round(100*p.seen/p.of):0;
  return `<div class="bar"><span class="name">${esc(EL[e]||e)}</span><div class="track"><div class="fill" style="width:${pct}%"></div></div><span class="v">${p.seen}/${p.of}</span></div>`}).join('');
const comps=M.competitors||[];const cmax=Math.max(1,...comps.map(c=>c.count||0));
document.getElementById('competitors').innerHTML=comps.slice(0,10).map((c,i)=>
  `<div class="comp"><span class="rank">${i+1}</span><span class="name">${esc(c.brand)}</span><div class="ct"><span style="width:${Math.round(100*(c.count||0)/cmax)}%"></span></div><span class="v" style="width:60px;text-align:right;color:var(--muted);font-size:12px">${c.count}×</span></div>`).join('');
document.getElementById('rows').innerHTML=(M.queries||[]).map(q=>{
  const cell=v=>v===true?'<span class="yes">✓</span>':v===false?'<span class="no">✗</span>':'<span class="inst">–</span>';
  const cells=engs.map(e=>cell(q[e])).join(' &nbsp; ');
  return `<tr><td class="q">${esc(q.query)}</td><td>${cells}</td><td class="inst">${esc(q.recommends_instead||"")}</td></tr>`}).join('');
document.getElementById('th').innerHTML=engs.map(e=>esc((EL[e]||e).split(' ')[0])).join(' / ');
if((M.fixes||[]).length) document.getElementById('fixes').innerHTML=M.fixes.map(f=>`<div class="fix">→ ${esc(f)}</div>`).join('');
else document.getElementById('fixes-sec').style.display='none';
</script></body></html>"""


def main():
    if not os.path.exists(SRC):
        sys.exit(f"{SRC} not found. Run the mine step first (write mined.json).")
    m = json.load(open(SRC))
    html = TEMPLATE.replace("__MINED__", json.dumps(m))
    out = os.path.join(OUT, "dashboard.html")
    open(out, "w").write(html)
    print(f"OK  dashboard -> {out}")
    try:
        webbrowser.open(f"file://{out}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
