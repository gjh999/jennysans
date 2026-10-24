"""SEO 에셋 생성 — og-image(1200×630)·favicon(PNG 512/192/32)·apple-touch-icon(180) 을 JennySans 로 렌더한다.
실행: PYTHONUTF8=1 python tools/seo_assets.py   (dist/static 이 있어야 함)
산출: site/assets/og-image.png, site/assets/icon-512.png, icon-192.png, apple-touch-icon.png, favicon-32.png, favicon.ico
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "dist" / "static"
OUT = ROOT / "site" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

BG = (250, 250, 248)
FG = (22, 22, 22)
MUTED = (110, 110, 110)


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(STATIC / f"JennySans-{weight}.ttf"), size)


def og_image() -> Path:
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((80, 70), "JENNYSOFT · SIL OPEN FONT LICENSE 1.1 · 무료", font=font("Medium", 22), fill=MUTED)
    d.text((76, 110), "제니산스", font=font("Black", 150), fill=FG)
    d.text((80, 285), "JennySans", font=font("Light", 96), fill=(90, 90, 90))
    d.text((80, 410), "다람쥐 헌 쳇바퀴에 타고파 · ¿Qué tal, señor? · The quick brown fox", font=font("Regular", 34), fill=FG)
    d.text((80, 470), "한글 11,172자 전부 · 스페인어 등 라틴 · 그리스·키릴 · KS 기호 · 9 웨이트 + 변수 폰트",
           font=font("Regular", 28), fill=MUTED)
    d.text((80, 545), "font.jennysoft.co.kr", font=font("SemiBold", 30), fill=FG)
    p = OUT / "og-image.png"
    im.save(p, optimize=True)
    return p


def icon(size: int, name: str, radius_ratio: float = 0.22) -> Path:
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(size * radius_ratio)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=r, fill=(22, 22, 22, 255))
    f = font("Bold", int(size * 0.56))
    txt = "제"
    bbox = d.textbbox((0, 0), txt, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]), txt, font=f, fill=(255, 255, 255, 255))
    p = OUT / name
    im.save(p, optimize=True)
    return p


def main() -> None:
    made = [og_image(), icon(512, "icon-512.png"), icon(192, "icon-192.png"), icon(180, "apple-touch-icon.png"),
            icon(32, "favicon-32.png", 0.18)]
    ico = OUT / "favicon.ico"
    Image.open(OUT / "icon-192.png").save(ico, sizes=[(16, 16), (32, 32), (48, 48)])
    made.append(ico)
    for p in made:
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size:,} B")


if __name__ == "__main__":
    main()
