# site/ — JennySans 소개 홈페이지 (`font.jennysoft.co.kr`, font-site 소유)

> 상위 규칙: `AGENTS.md` §3-1(소유 구역)·§8(2026-09-06 도메인·홈페이지 결정), 역할 `.claude/agents/font-site.md`.
> 배포는 release 의 `deploy/`(`deploy/README.md`)가 한다. 이 문서는 **파일 구성·빌드·로컬 미리보기·경로 규약·검증 결과**만 다룬다.

## 1. 파일

| 파일 | 역할 | 비고 |
|---|---|---|
| `index.template.html` | 홈페이지 **원본 템플릿** — `{{PKG:…}}`·`{{FILE:…}}`·`{{CMAP:…}}`·`{{LANG:…}}`·`{{GLYPH:…}}`·`{{VERSION}}` 자리표시자 | 고칠 때는 이 파일을 고친다 |
| `index.html` | **생성 파일** — `tools/package.py --render-site` 가 템플릿의 자리표시자를 실측값으로 치환해 만든다 | 직접 고치지 말 것(머리 주석에 생성 시각) |
| `glyphs.template.html` → `glyphs.html` | **글자맵**(별도 페이지) 템플릿·생성 파일 | §7 |
| `assets/glyphs.js` | 글자맵 동작(블록·초성 탭·청크 렌더·검색·상세 패널) | 외부 의존 0, ES5 |
| `assets/glyphmap.json` · `assets/languages.json` · `assets/origin-diff.json` · `assets/first-paint.json` | 글자맵·지원 언어·원본 대비 차이·첫 화면 전송량 **실측 데이터**(생성물) | `tools/glyphmap.py` · `lang_support.py` · `origin_diff.py` · `first_paint.py` |
| `assets/site.css` · `assets/site.js` | 스타일(라이트/다크, 반응형) · 타입 테스터/탭/복사/테마/문장 견본 토글 | 외부 의존 0, ES5 |
| `test.html` | QA 격자(`?mode=static\|variable\|subset\|variable-subset`) — **QA 공용, 유지** | `../dist/…` 상대경로 → 서버에서는 `/dist/` 심링크 필요(§4) |
| `preview.py` | 로컬 미리보기 서버(배포 경로 규약을 흉내냄) | §3 |
| `check_site.py` | Playwright 실브라우저 검증 + 스크린샷 | §5 |
| `robots.txt` · `sitemap.xml` · `favicon.ico` · `google85364fe7cc780e8d.html` · `assets/{og-image,icon-512,icon-192,apple-touch-icon,favicon-32}.png` | SEO·소유확인·아이콘 | §6 |
| `README.md` | 이 문서 | |

페이지 구성 — `index.html`(단일 페이지 + 앵커): ① 히어로 ② 타입 테스터(변수 폰트, `font-weight` 100–900) ③ 웨이트 9종 + 줄높이 비교 ④ 문자 범위(표 + 글립 격자 + **글자맵 안내**) ④-2 **문장 견본**(한국어 3문단·영어·스페인어·`tnum` 표·UI 요소, 크기 14/16/18px · 줄 간격 1.5/1.7 토글) ④-3 **지원 언어**(실측 언어 수 + 언어별 샘플 문장) ⑤ 다운로드(zip 4종, 크기·SHA-256) ⑥ 사용법 탭(Windows / macOS / 한글·Office / Photoshop·Illustrator / 웹 / Flutter / Unity·Godot) ⑦ 라이선스(허용·조건·금지 + 크레딧) ⑧ 푸터(영문 요약 한 문단, 폰트 로드 상태). 헤더 메뉴 8개(테스터·웨이트·**글자맵**·문자 범위·**언어**·다운로드·사용법·라이선스) — 모바일에서는 가로 스크롤 + 끝 페이드.

폰트 로드 전략: 본문은 `/v/<ver>/css/jennysans-dynamic-subset.css`(정적 분할본, 라틴 조각 2개 preload), 타입 테스터만 `"JennySans VF"` 라는 **별도 패밀리명**으로 변수 WOFF2 를 선언해 정적/변수 이중 다운로드를 피한다(`docs/spec/05-web.md` §1 "섞어 선언하지 않는다"). 외부 요청 0(폰트·CSS·JS·아이콘 전부 같은 오리진, 아이콘은 인라인 SVG).

