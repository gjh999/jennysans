# -*- coding: utf-8 -*-
"""
정적 9 웨이트 빌드: Pretendard-<W>.ttf(glyf) → Noto 보충 글립 이식(07-supplement 규칙표) + 합성 4자 → 서브셋(빌드 대상)
→ name 전면 교체 → OS/2·head·hhea·post·STAT·gasp·meta 정리 → dist/static/JennySans-<W>.ttf

실행: PYTHONUTF8=1 python tools/build_static.py [--weights Regular,Bold] [--no-supplement]
결과: build/static-summary.json (BUILD-REPORT 가 읽음), build/supplement-refs-<W>.json (07 §3 참조값)
"""
import argparse
import sys
import time
from pathlib import Path

from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charset  # noqa: E402
import config  # noqa: E402
import fontutil  # noqa: E402
import naming  # noqa: E402
import supplement  # noqa: E402

LOG = fontutil.LOG


def transplant_static(font, weight_value, rules, doable, noto_needed):
    """Noto 인스턴스 + 규칙표로 보충 글립을 font 에 추가. 반환 (infos, skipped)."""
    noto = TTFont(supplement.noto_instance(noto_needed, weight_value))
    eng = supplement.Engine(font, noto, rules, weight_value)
    existing = set(font.getGlyphOrder())
    infos, skipped = [], []
    # 합성/미러는 부품·원본이 먼저 있어야 하므로 Noto 유래 → 미러 → 컴포지트 순
    order = [c for c in doable if c not in rules.composites and c not in rules.mirror] + \
            [c for c in doable if c in rules.mirror] + [c for c in doable if c in rules.composites]
    for cp in order:
        try:
            r = eng.make(cp)
        except Exception as e:
            LOG.error("U+%04X 이식 실패: %s", cp, e)
            skipped.append((cp, str(e)))
            continue
        if r is None:
            skipped.append((cp, "규칙 없음 또는 Noto 미보유"))
            continue
        glyph, adv, lsb, info = r
        name = supplement.glyph_name_for(cp, existing)
        existing.add(name)
        fontutil.add_glyph(font, name, glyph, adv, lsb, [cp])
        info["glyph"] = name
        infos.append(info)
    refs = eng.refs_report()
    noto.close()
    return infos, skipped, refs


def build_weight(weight_name, weight_value, sets, build_target, rules, doable, noto_needed, summary, no_supplement=False):
    t0 = time.time()
    src = config.PRETENDARD_TTF_DIR / f"Pretendard-{weight_name}.ttf"
    LOG.info("==== %s (%d) ← %s", weight_name, weight_value, src.name)
    font = TTFont(src)
    if "DSIG" in font:
        del font["DSIG"]

    # 1) 보충 글립 이식(서브셋 전 — 컴포지트 부품·참조 글립을 원본 상태에서 읽기 위해)
    infos, skipped, refs = ([], [], {}) if no_supplement else transplant_static(font, weight_value, rules, doable, noto_needed)
    fontutil.write_json(str(config.SUPPLEMENT_REFS_JSON).format(W=weight_name), dict(weight=weight_name, value=weight_value, refs=refs))
    LOG.info("보충 글립 %d개 이식(합성/미러 %d, 건너뜀 %d)", len(infos),
             sum(1 for i in infos if i["mode"] in ("composite", "mirror")), len(skipped))
    if skipped:
        LOG.warning("건너뜀: %s", [(f"U+{c:04X}", why) for c, why in skipped[:20]])

    # 2) 서브셋
    before_feats = fontutil.gsub_feature_tags(font)
    fontutil.subset_font(font, build_target)
    dropped = sorted(before_feats - fontutil.gsub_feature_tags(font))
    if dropped:
        LOG.warning("서브셋으로 사라진 피처: %s", dropped)

    # 2b) 중첩 컴포넌트 평탄화(QA 티켓 2) — 외곽선 불변, bbox 동일 검증
    flat, mism = supplement.flatten_nested(font)
    LOG.info("중첩 컴포지트 평탄화 %d글립, bbox 불일치 %d", len(flat), len(mism))
    if mism:
        LOG.error("평탄화 bbox 불일치: %s", mism[:5])

    # 2c) 고아 글립 제거(QA 티켓 11) — 평탄화로 컴포넌트 참조가 사라져 어디서도 안 쓰이게 된 글립
    pruned = fontutil.prune_unreachable(font)

    # 3) 이름
    preserved = naming.collect_feature_param_names(font)
    remap, _ = naming.apply_names(font, naming.static_names(weight_name, weight_value), preserved)
    LOG.info("name: FeatureParams 보존 %d개 재매핑", len(remap))

    # 4) 테이블 정리 + STAT
    cp_detail = fontutil.fix_tables(font, weight_name, weight_value, variable=False)
    fontutil.build_stat(font, weight_name, weight_value)
    font["STAT"].table.Version = 0x00010002

    # 5) 저장
    config.DIST_STATIC.mkdir(parents=True, exist_ok=True)
    out = config.DIST_STATIC / f"JennySans-{weight_name}.ttf"
    fontutil.save_font(font, out)
    font.close()

    # 6) 확인(다시 열어 실측)
    chk = TTFont(out, lazy=True)
    cmap = chk.getBestCmap()
    req_missing = sorted(sets[config.GATE_SET] - set(cmap))
    rec = dict(weight=weight_name, value=weight_value, source=src.name, out=str(out), bytes=out.stat().st_size,
               sha256=fontutil.sha256_of(out), numGlyphs=chk["maxp"].numGlyphs, cmap=len(cmap), supplement=len(infos),
               synthesized=[f"U+{i['cp']:04X}" for i in infos if i["mode"] in ("composite", "mirror")],
               skipped=[(f"U+{c:04X}", why) for c, why in skipped],
               required_missing=len(req_missing), required_missing_list=charset.format_ranges(req_missing[:200]),
               dropped_features=dropped, codepages={k: v[:3] for k, v in cp_detail.items()},
               flattened=len(flat), flatten_bbox_mismatch=[m[0] for m in mism],
               pruned=pruned, vertical_tables=[t for t in fontutil.VERTICAL_TABLES if t in chk],
               name1=chk["name"].getDebugName(1), name6=chk["name"].getDebugName(6), seconds=round(time.time() - t0, 1))
    chk.close()
    summary["weights"].append(rec)
    summary["supplement_glyphs"][weight_name] = infos
    LOG.info("→ %s glyphs=%d cmap=%d bytes=%d required 누락=%d (%.1fs)", out.name, rec["numGlyphs"], rec["cmap"], rec["bytes"],
             len(req_missing), rec["seconds"])
    if req_missing:
        LOG.error("required 누락 %d: %s", len(req_missing), rec["required_missing_list"])
    return rec


