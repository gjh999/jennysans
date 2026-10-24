# -*- coding: utf-8 -*-
"""
font-qa 공용 상수·헬퍼 (docs/qa/scripts/*). 빌더 코드(tools/verify_build.py)와 독립 — charset 파서만 tools/charset.py 를 임포트한다.
실행: 저장소 루트에서 `PYTHONUTF8=1 python docs/qa/scripts/<script>.py`
결과: docs/qa/results/<script>.md (+ .json)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DIST = ROOT / "dist"
STATIC_DIR = DIST / "static"
VARIABLE_DIR = DIST / "variable"
WEB_DIR = DIST / "web"
SUBSET_DIR = WEB_DIR / "subset"
CSS_DIR = DIST / "css"
PKG_DIR = DIST / "packages"
QA_DIR = ROOT / "docs" / "qa"
RESULTS = QA_DIR / "results"
SHOTS = QA_DIR / "shots"
SOURCES = ROOT / "sources"
PRETENDARD_TTF = SOURCES / "Pretendard" / "alternative-ttf"
PRETENDARD_VF = SOURCES / "Pretendard" / "PretendardVariable.ttf"
NOTO_VF = SOURCES / "NotoSansKR" / "NotoSansKR[wght].ttf"

sys.path.insert(0, str(ROOT / "tools"))

WEIGHTS = [("Thin", 100), ("ExtraLight", 200), ("Light", 300), ("Regular", 400), ("Medium", 500),
           ("SemiBold", 600), ("Bold", 700), ("ExtraBold", 800), ("Black", 900)]
WEIGHT_NAMES = [w for w, _ in WEIGHTS]
WEIGHT_VALUE = dict(WEIGHTS)
VERSION = "1.001"

STATIC_TTFS = [STATIC_DIR / f"JennySans-{w}.ttf" for w in WEIGHT_NAMES]
VF_TTF = VARIABLE_DIR / "JennySansVariable.ttf"
STATIC_WOFF2 = [WEB_DIR / f"JennySans-{w}.woff2" for w in WEIGHT_NAMES]
VF_WOFF2 = WEB_DIR / "JennySansVariable.woff2"
ALL_TTFS = STATIC_TTFS + [VF_TTF]
ALL_FONTS = ALL_TTFS + STATIC_WOFF2 + [VF_WOFF2]

# 외곽선이 없어도 되는 코드포인트(공백류·채움·default-ignorable). 빌더 config 와 별개로 QA 가 독립 정의.
BLANK_OK = {0x0020, 0x00A0, 0x00AD, 0x115F, 0x1160, 0x3000, 0x3164, 0xFFA0, 0xFEFF, 0x2060, 0x202F, 0x205F,
            0x200B, 0x200C, 0x200D, *range(0x2000, 0x200E)}


class Report:
    """PASS/FAIL/WARN/INFO 수집기 → markdown 표."""

    def __init__(self, title):
        self.title = title
        self.rows = []      # (status, section, message)
        self.extra = []     # 추가 markdown 블록

    def add(self, status, section, msg):
        self.rows.append((status, section, msg))
        print(f"[{status}] {section}: {msg}")

    def passed(self, section, msg):
        self.add("PASS", section, msg)

    def fail(self, section, msg):
        self.add("FAIL", section, msg)

    def warn(self, section, msg):
        self.add("WARN", section, msg)

    def info(self, section, msg):
        self.add("INFO", section, msg)

    def md(self, block):
        self.extra.append(block)

    def counts(self):
        c = {}
        for s, _, _ in self.rows:
            c[s] = c.get(s, 0) + 1
        return c

    def write(self, name):
        RESULTS.mkdir(parents=True, exist_ok=True)
        c = self.counts()
        verdict = "FAIL" if c.get("FAIL") else "PASS"
        lines = [f"# {self.title}", "",
                 f"결과: **{verdict}** (FAIL {c.get('FAIL', 0)} · WARN {c.get('WARN', 0)} · PASS {c.get('PASS', 0)} · INFO {c.get('INFO', 0)})",
                 "", "| 상태 | 항목 | 내용 |", "|---|---|---|"]
        for s, sec, m in self.rows:
            lines.append(f"| {s} | {sec} | {str(m).replace('|', '\\|')} |")
        for b in self.extra:
            lines += ["", b]
        out = RESULTS / f"{name}.md"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        (RESULTS / f"{name}.json").write_text(json.dumps({"verdict": verdict, "counts": c, "rows": self.rows},
                                                          ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n== {verdict} → {out}")
        return verdict


def load_charsets():
    import charset  # tools/charset.py
    return charset.load_sets()


def fmt_ranges(cps, limit=None):
    import charset
    cps = sorted(cps)
    if limit:
        cps = cps[:limit]
    return charset.format_ranges(cps)


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in r) + " |")
    return "\n".join(out)
