#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
measure_fonts.py — 후보 폰트 실측 (font-researcher 작성, builder/qa 재사용 가능)

사용:
  PYTHONUTF8=1 python docs/research/scripts/measure_fonts.py sources/Pretendard sources/Inter/InterVariable.ttf ...
  PYTHONUTF8=1 python docs/research/scripts/measure_fonts.py --all sources          # sources/ 아래 전부
옵션:
  --json <경로>   결과 JSON 저장 (기본 docs/research/measurements.json)
  --md   <경로>   Markdown 표 저장 (기본 docs/research/measurements.md)

측정 항목: 형식(CFF/CFF2/glyf)·변수축·UPM·수직메트릭(hhea/OS2 typo/win, USE_TYPO_METRICS)·웨이트·
name(0/1/2/4/5/6/7/13/14/16/17 + ko 레코드)·fsType·힌팅 테이블·GSUB/GPOS 피처·
코드포인트 집합별 커버리지(cmap 존재 + 빈 글립 여부).
"""
import sys, os, json, hashlib, argparse
from fontTools.ttLib import TTFont

# ---------- 측정용 코드포인트 집합 (AGENTS §1 범위 기준) ----------
def rng(a, b):
    return set(range(a, b + 1))

SPANISH = "ñÑáéíóúÁÉÍÓÚüÜ¿¡ªº€«»"
KSX_SYMBOLS = ("※○●◎◇◆□■△▲▽▼☆★①②③④⑤⑥⑦⑧⑨⑩㉠㉡㉢㈜㎏㎡㎜㎝㎞㎖℃℉→←↑↓↔±×÷≠≤≥∞∴√∠∑"
               "「」『』【】〔〕、。・…‥‘’“”§¶†‡‰₩€£¥¢")
SETS = [
    ("hangul_syllables", "한글 완성형 U+AC00–D7A3", rng(0xAC00, 0xD7A3)),
    ("compat_jamo", "호환자모 U+3131–318E", rng(0x3131, 0x318E)),
    ("jamo", "자모 U+1100–11FF", rng(0x1100, 0x11FF)),
    ("jamo_ext_a", "자모확장A U+A960–A97F (A97D–A97F 미배정)", rng(0xA960, 0xA97C)),
    ("jamo_ext_b", "자모확장B U+D7B0–D7FF (D7C7–D7CA, D7FC–D7FF 미배정)", rng(0xD7B0, 0xD7C6) | rng(0xD7CB, 0xD7FB)),
    ("ascii", "ASCII U+0020–007E", rng(0x20, 0x7E)),
    ("latin1_supp", "Latin-1 Supplement U+00A0–00FF", rng(0xA0, 0xFF)),
    ("latin_ext_a", "Latin Extended-A U+0100–017F", rng(0x100, 0x17F)),
    ("spanish", "스페인어 필수 " + SPANISH, set(ord(c) for c in SPANISH)),
    ("greek", "그리스 U+0391–03C9 (03A2 미배정 제외)", rng(0x391, 0x3C9) - {0x3A2}),
    ("cyrillic", "키릴 U+0410–044F", rng(0x410, 0x44F)),
    ("ksx_symbols", "KS X 1001 기호 샘플(" + str(len(set(KSX_SYMBOLS))) + "자)", set(ord(c) for c in KSX_SYMBOLS)),
]

NAME_IDS = {0: "copyright", 1: "family", 2: "subfamily", 3: "uniqueID", 4: "fullName", 5: "version",
            6: "psName", 7: "trademark", 8: "manufacturer", 9: "designer", 11: "vendorURL",
            12: "designerURL", 13: "licenseDesc", 14: "licenseURL", 16: "typoFamily", 17: "typoSubfamily",
            21: "wwsFamily", 22: "wwsSubfamily", 25: "varPSPrefix"}

RFN_WORDS = ["Pretendard", "Source", "Inter", "Noto", "Plex", "Spoqa", "Nanum", "M PLUS", "Wanted", "SUIT",
             "Gothic A1", "Freesentation", "Paperlogy"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


from fontTools.pens.boundsPen import BoundsPen

_GS_CACHE = {}

def glyph_is_empty(font, gname, fmt):
    """글립이 외곽선이 없는지(공백/미제작) 판단 — glyf/CFF/CFF2 공통으로 실제 외곽선을 그려 bounds 유무로 판정.
    (CFF 는 서브루틴 호출만으로 charstring 이 짧을 수 있어 바이트 길이로 판단하면 오탐이 난다.)
    공백문자는 비어 있어도 정상이므로 호출측에서 제외."""
    try:
        gs = _GS_CACHE.get(id(font))
        if gs is None:
            gs = font.getGlyphSet()
            _GS_CACHE[id(font)] = gs
        pen = BoundsPen(gs)
        gs[gname].draw(pen)
        return pen.bounds is None
    except Exception:
        return None


def measure(path):
    font = TTFont(path, lazy=True)
    r = {"file": path.replace("\\", "/"), "size_bytes": os.path.getsize(path), "sha256": sha256(path)}
    tags = sorted(font.keys())
    r["tables"] = tags
    fmt = "CFF2" if "CFF2" in font else ("CFF" if "CFF " in font else ("glyf" if "glyf" in font else "?"))
    r["outline_format"] = fmt
    r["is_variable"] = "fvar" in font
    if "fvar" in font:
        r["axes"] = [{"tag": a.axisTag, "min": a.minValue, "default": a.defaultValue, "max": a.maxValue}
                     for a in font["fvar"].axes]
        r["named_instances"] = len(font["fvar"].instances)
    r["has_STAT"] = "STAT" in font
    head = font["head"]
    r["upm"] = head.unitsPerEm
    r["fontRevision"] = round(head.fontRevision, 3)
    os2 = font["OS/2"]
    r["usWeightClass"] = os2.usWeightClass
    r["usWidthClass"] = os2.usWidthClass
    r["fsType"] = os2.fsType
    r["fsSelection"] = os2.fsSelection
    r["USE_TYPO_METRICS"] = bool(os2.fsSelection & (1 << 7))
    r["os2_version"] = os2.version
    r["typo"] = {"asc": os2.sTypoAscender, "desc": os2.sTypoDescender, "gap": os2.sTypoLineGap}
    r["win"] = {"asc": os2.usWinAscent, "desc": os2.usWinDescent}
    hhea = font["hhea"]
    r["hhea"] = {"asc": hhea.ascent, "desc": hhea.descent, "gap": hhea.lineGap}
    r["xHeight"] = getattr(os2, "sxHeight", None)
    r["capHeight"] = getattr(os2, "sCapHeight", None)
    r["vendorID"] = os2.achVendID
    r["numGlyphs"] = font["maxp"].numGlyphs
    # hinting
    r["hinting"] = {"fpgm": "fpgm" in font, "prep": "prep" in font, "cvt": "cvt " in font,
                    "gasp": "gasp" in font, "hdmx": "hdmx" in font}
    if fmt == "CFF":
        try:
            pd = font["CFF "].cff.topDictIndex[0].Private
            r["hinting"]["cff_BlueValues"] = hasattr(pd, "BlueValues")
        except Exception:
            try:
                fd = font["CFF "].cff.topDictIndex[0].FDArray[0].Private
                r["hinting"]["cff_BlueValues"] = hasattr(fd, "BlueValues")
            except Exception:
                r["hinting"]["cff_BlueValues"] = None
    # name table
    names = {}
    ko = {}
    rfn_hits = {}
    for rec in font["name"].names:
        try:
            s = rec.toUnicode()
        except Exception:
            continue
        nid = rec.nameID
        if nid in NAME_IDS and nid not in names and rec.platformID == 3 and rec.langID == 0x409:
            names[NAME_IDS[nid]] = s
        if rec.platformID == 3 and rec.langID == 0x412:
            ko[NAME_IDS.get(nid, str(nid))] = s
        for w in RFN_WORDS:
            if w.lower() in s.lower():
                rfn_hits.setdefault(w, set()).add(nid)
    # fallback: mac platform
    for rec in font["name"].names:
        if rec.nameID in NAME_IDS and NAME_IDS[rec.nameID] not in names:
            try:
                names[NAME_IDS[rec.nameID]] = rec.toUnicode()
            except Exception:
                pass
    r["name"] = names
    r["name_ko"] = ko
    r["name_rfn_word_hits"] = {k: sorted(v) for k, v in rfn_hits.items()}
    # features
    feats = {}
    for t in ("GSUB", "GPOS"):
        if t in font:
            try:
                feats[t] = sorted({fr.FeatureTag for fr in font[t].table.FeatureList.FeatureRecord})
            except Exception:
                feats[t] = []
    r["features"] = feats
    # cmap coverage
    cmap = font.getBestCmap() or {}
    r["cmap_count"] = len(cmap)
    cov = {}
    for key, desc, cps in SETS:
        present = [c for c in cps if c in cmap]
        missing = sorted(cps - set(present))
        empty = []
        for c in present:
            if c in (0x20, 0xA0, 0x3000):
                continue
            e = glyph_is_empty(font, cmap[c], fmt)
            if e:
                empty.append(c)
        cov[key] = {"desc": desc, "total": len(cps), "present": len(present), "missing_count": len(missing),
                    "missing_sample": ["U+%04X" % c for c in missing[:40]],
                    "empty_glyphs": ["U+%04X" % c for c in empty[:40]], "empty_count": len(empty)}
    r["coverage"] = cov
    # hangul jamo composition features
    r["hangul_jamo_features"] = [f for f in feats.get("GSUB", []) if f in ("ljmo", "vjmo", "tjmo", "ccmp")]
    font.close()
    return r


def collect(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in sorted(files):
                    if f.lower().endswith((".ttf", ".otf")):
                        out.append(os.path.join(root, f))
        else:
            out.append(p)
    return out


def md_table(results):
    lines = []
    lines.append("| 파일 | 형식 | 변수 | UPM | wght | typo asc/desc/gap | hhea asc/desc/gap | win asc/desc | USE_TYPO | 글립수 | cmap | 한글 11172 | 호환자모(94) | 자모(256) | 자모확A(29) | 자모확B(72) | ASCII(95) | Lat1(96) | LatExtA(128) | 스페인어(22) | 그리스(56) | 키릴(64) | KS기호(N) | 힌팅 | 크기(KB) | 버전 |")
    lines.append("|" + "---|" * 26)
    for r in results:
        c = r["coverage"]
        def cv(k):
            x = c[k]
            s = f"{x['present']}/{x['total']}"
            if x["empty_count"]:
                s += f" (빈{x['empty_count']})"
            return s
        hint = ("TT:" + ("fpgm" if r["hinting"]["fpgm"] else "-")) if r["outline_format"] == "glyf" else ("CFF:" + ("blue" if r["hinting"].get("cff_BlueValues") else "-"))
        axes = ",".join(f"{a['tag']}{a['min']:g}-{a['max']:g}" for a in r.get("axes", [])) if r["is_variable"] else "-"
        lines.append("| " + " | ".join([
            os.path.basename(r["file"]), r["outline_format"], axes, str(r["upm"]), str(r["usWeightClass"]),
            f"{r['typo']['asc']}/{r['typo']['desc']}/{r['typo']['gap']}",
            f"{r['hhea']['asc']}/{r['hhea']['desc']}/{r['hhea']['gap']}",
            f"{r['win']['asc']}/{r['win']['desc']}", "Y" if r["USE_TYPO_METRICS"] else "N",
            str(r["numGlyphs"]), str(r["cmap_count"]),
            cv("hangul_syllables"), cv("compat_jamo"), cv("jamo"), cv("jamo_ext_a"), cv("jamo_ext_b"),
            cv("ascii"), cv("latin1_supp"), cv("latin_ext_a"), cv("spanish"), cv("greek"), cv("cyrillic"), cv("ksx_symbols"),
            hint, f"{r['size_bytes']/1024:.0f}", r["name"].get("version", "")]) + " |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--all", default=None)
    ap.add_argument("--json", default="docs/research/measurements.json")
    ap.add_argument("--md", default="docs/research/measurements.md")
    a = ap.parse_args()
    paths = collect([a.all] if a.all else a.paths)
    results = []
    for p in paths:
        try:
            results.append(measure(p))
            print("OK ", p, file=sys.stderr)
        except Exception as e:
            print("ERR", p, e, file=sys.stderr)
            results.append({"file": p, "error": str(e)})
    ok = [r for r in results if "error" not in r]
    os.makedirs(os.path.dirname(a.json) or ".", exist_ok=True)
    with open(a.json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    with open(a.md, "w", encoding="utf-8") as f:
        f.write("# 실측 결과 (자동 생성: docs/research/scripts/measure_fonts.py)\n\n")
        f.write("측정 집합: " + "; ".join(f"{k}={d}" for k, d, _ in SETS) + "\n\n")
        f.write(md_table(ok) + "\n")
    print(md_table(ok))


if __name__ == "__main__":
    main()
