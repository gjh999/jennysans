# -*- coding: utf-8 -*-
"""
tools/package.py — JennySans 다운로드 패키지(zip 4종) 생성 + 홈페이지 렌더 (font-site 소유)

    PYTHONUTF8=1 python tools/package.py                  # dist/ → dist/packages/*.zip + index.json + SHA256SUMS.txt
    PYTHONUTF8=1 python tools/package.py --render-site    # zip 생성 후 site/index.template.html → site/index.html
    PYTHONUTF8=1 python tools/package.py --render-only    # zip 재생성 없이 기존 index.json 으로 렌더만
    PYTHONUTF8=1 python tools/package.py --kinds desktop,web --render-site

- dist/ 는 읽기만 한다(빌더 소유). 쓰는 곳은 dist/packages/ 와 site/index.html 뿐.
- 버전은 tools/config.py 의 VERSION. zip 내부 최상위 폴더는 JennySans-<ver>-<kind>/.
- 크기·SHA-256·cmap 수치는 실행 시점에 실측해 index.json 에 넣고, 템플릿의 {{...}} 자리를 치환한다.
  치환되지 않은 {{...}} 가 남으면 실패한다(문서 실측치 게이트, docs/DISTRIBUTION.md §4-2 와 같은 기준).

템플릿 자리표시자 (site/index.template.html · site/glyphs.template.html — --render-site 가 둘 다 렌더)
    {{VERSION}} {{NPM_VERSION}} {{DATE}} {{GENERATED}} {{BASE_URL}}
    {{PKG:<kind>:file|bytes|size|sha256|sha12|files}}       kind = desktop | web | variable | all
    {{FILE:<dist 상대경로>:bytes|size|sha256}}               예 {{FILE:static/JennySans-Regular.ttf:size}}
    {{CMAP:total|hangul|jamo|compat|latin|greek|cyrillic|ks_symbols}}   Regular TTF cmap 실측
    {{LATIN_SLICE:<Weight>}}                                 분할 CSS 에서 U+0041 을 담는 조각 파일명
    {{SLICES}}                                               웨이트당 조각 수(Regular)
    {{LANG:total|latin|cyrillic|other|<script>_rows|excluded}}   tools/lang_support.py 실측(언어 수)
    {{LANG_TABLE:latin|cyrillic|other}}                      언어 표의 <tr> 들
    {{GLYPH:total|blocks|block_list}}                        tools/glyphmap.py 실측(글자 수·블록 수·블록 목록)

zip 은 **재현 가능**하다: 내부 타임스탬프와 안내문 날짜를 "가장 최근에 바뀐 입력 파일"의 시각으로 고정하므로
dist/ 가 그대로면 몇 번을 다시 만들어도 SHA-256 이 같다(QA 가 체크섬을 비교할 수 있게).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import config  # noqa: E402  (tools/config.py — builder 소유, 읽기만)

FAMILY = "JennySans"
VERSION: str = config.VERSION
DIST: Path = config.DIST
DIST_STATIC: Path = config.DIST_STATIC
DIST_VARIABLE: Path = config.DIST_VARIABLE
DIST_WEB: Path = config.DIST_WEB
DIST_WEB_SUBSET: Path = config.DIST_WEB_SUBSET
DIST_CSS: Path = config.DIST_CSS
WEIGHT_NAMES: list[str] = list(config.WEIGHT_NAMES)
BASE_URL: str = getattr(config, "CSS_VENDOR_URL", "https://font.jennysoft.co.kr").rstrip("/")

PKG_DIR = DIST / "packages"
SITE = ROOT / "site"
TEMPLATE = SITE / "index.template.html"
OUTPUT = SITE / "index.html"
# --render-site 가 렌더하는 템플릿 전부 (템플릿 → 산출 파일)
TEMPLATES = [(SITE / "index.template.html", SITE / "index.html"),
             (SITE / "glyphs.template.html", SITE / "glyphs.html")]
LANG_JSON = SITE / "assets" / "languages.json"
GLYPHMAP_JSON = SITE / "assets" / "glyphmap.json"
DIFF_JSON = SITE / "assets" / "origin-diff.json"
PAINT_JSON = SITE / "assets" / "first-paint.json"
KINDS = ("desktop", "web", "variable", "all")

KIND_TITLE = {
    "desktop": "데스크톱 설치용 (정적 TTF 9종)",
    "web": "웹용 (WOFF2 전체본·분할본 + CSS)",
    "variable": "변수 폰트 (TTF + WOFF2 + CSS)",
    "all": "전체 (정적·변수·웹·CSS·문서)",
}


# --------------------------------------------------------------------------- utils
def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def human_size(n: int) -> str:
    """십진 단위(1 MB = 1,000,000 bytes). 페이지에는 bytes 도 함께 표기한다."""
    if n < 1000:
        return f"{n} B"
    if n < 1_000_000:
        return f"{n / 1000:.0f} KB"
    if n < 1_000_000_000:
        return f"{n / 1_000_000:.1f} MB"
    return f"{n / 1_000_000_000:.2f} GB"


def npm_version(v: str) -> str:
    """폰트 버전 X.YZZ ↔ npm X.Y.ZZ (docs/DISTRIBUTION.md §1-1)."""
    m = re.fullmatch(r"(\d+)\.(\d)(\d\d)", v)
    if not m:
        return v
    return f"{int(m.group(1))}.{int(m.group(2))}.{int(m.group(3))}"


def now_kst() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9)))


def need(path: Path, what: str) -> Path:
    if not path.exists():
        raise SystemExit(f"!! 없음: {path}  ({what}) — 빌더(tools/build.py)가 dist/ 를 먼저 만들어야 한다")
    return path


# --------------------------------------------------------------------------- zip 구성
def kind_entries(kind: str) -> tuple[str, list[tuple[Path, str]]]:
    """(최상위 폴더명, [(원본 경로, zip 안 상대경로), ...]) — 공통 LICENSE 류 포함."""
    top = f"{FAMILY}-{VERSION}-{kind}"
    ents: list[tuple[Path, str]] = []

    def add_static() -> None:
        for w in WEIGHT_NAMES:
            ents.append((need(DIST_STATIC / f"{FAMILY}-{w}.ttf", "정적 TTF"), f"static/{FAMILY}-{w}.ttf"))

    def add_css(names: list[str] | None = None) -> None:
        files = sorted(DIST_CSS.glob("*.css")) if names is None else [need(DIST_CSS / n, "CSS") for n in names]
        if not files:
            raise SystemExit(f"!! dist/css 에 CSS 가 없다: {DIST_CSS}")
        for p in files:
            ents.append((p, f"css/{p.name}"))

    def add_web_full() -> None:
        files = sorted(DIST_WEB.glob("*.woff2"))
        if len(files) < 10:
            raise SystemExit(f"!! dist/web 전체본 WOFF2 가 10개 미만({len(files)}): {DIST_WEB}")
        for p in files:
            ents.append((p, f"web/{p.name}"))

    def add_web_subset() -> None:
        files = sorted(DIST_WEB_SUBSET.glob("*.woff2"))
        if not files:
            raise SystemExit(f"!! dist/web/subset 분할본이 없다: {DIST_WEB_SUBSET}")
        for p in files:
            ents.append((p, f"web/subset/{p.name}"))

    if kind == "desktop":
        # 데스크톱은 폴더 없이 바로 TTF (설치할 때 파일만 고르면 되게)
        for w in WEIGHT_NAMES:
            ents.append((need(DIST_STATIC / f"{FAMILY}-{w}.ttf", "정적 TTF"), f"{FAMILY}-{w}.ttf"))
    elif kind == "web":
        add_css()
        add_web_full()
        add_web_subset()
    elif kind == "variable":
        ents.append((need(DIST_VARIABLE / f"{FAMILY}Variable.ttf", "변수 TTF"), f"variable/{FAMILY}Variable.ttf"))
        ents.append((need(DIST_WEB / f"{FAMILY}Variable.woff2", "변수 WOFF2"), f"web/{FAMILY}Variable.woff2"))
        add_css(["jennysans-variable.css"])  # css/../web/ 상대경로가 그대로 동작하도록 구조 유지
    elif kind == "all":
        add_static()
        ents.append((need(DIST_VARIABLE / f"{FAMILY}Variable.ttf", "변수 TTF"), f"variable/{FAMILY}Variable.ttf"))
        add_web_full()
        add_web_subset()
        add_css()
        for name, arc in (("README.md", "README.md"), ("CHANGELOG.md", "CHANGELOG.md"), ("docs/INSTALL.md", "INSTALL.md")):
            p = ROOT / name
            if p.exists():
                ents.append((p, arc))
    else:
        raise SystemExit(f"!! 모르는 kind: {kind}")

    # 공통: 라이선스·고지 (OFL 조건 2 — 폰트를 재배포할 때 함께 둔다)
    ents.append((need(ROOT / "LICENSE", "LICENSE"), "LICENSE"))
    ents.append((need(ROOT / "LICENSE", "LICENSE"), "LICENSE.txt"))
    tp = ROOT / "THIRD-PARTY-NOTICES.md"
    if tp.exists():
        ents.append((tp, "THIRD-PARTY-NOTICES.md"))
    return top, ents


# --------------------------------------------------------------------------- README-설치안내.txt
_GUIDE_HEAD = """JennySans 「제니산스」 {version} — {title}
======================================================================
제니소프트(JennySoft)의 범용 한글·영문(라틴) 고딕(산세리프) 폰트 패밀리.
현대 한글 11,172자 전부 · 서유럽/중앙유럽 라틴(스페인어 포함) · 그리스/키릴 기본 · 한국 문서용 기호(KS X 1001).
9 웨이트(Thin 100 – Black 900) + 변수 폰트 1종. 이탤릭 없음.
라이선스: SIL Open Font License 1.1 (Reserved Font Names 'JennySans', '제니산스')