## 2. 빌드 (패키지 + 렌더)

```bash
cd <repo>
PYTHONUTF8=1 python tools/package.py --render-site     # dist/ → dist/packages/*.zip + index.json + SHA256SUMS.txt → site/index.html
PYTHONUTF8=1 python tools/package.py --render-only     # zip 은 그대로 두고 템플릿만 다시 렌더
```

- `tools/package.py` 는 `dist/` 를 **읽기만** 하고 `dist/packages/` 와 `site/`(`index.html`·`glyphs.html`·`assets/glyphmap.json`·`assets/languages.json`)에만 쓴다. 버전은 `tools/config.py` 의 `VERSION`.
- `--render-site` 는 (1) 글자맵·언어 JSON 을 dist 실측으로 다시 만들고 (2) `index.template.html`·`glyphs.template.html` 을 **둘 다** 렌더한다.
- **zip 은 재현 가능하다**: 내부 타임스탬프·안내문 날짜를 "가장 최근에 바뀐 입력 파일"의 시각으로 고정하므로 `dist/` 가 그대로면 몇 번을 다시 만들어도 SHA-256 이 같다(2026-09-08 실측 확인).
- zip 4종(내부 최상위 폴더 `JennySans-<ver>-<kind>/`, 각각 `LICENSE`·`LICENSE.txt`·`THIRD-PARTY-NOTICES.md`·`README-설치안내.txt`(한국어, UTF-8 BOM, CRLF) 동봉):

| zip | 내용 |
|---|---|
| `JennySans-<ver>-desktop.zip` | 정적 TTF 9종(폴더 없이 바로) |
| `JennySans-<ver>-web.zip` | `css/`(4) + `web/`(전체본 9 + 변수 1) + `web/subset/`(분할본 전부) — CSS 의 `../web/` 상대경로 유지 |
| `JennySans-<ver>-variable.zip` | `variable/JennySansVariable.ttf` + `web/JennySansVariable.woff2` + `css/jennysans-variable.css` |
| `JennySans-<ver>-all.zip` | `static/` `variable/` `web/` `css/` + `README.md` `CHANGELOG.md` `INSTALL.md` |

- `index.json`: 버전·npm 버전·생성 시각·zip 별 파일명/bytes/SHA-256/파일 수/내용 목록 + 정적·변수·WOFF2·CSS 개별 파일 bytes/SHA + Regular cmap 실측(한글·자모·호환자모·라틴·그리스·키릴·기호 블록) + 라틴 조각 파일명(분할 CSS 에서 U+0041 을 담는 조각을 파싱) + 웨이트당 조각 수.
- 렌더는 **치환되지 않은 `{{…}}` 가 하나라도 남으면 실패**한다(`docs/DISTRIBUTION.md` §4-2 의 `grep "{{"` 게이트와 같은 기준).
- **빌더가 `dist/` 를 다시 만들면 반드시 다시 실행**한다(zip 내용·SHA·cmap 수치가 바뀐다). `*.zip` 은 `.gitignore` 로 커밋되지 않고 `index.json`·`SHA256SUMS.txt` 만 커밋된다.

## 3. 로컬 미리보기

```bash
PYTHONUTF8=1 python site/preview.py            # http://127.0.0.1:8765/
PYTHONUTF8=1 python site/preview.py --port 9000 --open
```

`http.server` 로 `site/` 를 루트로 띄우되, 배포 서버와 같은 URL 구조가 되도록 아래처럼 매핑한다(§4). `Access-Control-Allow-Origin: *`, `Cache-Control: no-cache`, MIME `font/woff2`·`font/ttf`·`text/css; charset=utf-8`, zip 은 `Content-Disposition: attachment`.

## 4. 경로 규약 (배포 루트 = `site/` 내용 + `v/<ver>/` + `latest/` + `download/`)

