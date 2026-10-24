# -*- coding: utf-8 -*-
"""참조 글립 실측(docs/spec/07-supplement.md 근거): Pretendard 정적 TTF vs Noto KR VF 인스턴스의 참조쌍 bbox/advance, Noto 단독 글립, 사이드베어링, 괘선 획 두께, 3차 후보.
실행: PYTHONUTF8=1 python charset/scripts/supplement_refs.py [400|700]"""
import sys, os, statistics, json
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.varLib import instancer
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
W = int(sys.argv[1]) if len(sys.argv) > 1 else 400

def gm(font, cp):
    cmap = font.getBestCmap(); gs = font.getGlyphSet(); hm = font["hmtx"]
    g = cmap.get(cp)
    if g is None: return None
    pen = BoundsPen(gs); gs[g].draw(pen)
    b = pen.bounds
    adv = hm[g][0]
    if b is None: return {"adv": adv, "bbox": None}
    x0, y0, x1, y1 = b
    return {"adv": adv, "bbox": [round(v, 1) for v in b], "w": round(x1 - x0, 1), "h": round(y1 - y0, 1),
            "cx": round((x0 + x1) / 2, 1), "cy": round((y0 + y1) / 2, 1), "lsb": round(x0, 1), "rsb": round(adv - x1, 1)}

P = TTFont(os.path.join(ROOT, {400: "sources/Pretendard/alternative-ttf/Pretendard-Regular.ttf", 700: "sources/Pretendard/alternative-ttf/Pretendard-Bold.ttf"}[W]))
N = instancer.instantiateVariableFont(TTFont(os.path.join(ROOT, "sources/NotoSansKR/NotoSansKR[wght].ttf")), {"wght": W}, inplace=False, optimize=False)

REF = [0x2460, 0x2469, 0x321C, 0x25A0, 0x25A1, 0x25CB, 0x25CF, 0x25C7, 0x25B3, 0x2605, 0x2606, 0x203B, 0x2260, 0x2212, 0x221E, 0x2264, 0x2211, 0x222B, 0x221A, 0x00B1, 0x2192, 0x2194, 0x21D2, 0x3014, 0x3010, 0x300C, 0x3001, 0x3002, 0x00AC, 0xFF3E, 0xFF5E, 0xFF21, 0xFF10, 0x338F, 0x33A1, 0x339C, 0x2103, 0x2116, 0x2122, 0x2153, 0x00BD, 0x2160, 0x3131, 0x314F, 0xAC00, 0x2013, 0x2014, 0x2026, 0x00B7, 0x2022]
NOTO_ONLY = [0x2500, 0x2501, 0x2502, 0x2503, 0x250C, 0x253C, 0x254B, 0x2588, 0x2592, 0x2580, 0x1100, 0x1112, 0x115F, 0x1160, 0x1161, 0x1175, 0x11A8, 0x11C2, 0x1113, 0x1176, 0x11C3, 0xA960, 0xD7B0, 0xD7CB, 0x302E, 0x302F, 0x3165, 0x318E, 0x24D0, 0x249C, 0x2474, 0x3200, 0x3260, 0x327E, 0x327F, 0x25A3, 0x25D0, 0x260E, 0x261E, 0x2664, 0x2668, 0x2669, 0x3013, 0x2200, 0x2208, 0x2234, 0x2261, 0x2282, 0x2227, 0x222C, 0x226A, 0x2312, 0xFFE2, 0xFFE3, 0x223D, 0x2253]

print(f"=== wght {W}: Pretendard vs Noto@{W} (reference glyphs, both present) ===")
print("cp\tchar\tP.adv\tP.bbox\tP.w\tP.h\tP.cy\tN.adv\tN.bbox\tN.w\tN.h\tN.cy\trw\trh\tradv")
for cp in REF:
    p, n = gm(P, cp), gm(N, cp)
    if not p or not n or p.get("bbox") is None or n.get("bbox") is None:
        print(f"U+{cp:04X}\t{chr(cp)}\tP={p}\tN={n}"); continue
    print(f"U+{cp:04X}\t{chr(cp)}\t{p['adv']}\t{p['bbox']}\t{p['w']}\t{p['h']}\t{p['cy']}\t{n['adv']}\t{n['bbox']}\t{n['w']}\t{n['h']}\t{n['cy']}\t{p['w']/n['w']:.3f}\t{p['h']/n['h']:.3f}\t{p['adv']/n['adv']:.3f}")

