# JennySans 배포·버전 정책 (font-release 소유)

> 상위 규칙: `AGENTS.md` §7(이름·버전)·§8(결정), 스펙 `docs/spec/05-web.md` §6(서버 헤더)·`06-license.md`.
> **외부 전파(git push · GitHub Release · npm publish · DNS · 서버 반영)는 전부 사용자 승인 후 실행한다.** §5 실행 대기 목록이 그 단위다.
> 작성 2026-09-06 · **실측값 갱신 2026-09-09(8차 빌드 확정본)**. 실측값은 `build/BUILD-REPORT.md`(8차 2026-09-09, 빌더 자체 점검 PASS · fontbakery FAIL 0)와 `dist/packages/index.json`(2026-09-09 10:10 재생성) 기준. KB = 1,000 bytes.

## 1. 버전 정책

### 1-1. 표기
- 폰트 버전은 관례대로 `X.YZZ`(`name ID 5` = `Version 1.000 (based on Pretendard 1.3.9; Noto Sans KR 2.004)`, `head.fontRevision` = 1.000). 첫 릴리스 **1.000**.
- npm 은 SemVer 만 허용하므로 **`X.YZZ` ↔ `X.Y.ZZ`** 로 1:1 대응한다. 같은 규칙을 git 태그에도 쓴다.

| 폰트 버전(name ID 5) | npm / git 태그 | 서버 경로 | 비고 |
|---|---|---|---|
| 1.000 | `1.0.0` / `v1.0.0` | `/v/1.000/` | 첫 릴리스 |
| 1.001 | `1.0.1` / `v1.0.1` | `/v/1.001/` | 패치 |
| 1.100 | `1.1.0` / `v1.1.0` | `/v/1.100/` | 마이너 |
| 2.000 | `2.0.0` / `v2.0.0` | `/v/2.000/` | 메이저 |

> **팀장 확인 요청**: `docs/ROADMAP.md` P6 는 "태그 1.000" 으로 적혀 있다. jsDelivr GitHub 엔드포인트는 태그 문자열을 그대로 받으므로 `v1.000` 도 동작하지만, npm 버전(`1.0.0`)과 URL 이 어긋나 혼동된다. 이 문서는 **`v1.0.0`** 을 기준으로 쓴다. `v1.000` 으로 결정되면 §2·§5 의 URL·명령에서 태그만 치환.

### 1-2. 무엇을 올리면 어느 자리가 오르나 (SemVer 대응)

| 변경 | 자리 | 이유 |
|---|---|---|
| **메트릭 변경** — UPM, typo/hhea/win ascender·descender·lineGap, 한글 음절 advance, 라틴 advance/커닝의 대량 변경, 글립 외곽선의 시각적 변경 | **major** (1.x → 2.000) | 줄 높이·줄바꿈 위치가 바뀌어 기존 문서·화면 레이아웃이 깨진다 |
| **글립 추가**(문자 범위 확장, 새 OpenType 기능, 새 웨이트, 새 형식(OTF) 추가, 웹 슬라이스 재분할) | **minor** (1.000 → 1.100) | 기존 텍스트 렌더는 그대로, 새 글자·기능만 늘어남 |
| 버그 수정(개별 글립 오류, 메타데이터·name/STAT 수정, CSS 오류, 힌팅), 문서·패키징만 변경 | **patch** (1.000 → 1.001) | |
| 글립 **삭제**·이름 변경 | major | 호환성 파괴 |

- **파일명에 버전을 넣지 않는다**(`JennySans-Bold.woff2`). 버전은 경로(`/v/1.000/`)·태그·패키지 버전으로 구분한다(스펙 01 §5).
- 한 릴리스 안의 모든 파일(정적 9·변수·WOFF2·CSS)은 **같은 버전 문자열**을 가진다(fontbakery `equal_font_versions`).
- `CHANGELOG.md` 에 항목이 없으면 릴리스하지 않는다.

## 2. 배포 채널과 URL

CSS 안의 `src: url("../web/…")` 은 상대경로라 세 채널 모두에서 그대로 동작한다(`dist/` 구조 유지가 조건).

