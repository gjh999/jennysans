#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KS X 1001 전 영역이 charset 파일에 어떻게 배치됐는지 검증한다(README 근거).

  - 기호 영역 행1~12 (0xA1A1–0xACFE): 행별로 required / recommended / korean-old / 없음 개수
  - 한글 완성형 2,350자 (행16~40, 0xB0A1–0xC8FE): required 포함 여부 + 정확한 수(웹 분할 1티어 근거, docs/spec/05-web.md)
  - 한자 4,888자 (행42~93): 범위 밖 확인

실행: PYTHONUTF8=1 python charset/scripts/check_ks.py [--md] [--dump-2350 경로]
기대값: 행1~3·6~9 및 행5 로마숫자 → required 100%, 행4 → required, 행5 그리스·행12 키릴 → recommended,
        행10·11 가나 → 없음(범위 밖), 2,350 완성형 → required 100%, 한자 → 없음.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from count import parse_file, CHARSET_DIR  # noqa: E402
from ksx1001_symbols import decode_rows, ROW_LABEL  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--dump-2350", help="KS 완성형 2,350자 코드포인트를 U+XXXX 형식으로 저장")
    args = ap.parse_args()

    sets = {}
    for name in ("required.txt", "recommended.txt", "korean-old.txt"):
        sets[name.replace(".txt", "")] = parse_file(os.path.join(CHARSET_DIR, name))["cps"]

    def where(cp):
        for k, s in sets.items():
            if cp in s:
                return k
        return "없음"

    rows = []
    decoded, _ = decode_rows("cp949", 1, 12)
    by_row = {}
    for row, col, cp in decoded:
        by_row.setdefault(row, []).append(cp)
    for row in sorted(by_row):
        cnt = {"required": 0, "recommended": 0, "korean-old": 0, "없음": 0}
        for cp in by_row[row]:
            cnt[where(cp)] += 1
        rows.append((ROW_LABEL.get(row, f"행{row}"), len(by_row[row]), cnt))

    # 한글 완성형 2,350 (행 16~40)
    hangul, _ = decode_rows("cp949", 16, 40)
    hcps = [cp for _, _, cp in hangul]
    assert all(0xAC00 <= c <= 0xD7A3 for c in hcps), "행16~40 에 비한글 코드포인트"
    h_req = sum(1 for c in hcps if c in sets["required"])
    # 한자 (행 42~93)
    hanja, _ = decode_rows("cp949", 42, 93)
    jcps = [cp for _, _, cp in hanja]
    j_any = sum(1 for c in jcps if where(c) != "없음")

    if args.md:
        print("| KS X 1001 영역 | 자수 | required | recommended | korean-old | 없음(범위 밖) |")
        print("|---|---|---|---|---|---|")
        for label, n, cnt in rows:
            print(f"| {label} | {n} | {cnt['required']} | {cnt['recommended']} | {cnt['korean-old']} | {cnt['없음']} |")
        print(f"| 행16~40 한글 완성형 | {len(hcps)} | {h_req} | 0 | 0 | {len(hcps) - h_req} |")
        print(f"| 행42~93 한자 | {len(jcps)} | 0 | 0 | 0 | {len(jcps) - j_any} |")
    else:
        for label, n, cnt in rows:
            print(f"{label:34s} {n:3d}  " + "  ".join(f"{k}={v}" for k, v in cnt.items()))
        print(f"행16~40 한글 완성형: {len(hcps)}자, required 포함 {h_req}")
        print(f"행42~93 한자: {len(jcps)}자, charset 포함 {j_any} (기대 0)")

    if args.dump_2350:
        with open(args.dump_2350, "w", encoding="utf-8") as f:
            f.write("# KS X 1001 Hangul syllables (rows 16-40, cp949 decode) — %d code points, in KS order\n" % len(hcps))
            for cp in hcps:
                f.write(f"U+{cp:04X}  # {chr(cp)}\n")
        print("wrote", args.dump_2350)


if __name__ == "__main__":
    main()
