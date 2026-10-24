#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
charset/*.txt 파서 + 검증 + 집계 (빌더 `tools/charset.py` 와 QA 커버리지 검사의 참조 구현).

파일 형식(빌더·QA 공통 계약):
  - 한 줄에 하나: `U+XXXX` 또는 `U+XXXX-U+YYYY` (16진 4~6자리, 대소문자 무관). 뒤에 `  # 설명` 허용.
  - `#` 로 시작하는 줄과 빈 줄은 무시. 인라인 `#` 이후는 주석.
  - 같은 파일 안의 중복은 허용(집합으로 합침)하되 경고. 파일 간(required/recommended/korean-old) 겹침은 오류.
  - 미할당(unassigned) 코드포인트가 구간 안에 있으면 경고만(구간 표기의 편의상 허용) — 단, 빌더는 서브셋 시
    cmap 에 없는 코드포인트를 무시하므로 실제 요구 수는 "할당된 코드포인트 수" 로 본다.

실행:
  PYTHONUTF8=1 python charset/scripts/count.py                # 세 파일 집계 + 검증
  PYTHONUTF8=1 python charset/scripts/count.py --md           # README 용 Markdown 표
  PYTHONUTF8=1 python charset/scripts/count.py --font X.ttf   # 폰트 cmap 대비 커버리지(누락 목록)
  PYTHONUTF8=1 python charset/scripts/count.py --dump required  # 코드포인트 전체 나열(디버그)
종료 코드: 형식 오류·파일 간 겹침이 있으면 1.
"""
import argparse
import os
import re
import sys
import unicodedata
from collections import OrderedDict

CHARSET_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["required.txt", "recommended.txt", "korean-old.txt"]

LINE_RE = re.compile(r"^\s*U\+([0-9A-Fa-f]{4,6})(?:\s*-\s*U\+([0-9A-Fa-f]{4,6}))?\s*$")

# 집계용 블록(유니코드 블록을 프로젝트 관점으로 묶음). 순서대로 첫 매칭.
BLOCKS = [
    (0x0020, 0x007E, "ASCII (Basic Latin)"),
    (0x00A0, 0x00FF, "Latin-1 Supplement"),
    (0x0100, 0x017F, "Latin Extended-A"),
    (0x0180, 0x024F, "Latin Extended-B"),
    (0x02B0, 0x02FF, "Spacing Modifier Letters"),
    (0x0300, 0x036F, "Combining Diacritical Marks"),
    (0x0370, 0x03FF, "Greek and Coptic"),
    (0x0400, 0x04FF, "Cyrillic"),
    (0x1100, 0x11FF, "Hangul Jamo"),
    (0x1E00, 0x1EFF, "Latin Extended Additional"),
    (0x2000, 0x206F, "General Punctuation"),
    (0x2070, 0x209F, "Superscripts and Subscripts"),
    (0x20A0, 0x20CF, "Currency Symbols"),
    (0x2100, 0x214F, "Letterlike Symbols"),
    (0x2150, 0x218F, "Number Forms"),
    (0x2190, 0x21FF, "Arrows"),
    (0x2200, 0x22FF, "Mathematical Operators"),
    (0x2300, 0x23FF, "Miscellaneous Technical"),
    (0x2460, 0x24FF, "Enclosed Alphanumerics"),
    (0x2500, 0x257F, "Box Drawing"),
    (0x2580, 0x259F, "Block Elements"),
    (0x25A0, 0x25FF, "Geometric Shapes"),
    (0x2600, 0x26FF, "Miscellaneous Symbols"),
    (0x2700, 0x27BF, "Dingbats"),
    (0x3000, 0x303F, "CJK Symbols and Punctuation"),
    (0x30A0, 0x30FF, "Katakana (예외 1자)"),
    (0x3130, 0x318F, "Hangul Compatibility Jamo"),
    (0x3200, 0x32FF, "Enclosed CJK Letters and Months"),
    (0x3300, 0x33FF, "CJK Compatibility"),
    (0xA960, 0xA97F, "Hangul Jamo Extended-A"),
    (0xAC00, 0xD7A3, "Hangul Syllables"),
    (0xD7B0, 0xD7FF, "Hangul Jamo Extended-B"),
    (0xFE00, 0xFE0F, "Variation Selectors"),
    (0xFF00, 0xFFEF, "Halfwidth and Fullwidth Forms"),
    (0xFFF0, 0xFFFF, "Specials"),
]


def block_of(cp):
    for lo, hi, name in BLOCKS:
        if lo <= cp <= hi:
            return name
    return f"Other (U+{cp:04X})"


def parse_file(path):
    """반환: {'cps': set, 'entries': [(lo, hi, comment, lineno)], 'errors': [...], 'warnings': [...]}"""
    cps = set()
    entries = []
    errors = []
    warnings = []
    seen = set()
    with open(path, encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if "#" in line:
                body, comment = line.split("#", 1)
                comment = comment.strip()
            else:
                body, comment = line, ""
            body = body.strip()
            if not body:
                continue
            m = LINE_RE.match(body)
            if not m:
                errors.append(f"{os.path.basename(path)}:{lineno}: 형식 오류: {body!r}")
                continue
            lo = int(m.group(1), 16)
            hi = int(m.group(2), 16) if m.group(2) else lo
            if hi < lo:
                errors.append(f"{os.path.basename(path)}:{lineno}: 역순 구간 U+{lo:04X}-U+{hi:04X}")
                continue
            entries.append((lo, hi, comment, lineno))
            for cp in range(lo, hi + 1):
                if cp in seen:
                    warnings.append(f"{os.path.basename(path)}:{lineno}: 중복 U+{cp:04X}")
                seen.add(cp)
                cps.add(cp)
    return {"cps": cps, "entries": entries, "errors": errors, "warnings": warnings}


def assigned(cps):
    return {cp for cp in cps if unicodedata.name(chr(cp), None) is not None}


def block_table(cps):
    table = OrderedDict()
    for cp in sorted(cps):
        b = block_of(cp)
        table[b] = table.get(b, 0) + 1
    return table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="Markdown 표 출력")
    ap.add_argument("--font", help="TTF/OTF 경로: cmap 대비 커버리지 검사")
    ap.add_argument("--dump", help="파일 이름(required/recommended/korean-old): 코드포인트 나열")
    ap.add_argument("--dir", default=CHARSET_DIR)
    args = ap.parse_args()

    results = OrderedDict()
    all_errors = []
    all_warnings = []
    for name in FILES:
        path = os.path.join(args.dir, name)
        if not os.path.exists(path):
            all_errors.append(f"{name}: 파일 없음")
            continue
        r = parse_file(path)
        results[name] = r
        all_errors += r["errors"]
        all_warnings += r["warnings"]

    # 파일 간 겹침 검사
    names = list(results)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ov = results[names[i]]["cps"] & results[names[j]]["cps"]
            if ov:
                sample = " ".join(f"U+{c:04X}" for c in sorted(ov)[:10])
                all_errors.append(f"{names[i]} ∩ {names[j]} = {len(ov)}개 (예: {sample})")

    if args.dump:
        key = args.dump if args.dump.endswith(".txt") else args.dump + ".txt"
        for cp in sorted(results[key]["cps"]):
            print(f"U+{cp:04X}\t{chr(cp)}\t{unicodedata.name(chr(cp), '<unassigned>')}")
        return

    # 집계
    if args.md:
        print("| 파일 | 코드포인트(구간 나열) | 할당된 코드포인트 | 미할당(구간 내 빈 칸) |")
        print("|---|---|---|---|")
        for name, r in results.items():
            a = assigned(r["cps"])
            print(f"| `{name}` | {len(r['cps']):,} | **{len(a):,}** | {len(r['cps']) - len(a):,} |")
        print()
        blocks = OrderedDict()
        for name, r in results.items():
            for b, n in block_table(assigned(r["cps"])).items():
                blocks.setdefault(b, {})[name] = n
        print("| 블록 | " + " | ".join(results) + " |")
        print("|---|" + "---|" * len(results))
        order = [b[2] for b in BLOCKS]
        keys = sorted(blocks, key=lambda k: order.index(k) if k in order else 999)
        for b in keys:
            print(f"| {b} | " + " | ".join(str(blocks[b].get(n, "")) for n in results) + " |")
    else:
        for name, r in results.items():
            a = assigned(r["cps"])
            print(f"{name}: 구간 {len(r['entries'])}개, 코드포인트 {len(r['cps']):,} (할당 {len(a):,}, 미할당 {len(r['cps']) - len(a):,})")
            for b, n in block_table(a).items():
                print(f"    {b:36s} {n:6,}")
            print()

    for w in all_warnings:
        print("WARN", w)
    for e in all_errors:
        print("ERROR", e)

    if args.font:
        from fontTools.ttLib import TTFont
        font = TTFont(args.font, lazy=True)
        cmap = font.getBestCmap() or {}
        glyph_set = font.getGlyphSet()
        print(f"\n[font] {args.font}: cmap {len(cmap):,} entries")
        for name, r in results.items():
            a = assigned(r["cps"])
            missing = sorted(c for c in a if c not in cmap)
            print(f"  {name}: {len(a) - len(missing):,}/{len(a):,} 커버, 누락 {len(missing):,}")
            bt = block_table(missing)
            for b, n in bt.items():
                sample = " ".join(f"U+{c:04X}" for c in [c for c in missing if block_of(c) == b][:8])
                print(f"      {b:36s} {n:6,}  {sample}")

    if all_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