| 채널 | URL 예(정적 CSS) | 갱신 주체 | 캐시 |
|---|---|---|---|
| **jsDelivr (GitHub 태그)** | `https://cdn.jsdelivr.net/gh/gjh999/jennysans@v1.0.0/dist/css/jennysans.css` | git 태그 push 만으로 즉시(공개 저장소 필수) | 고정 버전 = 영구(jsDelivr: 1년 헤더 + S3 영구 보관) |
| **jsDelivr (npm)** | `https://cdn.jsdelivr.net/npm/jennysans@1.0.0/dist/css/jennysans.css` | `npm publish` | 동일. `@1` `@1.0` 같은 범위 지정은 7일 캐시(운영 비권장) |
| **자체 CDN** | `https://font.jennysoft.co.kr/v/1.000/css/jennysans.css` · `https://font.jennysoft.co.kr/latest/css/jennysans.css` | `deploy/deploy.sh` | `/v/…` immutable 1년, `/latest/` 5분 |

- 분할 CSS: 위 경로에서 `jennysans.css` → `jennysans-dynamic-subset.css`, 변수: `jennysans-variable.css`.
- unpkg 도 `https://unpkg.com/jennysans@1.0.0/dist/css/jennysans.css` 로 동작한다(`package.json` `unpkg` 필드).
- jsDelivr 제한(공식 README, 2026-09-06 확인): **패키지 150 MB 초과 또는(GitHub 의 경우) 단일 파일 20 MB 초과는 서빙하지 않음.** HTML 은 `text/plain` 으로 서빙(스페시먼 페이지는 jsDelivr 로 못 봄 → 자체 서버).
- 선례: Pretendard npm 1.3.9 = unpacked 97,653,151 bytes · 1,826 파일, jsDelivr 로 서빙 중(2026-09-06 레지스트리 조회). JennySans npm 패키지 예상 크기(**8차 빌드 실측**, `dist/css` + `dist/web` + LICENSE·THIRD-PARTY·README): **23,734,705 bytes ≈ 23.7 MB**(`dist/web` 23,167,820 B: 전체본 9 + 변수 + 분할 990 파일, `dist/css` 520,115 B) — 150 MB 제한 내. `dist/` 전체 129,862,207 B = 폰트·CSS 54,160,583 B(정적 TTF 23,462,992 + 변수 7,009,656 + 웹 23,167,820 + CSS 520,115) + `dist/packages/` 75,701,624 B(zip 4종 + SHA256SUMS + index.json — npm `files` 에 포함되지 않음). 최종은 `npm pack --dry-run` 으로 재확인.
- **jsDelivr 는 우리 서버가 죽어도 되지만, 자체 CDN 은 DNS·인증서·서버 운영이 필요**하다. 사내 앱 기본값은 자체 CDN(`font.jennysoft.co.kr`), 외부 공개 문서에는 jsDelivr(npm)를 함께 안내.

## 3. 캐시 무효화

- **버전 경로 밑의 파일은 절대 내용을 바꾸지 않는다.** `immutable` 이라 브라우저·CDN 이 재검증하지 않는다. 고칠 것이 있으면 **새 버전**(1.001)으로 낸다. 서버 `deploy.sh` 는 같은 버전을 다시 올리면 기존 디렉터리를 `.bak.<ts>` 로 백업하지만, 이미 배포된 버전의 재배포는 원칙적으로 금지(긴급 시 팀장 결정).
- `latest/` 별칭과 `download/` 는 `Cache-Control: max-age=300, must-revalidate` — 새 버전으로 심링크를 바꾸거나 패키지를 교체하면 5분 내 반영. 사내 앱도 운영에서는 **고정 버전 경로**를 쓰고 `latest` 는 데모·QA 용으로만.
- jsDelivr: 고정 버전은 무효화 불필요(불변). 범위/`latest` 는 7일 캐시, 필요 시 purge API `https://purge.jsdelivr.net/npm/jennysans@1.0.0/dist/css/jennysans.css`(파일 단위) — 사용자 승인 후.
- 분할 CSS 가 참조하는 슬라이스 파일 집합이 바뀌면(재분할) 반드시 minor 이상 버전 상승(구 CSS 가 캐시된 브라우저가 새 슬라이스 파일을 요청하는 불일치 방지).

## 4. 릴리스 체크리스트 (순서 고정)

