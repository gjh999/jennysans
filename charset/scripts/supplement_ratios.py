#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
보충 글립(Noto Sans KR VF → Pretendard 좌표계 UPM 2048) 이식 비율 실측 — docs/spec/07-supplement.md 근거.

두 폰트가 공통 보유한 글립의 bbox(BoundsPen)·advance 를 카테고리별로 비교해
  가로 비율 = P_width / N_width,  세로 비율 = P_height / N_height,  진행폭 비율 = P_adv / N_adv,
  베이스라인 기준 수직 위치: P_ymin 대 N_ymin×s, P_ymax 대 N_ymax×s (s = 세로 비율 중앙값)
의 중앙값·사분위·표준편차를 낸다. 괘선(공통 없음)은 Noto 단독 bbox 를 em 대비로 출력한다.

실행: PYTHONUTF8=1 python charset/scripts/supplement_ratios.py [--wght 400] [--md] [--json 경로]
  --wght : Noto VF 인스턴스 굵기(기본 400 → Pretendard-Regular.ttf 와 비교; 700 → Pretendard-Bold.ttf)
  --pv   : Pretendard 쪽도 PretendardVariable.ttf 를 같은 굵기로 인스턴스해 비교(100·900 등 정적 TTF 가 없는 굵기)
"""
import argparse
import json
import os
import statistics
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P_STATIC = {400: "sources/Pretendard/alternative-ttf/Pretendard-Regular.ttf",
            700: "sources/Pretendard/alternative-ttf/Pretendard-Bold.ttf"}
P_VAR = "sources/Pretendard/PretendardVariable.ttf"
N_VAR = "sources/NotoSansKR/NotoSansKR[wght].ttf"

# 카테고리: (이름, 코드포인트 목록 생성)
def rng(a, b):
    return list(range(a, b + 1))

CATEGORIES = [
    ("hangul_syllable", "한글 음절(샘플 120: 가~힣 등간격)", [0xAC00 + i * 93 for i in range(120)] + [0xAC00, 0xD55C, 0xAE00, 0xD7A3]),
    ("compat_jamo", "호환 자모 U+3131–3163", rng(0x3131, 0x3163)),
    ("enclosed_num", "원숫자 ①–⑳ U+2460–2473", rng(0x2460, 0x2473)),
    ("enclosed_latin", "원·괄호 라틴 ⓐ–ⓩ ⒜–⒵ U+24D0–24E9, 249C–24B5", rng(0x24D0, 0x24E9) + rng(0x249C, 0x24B5)),
    ("enclosed_cjk", "원·괄호 한글 U+3200–327F (+㈜)", rng(0x3200, 0x321C) + rng(0x3260, 0x327F)),
    ("units", "단위 U+3380–33DF", rng(0x3380, 0x33DF)),
    ("box", "괘선 U+2500–257F", rng(0x2500, 0x257F)),
    ("block", "블록 U+2580–259F", rng(0x2580, 0x259F)),
    ("geometric", "도형 U+25A0–25FF", rng(0x25A0, 0x25FF)),
    ("arrows", "화살표 U+2190–21FF", rng(0x2190, 0x21FF)),
    ("math", "수학 U+2200–22FF", rng(0x2200, 0x22FF)),
    ("misc_symbols", "기타 기호 U+2600–26FF", rng(0x2600, 0x26FF)),
    ("cjk_punct", "CJK 구두점 U+3000–303F", rng(0x3000, 0x303F)),
    ("fullwidth", "전각 U+FF01–FF5E", rng(0xFF01, 0xFF5E)),
    ("letterlike_numforms", "문자형·숫자형·상하첨자 U+2100–218F, 2070–209F", rng(0x2100, 0x218F) + rng(0x2070, 0x209F)),
    ("latin_ref", "라틴 참조 H x 0 (스케일 비교용)", [0x48, 0x78, 0x30, 0x4F, 0x6F]),
]


def load(path):
    return TTFont(os.path.join(ROOT, path))


def instance(vf, wght):
    return instancer.instantiateVariableFont(vf, {"wght": wght}, inplace=False, optimize=False)


def glyph_metrics(font, gs, cmap, hmtx, cp):
    g = cmap.get(cp)
    if g is None:
        return None
    pen = BoundsPen(gs)
    gs[g].draw(pen)
    if pen.bounds is None:
        return None
    x0, y0, x1, y1 = pen.bounds
    return {"glyph": g, "adv": hmtx[g][0], "bbox": (x0, y0, x1, y1), "w": x1 - x0, "h": y1 - y0}


def q(vals, p):
    if not vals:
        return None
    vals = sorted(vals)
    k = (len(vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    return vals[f] + (vals[c] - vals[f]) * (k - f)


def stats(vals):
    if not vals:
        return {"n": 0}
    return {"n": len(vals), "median": round(statistics.median(vals), 4), "q1": round(q(vals, 0.25), 4),
            "q3": round(q(vals, 0.75), 4), "min": round(min(vals), 4), "max": round(max(vals), 4),
            "stdev": round(statistics.pstdev(vals), 4) if len(vals) > 1 else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wght", type=int, default=400)
    ap.add_argument("--pv", action="store_true", help="Pretendard 쪽을 변수 폰트 인스턴스로")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--json")
    args = ap.parse_args()

    if args.pv or args.wght not in P_STATIC:
        P = instance(load(P_VAR), args.wght)
        p_label = f"PretendardVariable@{args.wght}"
    else:
        P = load(P_STATIC[args.wght])
        p_label = os.path.basename(P_STATIC[args.wght])
    N = instance(load(N_VAR), args.wght)
    n_label = f"NotoSansKR[wght]@{args.wght}"
    upm_p, upm_n = P["head"].unitsPerEm, N["head"].unitsPerEm

    Pgs, Ngs = P.getGlyphSet(), N.getGlyphSet()
    Pc, Nc = P.getBestCmap(), N.getBestCmap()
    Ph, Nh = P["hmtx"], N["hmtx"]

    report = {"pretendard": p_label, "noto": n_label, "upm": [upm_p, upm_n], "wght": args.wght, "categories": {}}
    for key, label, cps in CATEGORIES:
        rw, rh, ra, ymin_p, ymax_p, ymin_n, ymax_n, xoff = [], [], [], [], [], [], [], []
        n_only = []
        common = 0
        for cp in cps:
            pm = glyph_metrics(P, Pgs, Pc, Ph, cp)
            nm = glyph_metrics(N, Ngs, Nc, Nh, cp)
            if nm is None:
                continue
            if pm is None:
                n_only.append({"cp": f"U+{cp:04X}", "adv": nm["adv"], "bbox": nm["bbox"]})
                continue
            common += 1
            if nm["w"] > 0 and pm["w"] > 0:
                rw.append(pm["w"] / nm["w"])
            if nm["h"] > 0 and pm["h"] > 0:
                rh.append(pm["h"] / nm["h"])
            if nm["adv"] > 0:
                ra.append(pm["adv"] / nm["adv"])
            ymin_p.append(pm["bbox"][1]); ymax_p.append(pm["bbox"][3])
            ymin_n.append(nm["bbox"][1]); ymax_n.append(nm["bbox"][3])
            # 진행폭 안에서의 중심 위치(0~1)
            xoff.append(((pm["bbox"][0] + pm["bbox"][2]) / 2 / pm["adv"]) - ((nm["bbox"][0] + nm["bbox"][2]) / 2 / nm["adv"]))
        cat = {"label": label, "common": common, "noto_only": len(n_only),
               "ratio_w": stats(rw), "ratio_h": stats(rh), "ratio_adv": stats(ra),
               "center_shift": stats(xoff)}
        if rh:
            s = statistics.median(rh)
            # 세로 위치: P_ymin − N_ymin×s (양수면 P 가 더 위)
            dy_min = [a - b * s for a, b in zip(ymin_p, ymin_n)]
            dy_max = [a - b * s for a, b in zip(ymax_p, ymax_n)]
            cat["dy_min_at_median_scale"] = stats(dy_min)
            cat["dy_max_at_median_scale"] = stats(dy_max)
        if n_only:
            advs = [x["adv"] for x in n_only]
            ymins = [x["bbox"][1] for x in n_only]; ymaxs = [x["bbox"][3] for x in n_only]
            xmins = [x["bbox"][0] for x in n_only]; xmaxs = [x["bbox"][2] for x in n_only]
            cat["noto_only_metrics"] = {"adv": stats(advs), "ymin": stats(ymins), "ymax": stats(ymaxs),
                                        "xmin": stats(xmins), "xmax": stats(xmaxs),
                                        "samples": n_only[:6]}
        report["categories"][key] = cat

    # 참조: 두 폰트의 수직 메트릭
    report["metrics"] = {
        "P": {"typo": [P["OS/2"].sTypoAscender, P["OS/2"].sTypoDescender], "hhea": [P["hhea"].ascent, P["hhea"].descent], "win": [P["OS/2"].usWinAscent, P["OS/2"].usWinDescent]},
        "N": {"typo": [N["OS/2"].sTypoAscender, N["OS/2"].sTypoDescender], "hhea": [N["hhea"].ascent, N["hhea"].descent], "win": [N["OS/2"].usWinAscent, N["OS/2"].usWinDescent]},
    }

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)

    if args.md:
        print(f"| 카테고리 | 공통 | Noto만 | 가로비 중앙값(Q1–Q3) | 세로비 중앙값(Q1–Q3) | 진행폭비 중앙값 | Δymin/Δymax(중앙값, P units) | 중심이동 |")
        print("|---|---|---|---|---|---|---|---|")
        for key, cat in report["categories"].items():
            rw, rh, ra = cat["ratio_w"], cat["ratio_h"], cat["ratio_adv"]
            f = lambda s: f"{s['median']} ({s['q1']}–{s['q3']})" if s.get("n") else "—"
            dy = cat.get("dy_min_at_median_scale")
            dyx = cat.get("dy_max_at_median_scale")
            dys = f"{dy['median']}/{dyx['median']}" if dy else "—"
            cs = cat["center_shift"]
            print(f"| {cat['label']} | {cat['common']} | {cat['noto_only']} | {f(rw)} | {f(rh)} | {ra.get('median','—')} | {dys} | {cs.get('median','—')} |")
        for key, cat in report["categories"].items():
            if "noto_only_metrics" in cat:
                m = cat["noto_only_metrics"]
                print(f"\nNoto-only [{cat['label']}]: n={cat['noto_only']} adv median {m['adv']['median']} (min {m['adv']['min']} max {m['adv']['max']}); "
                      f"ymin median {m['ymin']['median']} (min {m['ymin']['min']}); ymax median {m['ymax']['median']} (max {m['ymax']['max']}); "
                      f"xmin median {m['xmin']['median']} xmax median {m['xmax']['median']}")
        print("\nmetrics:", json.dumps(report["metrics"]))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
