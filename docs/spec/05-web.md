# 05 — 웹 배포 스펙: WOFF2·unicode-range 분할·CSS·CDN (JennySans)

> 소유: font-architect · 상태: **P2 2차 — 팀장 결정(Google 124 슬라이스 재사용, CDN 경로 `/v/1.000/`)·빌더 1차 실측 반영(2026-09-06)**.
> 근거: `docs/research/03-web-and-platform.md` §1(Google Fonts KR 슬라이스 실측), `docs/research/google-kr-slices.css`(범위 데이터), `build/BUILD-REPORT.md`(1차 빌드 크기).
> 목표(AGENTS §4-6): 첫 화면 폰트 로드를 **수십 KB~100 KB 대**로 — 라틴 1 슬라이스 + 고빈도 한글 2~3 슬라이스.

## 1. 형식·브라우저

- **WOFF2 만** 배포(WOFF/TTF/EOT 웹 형식 없음). 정적 WOFF2 는 전 브라우저(Chrome 36+·Firefox 39+·Safari 10+·Edge 14+), 변수 WOFF2 는 Chrome 62+·Firefox 62+·Safari 11+.
- `local()` 소스는 쓰지 않는다(설치된 옛 버전이 웹 버전을 덮는 문제).
- 웹 WOFF2 는 무힌팅(원본 Pretendard TTF·Noto VF 모두 TT 힌트 없음) — 추가 제거 옵션 불필요.

## 2. 산출 파일 (`01-family.md` §4·§5)

```
dist/web/JennySans-<W>.woff2                          정적 전체본 9
dist/web/JennySansVariable.woff2                      변수 전체본 1
dist/web/subset/JennySans-<W>.subset.<n>.woff2        정적 분할본 9 × 99(+rest)   n = Google 슬라이스 번호
dist/web/subset/JennySansVariable.subset.<n>.woff2    변수 분할본
dist/css/jennysans.css                                 정적 전체본 9 @font-face
dist/css/jennysans-variable.css                        변수 전체본 1 @font-face
dist/css/jennysans-dynamic-subset.css                  정적 분할본 @font-face × (9 × 슬라이스 수)
dist/css/jennysans-variable-dynamic-subset.css         변수 분할본 @font-face × 슬라이스 수
```
- 분할 파일명은 AGENTS §7 형식 `JennySans-<W>.subset.<n>.woff2` 고정.
- CSS 안의 URL 은 **상대 경로**(`../web/...`); CDN 배포본은 release 가 §6 절대 URL 로 치환한다.

## 3. 분할 전략 — **채택: Google Fonts 한국어 124 슬라이스 unicode-range 재사용** (AGENTS §8)