| # | 단계 | 담당 | 명령/산출 | 승인 |
|---|---|---|---|---|
| 1 | ✅ **완료 2026-09-09** — QA 판정 **RELEASE OK**(조건 없음·승인 예외 0), `docs/qa/QA-REPORT-1.000.md` | qa → 팀장 | | 팀장 |
| 2 | ✅ **완료 2026-09-09**(8차 빌드 기준 재기입) — 문서 실측치 대조 | release | 미기입 표식(이중 중괄호 TBD) 검사: `grep -rnE '\{\{' README.md CHANGELOG.md THIRD-PARTY-NOTICES.md package.json docs/INSTALL.md docs/DISTRIBUTION.md docs/ADOPTION.md docs/OFL-FAQ-ko.md deploy` → 0건 | |
| 3 | ✅ **완료** — 라이선스 게이트(LICENSE 첫 줄·원본 문구·OFL 본문 SHA `ebc10907…`, THIRD-PARTY ↔ AGENTS §5-1 ↔ MANIFEST 3자 일치) | release·qa | `docs/spec/06-license.md` §8 | |
| 4 | 패키지 점검 — `npm pack --dry-run`(파일 목록·크기), `bash -n deploy/*.sh`, `site/test.html` 4 모드(`?mode=static|variable|subset|variable-subset`) 스크린샷 | release·qa | | |
| 5 | ✅ **완료 2026-09-09** — 로컬 커밋(`dist/` 포함) | 팀장 | `git add -A && git commit -m "release: JennySans 1.000"` | 팀장 |
| 6 | ✅ **완료 2026-09-09** — 태그 `v1.0.0`(푸시는 8번에서) | 팀장 | `git tag -a v1.0.0 -m "JennySans 1.000"` | 팀장 |
| 7 | ✅ **완료 2026-09-09 10:27** — zip 4종 + `SHA256SUMS.txt` + `index.json` 최종 재생성 → 서버 `/download/` 배포본과 SHA 일치 확인 | font-site | `python tools/package.py --render-site` | |
| 8 | ⬜ **남음** — GitHub 저장소 생성·push·태그 push | release | §5 A·B·C | **사용자 승인 대기** |
| 9 | ⬜ **남음** — GitHub Release 생성 + 에셋 업로드 | release | §5 D | **사용자 승인 대기** |
| 10 | ⬜ **남음** — npm publish | release | §5 E | **사용자 승인 대기** |
| 11 | DNS A 레코드 `font.jennysoft.co.kr → 175.127.49.246` | 사용자 | §5 F — **완료**(2026-09-06 실측) | 완료 |
| 12 | ✅ **완료 2026-09-09 10:28** — nginx·인증서 + `deploy.sh 1.000` 배포. **배포 직후 전 경로 403** → 원인 SELinux 컨텍스트(`user_tmp_t`), `sudo restorecon -RF /var/www/font` 로 해소(`deploy/README.md` §4-1, 이후 `remote-install.sh` 가 자동 수행) | **팀장(서버 직접)** | `deploy/README.md` §2·§3 | 팀장 |
| 13 | ✅ **완료 2026-09-09** — 실브라우저 검증 **ALL PASS**(홈페이지·다운로드 zip SHA-256 원본 대조 일치·CORS·캐시 헤더) | release·qa | §5 I | 팀장 |
| 14 | `docs/PROGRESS.md`·ROADMAP P7 갱신, 사내 적용 파일럿(P8, `docs/ADOPTION.md`) | 팀장 | | |

### 4-1. 릴리스 순서 — 1.000 먼저, 곧이어 1.100 (팀장 결정 `AGENTS.md` §8 2026-09-08)

**1.000 은 한자를 기다리지 않고 QA 통과 즉시 공개한다.** 사이트 개통·SEO 색인이 빨리 시작될수록 좋고, 버전 경로(`/v/<ver>/`)와 `latest` 심링크가 있어 이중 릴리스 비용이 사실상 없기 때문이다.