페이지 안의 폰트·다운로드 링크는 전부 **사이트 루트 기준 절대경로**다. 저장소 상대경로(`../dist/…`)는 서버에서 동작하지 않으므로 쓰지 않는다.

| URL | 서버 `/var/www/font/` (release `deploy/remote-install.sh`) | 로컬 `preview.py` | 쓰는 곳 |
|---|---|---|---|
| `/` `/index.html` `/assets/…` `/test.html` | `site/` 내용을 루트에 복사 | `site/` | 홈페이지 |
| `/v/1.000/css/…` `/v/1.000/web/…` `/v/1.000/static/…` `/v/1.000/variable/…` | `v/1.000/` = `dist/{css,web,static,variable}` (immutable 1년 + CORS `*`) | `dist/` | 페이지 폰트, 개별 파일 링크, 코드 예시의 CDN URL |
| `/v/1.000/LICENSE` `/v/1.000/THIRD-PARTY-NOTICES.md` | `remote-install.sh` 가 `v/<ver>/` 에 복사 | 저장소 루트 파일 | 라이선스 링크 |
| `/latest/…` | 심링크 `latest -> v/1.000` (5분 캐시) | `dist/` | 문서 안내용(페이지는 고정 버전 경로 사용) |
| `/download/JennySans-1.000-*.zip` `/download/SHA256SUMS.txt` `/download/index.json` | `download/` = `dist/packages/` (5분 캐시, 첨부 다운로드) | `dist/packages/` | 다운로드 버튼 4개, 체크섬 링크 |
| `/dist/…` | (선택) 심링크 `dist -> latest` — `test.html` 의 `../dist/` 용 | `dist/` | QA 격자 |

- `site/` 를 통째로 루트에 올리면 `index.template.html`·`preview.py`·`check_site.py`·`README.md` 도 함께 올라간다. 무해하지만 노출을 원치 않으면 `remote-install.sh` 에서 제외하거나 nginx 로 `\.py$|\.template\.html$|README\.md$` 를 404 처리하면 된다(release 판단).
- 새 버전(예 1.001)을 낼 때: `tools/config.py` `VERSION` 갱신 → 빌드 → `package.py --render-site` → 페이지의 모든 `/v/1.001/…`·zip 이름이 함께 바뀐다. 템플릿에 버전 숫자를 직접 적지 않는다.

## 5. 검증 (`check_site.py`)

```bash
PYTHONUTF8=1 python site/check_site.py                                   # preview 서버를 스스로 띄워 검사 + 스크린샷
PYTHONUTF8=1 python site/check_site.py --url https://font.jennysoft.co.kr  # 배포 후 실서버
```

검사: ① 미치환 `{{…}}` 0(`index.html`·`glyphs.html`) ② 콘솔 error·pageerror·실패/4xx 요청 0(데스크톱·모바일) ③ `document.fonts` 로 "JennySans" 조각이 실제 loaded + `check('400 16px')`·`check('800 16px')` + **폴백(serif) 대비 렌더 폭이 다름**(웹폰트 적용 실증), 3b 변수 폰트 로드·테스터 굵기 900 반영, 3c **합성 4자 ⅔ ∼ ≒ ◈** 가 JennySans 로 그려짐 ④ `/download/*.zip` 4개 200 + `Content-Length` = `index.json` bytes, `SHA256SUMS.txt` 200 ⑤ 모바일 가로 스크롤 없음 ⑥ 탭 전환 ⑦ **SEO 메타·JSON-LD**(canonical·robots·keywords·OG/Twitter·hreflang·아이콘 링크 + JSON-LD 가 JSON 으로 파싱되고 `@graph` 에 Organization/WebSite/SoftwareApplication, `softwareVersion`·`datePublished`·`downloadUrl` 이 치환됨) ⑧ **SEO·데이터 정적 파일 200**(robots·sitemap·favicon.ico·og-image·아이콘 4종·구글 소유확인·`glyphmap.json`·`languages.json`·`glyphs.js`) ⑨ **글자맵 페이지**(로드·콘솔 0·블록 버튼 수·초성 탭·`"JennySans VF"` 적용을 폴백 폭 비교로 확인·블록 전환·검색 `U+AC00` → 상세 패널의 코드포인트·유니코드 이름) ⑩ 스크린샷 `docs/qa/shots/site-desktop.png`(1280 폭 전체) · `site-mobile.png`(390 폭, DPR 2, 전체) · `site-glyphs.png`(글자맵 1280×900).