홈페이지·최신 버전·사용법: {base_url}
패키지 생성: {date}

[이 패키지의 내용]
{contents}
"""

_GUIDE_DESKTOP = """
[Windows 10/11 설치]
 1. TTF 파일을 모두 선택 → 마우스 오른쪽 → "설치"(내 계정) 또는 "모든 사용자용으로 설치"(관리자).
 2. 이미 JennySans 가 설치돼 있으면: 폰트를 쓰는 프로그램(한글·Office·브라우저·Photoshop 등)을 모두 닫고,
    설정 > 개인 설정 > 글꼴 에서 JennySans 항목(웨이트별로 여러 개)을 제거한 뒤 새로 설치합니다.
 3. 옛 모양이 계속 보이면 재부팅하거나 관리자 PowerShell 에서:  Stop-Service FontCache; Start-Service FontCache
 4. 사용자 설치본과 모든 사용자용 설치본을 같은 이름으로 둘 다 두지 마세요(프로그램마다 다른 쪽을 씁니다).

[macOS 설치]
 TTF 를 더블클릭 → "서체 설치"(Font Book/서체 관리자). 사용자(~/Library/Fonts) 또는 컴퓨터(/Library/Fonts).
 교체할 때는 Font Book 에서 기존 JennySans 패밀리를 제거한 뒤 설치하고 앱을 다시 엽니다.

