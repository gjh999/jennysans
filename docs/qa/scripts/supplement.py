# -*- coding: utf-8 -*-
"""
보충 글립 스펙 검사 — docs/spec/07-supplement.md §8 (정적 9종 + VF 기본 인스턴스), font-qa 독립 측정.
 2. 한글류 400 글립 adv 1770(방점 481);
    hangul-pos(2026-09-07 정정, QA 티켓 5·AGENTS §8): 옛 호환자모 U+3165–U+318E 보충 글립 전부에 대해
      |(J대상하단 − J ㄴ하단) − sy(1.965)×(N대상하단 − N ㄴ하단)| ≤ 6 unit
    N = 보충원본 Noto Sans KR VF 를 해당 wght 로 **QA 가 직접 인스턴스**해 실측(빌드 기록 미사용).
    (옛 기준 "ㅥ 하단 ≈ ㄴ 하단 ±15" 은 틀린 전제였다 — Noto 자신이 ㅥ 을 ㄴ 보다 아래에 그린다. `build/ticket5-measure.md`)
    초성 자모(1100–1112) 상단 ≤ 음절 상단(가 yMax)+여유
 3. 참조 관계(웨이트별): ㉠~① 높이 ±1% · ㈀~㈜ ±1% · ▣~■ ±2 unit · ◐~○ ±1% · ⊂~≠ ±2% · ∬~∫ ±1% · ♠~♥ ±2% · ☎ adv ≈ ★ ±10% · 〓~■ — 실측값 표
 4. 괘선 (a)–(c),(e): adv 1770, 가로 연결 xMin 0/xMax 1770, 세로 연결 yMin -494/yMax 1950, █ 셀 완전 채움 ((d) 렌더는 render.py)
 5. 합성 4자: ⅔ 컴포지트 = ⅓ 동형(부품 3·순서), ∼ bbox = ∽ 좌우 대칭, ≒ 4윤곽 40점·adv = '=' adv, ◈ 3윤곽 12점·adv = ◇ adv
 6. 미러 글립 윤곽 방향(AreaPen 부호) = Pretendard 글립(∽·H)과 동일
 7. 보충 글립이 GSUB/GPOS 룩업 어디에도 참조되지 않음(Noto 피처 미유입)
실행: PYTHONUTF8=1 python docs/qa/scripts/supplement.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.pens.boundsPen import BoundsPen  # noqa: E402
from fontTools.pens.areaPen import AreaPen  # noqa: E402
from fontTools.pens.recordingPen import DecomposingRecordingPen  # noqa: E402

# ---- hangul-pos (QA 티켓 5 정정판) ----------------------------------------
SY_HANGUL = 1.965          # spec 07 §4-1·§6 hangul 규칙의 고정 세로 스케일
HANGUL_POS_TOL = 6         # unit(2048 UPM). build/ticket5-measure.md §3 — 실측 최대 오차 1.1u
NOTO_CACHE = Path(tempfile.gettempdir()) / "jennysans-qa-noto"   # QA 전용 캐시(빌더 build/cache 와 별개)
_NOTO_BBOX = {}
REF_PAIRS = [  # (대상, 참조, 허용 상대오차, 비교 항목[, 기대 비율]) — 07 §8-3 개정(2026-09-06): 높이비 = Noto 원본 높이비 ±2%
    ("㉠", "①", 0.01, "h"), ("㈀", "㈜", 0.01, "h"), ("▣", "■", 2, "bbox"), ("◐", "○", 0.02, "h", 0.978), ("⊂", "≠", 0.02, "h", 0.912),
    ("∬", "∫", 0.01, "h"), ("♠", "♥", 0.02, "h", 1.093), ("☎", "★", 0.10, "adv"), ("〓", "■", 0.01, "h"),
    ("ⓐ", "①", 0.01, "h"), ("⑴", "㈜", 0.01, "h"), ("∀", "H", None, "h"), ("◎", "○", 0.01, "h"), ("◌", "○", 0.02, "h", 1.020),
]
BOX_H = [0x2500, 0x2501, 0x2550, 0x253C, 0x254B, 0x2566, 0x2569, 0x256C, 0x2588, 0x252C, 0x2534]
BOX_V = [0x2502, 0x2503, 0x2551, 0x253C, 0x254B, 0x2560, 0x2563, 0x256C, 0x2588, 0x251C, 0x2524]


def bb(font, cp, cmap=None):
    cmap = cmap or font.getBestCmap()
    g = cmap.get(cp)
    if g is None:
        return None
    gs = font.getGlyphSet()
    pen = BoundsPen(gs)
    gs[g].draw(pen)
    return pen.bounds


def adv(font, cp, cmap=None):
    cmap = cmap or font.getBestCmap()
    return font["hmtx"][cmap[cp]][0]


def noto_bbox(weight_value, cps):
    """보충원본 Noto Sans KR VF 를 `wght=weight_value` 로 인스턴스해 코드포인트별 bbox(원본 UPM 1000)를 반환.

    빌드 기록(`build/static-summary.json` 의 src_bbox)이나 빌더 캐시를 쓰지 않는 **QA 독립 구현**:
    원본 VF 를 필요한 코드포인트로 서브셋(1회) → fontTools.varLib.instancer 로 웨이트별 인스턴스(캐시) → BoundsPen 측정.
    """
    from fontTools import subset
    from fontTools.varLib import instancer

    key = (weight_value, tuple(sorted(cps)))
    if key in _NOTO_BBOX:
        return _NOTO_BBOX[key]
    NOTO_CACHE.mkdir(parents=True, exist_ok=True)
    import hashlib
    tag = hashlib.sha256(",".join(f"{c:04X}" for c in sorted(cps)).encode()).hexdigest()[:10]
    vf = NOTO_CACHE / f"noto-qa-{tag}[wght].ttf"
    if not vf.exists():
        opts = subset.Options()
        opts.layout_features = []
        opts.notdef_outline = True
        opts.drop_tables += ["DSIG"]
        f = TTFont(Q.NOTO_VF)
        s = subset.Subsetter(options=opts)
        s.populate(unicodes=sorted(cps))
        s.subset(f)
        f.save(vf)
        f.close()
    inst_path = NOTO_CACHE / f"noto-qa-{tag}-{weight_value}.ttf"
    if not inst_path.exists():
        f = TTFont(vf)
        instancer.instantiateVariableFont(f, {"wght": weight_value}, inplace=True)
        f.save(inst_path)
        f.close()
    f = TTFont(inst_path)
    cm = f.getBestCmap()
    out = {}
    for c in sorted(cps):
        b = bb(f, c, cm)
        if b:
            out[c] = b
    f.close()
    _NOTO_BBOX[key] = out
    return out


def weight_value_of(path, font):
    """정적은 파일명, VF 는 fvar wght 기본값(= 기본 인스턴스)."""
    if "fvar" in font:
        for a in font["fvar"].axes:
            if a.axisTag == "wght":
                return int(a.defaultValue)
    return Q.WEIGHT_VALUE[path.stem.split("-")[1]]


def contours(font, cp, cmap):
    g = font["glyf"][cmap[cp]]
    if g.isComposite():
        return ("composite", [(c.glyphName, getattr(c, "x", 0), getattr(c, "y", 0), getattr(c, "transform", None)) for c in g.components])
    coords, ends, flags = g.getCoordinates(font["glyf"])
    return ("simple", g.numberOfContours, len(coords))


def outer_area_sign(font, cp, cmap):
    """가장 큰 |면적| 윤곽의 부호."""
    g = font["glyf"][cmap[cp]]
    gs = font.getGlyphSet()
    rp = DecomposingRecordingPen(gs)
    gs[cmap[cp]].draw(rp)
    # 윤곽별로 나눠 면적 계산
    areas = []
    cur = []
    for op, args in rp.value:
        cur.append((op, args))
        if op in ("closePath", "endPath"):
            ap = AreaPen(gs)
            for o, a in cur:
                getattr(ap, o)(*a)
            areas.append(ap.value)
            cur = []
    if not areas:
        return 0
    big = max(areas, key=abs)
    return 1 if big > 0 else -1


def lookup_glyphs(table):
    """GSUB/GPOS 테이블의 모든 Coverage/ClassDef 에 등장하는 글립명 집합(재귀 순회)."""
    seen = set()
    out = set()

    def walk(o):
        if id(o) in seen:
            return
        seen.add(id(o))
        if hasattr(o, "glyphs") and isinstance(getattr(o, "glyphs"), (list, tuple, set)):
            out.update(o.glyphs)
        if hasattr(o, "classDefs") and isinstance(o.classDefs, dict):
            out.update(o.classDefs.keys())
        if hasattr(o, "mapping") and isinstance(o.mapping, dict):
            out.update(o.mapping.keys())
            for v in o.mapping.values():
                if isinstance(v, str):
                    out.add(v)
                elif isinstance(v, (list, tuple)):
                    out.update(x for x in v if isinstance(x, str))
        if hasattr(o, "alternates") and isinstance(o.alternates, dict):
            out.update(o.alternates.keys())
        if hasattr(o, "ligatures") and isinstance(o.ligatures, dict):
            out.update(o.ligatures.keys())
        if hasattr(o, "__dict__"):
            for v in vars(o).values():
                if isinstance(v, (list, tuple)):
                    for x in v:
                        if hasattr(x, "__dict__"):
                            walk(x)
                elif hasattr(v, "__dict__"):
                    walk(v)
    walk(table.table.LookupList)
    return out


def check_font(path, rep, pret_cmap_set, rows, pos_rows):
    f = TTFont(path)
    n = path.name
    cmap = f.getBestCmap()
    sup = sorted(set(cmap) - pret_cmap_set)
    wv = weight_value_of(path, f)
    # 2. 한글류
    hang = [c for c in sup if 0x1100 <= c <= 0x11FF or 0x3165 <= c <= 0x318E or 0xA960 <= c <= 0xA97C or 0xD7B0 <= c <= 0xD7FB]
    bad = [c for c in hang if adv(f, c, cmap) != 1770]
    (rep.passed if not bad else rep.fail)("hangul-adv", f"{n}: 한글류 보충 {len(hang)} 글립 adv 1770 (위반 {len(bad)})")
    dots = [c for c in (0x302E, 0x302F) if c in cmap]
    (rep.passed if all(adv(f, c, cmap) == 481 for c in dots) else rep.fail)("hangul-adv", f"{n}: 방점 adv {[adv(f, c, cmap) for c in dots]} (기대 481)")
    # hangul-pos (2026-09-07 정정): 원본이 가진 ㄴ 대비 기저선 차이를 sy 배로 정확히 재현했는가
    sup_set = set(sup)
    pos_cps = [c for c in range(0x3165, 0x318F) if c in cmap and c in sup_set]
    b_3134 = bb(f, 0x3134, cmap)
    if b_3134 and pos_cps:
        nb = noto_bbox(wv, set(pos_cps) | {0x3134})
        if 0x3134 in nb:
            jn, nn = b_3134[1], nb[0x3134][1]
            off, worst, worst_cp = [], 0.0, None
            for c in pos_cps:
                b = bb(f, c, cmap)
                if b is None or c not in nb:
                    continue
                exp = SY_HANGUL * (nb[c][1] - nn)
                d = (b[1] - jn) - exp
                if abs(d) > worst:
                    worst, worst_cp = abs(d), c
                if abs(d) > HANGUL_POS_TOL:
                    off.append((f"U+{c:04X}", b[1] - jn, round(exp, 1), round(d, 1)))
                if c in (0x3165, 0x3167, 0x3186, 0x318D) or abs(d) > HANGUL_POS_TOL:
                    pos_rows.append((n, f"U+{c:04X} {chr(c)}", f"{b[1]}/{jn}", b[1] - jn,
                                     f"{nb[c][1]}/{nn}", f"{nb[c][1] - nn:+}", f"{exp:+.1f}", f"{d:+.1f}",
                                     "PASS" if abs(d) <= HANGUL_POS_TOL else "FAIL"))
            (rep.passed if not off else rep.fail)(
                "hangul-pos",
                f"{n}: U+3165–318E 보충 {len(pos_cps)}자 원본 기저선차 재현 |J차 − {SY_HANGUL}×N차| ≤ {HANGUL_POS_TOL}u "
                f"(최대 {worst:.1f}u @ U+{worst_cp:04X}, 위반 {len(off)}{'' if not off else ' ' + str(off[:6])})")
        else:
            rep.warn("hangul-pos", f"{n}: Noto 인스턴스에 ㄴ(U+3134) 없음 — 미측정")
    else:
        rep.warn("hangul-pos", f"{n}: ㄴ 또는 U+3165–318E 보충 글립 없음 — 미측정")
    top_ga = bb(f, 0xAC00, cmap)[3]
    over = [c for c in range(0x1100, 0x1113) if bb(f, c, cmap) and bb(f, c, cmap)[3] > top_ga + 20]
    (rep.passed if not over else rep.warn)("hangul-pos", f"{n}: 초성 자모 U+1100–1112 상단 ≤ 가 yMax {top_ga}+20: 위반 {[f'U+{c:04X}' for c in over]}")
    # 3. 참조 관계 — 기대 비율은 **Noto 원본에서 직접 실측**(spec 07 §8-3 개정판). 못 재면 스펙 표기값으로 폴백.
    h_cps = {ord(p[i]) for p in REF_PAIRS if p[3] == "h" for i in (0, 1)}
    nref = noto_bbox(wv, h_cps)
    for pair in REF_PAIRS:
        tgt, ref, tol, kind = pair[:4]
        expect = pair[4] if len(pair) > 4 else 1.0
        exp_src = "spec"
        ct, cr = ord(tgt), ord(ref)
        if kind == "h" and ct in nref and cr in nref:
            hn_t, hn_r = nref[ct][3] - nref[ct][1], nref[cr][3] - nref[cr][1]
            if hn_r:
                expect, exp_src = hn_t / hn_r, "Noto실측"
        if ct not in cmap or cr not in cmap:
            rep.warn("ref", f"{n}: {tgt}/{ref} cmap 없음")
            continue
        bt, br = bb(f, ct, cmap), bb(f, cr, cmap)
        at, ar = adv(f, ct, cmap), adv(f, cr, cmap)
        ht, hr = bt[3] - bt[1], br[3] - br[1]
        if kind == "h":
            ratio = ht / hr
            ok = tol is None or abs(ratio - expect) <= tol
            allow = f"{expect:.3f}±{tol}({exp_src})" if tol else "-"
            rows.append((n, f"{tgt}~{ref}", f"h {ht}/{hr}", f"{ratio:.3f}", allow, f"adv {at}/{ar}", "PASS" if ok else "FAIL"))
        elif kind == "bbox":
            dmax = max(abs(x - y) for x, y in zip(bt, br))
            ok = dmax <= tol
            rows.append((n, f"{tgt}~{ref}", f"bbox {bt}/{br}", f"Δ{dmax}", f"±{tol}u", f"adv {at}/{ar}", "PASS" if ok else "FAIL"))
        else:
            ratio = at / ar
            ok = abs(ratio - 1) <= tol
            rows.append((n, f"{tgt}~{ref}", f"adv {at}/{ar}", f"{ratio:.3f}", f"±{tol}", "", "PASS" if ok else "FAIL"))
        if not ok:
            rep.warn("ref", f"{n}: {tgt}~{ref} 스펙 07 §8-3 허용치 밖 ({rows[-1][3]}, {rows[-1][4]})")
    # 4. 괘선
    box = [c for c in range(0x2500, 0x25A0) if c in cmap]
    bad_adv = [c for c in box if adv(f, c, cmap) != 1770]
    bx = [c for c in BOX_H if c in cmap and (bb(f, c, cmap)[0], bb(f, c, cmap)[2]) != (0, 1770)]
    by = [c for c in BOX_V if c in cmap and (bb(f, c, cmap)[1], bb(f, c, cmap)[3]) != (-494, 1950)]
    full = bb(f, 0x2588, cmap)
    (rep.passed if not (bad_adv or bx or by) and full == (0, -494, 1770, 1950) else rep.fail)(
        "box", f"{n}: 괘선·블록 {len(box)} 글립 adv 1770 위반 {len(bad_adv)}, 가로 연결 위반 {[f'U+{c:04X}' for c in bx]}, 세로 연결 위반 {[f'U+{c:04X}' for c in by]}, █ bbox {full}")
    # 5. 합성 4자
    c23, c13 = contours(f, 0x2154, cmap), contours(f, 0x2153, cmap)
    ok = c23[0] == "composite" and c13[0] == "composite" and len(c23[1]) == 3 == len(c13[1]) and [x[0] for x in c23[1]][1] == "fraction"
    (rep.passed if ok else rep.fail)("synth", f"{n}: ⅔ {c23} / ⅓ {c13}")
    b_sim, b_rev = bb(f, 0x223C, cmap), bb(f, 0x223D, cmap)
    a_sim, a_rev = adv(f, 0x223C, cmap), adv(f, 0x223D, cmap)
    ok = b_sim and b_rev and (b_sim[2] - b_sim[0]) == (b_rev[2] - b_rev[0]) and (b_sim[1], b_sim[3]) == (b_rev[1], b_rev[3]) and abs((b_sim[0] + b_sim[2]) - (b_rev[0] + b_rev[2])) <= 2 and a_sim == a_rev
    (rep.passed if ok else rep.fail)("synth", f"{n}: ∼ bbox {b_sim} adv {a_sim} vs ∽ bbox {b_rev} adv {a_rev} (폭·높이·중심 x 동일)")
    c_ap = contours(f, 0x2252, cmap)
    a_eq = adv(f, 0x003D, cmap)
    c_pd = contours(f, 0x002E, cmap)
    c_eqc = contours(f, 0x003D, cmap)
    exp_pts = (c_eqc[2] if c_eqc[0] == "simple" else 0) + 2 * (c_pd[2] if c_pd[0] == "simple" else 0)
    ok = c_ap[0] == "simple" and c_ap[1] == 4 and c_ap[2] == exp_pts and adv(f, 0x2252, cmap) == a_eq
    (rep.passed if ok else rep.fail)("synth", f"{n}: ≒ {c_ap} adv {adv(f, 0x2252, cmap)} (기대 4윤곽, 점 = '='{c_eqc[2] if c_eqc[0] == 'simple' else '?'} + 2×period{c_pd[2] if c_pd[0] == 'simple' else '?'} = {exp_pts} [spec 07 §8-5 의 40점은 Regular 기준], adv = '=' {a_eq})")
    c_di = contours(f, 0x25C8, cmap)
    a_dia = adv(f, 0x25C7, cmap)
    ok = c_di[0] == "simple" and c_di[1] == 3 and c_di[2] == 12 and adv(f, 0x25C8, cmap) == a_dia
    (rep.passed if ok else rep.fail)("synth", f"{n}: ◈ {c_di} adv {adv(f, 0x25C8, cmap)} (기대 3윤곽 12점, adv = ◇ {a_dia})")
    for cp, comp in ((0xFFE2, "logicalnot"), (0xFFE3, "macron"), (0xFFE4, "brokenbar")):
        if cp in cmap:
            c = contours(f, cp, cmap)
            ok = c[0] == "composite" and len(c[1]) == 1 and c[1][0][0] == comp and adv(f, cp, cmap) == 1920
            (rep.passed if ok else rep.fail)("synth", f"{n}: U+{cp:04X} {c} adv {adv(f, cp, cmap)} (기대 {comp} 컴포지트, adv 1920)")
    # 6. 미러 방향
    s_sim, s_rev, s_h = outer_area_sign(f, 0x223C, cmap), outer_area_sign(f, 0x223D, cmap), outer_area_sign(f, 0x0048, cmap)
    (rep.passed if s_sim == s_rev == s_h else rep.fail)("mirror", f"{n}: 외곽 윤곽 면적 부호 ∼ {s_sim}, ∽ {s_rev}, H {s_h}")
    # 7. 룩업 미참조
    sup_names = {cmap[c] for c in sup}
    ref = set()
    for t in ("GSUB", "GPOS"):
        if t in f:
            ref |= lookup_glyphs(f[t])
    hit = sorted(sup_names & ref)
    (rep.passed if not hit else rep.fail)("lookups", f"{n}: 보충 {len(sup_names)} 글립 중 GSUB/GPOS 룩업 참조 {len(hit)} {hit[:10]}")
    # GDEF 클래스
    if "GDEF" in f and f["GDEF"].table.GlyphClassDef:
        cd = f["GDEF"].table.GlyphClassDef.classDefs
        inc = sorted(g for g in sup_names if g in cd)
        rep.info("gdef", f"{n}: 보충 글립 중 GDEF GlyphClassDef 등재 {len(inc)} {inc[:5]}")
    f.close()


def main():
    rep = Q.Report("보충 글립 스펙 검사 (07 §8)")
    pret = TTFont(Q.PRETENDARD_TTF / "Pretendard-Regular.ttf", lazy=True)
    pret_set = set(pret.getBestCmap())
    rows, pos_rows = [], []
    for p in Q.STATIC_TTFS + [Q.VF_TTF]:
        check_font(p, rep, pret_set, rows, pos_rows)
    rep.md("## 참조 관계 실측 (07 §8-3, 기대비 = Noto 원본 실측)\n\n"
           + Q.table(["파일", "쌍", "실측", "비/차", "허용(기대)", "adv", "판정"], rows))
    rep.md(f"## hangul-pos 실측 (QA 티켓 5 정정식, 허용 ±{HANGUL_POS_TOL}u · sy {SY_HANGUL})\n\n"
           "표본 4자(ㅥ U+3165·ㅧ U+3167·ㆆ U+3186·ㆍ U+318D) + 위반 전부. J = 산출물(UPM 2048), N = Noto 인스턴스(UPM 1000).\n\n"
           + Q.table(["파일", "글립", "J 대상/ㄴ 하단", "J 차", "N 대상/ㄴ 하단", "N 차", "기대 sy×N차", "오차", "판정"], pos_rows))
    rep.write("supplement")


if __name__ == "__main__":
    main()
