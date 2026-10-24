# deploy/ — font.jennysoft.co.kr 배포 절차

> 도메인 **`font.jennysoft.co.kr`** → 175.127.49.246 (사용자 등록, 2026-09-06 `nslookup` 실측 확인). 소개 홈페이지 + 폰트 CDN + 다운로드를 공개한다(AGENTS §8 2026-09-06).
> **서버 작업(nginx conf 설치·인증서)은 팀장이 직접**, 파일 배포(`deploy.sh`)는 QA RELEASE OK 후 팀장이 실행. release 는 파일만 준비하고 **실행하지 않았다.**
> 서버: `ssh debc-dev` (= <user>@<server> -p <ssh-port>), Rocky Linux 10, nginx 계정 `nginx`, 인증서는 acme.sh TLS-ALPN(latinbeat/qaudio/qpinball 패턴).

| 파일 | 역할 |
|---|---|
| `nginx-font.conf` | `/etc/nginx/conf.d/font.conf` — qaudio.conf 골격. `/v/` immutable 1년 + CORS + `font/woff2`·`font/ttf` MIME, `/latest/`·`/download/` 5분 + CORS, zip 은 `application/zip` + `Content-Disposition: attachment`, gzip 은 html/css/js/json 만 |
| `deploy.sh` | 로컬 → 서버 전송 + `remote-install.sh` 실행 (`DRY=1` 미리보기, `NO_LATEST=1`, `SITE_SRC=`, `SITE_EXCLUDE=`) |
| `remote-install.sh` | 서버에서 `/var/www/font` 배치: `v/<ver>`·홈페이지·`download/`·`latest`, `.bak.<ts>` 백업 3개 유지 |

## 0. 경로 매핑

| 로컬 | 서버 `/var/www/font/` | URL | 캐시 |
|---|---|---|---|
| `site/` (font-site 소유; 빌드 산출 폴더가 다르면 `SITE_SRC=site/dist`) | 루트 (`index.html` …) | `https://font.jennysoft.co.kr/` | html no-cache, 에셋 1일 |

**홈페이지는 전부 올리지 않는다.** `deploy.sh` 의 `SITE_EXCLUDE`(스크립트 상단 변수)가 개발용 파일을 제외한다 — 렌더 원본 `*.template.html`(이중 중괄호 치환 전 원본), 로컬 스크립트 `preview.py`·`check_site.py`, 개발 문서 `site/README.md`, `__pycache__/`, 임시 `_measure_tmp.html`. 8차 기준 **26개 중 6개 제외 → 20개 전송**(`DRY=1` 실행 시 전송 대상 목록이 출력된다).
⚠ `google85364fe7cc780e8d.html`(구글 소유확인)·`robots.txt`·`sitemap.xml`·`favicon.ico`·`assets/` 는 SEO 색인에 필요하므로 **절대 제외 목록에 넣지 않는다**(`docs/SEO_REGISTRATION.md`). `test.html` 은 QA 공용이라 올리되 `robots.txt` 가 색인을 막는다.
| `dist/{static,variable,web,css}` + `LICENSE`·`THIRD-PARTY-NOTICES.md`·`README.md`·`CHANGELOG.md` | `v/1.000/` | `https://font.jennysoft.co.kr/v/1.000/css/jennysans.css` | immutable 1년 + CORS `*` |
| (심링크) | `latest -> v/1.000` | `https://font.jennysoft.co.kr/latest/css/jennysans.css` | 5분 |
| `dist/packages/` (`tools/package.py` 산출: zip 3종 + `SHA256SUMS.txt`) | `download/` | `https://font.jennysoft.co.kr/download/JennySans-1.000-desktop.zip` | 5분, 첨부 다운로드 |

- 홈페이지가 `../dist/…` 같은 저장소 상대경로를 쓰면 서버에서는 동작하지 않는다 — `/latest/css/…` 또는 `/v/1.000/css/…` 절대경로를 쓴다(font-site). 저장소용 `site/test.html` 을 서버에서도 쓰려면 `sudo ln -sfn latest /var/www/font/dist` 한 줄로 `/dist/` 별칭을 만들 수 있다(선택).

## 1. 전제 조건

| # | 조건 | 상태(2026-09-06) | 담당 |
|---|---|---|---|
| 1 | DNS A 레코드 `font.jennysoft.co.kr → 175.127.49.246` | **완료**(실측) | 사용자 |
| 2 | QA RELEASE OK + `dist/` 최종 빌드 + `dist/packages/` | 5차 빌드(빌더 자체 점검 PASS)·패키지 09:23 재생성 완료·QA 진행 중 | qa·builder·font-site |
| 3 | 서버 nginx conf + 인증서 | 미완 | **팀장(서버 직접)** — §2 |
| 4 | 파일 배포 | 미완 | **팀장** — §3 |

## 1-1. 본배포 순서 (팀장, QA RELEASE OK 후) — 팀장 결정 2026-09-06