[한글(HWP) · MS Office]
 글꼴 목록에 「제니산스」(JennySans) 와 웨이트별 항목(JennySans Light, JennySans Medium …)이 따로 보입니다.
 굵기는 목록에서 직접 고르세요. Regular 에서 '진하게'(Ctrl+B)는 진짜 Bold 파일로 바뀌지만,
 Light 등 다른 웨이트에서 '진하게'를 누르면 합성 굵게가 되어 품질이 떨어집니다. 한글·Office 는 변수 폰트 축을 지원하지 않습니다.

[Photoshop · Illustrator · InDesign · Figma]
 패밀리 "JennySans" 하나에 스타일 9개(Thin … Black)가 보입니다. 이탤릭이 없으니 가짜 기울임(Faux Italic)은 쓰지 마세요.

[Flutter]
 assets/fonts/ 에 TTF 를 복사하고 pubspec.yaml 에 family: JennySans 로 웨이트별(weight: 100 … 900)로 선언합니다.
 실제로 쓰는 웨이트만 선언하면 앱 크기가 줄어듭니다(정적 TTF 1개 ≈ 2.5 MB).

[Unity(TextMesh Pro) · Godot]
 Unity: Font Asset Creator 로 SDF 에셋 생성. 한글 11,172자를 정적 아틀라스에 다 굽지 말고 Dynamic 모드(+ Multi Atlas)
        또는 KS X 1001 2,350자 정적 + Dynamic 을 권장. Godot 4: TTF 를 그대로 임포트(FontFile), 변수 TTF 는 FontVariation.
