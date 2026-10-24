# -*- coding: utf-8 -*-
"""
site/check_site.py — 홈페이지 실브라우저 검증 + 스크린샷 (Playwright chromium; font-site 소유)

    PYTHONUTF8=1 python site/check_site.py                       # 미리보기 서버를 스스로 띄워 검사
    PYTHONUTF8=1 python site/check_site.py --shots docs/qa/shots  # 스크린샷 저장 위치(기본값과 동일)
    PYTHONUTF8=1 python site/check_site.py --url https://font.jennysoft.co.kr   # 배포 후 실서버 검사

검사 항목 (하나라도 실패하면 종료 코드 1)
  1. index.html 에 치환되지 않은 {{…}} 가 없다
  2. 콘솔 error 0 · pageerror 0 · 실패/4xx/5xx 요청 0 (데스크톱·모바일 각각)
  3. document.fonts: "JennySans" 조각이 실제로 loaded 이고, 폴백(serif)과 렌더 폭이 달라 웹폰트가 적용됐다
     + 변수 폰트("JennySans VF") 로드, 타입 테스터 굵기 900 반영
  4. 다운로드 링크 4개(/download/*.zip) 가 200 이고 Content-Length 가 index.json 의 bytes 와 같다 + SHA256SUMS.txt 200
  5. 모바일(390×844)에서 가로 스크롤이 없다
  6. 탭 클릭 시 패널 전환
  7. 전체 페이지 스크린샷: docs/qa/shots/site-desktop.png (1280×900) · site-mobile.png (390×844, DPR 2)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))

FALLBACK_PROBE = "제니산스 JennySans ¿Qué tal, señor? 0123456789"
SYNTH_PROBE = "⅔∼≒◈"   # 원본 두 폰트에 없어 합성한 required 4자(U+2154 U+223C U+2252 U+25C8) — 5차 빌드부터 포함


def fmt_row(name: str, ok: bool, detail: str) -> str:
    return f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=None, help="검사할 사이트 루트 URL (없으면 preview 서버를 띄움)")
    ap.add_argument("--shots", default=str(ROOT / "docs" / "qa" / "shots"))
    ap.add_argument("--timeout", type=int, default=30000)
    args = ap.parse_args(argv)

    from playwright.sync_api import sync_playwright

    shots = Path(args.shots)
    shots.mkdir(parents=True, exist_ok=True)
    (shots / ".gitkeep").touch(exist_ok=True)

    srv = None
    base = args.url.rstrip("/") if args.url else None
    if base is None:
        import preview  # site/preview.py
        srv, base = preview.serve_background(port=0, quiet=True)

    results: list[tuple[str, bool, str]] = []
    try:
        html = ROOT / "site" / "index.html"
        if args.url is None:
            left_all: list[str] = []
            names = []
            for p in (html, ROOT / "site" / "glyphs.html"):
                if not p.exists():
                    left_all.append(f"{p.name} 없음")
                    continue
                left_all += [f"{p.name}:{m}" for m in re.findall(r"\{\{[^{}]+\}\}", p.read_text(encoding="utf-8"))]
                names.append(p.name)
            results.append(("1. 미치환 자리표시자", not left_all,
                            f"{' · '.join(names)} 0건" if not left_all else f"{len(left_all)}건 " + ", ".join(left_all[:5])))

        with sync_playwright() as p:
            browser = p.chromium.launch()

            def run(view: dict, shot_name: str, label: str) -> dict:
                ctx = browser.new_context(**view)
                page = ctx.new_page()
                console_errors: list[str] = []
                page_errors: list[str] = []
                bad_requests: list[str] = []
                page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
                page.on("pageerror", lambda e: page_errors.append(str(e)))
                page.on("requestfailed", lambda r: bad_requests.append(f"FAILED {r.url} ({r.failure})"))
                page.on("response", lambda r: bad_requests.append(f"{r.status} {r.url}") if r.status >= 400 else None)
                page.goto(base + "/", wait_until="networkidle", timeout=args.timeout)
                page.evaluate("document.fonts.ready")
                # 분할 CSS 는 화면에 글자가 그려진 뒤 조각이 순차 로드되므로 잠깐 더 기다린다
                page.wait_for_timeout(800)
                page.evaluate("document.fonts.ready")

                info = page.evaluate(
                    """([probe, synth]) => {
                      const out = {};
                      let loaded = 0, vf = 0, total = 0;
                      document.fonts.forEach(f => { const fam = f.family.replace(/["']/g, '');
                        if (fam === 'JennySans') { total++; if (f.status === 'loaded') loaded++; }
                        if (fam === 'JennySans VF' && f.status === 'loaded') vf++; });
                      out.faces_total = total; out.faces_loaded = loaded; out.vf_loaded = vf;
                      out.check400 = document.fonts.check('400 16px "JennySans"');
                      out.check800 = document.fonts.check('800 16px "JennySans"');
                      out.checkVF = document.fonts.check('650 16px "JennySans VF"');
                      // 폴백(serif) 대비 렌더 폭 비교 — 같으면 웹폰트가 적용되지 않은 것
                      const mk = (ff, text) => { const s = document.createElement('span'); s.textContent = text || probe;
                        s.style.cssText = 'position:absolute;left:-9999px;top:0;font-size:40px;white-space:nowrap;font-family:' + ff;
                        document.body.appendChild(s); const w = s.getBoundingClientRect().width; s.remove(); return w; };
                      out.width_jenny = mk('"JennySans", serif');
                      out.width_serif = mk('serif');
                      out.width_vf = mk('"JennySans VF", serif');
                      // 합성 4자: JennySans 조각이 로드된 뒤 폭을 재야 하므로 document.fonts.ready 이후 한 번 더 잰다(아래 synth_* 갱신)
                      out.synth_jenny = mk('"JennySans", serif', synth);
                      out.synth_serif = mk('serif', synth);
                      out.synth_check = document.fonts.check('400 16px "JennySans"', synth);
                      out.hero_family = getComputedStyle(document.querySelector('.hero-ko')).fontFamily;
                      out.scrollWidth = document.documentElement.scrollWidth;
                      out.innerWidth = window.innerWidth;
                      out.title = document.title;
                      out.font_status = (document.getElementById('font-status') || {}).textContent || '';
                      out.download_links = Array.from(document.querySelectorAll('a[href^="/download/"]')).map(a => a.getAttribute('href'));
                      // SEO 메타·JSON-LD (팀장 추가분) — 렌더 후에도 살아 있고 치환이 끝났는지
                      const meta = (sel, attr) => { const el = document.querySelector(sel); return el ? el.getAttribute(attr || 'content') : null; };
                      out.seo = {
                        canonical: meta('link[rel="canonical"]', 'href'),
                        robots: meta('meta[name="robots"]'),
                        keywords: !!meta('meta[name="keywords"]'),
                        og_title: meta('meta[property="og:title"]'),
                        og_url: meta('meta[property="og:url"]'),
                        og_image: meta('meta[property="og:image"]'),
                        og_desc: meta('meta[property="og:description"]'),
                        tw_card: meta('meta[name="twitter:card"]'),
                        tw_image: meta('meta[name="twitter:image"]'),
                        hreflang: document.querySelectorAll('link[rel="alternate"][hreflang]').length,
                        icons: Array.from(document.querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"]')).map(l => l.getAttribute('href')),
                      };
                      const ld = document.querySelector('script[type="application/ld+json"]');
                      out.seo.ld_raw = ld ? ld.textContent : null;
                      try {
                        const j = JSON.parse(ld.textContent);
                        const g = j['@graph'] || [j];
                        out.seo.ld_types = g.map(n => n['@type']);
                        const app = g.find(n => n['@type'] === 'SoftwareApplication') || {};
                        out.seo.ld_version = app.softwareVersion || null;
                        out.seo.ld_date = app.datePublished || null;
                        out.seo.ld_download = app.downloadUrl || null;
                        out.seo.ld_desc = app.description || null;
                        out.seo.ld_ok = true;
                      } catch (e) { out.seo.ld_ok = false; out.seo.ld_error = String(e); }
                      return out;
                    }""",
                    [FALLBACK_PROBE, SYNTH_PROBE],
                )
                # 합성 4자가 든 조각은 위 측정으로 처음 요청될 수 있으므로 로드를 기다렸다가 다시 잰다
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(600)
                info.update(page.evaluate(
                    """(synth) => {
                      const mk = (ff) => { const s = document.createElement('span'); s.textContent = synth;
                        s.style.cssText = 'position:absolute;left:-9999px;top:0;font-size:40px;white-space:nowrap;font-family:' + ff;
                        document.body.appendChild(s); const w = s.getBoundingClientRect().width; s.remove(); return w; };
                      return { synth_jenny: mk('"JennySans", serif'), synth_serif: mk('serif'),
                               synth_check: document.fonts.check('400 16px "JennySans"', synth) };
                    }""",
                    SYNTH_PROBE,
                ))
                # 타입 테스터 굵기 900 반영
                page.evaluate("""() => { const r = document.getElementById('ctl-weight'); r.value = '900'; r.dispatchEvent(new Event('input', {bubbles:true})); }""")
                page.wait_for_timeout(150)
                info["tester_weight"] = page.evaluate("getComputedStyle(document.getElementById('tester-text')).fontWeight")
                info["tester_out"] = page.evaluate("document.getElementById('out-weight').textContent")
                page.evaluate("""() => { const r = document.getElementById('ctl-weight'); r.value = '400'; r.dispatchEvent(new Event('input', {bubbles:true})); }""")
                # 탭 전환
                page.click("#tab-web")
                info["tab_web_visible"] = page.evaluate("!document.getElementById('panel-web').hidden && document.getElementById('panel-win').hidden")
                page.click("#tab-win")
                page.wait_for_timeout(200)
                page.screenshot(path=str(shots / shot_name), full_page=True)
                info["console_errors"] = console_errors
                info["page_errors"] = page_errors
                info["bad_requests"] = bad_requests
                info["label"] = label
                ctx.close()
                return info

            desk = run({"viewport": {"width": 1280, "height": 900}, "device_scale_factor": 1, "locale": "ko-KR"}, "site-desktop.png", "desktop 1280×900")
            mob = run({"viewport": {"width": 390, "height": 844}, "device_scale_factor": 2, "is_mobile": True, "has_touch": True, "locale": "ko-KR"}, "site-mobile.png", "mobile 390×844")

            for info in (desk, mob):
                lab = info["label"]
                errs = info["console_errors"] + info["page_errors"] + info["bad_requests"]
                results.append((f"2. 콘솔·요청 오류 ({lab})", not errs, "0건" if not errs else "; ".join(errs[:6])))
                font_ok = (info["faces_loaded"] > 0 and info["check400"] and info["check800"]
                           and abs(info["width_jenny"] - info["width_serif"]) > 1)
                results.append((f"3. JennySans 렌더 ({lab})", font_ok,
                                f"faces loaded {info['faces_loaded']}/{info['faces_total']} · check 400 {info['check400']} / 800 {info['check800']} · 폭 JennySans {info['width_jenny']:.0f}px vs serif {info['width_serif']:.0f}px · 상태줄 \"{info['font_status']}\""))
                vf_ok = info["vf_loaded"] > 0 and info["checkVF"] and abs(info["width_vf"] - info["width_serif"]) > 1 and str(info["tester_weight"]) == "900"
                results.append((f"3b. 변수 폰트·테스터 ({lab})", vf_ok,
                                f"VF loaded {info['vf_loaded']} · check {info['checkVF']} · 폭 {info['width_vf']:.0f}px · 굵기 900 → computed {info['tester_weight']} ({info['tester_out']})"))
                synth_ok = bool(info["synth_check"]) and abs(info["synth_jenny"] - info["synth_serif"]) > 1
                results.append((f"3c. 합성 4자 {SYNTH_PROBE} 렌더 ({lab})", synth_ok,
                                f"check {info['synth_check']} · 폭 JennySans {info['synth_jenny']:.0f}px vs serif {info['synth_serif']:.0f}px"))
                results.append((f"6. 탭 전환 ({lab})", bool(info["tab_web_visible"]), "웹 탭 클릭 → panel-web 표시, panel-win 숨김" if info["tab_web_visible"] else "전환 안 됨"))
            results.append(("5. 모바일 가로 스크롤 없음", mob["scrollWidth"] <= mob["innerWidth"], f"scrollWidth {mob['scrollWidth']} ≤ innerWidth {mob['innerWidth']}"))

            # 7. SEO 메타·JSON-LD (팀장 추가분이 렌더 뒤에도 살아 있고 치환이 끝났는지)
            seo = desk["seo"]
            ld_placeholder = "{{" in (seo.get("ld_raw") or "")
            seo_ok = (bool(seo["canonical"]) and bool(seo["robots"]) and seo["keywords"]
                      and bool(seo["og_title"]) and bool(seo["og_url"]) and bool(seo["og_image"])
                      and seo["tw_card"] == "summary_large_image" and bool(seo["tw_image"])
                      and seo["hreflang"] >= 2 and len(seo["icons"]) >= 3
                      and seo["ld_ok"] and not ld_placeholder
                      and "SoftwareApplication" in (seo.get("ld_types") or [])
                      and seo.get("ld_version") and seo.get("ld_date") and seo.get("ld_download")
                      and "{{" not in (seo.get("ld_desc") or "{{"))
            results.append(("7. SEO 메타·JSON-LD", seo_ok,
                            f"canonical {seo['canonical']} · robots \"{seo['robots']}\" · og:image {seo['og_image']} · twitter {seo['tw_card']} · hreflang {seo['hreflang']} · icon 링크 {len(seo['icons'])} · JSON-LD {seo.get('ld_types')} version {seo.get('ld_version')} date {seo.get('ld_date')} (치환 잔여 {'있음' if ld_placeholder else '없음'})"))

            # 4. 다운로드 링크
            ctx = browser.new_context()
            idx = ctx.request.get(base + "/download/index.json")
            index = idx.json() if idx.ok else {}
            links = sorted(set(desk["download_links"]))
            zips = [l for l in links if l.endswith(".zip")]
            details = []
            ok_all = idx.ok and len(zips) == 4
            for href in zips:
                r = ctx.request.head(base + href)
                cl = r.headers.get("content-length")
                fname = href.rsplit("/", 1)[-1]
                expect = next((p["bytes"] for p in index.get("packages", {}).values() if p["file"] == fname), None)
                good = r.status == 200 and expect is not None and str(expect) == str(cl)
                ok_all = ok_all and good
                details.append(f"{fname} {r.status} {cl}B{'' if good else ' ≠ ' + str(expect)}")
            r2 = ctx.request.head(base + "/download/SHA256SUMS.txt")
            ok_all = ok_all and r2.status == 200
            details.append(f"SHA256SUMS.txt {r2.status}")
            results.append(("4. 다운로드 링크 4개 + 체크섬", ok_all, " · ".join(details)))

            # 9. 글자맵 페이지 (별도 페이지): 로드·콘솔 0·폰트 적용·블록 전환·검색·상세
            gp = ctx.new_page()
            g_console: list[str] = []
            g_bad: list[str] = []
            gp.on("console", lambda m: g_console.append(m.text) if m.type == "error" else None)
            gp.on("pageerror", lambda e: g_console.append(str(e)))
            gp.on("requestfailed", lambda r: g_bad.append(f"FAILED {r.url}"))
            gp.on("response", lambda r: g_bad.append(f"{r.status} {r.url}") if r.status >= 400 else None)
            gp.set_viewport_size({"width": 1280, "height": 900})
            gp.goto(base + "/glyphs.html", wait_until="networkidle", timeout=args.timeout)
            gp.wait_for_selector('[data-glyphmap="ready"]', timeout=args.timeout)
            gp.evaluate("document.fonts.ready")
            gp.wait_for_timeout(800)
            g1 = gp.evaluate(
                """() => ({
                     blocks: document.querySelectorAll('#g-blocks button').length,
                     title: document.getElementById('g-title').textContent,
                     cells: document.querySelectorAll('#g-grid .glyph-cell').length,
                     groups: document.querySelectorAll('#g-groups button').length,
                     vf: document.fonts.check('400 40px "JennySans VF"'),
                   })""")
            # 한글 → 다른 블록(단위) 전환
            t0 = time.time()
            gp.click('#g-blocks button[data-block="units"]')
            gp.wait_for_timeout(400)
            g2 = gp.evaluate("""() => ({ title: document.getElementById('g-title').textContent,
                                          cells: document.querySelectorAll('#g-grid .glyph-cell').length })""")
            # 검색 → 상세 패널
            gp.fill("#g-search", "U+AC00")
            gp.press("#g-search", "Enter")
            gp.wait_for_timeout(900)
            g3 = gp.evaluate(
                """() => ({ open: !document.getElementById('g-detail').hidden,
                            cp: document.getElementById('g-detail-cp').textContent,
                            name: document.getElementById('g-detail-name').textContent,
                            block: document.getElementById('g-detail-block').textContent,
                            title: document.getElementById('g-title').textContent,
                            cells: document.querySelectorAll('#g-grid .glyph-cell').length })""")
            # 글립이 폴백이 아닌지: 격자 셀 하나의 렌더 폭을 serif 와 비교
            g_font = gp.evaluate(
                """() => { const mk = (ff) => { const s = document.createElement('span'); s.textContent = '가나다ABC';
                     s.style.cssText = 'position:absolute;left:-9999px;font-size:40px;white-space:nowrap;font-family:' + ff;
                     document.body.appendChild(s); const w = s.getBoundingClientRect().width; s.remove(); return w; };
                     return { vf: mk('"JennySans VF", serif'), serif: mk('serif') }; }""")
            gp.evaluate("() => { document.getElementById('g-detail').hidden = true; }")
            gp.click('#g-blocks button[data-block="hangul"]')
            gp.wait_for_timeout(600)
            gp.evaluate("window.scrollTo(0, 0)")
            gp.wait_for_timeout(200)
            gp.screenshot(path=str(shots / "site-glyphs.png"), full_page=False)
            elapsed = time.time() - t0
            gerrs = g_console + g_bad
            results.append(("9. 글자맵 로드·콘솔 (glyphs.html)", not gerrs and g1["blocks"] >= 10,
                            f"블록 버튼 {g1['blocks']} · 첫 화면 \"{g1['title']}\" 초성 탭 {g1['groups']} · 셀 {g1['cells']} · 오류 {len(gerrs)}건"
                            + ("" if not gerrs else " → " + "; ".join(gerrs[:4]))))
            results.append(("9b. 글자맵 폰트 적용 (glyphs.html)", bool(g1["vf"]) and abs(g_font["vf"] - g_font["serif"]) > 1,
                            f"check VF {g1['vf']} · 폭 JennySans VF {g_font['vf']:.0f}px vs serif {g_font['serif']:.0f}px"))
            results.append(("9c. 글자맵 블록 전환·검색·상세", g2["title"] == "단위" and g2["cells"] > 0 and g3["open"]
                            and "U+AC00" in g3["cp"] and "GA" in g3["name"],
                            f"단위 블록 {g2['cells']}자 → 검색 U+AC00 → {g3['title']} / {g3['cp']} / {g3['name']} / {g3['block']} ({elapsed:.1f}s)"))
            gp.close()

            # 8. SEO 정적 파일 (파비콘·og 이미지·robots·sitemap·소유확인) 200 인지
            seo_files = ["/robots.txt", "/sitemap.xml", "/favicon.ico", "/assets/og-image.png",
                         "/assets/icon-512.png", "/assets/icon-192.png", "/assets/apple-touch-icon.png",
                         "/assets/favicon-32.png", "/google85364fe7cc780e8d.html",
                         "/assets/glyphmap.json", "/assets/languages.json", "/assets/glyphs.js"]
            seo_files += [h for h in (desk["seo"]["icons"] or []) if h and h.startswith("/") and h not in seo_files]
            f_ok, f_detail = True, []
            for path in seo_files:
                r = ctx.request.get(base + path)
                good = r.status == 200 and len(r.body()) > 0
                f_ok = f_ok and good
                f_detail.append(f"{path.rsplit('/', 1)[-1]} {r.status}/{len(r.body())}B" if not good else f"{path.rsplit('/', 1)[-1]} {len(r.body())}B")
            results.append(("8. SEO 정적 파일 200", f_ok, " · ".join(f_detail)))
            ctx.close()
            browser.close()
    finally:
        if srv is not None:
            srv.shutdown()

    print(f"| 검사 | 결과 | 상세 |\n|---|---|---|")
    for name, ok, detail in results:
        print(fmt_row(name, ok, detail))
    fails = [r for r in results if not r[1]]
    print(f"\n스크린샷: {shots / 'site-desktop.png'} · {shots / 'site-mobile.png'}")
    print(f"결과: {'ALL PASS' if not fails else str(len(fails)) + ' FAIL'} ({time.strftime('%Y-%m-%d %H:%M:%S')}, base {base})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
