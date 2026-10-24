# -*- coding: utf-8 -*-
"""
변수 폰트 빌드: PretendardVariable.ttf → 서브셋(빌드 대상) → wght 축 45–930 → 100–400–900 제한(instancer L4, 07 §7-2)
→ 보충 글립 이식(07 §7: 9 인스턴스 피크 gvar — 정적과 같은 규칙으로 웨이트마다 만든 외곽선을 마스터로, 400 기본 + 8 텐트;
  합성/컴포지트 글립은 Pretendard VF 부품 인스턴스에서 생성, 컴포지트는 컴포넌트 오프셋 델타) → 실패 시 2마스터 → rename-only
→ name/fvar/STAT 전면 교체 → OS/2 등 정리 → dist/variable/JennySansVariable.ttf

실행: PYTHONUTF8=1 python tools/build_variable.py [--stage 9|2|0]
결과: build/variable-summary.json
"""
import argparse
import sys
import time
from pathlib import Path

from fontTools.misc.roundTools import otRound
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib import instancer
from fontTools.varLib.models import normalizeValue

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charset  # noqa: E402
import config  # noqa: E402
import fontutil  # noqa: E402
import naming  # noqa: E402
import supplement  # noqa: E402
from build_static import plan  # noqa: E402

LOG = fontutil.LOG
AXIS_MIN, AXIS_DEF, AXIS_MAX = 100, 400, 900


def _coords(glyph, adv):
    if glyph.isComposite():
        pts = [(c.x, c.y) for c in glyph.components]
    elif glyph.numberOfContours > 0:
        pts = [tuple(p) for p in glyph.coordinates]
    else:
        pts = []
    return pts + [(0, 0), (adv, 0), (0, 0), (0, 0)]


def _compatible(g0, g1):
    if g0.isComposite() != g1.isComposite():
        return False
    if g0.isComposite():
        return [c.glyphName for c in g0.components] == [c.glyphName for c in g1.components]
    if g0.numberOfContours != g1.numberOfContours:
        return False
    if g0.numberOfContours <= 0:
        return True
    return list(g0.endPtsOfContours) == list(g1.endPtsOfContours) and len(g0.coordinates) == len(g1.coordinates)


def tents(weights):
    """웨이트별 (start, peak, end) 정규화 좌표 — 9 인스턴스 피크(이웃 피크로 감싼 텐트, 07 §7-3)."""
    n = {w: normalizeValue(w, (AXIS_MIN, AXIS_DEF, AXIS_MAX)) for w in weights}
    ws = sorted(weights)
    out = {}
    for i, w in enumerate(ws):
        if w == AXIS_DEF:
            continue
        peak = n[w]
        if w < AXIS_DEF:
            start = n[ws[i - 1]] if i > 0 else -1.0
            end = 0.0 if ws[i + 1] == AXIS_DEF else n[ws[i + 1]]
        else:
            start = 0.0 if ws[i - 1] == AXIS_DEF else n[ws[i - 1]]
            end = n[ws[i + 1]] if i + 1 < len(ws) else 1.0
        out[w] = (start, peak, end)
    return out


