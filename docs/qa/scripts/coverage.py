# -*- coding: utf-8 -*-
"""
게이트 1 — 커버리지 전수 (font-qa 독립 검사).
charset/required.txt 전 코드포인트 × (정적 9 TTF + 변수 TTF + WOFF2 10) → cmap 존재 · 글립이 .notdef 아님 · 외곽선 비어 있지 않음(공백류 제외).
+ 9 정적·변수 cmap 집합 동일(spec 01 §2), 같은 웨이트 TTF/WOFF2 cmap 동일(spec 01 §4), recommended/korean-old 보유 수, 블록별 누락 표.
실행: PYTHONUTF8=1 python docs/qa/scripts/coverage.py
"""
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.pens.boundsPen import BoundsPen  # noqa: E402

BLOCKS = [  # (이름, lo, hi) — charset/README.md §4 블록 표와 같은 구분
    ("ASCII", 0x0020, 0x007E), ("Latin-1 Supplement", 0x00A0, 0x00FF), ("Latin Extended-A", 0x0100, 0x017F),
    ("Latin Extended-B", 0x0180, 0x024F), ("Spacing Modifier", 0x02B0, 0x02FF), ("Combining Diacritical", 0x0300, 0x036F),
    ("Greek", 0x0370, 0x03FF), ("Cyrillic", 0x0400, 0x04FF), ("Hangul Jamo", 0x1100, 0x11FF),
    ("Latin Ext Additional", 0x1E00, 0x1EFF), ("General Punctuation", 0x2000, 0x206F), ("Super/Subscripts", 0x2070, 0x209F),
    ("Currency", 0x20A0, 0x20CF), ("Letterlike", 0x2100, 0x214F), ("Number Forms", 0x2150, 0x218F), ("Arrows", 0x2190, 0x21FF),
    ("Math Operators", 0x2200, 0x22FF), ("Misc Technical", 0x2300, 0x23FF), ("Enclosed Alphanumerics", 0x2460, 0x24FF),
    ("Box Drawing", 0x2500, 0x257F), ("Block Elements", 0x2580, 0x259F), ("Geometric Shapes", 0x25A0, 0x25FF),
    ("Misc Symbols", 0x2600, 0x26FF), ("Dingbats", 0x2700, 0x27BF), ("CJK Symbols", 0x3000, 0x303F),
    ("Katakana", 0x30A0, 0x30FF), ("Hangul Compat Jamo", 0x3130, 0x318F), ("Enclosed CJK", 0x3200, 0x32FF),
    ("CJK Compatibility", 0x3300, 0x33FF), ("Hangul Jamo Ext-A", 0xA960, 0xA97F), ("Hangul Syllables", 0xAC00, 0xD7A3),
    ("Hangul Jamo Ext-B", 0xD7B0, 0xD7FF), ("Halfwidth/Fullwidth", 0xFF00, 0xFFEF), ("Specials", 0xFFF0, 0xFFFF),
]


def block_of(cp):
    for n, lo, hi in BLOCKS:
        if lo <= cp <= hi:
            return n
    return f"other U+{cp:04X}"


def blank_ok(cp):
    if cp in Q.BLANK_OK:
        return True
    return unicodedata.category(chr(cp)) in ("Zs", "Zl", "Zp", "Cc", "Cf")


def glyph_has_ink(font, gname, glyphset):
    """glyf 글립이 외곽선(또는 잉크 있는 컴포넌트)을 갖는지. BoundsPen 으로 실측(컴포지트 포함)."""
    try:
        pen = BoundsPen(glyphset)
        glyphset[gname].draw(pen)
        return pen.bounds is not None
    except Exception:
        return False


