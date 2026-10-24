# -*- coding: utf-8 -*-
"""
(1.001) 체크박스 견본: 정적 9 웨이트 + 변수 폰트 wght 100/400/900 인스턴스로 ☐☑☒□✓× 를 나란히 렌더.
가는 선(빨강)은 □ 외곽 bbox 의 위·아래 — ☐☑☒ 박스가 □ 와 같은 높이·위치인지 눈으로 확인한다.
→ build/preview/ballot-static.png, build/preview/ballot-variable.png
실행: PYTHONUTF8=1 python tools/ballot_preview.py
"""
import io
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

SAMPLE = "☐☑☒□✓×"
SIZE = 96


def _row_img(rows, title, out):
    lab = ImageFont.truetype(str(config.DIST_STATIC / "JennySans-Regular.ttf"), 24)
    W, H = 1300, 90 + 140 * len(rows)
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((24, 20), title, font=lab, fill=(60, 60, 60))
    for i, (label, font_bytes, upm, box_bbox) in enumerate(rows):
        y = 80 + 140 * i
        ft = ImageFont.truetype(io.BytesIO(font_bytes), SIZE)
        d.text((24, y + 45), label, font=lab, fill=(90, 90, 90))
        x0 = 330
        asc = ft.getmetrics()[0]
        base = y + asc
        for yy in (box_bbox[1], box_bbox[3]):   # □ bbox 위·아래 기준선
            py = base - yy * SIZE / upm
            d.line([(x0 - 10, py), (W - 20, py)], fill=(230, 80, 80), width=1)
        x = x0
        for ch in SAMPLE:
            d.text((x, y), ch, font=ft, fill="black")
            x += 150
    img.save(out)
    print("→", out)


def _box_bbox(f):
    g = f["glyf"][f.getBestCmap()[0x25A1]]
    g.recalcBounds(f["glyf"])
    return (g.xMin, g.yMin, g.xMax, g.yMax)


def main():
    config.PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for w in config.WEIGHT_NAMES:
        p = config.DIST_STATIC / f"JennySans-{w}.ttf"
        f = TTFont(p)
        rows.append((w, p.read_bytes(), f["head"].unitsPerEm, _box_bbox(f)))
    _row_img(rows, f"JennySans {config.VERSION} 정적 9 웨이트 — {SAMPLE} (빨간 선 = □ 위·아래)",
             config.PREVIEW_DIR / "ballot-static.png")
    rows = []
    vf = config.DIST_VARIABLE / "JennySansVariable.ttf"
    for wv in (100, 400, 900):
        inst = instancer.instantiateVariableFont(TTFont(vf), {"wght": wv})
        buf = io.BytesIO()
        inst.save(buf)
        rows.append((f"VF wght={wv}", buf.getvalue(), inst["head"].unitsPerEm, _box_bbox(inst)))
    _row_img(rows, f"JennySans Variable {config.VERSION} — wght 100/400/900 인스턴스 {SAMPLE}",
             config.PREVIEW_DIR / "ballot-variable.png")


if __name__ == "__main__":
    main()