| 시점 | 하는 일 | `latest` 가 가리키는 곳 |
|---|---|---|
| ① QA RELEASE OK 직후 | §4 체크리스트 1~14 를 **1.000** 으로 완주 → `/v/1.000/` 배포, 홈페이지·다운로드 공개, 검색엔진 등록(`docs/SEO_REGISTRATION.md`) | `/v/1.000/` |
| ② 곧바로 | **1.100**(한자 4,620 + 베트남어 92 + 확장 키릴 18) 빌드 → QA → 태그 `v1.1.0` → `/v/1.100/` 배포 | 아직 `/v/1.000/` |
| ③ 1.100 검증 완료 후 | `latest` 심링크를 **1.100 으로 이동**, `/download/` zip 교체, npm publish 1.1.0, GitHub Release v1.1.0 | `/v/1.100/` |

- **`/v/1.000/` 는 지우지 않는다.** `immutable` 로 캐시된 기존 사용자가 계속 쓴다(§3). 1.100 으로 옮기는 것은 `latest` 와 `/download/` 뿐이다.
- 1.100 은 **글립 추가만** 있는 minor 이므로(§1-2) 메트릭·줄바꿈이 바뀌지 않는다 — 기존 페이지가 `latest` 를 쓰고 있어도 레이아웃이 깨지지 않는다. 그래도 운영 앱은 고정 버전 경로를 쓰는 것이 원칙이다.
- `/download/` 의 zip 파일명에는 버전이 들어가므로(`JennySans-1.100-desktop.zip`) 교체 시 홈페이지 링크(`dist/packages/index.json` → `site/`)도 함께 갱신된다(font-site `tools/package.py`).

## 5. 실행 대기 목록 — 사용자 승인 필요 (명령 단위, 위에서 아래 순서)

> 전제: 로컬 git 2.55 있음(`C:\Program Files\Git`), `gh` CLI 없음 → GitHub API 는 `git credential fill` 의 저장 토큰으로 호출(값 출력 금지 — LatinBeat 선례). Node 는 `D:\dev\node`(PATH 미등록). 아래 명령은 **준비만 된 상태**이며 실행하지 않았다.

### A. GitHub 저장소 생성 (`gjh999/jennysans`, public)
```bash
# 토큰을 변수에만 담고 출력하지 않는다
TOKEN=$(printf 'protocol=https\nhost=github.com\n' | git credential fill | sed -n 's/^password=//p')
curl -sS -X POST https://api.github.com/user/repos \
  -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" \
  -d '{"name":"jennysans","description":"JennySans (제니산스) — general-purpose Korean & English (Latin) sans-serif font family, SIL OFL 1.1","homepage":"https://font.jennysoft.co.kr","private":false,"has_issues":true,"has_wiki":false}'
# 또는 웹 UI: https://github.com/new (이름 jennysans, Public, README/LICENSE 는 추가하지 않음 — 로컬 것 사용)
```
- 공개 전 점검(전역 규칙): 저장소 루트가 `<repo>` 로 한정되는지, `.gitignore` 로 `sources/`·`build/` 제외, 스테이징 파일에 비밀값 없음(`git diff --cached --stat`, 토큰·키 패턴 grep). 이 프로젝트에는 비밀값이 원칙적으로 없다.

### B. 원격 등록·푸시
```bash
cd <repo>
git remote add origin https://github.com/gjh999/jennysans.git
git push -u origin main
```

### C. 태그 푸시 (jsDelivr GitHub 채널이 이 시점부터 동작)
```bash
git push origin v1.0.0
```

### D. GitHub Release 생성 + 에셋 3종 업로드
```bash
REL=$(curl -sS -X POST https://api.github.com/repos/gjh999/jennysans/releases \
  -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" \
  -d '{"tag_name":"v1.0.0","name":"JennySans 1.000","body":"첫 릴리스. 자세한 내용은 CHANGELOG.md","draft":false,"prerelease":false}')
RID=$(printf '%s' "$REL" | python -c "import sys,json;print(json.load(sys.stdin)['id'])")
for f in dist/packages/JennySans-1.000-desktop.zip dist/packages/JennySans-1.000-web.zip dist/packages/JennySans-1.000-variable.zip dist/packages/JennySans-1.000-all.zip dist/packages/SHA256SUMS.txt; do
  curl -sS -X POST "https://uploads.github.com/repos/gjh999/jennysans/releases/$RID/assets?name=$(basename "$f")" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/octet-stream" --data-binary @"$f" >/dev/null && echo "uploaded $f"
done
```