def check_font(path, sets, rep):
    f = TTFont(path)
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    req = sets["required"]
    missing, notdef, empty = [], [], []
    for cp in sorted(req):
        g = cmap.get(cp)
        if g is None:
            missing.append(cp)
        elif g == ".notdef":
            notdef.append(cp)
        elif not blank_ok(cp) and not glyph_has_ink(f, g, gs):
            empty.append(cp)
    # 한글 11,172 별도 집계
    hangul = [cp for cp in range(0xAC00, 0xD7A4)]
    h_miss = [cp for cp in hangul if cp not in cmap or cmap[cp] == ".notdef"]
    name = path.name
    if missing or notdef or empty:
        rep.fail("coverage", f"{name}: required 누락 {len(missing)} {Q.fmt_ranges(missing, 40)} / .notdef {len(notdef)} / 빈 외곽선 {len(empty)} {Q.fmt_ranges(empty, 40)}")
    else:
        rep.passed("coverage", f"{name}: required {len(req)}/{len(req)} cmap 존재·비-notdef·외곽선 있음(공백류 {sum(1 for c in req if blank_ok(c))} 제외)")
    if h_miss:
        rep.fail("hangul", f"{name}: 한글 음절 누락 {len(h_miss)}")
    else:
        rep.passed("hangul", f"{name}: 한글 음절 11,172/11,172")
    extra = {}
    for n in ("recommended", "korean-old"):
        have = sum(1 for c in sets[n] if c in cmap and cmap[c] != ".notdef")
        extra[n] = have
        rep.info("coverage", f"{name}: {n} 보유 {have}/{len(sets[n])}")
    by_block = {}
    for cp in missing + notdef + empty:
        by_block[block_of(cp)] = by_block.get(block_of(cp), 0) + 1
    f.close()
    return {"cmap": set(cmap), "missing": missing, "notdef": notdef, "empty": empty, "by_block": by_block, **extra,
            "numGlyphs": f["maxp"].numGlyphs if "maxp" in f else None}


def main():
    rep = Q.Report("커버리지 전수 (게이트 1)")
    sets = Q.load_charsets()
    rep.info("charset", f"required {len(sets['required'])} · recommended {len(sets['recommended'])} · korean-old {len(sets['korean-old'])} (tools/charset.py 파싱)")
    results = {}
    for p in Q.ALL_FONTS:
        if not p.exists():
            rep.fail("file", f"{p} 없음")
            continue
        results[p.name] = check_font(p, sets, rep)
    # cmap 집합 동일성
    cm_static = [results[p.name]["cmap"] for p in Q.STATIC_TTFS if p.name in results]
    if cm_static and all(c == cm_static[0] for c in cm_static):
        rep.passed("cmap-equal", f"정적 9종 cmap 집합 동일 ({len(cm_static[0])} cps)")
    else:
        rep.fail("cmap-equal", "정적 9종 cmap 집합 불일치")
    if Q.VF_TTF.name in results and cm_static and results[Q.VF_TTF.name]["cmap"] == cm_static[0]:
        rep.passed("cmap-equal", "변수 폰트 cmap = 정적 cmap")
    else:
        rep.fail("cmap-equal", "변수 폰트 cmap ≠ 정적 cmap")
    for t, w in zip(Q.STATIC_TTFS + [Q.VF_TTF], Q.STATIC_WOFF2 + [Q.VF_WOFF2]):
        if t.name in results and w.name in results:
            if results[t.name]["cmap"] == results[w.name]["cmap"]:
                rep.passed("ttf=woff2", f"{t.name} ↔ {w.name} cmap 동일")
            else:
                rep.fail("ttf=woff2", f"{t.name} ↔ {w.name} cmap 불일치")
    # 블록별 누락 표
    rows = []
    for n, r in results.items():
        rows.append((n, r["numGlyphs"], len(r["cmap"]), len(r["missing"]), len(r["notdef"]), len(r["empty"]), r.get("recommended"), r.get("korean-old"),
                     ", ".join(f"{k}:{v}" for k, v in sorted(r["by_block"].items())) or "-"))
    rep.md("## 파일별 집계\n\n" + Q.table(["파일", "numGlyphs", "cmap", "required 누락", ".notdef", "빈 외곽선", "recommended", "korean-old", "누락 블록"], rows))
    # required 블록별 커버 표 (Regular 기준)
    reg = results.get("JennySans-Regular.ttf")
    if reg:
        rows = []
        for bn, lo, hi in BLOCKS:
            req_b = [c for c in sets["required"] if lo <= c <= hi]
            if not req_b:
                continue
            have = sum(1 for c in req_b if c in reg["cmap"])
            rows.append((bn, f"U+{lo:04X}-{hi:04X}", len(req_b), have, len(req_b) - have))
        rep.md("## required 블록별 커버 (JennySans-Regular.ttf)\n\n" + Q.table(["블록", "범위", "required", "보유", "누락"], rows))
    rep.write("coverage")


if __name__ == "__main__":
    main()
