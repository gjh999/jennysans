#!/usr/bin/env bash
# JennySans → font.jennysoft.co.kr 배포 (로컬에서 실행; Git Bash / Linux / macOS)
#
# 사용: bash deploy/deploy.sh <버전>            예) bash deploy/deploy.sh 1.000
#       DRY=1 bash deploy/deploy.sh 1.000        # 전송·변경 없이 할 일만 출력
#       NO_LATEST=1 bash deploy/deploy.sh 1.001  # latest 심링크는 옮기지 않음(사전 배포)
#       SITE_SRC=site/dist bash deploy/deploy.sh 1.000   # 홈페이지 빌드 산출 폴더가 다를 때(기본 site/)
#
# 경로 매핑 (deploy/nginx-font.conf 와 1:1)
#   site/            (SITE_SRC)            → /var/www/font/               소개 홈페이지 (font-site 소유)
#   dist/{static,variable,web,css}/        → /var/www/font/v/<버전>/      폰트 CDN (immutable)
#   LICENSE THIRD-PARTY-NOTICES.md README.md CHANGELOG.md → /var/www/font/v/<버전>/ + 루트 LICENSE
#   dist/packages/   (zip 3종 + SHA256SUMS.txt, tools/package.py 산출) → /var/www/font/download/
#   latest -> v/<버전>                       (NO_LATEST=1 이면 유지)
#   교체 전 백업: v/<버전>.bak.<ts>, site.bak.<ts>/, download.bak.<ts>/ (각 최근 3개 유지)
#
# ⚠ 외부 전파(비가역)다 — QA RELEASE OK 후 팀장이 실행(AGENTS §3, docs/DISTRIBUTION.md §5-H). 이 파일을 만든 release 는 실행하지 않았다.
# ⚠ nginx conf·인증서·DNS 는 이 스크립트가 만지지 않는다(팀장 서버 작업, deploy/README.md §2).
# ⚠ curl 200 은 검증이 아니다 — 끝나면 다른 오리진의 브라우저에서 폰트 적용을 확인한다(deploy/README.md §4).
set -euo pipefail

VERSION="${1:-}"
[ -n "$VERSION" ] || { echo "사용: bash deploy/deploy.sh <버전>  예) 1.000"; exit 2; }
case "$VERSION" in *.???) ;; *) echo "!! 버전은 X.YZZ 형식(예 1.000)"; exit 2;; esac

SSH_HOST="${FONT_SSH_HOST:-debc-dev}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SITE_SRC="${SITE_SRC:-site}"
# 공개 서버에 올리지 않을 개발용 파일(렌더 원본 템플릿·로컬 스크립트·개발 문서·파이썬 캐시).
# 공백으로 구분한 glob 패턴이며 SITE_SRC 기준 상대경로에 대해 매칭한다(디렉터리는 하위 전체 제외).
# ⚠ google*.html(구글 소유확인)·robots.txt·sitemap.xml·favicon.ico·assets/ 는 SEO 에 필요하므로 절대 넣지 말 것.
SITE_EXCLUDE="${SITE_EXCLUDE:-*.template.html preview.py check_site.py README.md __pycache__ _measure_tmp.html}"
DRY="${DRY:-0}"
NO_LATEST="${NO_LATEST:-0}"
TS="$(date +%Y%m%d-%H%M%S)"
TGZ="jennysans-${VERSION}-${TS}.tgz"
STAGE="${TMPDIR:-/tmp}/jennysans-deploy-$$"

run() { echo "  \$ $*"; if [ "$DRY" != "1" ]; then "$@"; fi; }

