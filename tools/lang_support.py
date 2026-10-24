# -*- coding: utf-8 -*-
"""
tools/lang_support.py — 지원 언어 실측 (font-site 소유)

"몇 개 언어를 지원하나"를 **추측하지 않고** 실제 산출물 cmap 으로 검증한다.

    PYTHONUTF8=1 python tools/lang_support.py           # site/assets/languages.json 생성 + 요약 출력
    PYTHONUTF8=1 python tools/lang_support.py --md      # 표로 출력

검증 방법
1. 라틴 문자권 언어의 **정서법 필수 문자 목록**은 architect 소유 `charset/scripts/lang_check.py` 의 `LANGS`
   를 그대로 import 해서 쓴다(읽기만 — 목록이 갈라지지 않게).
2. 키릴·그리스·한국어·영어는 이 파일에서 필수 문자를 정의한다(각 언어 정서법의 자모 전부).
3. 각 언어의 **필수 문자 + 샘플 문장의 모든 글자**가 `dist/static/JennySans-Regular.ttf` 의 cmap 에
   전부 있을 때만 "지원"으로 센다. 하나라도 빠지면 제외하고 사유(빠진 코드포인트)를 기록한다.
   → 폰트가 바뀌면 숫자도 자동으로 바뀐다. 페이지에는 이 JSON 값만 들어간다.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "charset" / "scripts"))
import config  # noqa: E402

OUT = ROOT / "site" / "assets" / "languages.json"

# 라틴 문자권: (lang_check.py 의 표기, 한국어 이름, 자국어 이름, 샘플 문장)
LATIN_META = {
    "스페인어 es": ("스페인어", "Español", "El veloz murciélago hindú comía feliz cardillo y kiwi."),
    "포르투갈어 pt": ("포르투갈어", "Português", "Um pequeno jabuti xereta viu dez cegonhas felizes."),
    "프랑스어 fr": ("프랑스어", "Français", "Portez ce vieux whisky au juge blond qui fume."),
    "독일어 de": ("독일어", "Deutsch", "Falsches Üben von Xylophonmusik quält jeden größeren Zwerg."),
    "이탈리아어 it": ("이탈리아어", "Italiano", "Pranzo d'acqua fa volti sghembi. Perché non è così?"),
    "네덜란드어 nl": ("네덜란드어", "Nederlands", "Pa's wijze lynx bezag vroom het fikse aquaduct."),
    "폴란드어 pl": ("폴란드어", "Polski", "Zażółć gęślą jaźń — pchnąć w tę łódź jeża."),
    "체코어 cs": ("체코어", "Čeština", "Příliš žluťoučký kůň úpěl ďábelské ódy."),
    "슬로바키아어 sk": ("슬로바키아어", "Slovenčina", "Kŕdeľ šťastných ďatľov učí pri ústí Váhu mĺkveho koňa."),
    "헝가리어 hu": ("헝가리어", "Magyar", "Árvíztűrő tükörfúrógép a szomjas öreg fűzfa mögött."),
    "터키어 tr": ("터키어", "Türkçe", "Pijamalı hasta yağız şoföre çabucak güvendi."),
    "크로아티아어 hr": ("크로아티아어", "Hrvatski", "Čokolada, ćevapi, đak, šešir i žaba u Đakovu."),
    "슬로베니아어 sl": ("슬로베니아어", "Slovenščina", "Šerif bo za vajo spet skuhal domače žgance."),
    "루마니아어 ro": ("루마니아어", "Română", "Înțelepciunea și frumusețea în România de astăzi."),
    "리투아니아어 lt": ("리투아니아어", "Lietuvių", "Įlinkdama fechtuotojo špaga sublykčiojusi pragręžė apvalų arbūzą."),
    "라트비아어 lv": ("라트비아어", "Latviešu", "Glāžšķūņa rūķīši dzērumā čiepj Baha koncertflīģeļu vākus."),
    "에스토니아어 et": ("에스토니아어", "Eesti", "Põdur Zagrebi tšellomängija-följetonist läks garaaži."),
    "핀란드어 fi": ("핀란드어", "Suomi", "Törkylempijävongahdus — hyvän lämmön ääriviivat."),
    "스웨덴어 sv": ("스웨덴어", "Svenska", "Flygande bäckasiner söka hwila på mjuka tuvor."),
    "덴마크어/노르웨이어 da/no": ("덴마크어 · 노르웨이어", "Dansk · Norsk", "Høj bly gom vandt frækt på wc — æbler og øl i Åbenrå."),
    "아이슬란드어 is": ("아이슬란드어", "Íslenska", "Kæmi ný öxi hér, ykist þjófum nú bæði víl og ádrepa."),
    "카탈루냐어 ca": ("카탈루냐어", "Català", "Jove xef, porti whisky amb quinze glaçons d'hidrogen."),
    "갈리시아어 gl": ("갈리시아어", "Galego", "A lingua galega é o noso sinal de identidade máis señeiro."),
    "바스크어 eu": ("바스크어", "Euskara", "Euskara ez da hizkuntza arrunta; Iruñean ikasi dugu."),
    "몰타어 mt": ("몰타어", "Malti", "Ċikkulata bil-ġobon u ħwawar żgħar fil-belt."),
    "웨일스어 cy": ("웨일스어", "Cymraeg", "Mae'r ŵy hwn yn flasus iawn, a'r tŷ yn hyfryd."),
    "아일랜드어 ga": ("아일랜드어", "Gaeilge", "Chuaigh bé mhórshách le dlúthspád fíorfhinn."),
    "에스페란토 eo": ("에스페란토", "Esperanto", "Eĥoŝanĝo ĉiuĵaŭde — ĝi ja ŝajnas facila."),
}
LATIN_EXCLUDE = {"베트남어 vi(범위 밖)": ("베트남어", "Tiếng Việt")}

# 키릴 문자권: (한국어 이름, 자국어 이름, 정서법 필수 문자, 샘플 문장)
CYRILLIC = [
    ("러시아어", "Русский", "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
     "Съешь же ещё этих мягких французских булок, да выпей чаю."),
    ("우크라이나어", "Українська", "абвгґдеєжзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ",
     "Чуєш їх, доцю, га? Кумедна ж ти, знаєш?"),
    ("벨라루스어", "Беларуская", "абвгдеёжзійклмнопрстуўфхцчшыьэюяАБВГДЕЁЖЗІЙКЛМНОПРСТУЎФХЦЧШЫЬЭЮЯ",
     "Я жыву ў Беларусі — цудоўны край і мова."),
    ("불가리아어", "Български", "абвгдежзийклмнопрстуфхцчшщъьюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЮЯ",
     "Ах, чудна българска земьо, полюшвай цъфтящи жита."),
    ("세르비아어", "Српски", "абвгдђежзијклљмнњопрстћуфхцчџшАБВГДЂЕЖЗИЈКЛЉМНЊОПРСТЋУФХЦЧЏШ",
     "Љубазни фењерџија чађавог лица хоће да ми покаже штос."),
    ("마케도니아어", "Македонски", "абвгдѓежзѕијклљмнњопрстќуфхцчџшАБВГДЃЕЖЗЅИЈКЛЉМНЊОПРСТЌУФХЦЧЏШ",
     "Ѕидарот ѓоа ќе дојде да ја заврши куќата."),
]

# 그 밖(고유 문자)
OTHER = [
    ("한국어", "한국어", "가나다라마바사아자차카타파하", "다람쥐 헌 쳇바퀴에 타고파. 키스의 고유조건은 입술끼리 만나야 한다."),
    ("영어", "English", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
     "Sphinx of black quartz, judge my vow."),
    ("그리스어", "Ελληνικά", "αβγδεζηθικλμνξοπρστυφχψωάέήίόύώϊϋΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ",
     "Ξεσκεπάζω την ψυχοφθόρα βδελυγμία."),
]


def cmap_of(font_path: Path) -> set[int]:
    from fontTools.ttLib import TTFont

    f = TTFont(str(font_path), lazy=True)
    cm = set(f.getBestCmap())
    f.close()
    return cm


def missing(text: str, cmap: set[int]) -> list[int]:
    return sorted({ord(c) for c in text if not c.isspace() and ord(c) not in cmap})


def build(font_path: Path) -> dict:
    import lang_check  # charset/scripts (architect 소유 — 읽기만)

    cmap = cmap_of(font_path)
    groups: dict[str, list[dict]] = {"latin": [], "cyrillic": [], "other": []}
    excluded: list[dict] = []

    def check(name_ko: str, name_native: str, letters: str, sample: str, script: str) -> None:
        miss = sorted(set(missing(letters, cmap)) | set(missing(sample, cmap)))
        entry = {"name": name_ko, "native": name_native, "sample": sample, "letters": len(set(letters)),
                 "script": script}
        if miss:
            entry["missing"] = [f"U+{c:04X}" for c in miss]
            excluded.append(entry)
        else:
            groups[script].append(entry)

    for label, must, _opt in lang_check.LANGS:
        if label in LATIN_META:
            ko, native, sample = LATIN_META[label]
            check(ko, native, must, sample, "latin")
        elif label in LATIN_EXCLUDE:
            ko, native = LATIN_EXCLUDE[label]
            miss = missing(must, cmap)
            excluded.append({"name": ko, "native": native, "script": "latin", "sample": "",
                             "missing": [f"U+{c:04X}" for c in miss[:6]] + (["…"] if len(miss) > 6 else []),
                             "missing_count": len(miss), "reason": "원본 폰트 미보유(후속 검토)"})
        # LATIN_META 에 없는 새 언어가 lang_check 에 추가되면 조용히 빠지지 않도록 알린다
        elif label not in LATIN_EXCLUDE:
            excluded.append({"name": label, "native": "", "script": "latin", "sample": "",
                             "reason": "tools/lang_support.py LATIN_META 에 샘플 문장 미등록"})

    for ko, native, letters, sample in CYRILLIC:
        check(ko, native, letters, sample, "cyrillic")
    for ko, native, letters, sample in OTHER:
        check(ko, native, letters, sample, "other")

    # 항목 수와 실제 언어 수를 나눠 센다("덴마크어 · 노르웨이어" 처럼 한 항목이 두 언어인 경우)
    counts = {k: len(v) for k, v in groups.items()}
    langs = {k: sum(len(e["name"].split(" · ")) for e in v) for k, v in groups.items()}
    for k, v in groups.items():
        for e in v:
            e["langs"] = len(e["name"].split(" · "))
    return {
        "generated": _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds"),
        "version": config.VERSION,
        "font": font_path.name,
        "method": "정서법 필수 문자 + 샘플 문장의 모든 글자가 dist 산출물 cmap 에 있을 때만 지원으로 셈 "
                  "(라틴 목록은 charset/scripts/lang_check.py 의 LANGS 를 그대로 사용)",
        "counts": {**counts, "total": sum(counts.values())},
        "languages": {**langs, "total": sum(langs.values())},
        "groups": groups,
        "excluded": excluded,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="지원 언어 실측 → site/assets/languages.json")
    ap.add_argument("--font", default=str(config.DIST_STATIC / "JennySans-Regular.ttf"))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--md", action="store_true")
    args = ap.parse_args(argv)

    font = Path(args.font)
    if not font.exists():
        raise SystemExit(f"!! 폰트가 없다: {font}")
    data = build(font)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    c, L = data["counts"], data["languages"]
    print(f"== 지원 언어(항목/언어): 라틴 {c['latin']}/{L['latin']} · 키릴 {c['cyrillic']}/{L['cyrillic']} · "
          f"그 밖 {c['other']}/{L['other']} = 총 {c['total']}항목 / {L['total']}개 언어 → {out}")
    if args.md:
        print("\n| 문자권 | 언어 | 표기 | 샘플 |\n|---|---|---|---|")
        for script, rows in data["groups"].items():
            for r in rows:
                print(f"| {script} | {r['name']} | {r['native']} | {r['sample']} |")
    for e in data["excluded"]:
        print(f"  제외: {e['name']} — {e.get('reason') or ('빠진 글자 ' + ' '.join(e.get('missing', [])[:8]))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
