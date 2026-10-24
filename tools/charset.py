# -*- coding: utf-8 -*-
"""
charset/*.txt 파서 (빌더·QA 공용). 형식은 charset/README.md §2 (참조 구현 charset/scripts/count.py 와 동일 계약).

  U+XXXX            # 설명
  U+XXXX-U+YYYY     # 설명   (폐구간, 끝값에도 U+)
  # 주석 / 빈 줄 무시

사용:
  from tools.charset import parse_file, load_sets, format_ranges, css_unicode_range
  sets = load_sets()             # {"required": set(int), "recommended": ..., "korean-old": ...}
CLI:
  PYTHONUTF8=1 python tools/charset.py                 # 집계
  PYTHONUTF8=1 python tools/charset.py --font X.ttf     # 폰트 cmap 대비 누락 목록
"""
import re
import sys
from pathlib import Path

try:
    from . import config
except ImportError:  # 스크립트 직접 실행
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import config

LINE_RE = re.compile(r"^\s*U\+([0-9A-Fa-f]{4,6})(?:\s*-\s*U\+([0-9A-Fa-f]{4,6}))?\s*$")


class CharsetError(ValueError):
    pass


def parse_file(path):
    """charset 파일 하나 → set(int). 형식 오류는 CharsetError(파일:줄번호)."""
    path = Path(path)
    cps = set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        body = line.split("#", 1)[0].strip()
        if not body:
            continue
        m = LINE_RE.match(body)
        if not m:
            raise CharsetError(f"{path}:{lineno}: 형식 오류: {line!r}")
        lo = int(m.group(1), 16)
        hi = int(m.group(2), 16) if m.group(2) else lo
        if hi < lo:
            raise CharsetError(f"{path}:{lineno}: 구간 역순: {line!r}")
        cps.update(range(lo, hi + 1))
    return cps


def load_sets(files=None):
    """{이름: set} — config.CHARSET_FILES 기준. 파일 간 겹침이 있으면 CharsetError."""
    files = files or config.CHARSET_FILES
    out = {}
    for name, p in files.items():
        out[name] = parse_file(p)
    names = list(out)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            dup = out[a] & out[b]
            if dup:
                raise CharsetError(f"{a} ∩ {b} 겹침 {len(dup)}개: {format_ranges(sorted(dup)[:10])} ...")
    return out


def build_target(sets=None):
    """빌드 대상 코드포인트 집합(config.BUILD_SETS 합집합)."""
    sets = sets or load_sets()
    out = set()
    for n in config.BUILD_SETS:
        out |= sets[n]
    return out


def to_ranges(cps):
    """정렬된 코드포인트 iterable → [(lo, hi), ...]"""
    out = []
    start = prev = None
    for c in sorted(set(cps)):
        if start is None:
            start = prev = c
        elif c == prev + 1:
            prev = c
        else:
            out.append((start, prev))
            start = prev = c
    if start is not None:
        out.append((start, prev))
    return out


def format_ranges(cps, sep=" "):
    """`U+XXXX` / `U+XXXX-U+YYYY` 표기(charset 파일 형식)."""
    return sep.join(f"U+{a:04X}" if a == b else f"U+{a:04X}-U+{b:04X}" for a, b in to_ranges(cps))


def css_unicode_range(cps):
    """CSS unicode-range 표기(`U+AC00-D7A3`, 끝값에 U+ 없음, 소문자 hex 는 Google 관행이나 대문자로 통일)."""
    return ", ".join(f"U+{a:04X}" if a == b else f"U+{a:04X}-{b:04X}" for a, b in to_ranges(cps))


def parse_css_unicode_range(text):
    """CSS unicode-range 문자열 → set(int). `U+XXXX`, `U+XXXX-YYYY`, `U+XX??` 지원."""
    cps = set()
    for tok in text.split(","):
        tok = tok.strip()
        if not tok:
            continue
        m = re.match(r"^U\+([0-9A-Fa-f?]{1,6})(?:-([0-9A-Fa-f]{1,6}))?$", tok, re.I)
        if not m:
            raise CharsetError(f"unicode-range 토큰 오류: {tok!r}")
        a, b = m.group(1), m.group(2)
        if "?" in a:
            lo = int(a.replace("?", "0"), 16)
            hi = int(a.replace("?", "F"), 16)
        else:
            lo = int(a, 16)
            hi = int(b, 16) if b else lo
        cps.update(range(lo, hi + 1))
    return cps


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--font", help="폰트 파일 cmap 대비 커버리지")
    ap.add_argument("--dump", choices=list(config.CHARSET_FILES), help="코드포인트 전체 나열")
    a = ap.parse_args(argv)
    sets = load_sets()
    for n, s in sets.items():
        print(f"{n:12s} {len(s):6d}  {format_ranges(s)[:100]}...")
    print(f"{'build_target':12s} {len(build_target(sets)):6d}")
    if a.dump:
        print(format_ranges(sets[a.dump], sep="\n"))
    if a.font:
        from fontTools.ttLib import TTFont
        cm = set(TTFont(a.font, lazy=True).getBestCmap())
        for n, s in sets.items():
            miss = s - cm
            print(f"{a.font}: {n} 보유 {len(s - miss)}/{len(s)} 누락 {len(miss)}: {format_ranges(miss)[:400]}")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
