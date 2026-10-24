#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
원본 폰트 실측(docs/spec 01~06 의 {{원본 기준}} 확정용). fontTools 로 직접 읽는다.

실행: PYTHONUTF8=1 python charset/scripts/measure_sources.py [--json 출력경로] 파일...
기본 대상(인자 없을 때):
  sources/Pretendard/alternative-ttf/Pretendard-Regular.ttf
  sources/Pretendard/alternative-ttf/Pretendard-Bold.ttf
  sources/Pretendard/PretendardVariable.ttf
  sources/NotoSansKR/NotoSansKR[wght].ttf
출력: head/hhea/OS/2/post/name 요약, fvar 축·인스턴스, STAT, GSUB/GPOS 피처·스크립트·언어, cmap 수, 테이블 목록, gasp,
      대표 글립(x, H, 가, 한, 0, ¿, ñ) bbox·advance
"""
import argparse
import json
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT = [
    "sources/Pretendard/alternative-ttf/Pretendard-Regular.ttf",
    "sources/Pretendard/alternative-ttf/Pretendard-Bold.ttf",
    "sources/Pretendard/PretendardVariable.ttf",
    "sources/NotoSansKR/NotoSansKR[wght].ttf",
]
SAMPLE = [0x78, 0x48, 0xAC00, 0xD55C, 0x30, 0xBF, 0xF1, 0x20, 0xA0, 0x203B, 0x2460, 0x3131, 0x5C]


def name_str(font, nid, plat=3, lang=0x409):
    r = font["name"].getName(nid, plat, 1, lang)
    return r.toUnicode() if r else None


def bounds(font, gs, gname):
    pen = BoundsPen(gs)
    gs[gname].draw(pen)
    return pen.bounds


def measure(path):
    f = TTFont(path)
    out = {"file": os.path.relpath(path, ROOT)}
    out["tables"] = sorted(f.keys())
    head, hhea, os2, post = f["head"], f["hhea"], f["OS/2"], f["post"]
    out["head"] = {"unitsPerEm": head.unitsPerEm, "fontRevision": round(head.fontRevision, 3), "flags": hex(head.flags),
                   "macStyle": hex(head.macStyle), "lowestRecPPEM": head.lowestRecPPEM,
                   "bbox": [head.xMin, head.yMin, head.xMax, head.yMax]}
    out["hhea"] = {"ascent": hhea.ascent, "descent": hhea.descent, "lineGap": hhea.lineGap,
                   "advanceWidthMax": hhea.advanceWidthMax, "caretSlopeRise": hhea.caretSlopeRise,
                   "caretSlopeRun": hhea.caretSlopeRun, "caretOffset": hhea.caretOffset}
    out["OS/2"] = {
        "version": os2.version, "xAvgCharWidth": os2.xAvgCharWidth, "usWeightClass": os2.usWeightClass,
        "usWidthClass": os2.usWidthClass, "fsType": os2.fsType, "fsSelection": hex(os2.fsSelection),
        "achVendID": os2.achVendID, "sTypoAscender": os2.sTypoAscender, "sTypoDescender": os2.sTypoDescender,
        "sTypoLineGap": os2.sTypoLineGap, "usWinAscent": os2.usWinAscent, "usWinDescent": os2.usWinDescent,
        "sxHeight": getattr(os2, "sxHeight", None), "sCapHeight": getattr(os2, "sCapHeight", None),
        "yStrikeoutSize": os2.yStrikeoutSize, "yStrikeoutPosition": os2.yStrikeoutPosition,
        "ySubscriptXSize": os2.ySubscriptXSize, "ySubscriptYSize": os2.ySubscriptYSize,
        "ySubscriptXOffset": os2.ySubscriptXOffset, "ySubscriptYOffset": os2.ySubscriptYOffset,
        "ySuperscriptXSize": os2.ySuperscriptXSize, "ySuperscriptYSize": os2.ySuperscriptYSize,
        "ySuperscriptXOffset": os2.ySuperscriptXOffset, "ySuperscriptYOffset": os2.ySuperscriptYOffset,
        "panose": [os2.panose.bFamilyType, os2.panose.bSerifStyle, os2.panose.bWeight, os2.panose.bProportion,
                   os2.panose.bContrast, os2.panose.bStrokeVariation, os2.panose.bArmStyle, os2.panose.bLetterForm,
                   os2.panose.bMidline, os2.panose.bXHeight],
        "ulUnicodeRange": [hex(os2.ulUnicodeRange1), hex(os2.ulUnicodeRange2), hex(os2.ulUnicodeRange3), hex(os2.ulUnicodeRange4)],
        "ulCodePageRange": [hex(os2.ulCodePageRange1), hex(os2.ulCodePageRange2)],
        "usFirstCharIndex": hex(os2.usFirstCharIndex), "usLastCharIndex": hex(os2.usLastCharIndex),
        "usDefaultChar": os2.usDefaultChar, "usBreakChar": os2.usBreakChar, "usMaxContext": os2.usMaxContext,
    }
    out["post"] = {"formatType": post.formatType, "italicAngle": post.italicAngle,
                   "underlinePosition": post.underlinePosition, "underlineThickness": post.underlineThickness,
                   "isFixedPitch": post.isFixedPitch}
    out["maxp"] = {"numGlyphs": f["maxp"].numGlyphs}
    if "gasp" in f:
        out["gasp"] = {str(k): hex(v) for k, v in f["gasp"].gaspRange.items()}
    out["name"] = {nid: name_str(f, nid) for nid in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 25)}
    out["name_langs"] = sorted({(r.platformID, r.platEncID, r.langID) for r in f["name"].names})
    cmap = f.getBestCmap()
    out["cmap"] = {"count": len(cmap), "hangul": sum(1 for c in cmap if 0xAC00 <= c <= 0xD7A3),
                   "jamo1100": sum(1 for c in cmap if 0x1100 <= c <= 0x11FF)}
    if "fvar" in f:
        fv = f["fvar"]
        out["fvar"] = {"axes": [{"tag": a.axisTag, "min": a.minValue, "default": a.defaultValue, "max": a.maxValue,
                                 "nameID": a.axisNameID, "name": name_str(f, a.axisNameID)} for a in fv.axes],
                       "instances": [{"coords": i.coordinates, "subfamily": name_str(f, i.subfamilyNameID),
                                      "psname": name_str(f, i.postscriptNameID) if i.postscriptNameID != 0xFFFF else None}
                                     for i in fv.instances]}
        out["avar"] = {}
        if "avar" in f:
            out["avar"] = {tag: seg for tag, seg in f["avar"].segments.items()}
    if "STAT" in f:
        st = f["STAT"].table
        axes = [{"tag": a.AxisTag, "name": name_str(f, a.AxisNameID), "ordering": a.AxisOrdering} for a in st.DesignAxisRecord.Axis]
        vals = []
        if st.AxisValueArray:
            for av in st.AxisValueArray.AxisValue:
                d = {"format": av.Format, "flags": av.Flags, "name": name_str(f, av.ValueNameID)}
                if av.Format in (1, 3):
                    d["value"] = av.Value
                if av.Format == 3:
                    d["linked"] = av.LinkedValue
                if av.Format == 2:
                    d.update({"nominal": av.NominalValue, "min": av.RangeMinValue, "max": av.RangeMaxValue})
                if av.Format == 4:
                    d["values"] = [(r.AxisIndex, r.Value) for r in av.AxisValueRecord]
                vals.append(d)
        out["STAT"] = {"version": hex(st.Version), "axes": axes, "values": vals,
                       "elidedFallbackNameID": getattr(st, "ElidedFallbackNameID", None)}
    for tbl in ("GSUB", "GPOS"):
        if tbl in f:
            t = f[tbl].table
            feats = sorted({fr.FeatureTag for fr in t.FeatureList.FeatureRecord})
            scripts = {}
            for sr in t.ScriptList.ScriptRecord:
                langs = [ls.LangSysTag for ls in sr.Script.LangSysRecord]
                scripts[sr.ScriptTag] = langs
            out[tbl] = {"features": feats, "scripts": scripts, "lookups": t.LookupList.LookupCount}
    if "GDEF" in f:
        g = f["GDEF"].table
        out["GDEF"] = {"glyphClassDef": bool(g.GlyphClassDef), "markAttach": bool(getattr(g, "MarkAttachClassDef", None)),
                       "markGlyphSets": bool(getattr(g, "MarkGlyphSetsDef", None))}
    if "MVAR" in f:
        out["MVAR"] = sorted({r.ValueTag for r in f["MVAR"].table.ValueRecord})
    gs = f.getGlyphSet()
    hmtx = f["hmtx"]
    samples = {}
    for cp in SAMPLE:
        gname = cmap.get(cp)
        if gname:
            b = bounds(f, gs, gname)
            samples[f"U+{cp:04X}"] = {"glyph": gname, "adv": hmtx[gname][0], "lsb": hmtx[gname][1], "bbox": b}
        else:
            samples[f"U+{cp:04X}"] = None
    out["samples"] = samples
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--json")
    args = ap.parse_args()
    files = args.files or [os.path.join(ROOT, p) for p in DEFAULT]
    results = []
    for p in files:
        if not os.path.exists(p):
            print("MISSING", p)
            continue
        r = measure(p)
        results.append(r)
        print("=" * 100)
        print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, ensure_ascii=False, indent=1, default=str)


if __name__ == "__main__":
    main()