`font-bootstrap.sh` 의 인라인 conf 는 부트스트랩용이고, **본배포 때는 더 완전한 `deploy/nginx-font.conf` 로 서버 conf 를 교체**한다.

| 순서 | 할 일 | 명령 |
|---|---|---|
| ① | nginx conf 교체 → 문법 검사 → reload | `scp deploy/nginx-font.conf debc-dev:/tmp/font.conf && ssh debc-dev "sudo cp /etc/nginx/conf.d/font.conf /etc/nginx/conf.d/font.conf.bak.\$(date +%Y%m%d-%H%M%S); sudo cp /tmp/font.conf /etc/nginx/conf.d/font.conf && sudo nginx -t && sudo systemctl reload nginx"` |
| ② | 파일 배포(홈페이지·`/v/1.000/`·`/download/`·`latest`) | `DRY=1 bash deploy/deploy.sh 1.000` 로 미리보기 — **홈페이지 전송 파일이 20개(26 중 6 제외)이고 `google…html`·`robots.txt`·`sitemap.xml`·`assets/` 가 목록에 있는지 확인** — 후 `bash deploy/deploy.sh 1.000` (§3) |
| ③ | 운영 URL 로 홈페이지·다운로드·CDN 헤더 검사(font-site 스크립트) | `PYTHONUTF8=1 python site/check_site.py --url https://font.jennysoft.co.kr` → ALL PASS. 그 다음 §4 의 브라우저·타 오리진 확인 |

- ①에서 `nginx -t` 가 실패하면 백업 conf 로 되돌린다: `ssh debc-dev "sudo cp /etc/nginx/conf.d/font.conf.bak.<ts> /etc/nginx/conf.d/font.conf && sudo nginx -t && sudo systemctl reload nginx"`.
- 같은 버전을 다시 배포하면 `remote-install.sh` 가 `v/1.000.bak.<ts>` 로 백업하지만, 공개 뒤에는 버전 경로 내용을 바꾸지 않는다(`docs/DISTRIBUTION.md` §3).

## 2. 서버 준비 — 팀장 직접 (`deploy/font-bootstrap.sh`)
팀장이 작성한 **`deploy/font-bootstrap.sh`**(root 로 1회 실행)가 정본이다: 디렉터리(`/var/www/font/{v,download}` + 임시 index.html, `chown nginx:nginx`) → 80 임시 블록 → acme.sh `--issue --alpn --server letsencrypt --keylength ec-256`(nginx 일시 중단) → `/etc/pki/tls/{certs/font.crt,private/font.key}` → 최종 conf `/etc/nginx/conf.d/font.conf`(스크립트 안에 인라인) → `/usr/local/sbin/renew-font-cert.sh` + cron `7 5 * * *`.
```bash
scp deploy/font-bootstrap.sh debc-dev:/tmp/
ssh debc-dev "sudo bash /tmp/font-bootstrap.sh"
```
- 부트스트랩의 인라인 conf 와 `deploy/nginx-font.conf` 의 차이(2026-09-06 대조): `nginx-font.conf` 쪽에만 있는 것 — OPTIONS 프리플라이트 204, `Access-Control-Allow-Methods`·`Timing-Allow-Origin`·`X-Content-Type-Options`, `.bak.<ts>`·숨김 파일 404, 폰트·zip `gzip off` 명시, `.html` no-cache(부트스트랩은 홈페이지 전체 5분), `/latest/` `must-revalidate`, `/v/` 의 LICENSE·md MIME. 필요하면 부트스트랩 실행 후 `scp deploy/nginx-font.conf debc-dev:/tmp/font.conf && ssh debc-dev "sudo cp /tmp/font.conf /etc/nginx/conf.d/font.conf && sudo nginx -t && sudo systemctl reload nginx"` 로 교체(팀장 판단).
- `remote-install.sh` 는 부트스트랩과 같은 `nginx:nginx` 소유권을 유지한다.

## 3. 파일 배포 — 팀장 (QA RELEASE OK 후)
```bash
cd <repo>
DRY=1 bash deploy/deploy.sh 1.000     # 할 일 미리보기(전송·변경 없음)
bash deploy/deploy.sh 1.000           # 실제 배포
```
- 결과: `/var/www/font/v/1.000/`, `latest`, `download/`, 루트 홈페이지 + `LICENSE`.
- 같은 버전 재배포 시 기존본은 `v/1.000.bak.<ts>` 로(최근 3개). **배포된 버전 경로의 파일 내용을 바꾸는 것은 원칙 금지**(immutable 캐시) — 고칠 것은 새 버전으로.
- 새 버전 사전 배포(latest 유지): `NO_LATEST=1 bash deploy/deploy.sh 1.001`, 검증 후 `ssh debc-dev "sudo ln -sfn v/1.001 /var/www/font/latest"`.
- `dist/packages/` 가 없으면 `download/` 는 건드리지 않는다(경고만).