### E. npm 배포 (`jennysans`, 1.0.0)
```bash
export PATH="<node 설치 경로>:$PATH"
cd <repo>
npm whoami || npm login          # 브라우저 로그인. 계정이 없으면 https://www.npmjs.com/signup
npm pack --dry-run               # 파일 목록·크기 확인(150 MB 미만인지)
npm publish --access public      # 되돌릴 수 없음(72시간 내 unpublish 만 가능)
```
- 대안 `@jennysoft/jennysans` 를 쓰려면 먼저 npm 조직/사용자 `jennysoft` 를 만들어야 한다(§부록 B). `package.json` `name` 만 바꾸면 되고 URL 은 `https://cdn.jsdelivr.net/npm/@jennysoft/jennysans@1.0.0/…`.

### F. DNS — 완료
- 사용자 확정 도메인 **`font.jennysoft.co.kr` → 175.127.49.246** (AGENTS §8 2026-09-06). 2026-09-06 08:50 실측 `nslookup font.jennysoft.co.kr` = `175.127.49.246`. (초기 후보였던 복수형 `fonts.` 서브도메인은 미등록이었고 더 이상 쓰지 않는다.)

### G. 서버 준비 — 팀장이 서버에서 직접 (`ssh debc-dev`, Rocky Linux 10, nginx 계정 `nginx`)
- 절차·명령은 **`deploy/README.md` §2** 가 정본(디렉터리 `/var/www/font` → `deploy/nginx-font.conf` 를 `/etc/nginx/conf.d/font.conf` 로 → `renew-qaudio-cert.sh` 복제·`sed 's/qaudio/font/g'`·`cat` 확인 → 최초 발급 → `nginx -t && reload` → cron). `deploy/font-bootstrap.sh`(팀장 작성)가 있으면 그것을 따른다.
- release 는 서버에 접속하지 않았다.

### H. 파일 배포 — 팀장 (QA RELEASE OK 후)
```bash
DRY=1 bash deploy/deploy.sh 1.000      # 미리보기(전송·변경 없음)
bash deploy/deploy.sh 1.000            # site/ → 루트 · dist/{static,variable,web,css} + 문서 4 → /var/www/font/v/1.000 · dist/packages → /download · latest 심링크 · 기존본 .bak.<ts>
```

- 홈페이지는 `deploy.sh` 의 **`SITE_EXCLUDE`** 가 개발용 파일(`*.template.html` · `preview.py` · `check_site.py` · `site/README.md` · `__pycache__` · `_measure_tmp.html`)을 빼고 올린다 — 8차 기준 26개 중 20개 전송. `DRY=1` 실행 시 전송 대상 목록이 출력되므로 **`google85364fe7cc780e8d.html`·`robots.txt`·`sitemap.xml`·`favicon.ico`·`assets/` 가 들어 있는지 확인**한다(빠지면 검색엔진 소유확인·색인이 깨진다).

### I. 검증 (curl 200 은 검증이 아님)
```bash
curl -sI -H "Origin: https://example.com" https://font.jennysoft.co.kr/v/1.000/web/JennySans-Regular.woff2 | grep -i -E "HTTP/|access-control|content-type|cache-control"
curl -sI https://cdn.jsdelivr.net/npm/jennysans@1.0.0/dist/css/jennysans.css | head -5
curl -sI https://cdn.jsdelivr.net/gh/gjh999/jennysans@v1.0.0/dist/css/jennysans.css | head -5
```
- 그리고 **다른 오리진**(예: `https://qaudio.jennysoft.co.kr/fonts-test.html` 임시 업로드, 또는 로컬 `python -m http.server`)에 `site/test.html` 의 CSS 경로를 CDN 절대 URL 로 바꾼 사본을 올려 브라우저에서 9 웨이트가 JennySans 로 그려지는지 스크린샷(Playwright `docs/qa/scripts/browser.py` 재사용). 홈페이지 `https://font.jennysoft.co.kr/` 새로고침 + 다운로드 버튼이 실제 zip 을 받는지(`/download/SHA256SUMS.txt` 대조)도 확인.

## 6. GitHub 저장소·릴리스 에셋 계획