### 검증 결과

(아래는 `check_site.py` 출력을 그대로 옮긴 것. 빌드가 바뀌면 다시 실행해 갱신한다.)

**2026-09-09 10:10 — 빌더 8차 빌드(확정본, 자체 점검 PASS/WARN 0, 정적·VF 글립 13,980 · cmap 13,254) 기준 재실행: ALL PASS 18/18.**
패키지 실측: desktop **10,061,718 B**(`ec28ffdb…`) · web **23,408,206 B**(`bfe26a58…`) · variable **5,432,365 B**(`92cb52bf…`) · all **36,677,382 B**(`2d822287…`). 첫 화면 재측정: 라틴 30.4 KB · 한국어 한 문장 83.4 KB · 한 문단 102.8 KB · 두 문단 2웨이트 154.6 KB. 원본 대비 차이 표는 cmap 이 그대로라 7차와 동일.

**2026-09-08 01:05 — 빌더 7차 빌드(`build/BUILD-REPORT.md`, 자체 점검 PASS, 정적 글립 13,984 · cmap 13,254) + 글자맵·문장 견본·지원 언어·「원본과 무엇이 다른가」 섹션 추가 뒤 재실행. 결과 ALL PASS 18/18.**
(아래 표는 00:01 실행분이며, 01:05 재실행에서 항목 9·9b·9c(글자맵)와 8(데이터 파일)이 추가로 PASS 했다 — 상세는 §5 검사 목록 참조.)

| 검사 | 결과 | 상세 |
|---|---|---|
| 1. 미치환 자리표시자 | PASS | index.html 0건 |
| 2. 콘솔·요청 오류 (desktop 1280×900) | PASS | 0건 |
| 3. JennySans 렌더 (desktop 1280×900) | PASS | faces loaded 130/891 · check 400 True / 800 True · 폭 JennySans 884px vs serif 944px · 상태줄 "JennySans 웹폰트 로드됨 (조각 130, 변수 1)" |
| 3b. 변수 폰트·테스터 (desktop 1280×900) | PASS | VF loaded 1 · check True · 폭 884px · 굵기 900 → computed 900 (900 · Black) |
| 3c. 합성 4자 ⅔∼≒◈ 렌더 (desktop 1280×900) | PASS | check True · 폭 JennySans 136px vs serif 160px |
| 6. 탭 전환 (desktop 1280×900) | PASS | 웹 탭 클릭 → panel-web 표시, panel-win 숨김 |
| 2. 콘솔·요청 오류 (mobile 390×844) | PASS | 0건 |
| 3. JennySans 렌더 (mobile 390×844) | PASS | faces loaded 130/891 · check 400 True / 800 True · 폭 JennySans 884px vs serif 944px |
| 3b. 변수 폰트·테스터 (mobile 390×844) | PASS | VF loaded 1 · check True · 폭 884px · 굵기 900 → computed 900 |
| 3c. 합성 4자 ⅔∼≒◈ 렌더 (mobile 390×844) | PASS | check True · 폭 JennySans 136px vs serif 160px |
| 6. 탭 전환 (mobile 390×844) | PASS | 웹 탭 클릭 → panel-web 표시, panel-win 숨김 |
| 5. 모바일 가로 스크롤 없음 | PASS | scrollWidth 390 ≤ innerWidth 390 |
| 7. SEO 메타·JSON-LD | PASS | canonical `https://font.jennysoft.co.kr/` · robots "index, follow, max-image-preview:large" · og:image `/assets/og-image.png` · twitter summary_large_image · hreflang 2 · icon 링크 4 · JSON-LD `['Organization','WebSite','SoftwareApplication']` version 1.000 date 2026-09-08 (치환 잔여 없음) |
| 4. 다운로드 링크 4개 + 체크섬 | PASS | all 200 36,730,555B · desktop 200 10,080,428B · variable 200 5,429,727B · web 200 23,452,457B · SHA256SUMS.txt 200 |
| 8. SEO 정적 파일 200 | PASS | robots.txt 114B · sitemap.xml 1,070B · favicon.ico 3,188B · og-image.png 52,744B · icon-512.png 6,479B · icon-192.png 2,341B · apple-touch-icon.png 2,195B · favicon-32.png 497B · google85364fe7cc780e8d.html 53B |

