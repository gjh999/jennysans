# -*- coding: utf-8 -*-
"""
웹 산출물 검사 (spec 05 §3·§4·§7-4, 01 §4·§5).
- CSS 4종 파싱: @font-face 블록 수, url() 실존, unicode-range 문법, font-family "JennySans", font-display swap.
- 분할: (a) 각 슬라이스 cmap ⊆ 자기 unicode-range (b) 슬라이스 간 교집합 0 (c) 합집합 = 전체본 cmap (d) #123 에 U+0020·U+00A0
  (e) 9 웨이트·변수 슬라이스 정의 동일 (f) rest(#124–) 코드포인트 목록 기록.
- WOFF2 열림·테이블·메트릭, 파일 크기 표(정적 슬라이스 ≤40 KB·라틴 ≤35 KB, 변수 슬라이스 ≤95 KB·라틴 ≤70 KB, CSS gzip ≤110 KB — 스펙 05 §4, 2026-09-09 조정). KB = 1,000 bytes.
실행: PYTHONUTF8=1 python docs/qa/scripts/web.py
"""
import gzip
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
import charset  # noqa: E402  (tools/charset.py — parse_css_unicode_range)

FACE_RE = re.compile(r"@font-face\s*\{(.*?)\}", re.S)


def parse_css(path):
    text = path.read_text(encoding="utf-8")
    faces = []
    for m in FACE_RE.finditer(text):
        body = m.group(1)
        d = {}
        for line in body.split(";"):
            if ":" in line:
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()
        urls = re.findall(r'url\("([^"]+)"\)', body)
        d["_urls"] = urls
        faces.append(d)
    return text, faces


