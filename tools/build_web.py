# -*- coding: utf-8 -*-
"""
웹 산출: 정적 9 + 변수 전체 WOFF2, Google Fonts 한국어 124 슬라이스 unicode-range(docs/research/google-kr-slices.css)
분할 WOFF2, CSS 3종(+변수 분할 1종).

  dist/web/JennySans-<W>.woff2, dist/web/JennySansVariable.woff2
  dist/web/subset/JennySans-<W>.subset.<n>.woff2, dist/web/subset/JennySansVariable.subset.<n>.woff2
  dist/css/jennysans.css · jennysans-variable.css · jennysans-dynamic-subset.css · jennysans-variable-dynamic-subset.css
  tools/data/korean-slices.google.json (CSS 에서 파싱한 슬라이스 정의 — 재현용)

슬라이스 규칙: Google 124 블록을 그대로 쓰되 (a) 같은 코드포인트가 여러 블록에 있으면 뒤 블록(브라우저 우선순위)에 남긴다
(b) 어느 블록에도 없는 cmap 코드포인트는 마지막 슬라이스 `rest`(#124)에 넣는다 (c) 빈 슬라이스는 파일·CSS 를 만들지 않는다.

실행: PYTHONUTF8=1 python tools/build_web.py [--jobs N] [--no-subset]
결과 요약: build/web-summary.json
"""
import argparse
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charset  # noqa: E402
import config  # noqa: E402
import fontutil  # noqa: E402

LOG = fontutil.LOG
REST_CHUNK = 256   # Google 슬라이스 밖 cmap 을 이 크기로 나눠 rest 슬라이스 생성(정적 ≈15 KB, 변수 ≈2–3배)
FONT_FACE_RE = re.compile(r"@font-face\s*\{(.*?)\}", re.S)
UR_RE = re.compile(r"unicode-range:\s*([^;]+);")


def load_slices():
    """google-kr-slices.css → [(index, set(int)), ...] (겹침 제거: 뒤 블록 우선). JSON 으로도 저장."""
    text = config.GOOGLE_SLICES_CSS.read_text(encoding="utf-8")
    raw = []
    for m in FONT_FACE_RE.finditer(text):
        um = UR_RE.search(m.group(1))
        if not um:
            continue
        raw.append(charset.parse_css_unicode_range(um.group(1)))
    seen = set()
    slices = []
    for i in range(len(raw) - 1, -1, -1):
        s = raw[i] - seen
        seen |= s
        slices.append((i, s))
    slices.reverse()
    fontutil.write_json(config.SLICES_JSON, {
        "source": str(config.GOOGLE_SLICES_CSS.relative_to(config.ROOT)).replace("\\", "/"),
        "note": "Google Fonts Noto Sans KR css2 응답의 unicode-range(사실 데이터). 겹침은 뒤 블록에 남김.",
        "count": len(slices),
        "slices": [{"index": i, "count": len(s), "unicode_range": charset.css_unicode_range(s)} for i, s in slices],
    })
    return slices


def to_woff2(src, dest):
    f = TTFont(src)
    f.flavor = "woff2"
    dest.parent.mkdir(parents=True, exist_ok=True)
    f.save(dest)
    f.close()
    return dest.stat().st_size


def _prune_cmap(font, cps):
    """서브세터가 레이아웃 클로저로 끌어온 글립의 cmap 항목(예: ＜ 요청 시 ＞)이 남는다 → unicode-range 밖 항목 제거(글립은 유지).
    spec 05 §3 QA (a) 슬라이스 cmap ⊆ unicode-range, (b) 슬라이스 간 교집합 0."""
    for st in font["cmap"].tables:
        st.cmap = {u: g for u, g in st.cmap.items() if u in cps}


def _slice_one(data, cps, dest):
    import io
    f = TTFont(io.BytesIO(data))
    fontutil.subset_font(f, cps, hinting=config.WOFF2_HINTING)
    _prune_cmap(f, cps)
    f.flavor = "woff2"
    f.save(dest)
    got = set(f.getBestCmap())
    f.close()
    return got


def slice_font(src, stem, slices):
    """워커: 폰트 하나를 슬라이스별 WOFF2 로. 반환 [(index, count, bytes, unicode_range_css, cmap-range 밖 수)]"""
    from fontTools import subset as _subset  # noqa: F401 (워커 프로세스에서 import 보장)
    import io
    src = Path(src)
    data = src.read_bytes()
    cmap = set(TTFont(io.BytesIO(data), lazy=True).getBestCmap())
    covered = set()
    out = []
    for idx, cps in slices:
        cps = cps & cmap
        covered |= cps
        if not cps:
            continue
        dest = config.DIST_WEB_SUBSET / f"{stem}.subset.{idx}.woff2"
        got = _slice_one(data, cps, dest)
        out.append((idx, len(cps), dest.stat().st_size, charset.css_unicode_range(cps), len(got - cps)))
    rest = sorted(cmap - covered - {0x0000, 0x000D})
    # Google 슬라이스에 없는 cmap(KS 기호·괘선·원문자 등) → rest 슬라이스 #124, #125, … (코드포인트 순 REST_CHUNK 개씩)
    for k in range(0, len(rest), REST_CHUNK):
        chunk = set(rest[k:k + REST_CHUNK])
        idx = len(slices) + k // REST_CHUNK
        dest = config.DIST_WEB_SUBSET / f"{stem}.subset.{idx}.woff2"
        got = _slice_one(data, chunk, dest)
        out.append((idx, len(chunk), dest.stat().st_size, charset.css_unicode_range(chunk), len(got - chunk)))
    return stem, out