| 항목 | 값 |
|---|---|
| 저장소 | `github.com/gjh999/jennysans` — **public**, 기본 브랜치 `main`, Issues 켬, Wiki 끔 |
| 설명 | JennySans (제니산스) — general-purpose Korean & English (Latin) sans-serif font family, SIL OFL 1.1 |
| Topics | `font` `typeface` `korean` `hangul` `webfont` `woff2` `variable-font` `ofl` |
| 커밋 대상 | 소스 트리 전체(`AGENTS.md`·`docs/`·`charset/`·`tools/`·`site/`·`deploy/`·`LICENSE`·`README.md`…). `sources/`·`build/` 제외(`.gitignore`). **`dist/` 는 태그 시점에만 커밋**(AGENTS §2) — jsDelivr GitHub 채널이 `dist/` 를 읽으므로 태그에는 반드시 포함 |
| `.gitignore` 검토(2026-09-06) | 현재 `sources/`(MANIFEST 제외)·`build/`·`__pycache__`·`*.zip`·`docs/qa/shots/*.png` 제외 — 유지. **추가 권고**: `node_modules/`, `*.tgz`(`npm pack` 산출), `.npmrc` — 소유 구역 밖이라 팀장에게 제안만 |
| 라이선스 표시 | GitHub 는 `LICENSE` 를 OFL-1.1 로 인식(헤더 때문에 "Other" 로 나올 수 있음 — 무해) |
| 릴리스 | 태그 `v1.0.0`, 제목 `JennySans 1.000`, 본문 = CHANGELOG 1.000 절 |
| 에셋 | `JennySans-1.000-desktop.zip` · `JennySans-1.000-web.zip` · `JennySans-1.000-variable.zip` · `JennySans-1.000-all.zip` · `SHA256SUMS.txt` (font-site `tools/package.py` 산출 `dist/packages/` — `index.json` 은 홈페이지용, Release 에는 올리지 않음) |

### zip 구성

| zip (**릴리스본**, `dist/packages/index.json` 2026-09-09T10:27:45+09:00 — 서버 `/download/` 와 동일) | 내용 | 크기 | SHA-256 (`SHA256SUMS.txt` 와 일치 확인) | 대상 |
|---|---|---|---|---|
| `JennySans-1.000-desktop.zip` | 정적 TTF 9종 + 설치 안내 + LICENSE 류 (13 파일) | 10,061,879 bytes (10.1 MB) | `6b8d52bd59b58f0c900c48a2a4a345386d666376a676fa7fea34874051e3b4d8` | Windows·macOS·한글·Office·Adobe·Unity·Flutter |
| `JennySans-1.000-web.zip` | WOFF2 전체본·변수·분할본 + CSS 4종 + LICENSE 류 (1,008 파일) | 23,408,367 bytes (23.4 MB) | `5ca4262669e5d53fb345ee3991cced26d85d00a3a8c2825e1fb5fd4e926e768e` | self-host 웹 |
| `JennySans-1.000-variable.zip` | `JennySansVariable.ttf` + `.woff2` + `css/jennysans-variable.css` + LICENSE 류 (7 파일) | 5,432,526 bytes (5.4 MB) | `e05769a81db2cd0d2bec2bc9f3738b76c8b9c67ada4bc38f47bcc8aa1b778b25` | 변수 폰트 사용자 |
| `JennySans-1.000-all.zip` | 정적·변수·웹·CSS·**문서** 전체 (1,021 파일) | 36,679,359 bytes (36.7 MB) | `f1b1243efe992fd899071220efe6ab3bac4e8f760fb818c9d88d719cf1e3b172` | 한 번에 받는 사용자 |

> zip 은 **결정적(deterministic)으로 재현된다** — 같은 `dist/` 를 넣으면 `tools/package.py` 가 언제 돌아도 같은 바이트·같은 SHA-256 을 낸다(타임스탬프·압축 순서 고정).
> ⚠ 단 **`all.zip` 은 문서(README·CHANGELOG·docs)를 담고 있어 문서를 한 글자만 고쳐도 크기·SHA 가 바뀐다.**
> **1.000 은 이미 배포됐으므로 이 표를 맞추려고 zip 을 다시 만들지 않는다** — 배포된 파일의 정본은 서버의 `https://font.jennysoft.co.kr/download/SHA256SUMS.txt` 다. 위 표는 릴리스 시점(10:27) 스냅숏이며, 이후 문서 수정으로 로컬 `all.zip` 을 재생성하면 값이 달라진다.
> 다음 버전(1.100)부터는 zip 생성을 **문서 확정 뒤 마지막 단계**로 두고 표를 그때 한 번만 맞춘다.

