# -*- coding: utf-8 -*-
"""
Pillow 렌더 미리보기: build/preview/JennySans-Regular.png (+ 웨이트 9종 한 줄씩).
한글·스페인어·영문·숫자·기호·보충 글립(첫가끝 자모·옛 호환자모·원문자·괘선) 샘플. 팀장 육안 확인용.
실행: PYTHONUTF8=1 python tools/preview.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

LINES = [
    ("한글", "다람쥐 헌 쳇바퀴에 타고파 — 제니산스는 제니소프트의 범용 고딕입니다. 똠방각하 뷁 힣"),
    ("es", "¿Qué tal, señor? ¡Año nuevo! Ñandú, pingüino, 1ª 2º, 12,50 € — Łódź Český Ğüneş"),
    ("en", "The quick brown fox jumps over the lazy dog. Sphinx of black quartz, judge my vow."),
    ("숫자·기호", "0123456789 ±×÷ ≤≥≠≈ ₩€$¥ ※ ①②③ ⓐⓑ ⑴⑵ ○●◇◆ ★☆ → ↔ ㎏㎡㎜ ㈜ Ⅰ Ⅱ Ⅲ ㄱㄴㄷ ㅏㅑㅓ"),
    ("보충(Noto)", "ᄀᄁᄂ ᅡᅣᅥ ᇂᇁᇀ ㅥㅦㅱㆍㆎ ㉠㉡㉢㉾㉿ ㈀㈁㈂ ⒜⒝ ∠∴∵∀∃∈ ◎◐◑◌ ┌─┬─┐ ├─┼─┤ └─┴─┘ ▒▣▤ ☎☞♨♩♬ ￢￣ ꥠ ힰ"),
]
WEIGHT_SAMPLE = "가나다라 한글 JennySans 제니산스 ¿Qué? 0123 ㉠∠∴◎ 갛"


def main(argv=None):
    config.PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    reg = config.DIST_STATIC / "JennySans-Regular.ttf"
    if not reg.exists():
        raise SystemExit(f"없음: {reg}")
    size = 40
    W = 2200
    pad = 40
    lh = int(size * 1.6)
    h = pad * 2 + lh * (len(LINES) + 1) + 30 + lh * len(config.WEIGHTS) + 40
    img = Image.new("RGB", (W, h), "white")
    d = ImageDraw.Draw(img)
    label_font = ImageFont.truetype(str(reg), 22)
    y = pad
    d.text((pad, y), f"JennySans {config.VERSION} — Regular (Pillow {Image.__version__}, {reg.name})", font=label_font, fill=(90, 90, 90))
    y += lh
    for label, text in LINES:
        engine = ImageFont.Layout.BASIC if label.startswith("보충") else None
        try:
            font = ImageFont.truetype(str(reg), size, layout_engine=engine) if engine is not None else ImageFont.truetype(str(reg), size)
        except Exception:
            font = ImageFont.truetype(str(reg), size)
        d.text((pad, y + 10), label, font=label_font, fill=(150, 150, 150))
        d.text((pad + 170, y), text, font=font, fill="black")
        y += lh
    y += 30
    d.text((pad, y), "9 weights (static TTF)", font=label_font, fill=(90, 90, 90))
    y += 36
    for wn, wv in config.WEIGHTS:
        p = config.DIST_STATIC / f"JennySans-{wn}.ttf"
        if not p.exists():
            continue
        font = ImageFont.truetype(str(p), size, layout_engine=ImageFont.Layout.BASIC)
        d.text((pad, y + 10), f"{wv} {wn}", font=label_font, fill=(150, 150, 150))
        d.text((pad + 220, y), WEIGHT_SAMPLE, font=font, fill="black")
        y += lh
    img.save(config.PREVIEW_PNG)
    print("→", config.PREVIEW_PNG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
