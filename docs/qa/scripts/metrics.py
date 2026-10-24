# -*- coding: utf-8 -*-
"""
게이트 5 (+3·4 보조) — 메트릭·OS/2·head·hhea·post·STAT·피처 (spec 03·04·02 §3·§4-3).
전 파일(정적 9·VF·WOFF2 10): UPM 2048, typo=hhea=win 1950/-494/0·1950/494, USE_TYPO·WWS, fsSelection/macStyle RIBBI, usWeightClass,
fsType 0, Panose, achVendID JNSF, underline -258/139, italicAngle 0, caretSlope 1/0, head.flags 3, fontRevision 1.0, gasp, DSIG 없음, glyf/loca·CFF 없음,
한글 11,172+호환자모+이식 자모 adv 1770, 대표 글립 bbox 원본(Pretendard) 동일, 피처 태그 49(원본 − ss16 / − ss16,rlig)·빈 피처 0,
STAT(정적: 값 1; VF: 9 값·Regular Format3→700 elidable·ital 축 없음), codePageRange, xAvgCharWidth 재계산 확인.
실행: PYTHONUTF8=1 python docs/qa/scripts/metrics.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.pens.boundsPen import BoundsPen  # noqa: E402

PANOSE_W = {100: 2, 200: 3, 300: 4, 400: 5, 500: 6, 600: 7, 700: 8, 800: 9, 900: 10}
REPR = "가힣한글ㄱㅏHxg0€¿ñ①○■※≠∫★"


def bbox(font, gname):
    gs = font.getGlyphSet()
    pen = BoundsPen(gs)
    gs[gname].draw(pen)
    return pen.bounds


def features(font, tbl):
    if tbl not in font:
        return set(), []
    t = font[tbl].table
    tags = set()
    empty = []
    for fr in t.FeatureList.FeatureRecord:
        tags.add(fr.FeatureTag)
        if not fr.Feature.LookupListIndex:
            empty.append(fr.FeatureTag)
    return tags, empty


def check(path, rep, orig_feats):
    f = TTFont(path)
    n = path.name
    is_vf = "fvar" in f
    os2, head, hhea, post = f["OS/2"], f["head"], f["hhea"], f["post"]
    w = None if is_vf else path.name.rsplit(".", 1)[0].split("-")[1]
    wv = 400 if is_vf else Q.WEIGHT_VALUE[w]
    vals = (head.unitsPerEm, os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap, hhea.ascent, hhea.descent, hhea.lineGap,
            os2.usWinAscent, os2.usWinDescent)
    exp = (2048, 1950, -494, 0, 1950, -494, 0, 1950, 494)
    (rep.passed if vals == exp else rep.fail)("vmetrics", f"{n}: UPM/typo/hhea/win = {vals}" + ("" if vals == exp else f" ≠ {exp}"))
    fs = os2.fsSelection
    use_typo, wws, regular, bold, italic, oblique = bool(fs & 0x80), bool(fs & 0x100), bool(fs & 0x40), bool(fs & 0x20), bool(fs & 1), bool(fs & 0x200)
    exp_fs = 0x1A0 if w == "Bold" else 0x1C0
    (rep.passed if fs == exp_fs else rep.fail)("fsSelection", f"{n}: fsSelection 0x{fs:X} (USE_TYPO {use_typo}, WWS {wws}, REGULAR {regular}, BOLD {bold}, ITALIC {italic}) 기대 0x{exp_fs:X}")
    exp_mac = 1 if w == "Bold" else 0
    (rep.passed if head.macStyle == exp_mac else rep.fail)("macStyle", f"{n}: macStyle {head.macStyle} 기대 {exp_mac}")
    (rep.passed if os2.usWeightClass == wv else rep.fail)("weightClass", f"{n}: usWeightClass {os2.usWeightClass} 기대 {wv}")
    (rep.passed if os2.usWidthClass == 5 else rep.fail)("widthClass", f"{n}: usWidthClass {os2.usWidthClass}")
    (rep.passed if os2.fsType == 0 else rep.fail)("fsType", f"{n}: fsType {os2.fsType}")
    (rep.passed if os2.achVendID == "JNSF" else rep.fail)("vendID", f"{n}: achVendID {os2.achVendID!r}")
    pan = os2.panose
    pv = (pan.bFamilyType, pan.bSerifStyle, pan.bWeight, pan.bProportion, pan.bContrast, pan.bStrokeVariation, pan.bArmStyle, pan.bLetterForm, pan.bMidline, pan.bXHeight)
    exp_pw = 5 if is_vf else PANOSE_W[wv]
    ok = pv[0] == 2 and pv[1] == 11 and pv[2] == exp_pw and pv[3] == 3
    (rep.passed if ok else rep.fail)("panose", f"{n}: panose {list(pv)} (기대 2/11/{exp_pw}/3)")
    ul = (post.underlinePosition, post.underlineThickness)
    (rep.passed if ul == (-258, 139) else rep.fail)("underline", f"{n}: underline {ul}")
    (rep.passed if post.italicAngle == 0 and hhea.caretSlopeRise == 1 and hhea.caretSlopeRun == 0 and hhea.caretOffset == 0 else rep.fail)(
        "italic", f"{n}: italicAngle {post.italicAngle}, caret {hhea.caretSlopeRise}/{hhea.caretSlopeRun}/{hhea.caretOffset}")
    # WOFF2 는 fontTools 가 압축 해제하면서 bit 11(0x0800, "lossless")을 세우므로 0x0803 은 TTF 0x0003 과 동등(파일 자체 차이 아님).
    (rep.passed if head.flags in (3, 0x803) else rep.warn)("head.flags", f"{n}: head.flags 0x{head.flags:04X}{' (WOFF2 해제 시 bit11 부가 — TTF 0x0003 과 동등)' if head.flags == 0x803 else ''}")
    (rep.passed if abs(head.fontRevision - float(Q.VERSION)) < 0.0005 else rep.fail)("fontRevision", f"{n}: head.fontRevision {head.fontRevision}")
    (rep.passed if head.lowestRecPPEM == 7 else rep.info)("lowestRecPPEM", f"{n}: lowestRecPPEM {head.lowestRecPPEM}")
    (rep.passed if post.formatType == 2.0 and post.isFixedPitch == 0 else rep.fail)("post", f"{n}: post format {post.formatType}, isFixedPitch {post.isFixedPitch}")
    (rep.passed if os2.version == 4 else rep.warn)("os2.version", f"{n}: OS/2 version {os2.version}")
    (rep.passed if (os2.sxHeight, os2.sCapHeight) == (1086, 1448) else rep.warn)("xh/cap", f"{n}: sxHeight {os2.sxHeight} sCapHeight {os2.sCapHeight}")
    tables = sorted(f.keys())
    (rep.passed if "DSIG" not in f else rep.fail)("DSIG", f"{n}: DSIG {'없음' if 'DSIG' not in f else '있음'}")
    (rep.passed if ("glyf" in f and "loca" in f and "CFF " not in f) else rep.fail)("glyf", f"{n}: glyf/loca {('glyf' in f, 'loca' in f)}, CFF {'CFF ' in f}")
    if "gasp" in f:
        rep.passed("gasp", f"{n}: gasp {f['gasp'].gaspRange}")
    else:
        rep.fail("gasp", f"{n}: gasp 없음")
    # prep: QA 티켓 4(fontbakery smart_dropout)에 따라 6차 빌드에서 **의도적으로 추가**됨 → 있어야 정상(스펙 03 §"cvt/fpgm/prep 없음"은 갱신 필요, 티켓 8).
    if "prep" in f:
        rep.passed("tables", f"{n}: prep 존재 — 티켓 4(smart dropout) 대응으로 의도된 추가")
    else:
        rep.fail("tables", f"{n}: prep 없음 (티켓 4: smart dropout 제어 필요)")
    for t in ("fpgm", "cvt ", "vhea", "vmtx", "BASE", "HVAR", "MVAR"):
        if t in f:
            rep.warn("tables", f"{n}: {t} 존재(스펙: 없음)")
    rep.info("tables", f"{n}: 테이블 {tables}")
    (rep.passed if "meta" in f else rep.info)("meta", f"{n}: meta {'있음 ' + str({k: v for k, v in f['meta'].data.items()}) if 'meta' in f else '없음'}")
    # 한글 진행폭
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    bad = []
    groups = {"음절": range(0xAC00, 0xD7A4), "호환자모": range(0x3131, 0x318F), "첫가끝자모": range(0x1100, 0x1200),
              "자모확장A": range(0xA960, 0xA97D), "자모확장B": list(range(0xD7B0, 0xD7C7)) + list(range(0xD7CB, 0xD7FC)), "괘선": range(0x2500, 0x25A0)}
    for gname, rng in groups.items():
        advs = {hmtx[cmap[c]][0] for c in rng if c in cmap}
        (rep.passed if advs <= {1770} else rep.fail)("hangul-adv", f"{n}: {gname} adv 집합 {sorted(advs)} (기대 {{1770}})")
    for c, exp_adv in ((0x302E, 481), (0x302F, 481), (0xFFA0, 885)):
        if c in cmap:
            a = hmtx[cmap[c]][0]
            (rep.passed if a == exp_adv else rep.fail)("hangul-adv", f"{n}: U+{c:04X} adv {a} (기대 {exp_adv})")
    # 대표 글립 bbox 원본 동일(정적: Pretendard alternative TTF)
    if not is_vf:
        op = Q.PRETENDARD_TTF / f"Pretendard-{w}.ttf"
        if op.exists():
            of = TTFont(op)
            ocmap = of.getBestCmap()
            diffs = []
            for ch in REPR:
                cp = ord(ch)
                if cp in cmap and cp in ocmap:
                    b1, b2 = bbox(f, cmap[cp]), bbox(of, ocmap[cp])
                    a1, a2 = hmtx[cmap[cp]][0], of["hmtx"][ocmap[cp]][0]
                    if b1 != b2 or a1 != a2:
                        diffs.append((ch, b1, b2, a1, a2))
            (rep.passed if not diffs else rep.fail)("bbox=orig", f"{n}: 대표 글립 {len(REPR)}자 bbox·adv Pretendard-{w}.ttf 와 {'동일' if not diffs else '차이 ' + str(diffs[:3])}")
            # 원본 메트릭 참고
            oo = of["OS/2"]
            rep.info("orig", f"Pretendard-{w}.ttf: typo {oo.sTypoAscender}/{oo.sTypoDescender}/{oo.sTypoLineGap} win {oo.usWinAscent}/{oo.usWinDescent} hhea {of['hhea'].ascent}/{of['hhea'].descent} fsSel 0x{oo.fsSelection:X} underline {of['post'].underlinePosition}/{of['post'].underlineThickness} xAvg {oo.xAvgCharWidth} → ours xAvg {os2.xAvgCharWidth}")
            of.close()
    # head bbox yMax(승인 예외 근거 기록)
    rep.info("bbox", f"{n}: head bbox ({head.xMin}, {head.yMin}, {head.xMax}, {head.yMax}) — yMax {head.yMax} vs winAscent {os2.usWinAscent}, yMin {head.yMin} vs -winDescent {-os2.usWinDescent}")
    # 피처
    gsub, gsub_empty = features(f, "GSUB")
    gpos, gpos_empty = features(f, "GPOS")
    key = "vf" if is_vf else "static"
    exp_lost = {"ss16", "rlig"} if is_vf else {"ss16"}
    lost = (orig_feats[key]["GSUB"] - gsub) | (orig_feats[key]["GPOS"] - gpos)
    gained = (gsub - orig_feats[key]["GSUB"]) | (gpos - orig_feats[key]["GPOS"])
    total = len(gsub) + len(gpos)
    ok = lost <= exp_lost and not gained and not gsub_empty and not gpos_empty and total == 49
    (rep.passed if ok else rep.fail)("features", f"{n}: GSUB {len(gsub)} + GPOS {len(gpos)} = {total}, 사라짐 {sorted(lost)} (허용 {sorted(exp_lost)}), 추가 {sorted(gained)}, 빈 피처 {gsub_empty + gpos_empty}")
    for tag in ("vert", "vrt2", "palt", "halt", "ljmo", "vjmo", "tjmo", "liga", "lnum", "onum"):
        if tag in gsub | gpos:
            rep.fail("features", f"{n}: 스펙상 없어야 할 피처 {tag} 존재")
    if "GSUB" in f:
        scripts = {sr.ScriptTag: [ls.LangSysTag for ls in sr.Script.LangSysRecord] for sr in f["GSUB"].table.ScriptList.ScriptRecord}
        rep.info("scripts", f"{n}: GSUB 스크립트 {scripts}")
    # STAT
    if "STAT" in f:
        st = f["STAT"].table
        axes = [a.AxisTag for a in st.DesignAxisRecord.Axis]
        avs = []
        if st.AxisValueArray:
            for av in st.AxisValueArray.AxisValue:
                nm = f["name"].getDebugName(av.ValueNameID)
                if av.Format == 1:
                    avs.append((1, av.Value, nm, av.Flags))
                elif av.Format == 2:
                    avs.append((2, av.NominalValue, nm, av.Flags))
                elif av.Format == 3:
                    avs.append((3, av.Value, nm, av.Flags, av.LinkedValue))
        ver_ok = st.Version == 0x00010002
        fallback = f["name"].getDebugName(st.ElidedFallbackNameID) if hasattr(st, "ElidedFallbackNameID") else None
        if is_vf:
            ok = axes == ["wght"] and len(avs) == 9 and any(a[0] == 3 and a[1] == 400 and a[4] == 700 and (a[3] & 2) for a in avs) and ver_ok
            (rep.passed if ok else rep.fail)("STAT", f"{n}: 축 {axes}, 값 {len(avs)} {avs}, ver 0x{st.Version:X}, fallback {fallback!r}")
        else:
            ok = axes == ["wght"] and len(avs) == 1 and avs[0][1] == wv and ver_ok and (avs[0][0] == 3 if w == "Regular" else avs[0][0] == 1)
            (rep.passed if ok else rep.fail)("STAT", f"{n}: 축 {axes}, 값 {avs}, ver 0x{st.Version:X}, fallback {fallback!r}")
    else:
        rep.fail("STAT", f"{n}: STAT 없음")
    # fvar
    if is_vf:
        fv = f["fvar"]
        ax = [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in fv.axes]
        inst = [(f["name"].getDebugName(i.subfamilyNameID), i.coordinates["wght"], f["name"].getDebugName(i.postscriptNameID)) for i in fv.instances]
        exp_inst = [(wn, float(wv_), f"JennySansVariable-{wn}") for wn, wv_ in Q.WEIGHTS]
        (rep.passed if ax == [("wght", 100.0, 400.0, 900.0)] else rep.fail)("fvar", f"{n}: 축 {ax}")
        (rep.passed if inst == exp_inst else rep.fail)("fvar", f"{n}: 인스턴스 {inst}")
        rep.info("fvar", f"{n}: avar {'있음' if 'avar' in f else '없음'}, gvar 글립 {len(f['gvar'].variations) if 'gvar' in f else 0}")
    # codePageRange / unicodeRange
    rep.info("codepage", f"{n}: ulCodePageRange1 0x{os2.ulCodePageRange1:08X} / 2 0x{os2.ulCodePageRange2:08X}; ulUnicodeRange 0x{os2.ulUnicodeRange1:08X} 0x{os2.ulUnicodeRange2:08X} 0x{os2.ulUnicodeRange3:08X} 0x{os2.ulUnicodeRange4:08X}")
    (rep.passed if os2.ulCodePageRange1 == 0x2028009F else rep.warn)("codepage", f"{n}: ulCodePageRange1 {'== 0x2028009F(spec 03 §4)' if os2.ulCodePageRange1 == 0x2028009F else '≠ 0x2028009F'}")
    rep.info("misc", f"{n}: xAvgCharWidth {os2.xAvgCharWidth}, usMaxContext {os2.usMaxContext}, first/last {os2.usFirstCharIndex:#x}/{os2.usLastCharIndex:#x}, strikeout {os2.yStrikeoutSize}/{os2.yStrikeoutPosition}, numGlyphs {f['maxp'].numGlyphs}, hhea.advanceWidthMax {hhea.advanceWidthMax}")
    f.close()
    return vals, ul, head.unitsPerEm


def main():
    rep = Q.Report("메트릭·OS/2·STAT·피처 동일성 (게이트 5, 3·4 보조)")
    # 원본 피처 집합
    orig = {}
    op = Q.PRETENDARD_TTF / "Pretendard-Regular.ttf"
    for key, p in (("static", op), ("vf", Q.PRETENDARD_VF)):
        if p.exists():
            of = TTFont(p, lazy=True)
            orig[key] = {"GSUB": features(of, "GSUB")[0], "GPOS": features(of, "GPOS")[0]}
            rep.info("orig-features", f"{p.name}: GSUB {len(orig[key]['GSUB'])} GPOS {len(orig[key]['GPOS'])}")
            of.close()
        else:
            rep.warn("orig-features", f"{p} 없음 — 피처 소실 비교 불가")
            orig[key] = {"GSUB": set(), "GPOS": set()}
    allvals = {}
    for p in Q.ALL_FONTS:
        if not p.exists():
            rep.fail("file", f"{p} 없음")
            continue
        allvals[p.name] = check(p, rep, orig)
    vs = set(allvals.values())
    (rep.passed if len(vs) == 1 else rep.fail)("identity", f"{len(allvals)} 파일 메트릭 튜플 {'전부 동일 ' + str(next(iter(vs))) if len(vs) == 1 else '불일치 ' + str(vs)}")
    # Panose 단조 증가
    rep.write("metrics")


if __name__ == "__main__":
    main()