- 생성 주체 font-site(`tools/package.py`). 위 4개 모두 jsDelivr GitHub 단일 파일 20 MB 제한과 무관(Release 에셋·자체 `/download/` 로만 배포). zip 내용·SHA 는 `dist/packages/index.json`(홈페이지가 읽음)과 `SHA256SUMS.txt` 가 정본이며 빌드가 바뀌면 둘 다 재생성된다.

생성은 **font-site 의 `tools/package.py` → `dist/packages/`** 가 정본(홈페이지 `/download/` 와 GitHub Release 에셋에 같은 파일을 쓴다). 폴백(PowerShell, 같은 결과):
```powershell
Set-Location <repo>; New-Item -ItemType Directory -Force dist\packages | Out-Null
Copy-Item LICENSE dist\packages\LICENSE.txt
Compress-Archive -Force -DestinationPath dist\packages\JennySans-1.000-desktop.zip -Path dist\static\*.ttf, LICENSE, dist\packages\LICENSE.txt, THIRD-PARTY-NOTICES.md, README.md, docs\INSTALL.md
Compress-Archive -Force -DestinationPath dist\packages\JennySans-1.000-web.zip -Path dist\css, dist\web, LICENSE, THIRD-PARTY-NOTICES.md, README.md
Compress-Archive -Force -DestinationPath dist\packages\JennySans-1.000-variable.zip -Path dist\variable\JennySansVariable.ttf, dist\web\JennySansVariable.woff2, dist\css\jennysans-variable.css, LICENSE, THIRD-PARTY-NOTICES.md
Remove-Item dist\packages\LICENSE.txt
Get-FileHash dist\packages\*.zip -Algorithm SHA256 | ForEach-Object { "$($_.Hash.ToLower())  $(Split-Path $_.Path -Leaf)" } | Set-Content -Encoding ascii dist\packages\SHA256SUMS.txt
```
(`*.zip` 은 `.gitignore` 로 커밋되지 않는다 — 홈페이지 `/download/` 와 GitHub Release 에셋으로만 배포. `SHA256SUMS.txt` 는 커밋 가능.)

## 부록 A. 상표·이름 충돌 조사 — "JennySans" (2026-09-06, font-release)