def main():
    rep = Q.Report("웹 산출물: CSS·분할·WOFF2 (spec 05)")
    full_cmaps = {}
    for p in Q.STATIC_WOFF2 + [Q.VF_WOFF2]:
        f = TTFont(p)
        full_cmaps[p.stem] = set(f.getBestCmap())
        rep.passed("woff2", f"{p.name}: 열림, flavor {f.flavor}, cmap {len(full_cmaps[p.stem])}, {p.stat().st_size:,} B, 테이블 {len(f.keys())}")
        f.close()
    slice_defs = {}   # stem → {n: set(cps)}
    size_rows = []
    for css in sorted(Q.CSS_DIR.glob("*.css")):
        text, faces = parse_css(css)
        gz = len(gzip.compress(text.encode("utf-8")))
        rep.info("css", f"{css.name}: {css.stat().st_size:,} B (gzip {gz:,} B), @font-face {len(faces)}")
        bad_url, bad_fam, bad_disp, bad_ur = [], [], [], []
        for d in faces:
            for u in d["_urls"]:
                if not (css.parent / u).resolve().exists():
                    bad_url.append(u)
            if d.get("font-family") != '"JennySans"':
                bad_fam.append(d.get("font-family"))
            if d.get("font-display") != "swap":
                bad_disp.append(d.get("font-display"))
            if "unicode-range" in d:
                try:
                    charset.parse_css_unicode_range(d["unicode-range"])
                except Exception as e:
                    bad_ur.append(str(e))
        (rep.passed if not (bad_url or bad_fam or bad_disp or bad_ur) else rep.fail)(
            "css", f"{css.name}: url 실존 위반 {len(bad_url)}, font-family 위반 {len(bad_fam)}, font-display 위반 {len(bad_disp)}, unicode-range 문법 오류 {len(bad_ur)} {bad_url[:3]}{bad_ur[:2]}")
        if "dynamic-subset" in css.name:
            for d in faces:
                u = d["_urls"][0]
                m = re.match(r"\.\./web/subset/(.+)\.subset\.(\d+)\.woff2$", u)
                if not m:
                    rep.fail("css", f"{css.name}: 분할 파일명 규칙 위반 {u}")
                    continue
                stem, n = m.group(1), int(m.group(2))
                slice_defs.setdefault(stem, {})[n] = charset.parse_css_unicode_range(d["unicode-range"])
            if "variable" in css.name:
                (rep.passed if all(d.get("font-weight") == "100 900" for d in faces) else rep.fail)("css", f"{css.name}: font-weight '100 900' 전부")
            else:
                ws = sorted({int(d.get("font-weight")) for d in faces})
                (rep.passed if ws == [100, 200, 300, 400, 500, 600, 700, 800, 900] else rep.fail)("css", f"{css.name}: font-weight 집합 {ws}")
        if css.name == "jennysans-variable.css":
            (rep.passed if "tech(\"variations\")" in text and "woff2-variations" in text and len(faces) == 1 else rep.fail)("css", f"{css.name}: 변수 src 3중 폴백 표기")
        if css.name == "jennysans.css":
            (rep.passed if len(faces) == 9 else rep.fail)("css", f"{css.name}: @font-face 9")
        # 목표치는 스펙 05 §4 (팀장 결정 AGENTS §8 2026-09-09 로 실측 기준 조정). KB = 1,000 bytes(프로젝트 표기 규약).
        gzip_target = 110_000 if css.name == "jennysans-dynamic-subset.css" else None
        if gzip_target:
            (rep.passed if gz <= gzip_target else rep.warn)("size", f"{css.name}: gzip {gz:,} B (목표 ≤ {gzip_target // 1000} KB, 스펙 05 §4)")
    # 분할 정합
    ref_def = None
    rest_cps = None
    for stem, defs in slice_defs.items():
        full = full_cmaps[stem]
        union, overlap, subset_viol, sizes = set(), 0, [], []
        for n, rng in sorted(defs.items()):
            p = Q.SUBSET_DIR / f"{stem}.subset.{n}.woff2"
            if not p.exists():
                rep.fail("slice", f"{p.name} 없음")
                continue
            f = TTFont(p)
            cm = set(f.getBestCmap())
            f.close()
            sizes.append((n, p.stat().st_size))
            if not cm <= rng:
                subset_viol.append((n, len(cm - rng)))
            overlap += len(union & cm)
            union |= cm
        missing = full - union
        extra = union - full
        rest_n = [n for n in defs if n >= 124]
        d_rest = set().union(*[defs[n] for n in rest_n]) if rest_n else set()
        d_signature = {n: (len(v), min(v), max(v)) for n, v in defs.items()}
        if ref_def is None:
            ref_def, ref_stem, rest_cps = d_signature, stem, d_rest
        same_def = d_signature == ref_def
        latin = defs.get(123, set())
        ok = not subset_viol and overlap == 0 and not missing and not extra and {0x20, 0xA0} <= latin and same_def
        (rep.passed if ok else rep.fail)("slice", f"{stem}: 슬라이스 {len(defs)}개, cmap⊆range 위반 {subset_viol[:3]}, 겹침 {overlap}, 합집합−전체본 누락 {len(missing)} 추가 {len(extra)}, #123 space/nbsp {({0x20, 0xA0} <= latin)}, 정의 = {ref_stem} {same_def}")
        mx = max(s for _, s in sizes)
        lat = dict(sizes).get(123, 0)
        # 스펙 05 §4: 변수 슬라이스 ≤95 KB·라틴 ≤70 KB(2026-09-09 조정), 정적 슬라이스 ≤40 KB·라틴 ≤35 KB. KB = 1,000 bytes.
        lim = 95_000 if "Variable" in stem else 40_000
        lat_lim = 70_000 if "Variable" in stem else 35_000
        (rep.passed if mx <= lim and lat <= lat_lim else rep.warn)("size", f"{stem}: 슬라이스 최대 {mx:,} B (≤{lim // 1000} KB), 라틴 #123 {lat:,} B (≤{lat_lim // 1000} KB), 합계 {sum(s for _, s in sizes):,} B, rest #{rest_n} {sum(dict(sizes).get(n, 0) for n in rest_n):,} B")
        size_rows.append((stem, len(defs), f"{sum(s for _, s in sizes):,}", f"{min(s for _, s in sizes):,}", f"{mx:,}", f"{lat:,}", f"{sum(dict(sizes).get(n, 0) for n in rest_n):,}"))
    rep.md("## 분할 크기\n\n" + Q.table(["stem", "슬라이스", "합계 B", "최소", "최대", "라틴 #123", "rest"], size_rows))
    if rest_cps:
        rep.md(f"## rest 슬라이스(#124–) 코드포인트 {len(rest_cps)}개\n\n`{Q.fmt_ranges(rest_cps)}`")
    # subset 디렉터리 파일 수·규칙 외 파일
    files = list(Q.SUBSET_DIR.glob("*"))
    bad = [p.name for p in files if not re.match(r"^JennySans(-\w+|Variable)\.subset\.\d+\.woff2$", p.name)]
    (rep.passed if not bad else rep.fail)("files", f"dist/web/subset 파일 {len(files)}개, 규칙 외 {bad[:5]}")
    rep.write("web")


if __name__ == "__main__":
    main()
