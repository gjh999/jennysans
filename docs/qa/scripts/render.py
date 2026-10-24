# -*- coding: utf-8 -*-
"""
게이트 7 — PIL(FreeType) 렌더 이미지 (font-qa).
- 웨이트별 샘플 시트 docs/qa/shots/render-<W>.png: 한글 문장·스페인어(¿Qué tal, señor? ¡Año nuevo!)·영문 팬그램·숫자·기호·보충 글립(자모·원문자·괄호·수학·도형·괘선)·참조쌍 나란히.
- 9 웨이트 한 장 docs/qa/shots/render-all-weights.png (줄높이 비교 포함: 같은 문장 100/400/900 세 줄의 줄 간격 픽셀 동일 검사, spec 03 §2).
- 괘선 연결 검사 07 §4-5(d): `┌─┬─┐ / │한│글│ / └─┴─┘` 를 24·48 px, line-height 1.0(네이티브 2444/2048) 로 찍어
  가로선 픽셀 행이 셀 경계에서 끊기지 않고(빈 열 0), 세로선 픽셀 열이 줄 경계에서 끊기지 않음(빈 행 0) → docs/qa/shots/box-<W>.png
- 변수 폰트: FreeType variation 으로 wght 100/250/400/650/900 렌더 docs/qa/shots/render-variable.png
실행: PYTHONUTF8=1 python docs/qa/scripts/render.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
from PIL import Image, ImageDraw, ImageFont, features  # noqa: E402

LINES = [
    ("한글", "다람쥐 헌 쳇바퀴에 타고파. 키스의 고유조건은 입술끼리 만나야 하고 특별한 기술은 필요치 않다. 똠방각하 뷁 힣"),
    ("es", "¿Qué tal, señor? ¡Año nuevo! Ñandú, pingüino, 1ª 2º, 12,50 € — «Güell» áéíóú ÁÉÍÓÚ üÜ"),
    ("en", "The quick brown fox jumps over the lazy dog. Sphinx of black quartz, judge my vow."),
    ("eu", "Zażółć gęślą jaźń · Příliš žluťoučký kůň · Ğüneş İı Şş · Straße ÄÖÜ · Șș Țț · Αλφάβητο · Съешь ещё"),
    ("숫자", "0123456789 1,234,567.89 ½ ¼ ¾ ⅓ ⅔ ¹²³ ₩1,000 €12,50 $9.99 ￦ ０１２３ +82-10-1234-5678"),
    ("기호", "※ ①②③ ㉠㉡㉢ ㈜ ㈎ ⒜ ㎏ ㎡ ℃ ← → ↔ ★ ☆ ○ ● ◎ ◐ ■ □ ▣ ◇ ◈ ◌ 「」『』〈〉《》 · … ― ~ ∼ ≒ ∠ ∴ ∀ ∃ ∬ ± × ÷ ≠ ≤ ≥ ∞ ⊂ ♠ ♥ ☎ ♩"),
    ("자모", "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ ㅥㅱㅸㆁㆆㆍ ᄀᄂᄃᄒ ᅡᅢᅣ ᆨᆩᆪ 한글 NFD: 한글"),
    ("참조쌍", "㉠① ㈀㈜ ▣■ ◐○ ◎○ ⊂≠ ∬∫ ♠♥ ☎★ 〓■ ⅔⅓ ∼∽ ≒= ◈◇◆ ∀H ￢¬ ￣¯"),
    ("괘선", "┌─┬─┐ ├─┼─┤ └─┴─┘ ┏━┳━┓ ┃ ┗━┻━┛ ╔═╦═╗ ║ ╚═╩═╝ ▒ █ ▓ ░"),
]
BOX = ["┌─┬─┐", "│한│글│", "└─┴─┘"]
BOX2 = ["┏━┳━┓", "┃제┃니┃", "┗━┻━┛"]


def font_at(path, px, variation=None):
    f = ImageFont.truetype(str(path), px)
    if variation is not None:
        f.set_variation_by_axes([variation])
    return f


def render_sheet(path, title, out, px=36, variation=None):
    f = font_at(path, px, variation)
    label = ImageFont.truetype(str(Q.STATIC_DIR / "JennySans-Regular.ttf"), 14)
    lh = int(px * 2444 / 2048) + 8
    W = 2200
    H = 60 + lh * len(LINES) + 20
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.text((20, 16), f"{title} — Pillow {Image.__version__} FreeType {features.version_module('freetype2')}", font=label, fill="#666")
    y = 60
    for lab, txt in LINES:
        d.text((20, y + 8), lab, font=label, fill="#888")
        d.text((140, y), txt, font=f, fill="black", anchor="la")
        y += lh
    im.save(out)
    return out


def measure_line_gap(path, px=40):
    """같은 문장 3줄을 PIL 기본 줄간격(getmetrics 기반)으로 찍어 줄 간격 px 를 반환 — 웨이트별 동일해야 함."""
    f = font_at(path, px)
    asc, desc = f.getmetrics()
    return asc, desc, asc + desc


def box_test(path, px, out, box=BOX, variation=None):
    """07 §4-5(d): 네이티브 줄높이(2444/2048·px)로 3줄을 찍고 가로선 연속·세로선 연속을 픽셀로 검사."""
    f = font_at(path, px, variation)
    lh = round(px * 2444 / 2048)
    asc = round(px * 1950 / 2048)
    W = px * 6 + 40
    H = lh * 3 + 40
    im = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(im)
    x0, y0 = 20, 20
    for i, line in enumerate(box):
        d.text((x0, y0 + i * lh + asc), line, font=f, fill=0, anchor="ls")
    px_ = im.load()
    # 잉크 bbox
    ink = [(x, y) for y in range(H) for x in range(W) if px_[x, y] < 128]
    xs, ys = [p[0] for p in ink], [p[1] for p in ink]
    L, R, T, B = min(xs), max(xs), min(ys), max(ys)
    # 가로선: 첫 줄(┌─┬─┐)의 가로획이 있는 행 = 첫 줄 영역에서 잉크 폭이 가장 넓은 행들
    row_span = {}
    for y in range(y0, y0 + lh):
        row = [x for x in range(W) if px_[x, y] < 128]
        if row:
            row_span[y] = (min(row), max(row), len(row))
    # 가장 넓게 채워진 행(가로선)
    top_rows = [y for y, (a, b, n) in row_span.items() if n >= (R - L) * 0.9]
    gaps_h = []
    for y in top_rows:
        gaps_h += [x for x in range(L, R + 1) if px_[x, y] >= 128]
    # 세로선: 첫 셀 경계 열(┌ 의 세로획) — 좌측 잉크 열 중 잉크가 가장 많은 열
    col_cnt = {x: sum(1 for y in range(T, B + 1) if px_[x, y] < 128) for x in range(L, R + 1)}
    left_cols = [x for x in range(L, L + max(2, px // 6)) if col_cnt[x] >= (B - T) * 0.9]
    gaps_v = []
    for x in left_cols:
        gaps_v += [y for y in range(T, B + 1) if px_[x, y] >= 128]
    # 저장(확대)
    big = im.resize((W * 4, H * 4), Image.NEAREST)
    big.save(out)
    return {"px": px, "line_height_px": lh, "h_rows": len(top_rows), "h_gap_cols": len(set(gaps_h)), "v_cols": len(left_cols), "v_gap_rows": len(set(gaps_v)),
            "ink_bbox": (L, T, R, B)}


def main():
    rep = Q.Report("PIL 렌더 이미지·괘선 연결·줄높이 (게이트 7, 07 §4-5(d), 03 §2)")
    rep.info("env", f"Pillow {Image.__version__}, FreeType {features.version_module('freetype2')}, raqm {features.check('raqm')}")
    Q.SHOTS.mkdir(parents=True, exist_ok=True)
    gaps = {}
    for (w, wv), p in zip(Q.WEIGHTS, Q.STATIC_TTFS):
        out = Q.SHOTS / f"render-{w}.png"
        render_sheet(p, f"JennySans {w} ({wv}) — {p.name}", out)
        rep.info("sheet", f"{w}: {out.relative_to(Q.ROOT)}")
        gaps[w] = measure_line_gap(p)
        for px in (24, 48):
            r = box_test(p, px, Q.SHOTS / f"box-{w}-{px}px.png")
            ok = r["h_rows"] > 0 and r["h_gap_cols"] == 0 and r["v_cols"] > 0 and r["v_gap_rows"] == 0
            (rep.passed if ok else rep.fail)("box", f"{w} {px}px (lh {r['line_height_px']}px): 가로선 행 {r['h_rows']}·빈 열 {r['h_gap_cols']}, 세로선 열 {r['v_cols']}·빈 행 {r['v_gap_rows']} → {Q.SHOTS.name}/box-{w}-{px}px.png")
        r = box_test(p, 48, Q.SHOTS / f"box-{w}-48px-heavy.png", box=BOX2)
        ok = r["h_rows"] > 0 and r["h_gap_cols"] == 0 and r["v_cols"] > 0 and r["v_gap_rows"] == 0
        (rep.passed if ok else rep.fail)("box", f"{w} 48px 굵은 괘선(┏━┳): 빈 열 {r['h_gap_cols']}, 빈 행 {r['v_gap_rows']}")
    vals = set(gaps.values())
    (rep.passed if len(vals) == 1 else rep.fail)("line-height", f"9 웨이트 FreeType getmetrics (ascent, descent, 합) 40px: {gaps['Regular']} — {'전부 동일' if len(vals) == 1 else '상이 ' + str(gaps)}")
    # 9 웨이트 한 장 + 줄높이 비교
    px = 34
    lh = int(px * 2444 / 2048) + 6
    im = Image.new("RGB", (2000, 60 + lh * 9 + 40 + 3 * (lh) + 60), "white")
    d = ImageDraw.Draw(im)
    label = ImageFont.truetype(str(Q.STATIC_DIR / "JennySans-Regular.ttf"), 14)
    d.text((20, 16), f"JennySans {Q.VERSION} — 9 weights (static TTF, Pillow/FreeType)", font=label, fill="#666")
    y = 60
    for (w, wv), p in zip(Q.WEIGHTS, Q.STATIC_TTFS):
        f = font_at(p, px)
        d.text((20, y + 10), f"{wv} {w}", font=label, fill="#888")
        d.text((180, y), "가나다라 한글 제니산스 JennySans ¿Qué tal, señor? 0123 ㉠①∠∴◎ ┌─┐ ᄀ ᅡ ᇂ", font=f, fill="black", anchor="la")
        y += lh
    y += 30
    d.text((20, y), "줄 높이 비교 — 같은 문장 100 / 400 / 900 (줄 간격 = FreeType 기본, 세 블록의 줄 간격 픽셀이 같아야 함)", font=label, fill="#666")
    y += 24
    x = 20
    for w in ("Thin", "Regular", "Black"):
        f = font_at(Q.STATIC_DIR / f"JennySans-{w}.ttf", 28)
        a, de, tot = measure_line_gap(Q.STATIC_DIR / f"JennySans-{w}.ttf", 28)
        for i, t in enumerate(("제니산스 ¿Qué?", "둘째 줄 Second", "셋째 줄 Tercera")):
            d.text((x, y + i * tot), t, font=f, fill="black", anchor="la")
            d.line((x - 6, y + i * tot, x - 6 + 620, y + i * tot), fill="#ddd")
        d.text((x, y + 3 * tot + 4), f"{w}: ascent {a} + descent {de} = {tot}px", font=label, fill="#888")
        x += 640
    out = Q.SHOTS / "render-all-weights.png"
    im.save(out)
    rep.info("sheet", f"9 웨이트 + 줄높이: {out.relative_to(Q.ROOT)}")
    # 변수 폰트
    try:
        f = ImageFont.truetype(str(Q.VF_TTF), 34)
        axes = f.get_variation_axes()
        rep.info("variable", f"FreeType 축 {axes}")
        px = 34
        lh = int(px * 2444 / 2048) + 6
        im = Image.new("RGB", (2000, 60 + lh * 5 + 20), "white")
        d = ImageDraw.Draw(im)
        d.text((20, 16), "JennySansVariable.ttf — wght 100 / 250 / 400 / 650 / 900 (FreeType variation)", font=label, fill="#666")
        y = 60
        for wv in (100, 250, 400, 650, 900):
            fv = font_at(Q.VF_TTF, px, variation=wv)
            d.text((20, y + 10), f"wght {wv}", font=label, fill="#888")
            d.text((180, y), "가나다라 한글 제니산스 JennySans ¿Qué tal, señor? 0123 ㉠①∠∴◎ ┌─┐ ᄀ ᅡ ᇂ ⅔ ≒ ◈ ∼", font=fv, fill="black", anchor="la")
            y += lh
        out = Q.SHOTS / "render-variable.png"
        im.save(out)
        rep.info("variable", f"{out.relative_to(Q.ROOT)}")
        for wv in (250, 650):
            r = box_test(Q.VF_TTF, 48, Q.SHOTS / f"box-variable-{wv}-48px.png", variation=wv)
            ok = r["h_rows"] > 0 and r["h_gap_cols"] == 0 and r["v_cols"] > 0 and r["v_gap_rows"] == 0
            (rep.passed if ok else rep.fail)("box-vf", f"VF wght {wv} 48px: 빈 열 {r['h_gap_cols']}, 빈 행 {r['v_gap_rows']}")
    except Exception as e:
        rep.warn("variable", f"FreeType variation 렌더 실패: {e}")
    rep.write("render")


if __name__ == "__main__":
    main()