| 조사 | 방법 | 결과 |
|---|---|---|
| 동명 폰트 존재 | 웹 검색 `"JennySans" font`, `"Jenny Sans" typeface OR font OR trademark`, `"JennySans" OR "jenny-sans" github OR npm OR fontshare OR myfonts` | **"JennySans"/"Jenny Sans" 라는 폰트·서체는 검색 결과에 없음.** 근접 이름: 「Jenny」(dafont 손글씨체, 2010, 개인용) · 「Jenny's Handwriting」(Fonts-A-Go-Go, Jennifer Heinicke) · 「Jensans」(1997 년 서체, fontsinuse.com) — 모두 산세리프 본문체가 아니며 표기도 다름 |
| 한국어 「제니산스」 | 웹 검색 `"제니산스" 폰트 OR 글꼴 OR 상표` | **동명 없음.** 다만 블랙핑크 제니(Jennie)의 한글 서체 **「젠 세리프(ZEN SERIF)」**(OA엔터테인먼트 배포)가 "제니 폰트"로 널리 불림 → 국내에서 "제니산스" 가 그쪽으로 연상될 가능성. 이름·성격(세리프/블랙레터 vs 고딕) 모두 다르므로 충돌은 아니나 홍보 문구에서 "제니(Jennie)" 와 무관함을 굳이 부각할 필요는 없음 |
| GitHub | `api.github.com/search/repositories?q=jennysans` · `repos/gjh999/jennysans` | 저장소 0건 / `gjh999/jennysans` 미존재(404) → 사용 가능 |
| npm | 부록 B | `jennysans` 미등록 |
| 상표 등록(KIPRIS·USPTO·EUIPO) | **확인 못 함** — 검색 API 를 이 세션에서 실행하지 못함 | 사용자가 KIPRIS(http://www.kipris.or.kr) 에서 상표 「JennySans」·「제니산스」, 상품류 **9류(컴퓨터 소프트웨어·글꼴)·42류** 로 직접 조회 권고. 현 단계 표기는 ™(미등록) — `docs/spec/06-license.md` §7 |

결론: 폰트·오픈소스 영역에서 이름 충돌 없음(2026-09-06 기준). 상표 출원 여부는 사용자 결정(출원 시 이 표를 근거로).

## 부록 B. npm 패키지 이름 가용성 (2026-09-06, font-release 실측)

| 이름 | 확인 | 결과 |
|---|---|---|
| `jennysans` | `https://registry.npmjs.org/jennysans` → **HTTP 404** · `registry.npmjs.org/-/v1/search?text=jennysans` → total 0 | **사용 가능** (1순위, `package.json` 에 반영) |
| `@jennysoft/jennysans` | `registry.npmjs.org/@jennysoft%2Fjennysans` → 404 · `search?text=scope:jennysoft` → 0 패키지 | 패키지 없음. 단 스코프 `@jennysoft` 는 npm 사용자/조직 `jennysoft` 소유자만 publish 가능 — 사용자·조직 존재 여부는 **확인 못 함**(`/-/user/org.couchdb.user:jennysoft` 401, npmjs.com 403 차단). 쓰려면 `npm login` 후 https://www.npmjs.com/org/create 에서 `jennysoft` 조직 생성(무료 public) |
| 권고 | | `jennysans` 로 배포(짧고 CDN URL 단순). 조직을 만들면 `@jennysoft/jennysans` 를 **별칭이 아니라 동일 내용의 2차 패키지**로 낼 수 있으나 유지비만 늘어 비권고 |

## 부록 C. 스펙·지시 대조 — 팀장 결정 반영 (AGENTS §8 2026-09-06 하단 2줄)

| 항목 | 결정(AGENTS §8) | 산출물 반영 상태 |
|---|---|---|
| **LICENSE 1행 = name ID 0 1행(정본)** | `Copyright (c) 2026 JennySoft (https://jennysoft.co.kr), with Reserved Font Names 'JennySans' and '제니산스'.` — 원본 고지는 ID 0 에서 `Portions ` 접두 허용, LICENSE 에서는 원문 그대로 | **반영** — `LICENSE`(UTF-8·LF, 1행만 비ASCII), `THIRD-PARTY-NOTICES.md`·`README.md`·`docs/OFL-FAQ-ko.md`·`CHANGELOG.md`·`site/index.html` 의 RFN 문구를 두 이름으로 갱신. 빌더가 name ID 0 1행을 같은 문구로 맞춤 |
| 「제니산스」 RFN | **선언**(위 정본에 포함) | 반영. 스펙 06 §1 의 "선언하지 않음" 은 architect 가 갱신할 것(소유 밖) |
| 자체 CDN 경로 | `https://font.jennysoft.co.kr/v/1.000/…` + `/latest/`(심링크) | 반영(작성 당시부터) — 스펙 05 §5-4·§6 의 `/v1.000/` 예시는 architect 갱신 대상 |
| 분할본 파일명 | `JennySans-<W>.subset.<n>.woff2`(빌더 동일) | 반영 |
| git 태그 | `v1.0.0`(npm 1.0.0) ↔ 폰트 1.000, `X.YZZ ↔ X.Y.ZZ` | 반영(§1-1) — ROADMAP P6 "태그 1.000" 표기는 팀장 갱신 |
| Adobe 저작권 연도 | (결정 없음) 리서치 02 §3 의 `2014-2025` 확대 제안 대신 **원문 `2014-2021`** 유지 | 실제 병합 파일(Pretendard 내장분·Noto KR VF) 문구가 모두 2014-2021, SHS 2.005R 미포함 |
| 변수 폰트 패밀리명 | (결정 대기) 스펙 01/02 "JennySans Variable" | 문서는 "JennySans Variable" 로 기재 |
| `.gitignore` | (제안) `node_modules/`·`*.tgz` 추가 | 소유 구역 밖 — 팀장 판단 |