def transplant_variable(font, rules, doable, noto_needed, stage):
    """반환 (델타 성공 글립명, 실패 cp, infos)."""
    if stage == 0 or not doable:
        return [], [], []
    weights = [v for _, v in config.WEIGHTS] if stage == 9 else [100, 400, 900]
    parts_cps = sorted(set(rules.ref_cps()) | set(rules.part_cps()))
    wname = {v: n for n, v in config.WEIGHTS}
    engines = {}
    for w in weights:
        P = TTFont(supplement.pretendard_parts_instance(parts_cps, w, rules.part_names()))   # 부품: VF 인스턴스(점 구조 일관)
        P_ref = TTFont(config.PRETENDARD_TTF_DIR / f"Pretendard-{wname[w]}.ttf", lazy=True)   # 참조값: 정적과 동일 원천
        N = TTFont(supplement.noto_instance(noto_needed, w))
        engines[w] = supplement.Engine(P, N, rules, w, P_ref=P_ref)
    tent = tents(weights)
    gvar = font["gvar"]
    existing = set(font.getGlyphOrder())
    order = [c for c in doable if c not in rules.composites and c not in rules.mirror] + \
            [c for c in doable if c in rules.mirror] + [c for c in doable if c in rules.composites]
    added, failed, infos = [], [], []
    for cp in order:
        made = {}
        try:
            for w in weights:
                r = engines[w].make(cp)
                if r is None:
                    break
                made[w] = r
        except Exception as e:
            LOG.error("U+%04X 변수 이식 실패: %s", cp, e)
            failed.append(cp)
            continue
        if len(made) != len(weights):
            continue
        g0, adv0, lsb0, info = made[AXIS_DEF]
        # 컴포지트가 참조하는 글립이 VF 에 있어야 한다
        if g0.isComposite() and any(c.glyphName not in existing for c in g0.components):
            LOG.error("U+%04X 컴포넌트 %s 가 VF 에 없음", cp, [c.glyphName for c in g0.components])
            failed.append(cp)
            continue
        name = supplement.glyph_name_for(cp, existing)
        existing.add(name)
        fontutil.add_glyph(font, name, g0, adv0, lsb0, [cp])
        info["glyph"] = name
        base = _coords(g0, adv0)
        variations = []
        ok = True
        for w in weights:
            if w == AXIS_DEF:
                continue
            gw, advw, _, _ = made[w]
            if not _compatible(g0, gw):
                ok = False
                break
            cw = _coords(gw, advw)
            deltas = [(otRound(x1 - x0), otRound(y1 - y0)) for (x0, y0), (x1, y1) in zip(base, cw)]
            variations.append(TupleVariation({"wght": tent[w]}, deltas))
        if ok:
            if (not g0.isComposite()) and g0.numberOfContours > 0:
                ends = list(g0.endPtsOfContours)
                for var in variations:
                    var.optimize(base, ends)     # IUP 최적화(허용 오차 0.5) — 인스턴스 좌표 ±1 unit
            # 델타가 전부 0 인 텐트(괘선 등)는 생략
            variations = [v for v in variations if any(d is not None and d != (0, 0) for d in v.coordinates)]
            gvar.variations[name] = variations
            added.append(name)
            info["tuples"] = len(variations)
        else:
            gvar.variations[name] = []
            failed.append(cp)
            info["variation"] = "FAILED(점 구조 불일치) — 400 형태 고정"
        infos.append(info)
    for e in engines.values():
        e.P.font.close()
        e.P_ref.font.close()
        e.N.font.close()
    return added, failed, infos


def _mini_instances(font, names, weights):
    """font 를 names(+컴포넌트 클로저)로 서브셋한 mini VF 를 9 웨이트로 인스턴스 → {w: TTFont}"""
    import io
    buf = io.BytesIO()
    font.save(buf)
    mini = TTFont(io.BytesIO(buf.getvalue()))
    fontutil.subset_font(mini, [], glyph_names=names, layout=False)
    mb = io.BytesIO()
    mini.save(mb)
    out = {}
    for w in weights:
        mf = TTFont(io.BytesIO(mb.getvalue()))
        out[w] = instancer.instantiateVariableFont(mf, {"wght": w}, inplace=True, optimize=False)
    return out