# SITE_EXCLUDE 를 적용한 뒤 실제로 올라가는 홈페이지 파일 목록(SITE_SRC 기준 상대경로)
site_file_list() {
  find "$SITE_SRC" -type f | sed "s|^$SITE_SRC/||" | while IFS= read -r rel; do
    skip=0
    for x in $SITE_EXCLUDE; do
      case "$rel" in $x|$x/*|*/$x|*/$x/*) skip=1; break;; esac
    done
    [ "$skip" = "1" ] || printf '%s\n' "$rel"
  done
}

cd "$HERE"
echo "== JennySans $VERSION → $SSH_HOST:/var/www/font (v/$VERSION · download · 홈페이지) =="

# 1) 산출물 확인 -----------------------------------------------------------
echo "-- 1/3 산출물 확인"
missing=0
need() { if [ ! -e "$1" ]; then echo "  !! 없음: $1"; missing=1; fi; }
for w in Thin ExtraLight Light Regular Medium SemiBold Bold ExtraBold Black; do
  need "dist/static/JennySans-$w.ttf"
  need "dist/web/JennySans-$w.woff2"
done
need dist/variable/JennySansVariable.ttf
need dist/web/JennySansVariable.woff2
need dist/web/subset
need dist/css/jennysans.css
need dist/css/jennysans-variable.css
need dist/css/jennysans-dynamic-subset.css
need LICENSE; need THIRD-PARTY-NOTICES.md; need README.md; need CHANGELOG.md
need "$SITE_SRC/index.html"
need deploy/remote-install.sh
[ "$missing" = "0" ] || { echo "!! 빠진 산출물이 있다. 빌더(tools/build.py)·font-site·QA 를 먼저."; exit 1; }
if ! grep -q "JennySans $VERSION" dist/css/jennysans.css; then
  echo "  ⚠ dist/css/jennysans.css 에 'JennySans $VERSION' 문자열이 없다 — 버전이 맞는지 확인"
fi
PKG=0
if [ -d dist/packages ] && ls dist/packages/*.zip >/dev/null 2>&1; then
  PKG=1; echo "  다운로드 패키지: $(ls dist/packages/*.zip | wc -l | tr -d ' ') zip $( [ -f dist/packages/SHA256SUMS.txt ] && echo '+ SHA256SUMS.txt' || echo '(SHA256SUMS.txt 없음 — tools/package.py 확인)')"
else
  echo "  ⚠ dist/packages/*.zip 없음 — /download/ 는 갱신하지 않는다(tools/package.py 로 먼저 생성)"
fi
nsub=$(find dist/web/subset -name '*.woff2' | wc -l | tr -d ' ')
site_all=$(find "$SITE_SRC" -type f | wc -l | tr -d ' ')
site_send=$(site_file_list | wc -l | tr -d ' ')
echo "  정적 9 · 변수 1 · 분할 WOFF2 $nsub 개 · CSS $(ls dist/css/*.css | wc -l | tr -d ' ') · 문서 4 · 홈페이지 $SITE_SRC/ ($site_send 파일 전송 / $site_all 중, 개발용 $((site_all - site_send)) 제외)"
echo "  홈페이지 제외 패턴(SITE_EXCLUDE): $SITE_EXCLUDE"
if [ "$DRY" = "1" ]; then
  echo "  전송 대상:"; site_file_list | sed 's/^/    /'
fi

# 2) 묶어서 전송 -----------------------------------------------------------
echo "-- 2/3 전송 ($TGZ)"
run mkdir -p "$STAGE"
# tgz 내부 구조: dist/{static,variable,web,css}[,packages] · 문서 4 · site/ (SITE_SRC 를 site/ 이름으로 정규화)
run mkdir -p "$STAGE/pack/dist"
run cp -a dist/static dist/variable dist/web dist/css "$STAGE/pack/dist/"
[ "$PKG" = "1" ] && run cp -a dist/packages "$STAGE/pack/dist/"
run cp -a LICENSE THIRD-PARTY-NOTICES.md README.md CHANGELOG.md "$STAGE/pack/"
run mkdir -p "$STAGE/pack/site"
run cp -a "$SITE_SRC/." "$STAGE/pack/site/"
# SITE_EXCLUDE 적용 — 개발용 파일은 공개 서버에 올리지 않는다 (glob 을 살려야 하므로 run 을 쓰지 않는다)
for x in $SITE_EXCLUDE; do
  echo "  \$ rm -rf $STAGE/pack/site/$x"
  if [ "$DRY" != "1" ]; then rm -rf "$STAGE"/pack/site/$x; fi
done
if [ "$DRY" != "1" ]; then
  echo "  홈페이지 전송 파일 $(find "$STAGE/pack/site" -type f | wc -l | tr -d ' ') 개"
fi
run tar -C "$STAGE/pack" -czf "$STAGE/$TGZ" .
if [ "$DRY" != "1" ]; then ls -l "$STAGE/$TGZ"; fi
run scp -o BatchMode=yes "$STAGE/$TGZ" deploy/remote-install.sh "$SSH_HOST:/tmp/"

# 3) 서버 설치 -------------------------------------------------------------
echo "-- 3/3 서버 설치 (sudo remote-install.sh)"
flag=""; [ "$NO_LATEST" = "1" ] && flag="--no-latest"
run ssh -o BatchMode=yes "$SSH_HOST" "sudo bash /tmp/remote-install.sh '$VERSION' '/tmp/$TGZ' $flag && rm -f '/tmp/$TGZ' /tmp/remote-install.sh"
run rm -rf "$STAGE"

echo
echo "== 완료. 실제 확인(curl 200 은 검증이 아니다) =="
echo "  1) curl -sI -H 'Origin: https://example.com' https://font.jennysoft.co.kr/v/$VERSION/web/JennySans-Regular.woff2 | grep -i -E 'HTTP/|access-control|content-type|cache-control'"
echo "  2) curl -sI https://font.jennysoft.co.kr/download/JennySans-$VERSION-desktop.zip | grep -i -E 'HTTP/|content-type|content-disposition|cache-control'"
echo "  3) 브라우저: https://font.jennysoft.co.kr/ (홈페이지·다운로드 버튼 실제 파일 수신) — 강력 새로고침"
echo "  4) 다른 오리진 페이지에서 https://font.jennysoft.co.kr/v/$VERSION/css/jennysans-dynamic-subset.css 로 폰트 적용 스크린샷(docs/DISTRIBUTION.md §5-I)"
echo "  롤백: 서버의 /var/www/font/v/$VERSION.bak.<ts> · site.bak.<ts> · download.bak.<ts> 를 되돌리고 latest 심링크를 이전 버전으로(deploy/README.md §5)"