- 스크린샷(00:01 갱신): `docs/qa/shots/site-desktop.png`(1280 폭 전체 페이지) · `docs/qa/shots/site-mobile.png`(390 폭, DPR 2 전체 페이지). 라이트 모드(Playwright 기본 `prefers-color-scheme: light`). 다크 모드는 우상단 토글 또는 OS 설정.
- 패키지(2026-09-08 00:01 실측, `dist/packages/index.json`): desktop **10,080,428 B**(13 파일, `05ba1963…`) · web **23,452,457 B**(1,008, `a1fe96a9…`) · variable **5,429,727 B**(7, `8fb67983…`) · all **36,730,555 B**(1,021, `6b9f9cf9…`).
- 합성 4자는 문자 범위 격자의 「괘선·도형」(◈) · 「화살표·수학」(∼ ≒) · 「구두점·화폐·문자형」(⅔) 카드에 넣었고, 3c 검사(폴백 대비 폭 차 + `document.fonts.check`)로 JennySans 조각에서 그려짐을 확인했다.
- 첫 실행(2026-09-06 09:05)에서 6 FAIL 이 났던 원인은 빌더가 `dist/web/subset/` 을 쓰는 중이었기 때문이다 — **`dist/` 가 바뀌는 중에는 검증하지 말 것.**

## 6. SEO·아이콘 파일 (팀장 추가, 2026-09-07)

| 파일 | 내용 |
|---|---|
| `index.template.html` `<head>` | `robots`·`keywords`·`author`, OG(`og:site_name`·`title`·`description`·`url`·`image` 1200×630·`alt`)·Twitter(`summary_large_image`), `canonical`, `hreflang`(ko·x-default), 아이콘 링크 4종, `link rel="license"`, **JSON-LD `@graph`**(Organization / WebSite / SoftwareApplication — `softwareVersion`=`{{VERSION}}`, `datePublished`=`{{DATE}}`, `downloadUrl`, 설명의 `{{CMAP:hangul}}`; 전부 `package.py` 가 치환) |
| `robots.txt` | `Allow: /`, `/*.bak.*`·`/test.html` 차단, `Sitemap:` 절대 URL |
| `sitemap.xml` | 루트 + `#download`·`#usage`·`#license`·`/LICENSE`, og 이미지. **`lastmod` 는 수동 값**이므로 내용이 크게 바뀌면 손으로 갱신 |
| `favicon.ico`(루트) · `assets/{favicon.ico,favicon-32,icon-192,icon-512,apple-touch-icon}.png` | 「제」 아이콘(JennySans Bold 로 렌더) |
| `assets/og-image.png` | 1200×630 스페시먼 카드(제니산스/JennySans/샘플 문장/도메인) |
| `google85364fe7cc780e8d.html` | Google Search Console 소유확인 — **파일명·내용을 바꾸지 말 것** |

재생성(폰트가 바뀌어 아이콘·OG 이미지를 다시 그릴 때만):
```bash
PYTHONUTF8=1 python tools/seo_assets.py     # dist/static 의 TTF 로 og-image·아이콘 5종·favicon.ico 재생성
```
`site/favicon.ico`(루트 사본)는 `site/assets/favicon.ico` 와 같은 파일이다 — 재생성 후 루트로 복사해 두 곳을 맞춘다. 배포 시 `site/` 전체가 루트로 가므로 `/robots.txt`·`/sitemap.xml`·`/favicon.ico`·`/google….html` 이 그대로 사이트 루트에서 서빙된다(`preview.py` 도 같은 경로로 매핑, `.ico`·`.xml` MIME 포함).
- 첫 실행(09:05)에서는 빌더가 `dist/web/subset/` 을 다시 쓰는 도중이라 ExtraBold·Black 조각 404 + 폴백 렌더로 6 FAIL 이 났다 — 빌드 완료 후 재실행해 해소. **`dist/` 가 바뀌는 중에는 검증하지 말 것.**
- 알려진 표시 특성: Windows 헤드리스 Chromium 은 LCD 서브픽셀 AA 를 쓰므로 스크린샷의 가는 괘선(─ │ ┌)에 색 번짐이 보일 수 있다(폰트 결함 아님, 실제 화면과 동일한 OS 렌더). 모바일 캡처(DPR 2)에서는 보이지 않는다.

