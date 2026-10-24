#!/usr/bin/env bash
# 서버 측 설치 스크립트 — deploy/deploy.sh 가 /tmp 로 올려 `sudo bash` 로 실행한다. (root 권한 필요)
#
# 사용: sudo bash remote-install.sh <버전> <tgz> [--no-latest]
#   <tgz> 내부 구조: dist/{static,variable,web,css}[,packages]  LICENSE THIRD-PARTY-NOTICES.md README.md CHANGELOG.md  site/
#
# 결과 /var/www/font/
#   (site/ 의 파일 전부 = 소개 홈페이지)  + LICENSE 사본
#   v/<버전>/{static,variable,web,css}/ + LICENSE LICENSE.txt THIRD-PARTY-NOTICES.md README.md CHANGELOG.md
#   latest -> v/<버전>        (--no-latest 가 없을 때)
#   download/                 ← dist/packages/ (같은 이름 파일은 덮어쓰기 전 download.bak.<ts>/ 로 보관)
# 백업: v/<버전> 이 이미 있으면 v/<버전>.bak.<ts> 로, 기존 홈페이지 파일은 site.bak.<ts>/ 로 (각 최근 3개 유지).
# 소유권: nginx:nginx(팀장 font-bootstrap.sh 와 동일), 디렉터리 755 / 파일 644.
# SELinux: 설치 후 restorecon -RF 로 컨텍스트를 복구한다(5-1) — 빠뜨리면 권한이 정상이어도 전 경로 403 (2026-09-09 사고).
set -euo pipefail

ROOT="${FONT_ROOT:-/var/www/font}"
VER="${1:-}"; TGZ="${2:-}"; NO_LATEST=0
[ "${3:-}" = "--no-latest" ] && NO_LATEST=1
[ -n "$VER" ] && [ -f "$TGZ" ] || { echo "사용: sudo bash remote-install.sh <버전> <tgz> [--no-latest]"; exit 2; }
[ "$(id -u)" = "0" ] || { echo "!! root 로 실행(sudo)"; exit 2; }

TS="$(date +%Y%m%d-%H%M%S)"
STAGE="$(mktemp -d /tmp/jennysans-stage.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT
prune() { ls -1d "$1".* 2>/dev/null | sort | head -n -3 | while read -r old; do echo "   오래된 백업 삭제: $old"; rm -rf "$old"; done; }

echo "== remote-install: JennySans $VER → $ROOT =="
tar -xzf "$TGZ" -C "$STAGE"
for p in dist/css/jennysans.css dist/web dist/static dist/variable LICENSE site/index.html; do
  [ -e "$STAGE/$p" ] || { echo "!! tgz 에 $p 가 없다"; exit 1; }
done
mkdir -p "$ROOT/v"

# 1) 폰트 CDN v/<버전> --------------------------------------------------------
if [ -e "$ROOT/v/$VER" ]; then
  echo "-- 기존 v/$VER → v/$VER.bak.$TS"
  mv "$ROOT/v/$VER" "$ROOT/v/$VER.bak.$TS"
  prune "$ROOT/v/$VER.bak"
fi
echo "-- 설치 v/$VER"
mkdir -p "$ROOT/v/$VER"
for d in static variable web css; do cp -a "$STAGE/dist/$d" "$ROOT/v/$VER/"; done
for f in LICENSE THIRD-PARTY-NOTICES.md README.md CHANGELOG.md; do
  [ -f "$STAGE/$f" ] && cp -a "$STAGE/$f" "$ROOT/v/$VER/$f"
done
cp -a "$STAGE/LICENSE" "$ROOT/v/$VER/LICENSE.txt"

# 2) 홈페이지 (site/ → 루트) ----------------------------------------------------
# 루트에 있는 v/·latest·download·*.bak.* 를 제외한 모든 파일·폴더가 홈페이지다 → site.bak.<ts>/ 로 옮긴 뒤 새로 놓는다
if find "$ROOT" -mindepth 1 -maxdepth 1 ! -name v ! -name latest ! -name download ! -name '*.bak.*' | grep -q .; then
  echo "-- 기존 홈페이지 → site.bak.$TS/"
  mkdir -p "$ROOT/site.bak.$TS"
  find "$ROOT" -mindepth 1 -maxdepth 1 ! -name v ! -name latest ! -name download ! -name '*.bak.*' -exec mv {} "$ROOT/site.bak.$TS/" \;
  prune "$ROOT/site.bak"
