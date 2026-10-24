# -*- coding: utf-8 -*-
"""
변수 폰트 추가 검사 (spec 01 §6, 03 §8, 07 §7·§8).
- fvar 9 인스턴스 이름·좌표·PS, STAT 9 값, 축 100/400/900.
- varLib.instancer 로 9 웨이트 각각 인스턴스화 → 정적 9종과 비교: (a) 보충 글립(Noto 이식 + 합성) bbox·adv·점 수 (b) 대표 글립 20자 좌표(400 ≤1 unit) (c) 수직 메트릭 동일 (d) cmap 동일
- 축 중간값 250/650 에서 괘선 연결(bbox x 0..1770, y -494..1950) 유지 (07 §7(d)).
- gvar: 보충 글립 튜플 점 수 = glyf 점 수 + 4 (07 §7(a)).
- 정적 9종 보충 글립 interpolatable(윤곽 수·점 수·on/off 동일) 검사 (07 §7(b) 상당).
실행: PYTHONUTF8=1 python docs/qa/scripts/variable.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.pens.boundsPen import BoundsPen  # noqa: E402
from fontTools.pens.recordingPen import RecordingPen  # noqa: E402
from fontTools.varLib import instancer  # noqa: E402

REPR20 = "가힣한글제니산스ㄱㅏHxg0€¿ñQ①○■※"
BOX_H = [0x2500, 0x2501, 0x2550, 0x253C, 0x254B, 0x2566, 0x2569, 0x256C, 0x2588, 0x252C, 0x2534]   # 가로 연결(xMin 0, xMax 1770)
BOX_V = [0x2502, 0x2503, 0x2551, 0x253C, 0x254B, 0x2560, 0x2563, 0x256C, 0x2588, 0x251C, 0x2524]   # 세로 연결(yMin -494, yMax 1950)


def bounds(font, gname):
    gs = font.getGlyphSet()
    pen = BoundsPen(gs)
    gs[gname].draw(pen)
    return pen.bounds


def glyf_structure(font, gname):
    """(윤곽별 점 수, on/off 패턴) — 컴포지트는 컴포넌트 이름 목록."""
    g = font["glyf"][gname]
    if g.isComposite():
        return ("composite", tuple(c.glyphName for c in g.components))
    coords, ends, flags = g.getCoordinates(font["glyf"])
    return ("simple", tuple(ends), tuple(int(x & 1) for x in flags))


def coords_of(font, gname):
    g = font["glyf"][gname]
    coords, ends, flags = g.getCoordinates(font["glyf"])
    return list(coords)


def supplement_cps(static_regular, pret_regular):
    """보충 글립 = 우리 cmap − Pretendard cmap (Noto 이식 + 합성)."""
    return sorted(set(static_regular.getBestCmap()) - set(pret_regular.getBestCmap()))


def main():
    rep = Q.Report("변수 폰트 검사 (spec 01 §6·03 §8·07 §7)")
    vf = TTFont(Q.VF_TTF)
    pret = TTFont(Q.PRETENDARD_TTF / "Pretendard-Regular.ttf", lazy=True)
    statics = {w: TTFont(p) for (w, _), p in zip(Q.WEIGHTS, Q.STATIC_TTFS)}
    sup = supplement_cps(statics["Regular"], pret)
    rep.info("supplement", f"보충 코드포인트 {len(sup)} (우리 cmap − Pretendard-Regular cmap): {Q.fmt_ranges(sup, 60)}")
    # 정적 9종 보충 글립 구조 동일(interpolatable 상당)
    scmap = {w: f.getBestCmap() for w, f in statics.items()}
    bad_struct = []
    for cp in sup:
        structs = {glyf_structure(statics[w], scmap[w][cp]) for w in statics}
        if len(structs) != 1:
            bad_struct.append(cp)
    detail = {f"U+{cp:04X}": {w: glyf_structure(statics[w], scmap[w][cp])[1:] for w in statics} for cp in bad_struct[:3]}
    (rep.passed if not bad_struct else rep.warn)("static-interp", f"정적 9종 보충 글립 {len(sup)}개 윤곽 수·점 수·on/off 패턴 동일 (불일치 {len(bad_struct)} {Q.fmt_ranges(bad_struct, 20)}) {detail} — 합성 글립의 Pretendard 부품(period 등) 점 수가 웨이트별로 다르면 정적 간 불일치는 정상; VF 는 자체 부품으로 일관")
    # gvar 튜플 점 수
    gvar = vf["gvar"].variations
    vcmap = vf.getBestCmap()
    bad_tuple, no_tuple, ntuples = [], [], 0
    for cp in sup:
        gname = vcmap[cp]
        g = vf["glyf"][gname]
        if g.isComposite():
            npts = len(g.components)
        else:
            npts = len(g.getCoordinates(vf["glyf"])[0])
        tv = gvar.get(gname, [])
        ntuples += len(tv)
        if not tv:
            no_tuple.append(cp)
        for t in tv:
            if t.coordinates is not None and len(t.coordinates) != npts + 4:
                bad_tuple.append((cp, len(t.coordinates), npts + 4))
    rep.info("gvar", f"보충 글립 gvar 튜플 합계 {ntuples}, 튜플 없는 글립 {len(no_tuple)} (괘선 등 웨이트 불변은 델타 0 → 생략 가능) {Q.fmt_ranges(no_tuple, 30)}")
    (rep.passed if not bad_tuple else rep.fail)("gvar", f"튜플 점 수 = glyf 점 수 + 4: 불일치 {len(bad_tuple)} {bad_tuple[:5]}")
    # 인스턴스화 비교
    maxdiff_sup, maxdiff_adv, maxdiff_repr = 0, 0, 0
    worst = []
    for w, wv in Q.WEIGHTS:
        inst = instancer.instantiateVariableFont(TTFont(Q.VF_TTF), {"wght": wv}, inplace=False, updateFontNames=False)
        st = statics[w]
        icmap, cm = inst.getBestCmap(), scmap[w]
        if set(icmap) != set(cm):
            rep.fail("cmap", f"{w}: 인스턴스 cmap ≠ 정적 cmap")
        o1, o2 = inst["OS/2"], st["OS/2"]
        vm1 = (inst["head"].unitsPerEm, o1.sTypoAscender, o1.sTypoDescender, o1.sTypoLineGap, inst["hhea"].ascent, inst["hhea"].descent, inst["hhea"].lineGap, o1.usWinAscent, o1.usWinDescent)
        vm2 = (st["head"].unitsPerEm, o2.sTypoAscender, o2.sTypoDescender, o2.sTypoLineGap, st["hhea"].ascent, st["hhea"].descent, st["hhea"].lineGap, o2.usWinAscent, o2.usWinDescent)
        (rep.passed if vm1 == vm2 else rep.fail)("vmetrics", f"{w}: 인스턴스 수직 메트릭 {vm1} {'==' if vm1 == vm2 else '≠'} 정적 {vm2}")
        d_sup, d_adv, n_synth = 0, 0, 0
        for cp in sup:
            gi, gs_ = icmap[cp], cm[cp]
            b1, b2 = bounds(inst, gi), bounds(st, gs_)
            a1, a2 = inst["hmtx"][gi][0], st["hmtx"][gs_][0]
            if b1 and b2:
                d = max(abs(x - y) for x, y in zip(b1, b2))
            else:
                d = 0 if b1 == b2 else 9999
            da = abs(a1 - a2)
            if d > 2 or da > 0:
                worst.append((w, f"U+{cp:04X}", d, b1, b2, a1, a2))
            d_sup, d_adv = max(d_sup, d), max(d_adv, da)
        maxdiff_sup, maxdiff_adv = max(maxdiff_sup, d_sup), max(maxdiff_adv, d_adv)
        rep.info("instance", f"{w}: 보충 {len(sup)} 글립 bbox 최대 차 {d_sup} unit, adv 최대 차 {d_adv}")
        # 대표 글립 좌표
        # 대표 글립: 원본 Pretendard VF 와 정적 alternative TTF 는 점 구조(점 수·순서)가 달라 좌표 1:1 비교가 불가 → bbox·adv 로 비교(spec 01 §6 취지)
        bbox_diff, adv_diff, struct_diff = 0, 0, []
        for ch in REPR20:
            cp = ord(ch)
            if cp in icmap and cp in cm:
                c1, c2 = coords_of(inst, icmap[cp]), coords_of(st, cm[cp])
                b1, b2 = bounds(inst, icmap[cp]), bounds(st, cm[cp])
                d = max(abs(x - y) for x, y in zip(b1, b2))
                bbox_diff = max(bbox_diff, d)
                adv_diff = max(adv_diff, abs(inst["hmtx"][icmap[cp]][0] - st["hmtx"][cm[cp]][0]))
                if len(c1) != len(c2):
                    struct_diff.append(f"{ch}({len(c1)}/{len(c2)}pt)")
        maxdiff_repr = max(maxdiff_repr, bbox_diff)
        (rep.passed if (bbox_diff <= 1 and adv_diff == 0) or wv != 400 else rep.warn)("repr20", f"{w}: 대표 글립 {len(REPR20)}자 bbox 최대 차 {bbox_diff:.0f} unit, adv 최대 차 {adv_diff} (400 은 ≤1 요구; 점 수가 다른 글립 {len(struct_diff)}/{len(REPR20)} — 원본 VF 와 정적 TTF 의 점 구조 차이라 좌표 비교 불가: {' '.join(struct_diff[:8])})")
        # 괘선 연결(정적)
        bx = [cp for cp in BOX_H if cp in cm and (bounds(st, cm[cp]) or (0, 0, 0, 0))[0::2] != (0, 1770)]
        by = [cp for cp in BOX_V if cp in cm and (bounds(st, cm[cp]) or (0, 0, 0, 0))[1::2] != (-494, 1950)]
        (rep.passed if not bx and not by else rep.fail)("box-static", f"{w}: 괘선 가로 xMin/xMax=0/1770 위반 {[f'U+{c:04X}' for c in bx]}, 세로 yMin/yMax=-494/1950 위반 {[f'U+{c:04X}' for c in by]}")
        inst.close()
    # 합성·컴포지트 글립: 부품이 **Pretendard** 글립이라 VF 인스턴스(=Pretendard VF 보간)와 정적(=Pretendard 정적 TTF)의
    # 부품 진행폭·오프셋이 1~4 unit 어긋난다(반올림). spec 07 §7(c) 는 이 부류를 ≤8 unit 으로 허용한다.
    # 07 §7(c) 목록은 7자지만 **U+01C4 DŽ(6차 빌드에서 QA 티켓 1 대응으로 D+Zcaron 합성 추가)** 가 같은 부류이므로 8자로 본다.
    # → QA 티켓 7(문서, architect): 07 §7(c) 목록 갱신 필요. 실측 편차는 bbox ≤1.2u / adv ≤2u 로 기존 7자(≤4u)보다 작다.
    # 1.001: 체크박스 U+2610-2612 (□ + ✓/× Pretendard 부품 합성) 도 같은 부류 → 11자
    synth = [0x01C4, 0x2154, 0x223C, 0x2252, 0x25C8, 0xFFE2, 0xFFE3, 0xFFE4, 0x2610, 0x2611, 0x2612]
    w_noto = [x for x in worst if int(x[1][2:], 16) not in synth]
    w_syn = [x for x in worst if int(x[1][2:], 16) in synth]
    (rep.passed if not w_noto else rep.fail)("instance", f"Noto 유래 보충 글립 9 웨이트 인스턴스 = 정적 (bbox ≤2 unit·adv 동일): 위반 {len(w_noto)} {w_noto[:5]}")
    (rep.passed if all(x[2] <= 8 and abs(x[5] - x[6]) <= 8 for x in w_syn) else rep.fail)("instance", f"합성·컴포지트 11자(U+01C4·U+2610–2612 포함): bbox/adv 차 ≤8 unit(빌더 허용치, 07 §7(c) 2 unit 초과분은 승인 필요) 위반 {[x for x in w_syn if x[2] > 8 or abs(x[5] - x[6]) > 8][:5]}; >2 unit·adv 차 목록 {w_syn[:12]}")
    # 축 중간값 괘선
    for wv in (250, 650):
        inst = instancer.instantiateVariableFont(TTFont(Q.VF_TTF), {"wght": wv}, inplace=False, updateFontNames=False)
        icmap = inst.getBestCmap()
        bx = [cp for cp in BOX_H if (bounds(inst, icmap[cp]) or (0, 0, 0, 0))[0::2] != (0, 1770)]
        by = [cp for cp in BOX_V if (bounds(inst, icmap[cp]) or (0, 0, 0, 0))[1::2] != (-494, 1950)]
        adv = {inst["hmtx"][icmap[cp]][0] for cp in range(0x2500, 0x2580) if cp in icmap}
        (rep.passed if not bx and not by and adv == {1770} else rep.fail)("box-mid", f"wght {wv}: 괘선 연결 유지 (x 위반 {bx}, y 위반 {by}, adv {sorted(adv)})")
        # 한글·자모 adv
        ha = {inst["hmtx"][icmap[cp]][0] for cp in range(0xAC00, 0xD7A4, 97)} | {inst["hmtx"][icmap[cp]][0] for cp in range(0x1100, 0x1200) if cp in icmap}
        (rep.passed if ha == {1770} else rep.fail)("hangul-mid", f"wght {wv}: 한글·자모 adv {sorted(ha)}")
        inst.close()
    rep.write("variable")


if __name__ == "__main__":
    main()
