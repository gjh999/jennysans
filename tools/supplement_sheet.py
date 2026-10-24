# -*- coding: utf-8 -*-
"""
보충 글립 전수 시트(07 §6 outputs.sheet_png, §8-8): build/supplement-sheet-<W>.png
각 셀 = [참조 글립(회색)] [이식 글립(검정)] + 코드포인트. Pillow BASIC 레이아웃(셰이핑 없음, cmap 직접).
실행: PYTHONUTF8=1 python tools/supplement_sheet.py [--weights Regular,Bold]
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
import fontutil  # noqa: E402

COLS = 10
CELL_W, CELL_H = 200, 92
SIZE = 44


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default=",".join(config.WEIGHT_NAMES))
    a = ap.parse_args(argv)
    ss = fontutil.read_json(config.BUILD / "static-summary.json", {})
    for wn in a.weights.split(","):
        infos = ss.get("supplement_glyphs", {}).get(wn)
        p = config.DIST_STATIC / f"JennySans-{wn}.ttf"
        if not infos or not p.exists():
            print("건너뜀:", wn)
            continue
        font = ImageFont.truetype(str(p), SIZE, layout_engine=ImageFont.Layout.BASIC)
        small = ImageFont.truetype(str(p), 14, layout_engine=ImageFont.Layout.BASIC)
        rows = (len(infos) + COLS - 1) // COLS
        img = Image.new("RGB", (COLS * CELL_W + 40, rows * CELL_H + 80), "white")
        d = ImageDraw.Draw(img)
        d.text((20, 16), f"JennySans-{wn} supplement sheet — {len(infos)} glyphs: [ref grey] [supplement black] U+XXXX rule", font=small, fill=(80, 80, 80))
        for i, info in enumerate(infos):
            cp = info["cp"]
            x = 20 + (i % COLS) * CELL_W
            y = 60 + (i // COLS) * CELL_H
            ref = info.get("ref") or (info.get("mirror_of")) or ("U+2153" if cp == 0x2154 else None)
            if info["mode"] == "composite" and cp in (0xFFE2, 0xFFE3, 0xFFE4):
                ref = {0xFFE2: "U+00AC", 0xFFE3: "U+00AF", 0xFFE4: "U+00A6"}[cp]
            if info["mode"] == "composite" and cp == 0x2252:
                ref = "U+2260"
            if info["mode"] == "composite" and cp == 0x25C8:
                ref = "U+25C7"
            if info["mode"] == "fixed":
                ref = "U+3131" if cp < 0x3000 or cp > 0x3200 else "U+3134"
            if ref:
                d.text((x, y), chr(int(ref[2:], 16)), font=font, fill=(170, 170, 170))
            d.text((x + 70, y), chr(cp), font=font, fill="black")
            d.text((x, y + 62), f"U+{cp:04X} {info.get('rule', info['mode'])[:14]} {info.get('adv', '')}", font=small, fill=(120, 120, 120))
        out = Path(str(config.SUPPLEMENT_SHEET_PNG).format(W=wn))
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
        print("→", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