CSS_HEADER = ("/* {family} {ver} — {what}. SIL OFL 1.1 (see LICENSE)\n"
              "   CDN: {url}/v/{ver}/css/{file}  (relative ../web/ paths below; release rewrites them to {url}/v/{ver}/web/…)\n"
              "   latest: {url}/latest/css/{file} */\n")


def face(family, weight, src_rel, unicode_range=None, variable=False):
    lines = ["@font-face {", f'  font-family: "{family}";', "  font-style: normal;",
             f"  font-weight: {'100 900' if variable else weight};", "  font-display: swap;"]
    if variable:
        lines.append(f'  src: url("{src_rel}") format("woff2") tech("variations"),')
        lines.append(f'       url("{src_rel}") format("woff2-variations"),')
        lines.append(f'       url("{src_rel}") format("woff2");')
    else:
        lines.append(f'  src: url("{src_rel}") format("woff2");')
    if unicode_range:
        lines.append(f"  unicode-range: {unicode_range};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def write_css(sliced, have_variable):
    config.DIST_CSS.mkdir(parents=True, exist_ok=True)
    fam, ver = config.CSS_FAMILY, config.VERSION
    # 1) 정적 전체본
    css = CSS_HEADER.format(family=fam, ver=ver, what="static, full charset", url=config.CSS_VENDOR_URL, file="jennysans.css")
    for wn, wv in config.WEIGHTS:
        css += face(fam, wv, f"../web/JennySans-{wn}.woff2")
    (config.DIST_CSS / "jennysans.css").write_text(css, encoding="utf-8")
    # 2) 변수 전체본
    if have_variable:
        css = CSS_HEADER.format(family=fam, ver=ver, what="variable (wght 100-900), full charset", url=config.CSS_VENDOR_URL, file="jennysans-variable.css")
        css += face(fam, None, "../web/JennySansVariable.woff2", variable=True)
        (config.DIST_CSS / "jennysans-variable.css").write_text(css, encoding="utf-8")
    # 3) 정적 분할본
    css = CSS_HEADER.format(family=fam, ver=ver, what="dynamic subset (unicode-range, Google KR 124 slices + rest)",
                            url=config.CSS_VENDOR_URL, file="jennysans-dynamic-subset.css")
    for wn, wv in config.WEIGHTS:
        for idx, _, _, ur, _ in sliced.get(f"JennySans-{wn}", []):
            css += face(fam, wv, f"../web/subset/JennySans-{wn}.subset.{idx}.woff2", ur)
    (config.DIST_CSS / "jennysans-dynamic-subset.css").write_text(css, encoding="utf-8")
    # 4) 변수 분할본
    if have_variable and "JennySansVariable" in sliced:
        css = CSS_HEADER.format(family=fam, ver=ver, what="variable dynamic subset (unicode-range)", url=config.CSS_VENDOR_URL, file="jennysans-variable-dynamic-subset.css")
        for idx, _, _, ur, _ in sliced["JennySansVariable"]:
            css += face(fam, None, f"../web/subset/JennySansVariable.subset.{idx}.woff2", ur, variable=True)
        (config.DIST_CSS / "jennysans-variable-dynamic-subset.css").write_text(css, encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--no-subset", action="store_true", help="분할본 생략(전체 WOFF2·CSS 만)")
    a = ap.parse_args(argv)
    fontutil.setup_logging("web")
    t0 = time.time()
    config.DIST_WEB.mkdir(parents=True, exist_ok=True)
    config.DIST_WEB_SUBSET.mkdir(parents=True, exist_ok=True)

    inputs = [(config.DIST_STATIC / f"JennySans-{wn}.ttf", f"JennySans-{wn}") for wn, _ in config.WEIGHTS]
    vf = config.DIST_VARIABLE / "JennySansVariable.ttf"
    have_variable = vf.exists()
    if have_variable:
        inputs.append((vf, "JennySansVariable"))
    else:
        LOG.warning("변수 폰트 없음(%s) — 변수 WOFF2/CSS 생략", vf)
    missing = [p for p, _ in inputs if not p.exists()]
    if missing:
        raise SystemExit(f"입력 없음: {missing} — 먼저 build static/variable")

    full = {}
    for p, stem in inputs:
        dest = config.DIST_WEB / f"{stem}.woff2"
        full[stem] = to_woff2(p, dest)
        LOG.info("WOFF2 %s %d bytes", dest.name, full[stem])

    sliced = {}
    if not a.no_subset:
        slices = load_slices()
        LOG.info("슬라이스 %d개 로드(%s), %d 워커로 분할 시작", len(slices), config.GOOGLE_SLICES_CSS.name, a.jobs)
        for old in config.DIST_WEB_SUBSET.glob("*.woff2"):
            old.unlink()
        with ProcessPoolExecutor(max_workers=a.jobs) as ex:
            futs = [ex.submit(slice_font, str(p), stem, slices) for p, stem in inputs]
            for fut in as_completed(futs):
                stem, out = fut.result()
                sliced[stem] = sorted(out)
                tot = sum(b for _, _, b, _, _ in out)
                extra = sum(e for _, _, _, _, e in out)
                LOG.info("분할 %s: %d 슬라이스, 합계 %d bytes, 최대 %d, unicode-range 밖 cmap %d",
                         stem, len(out), tot, max(b for _, _, b, _, _ in out), extra)
    write_css(sliced, have_variable)
    summary = dict(full=full, sliced={k: [dict(index=i, count=c, bytes=b, extra=e) for i, c, b, _, e in v] for k, v in sliced.items()},
                   css=sorted(p.name for p in config.DIST_CSS.glob("*.css")), seconds=round(time.time() - t0, 1))
    fontutil.write_json(config.BUILD / "web-summary.json", summary)
    LOG.info("웹 빌드 완료 %.0fs", summary["seconds"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