## 7. 글자맵 · 지원 언어 (2026-09-08, 사용자 요청)

### 7-1. 글자맵 `glyphs.html`
- 데이터: `tools/glyphmap.py` 가 `dist/static/JennySans-Regular.ttf` 의 **cmap 을 그대로 읽어** `site/assets/glyphmap.json` 을 만든다(블록 정의 = 코드포인트 범위만, 수록 여부는 교집합으로 결정). 페이지는 이 JSON 만 fetch 한다.
  - 한글 음절은 **초성 19 그룹**으로 나누고 이름을 싣지 않는다(자모 로마자 표만 실어 클라이언트가 `HANGUL SYLLABLE GA` 를 조립). 한자는 `CJK UNIFIED IDEOGRAPH-XXXX` 패턴. 그 밖 블록은 `unicodedata.name()` 을 그대로 넣는다 → 전체 78 KB.
  - **1.100(한자) 대비**: 한자 블록 정의(U+3400–4DBF·4E00–9FFF·F900–FAFF)가 이미 들어 있고, cmap 에 한자가 하나도 없으면 블록이 아예 빠진다. 한자가 들어오는 순간 목록에 자동으로 나타난다 — 페이지·JSON 어디에도 숫자를 하드코딩하지 않았다.
- 성능: 한 번에 DOM 에 붙이는 셀을 **250개씩 `requestAnimationFrame` 으로 나눠** 추가한다. 한글은 초성 탭당 588자만 그리고(11,172자를 한꺼번에 그리지 않는다), 그룹이 없는 큰 블록은 처음 1,000자 + "더 보기". 블록 전환·검색 시 진행 중인 렌더를 취소한다.
- 기능: 웨이트 100–900(변수 폰트) · 크기 16–96px · 검색(`U+AC00`·`AC00`·글자 직접 입력) · 글립 클릭 → 상세 패널(글자·`U+XXXX`·유니코드 이름·블록·글자/`U+`/HTML 코드 복사) · `#블록id-그룹` 해시로 딥링크.
- 폰트: 격자는 **변수 폰트 전체본**(`/v/<ver>/web/JennySansVariable.woff2`, 약 2.2 MB) 하나를 `"JennySans VF"` 로 선언해 쓴다. 모든 글자를 보여줘야 해서 분할본(조각 99개 요청)보다 전체본 1개가 낫다. UI 텍스트는 홈과 같은 분할 CSS.

### 7-2. 지원 언어 (index `#languages`)
- `tools/lang_support.py` 가 **정서법 필수 문자 + 샘플 문장의 모든 글자**가 산출물 cmap 에 있는지 확인해 `site/assets/languages.json` 을 만들고, `package.py` 가 그 값으로 `{{LANG:…}}`·`{{LANG_TABLE:…}}` 를 채운다(숫자·표 모두 하드코딩 아님).
- 라틴 문자권 목록은 architect 소유 `charset/scripts/lang_check.py` 의 `LANGS` 를 **import 해서 그대로** 쓴다(읽기만 — 목록이 갈라지지 않게). 샘플 문장·한국어/자국어 표기는 `tools/lang_support.py` 의 `LATIN_META` 에 있고, `LANGS` 에 새 언어가 생기면 "샘플 문장 미등록"으로 제외 목록에 뜬다.
- 키릴·그리스·한국어·영어는 `tools/lang_support.py` 에서 자모 전부를 정의해 검증한다.
- 2026-09-08 실측: **라틴 29 · 키릴 6 · 그 밖 3 = 38개 언어**(표 항목 37개 — "덴마크어 · 노르웨이어"가 한 항목 2개 언어). 베트남어는 U+1EA0–1EF9 미보유로 **제외**(페이지에 미지원으로 명시).
- 언어별 국기 이모지는 쓰지 않는다(폰트에 이모지 글립이 없다) — 언어명 + 샘플 문장만.

