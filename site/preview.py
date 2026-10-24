# -*- coding: utf-8 -*-
"""
site/preview.py — JennySans 홈페이지 로컬 미리보기 (배포 경로 규약을 그대로 흉내낸다; font-site 소유)

    PYTHONUTF8=1 python site/preview.py               # http://127.0.0.1:8765/
    PYTHONUTF8=1 python site/preview.py --port 9000 --open

경로 매핑 (서버 /var/www/font 와 동일한 URL 구조, deploy/README.md)
    /                → site/                       (index.html, test.html, assets/)
    /v/<ver>/…       → dist/…                      (static/ variable/ web/ css/)
    /latest/…        → dist/…                      (서버에서는 latest -> v/<ver> 심링크)
    /dist/…          → dist/…                      (test.html 의 ../dist/ 상대경로용; 서버에서는 dist -> latest 심링크)
    /download/…      → dist/packages/…             (tools/package.py 산출 zip + index.json + SHA256SUMS.txt)
    /v/<ver>/LICENSE 등 문서 → 저장소 루트의 LICENSE·THIRD-PARTY-NOTICES.md·README.md·CHANGELOG.md
헤더: Access-Control-Allow-Origin: * · Cache-Control: no-cache · MIME font/woff2, font/ttf, text/css;charset=utf-8
"""
from __future__ import annotations

import argparse
import http.server
import os
import posixpath
import sys
import threading
import urllib.parse
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DIST = ROOT / "dist"
PKG = DIST / "packages"
ROOT_DOCS = {"LICENSE": "LICENSE", "LICENSE.txt": "LICENSE", "THIRD-PARTY-NOTICES.md": "THIRD-PARTY-NOTICES.md",
             "README.md": "README.md", "CHANGELOG.md": "CHANGELOG.md"}
MIME = {
    ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".otf": "font/otf",
    ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".html": "text/html; charset=utf-8",
    ".md": "text/markdown; charset=utf-8", ".txt": "text/plain; charset=utf-8", ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml", ".zip": "application/zip", ".png": "image/png",
    ".ico": "image/x-icon", ".xml": "application/xml; charset=utf-8", ".webmanifest": "application/manifest+json",
}


class Handler(http.server.SimpleHTTPRequestHandler):
    quiet = False

    def translate_path(self, path: str) -> str:  # noqa: N802
        path = urllib.parse.unquote(urllib.parse.urlsplit(path).path)
        path = posixpath.normpath(path)
        parts = [p for p in path.split("/") if p and p not in (".", "..")]
        if parts and parts[0] in ("v", "latest", "dist"):
            rest = parts[2:] if parts[0] == "v" else parts[1:]
            if len(rest) == 1 and rest[0] in ROOT_DOCS:
                return str(ROOT / ROOT_DOCS[rest[0]])
            base = DIST.joinpath(*rest) if rest else DIST
            return str(base)
        if parts and parts[0] == "download":
            return str(PKG.joinpath(*parts[1:]) if len(parts) > 1 else PKG)
        if len(parts) == 1 and parts[0] in ROOT_DOCS:
            return str(ROOT / ROOT_DOCS[parts[0]])
        return str(SITE.joinpath(*parts) if parts else SITE)

    def guess_type(self, path: str) -> str:  # noqa: N802
        ext = os.path.splitext(path)[1].lower()
        if ext in MIME:
            return MIME[ext]
        if os.path.basename(path) == "LICENSE":
            return "text/plain; charset=utf-8"
        return super().guess_type(path)

    def end_headers(self) -> None:  # noqa: N802
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        if self.path.startswith("/download/") and self.path.endswith(".zip"):
            self.send_header("Content-Disposition", f'attachment; filename="{os.path.basename(self.path)}"')
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:  # noqa: N802
        if not self.quiet:
            super().log_message(fmt, *args)


class Server(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address) -> None:  # noqa: N802
        # 브라우저가 폰트 요청을 중간에 끊는 것(ConnectionAborted/Reset)은 정상 — 트레이스백을 찍지 않는다
        exc = sys.exc_info()[1]
        if isinstance(exc, (ConnectionAbortedError, ConnectionResetError, BrokenPipeError)):
            return
        super().handle_error(request, client_address)


def make_server(port: int = 8765, host: str = "127.0.0.1", quiet: bool = False) -> Server:
    Handler.quiet = quiet
    return Server((host, port), Handler)


def serve_background(port: int = 0, quiet: bool = True) -> tuple[http.server.ThreadingHTTPServer, str]:
    """검증 스크립트용: 백그라운드 스레드로 띄우고 (server, base_url) 반환. port 0 = 빈 포트."""
    srv = make_server(port, quiet=quiet)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="JennySans 홈페이지 로컬 미리보기")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--open", action="store_true", help="브라우저 열기")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    if not (SITE / "index.html").exists():
        print("!! site/index.html 이 없다 — 먼저 `PYTHONUTF8=1 python tools/package.py --render-site`", file=sys.stderr)
    if not PKG.exists():
        print("!! dist/packages/ 가 없다 — 다운로드 링크가 404 가 된다. `python tools/package.py`", file=sys.stderr)
    srv = make_server(args.port, args.host, args.quiet)
    url = f"http://{args.host}:{args.port}/"
    print(f"== JennySans preview: {url}   (/v/<ver>/ → dist/, /download/ → dist/packages/)  Ctrl+C 로 종료")
    if args.open:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
