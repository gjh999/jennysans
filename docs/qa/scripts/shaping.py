# -*- coding: utf-8 -*-
"""
게이트 2 — HarfBuzz 셰이핑 (uharfbuzz).
(a) 한글 11,172 음절 각 1자 (b) 한·영·es·pl·cs·tr·de·ro·el·ru 문단 (c) 결합문자 시퀀스(n+U+0303, u+U+0308, a+U+0301, c+U+0327, e+U+030C 등)
    → 프리컴포즈 결과와 비교(ccmp 합성 여부·mark 배치) (d) NFD 자모 시퀀스 → 음절 합성 (e) kern·tnum/pnum·frac·전각 숫자 adv(spec 04 §3·§4)
대상: 정적 9 TTF + 변수 TTF(기본 400 + wght 100/900 변형) + WOFF2 10.
실행: PYTHONUTF8=1 python docs/qa/scripts/shaping.py
"""
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
import uharfbuzz as hb  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402

SAMPLES = {
    "ko": "다람쥐 헌 쳇바퀴에 타고파. 키스의 고유조건은 입술끼리 만나야 하고 특별한 기술은 필요치 않다. 제니산스는 제니소프트의 범용 고딕입니다. 똠방각하 뷁 힣 ㉠㉡㉢ ㈜ ※ ①②③ ┌─┬─┐│└┴┘",
    "en": "The quick brown fox jumps over the lazy dog. Sphinx of black quartz, judge my vow. JennySans 1.000 (c) 2026 JennySoft.",
    "es": "¿Qué tal, señor? ¡Año nuevo! Ñandú, pingüino, 1ª 2º, 12,50 €. El veloz murciélago hindú comía feliz cardillo y kiwi. «Güell» ¡Ojalá! ü Ü á é í ó ú Á É Í Ó Ú",
    "pl": "Zażółć gęślą jaźń. Pchnąć w tę łódź jeża lub ośm skrzyń fig.",
    "cs": "Příliš žluťoučký kůň úpěl ďábelské ódy. Ľ ľ ď ť Ř ř Ů ů",
    "tr": "Pijamalı hasta yağız şoföre çabucak güvendi. İ ı Ş ş Ğ ğ",
    "de": "Falsches Üben von Xylophonmusik quält jeden größeren Zwerg. „Straße“ ÄÖÜ äöü ß",
    "ro": "Șase sași în șase saci. Țară, ață, Ș ș Ț ț Ş ş Ţ ţ",
    "el": "Αλφάβητο: α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ ς τ υ φ χ ψ ω · Α Β Γ Δ Ω",
    "ru": "Съешь же ещё этих мягких французских булок да выпей чаю. Ёё Йй Щщ Ъъ",
    "digits": "0123456789 1,234,567.89 ½ ¼ ¾ ⅓ ⅔ ¹²³ ₩1,000 €12,50 $9.99 ¥ ₹ ％ ０１２３４５６７８９",
    "symbols": "※ ①②③ ㉠㉡㉢ ㈜ ㎏ ㎡ ℃ ← → ↔ ★ ☆ ○ ● ◎ ■ □ ◇ ◈ 「」『』 〈〉 《》 · … ― ~ ∼ ≒ ∠ ∴ ± × ÷ ≠ ≤ ≥ ∞ ⅔ ￢ ￣ ◌",
    "jamo": "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ ㅥㅱㅸㆁㆆㆍ ᄀᄂᄃ ᅡᅢᅣ ᆨᆩᆪ",
}
# 결합 시퀀스: (설명, 시퀀스, 프리컴포즈)
COMBINING = [
    ("n+U+0303 → ñ", "ñ", "ñ"), ("u+U+0308 → ü", "ü", "ü"), ("a+U+0301 → á", "á", "á"),
    ("c+U+0327 → ç", "ç", "ç"), ("e+U+030C → ě", "ě", "ě"), ("N+U+0303 → Ñ", "Ñ", "Ñ"),
    ("U+U+0308 → Ü", "Ü", "Ü"), ("o+U+0301 → ó", "ó", "ó"), ("i+U+0301 → í", "í", "í"),
    ("A+U+030A → Å", "Å", "Å"), ("s+U+0327 → ş", "ş", "ş"), ("z+U+0307 → ż", "ż", "ż"),
]
NFD_TESTS = [("한글 NFD", unicodedata.normalize("NFD", "한글"), "한글"), ("똠 NFD", unicodedata.normalize("NFD", "똠"), "똠"),
             ("힣 NFD", unicodedata.normalize("NFD", "힣"), "힣"), ("제니산스 NFD", unicodedata.normalize("NFD", "제니산스"), "제니산스")]