fi
cp -a "$STAGE/site/." "$ROOT/"
cp -a "$STAGE/LICENSE" "$ROOT/LICENSE"

# 3) 다운로드 (dist/packages → download/) ---------------------------------------
if [ -d "$STAGE/dist/packages" ]; then
  mkdir -p "$ROOT/download"
  moved=0
  for f in "$STAGE"/dist/packages/*; do
    b="$(basename "$f")"
    if [ -e "$ROOT/download/$b" ]; then
      [ "$moved" = "0" ] && { echo "-- 같은 이름의 기존 패키지 → download.bak.$TS/"; mkdir -p "$ROOT/download.bak.$TS"; moved=1; }
      mv "$ROOT/download/$b" "$ROOT/download.bak.$TS/"
    fi
  done
  [ "$moved" = "1" ] && prune "$ROOT/download.bak"
  cp -a "$STAGE/dist/packages/." "$ROOT/download/"
  echo "-- download/: $(ls "$ROOT/download" | tr '\n' ' ')"
else
  echo "-- dist/packages 없음 → download/ 유지"
fi

# 4) 심링크 -------------------------------------------------------------------
if [ "$NO_LATEST" = "0" ]; then
  echo "-- latest → v/$VER"
  ln -sfn "v/$VER" "$ROOT/latest"
else
  echo "-- --no-latest: latest 유지 ($(readlink "$ROOT/latest" 2>/dev/null || echo 없음))"
fi

# 5) 권한 ---------------------------------------------------------------------
chown -R nginx:nginx "$ROOT"
find "$ROOT" -type d -exec chmod 755 {} +
find "$ROOT" -type f -exec chmod 644 {} +

# 5-1) SELinux 컨텍스트 복구 (Rocky/RHEL Enforcing 필수) --------------------------
# ⚠ 2026-09-09 1.000 배포 사고: 소유자·권한이 정상인데 전 경로가 403 이었다.
#    /tmp 에서 푼 파일이 `user_tmp_t` 컨텍스트를 그대로 달고 와 nginx 가 못 읽은 것
#    (정상은 `httpd_sys_content_t`). restorecon 으로 기본 컨텍스트를 다시 입힌다.
if command -v restorecon >/dev/null 2>&1; then
  echo "-- SELinux 컨텍스트 복구: restorecon -RF $ROOT"
  restorecon -RF "$ROOT" || echo "   ⚠ restorecon 실패 — 403 이 나면 수동으로 'sudo restorecon -RF $ROOT' 를 실행할 것"
else
  echo "   (restorecon 없음 — SELinux 미사용 환경으로 보고 건너뜀)"
fi

# 6) 요약 ---------------------------------------------------------------------
echo "-- 결과"
ls -la "$ROOT" | sed 's/^/   /'
echo "   SELinux 컨텍스트: $(ls -Zd "$ROOT" 2>/dev/null || echo '확인 불가')"   # httpd_sys_content_t 여야 nginx 가 읽는다
echo "   v/$VER: static $(ls "$ROOT/v/$VER/static" | wc -l) · web $(ls "$ROOT/v/$VER/web" | grep -c woff2) · subset $(ls "$ROOT/v/$VER/web/subset" 2>/dev/null | wc -l) · css $(ls "$ROOT/v/$VER/css" | wc -l)"
du -sh "$ROOT/v/$VER" "$ROOT/download" 2>/dev/null | sed 's/^/   /'
if command -v nginx >/dev/null 2>&1 && [ -f /etc/nginx/conf.d/font.conf ]; then
  nginx -t 2>&1 | sed 's/^/   /' || true
else
  echo "   ⚠ /etc/nginx/conf.d/font.conf 가 없다 — 팀장이 deploy/README.md §2 로 nginx 를 먼저 준비"
fi
echo "== 완료 =="
