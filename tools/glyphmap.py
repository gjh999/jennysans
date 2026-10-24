# -*- coding: utf-8 -*-
"""
tools/glyphmap.py — 글자맵 데이터 생성 (font-site 소유)

`dist/static/JennySans-Regular.ttf` 의 cmap 을 읽어 블록별 코드포인트·유니코드 이름을
`site/assets/glyphmap.json` 으로 쓴다. 페이지(`site/glyphs.html`)가 이 JSON 만 fetch 한다.

    PYTHONUTF8=1 python tools/glyphmap.py            # site/assets/glyphmap.json 생성
    PYTHONUTF8=1 python tools/glyphmap.py --print    # 블록별 집계만 출력

규칙
- **하드코딩하지 않는다**: 블록 정의(범위)만 두고 실제 수록 여부는 cmap 교집합으로 정한다.
  cmap 에 하나도 없는 블록은 JSON 에서 빠진다 → 1.100 의 한자 블록은 빌드에 들어오는 순간 자동으로 나타난다.
- 한글 음절·한자는 이름을 싣지 않는다(용량). 한글은 초성 19 그룹으로 나누고 자모 로마자 표를 함께 실어
  클라이언트가 "HANGUL SYLLABLE GA" 를 조립한다. 한자는 "CJK UNIFIED IDEOGRAPH-XXXX" 패턴.
- dist/ 는 읽기만 한다.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import config  # noqa: E402  (builder 소유, 읽기만)

OUT = ROOT / "site" / "assets" / "glyphmap.json"

# (id, 라벨, 설명, [범위…], 이름 싣기, 그룹 방식)
BLOCKS: list[dict] = [
    {"id": "hangul", "label": "한글 음절", "note": "현대 한글 완성형 (U+AC00–D7A3)",
     "ranges": [(0xAC00, 0xD7A3)], "names": False, "group": "hangul", "name_kind": "hangul"},
    {"id": "jamo", "label": "한글 자모", "note": "첫가끝 자모 (U+1100–11FF) · 자모 확장",
     "ranges": [(0x1100, 0x11FF), (0xA960, 0xA97F), (0xD7B0, 0xD7FF)], "names": True},
    {"id": "compat-jamo", "label": "호환 자모", "note": "ㄱ–ㆎ (U+3131–318E) — 낱자 표기·ㅋㅋ",
     "ranges": [(0x3130, 0x318F)], "names": True},
    {"id": "latin", "label": "라틴 기본", "note": "ASCII · Latin-1 Supplement — 영어·스페인어 등",
     "ranges": [(0x0020, 0x007E), (0x00A0, 0x00FF)], "names": True},
    {"id": "latin-ext", "label": "라틴 확장", "note": "Latin Extended-A/B · 결합 악센트 · 수식 문자",
     "ranges": [(0x0100, 0x024F), (0x02B0, 0x02FF), (0x0300, 0x036F), (0x1E00, 0x1EFF)], "names": True},
    {"id": "greek", "label": "그리스", "note": "모노토닉 그리스 (U+0370–03FF)",
     "ranges": [(0x0370, 0x03FF)], "names": True},
    {"id": "cyrillic", "label": "키릴", "note": "러시아어·우크라이나어 등 (U+0400–04FF)",
     "ranges": [(0x0400, 0x04FF)], "names": True},
    {"id": "punct", "label": "구두점 · 화폐", "note": "일반 구두점 · 상하첨자 · 화폐 (₩ € ₹ …)",
     "ranges": [(0x2000, 0x206F), (0x2070, 0x209F), (0x20A0, 0x20CF)], "names": True},
    {"id": "letterlike", "label": "문자형 · 숫자형", "note": "℃ ™ № · 로마숫자 · 분수",
     "ranges": [(0x2100, 0x214F), (0x2150, 0x218F)], "names": True},
    {"id": "arrows-math", "label": "화살표 · 수학", "note": "← → ⇒ · ± × ÷ ≠ ≤ ∞ ∴ √ ∑ ∫",
     "ranges": [(0x2190, 0x21FF), (0x2200, 0x22FF), (0x2300, 0x23FF)], "names": True},
    {"id": "enclosed", "label": "원문자 · 괄호문자", "note": "① ⑴ ⓐ ㉠ ㈜ ㈎",
     "ranges": [(0x2460, 0x24FF), (0x3200, 0x32FF)], "names": True},
    {"id": "units", "label": "단위", "note": "㎏ ㎡ ㎞ ㎐ ㏊ (CJK 호환)",
     "ranges": [(0x3300, 0x33FF)], "names": True},
    {"id": "shapes", "label": "괘선 · 도형 · 기호", "note": "─ ┌ █ ○ ● ■ △ ★ ☎ ♪",
     "ranges": [(0x2500, 0x257F), (0x2580, 0x259F), (0x25A0, 0x25FF), (0x2600, 0x26FF), (0x2700, 0x27BF)], "names": True},
    {"id": "cjk-punct", "label": "CJK 기호", "note": "「 」 『 』 〈 〉 【 】 · 、 。 ・",
     "ranges": [(0x3000, 0x303F), (0x30FB, 0x30FB)], "names": True},
    {"id": "fullwidth", "label": "전각 · 반각", "note": "Ａ Ｂ ０ １ ￦ ＠ (U+FF00–FFEF)",
     "ranges": [(0xFF00, 0xFFEF), (0xFFFD, 0xFFFD)], "names": True},
    # 1.100 대비 — cmap 에 한자가 들어오면 자동으로 나타난다(지금은 0개라 제외됨)
    {"id": "hanja", "label": "한자", "note": "KS X 1001 한자 (1.100 이후)",
     "ranges": [(0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF)], "names": False, "name_kind": "cjk"},
]

# 한글 음절 조립용 로마자 표(유니코드 이름 규칙 = 초성+중성+종성 로마자)
CHO = ["G", "GG", "N", "D", "DD", "R", "M", "B", "BB", "S", "SS", "", "J", "JJ", "C", "K", "T", "P", "H"]
JUNG = ["A", "AE", "YA", "YAE", "EO", "E", "YEO", "YE", "O", "WA", "WAE", "OE", "YO", "U", "WEO", "WE", "WI",
        "YU", "EU", "YI", "I"]
JONG = ["", "G", "GG", "GS", "N", "NJ", "NH", "D", "L", "LG", "LM", "LB", "LS", "LT", "LP", "LH", "M", "B",
        "BS", "S", "SS", "NG", "J", "C", "K", "T", "P", "H"]
CHO_LABEL = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]


def compress(cps: list[int]) -> list[list[int]]:
    """정렬된 코드포인트 목록 → [[start, end], …]"""
    out: list[list[int]] = []
    for cp in cps:
        if out and cp == out[-1][1] + 1:
            out[-1][1] = cp
        else:
            out.append([cp, cp])
    return out


def build(font_path: Path) -> dict:
    from fontTools.ttLib import TTFont

    f = TTFont(str(font_path), lazy=True)
    cmap = set(f.getBestCmap())
    f.close()

    blocks: list[dict] = []
    seen: set[int] = set()
    for spec in BLOCKS:
        cps = sorted({cp for a, b in spec["ranges"] for cp in range(a, b + 1) if cp in cmap} - seen)
        if not cps:
            continue
        seen |= set(cps)
        block: dict = {"id": spec["id"], "label": spec["label"], "note": spec["note"],
                       "count": len(cps), "ranges": compress(cps)}
        if spec.get("name_kind"):
            block["name_kind"] = spec["name_kind"]
        if spec.get("names"):
            names = {}
            for cp in cps:
                try:
                    names[f"{cp:04X}"] = unicodedata.name(chr(cp))
                except ValueError:
                    names[f"{cp:04X}"] = ""
            block["names"] = names
        if spec.get("group") == "hangul":
            groups = []
            for i, lab in enumerate(CHO_LABEL):
                g = [cp for cp in cps if 0xAC00 + i * 588 <= cp <= 0xAC00 + i * 588 + 587]
                if g:
                    groups.append({"label": lab, "count": len(g), "ranges": compress(g)})
            block["groups"] = groups
        blocks.append(block)

    # 그 밖(정의된 블록에 없는 cmap 코드포인트)도 빠뜨리지 않는다
    rest = sorted(cmap - seen)
    if rest:
        names = {}
        for cp in rest:
            try:
                names[f"{cp:04X}"] = unicodedata.name(chr(cp))
            except ValueError:
                names[f"{cp:04X}"] = ""
        blocks.append({"id": "other", "label": "그 밖", "note": "위 블록에 없는 나머지",
                       "count": len(rest), "ranges": compress(rest), "names": names})

    return {
        "generated": _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds"),
        "version": config.VERSION,
        "font": font_path.name,
        "total": len(cmap),
        "hangul_jamo_roman": {"cho": CHO, "jung": JUNG, "jong": JONG},
        "blocks": blocks,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="글자맵 JSON 생성")
    ap.add_argument("--font", default=str(config.DIST_STATIC / "JennySans-Regular.ttf"))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--print", dest="show", action="store_true", help="집계만 출력(파일도 씀)")
    args = ap.parse_args(argv)

    font = Path(args.font)
    if not font.exists():
        raise SystemExit(f"!! 폰트가 없다: {font}")
    data = build(font)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"== 글자맵: {out} ({out.stat().st_size:,} bytes) · cmap {data['total']:,} · 블록 {len(data['blocks'])}")
    if args.show:
        for b in data["blocks"]:
            g = f" · 그룹 {len(b['groups'])}" if b.get("groups") else ""
            print(f"  {b['id']:<14} {b['label']:<14} {b['count']:>6,}{g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