def make_face(path):
    """WOFF2 는 HarfBuzz 가 직접 못 열므로 fontTools 로 풀어(SFNT) 바이트로 넘긴다."""
    if str(path).endswith(".woff2"):
        import io
        f = TTFont(path)
        f.flavor = None
        b = io.BytesIO()
        f.save(b)
        f.close()
        blob = hb.Blob(b.getvalue())
    else:
        blob = hb.Blob.from_file_path(str(path))
    face = hb.Face(blob)
    font = hb.Font(face)
    return face, font


def shape(font, text, features=None, lang=None, script=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if lang:
        buf.language = lang
    if script:
        buf.script = script
    hb.shape(font, buf, features or {})
    return buf.glyph_infos, buf.glyph_positions


def gids(font, text, **kw):
    infos, _ = shape(font, text, **kw)
    return [i.codepoint for i in infos]


def advances(font, text, **kw):
    infos, pos = shape(font, text, **kw)
    return [p.x_advance for p in pos]


def check_font(path, rep, glyph_order):
    name = path.name
    face, font = make_face(path)
    # (a) 11,172 음절 한 글자씩 — 한 번에 셰이핑하면 클러스터로 확인 가능하나 "각 1자" 요구대로 개별 셰이핑
    notdef = []
    for cp in range(0xAC00, 0xD7A4):
        g = gids(font, chr(cp))
        if len(g) != 1 or g[0] == 0:
            notdef.append(cp)
    if notdef:
        rep.fail("hangul-11172", f"{name}: gid0/복수 글립 {len(notdef)} {Q.fmt_ranges(notdef, 30)}")
    else:
        rep.passed("hangul-11172", f"{name}: 11,172 음절 각각 1 글립·gid0 0건")
    # (b) 문단
    for k, t in SAMPLES.items():
        infos, _ = shape(font, t, lang=("es" if k == "es" else None))
        bad = [t[i.cluster] for i in infos if i.codepoint == 0]
        if bad:
            rep.fail("paragraph", f"{name}: {k} gid0 {len(bad)}건 {sorted(set(f'U+{ord(c):04X}' for c in bad))}")
        else:
            rep.passed("paragraph", f"{name}: {k} 문단 {len(t)}자 gid0 0건")
    # (c) 결합 시퀀스
    rows = []
    for desc, seq, pre in COMBINING:
        gs = gids(font, seq)
        gp = gids(font, pre)
        infos, pos = shape(font, seq)
        composed = gs == gp
        mark_ok = (len(gs) == 2 and 0 not in gs and pos[1].y_offset != 0) if not composed else True
        status = "ccmp 합성" if composed else ("mark 배치" if mark_ok else "실패")
        rows.append((desc, [glyph_order[g] if g < len(glyph_order) else g for g in gs], [glyph_order[g] for g in gp], status,
                     f"y_off={pos[1].y_offset if len(pos) > 1 else '-'}"))
        if 0 in gs:
            rep.fail("combining", f"{name}: {desc} gid0")
        elif not (composed or mark_ok):
            rep.fail("combining", f"{name}: {desc} 합성도 mark 배치도 아님")
    rep.md(f"### {name} 결합 시퀀스\n\n" + Q.table(["시퀀스", "결과 글립", "프리컴포즈 글립", "판정", "위치"], rows))
    composed_n = sum(1 for r in rows if r[3] == "ccmp 합성")
    mark_n = sum(1 for r in rows if r[3] == "mark 배치")
    rep.passed("combining", f"{name}: 결합 시퀀스 {len(rows)}종 — ccmp 합성 {composed_n}, mark 배치 {mark_n}, 실패 {len(rows) - composed_n - mark_n}")
    # (d) NFD 자모 → 음절
    for desc, seq, pre in NFD_TESTS:
        gs, gp = gids(font, seq), gids(font, pre)
        if gs == gp:
            rep.passed("nfd", f"{name}: {desc} → 음절 합성 동일 ({len(gp)} 글립)")
        else:
            rep.fail("nfd", f"{name}: {desc} 결과 {gs} ≠ NFC {gp}")
    # (e) kern / tnum / pnum / frac / 전각 숫자 (spec 04 §3·§4)
    for pair in ("AV", "To", "Ya"):
        a_sum = sum(advances(font, pair, features={"kern": False}))
        k_sum = sum(advances(font, pair))
        if a_sum != k_sum:
            rep.passed("kern", f"{name}: '{pair}' kern 적용 ({a_sum} → {k_sum})")
        else:
            rep.warn("kern", f"{name}: '{pair}' kern 변화 없음 ({a_sum})")
    dig = "0123456789"
    adv_default = advances(font, dig)
    adv_tnum = advances(font, dig, features={"tnum": True})
    adv_pnum = advances(font, dig, features={"pnum": True})
    rep.info("digits", f"{name}: 기본 adv {adv_default} → {'proportional' if len(set(adv_default)) > 1 else 'tabular'}")
    if len(set(adv_tnum)) == 1:
        rep.passed("tnum", f"{name}: tnum 10자 adv 동일 ({adv_tnum[0]})")
    else:
        rep.fail("tnum", f"{name}: tnum adv 상이 {adv_tnum}")
    if len(set(adv_pnum)) > 1:
        rep.passed("pnum", f"{name}: pnum adv 상이(비례폭)")
    else:
        rep.fail("pnum", f"{name}: pnum adv 전부 동일")
    fw = advances(font, "０１２３４５６７８９")
    if set(fw) == {1920}:
        rep.passed("fullwidth-digits", f"{name}: 전각 숫자 adv 1920 동일")
    else:
        rep.fail("fullwidth-digits", f"{name}: 전각 숫자 adv {sorted(set(fw))}")
    g_frac = gids(font, "1/2", features={"frac": True})
    g_plain = gids(font, "1/2")
    rep.info("frac", f"{name}: '1/2' frac {'적용' if g_frac != g_plain else '변화 없음'} → {[glyph_order[g] for g in g_frac]}")
    g23 = gids(font, "2/3", features={"frac": True})
    rep.info("frac", f"{name}: '2/3' frac → {[glyph_order[g] for g in g23]} (⅔ 프리컴포즈 글립 {glyph_order[gids(font, '⅔')[0]]})")
    # 하이픈·NBSP·공백 폭
    sp, nb = advances(font, " ")[0], advances(font, " ")[0]
    if sp == nb:
        rep.passed("space", f"{name}: space = nbsp adv {sp}")
    else:
        rep.fail("space", f"{name}: space {sp} ≠ nbsp {nb}")
    return font


def check_vf_variations(path, rep, glyph_order):
    """변수 폰트: wght 100/500/900 에서도 gid0 0 (a)(b)(c)."""
    face, font = make_face(path)
    for w in (100, 250, 500, 650, 900):
        font.set_variations({"wght": w})
        bad = 0
        for cp in range(0xAC00, 0xD7A4, 7):  # 1,596자 표본
            g = gids(font, chr(cp))
            if len(g) != 1 or g[0] == 0:
                bad += 1
        for k, t in SAMPLES.items():
            bad += sum(1 for i in shape(font, t)[0] if i.codepoint == 0)
        for desc, seq, pre in COMBINING:
            bad += (0 in gids(font, seq))
        if bad:
            rep.fail("vf-wght", f"{path.name} wght={w}: gid0 {bad}건")
        else:
            rep.passed("vf-wght", f"{path.name} wght={w}: 한글 표본 1,596 + 문단 + 결합 시퀀스 gid0 0건")
        # 보충 글립 진행폭이 웨이트에 따라 phantom 델타로 바뀌는지(㉠ = ① adv)
        a1, a2 = advances(font, "①")[0], advances(font, "㉠")[0]
        if a1 == a2:
            rep.passed("vf-phantom", f"{path.name} wght={w}: ㉠ adv {a2} = ① adv {a1}")
        elif abs(a1 - a2) <= 1:
            rep.warn("vf-phantom", f"{path.name} wght={w}: ㉠ adv {a2} vs ① adv {a1} (1 unit 차 — VF 의 ① 은 Pretendard VF 보간값, ㉠ 은 정적 참조값 유래)")
        else:
            rep.fail("vf-phantom", f"{path.name} wght={w}: ㉠ adv {a2} ≠ ① adv {a1}")


def main():
    rep = Q.Report("HarfBuzz 셰이핑 (게이트 2)")
    rep.info("env", f"uharfbuzz {hb.__version__}, harfbuzz {hb.version_string()}")
    for p in Q.ALL_FONTS:
        if not p.exists():
            rep.fail("file", f"{p} 없음")
            continue
        go = TTFont(p, lazy=True).getGlyphOrder()
        check_font(p, rep, go)
    for p in (Q.VF_TTF, Q.VF_WOFF2):
        if p.exists():
            check_vf_variations(p, rep, TTFont(p, lazy=True).getGlyphOrder())
    rep.write("shaping")


if __name__ == "__main__":
    main()
