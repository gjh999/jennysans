# -*- coding: utf-8 -*-
"""
tools/origin_diff.py — "원본과 무엇이 다른가" 실측 (font-site 소유)

주원본 Pretendard(정적 Regular)와 산출물 JennySans-Regular 의 **cmap 을 직접 비교**해
카테고리별 증감·전체 추가/제외 수를 `site/assets/origin-diff.json` 으로 쓴다.
페이지의 차이 표는 이 JSON 값으로 렌더된다(하드코딩 없음).

    PYTHONUTF8=1 python tools/origin_diff.py          # JSON 생성 + 표 출력
    PYTHONUTF8=1 python tools/origin_diff.py --md     # Markdown 표만

sources/ 와 dist/ 는 읽기만 한다.
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
import config  # noqa: E402

OUT = ROOT / "site" / "assets" / "origin-diff.json"

# (라벨, 설명, [범위…])  — 한국 문서·다국어 실무에서 눈에 띄게 달라진 영역
CATEGORIES = [
    ("첫가끝 자모", "U+1100–11FF — NFD 분해 텍스트(macOS 파일명)·옛자모 단독", [(0x1100, 0x11FF)]),
    ("옛 호환자모", "U+3131–318E — ㅥ ㅱ ㅸ ㆁ ㆆ ㆍ 등 잔여", [(0x3131, 0x318E)]),
    ("자모 확장 A·B", "U+A960–A97F · U+D7B0–D7FF", [(0xA960, 0xA97F), (0xD7B0, 0xD7FF)]),
    ("괘선", "U+2500–257F — ─ │ ┌ ┼ ┃ ═", [(0x2500, 0x257F)]),
    ("블록 요소", "U+2580–259F — █ ▒ ▤", [(0x2580, 0x259F)]),
    ("원문자 · 괄호문자", "U+2460–24FF · U+3200–32FF — ① ⑴ ⓐ ㉠ ㈜ ㈎", [(0x2460, 0x24FF), (0x3200, 0x32FF)]),
    ("수학 기호", "U+2200–22FF — ∠ ∴ ∵ ≡ ∫ ∑", [(0x2200, 0x22FF)]),
    ("도형 · 기타 기호", "U+25A0–25FF · U+2600–26FF — ◎ ◐ ☎ ♨ ♬", [(0x25A0, 0x25FF), (0x2600, 0x26FF)]),
    ("단위", "U+3380–33DF — ㎏ ㎡ ㎐ ㏊", [(0x3380, 0x33DF)]),
    ("일본어 가나", "U+3040–30FF — 한국 문서에 쓰이지 않아 제외(・ 1자만 유지)", [(0x3040, 0x30FF)]),
]


def cmap_of(p: Path) -> set[int]:
    from fontTools.ttLib import TTFont

    f = TTFont(str(p), lazy=True)
    cm = set(f.getBestCmap())
    f.close()
    return cm


def build(origin: Path, ours: Path) -> dict:
    P, J = cmap_of(origin), cmap_of(ours)
    rows = []
    added_in_cats = 0
    for label, note, ranges in CATEGORIES:
        a = sum(1 for r in ranges for cp in range(r[0], r[1] + 1) if cp in P)
        b = sum(1 for r in ranges for cp in range(r[0], r[1] + 1) if cp in J)
        gain = sum(1 for r in ranges for cp in range(r[0], r[1] + 1) if cp in J and cp not in P)
        rows.append({"label": label, "note": note, "origin": a, "ours": b, "delta": b - a, "added": gain,
                     "ranges": [f"U+{r[0]:04X}-U+{r[1]:04X}" for r in ranges]})
        if b - a > 0:
            added_in_cats += gain

    # 웹 분할본 규모(파일 수·라틴 조각 크기)도 같이 실측
    subset_dir = config.DIST_WEB_SUBSET
    slice_files = sorted(subset_dir.glob("*.woff2")) if subset_dir.exists() else []
    per_weight = len([p for p in slice_files if p.name.startswith("JennySans-Regular.subset.")])

    return {
        "generated": _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds"),
        "version": config.VERSION,
        "origin": {"file": origin.name, "path": str(origin.relative_to(ROOT)), "cmap": len(P),
                   "version": config.PRETENDARD_VERSION},
        "ours": {"file": ours.name, "cmap": len(J)},
        "rows": rows,
        "totals": {
            "category_added": added_in_cats,          # 위 카테고리에서 새로 채운 문자
            "kana_removed": sum(1 for cp in range(0x3040, 0x3100) if cp in P and cp not in J),
            "added_total": len(J - P),                # 원본에 없던 문자 전부
            "removed_total": len(P - J),              # 범위 밖으로 뺀 문자 전부
        },
        "web": {"slice_files": len(slice_files), "slices_per_weight": per_weight},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", default=str(config.PRETENDARD_TTF_DIR / "Pretendard-Regular.ttf"))
    ap.add_argument("--ours", default=str(config.DIST_STATIC / "JennySans-Regular.ttf"))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--md", action="store_true")
    args = ap.parse_args(argv)

    origin, ours = Path(args.origin), Path(args.ours)
    for p in (origin, ours):
        if not p.exists():
            raise SystemExit(f"!! 없다: {p}")
    d = build(origin, ours)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    if args.md:
        print(f"| 영역 | Pretendard 1.3.9 | JennySans {config.VERSION} | 증감 |\n|---|---|---|---|")
        for r in d["rows"]:
            print(f"| {r['label']} | {r['origin']} | {r['ours']} | {r['delta']:+d} |")
    else:
        for r in d["rows"]:
            print(f"  {r['label']:<18} {r['origin']:>5} → {r['ours']:>5}  ({r['delta']:+5d})   {r['note']}")
    t = d["totals"]
    print(f"== 카테고리 순수 추가 {t['category_added']:,}자 · 가나 제외 {t['kana_removed']}자 · "
          f"원본 대비 추가 {t['added_total']:,} / 제외 {t['removed_total']:,} "
          f"(cmap {d['origin']['cmap']:,} → {d['ours']['cmap']:,}) → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