def plan(sets):
    """보충 계획: (rules, doable, neither, noto_needed, base_cps)"""
    rules = supplement.Rules()
    reg = TTFont(config.PRETENDARD_TTF_DIR / "Pretendard-Regular.ttf", lazy=True)
    base_cps = set(reg.getBestCmap())
    reg.close()
    for w in config.WEIGHT_NAMES:
        f = TTFont(config.PRETENDARD_TTF_DIR / f"Pretendard-{w}.ttf", lazy=True)
        if set(f.getBestCmap()) != base_cps:
            LOG.warning("Pretendard-%s cmap 이 Regular 와 다름(%d vs %d)", w, len(f.getBestCmap()), len(base_cps))
        f.close()
    doable, neither, noto_needed = supplement.supplement_targets(base_cps, sets, rules)
    return rules, doable, neither, noto_needed, base_cps


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--weights", help="쉼표 구분(기본 9종 전부)")
    ap.add_argument("--no-supplement", action="store_true", help="보충 글립 이식 생략(디버그)")
    a = ap.parse_args(argv)
    fontutil.setup_logging("static")
    sets = charset.load_sets()
    build_target = charset.build_target(sets)
    LOG.info("charset: %s → 빌드 대상 %d", {k: len(v) for k, v in sets.items()}, len(build_target))
    rules, doable, neither, noto_needed, base_cps = plan(sets)
    req_neither = sorted(set(neither) & sets[config.GATE_SET])
    LOG.info("Pretendard 미보유 %d → 이식/합성 가능 %d (Noto 인스턴스 %d cps), 어디에도 없음 %d: %s",
             len(doable) + len(neither), len(doable), len(noto_needed), len(neither), charset.format_ranges(neither))
    if req_neither:
        LOG.error("required 인데 채울 수 없음 %d: %s (팀장 결정 필요)", len(req_neither), charset.format_ranges(req_neither))
    unruled = [c for c in doable if c not in rules.composites and c not in rules.mirror and rules.rule_for(c) is None]
    if unruled:
        LOG.warning("규칙표에 없는 코드포인트 %d: %s", len(unruled), charset.format_ranges(unruled))

    summary = dict(charset={k: len(v) for k, v in sets.items()}, build_target=len(build_target),
                   pretendard_missing=len(doable) + len(neither), supplement_candidates=len(doable),
                   neither=charset.format_ranges(neither), required_neither=charset.format_ranges(req_neither),
                   unruled=charset.format_ranges(unruled),
                   rules=[dict(name=r["name"], mode=r["mode"], ref=r.get("ref"), adv=r.get("adv"), sb=r.get("sb"),
                               scale=(r.get("sx"), r.get("sy")), ranges=r["ranges"]) for r in rules.rules],
                   composites={f"U+{k:04X}": v for k, v in rules.composites.items()},
                   mirror={f"U+{k:04X}": v for k, v in rules.mirror.items()},
                   weights=[], supplement_glyphs={})
    weights = config.WEIGHTS
    if a.weights:
        want = [w.strip() for w in a.weights.split(",")]
        weights = [(w, v) for w, v in config.WEIGHTS if w in want]
    for wn, wv in weights:
        build_weight(wn, wv, sets, build_target, rules, doable, noto_needed, summary, a.no_supplement)
    fontutil.write_json(config.BUILD / "static-summary.json", summary)
    bad = [r for r in summary["weights"] if r["required_missing"]]
    LOG.info("정적 빌드 완료: %d 파일, required 누락 있는 파일 %d", len(summary["weights"]), len(bad))
    return 0


if __name__ == "__main__":
    sys.exit(main())