"""

_GUIDE_WEB = """
[웹에서 쓰기]
 css/ 와 web/ 폴더를 같은 구조 그대로 서버에 올리고, CSS 중 하나만 <link> 하세요(둘 이상 링크하면 이중 다운로드).
   <link rel="stylesheet" href="/fonts/css/jennysans-dynamic-subset.css">
   <style> html {{ font-family: "JennySans", "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif; font-synthesis: none; }} </style>

   jennysans-dynamic-subset.css  — 한국어 페이지 기본 권장. 페이지에 실제로 쓰인 글자가 든 조각(unicode-range)만 내려받음
   jennysans.css                 — 웨이트별 전체본 1파일(인트라넷·오프라인·웨이트 1~2개)
   jennysans-variable.css        — 변수 폰트 전체본 1파일(wght 100–900, 웨이트 4개 이상일 때 총량 최소)
   jennysans-variable-dynamic-subset.css — 변수 폰트 분할본

 CSS 안의 경로는 ../web/ 상대경로이므로 css/ 와 web/ 의 상대 구조를 유지하면 CSS 를 고칠 필요가 없습니다.
 다른 도메인에서 폰트를 받아 쓰면 폰트 서버가 Access-Control-Allow-Origin 헤더를 내야 합니다(없으면 폴백 폰트로 보임).
 MIME: font/woff2. 캐시: 경로에 버전을 넣고 Cache-Control: public, max-age=31536000, immutable. WOFF2 는 gzip 하지 않습니다.

 자체 CDN(공개 후):  {base_url}/v/{version}/css/jennysans-dynamic-subset.css
"""

_GUIDE_VARIABLE = """
[변수 폰트]
 데스크톱: variable/JennySansVariable.ttf 를 설치하면 패밀리 "JennySans Variable"(wght 100–900) 로 보입니다.
          정적 9종과 이름이 달라 함께 설치해도 충돌하지 않습니다. 한글(HWP)·MS Office 는 변수 축을 지원하지 않습니다.
 웹:      css/jennysans-variable.css 를 링크하면 font-family: "JennySans" 에 font-weight 100–900 을 그대로 쓸 수 있습니다.
          Chrome 62+ · Firefox 62+ · Safari 11+ · Edge 17+.
 Godot:   FontVariation 의 variation_opentype = {{"wght": 700}}.  Flutter: TextStyle(fontVariations: [FontVariation('wght', 600)]).
"""

_GUIDE_TAIL = """
[라이선스 요지 — SIL Open Font License 1.1]
 - 상업 이용·수정·재배포·소프트웨어/게임/문서 임베드·웹폰트 사용: 모두 허용. 사용 대가·신고·표기 의무 없음.
 - 폰트 파일 자체를 단독으로 판매하는 것: 금지(소프트웨어·서비스에 포함해 파는 것은 가능).
 - 수정본을 'JennySans' 또는 '제니산스' 이름으로 배포하는 것: 금지(이름을 바꾸고 OFL 로만 배포).
 - 폰트 파일을 재배포할 때는 LICENSE 를 함께 두세요. 폰트 내부(name ID 0/13/14)에도 고지가 들어 있습니다.
 - 원본: Pretendard 1.3.9(그 안의 Inter · Source Han Sans · M PLUS 1 포함) · Noto Sans KR 2.004 —
   저작권 고지와 Reserved Font Name 은 LICENSE 와 THIRD-PARTY-NOTICES.md 에 그대로 보존돼 있습니다.
 - 보증 없음("있는 그대로"). 전문은 LICENSE / https://openfontlicense.org

문의: https://jennysoft.co.kr  ·  홈페이지: {base_url}
"""


def guide_text(kind: str, arcnames: list[str], stamp: _dt.datetime) -> str:
    contents = "\n".join(f" - {a}" for a in arcnames)
    head = _GUIDE_HEAD.format(version=VERSION, title=KIND_TITLE[kind], base_url=BASE_URL,
                              date=stamp.strftime("%Y-%m-%d"), contents=contents)
    body = ""
    if kind in ("desktop", "all"):
        body += _GUIDE_DESKTOP
    if kind in ("variable", "all"):
        body += _GUIDE_VARIABLE
    if kind in ("web", "all"):
        body += _GUIDE_WEB.format(base_url=BASE_URL, version=VERSION)
    tail = _GUIDE_TAIL.format(base_url=BASE_URL)
    return (head + body + tail).replace("\n", "\r\n")  # Windows 메모장 호환


# --------------------------------------------------------------------------- zip 생성
def build_zip(kind: str, out_dir: Path) -> dict:
    top, ents = kind_entries(kind)
    out = out_dir / f"{top}.zip"
    tmp = out.with_suffix(".zip.part")
    arcs = [arc for _, arc in ents] + ["README-설치안내.txt"]
    # 재현성: zip 안의 타임스탬프·안내문 날짜를 "가장 최근에 바뀐 입력 파일"의 시각으로 고정한다.
    # → 입력(dist·LICENSE 류)이 그대로면 다시 만들어도 SHA-256 이 같다(QA 가 체크섬을 비교할 수 있게).
    newest = max(src.stat().st_mtime for src, _ in ents)
    stamp = _dt.datetime.fromtimestamp(newest, _dt.timezone(_dt.timedelta(hours=9)))
    guide = guide_text(kind, arcs, stamp)
    t = stamp.timetuple()[:6]
    total_src = 0
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        # 안내문을 맨 앞에 (압축 파일을 열면 제일 먼저 보이게)
        zi = zipfile.ZipInfo(f"{top}/README-설치안내.txt", date_time=t)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o644 << 16
        zf.writestr(zi, guide.encode("utf-8-sig"))
        for src, arc in ents:
            zi = zipfile.ZipInfo(f"{top}/{arc}", date_time=t)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            with open(src, "rb") as fh:
                zf.writestr(zi, fh.read(), compress_type=zipfile.ZIP_DEFLATED)
            total_src += src.stat().st_size
        names = zf.namelist()
    if out.exists():
        out.unlink()
    tmp.rename(out)
    size = out.stat().st_size
    return {
        "kind": kind,
        "title": KIND_TITLE[kind],
        "file": out.name,
        "top_dir": top,
        "bytes": size,
        "size": human_size(size),
        "sha256": sha256_of(out),
        "files": len(names),
        "source_mtime": stamp.isoformat(timespec="seconds"),
        "uncompressed_bytes": total_src + len(guide.encode("utf-8-sig")),
        "contents": [n[len(top) + 1:] for n in names],
    }


# --------------------------------------------------------------------------- 실측(폰트·CSS)
def measure_fonts() -> dict:
    """정적 9·변수 1·WOFF2 10 의 bytes/SHA + Regular cmap 수치 + 라틴 조각 파일명."""
    files: dict[str, dict] = {}

    def rec(p: Path) -> None:
        if p.exists():
            files[p.relative_to(DIST).as_posix()] = {"bytes": p.stat().st_size, "sha256": sha256_of(p)}

    for w in WEIGHT_NAMES:
        rec(DIST_STATIC / f"{FAMILY}-{w}.ttf")
        rec(DIST_WEB / f"{FAMILY}-{w}.woff2")
    rec(DIST_VARIABLE / f"{FAMILY}Variable.ttf")
    rec(DIST_WEB / f"{FAMILY}Variable.woff2")
    for p in sorted(DIST_CSS.glob("*.css")):
        rec(p)

    cmap_info: dict[str, int] = {}
    reg = DIST_STATIC / f"{FAMILY}-Regular.ttf"
    if reg.exists():
        from fontTools.ttLib import TTFont  # 실행 환경에 있음(AGENTS §2)
        f = TTFont(str(reg), lazy=True)
        cm = f.getBestCmap()
        cps = set(cm)
        f.close()

        def count(a: int, b: int) -> int:
            return sum(1 for c in range(a, b + 1) if c in cps)

        cmap_info = {
            "total": len(cps),
            "hangul": count(0xAC00, 0xD7A3),
            "jamo": count(0x1100, 0x11FF),
            "compat": count(0x3131, 0x318E),
            "latin": count(0x0020, 0x007E) + count(0x00A0, 0x00FF) + count(0x0100, 0x017F),
            "greek": count(0x0370, 0x03FF),
            "cyrillic": count(0x0400, 0x04FF),
            "ks_symbols": (count(0x2460, 0x24FF) + count(0x3200, 0x32FF) + count(0x3300, 0x33FF)
                           + count(0x2500, 0x257F) + count(0x2190, 0x21FF) + count(0x2200, 0x22FF)
                           + count(0x25A0, 0x25FF) + count(0x2600, 0x26FF)),
        }

    latin_slice: dict[str, str] = {}
    slices: dict[str, int] = {}
    css = DIST_CSS / "jennysans-dynamic-subset.css"
    if css.exists():
        text = css.read_text(encoding="utf-8")
        for block in re.findall(r"@font-face\s*\{(.*?)\}", text, flags=re.S):
            mw = re.search(r"font-weight:\s*(\d+)", block)
            ms = re.search(r"url\(\"[^\"]*?/([^/\"]+\.woff2)\"\)", block)
            mu = re.search(r"unicode-range:\s*([^;]+);", block)
            if not (mw and ms and mu):
                continue
            wname = next((n for n, v in config.WEIGHTS if str(v) == mw.group(1)), None)
            if not wname:
                continue
            slices[wname] = slices.get(wname, 0) + 1
            # U+0041 'A' 를 담는 조각 = 라틴 조각
            for rng in mu.group(1).split(","):
                rng = rng.strip().upper().replace("U+", "")
                if "-" in rng:
                    a, b = rng.split("-")
                    if int(a, 16) <= 0x41 <= int(b, 16):
                        latin_slice[wname] = ms.group(1)
                elif rng and int(rng, 16) == 0x41:
                    latin_slice[wname] = ms.group(1)
    return {"files": files, "cmap": cmap_info, "latin_slice": latin_slice, "slices_per_weight": slices}


# --------------------------------------------------------------------------- index.json
def write_index(packages: list[dict], out_dir: Path) -> dict:
    meas = measure_fonts()
    ts = now_kst()
    index = {
        "family": FAMILY,
        "korean_name": "제니산스",
        "version": VERSION,
        "npm_version": npm_version(VERSION),
        "license": "SIL Open Font License 1.1 (Reserved Font Names 'JennySans', '제니산스')",
        "generated": ts.isoformat(timespec="seconds"),
        "base_url": BASE_URL,
        "download_path": "/download/",
        "packages": {p["kind"]: p for p in packages},
        "fonts": meas["files"],
        "cmap_regular": meas["cmap"],
        "latin_slice": meas["latin_slice"],
        "slices_per_weight": meas["slices_per_weight"],
    }
    (out_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with open(out_dir / "SHA256SUMS.txt", "w", encoding="ascii", newline="\n") as f:
        for p in packages:
            f.write(f"{p['sha256']}  {p['file']}\n")
    return index


def load_index(out_dir: Path) -> dict:
    p = out_dir / "index.json"
    if not p.exists():
        raise SystemExit(f"!! {p} 가 없다 — 먼저 zip 을 만들어라(--render-only 는 기존 index.json 이 필요)")
    return json.loads(p.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- 렌더
def refresh_site_data() -> tuple[dict, dict, dict]:
    """글자맵·지원 언어·원본 대비 차이 JSON 을 dist 실측으로 다시 만든다(전부 site/assets 에만 쓴다)."""
    import glyphmap  # tools/
    import lang_support  # tools/
    import origin_diff  # tools/

    font = DIST_STATIC / f"{FAMILY}-Regular.ttf"
    need(font, "글자맵·언어 실측용 Regular TTF")
    gm = glyphmap.build(font)
    GLYPHMAP_JSON.parent.mkdir(parents=True, exist_ok=True)
    GLYPHMAP_JSON.write_text(json.dumps(gm, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    lang = lang_support.build(font)
    LANG_JSON.write_text(json.dumps(lang, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"  글자맵 {GLYPHMAP_JSON.name} ({GLYPHMAP_JSON.stat().st_size:,} B, 블록 {len(gm['blocks'])}) · "
          f"언어 {LANG_JSON.name} (라틴 {lang['languages']['latin']} · 키릴 {lang['languages']['cyrillic']} · "
          f"그 밖 {lang['languages']['other']} = {lang['languages']['total']}개 언어)")

    diff: dict = {}
    origin_font = config.PRETENDARD_TTF_DIR / "Pretendard-Regular.ttf"
    if origin_font.exists():
        diff = origin_diff.build(origin_font, font)
        DIFF_JSON.write_text(json.dumps(diff, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        t = diff["totals"]
        print(f"  원본 대비 {DIFF_JSON.name} (카테고리 추가 {t['category_added']:,} · 가나 제외 {t['kana_removed']} · "
              f"전체 추가 {t['added_total']:,} / 제외 {t['removed_total']:,})")
    elif DIFF_JSON.exists():
        diff = json.loads(DIFF_JSON.read_text(encoding="utf-8"))
        print(f"  원본 대비: sources/ 가 없어 기존 {DIFF_JSON.name} 을 그대로 쓴다({diff.get('generated')})")
    return gm, lang, diff


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def lang_rows(lang: dict, script: str) -> str:
    """지원 언어 표의 <tr> 들 — languages.json 실측에서 생성(하드코딩 금지)."""
    rows = []
    for e in lang["groups"].get(script, []):
        rows.append(
            f'<tr><th scope="row">{_esc(e["name"])}<span class="lang-native">{_esc(e["native"])}</span></th>'
            f'<td class="lang-sample">{_esc(e["sample"])}</td></tr>'
        )
    return "\n            ".join(rows)


def glyph_block_rows(gm: dict) -> str:
    """문자 범위 섹션의 블록 요약 <li> — 글자맵 JSON 실측에서 생성."""
    items = []
    for b in gm["blocks"]:
        if b["id"] == "other":
            continue
        items.append(f'<li><b>{_esc(b["label"])}</b><span>{b["count"]:,}</span></li>')
    return "\n          ".join(items)


def diff_rows(diff: dict) -> str:
    """원본 대비 차이 표의 <tr> 들 — origin-diff.json 실측에서 생성."""
    rows = []
    for r in diff.get("rows", []):
        cls = "diff-up" if r["delta"] > 0 else ("diff-down" if r["delta"] < 0 else "")
        sign = f'{r["delta"]:+,}'
        rows.append(
            f'<tr><th scope="row">{_esc(r["label"])}<span class="diff-note">{_esc(r["note"])}</span></th>'
            f'<td class="num">{r["origin"]:,}</td><td class="num">{r["ours"]:,}</td>'
            f'<td class="num {cls}">{sign}</td></tr>'
        )
    return "\n            ".join(rows)


def render_site(index: dict, template: Path = TEMPLATE, output: Path = OUTPUT,
                gm: dict | None = None, lang: dict | None = None, diff: dict | None = None,
                paint: dict | None = None) -> int:
    if not template.exists():
        raise SystemExit(f"!! 템플릿이 없다: {template}")
    tpl = template.read_text(encoding="utf-8")
    generated = index["generated"]
    date = generated[:10]
    fonts: dict = index.get("fonts", {})
    cmap: dict = index.get("cmap_regular", {})
    missing: list[str] = []

    def fmt_int(n: int) -> str:
        return f"{n:,}"

    def resolve(key: str) -> str | None:
        parts = key.split(":")
        head = parts[0]
        if head == "VERSION":
            return index["version"]
        if head == "NPM_VERSION":
            return index.get("npm_version") or npm_version(index["version"])
        if head == "DATE":
            return date
        if head == "GENERATED":
            return generated
        if head == "BASE_URL":
            return index["base_url"]
        if head == "SLICES":
            s = index.get("slices_per_weight", {})
            return str(s.get("Regular") or (max(s.values()) if s else ""))
        if head == "PKG" and len(parts) == 3:
            pkg = index["packages"].get(parts[1])
            if not pkg:
                return None
            field = parts[2]
            if field == "bytes":
                return fmt_int(pkg["bytes"])
            if field == "sha12":
                return pkg["sha256"][:12]
            if field == "files":
                return str(pkg["files"])
            v = pkg.get(field)
            return None if v is None else str(v)
        if head == "FILE" and len(parts) == 3:
            rel = parts[1]
            info = fonts.get(rel)
            if info is None:
                p = DIST / rel
                if not p.exists():
                    return None
                info = {"bytes": p.stat().st_size, "sha256": sha256_of(p)}
                fonts[rel] = info
            field = parts[2]
            if field == "bytes":
                return fmt_int(info["bytes"])
            if field == "size":
                return human_size(info["bytes"])
            if field == "sha256":
                return info["sha256"]
            return None
        if head == "CMAP" and len(parts) == 2:
            v = cmap.get(parts[1])
            return None if v is None else fmt_int(v)
        if head == "LATIN_SLICE" and len(parts) == 2:
            return index.get("latin_slice", {}).get(parts[1])
        if head == "LANG" and len(parts) == 2 and lang:
            field = parts[1]
            if field in lang["languages"]:
                return fmt_int(lang["languages"][field])
            if field.endswith("_rows") and field[:-5] in lang["counts"]:
                return fmt_int(lang["counts"][field[:-5]])
            if field == "excluded":
                return ", ".join(e["name"] for e in lang.get("excluded", []))
            return None
        if head == "LANG_TABLE" and len(parts) == 2 and lang:
            return lang_rows(lang, parts[1])
        if head == "DIFF" and len(parts) == 2 and diff:
            field = parts[1]
            if field == "table":
                return diff_rows(diff)
            if field in diff.get("totals", {}):
                return fmt_int(diff["totals"][field])
            if field == "origin_cmap":
                return fmt_int(diff["origin"]["cmap"])
            if field == "ours_cmap":
                return fmt_int(diff["ours"]["cmap"])
            if field == "origin_version":
                return diff["origin"].get("version", "")
            if field in diff.get("web", {}):
                return fmt_int(diff["web"][field])
            return None
        if head == "PAINT" and len(parts) == 3 and paint:
            case = paint.get("cases", {}).get(parts[1])
            if not case:
                return None
            if parts[2] == "kb":
                return f'{case["kb"]:.1f}'
            if parts[2] in case:
                return fmt_int(case[parts[2]]) if isinstance(case[parts[2]], int) else str(case[parts[2]])
            return None
        if head == "GLYPH" and len(parts) == 2 and gm:
            if parts[1] == "blocks":
                return str(len([b for b in gm["blocks"] if b["id"] != "other"]))
            if parts[1] == "total":
                return fmt_int(gm["total"])
            if parts[1] == "block_list":
                return glyph_block_rows(gm)
            return None
        return None

    def repl(m: re.Match) -> str:
        key = m.group(1).strip()
        v = resolve(key)
        if v is None:
            missing.append(key)
            return m.group(0)
        return v

    out = re.sub(r"\{\{([^{}]+)\}\}", repl, tpl)
    if missing:
        raise SystemExit("!! 치환하지 못한 자리표시자: " + ", ".join(sorted(set(missing))))
    # 템플릿에서 왔음을 알리는 주석 (직접 수정 방지)
    banner = (f"<!-- 생성 파일: tools/package.py --render-site 가 site/index.template.html 에서 만든다. "
              f"직접 고치지 말고 템플릿을 고친 뒤 다시 렌더. {generated} -->\n")
    if out.lstrip().lower().startswith("<!doctype html>"):
        i = out.find("\n") + 1
        out = out[:i] + banner + out[i:]
    else:
        out = banner + out
    output.write_text(out, encoding="utf-8", newline="\n")
    return len(out.encode("utf-8"))


# --------------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="JennySans 다운로드 zip 4종 + index.json 생성, 홈페이지 렌더")
    ap.add_argument("--kinds", default=",".join(KINDS), help=f"쉼표 구분 (기본 {','.join(KINDS)})")
    ap.add_argument("--out", default=str(PKG_DIR), help="출력 디렉터리 (기본 dist/packages)")
    ap.add_argument("--render-site", action="store_true", help="zip 생성 후 site/*.html 렌더(글자맵·언어 JSON 도 갱신)")
    ap.add_argument("--render-only", action="store_true", help="zip 을 만들지 않고 기존 index.json 으로 렌더만")
    ap.add_argument("--template", default=None, help="이 템플릿 하나만 렌더(기본: TEMPLATES 전부)")
    ap.add_argument("--output", default=None, help="--template 과 함께 쓰는 출력 경로")
    args = ap.parse_args(argv)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.render_only:
        index = load_index(out_dir)
    else:
        kinds = [k.strip() for k in args.kinds.split(",") if k.strip()]
        bad = [k for k in kinds if k not in KINDS]
        if bad:
            raise SystemExit(f"!! 모르는 kind: {bad} (가능: {KINDS})")
        print(f"== JennySans {VERSION} 패키지 → {out_dir}")
        packages: list[dict] = []
        prev = load_index(out_dir)["packages"] if (out_dir / "index.json").exists() else {}
        for k in kinds:
            info = build_zip(k, out_dir)
            packages.append(info)
            print(f"  {info['file']:<36} {info['size']:>9} ({info['bytes']:>12,} bytes)  {info['files']:>5} files  sha256 {info['sha256'][:12]}…")
        # 이번에 만들지 않은 kind 는 기존 index.json 값을 유지(파일이 아직 있을 때만)
        for k, p in prev.items():
            if k not in {x["kind"] for x in packages} and (out_dir / p["file"]).exists():
                packages.append(p)
        packages.sort(key=lambda p: KINDS.index(p["kind"]))
        index = write_index(packages, out_dir)
        print(f"  index.json · SHA256SUMS.txt 갱신 ({index['generated']})")
        cm = index["cmap_regular"]
        if cm:
            print(f"  cmap(Regular): total {cm['total']:,} · 한글 {cm['hangul']:,} · 자모 {cm['jamo']} · 호환자모 {cm['compat']} · 그리스 {cm['greek']} · 키릴 {cm['cyrillic']}")
        if index["latin_slice"]:
            print(f"  라틴 조각: {index['latin_slice'].get('Regular')} (웨이트당 {index['slices_per_weight'].get('Regular')} 조각)")

    if args.render_site or args.render_only:
        gm, lang, diff = refresh_site_data()
        paint = json.loads(PAINT_JSON.read_text(encoding="utf-8")) if PAINT_JSON.exists() else {}
        if paint:
            print(f"  첫 화면 실측 {PAINT_JSON.name} ({paint.get('generated')}) — 갱신은 `python tools/first_paint.py`")
        pairs = [(Path(args.template), Path(args.output))] if args.template and args.output else TEMPLATES
        for tpl, out in pairs:
            if not tpl.exists():
                print(f"  (건너뜀: {tpl.name} 없음)")
                continue
            n = render_site(index, tpl, out, gm, lang, diff, paint)
            print(f"== 렌더: {out} ({n:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