## 4. 검증 (curl 200 은 검증이 아니다)
```bash
curl -sI -H "Origin: https://example.com" https://font.jennysoft.co.kr/v/1.000/web/JennySans-Regular.woff2 | grep -i -E "HTTP/|access-control|content-type|cache-control"
#  기대: HTTP/2 200 · content-type: font/woff2 · access-control-allow-origin: * · cache-control: public, max-age=31536000, immutable
curl -sI https://font.jennysoft.co.kr/latest/css/jennysans.css | grep -i -E "HTTP/|content-type|cache-control"
#  기대: text/css · max-age=300
curl -sI https://font.jennysoft.co.kr/download/JennySans-1.000-desktop.zip | grep -i -E "HTTP/|content-type|content-disposition|cache-control"
#  기대: application/zip · content-disposition: attachment
curl -sI -H "Accept-Encoding: gzip, br" https://font.jennysoft.co.kr/v/1.000/web/JennySans-Regular.woff2 | grep -i content-encoding
#  기대: 출력 없음(WOFF2 는 압축하지 않음)
```
그 다음 **브라우저**:
1. `https://font.jennysoft.co.kr/` 홈페이지 — 강력 새로고침, 다운로드 버튼이 실제 zip 을 받는지(파일 크기·SHA256SUMS 대조).
2. **다른 오리진**(예: `https://qaudio.jennysoft.co.kr/` 에 임시 HTML, 또는 로컬 `python -m http.server 8765`)에서 `<link rel="stylesheet" href="https://font.jennysoft.co.kr/v/1.000/css/jennysans-dynamic-subset.css">` 를 쓰는 페이지가 JennySans 로 그려지는지 — DevTools Network 폰트 요청 200 + `access-control-allow-origin`, Console 에 CORS 오류 없음. 스크린샷 `docs/qa/shots/`.
3. `document.fonts.check('400 16px "JennySans"')` → `true`.

## 4-1. 403 Forbidden 이 나면 — SELinux 컨텍스트 (2026-09-09 실제 사고)

**증상**: 배포 직후 홈페이지·`/v/`·`/download/` **모든 경로가 403**. 파일은 다 올라가 있고 소유자 `nginx:nginx`·권한 755/644 도 정상.

**원인**: Rocky Linux 는 **SELinux Enforcing** 이다. `/tmp` 에서 tgz 를 풀어 `/var/www/font` 로 복사하면 파일이 **`user_tmp_t`** 컨텍스트를 그대로 달고 온다. nginx 는 `httpd_sys_content_t` 만 읽을 수 있어 커널이 차단한다 — 권한(owner/mode)만 봐서는 절대 안 보인다.

**진단** (위에서 아래로):
```bash
ssh debc-dev "getenforce"                                   # Enforcing 이면 후보
ssh debc-dev "ls -Zd /var/www/font /var/www/font/index.html"  # user_tmp_t 면 확정 (정상: httpd_sys_content_t)
ssh debc-dev "sudo tail -20 /var/log/nginx/font.error.log"    # 'Permission denied' + open() 실패 경로
```

**해결**:
```bash
ssh debc-dev "sudo restorecon -RF /var/www/font && ls -Zd /var/www/font"
```

`deploy/remote-install.sh` 는 5-1 단계에서 이 `restorecon` 을 **자동으로 실행**하고, 6단계 요약에 `ls -Zd` 결과를 찍는다(1.000 사고 후 추가). `restorecon` 이 없는 환경(SELinux 미사용)은 건너뛴다.

> **확인은 `curl` 200 이 아니라 실제 응답 코드로 한다.** `curl -sI <url> | head -1` 로 **HTTP 상태줄을 직접 읽고**, 이어서 브라우저에서 홈페이지가 그려지는지 본다(§4). 403 은 조용히 나지 않고 상태줄에만 보인다.

## 5. 롤백
```bash
ssh debc-dev "ls -la /var/www/font /var/www/font/v"
ssh debc-dev "sudo ln -sfn v/<이전버전> /var/www/font/latest"                                   # latest 만 되돌리기
ssh debc-dev "sudo rm -rf /var/www/font/v/1.000 && sudo mv /var/www/font/v/1.000.bak.<ts> /var/www/font/v/1.000"   # 같은 버전 재배포 되돌리기
ssh debc-dev "sudo mv /var/www/font/site.bak.<ts>/* /var/www/font/"                             # 홈페이지 되돌리기(새 파일은 먼저 치움)
ssh debc-dev "sudo cp -a /var/www/font/download.bak.<ts>/. /var/www/font/download/"            # 패키지 되돌리기
```

## 6. 하지 않는 것
- 서버에서 폰트를 빌드하지 않는다(빌드는 로컬 `tools/`, 서버는 정적 서빙만).
- `latest` 를 사내 운영 앱의 기본 경로로 쓰지 않는다(고정 버전 `/v/1.000/`).
- release 팀원은 인증서·DNS·서버 반영·npm publish·git push 를 실행하지 않는다(팀장·사용자 승인).