- 데이터: `docs/research/google-kr-slices.css`(2026-09-05, `css2?family=Noto+Sans+KR:wght@100..900` 응답, `@font-face` 124 블록) → 빌더가 `tools/data/korean-slices.google.json` 으로 파싱해 커밋(취득 URL·일시·124 범위). 코드포인트 구간 목록은 사실 정보라 재사용 가능.
- 번호 규칙: **Google 슬라이스 인덱스 n(0–123)을 그대로 파일 번호로** 쓴다(추적성). 우리 cmap 과 교집합이 비는 슬라이스(#0–1 CJK 호환한자, #66–99 한자·가나 등)는 **결번**. 1차 빌드 실측: 웨이트당 **99 슬라이스** 생성.
- **rest = #124**: 어떤 Google 범위에도 속하지 않는 우리 cmap 코드포인트(1차 빌드 실측 256개, ≈14 KB) — 예: Google KR 슬라이스에 없는 그리스 기본·기호 일부. QA 는 rest 의 코드포인트 목록을 보고서에 남긴다.
- 라틴 = **#123**(`U+0000-00FF, 0131, 0152-0153, 02BB-02BC, 02C6, 02DA, 02DC, 0304, 0308, 0329, 2000-206F, 20AC, 2122, 2191, 2193, 2212, 2215, FEFF, FFFD`), 라틴 확장 = #122, 키릴 = #120, 베트남어 = #121(우리는 비어 결번). 한글은 #2–119 중 84개 슬라이스(빈도 역순: 번호 클수록 고빈도, `가·이` #119, `한·는` #118).
- 규칙: 슬라이스는 서로 겹치지 않고, 합집합 = 폰트 cmap(`.notdef`·space 제외); 정의에 있으나 cmap 에 없는 코드포인트는 `unicode-range` 에서 뺀다; `U+0020`·`U+00A0` 은 #123 에 있어야 한다.
- 변수 폰트도 같은 슬라이스 정의(Google 도 변수 KR 을 같은 방식으로 서빙).
- (미채택 예비) 자체 분할: KS 완성형 2,350(1티어 8슬라이스) + 나머지 22 슬라이스 + 공통 8 — Google 데이터를 쓸 수 없게 될 때만.

**QA 합격 기준 (3)**: 스크립트로 (a) 각 슬라이스 cmap ⊆ 자기 `unicode-range` (b) 슬라이스 간 교집합 0 (c) 합집합 = 전체본 cmap (d) #123 에 U+0020·U+00A0 (e) 9 웨이트·변수의 슬라이스 정의 동일 (f) rest 목록 기록 — 전부 PASS.

## 4. 파일 크기 — 목표와 실측 (1차 빌드 2026-09-06 · 8차 빌드/QA 실측 2026-09-09 반영)

| 항목 | 실측 | 목표 | 판정 |
|---|---|---|---|
| 정적 전체 WOFF2 / 웨이트 | 652 KB(Thin) ~ 764 KB(Black), Regular 726 KB | 원본 대비 증가 없음(Pretendard TTF 2.6 MB 의 WOFF2 대비 서브셋으로 감소) | QA 가 원본 WOFF2 와 비교 기록 |
| 변수 전체 WOFF2 | 2,180 KB | ≤ 2.5 MB | ✓ |
| 분할 합계 / 웨이트 | 1,190–1,233 KB (99 슬라이스) | — | 참고(Google Noto KR VF 124 슬라이스 3,520 KB) |
| 슬라이스 1개 | 2.3 KB ~ 32 KB | ≤ **40 KB** | ✓ |
| 라틴 #123 / 웨이트 | 31.3–32.0 KB | ≤ **35 KB** | ✓ (Google Noto 26 KB 보다 큼 — glyf 형식·Inter 계열 라틴 글립 수 때문; 허용) |
| rest #124 | 13–14 KB(256 cps) | ≤ 20 KB | ✓ |
| 변수 분할 합계 | 1차 3,333 KB(최대 82 KB·라틴 58 KB) → **8차 최대 90,472 B·라틴 #123 68,996 B** | 슬라이스 ≤ **95 KB**, 라틴 ≤ **70 KB** (팀장 결정 AGENTS §8 2026-09-09 — 6차 이후 보충 글립 gvar 증가분 반영) | ✓ |
| 테스트 페이지 A(라틴·스페인어만, 400·700) | (QA 측정) | 요청 2, 전송 ≤ **70 KB** | |
| 테스트 페이지 B(한국어 소개문 ~300자 + 라틴, 400·700) | (QA 측정) | 전송 ≤ **300 KB**(웨이트당 ≤ 150 KB; 예상 32 + 한글 3~4 슬라이스 × 30 ≈ 120–150 KB), 요청 ≤ 30 | |
| 테스트 페이지 C(한국어 긴 본문 ~2,000자, 400) | (QA 측정) | 전송 ≤ 400 KB | |
| 변수 폰트로 B | (QA 측정) | 전송 ≤ 정적 2 웨이트 합 × 1.2 | |
| `jennysans-dynamic-subset.css`(gzip) | **101,344 B**(QA 8차 실측) | ≤ **110 KB** (팀장 결정 AGENTS §8 2026-09-09) | ✓ — 9 웨이트 × 99 슬라이스 = **891 `@font-face`** 블록의 필연적 크기다(블록당 gzip 약 114 B). 블록 수를 줄이려면 웨이트나 슬라이스를 줄이는 수밖에 없으므로 목표를 실측에 맞춘다 |

- 목표 초과 시 티켓 → 팀장이 목표 조정 또는 분할 변경. 실측은 `docs/qa/QA-REPORT` 에(AGENTS §4-6). 티켓 10(2026-09-09)은 **목표 조정**으로 종결했다 — 게이트 6(AGENTS §4-6: 정적 원본 대비 증가 없음 + 첫 화면 수십 KB)은 실측 62,312 B/2요청으로 이미 PASS 였다.
- **소비자 권고(중요)**: `jennysans-dynamic-subset.css` 는 9 웨이트를 모두 선언하므로 CSS 자체가 크다. **9 웨이트가 전부 필요하지 않으면 ① 변수 폰트 CSS(`jennysans-variable.css` 또는 `jennysans-variable-dynamic-subset.css`)를 쓰거나 ② 필요한 웨이트의 `@font-face` 만 골라 쓰라**(예: 400·700 만 쓰면 CSS gzip 약 1/4.5). 이 권고는 release 가 README·`docs/INSTALL.md`·스페시먼 사이트 사용법에도 싣는다.

**QA 합격 기준 (4)**: 표의 (QA 측정) 항목을 Playwright(`page.on('response')` 로 font 요청 수·`content-length` 합산)로 3 페이지 × (정적·변수·분할) 실행해 기록; 목표 초과는 티켓.

## 5. CSS 템플릿

### 5-1. `jennysans.css` — 정적 전체본 9
```css
/* JennySans 1.000 — static, full charset. https://font.jennysoft.co.kr  SIL OFL 1.1 */
@font-face {
  font-family: "JennySans";
  font-style: normal;
  font-weight: 100;
  font-display: swap;
  src: url("../web/JennySans-Thin.woff2") format("woff2");
}
/* … 200 ExtraLight · 300 Light · 400 Regular · 500 Medium · 600 SemiBold · 700 Bold · 800 ExtraBold · 900 Black 반복 … */
```

### 5-2. `jennysans-variable.css` — 변수 전체본 1
```css
/* JennySans 1.000 — variable (wght 100–900), full charset */
@font-face {
  font-family: "JennySans";
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  src: url("../web/JennySansVariable.woff2") format("woff2") tech("variations"),
       url("../web/JennySansVariable.woff2") format("woff2-variations"),
       url("../web/JennySansVariable.woff2") format("woff2");
}
```
- 웹 패밀리명은 정적과 같은 `"JennySans"`(소비자 CSS 를 바꾸지 않고 파일만 교체). 설치용 "JennySans Variable" 과는 별개.

### 5-3. `jennysans-dynamic-subset.css` — 정적 분할본 (@font-face × 9 × 99)
```css
/* JennySans 1.000 — dynamic subset (Google Fonts KR slicing). n = Google slice index; #123 latin, #124 rest */
@font-face {
  font-family: "JennySans";
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url("../web/subset/JennySans-Regular.subset.123.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: "JennySans";
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url("../web/subset/JennySans-Regular.subset.119.woff2") format("woff2");
  unicode-range: U+20-22, U+27-2A, U+2C-38, U+3A-3B, U+3F, U+41-47, U+4A-4C, U+4F-5D, U+61-7B, U+7D, U+A1, U+AB, U+AE, U+B7, U+BB, U+BF, U+2013-2014, U+201C-201D, U+2122, U+AC00, U+ACE0, U+AE30, U+B2E4, U+B85C, U+B9AC, U+C0AC, U+C2A4, U+C2DC, U+C774, U+C778, U+C9C0, U+D558;   /* 빌더가 "Google 범위 ∩ cmap" 으로 생성 */
}
/* … 웨이트 오름차순 → 슬라이스 번호 오름차순으로 반복. 변수판(jennysans-variable-dynamic-subset.css)은 font-weight: 100 900 + JennySansVariable.subset.<n>.woff2 */
```
- 표기: `unicode-range` 는 CSS 문법(`U+AC00-D7A3`, 끝값에 `U+` 없음). charset 파일 표기(`U+XXXX-U+YYYY`)와 다르다.

### 5-4. 소비자 사용 예 (README·설치 가이드) — CDN 경로 `https://font.jennysoft.co.kr/v/1.000/…` (AGENTS §8)
```html
<link rel="preload" href="https://font.jennysoft.co.kr/v/1.000/web/subset/JennySans-Regular.subset.123.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="https://font.jennysoft.co.kr/v/1.000/css/jennysans-dynamic-subset.css">
<!-- 항상 최신: https://font.jennysoft.co.kr/latest/css/jennysans-dynamic-subset.css (캐시 짧음, 버전 고정을 권장) -->
<style>
  :root {
    font-family: "JennySans", "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif;
    font-synthesis: none;             /* 가짜 기울임·굵게 금지(01-family §3) */
    line-height: 1.6;                 /* 네이티브 줄높이 1.193em(03-metrics §2); 한국어 본문 1.5–1.7 권장 */
  }
  table { font-variant-numeric: tabular-nums; }   /* Pretendard 유래 tnum(04-features §4) */
</style>
```
- `preload` 는 라틴 #123 만(한글 슬라이스는 페이지마다 다름). `crossorigin` 필수.
- jsDelivr(npm): `https://cdn.jsdelivr.net/npm/@jennysoft/jennysans@1.0.0/dist/css/jennysans-dynamic-subset.css` (npm 1.0.0 ↔ 폰트 1.000, `01-family.md` §1).

## 6. 서버·CDN (release 가 `deploy/` 에 구현, 스펙은 여기)

| 항목 | 값 | 사유 |
|---|---|---|
| 경로 | `https://font.jennysoft.co.kr/v/<version>/{css,web,web/subset}/…` (`<version>` = 폰트 버전 `1.000`) + **`/latest/` 심링크**(최신 버전으로) | 버전 고정 캐시 + 편의 별칭 |
| `Access-Control-Allow-Origin` | `*` | 웹폰트는 크로스오리진 — **없으면 다른 도메인에서 폰트가 아예 적용되지 않는다**(전역 규칙: `curl` 200 으로 판단 금지, 실제 브라우저에서 확인) |
| `Cache-Control` | `/v/…`: `public, max-age=31536000, immutable` · `/latest/…`: `public, max-age=300` | |
| `Content-Type` | `font/woff2` · `text/css; charset=utf-8` | |
| 압축 | WOFF2 압축 안 함(이미 Brotli). CSS 는 gzip/brotli | |
| HTTP/2 | 켬 | 슬라이스 다중 요청 |
| 서버 | `ssh debc-dev` nginx(AGENTS §2) — 실제 conf 는 release 의 `deploy/nginx-font.conf` | |

## 7. QA 합격 기준 (이 문서 전체)
1. §3 슬라이스 정합 (a)–(f) PASS.
2. §4 측정표 작성(목표 초과는 티켓).
3. Playwright Chromium 으로 `site/test.html`(정적 9·변수·분할 모드)을 열어 한글·스페인어·영어·숫자·기호 샘플이 JennySans 로 렌더(`document.fonts.check()` + 스크린샷), FOIT 없음.
4. CSS 4 파일 파싱 오류 0, `unicode-range` 표기 규격.
5. P7 배포 후: 다른 오리진 테스트 페이지에서 `https://font.jennysoft.co.kr/v/1.000/…` 폰트가 적용되는 스크린샷 + 응답 헤더에 `Access-Control-Allow-Origin: *` (release·QA).

## 8. 갱신 이력
- 2026-09-06: 1차 공통 슬라이스 계획(0~7) 폐기 → Google 124 슬라이스 인덱스 재사용 + rest #124 채택; CDN 경로 `/v/1.000/`·`/latest/`; 1차 빌드 실측 크기 반영·목표 조정; 변수 분할 CSS 추가.
