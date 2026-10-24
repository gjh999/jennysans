#!/bin/bash
# font.jennysoft.co.kr 서버 부트스트랩 (qaudio 패턴). root 로 실행: sudo bash /tmp/font-bootstrap.sh
set -euo pipefail
DOMAIN=font.jennysoft.co.kr
ROOT=/var/www/font
CRT=/etc/pki/tls/certs/font.crt
KEY=/etc/pki/tls/private/font.key
CONF=/etc/nginx/conf.d/font.conf
ACME=/home/jenny/.acme.sh/acme.sh
ACME_HOME=/root/.acme.sh
TS=$(date +%Y%m%d-%H%M%S)

echo "== [1] 디렉터리"
mkdir -p "$ROOT/v" "$ROOT/download"
if [ ! -f "$ROOT/index.html" ]; then
cat > "$ROOT/index.html" <<'HTML'
<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JennySans 제니산스 — 준비 중</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:system-ui,sans-serif;background:#fafafa;color:#111}
main{text-align:center;padding:2rem}h1{font-size:2.5rem;margin:0 0 .5rem}p{color:#555}</style></head>
<body><main><h1>JennySans · 제니산스</h1><p>제니소프트 범용 다국어 고딕 폰트 — 홈페이지와 다운로드를 준비하고 있습니다.</p></main></body></html>
HTML
fi
chown -R nginx:nginx "$ROOT"
ls -la "$ROOT"

echo "== [2] nginx 80 임시 블록"
[ -f "$CONF" ] && cp -a "$CONF" "$CONF.bak.$TS"
cat > "$CONF" <<EOF
# JennySans font.jennysoft.co.kr — 임시(80 only, 인증서 발급 전)
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    location ^~ /.well-known/acme-challenge/ { root /var/www/html; }
    location / { root $ROOT; index index.html; }
}
EOF
nginx -t && systemctl reload nginx

echo "== [3] 인증서 발급 (TLS-ALPN, nginx 일시 중단)"
if [ ! -f "$CRT" ]; then
  systemctl stop nginx
  set +e
  $ACME --issue --alpn -d "$DOMAIN" --server letsencrypt --keylength ec-256 --home "$ACME_HOME" >>/var/log/acme-renew.log 2>&1
  RC=$?
  set -e
  systemctl start nginx
  if [ $RC -ne 0 ]; then echo "acme issue FAILED rc=$RC"; tail -30 /var/log/acme-renew.log; exit 1; fi
  $ACME --install-cert -d "$DOMAIN" --ecc --home "$ACME_HOME" --fullchain-file "$CRT" --key-file "$KEY" >>/var/log/acme-renew.log 2>&1
  chmod 600 "$KEY"
fi
openssl x509 -noout -subject -issuer -enddate -in "$CRT"

echo "== [4] nginx 최종 설정"
cat > "$CONF" <<EOF
# JennySans 「제니산스」 폰트 소개·다운로드·CDN — $DOMAIN (server: 175.127.49.246 / debc-dev)
# 파일: $CONF   원본: <repo>\\deploy\\nginx-font.conf
# 인증서: acme.sh --alpn --server letsencrypt (TLS-ALPN-01, 외부 80 미개방) → /usr/local/sbin/renew-font-cert.sh (cron 7 5 * * *)
# 경로: /            홈페이지(site/)          /v/<ver>/   불변 CDN(폰트·CSS)   /latest/ → v/<ver> 심링크   /download/  zip

server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    location ^~ /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://\$host\$request_uri; }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name $DOMAIN;

    ssl_certificate     $CRT;
    ssl_certificate_key $KEY;
    include snippets/ssl-common.conf;

    root $ROOT;
    index index.html;
    charset utf-8;
    client_max_body_size 1m;

    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml text/plain;
    gzip_min_length 1024;
    # woff2·zip 은 이미 압축돼 있어 gzip 대상이 아니다(gzip_types 에 없음)

    # ── 버전 고정 CDN: 1년 불변 캐시 + CORS(크로스도메인 폰트 필수) ──
    location ^~ /v/ {
        add_header Access-Control-Allow-Origin "*" always;
        add_header Cache-Control "public, max-age=31536000, immutable" always;
        location ~* \\.(woff2|woff|ttf|otf)\$ {
            types { font/woff2 woff2; font/woff woff; font/ttf ttf; font/otf otf; }
            add_header Access-Control-Allow-Origin "*" always;
            add_header Cache-Control "public, max-age=31536000, immutable" always;
        }
    }
    # ── latest 심링크: 5분 캐시 + CORS ──
    location ^~ /latest/ {
        add_header Access-Control-Allow-Origin "*" always;
        add_header Cache-Control "public, max-age=300" always;
        location ~* \\.(woff2|woff|ttf|otf)\$ {
            types { font/woff2 woff2; font/woff woff; font/ttf ttf; font/otf otf; }
            add_header Access-Control-Allow-Origin "*" always;
            add_header Cache-Control "public, max-age=300" always;
        }
    }
    # ── 다운로드 zip ──
    location ^~ /download/ {
        add_header Cache-Control "public, max-age=300" always;
        location ~* \\.zip\$ {
            types { application/zip zip; }
            add_header Content-Disposition "attachment" always;
            add_header Cache-Control "public, max-age=300" always;
        }
    }
    # ── 홈페이지 ──
    location / {
        try_files \$uri \$uri/ =404;
        add_header Cache-Control "public, max-age=300";
    }
}
EOF
nginx -t && systemctl reload nginx

echo "== [5] 갱신 스크립트·cron"
cat > /usr/local/sbin/renew-font-cert.sh <<EOF
#!/bin/bash
# $DOMAIN 인증서 갱신 — 만료 30일 이내일 때만 nginx 를 잠깐 멈추고 ALPN 갱신(renew-qaudio-cert.sh 와 동일 패턴)
CERT=$CRT
if openssl x509 -checkend \$((30*86400)) -noout -in "\$CERT" >/dev/null 2>&1; then exit 0; fi
logger -t renew-font-cert '인증서 갱신 시작(nginx 일시 중단)'
systemctl stop nginx
$ACME --cron --home $ACME_HOME >>/var/log/acme-renew.log 2>&1
systemctl start nginx
logger -t renew-font-cert '인증서 갱신 완료(nginx 재시작)'
EOF
chmod 755 /usr/local/sbin/renew-font-cert.sh
( crontab -l 2>/dev/null | grep -v renew-font-cert; echo "7 5 * * * /usr/local/sbin/renew-font-cert.sh" ) | crontab -
crontab -l | grep renew-font-cert

echo "== [6] 확인"
systemctl is-active nginx
curl -sI --max-time 10 "https://$DOMAIN/" | head -5
echo "DONE"