print(f"\n=== Noto-only glyphs @{W} (adv, bbox, w, h, cy) ===")
for cp in NOTO_ONLY:
    n = gm(N, cp)
    print(f"U+{cp:04X}\t{chr(cp)}\t{n}")

# Pretendard 사이드베어링 중앙값: 수학 연산자(보유), 단위, 도형
def sb_stats(font, cps, label):
    l, r, advs, hs, cys = [], [], [], [], []
    for cp in cps:
        m = gm(font, cp)
        if m and m.get("bbox"):
            l.append(m["lsb"]); r.append(m["rsb"]); advs.append(m["adv"]); hs.append(m["h"]); cys.append(m["cy"])
    if l:
        print(f"{label}: n={len(l)} lsb median {statistics.median(l)} rsb median {statistics.median(r)} adv median {statistics.median(advs)} h median {statistics.median(hs)} cy median {statistics.median(cys)}")
print(f"\n=== Pretendard sidebearing/axis stats @{W} ===")
sb_stats(P, [0x00B1, 0x00D7, 0x00F7, 0x2260, 0x2264, 0x2265, 0x221E, 0x221A, 0x2211, 0x220F, 0x222B, 0x2248, 0x2212, 0x2202, 0x2206, 0x2229, 0x222A], "P math ops")
sb_stats(P, list(range(0x3380, 0x33E0)), "P units 3380-33DF")
sb_stats(P, [0x25A0, 0x25A1, 0x25CB, 0x25CF, 0x25CE, 0x25C6, 0x25C7, 0x25B2, 0x25B3, 0x25BC, 0x25BD, 0x25B6, 0x25B7, 0x25C0, 0x25C1], "P geometric")
sb_stats(P, [0x2605, 0x2606, 0x2660, 0x2661, 0x2665, 0x2663, 0x266A, 0x2640, 0x2642], "P misc symbols present")
sb_stats(P, [0x2190, 0x2191, 0x2192, 0x2193, 0x2194, 0x2195, 0x2196, 0x2197, 0x2198, 0x2199, 0x21D2, 0x21D4], "P arrows")
sb_stats(P, list(range(0x2460, 0x2474)), "P circled 1-20")
sb_stats(P, list(range(0xFF01, 0xFF5F)), "P fullwidth")
sb_stats(N, list(range(0x2200, 0x2300)), "N math 2200-22FF")
sb_stats(N, list(range(0x3380, 0x33E0)), "N units")

# 괘선 획 두께 (Noto)
print(f"\n=== Noto box stroke @{W} ===")
for cp, lab in [(0x2500, "─ light h"), (0x2501, "━ heavy h"), (0x2502, "│ light v"), (0x2503, "┃ heavy v"), (0x2550, "═ double h"), (0x2551, "║ double v")]:
    n = gm(N, cp); print(lab, n)

# 3rd source candidates
print("\n=== 3rd-source candidates for U+2154 U+223C U+2252 U+25C8 ===")
for path in ["sources/GothicA1/GothicA1-Regular.ttf", "sources/GothicA1/GothicA1-Bold.ttf", "sources/Inter/Inter-Regular.ttf", "sources/Inter/Inter-Bold.ttf", "sources/SourceHanSansKR/SourceHanSansKR-Regular.otf"]:
    f = TTFont(os.path.join(ROOT, path))
    print(path, "UPM", f["head"].unitsPerEm, "typo", f["OS/2"].sTypoAscender, f["OS/2"].sTypoDescender, "wght", f["OS/2"].usWeightClass)
    for cp in [0x2154, 0x223C, 0x2252, 0x25C8, 0x2153, 0x223D, 0x2248, 0x25C7, 0x25C6, 0xAC00]:
        print(f"   U+{cp:04X} {chr(cp)} {gm(f, cp)}")