def flatten_variable(font, weights, noto_names=()):
    """QA 티켓 2(VF): 중첩 컴포지트를 평탄화하고 gvar 를 '외부 오프셋 델타 + 내부 글립 델타'(= 9 인스턴스에서 전개한 오프셋)로 재생성.

    채택 기준 = **spec 07 §7(c)** (8차 빌드에서 정정, 팀장 결정 AGENTS §8 2026-09-09):
      · Noto 유래 보충 글립(`noto_names`) → 9 인스턴스 bbox 가 정적과 ≤`config.FLATTEN_TOL_NOTO`(2) unit
      · 그 밖(= Pretendard 유래 컴포지트의 평탄화) → ≤`config.FLATTEN_TOL_COMPOSITE`(8) unit
    정적↔VF 원본 차이로 이미 허용치를 넘는 글립은 평탄화 전후 차 ≤1 이면 채택(평탄화가 원인이 아님).
    6차까지는 전부 2 unit 으로 판정해 편차 2.0~2.4 unit 인 12 글립을 되돌렸고 VF 에 중첩 5개가 남았다.
    반환 dict(flattened, kept_nested, detail, worst, adopted, reverted)"""
    noto_names = set(noto_names)
    names = supplement.nested_composites(font)
    if not names:
        return dict(flattened=[], kept_nested=[], detail="중첩 없음", worst=0, adopted=[], reverted=[])
    glyf = font["glyf"]
    gvar = font["gvar"]
    tent = tents(weights)
    before = _mini_instances(font, names, weights)
    # 정적 bbox·진행폭 (07 §7(c) 비교 기준)
    static_bbox, static_adv = {}, {}
    for wn, wv in config.WEIGHTS:
        p = config.DIST_STATIC / f"JennySans-{wn}.ttf"
        if p.exists():
            sf = TTFont(p, lazy=True)
            sg = sf["glyf"]
            static_bbox[wv] = {n: supplement.bounds_of(sg, n) for n in names if n in sg.glyphs}
            static_adv[wv] = {n: sf["hmtx"].metrics[n][0] for n in names if n in sg.glyphs}
            sf.close()
    snapshot = {n: (glyf[n].components, gvar.variations.get(n)) for n in names}
    flattened, kept = [], []
    for n in names:
        base_leaves = supplement.expand_components(glyf, n)
        leaf_names = [l[0] for l in base_leaves]
        per_w = {}
        ok = True
        for w in weights:
            lw = supplement.expand_components(before[w]["glyf"], n)
            if [l[0] for l in lw] != leaf_names:
                ok = False
                break
            per_w[w] = ([(otRound(t.dx), otRound(t.dy)) for _, t, _ in lw], before[w]["hmtx"].metrics[n][0])
        if not ok:
            kept.append((n, "인스턴스 컴포넌트 구조 불일치"))
            continue
        base = [(otRound(t.dx), otRound(t.dy)) for _, t, _ in base_leaves] + [(0, 0), (font["hmtx"].metrics[n][0], 0), (0, 0), (0, 0)]
        variations = []
        for w in weights:
            if w == AXIS_DEF:
                continue
            offs, adv = per_w[w]
            cw = offs + [(0, 0), (adv, 0), (0, 0), (0, 0)]
            deltas = [(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in zip(base, cw)]
            if any(d != (0, 0) for d in deltas):
                variations.append(TupleVariation({"wght": tent[w]}, deltas))
        supplement.flatten_nested(font, [n])
        gvar.variations[n] = variations
        flattened.append(n)
    # 자체 검증: 평탄화 후 인스턴스 bbox vs 정적 / vs 평탄화 전
    after = _mini_instances(font, flattened, weights) if flattened else {}
    adopted, reverted = [], []
    for n in flattened:
        worst_static, worst_before, worst_prev_static, worst_adv = 0, 0, 0, 0
        for w in weights:
            ba = supplement.bounds_of(after[w]["glyf"], n)
            bb = supplement.bounds_of(before[w]["glyf"], n)
            bs = static_bbox.get(w, {}).get(n)
            if ba and bb:
                worst_before = max(worst_before, max(abs(a - b) for a, b in zip(ba, bb)))
            if ba and bs:
                worst_static = max(worst_static, max(abs(a - b) for a, b in zip(ba, bs)))
            if bb and bs:
                worst_prev_static = max(worst_prev_static, max(abs(a - b) for a, b in zip(bb, bs)))
            sa = static_adv.get(w, {}).get(n)
            if sa is not None:
                worst_adv = max(worst_adv, abs(after[w]["hmtx"].metrics[n][0] - sa))
        tol = config.FLATTEN_TOL_NOTO if n in noto_names else config.FLATTEN_TOL_COMPOSITE
        row = (n, round(worst_static, 3), round(worst_before, 3), round(worst_adv, 3), tol)
        if worst_static <= tol or (worst_prev_static > tol and worst_before <= 1):
            adopted.append(row)
        else:
            comps, var = snapshot[n]
            glyf[n].components = comps
            gvar.variations[n] = var
            reverted.append(row)
    for insts in (before, after):
        for f in insts.values():
            f.close()
    worst = max([a[1] for a in adopted], default=0)
    worst_advmax = max([a[3] for a in adopted], default=0)
    top = sorted(adopted, key=lambda r: -r[1])[:8]
    detail = (f"중첩 {len(names)} → 평탄화 채택 {len(adopted)}(9 인스턴스 bbox 가 정적과 최대 {worst} unit·adv 최대 {worst_advmax} unit, "
              f"허용치 07 §7(c) Noto {config.FLATTEN_TOL_NOTO}/컴포지트 {config.FLATTEN_TOL_COMPOSITE}; 평탄화 전후 최대 "
              f"{max([a[2] for a in adopted], default=0)}), 되돌림 {len(reverted)} {[r[:2] for r in reverted[:8]]}, "
              f"구조 불일치 {kept[:5]}, 편차 상위 {[(r[0], r[1]) for r in top]}")
    return dict(flattened=[a[0] for a in adopted], kept_nested=[r[0] for r in reverted] + [k[0] for k in kept],
                detail=detail, worst=worst, worst_adv=worst_advmax,
                adopted=[list(r) for r in adopted], reverted=[list(r) for r in reverted])


def transformed_composites(font):
    glyf = font["glyf"]
    return [n for n in font.getGlyphOrder()
            if glyf[n].isComposite() and any(hasattr(c, "transform") for c in glyf[n].components)]


def decompose_composite(glyf, name):
    """컴포지트를 외곽선으로 전개 → (pts[(x,y)], endPts, flags). 반전(det<0) 컴포넌트는 윤곽 점 순서를 뒤집어 방향 복원."""
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
    allp, allends, allflags = [], [], []
    for c in glyf[name].components:
        coords, ends, flags = glyf[c.glyphName].getCoordinates(glyf)
        coords = GlyphCoordinates(coords)
        det = 1.0
        if hasattr(c, "transform"):
            t = c.transform
            coords.transform(((t[0][0], t[0][1]), (t[1][0], t[1][1])))
            det = t[0][0] * t[1][1] - t[0][1] * t[1][0]
        coords.translate((c.x, c.y))
        coords.toInt()
        pts = [tuple(p) for p in coords]
        fl = [f & 1 for f in flags]
        if det < 0:
            npts, nfl, start = [], [], 0
            for e in ends:
                npts += pts[start:e + 1][::-1]
                nfl += fl[start:e + 1][::-1]
                start = e + 1
            pts, fl = npts, nfl
        base = len(allp)
        allp += pts
        allflags += fl
        allends += [e + base for e in ends]
    return allp, allends, allflags


def make_simple_glyph(pts, ends, flags, overlap=False):
    import array
    from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
    g = Glyph()
    g.numberOfContours = len(ends)
    g.coordinates = GlyphCoordinates(pts)
    g.endPtsOfContours = list(ends)
    fl = [f & 1 for f in flags]
    if overlap and fl:
        fl[0] |= 0x40
    g.flags = array.array("B", fl)
    from fontTools.ttLib.tables import ttProgram
    g.program = ttProgram.Program()   # 무힌트(빈 프로그램) — compile 이 program 속성을 요구
    return g


def decompose_transformed(font, weights):
    """QA 티켓 6(VF): 반전·스케일 컴포넌트를 쓰는 글립을 외곽선으로 분해하고 gvar 를 '참조 글립 델타에 같은 변환 적용 + 오프셋 델타'
    (= 9 인스턴스에서 분해한 좌표)로 재생성. 채택 기준: 9 인스턴스 bbox 가 정적과 ≤2 unit(정적↔VF 원본 차 >2 인 글립은 전후 ≤1)."""
    names = transformed_composites(font)
    if not names:
        return dict(decomposed=[], kept=[], detail="변환 컴포넌트 없음")
    glyf = font["glyf"]
    gvar = font["gvar"]
    hmtx = font["hmtx"].metrics
    tent = tents(weights)
    before = _mini_instances(font, names, weights)
    static_bbox = {}
    for wn, wv in config.WEIGHTS:
        p = config.DIST_STATIC / f"JennySans-{wn}.ttf"
        if p.exists():
            sf = TTFont(p, lazy=True)
            sg = sf["glyf"]
            static_bbox[wv] = {n: supplement.bounds_of(sg, n) for n in names if n in sg.glyphs}
            sf.close()
    snapshot = {n: (glyf.glyphs[n], gvar.variations.get(n), hmtx[n]) for n in names}
    done, kept = [], []
    for n in names:
        pts0, ends0, fl0 = decompose_composite(glyf, n)
        per_w = {}
        ok = True
        for w in weights:
            pw, ew, fw = decompose_composite(before[w]["glyf"], n)
            if len(pw) != len(pts0) or ew != ends0:
                ok = False
                break
            per_w[w] = (pw, before[w]["hmtx"].metrics[n][0])
        if not ok:
            kept.append((n, "인스턴스 점 구조 불일치"))
            continue
        adv0 = hmtx[n][0]
        ncomp = len(glyf[n].components)
        g = make_simple_glyph(pts0, ends0, fl0, overlap=ncomp > 1)
        g.recalcBounds(glyf)
        glyf.glyphs[n] = g
        hmtx[n] = (adv0, g.xMin if g.numberOfContours > 0 else 0)
        base = list(pts0) + [(0, 0), (adv0, 0), (0, 0), (0, 0)]
        variations = []
        for w in weights:
            if w == AXIS_DEF:
                continue
            pw, advw = per_w[w]
            cw = list(pw) + [(0, 0), (advw, 0), (0, 0), (0, 0)]
            deltas = [(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in zip(base, cw)]
            if any(d != (0, 0) for d in deltas):
                variations.append(TupleVariation({"wght": tent[w]}, deltas))
        if g.numberOfContours > 0:
            for var in variations:
                var.optimize(base, list(ends0))
        gvar.variations[n] = variations
        done.append(n)
    after = _mini_instances(font, done, weights) if done else {}
    adopted, reverted = [], []
    for n in done:
        worst_static = worst_before = worst_prev = 0
        for w in weights:
            ba = supplement.bounds_of(after[w]["glyf"], n)
            bb = supplement.bounds_of(before[w]["glyf"], n)
            bs = static_bbox.get(w, {}).get(n)
            if ba and bb:
                worst_before = max(worst_before, max(abs(a - b) for a, b in zip(ba, bb)))
            if ba and bs:
                worst_static = max(worst_static, max(abs(a - b) for a, b in zip(ba, bs)))
            if bb and bs:
                worst_prev = max(worst_prev, max(abs(a - b) for a, b in zip(bb, bs)))
        if worst_static <= 2 or (worst_prev > 2 and worst_before <= 1):
            adopted.append((n, round(worst_static, 2), round(worst_before, 2)))
        else:
            gl, var, met = snapshot[n]
            glyf.glyphs[n] = gl
            gvar.variations[n] = var
            hmtx[n] = met
            reverted.append((n, round(worst_static, 2), round(worst_before, 2)))
    for insts in (before, after):
        for f in insts.values():
            f.close()
    detail = (f"변환 컴포넌트 글립 {len(names)} → 분해 채택 {len(adopted)}(정적 대비 최대 {max([a[1] for a in adopted], default=0)} unit, "
              f"전후 최대 {max([a[2] for a in adopted], default=0)}), 되돌림 {len(reverted)} {reverted[:6]}, 구조 불일치 {kept[:5]}")
    return dict(decomposed=[a[0] for a in adopted], kept=[r[0] for r in reverted] + [k[0] for k in kept], detail=detail)


def rebuild_fvar(font):
    fvar = font["fvar"]
    assert len(fvar.axes) == 1 and fvar.axes[0].axisTag == "wght"
    ax = fvar.axes[0]
    ax.minValue, ax.defaultValue, ax.maxValue = AXIS_MIN, AXIS_DEF, AXIS_MAX
    ax.axisNameID = naming.add_name(font, "Weight", ko="굵기")
    ax.flags = 0
    insts = []
    for wn, wv in config.WEIGHTS:
        ni = NamedInstance()
        ni.coordinates = {"wght": float(wv)}
        ni.flags = 0
        ni.subfamilyNameID = naming.add_name(font, wn)
        ni.postscriptNameID = naming.add_name(font, f"{naming.VF_PS_PREFIX}-{wn}")
        insts.append(ni)
    fvar.instances = insts


def _prepare(src, build_target):
    font = TTFont(src)
    before = fontutil.gsub_feature_tags(font)
    fontutil.subset_font(font, build_target)
    dropped = sorted(before - fontutil.gsub_feature_tags(font))
    font = instancer.instantiateVariableFont(font, {"wght": (AXIS_MIN, AXIS_DEF, AXIS_MAX)}, inplace=True,
                                             optimize=True, updateFontNames=False)
    ax = font["fvar"].axes[0]
    assert (ax.minValue, ax.defaultValue, ax.maxValue) == (AXIS_MIN, AXIS_DEF, AXIS_MAX), ax
    return font, dropped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", type=int, default=9, choices=[9, 2, 0], help="보충 글립 gvar 방식(기본 9)")
    a = ap.parse_args(argv)
    fontutil.setup_logging("variable")
    t0 = time.time()
    sets = charset.load_sets()
    build_target = charset.build_target(sets)
    rules, doable, neither, noto_needed, _ = plan(sets)
    LOG.info("보충 대상 %d (합성/미러 %d)", len(doable), sum(1 for c in doable if c in rules.composites or c in rules.mirror))

    src = config.PRETENDARD_VF
    LOG.info("==== Variable ← %s (서브셋 → 축 45–930 → %d/%d/%d 제한)", src.name, AXIS_MIN, AXIS_DEF, AXIS_MAX)
    font, dropped = _prepare(src, build_target)
    LOG.info("서브셋 후 사라진 피처 %s", dropped)

    stage_used = a.stage
    added, failed, infos = [], [], []
    for st in [s for s in (9, 2, 0) if s <= a.stage]:
        try:
            added, failed, infos = transplant_variable(font, rules, doable, noto_needed, st)
            stage_used = st
            break
        except Exception as e:
            LOG.exception("stage %d 실패 → 폴백: %s", st, e)
            font, dropped = _prepare(src, build_target)
    LOG.info("보충 글립 %d 추가 (stage %d, gvar 성공 %d, 실패 %d)", len(infos), stage_used, len(added), len(failed))
    weights9 = [v for _, v in config.WEIGHTS]
    # 07 §7(c) 허용치는 글립 성격에 따라 다르다 — Noto 유래 보충 글립(합성·미러 제외)만 2 unit, 나머지 컴포지트는 8 unit
    noto_names = {i["glyph"] for i in infos if i.get("glyph") and i["mode"] not in ("composite", "mirror")}
    flat = flatten_variable(font, weights9, noto_names)
    LOG.info("VF 중첩 컴포지트 평탄화: %s", flat["detail"])
    deco = decompose_transformed(font, weights9)
    LOG.info("VF 변환 컴포넌트 분해: %s", deco["detail"])
    still = supplement.nested_composites(font)
    if still:
        LOG.error("VF 중첩 컴포지트 잔존 %d: %s", len(still), still[:10])
    pruned = fontutil.prune_unreachable(font)          # QA 티켓 11: 평탄화·분해로 생긴 고아 글립 제거

    preserved = naming.collect_feature_param_names(font)
    naming.apply_names(font, naming.variable_names(), preserved)
    rebuild_fvar(font)
    fontutil.fix_tables(font, "Regular", 400, variable=True)
    fontutil.build_stat(font)
    font["STAT"].table.Version = 0x00010002
    if "MVAR" in font:
        LOG.warning("MVAR 존재 — 수직 메트릭 변동 방지를 위해 제거(spec 03 §8)")
        del font["MVAR"]

    config.DIST_VARIABLE.mkdir(parents=True, exist_ok=True)
    out = config.DIST_VARIABLE / "JennySansVariable.ttf"
    fontutil.save_font(font, out)
    font.close()

    chk = TTFont(out, lazy=True)
    cmap = chk.getBestCmap()
    req_missing = sorted(sets[config.GATE_SET] - set(cmap))
    inst = [(chk["name"].getDebugName(i.subfamilyNameID), i.coordinates["wght"], chk["name"].getDebugName(i.postscriptNameID))
            for i in chk["fvar"].instances]
    ax = chk["fvar"].axes[0]
    rec = dict(source=src.name, out=str(out), bytes=out.stat().st_size, sha256=fontutil.sha256_of(out),
               numGlyphs=chk["maxp"].numGlyphs, cmap=len(cmap), gvar_glyphs=len(chk["gvar"].variations),
               supplement=len(infos), supplement_with_deltas=len(added), supplement_failed=charset.format_ranges(failed),
               synthesized=[f"U+{i['cp']:04X}" for i in infos if i["mode"] in ("composite", "mirror")],
               stage=stage_used, stage_label={9: "9 인스턴스 피크 gvar(중간 마스터)", 2: "2 마스터(100/900)", 0: "rename-only(보충 없음)"}[stage_used],
               required_missing=len(req_missing), required_missing_list=charset.format_ranges(req_missing[:100]),
               dropped_features=dropped, axis=[ax.axisTag, ax.minValue, ax.defaultValue, ax.maxValue],
               flattened=len(flat["flattened"]), kept_nested=flat["kept_nested"], flatten_detail=flat["detail"],
               flatten_worst=flat["worst"], flatten_worst_adv=flat.get("worst_adv"),
               flatten_adopted=flat["adopted"], flatten_reverted=flat["reverted"], nested_left=still,
               decomposed=len(deco["decomposed"]), kept_transformed=deco["kept"], decompose_detail=deco["detail"],
               pruned=pruned, vertical_tables=[t for t in fontutil.VERTICAL_TABLES if t in chk],
               instances=inst, name1=chk["name"].getDebugName(1), name6=chk["name"].getDebugName(6),
               name25=chk["name"].getDebugName(25), seconds=round(time.time() - t0, 1), supplement_glyphs=infos)
    chk.close()
    fontutil.write_json(config.BUILD / "variable-summary.json", rec)
    LOG.info("→ %s glyphs=%d cmap=%d gvar=%d bytes=%d stage=%d required 누락=%d (%.0fs)", out.name, rec["numGlyphs"],
             rec["cmap"], rec["gvar_glyphs"], rec["bytes"], stage_used, len(req_missing), rec["seconds"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
