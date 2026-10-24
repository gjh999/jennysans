# -*- coding: utf-8 -*-
"""
보충 스케일 실측(아키텍트 07-supplement.md 작성 근거용). 웨이트를 맞춰(Pretendard-<W>.ttf vs Noto 인스턴스 <W>)
같은 디자인 계열 글립의 bbox 비율·진행폭·오프셋을 잰다. 결과: build/supplement-measure.md

실행: PYTHONUTF8=1 python tools/measure_supplement.py [--weights Regular,Bold]
"""
import argparse
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
import fontutil  # noqa: E402
import supplement  # noqa: E402

# (카테고리, 코드포인트) — Pretendard 가 SHS 계열 글립으로 이미 갖고 있는 "형제" 글립
PAIRS = [
    ("한글 음절", [0xAC00, 0xB098, 0xD55C, 0xAE00, 0xB9AC, 0xD798]),
    ("호환 자모", [0x3131, 0x3134, 0x3137, 0x314F, 0x3151, 0x3163]),
    ("원문자 ①", [0x2460, 0x2461, 0x2469]),
    ("도형 ○●◇", [0x25CB, 0x25CF, 0x25C7, 0x25A1, 0x25B3]),
    ("괄호 〈〉「」", [0x3008, 0x300C, 0x3010]),
    ("전각 ASCII", [0xFF21, 0xFF01, 0xFF10, 0xFF3C]),
    ("단위 ㎏㎐", [0x338F, 0x3390, 0x33A1, 0x339D, 0x3380]),
    ("기타 ※№℃", [0x203B, 0x2116, 0x2103, 0x2605, 0x321C]),
]


def bbox(gs, name):
    p = BoundsPen(gs)
    gs[name].draw(p)
    return p.bounds


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default="Regular,Bold")
    a = ap.parse_args(argv)
    cps = sorted({c for _, cs in PAIRS for c in cs})
    lines = ["# supplement-measure — Pretendard vs Noto Sans KR 인스턴스(웨이트 일치) bbox 실측", "",
             "sx/sy = Pretendard bbox 폭/높이 ÷ Noto bbox 폭/높이 · adv 비 = 진행폭 비 · dx,dy = 균등 sy 적용 시 좌하단 오프셋(2048 UPM)", ""]
    for wn in a.weights.split(","):
        wv = config.WEIGHT_VALUE[wn]
        pt = TTFont(config.PRETENDARD_TTF_DIR / f"Pretendard-{wn}.ttf", lazy=True)
        nt = TTFont(supplement.noto_instance(cps, wv), lazy=True)
        pcm, ncm = pt.getBestCmap(), nt.getBestCmap()
        pgs, ngs = pt.getGlyphSet(), nt.getGlyphSet()
        lines += [f"## {wn} ({wv})", "", "| 카테고리 | cp | 문자 | P adv | P bbox | N adv | N bbox | sx | sy | adv 비 | dx | dy |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for cat, cs in PAIRS:
            for c in cs:
                if c not in pcm or c not in ncm:
                    continue
                pb, nb = bbox(pgs, pcm[c]), bbox(ngs, ncm[c])
                pa, na = pt["hmtx"][pcm[c]][0], nt["hmtx"][ncm[c]][0]
                if not pb or not nb:
                    continue
                sx = (pb[2] - pb[0]) / (nb[2] - nb[0]) if nb[2] != nb[0] else 0
                sy = (pb[3] - pb[1]) / (nb[3] - nb[1]) if nb[3] != nb[1] else 0
                lines.append(f"| {cat} | U+{c:04X} | {chr(c)} | {pa} | {[int(v) for v in pb]} | {na} | {[int(v) for v in nb]} | "
                             f"{sx:.3f} | {sy:.3f} | {pa / na:.3f} | {pb[0] - nb[0] * sy:.0f} | {pb[1] - nb[1] * sy:.0f} |")
        lines.append("")
        pt.close()
        nt.close()
    out = config.BUILD / "supplement-measure.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("→", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
