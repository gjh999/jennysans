# -*- coding: utf-8 -*-
"""
tools/first_paint.py — 분할 CSS 로 페이지를 열었을 때 **실제로 내려받는 웹폰트 바이트**를 재는 스크립트 (font-site 소유)

홈페이지의 "첫 화면 ○○ KB" 문구를 추측이 아니라 실측으로 쓰기 위한 도구.
`site/preview.py` 로 로컬 서버를 띄우고, 시나리오별 임시 HTML 을 열어 `.woff2` 응답의 Content-Length 를 합산한다.

    PYTHONUTF8=1 python tools/first_paint.py
    PYTHONUTF8=1 python tools/first_paint.py --url https://font.jennysoft.co.kr   # 배포 후 실서버

출력은 `site/assets/first-paint.json` 에도 저장되며, `tools/package.py` 가 `{{PAINT:…}}` 로 페이지에 넣는다.
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
sys.path.insert(0, str(ROOT / "site"))
import config  # noqa: E402

OUT = ROOT / "site" / "assets" / "first-paint.json"

BODY = {
    "latin": ('라틴 전용 페이지 · 한 웨이트', 'font-weight:400',
              '<p lang="es">Sphinx of black quartz, judge my vow. ¿Qué tal, señor? 0123456789</p>'),
    "ko_short": ('한국어 한 문장 · 한 웨이트', 'font-weight:400',
                 '<p>제니산스는 범용 한글·라틴 고딕입니다.</p>'),
    "ko_para": ('한국어 소개문 한 문단 · 한 웨이트', 'font-weight:400',
                '<p>제니소프트의 웹·앱·게임·문서에서 공통으로 쓰는 범용 한글·라틴 고딕입니다. 현대 한글 11,172자 전부를 담았습니다.</p>'),
    "ko_two_weights": ('한국어 두 문단 + 제목 · 두 웨이트(400·700)', 'font-weight:400',
                       '<h1 style="font-weight:700">제니산스 JennySans</h1>'
                       '<p>제니소프트의 웹·앱·게임·문서에서 공통으로 쓰는 범용 한글·라틴 고딕입니다.</p>'
                       '<p>현대 한글 11,172자 전부와 스페인어를 포함한 라틴을 담았습니다.</p>'),
}


def measure(base: str, version: str, tmp_name: str = "_first_paint_tmp.html") -> dict:
    from playwright.sync_api import sync_playwright

    tmp = ROOT / "site" / tmp_name
    results: dict[str, dict] = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for key, (label, style, body) in BODY.items():
                tmp.write_text(
                    '<!doctype html><meta charset="utf-8">'
                    f'<link rel="stylesheet" href="/v/{version}/css/jennysans-dynamic-subset.css">'
                    f'<style>body{{font-family:"JennySans",serif;font-size:18px;{style}}}</style>' + body,
                    encoding="utf-8")
                page = browser.new_page()
                got: list[int] = []
                page.on("response", lambda r: got.append(int(r.headers.get("content-length") or 0))
                        if ".woff2" in r.url else None)
                page.goto(f"{base}/{tmp_name}?{key}", wait_until="networkidle")
                page.wait_for_timeout(900)
                total = sum(got)
                results[key] = {"label": label, "requests": len(got), "bytes": total,
                                "kb": round(total / 1024, 1)}
                page.close()
            browser.close()
    finally:
        tmp.unlink(missing_ok=True)
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=None, help="실서버 URL(없으면 site/preview.py 를 띄움)")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)

    srv = None
    base = args.url.rstrip("/") if args.url else None
    if base is None:
        import preview

        srv, base = preview.serve_background(0, True)
    try:
        res = measure(base, config.VERSION)
    finally:
        if srv is not None:
            srv.shutdown()

    data = {"generated": _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9))).isoformat(timespec="seconds"),
            "version": config.VERSION, "base": base, "css": "jennysans-dynamic-subset.css", "cases": res}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for k, v in res.items():
        print(f"  {v['label']:<34} 조각 {v['requests']:>2}개 · {v['bytes']:>8,} B ({v['kb']:>6.1f} KB)")
    print(f"== {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
