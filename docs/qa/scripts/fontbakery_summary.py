# -*- coding: utf-8 -*-
"""
fontbakery JSON(정적 9 + VF 각각 실행) → docs/qa/fontbakery-1.000.md 요약 + docs/qa/fontbakery-1.000.html 인덱스.
- 상태별 집계, FAIL/WARN 검사 ID 별 표(대상 파일·메시지 요약), 승인 예외(AGENTS §8: family/win_ascent_and_descent) 분리 표기.
실행 순서:
  python -m fontbakery check-universal dist/static/*.ttf -J 4 --html docs/qa/fontbakery-1.000-static.html --json docs/qa/results/fontbakery-static.json -l WARN
  python -m fontbakery check-universal dist/variable/JennySansVariable.ttf --html docs/qa/fontbakery-1.000-variable.html --json docs/qa/results/fontbakery-variable.json -l WARN
  PYTHONUTF8=1 python docs/qa/scripts/fontbakery_summary.py
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402

APPROVED = {"opentype/family/win_ascent_and_descent": "AGENTS §8 2026-09-06 — OS/2 win 1950/494 유지(Pretendard 동일), yMax 2172/2214 > 1950 은 라틴 악센트 대문자·GDI 극단 케이스"}
MIXED_RUN_ARTIFACTS = {"opentype/family/consistent_family_name", "typographic_family_name", "opentype/varfont/family_axis_ranges", "family/single_directory"}


def load(path):
    """fontbakery 1.1 JSON: sections[].checks[] — 검사 ID 는 key[1] 의 '<FontBakeryCheck:ID>' 문자열에서 추출."""
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for sec in d.get("sections", []):
        for ch in sec.get("checks", []):
            key = ch.get("key")
            m = re.search(r"FontBakeryCheck:([^>]+)>", str(key[1]) if isinstance(key, list) and len(key) > 1 else str(key))
            cid = m.group(1) if m else str(key)
            files = ch.get("filename")
            if isinstance(files, list):
                files = ", ".join(Path(str(x)).name for x in files)
            elif files:
                files = Path(str(files)).name
            else:
                files = "(family)"
            msgs = [(lg.get("message", {}).get("code"), lg.get("message", {}).get("message", "")) for lg in ch.get("logs", []) if lg.get("status") in ("FAIL", "WARN", "ERROR", "FATAL")]
            rows.append({"id": cid, "result": ch.get("result"), "files": files, "msgs": msgs, "desc": ch.get("description", ""), "rationale": ch.get("rationale", "")})
    return d, rows


def short(s, n=420):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[:n] + "…"


def main():
    out_md = [f"# fontbakery {getattr(__import__('fontbakery'), '__version__', '')} check-universal — JennySans {Q.VERSION}", "",
              "실행: 정적 9종 한 묶음 + 변수 1종 별도(패밀리 검사가 두 패밀리를 섞지 않도록; `JennySans` ≠ `JennySans Variable` 은 팀장 결정 ③).",
              f"원본 HTML: `docs/qa/fontbakery-{Q.VERSION}-static.html`, `docs/qa/fontbakery-{Q.VERSION}-variable.html` · JSON: `docs/qa/results/fontbakery-{{static,variable}}.json`", ""]
    total = defaultdict(int)
    fails, warns = defaultdict(list), defaultdict(list)
    infos = {}
    for tag, jp in (("static", Q.RESULTS / "fontbakery-static.json"), ("variable", Q.RESULTS / "fontbakery-variable.json")):
        if not jp.exists():
            out_md.append(f"- {tag}: JSON 없음(미실행)")
            continue
        d, rows = load(jp)
        cnt = defaultdict(int)
        for r in rows:
            cnt[r["result"]] += 1
            total[r["result"]] += 1
            if r["result"] == "FAIL":
                fails[r["id"]].append((tag, r["files"], r["msgs"], r["desc"], r["rationale"]))
            elif r["result"] == "WARN":
                warns[r["id"]].append((tag, r["files"], r["msgs"], r["desc"]))
        out_md.append(f"- **{tag}**: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items(), key=lambda x: x[0])) + f" (검사 실행 {len(rows)})")
    out_md += ["", "## 집계", "", "| 상태 | 수 |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(total.items())]
    approved_fail = {k: v for k, v in fails.items() if k in APPROVED}
    real_fail = {k: v for k, v in fails.items() if k not in APPROVED}
    out_md += ["", f"## FAIL — 승인 예외 제외 {len(real_fail)} 검사 ID (전부 티켓 대상)", ""]
    for cid, lst in sorted(real_fail.items()):
        out_md.append(f"### `{cid}`")
        out_md.append("")
        out_md.append(f"- 설명: {short(lst[0][3], 300)}")
        for tag, files, msgs, _, _ in lst:
            for code, m in msgs:
                out_md.append(f"- [{tag}] {files}: `{code}` {short(m)}")
        out_md.append("")
    out_md += ["## FAIL — 승인 예외", ""]
    if approved_fail:
        for cid, lst in approved_fail.items():
            out_md.append(f"### `{cid}` — {APPROVED[cid]}")
            for tag, files, msgs, _, _ in lst:
                for code, m in msgs:
                    out_md.append(f"- [{tag}] {files}: `{code}` {short(m)}")
            out_md.append("")
    else:
        out_md.append("- (해당 검사 FAIL 없음 — 아래 WARN 절 참조)")
        out_md.append("")
    out_md += [f"## WARN {len(warns)} 검사 ID (사유·판단)", ""]
    for cid, lst in sorted(warns.items()):
        out_md.append(f"### `{cid}`" + (f" — 승인 예외: {APPROVED[cid]}" if cid in APPROVED else ""))
        out_md.append("")
        out_md.append(f"- 설명: {short(lst[0][3], 240)}")
        seen = set()
        for tag, files, msgs, _ in lst:
            for code, m in msgs:
                key = (code, short(m, 200))
                if key in seen:
                    continue
                seen.add(key)
                out_md.append(f"- [{tag}] {files}: `{code}` {short(m, 360)}")
        out_md.append("")
    md = Q.QA_DIR / f"fontbakery-{Q.VERSION}.md"
    md.write_text("\n".join(out_md) + "\n", encoding="utf-8")
    html = Q.QA_DIR / f"fontbakery-{Q.VERSION}.html"
    html.write_text(f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>fontbakery — JennySans {Q.VERSION}</title></head>
<body style="font-family:system-ui;margin:40px"><h1>fontbakery check-universal — JennySans {Q.VERSION}</h1>
<p>집계: {', '.join(f'{k} {v}' for k, v in sorted(total.items()))}</p>
<ul><li><a href="fontbakery-{Q.VERSION}-static.html">정적 9종 리포트</a></li><li><a href="fontbakery-{Q.VERSION}-variable.html">변수 폰트 리포트</a></li>
<li><a href="fontbakery-{Q.VERSION}.md">요약(markdown)</a></li></ul></body></html>""", encoding="utf-8")
    print("\n".join(out_md[:40]))
    print(f"→ {md}\n→ {html}")


if __name__ == "__main__":
    main()