### 7-3. 「원본과 무엇이 다른가」 (index `#origin`, 라이선스 섹션 바로 앞)
- 차이 표는 `tools/origin_diff.py` 가 **`sources/Pretendard/alternative-ttf/Pretendard-Regular.ttf` 와 `dist/static/JennySans-Regular.ttf` 의 cmap 을 직접 비교**해 만든 `site/assets/origin-diff.json` 으로 렌더된다(하드코딩 없음). `sources/` 가 없는 환경에서는 기존 JSON 을 그대로 쓴다(`--render-site` 가 알려 준다).
- 2026-09-08 실측(Regular): 첫가끝 자모 0→256 · 옛 호환자모 53→94 · 자모 확장 A·B 0→101 · 괘선 0→128 · 블록 요소 0→32 · **원문자·괄호문자 59→253** · 수학 16→76 · 도형·기타 기호 31→74 · 단위 80→96 · 가나 184→1. **카테고리 순수 추가 871자 · 가나 183자 제외 · 원본 대비 전체 추가 909 / 제외 1,991(cmap 14,336 → 13,254).**
  - ⚠ 팀장이 준 수치와 두 곳이 다르다: 원문자·괄호문자 **253**(팀장 238), 합계 **+871**(팀장 +607). 내 범위는 U+2460–24FF(58→160) + U+3200–32FF(1→93) 이고 스크립트로 재현 가능하다 — 팀장이 쓴 범위가 다르면 `CATEGORIES` 를 고치면 된다. 나머지 8행과 가나 −183 은 팀장 수치와 일치.
- "첫 화면 ○○ KB" 는 `tools/first_paint.py` 가 **실제 브라우저 전송량**(분할 CSS + `.woff2` Content-Length 합)을 재서 `site/assets/first-paint.json` 에 남긴 값이다. 2026-09-08 실측: 라틴 전용 30.4 KB(1조각) · 한국어 한 문장 83.5 KB(7) · 한 문단 102.9 KB(9) · 두 문단+제목 2웨이트 154.7 KB(13). (팀장 메모의 "약 55 KB" 는 어떤 시나리오인지 확인 못 해 쓰지 않았다.)
- 저작권 박스: 글자체 도안 비보호(대법원 1996. 8. 23. 94누5632) · 폰트 파일의 프로그램 저작물성(대법원 2001. 6. 29. 99다23246) · OFL 네 조건 준수. 크레딧 표는 `THIRD-PARTY-NOTICES.md` 의 표기를 따랐다.
- 자체 제작 4자(⅔ ∼ ≒ ◈)는 큰 글자로 보여 주고 합성 방식을 적었다(`docs/spec/07-supplement.md` §5).

### 7-4. 다시 만들기
```bash
PYTHONUTF8=1 python tools/glyphmap.py --print       # 글자맵 JSON (블록별 집계 출력)
PYTHONUTF8=1 python tools/lang_support.py --md      # 언어 JSON (+ 표 출력)
PYTHONUTF8=1 python tools/origin_diff.py --md       # 원본 대비 차이 JSON (+ 표 출력) — sources/ 필요
PYTHONUTF8=1 python tools/first_paint.py            # 첫 화면 전송량 실측(브라우저) → first-paint.json
PYTHONUTF8=1 python tools/package.py --render-site  # 위 데이터 + zip + index.html·glyphs.html 을 한 번에
```
`--render-site` 는 글자맵·언어·원본차이 JSON 을 매번 다시 만들지만 **first-paint.json 은 다시 재지 않는다**(브라우저가 필요). 분할 방식이 바뀌면 `first_paint.py` 를 따로 돌린다.
