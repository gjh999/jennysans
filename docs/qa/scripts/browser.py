# -*- coding: utf-8 -*-
"""
게이트 7 (브라우저) + spec 05 §4·§7-3 — Playwright Chromium 실측.
1) site/test.html 4 모드(static·variable·subset·variable-subset, size=20): document.fonts.ready 후 상태줄·9 웨이트 check()·폰트 요청 수/바이트·콘솔 오류 →
   스크린샷 docs/qa/shots/browser-<mode>.png (전체 페이지)
2) docs/qa/pages/page-{A,B,C}.html × CSS(정적·변수·분할·변수분할): 폰트 요청 수·전송 바이트(응답 본문 길이) → spec 05 §4 목표와 비교
서버: 저장소 루트에서 python -m http.server 8765 를 자체 기동(이미 떠 있으면 재사용).
실행: PYTHONUTF8=1 python docs/qa/scripts/browser.py
"""
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

PORT = 8765
BASE = f"http://localhost:{PORT}"
MODES = ["static", "variable", "subset", "variable-subset"]
CSS = {"static": "jennysans.css", "variable": "jennysans-variable.css", "subset": "jennysans-dynamic-subset.css", "variable-subset": "jennysans-variable-dynamic-subset.css"}
TARGETS = {  # spec 05 §4 (bytes, requests) — None = 참고
    ("A", "subset"): (70 * 1024, 2), ("B", "subset"): (300 * 1024, 30), ("C", "subset"): (400 * 1024, None),
}


def port_open():
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def start_server():
    if port_open():
        return None
    p = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"], cwd=str(Q.ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        if port_open():
            break
        time.sleep(0.1)
    return p


def visit(pw_page, url, wait_ms=2500):
    fonts = []
    errors = []
    pw_page.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    pw_page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    pw_page.on("requestfailed", lambda r: errors.append(f"requestfailed: {r.url} {r.failure}"))

    def on_resp(resp):
        if resp.request.resource_type == "font" or resp.url.endswith(".woff2") or resp.url.endswith(".ttf"):
            try:
                size = len(resp.body())
            except Exception:
                size = int(resp.headers.get("content-length", 0) or 0)
            fonts.append((resp.url.rsplit("/", 1)[-1], resp.status, size))
    pw_page.on("response", on_resp)
    pw_page.goto(url, wait_until="load")
    pw_page.evaluate("document.fonts.ready")
    pw_page.wait_for_timeout(wait_ms)
    pw_page.evaluate("document.fonts.ready")
    pw_page.wait_for_timeout(500)
    return fonts, errors


def main():
    rep = Q.Report("브라우저 실측 (Playwright Chromium) — test.html 4 모드 + spec 05 §4 페이지 A/B/C")
    srv = start_server()
    rep.info("server", f"http.server {PORT} {'기동' if srv else '기존 재사용'} (root {Q.ROOT})")
    rows = []
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch()
            rep.info("env", f"Chromium {br.version}")
            for mode in MODES:
                ctx = br.new_context(viewport={"width": 1500, "height": 1000}, device_scale_factor=1)
                page = ctx.new_page()
                fonts, errors = visit(page, f"{BASE}/site/test.html?mode={mode}&size=20", wait_ms=4000)
                status = page.inner_text("#status")
                checks = page.evaluate("""() => [100,200,300,400,500,600,700,800,900].map(w => [w, document.fonts.check(w + ' 16px "JennySans"')])""")
                faces = page.evaluate("""() => { let n=0, l=0; document.fonts.forEach(f => { if (/JennySans/i.test(f.family)) { n++; if (f.status==='loaded') l++; } }); return [n, l]; }""")
                # 폴백 감지: 한글 칸 폭 — 세리프 폴백이면 계산된 폰트가 다름. computed font-family 는 항상 JennySans 이므로 check() 결과로 판단
                shot = Q.SHOTS / f"browser-{mode}.png"
                page.screenshot(path=str(shot), full_page=True)
                total = sum(s for _, _, s in fonts)
                bad = [c for c in checks if not c[1]]
                ok = faces[1] > 0 and not bad and not [e for e in errors if e.startswith(("error", "pageerror", "requestfailed"))]
                (rep.passed if ok else rep.fail)("test.html", f"mode={mode}: faces {faces[0]}/loaded {faces[1]}, check() 실패 {bad}, 폰트 요청 {len(fonts)}개 {total:,} B, 콘솔 오류 {len(errors)} {errors[:3]} → {shot.relative_to(Q.ROOT)}")
                rep.info("test.html", f"mode={mode} 상태줄: {status}")
                rows.append(("test.html", mode, len(fonts), f"{total:,}", "-", "-"))
                ctx.close()
            # spec 05 §4 페이지
            for pg in ("A", "B", "C"):
                for mode in MODES:
                    ctx = br.new_context(viewport={"width": 1200, "height": 900})
                    page = ctx.new_page()
                    fonts, errors = visit(page, f"{BASE}/docs/qa/pages/page-{pg}.html?mode={mode}", wait_ms=3000)
                    total = sum(s for _, _, s in fonts)
                    tgt = TARGETS.get((pg, mode))
                    verdict = "-"
                    if tgt:
                        ok = total <= tgt[0] and (tgt[1] is None or len(fonts) <= tgt[1])
                        verdict = "PASS" if ok else "FAIL"
                        (rep.passed if ok else rep.warn)("page", f"page-{pg} {mode}: 요청 {len(fonts)}, {total:,} B (목표 ≤{tgt[0] // 1024} KB{', ≤' + str(tgt[1]) + ' 요청' if tgt[1] else ''}) 오류 {len(errors)}")
                    else:
                        rep.info("page", f"page-{pg} {mode}: 요청 {len(fonts)}, {total:,} B, 오류 {len(errors)} {errors[:2]}")
                    if not fonts:
                        rep.fail("page", f"page-{pg} {mode}: 폰트 요청 0 — CSS 미적용 {errors[:3]}")
                    rep.info("page", f"page-{pg} {mode} 파일: {[(n, s) for n, _, s in fonts][:40]}")
                    if pg == "B" and mode == "subset":
                        page.screenshot(path=str(Q.SHOTS / "browser-pageB-subset.png"), full_page=True)
                    rows.append((f"page-{pg}", mode, len(fonts), f"{total:,}", f"≤{tgt[0] // 1024} KB" if tgt else "-", verdict))
                    ctx.close()
            br.close()
    finally:
        if srv:
            srv.terminate()
    rep.md("## 폰트 요청·전송량 (Playwright response body 합산, 로컬 http.server)\n\n" + Q.table(["페이지", "CSS 모드", "폰트 요청", "bytes", "목표", "판정"], rows))
    rep.write("browser")


if __name__ == "__main__":
    main()
