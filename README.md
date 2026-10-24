# JennySans 「제니산스」

제니소프트의 모든 솔루션(웹·앱·게임·데스크톱 문서·인쇄)에서 공통으로 쓰기 위한 **범용 한글·영문(라틴) 고딕(산세리프) 폰트 패밀리**입니다.
개성보다 **중립성·가독성**을 우선한 본문용 서체로, 현대 한글 11,172자 전부와 유럽 라틴·키릴·그리스, 한국 문서용 기호를 **한 패밀리·9 웨이트 + 변수 폰트**로 제공합니다.

- 라이선스: **SIL Open Font License 1.1**(Reserved Font Names "JennySans", "제니산스") — 상업 이용·수정·재배포·임베드 모두 허용, 폰트 단독 판매만 금지
- 원본: [Pretendard](https://github.com/orioncactus/pretendard) 1.3.9 + [Noto Sans KR](https://github.com/notofonts/noto-cjk) 2.004 의 파생(Modified Version). 글립을 새로 그리지 않고 **선별·보충·재구성·검증**한 폰트입니다 → [§8 원본과 무엇이 다른가](#8-원본과-무엇이-다른가--왜-저작권-문제가-없는가)
- 버전: **1.001**(npm 1.0.1, 2026-10-24 — 체크박스 ☐☑☒ 추가) · 첫 공개 1.000 은 2026-09-09(QA 판정 **RELEASE OK** · 승인 예외 0) · [CHANGELOG](CHANGELOG.md)
- 홈페이지: **https://font.jennysoft.co.kr** — 타입 테스터 · 웨이트 견본 · 문장 견본 · [**글자맵**(전체 글립 탐색)](https://font.jennysoft.co.kr/glyphs.html) · [문자 범위](https://font.jennysoft.co.kr/#charset) · [지원 언어](https://font.jennysoft.co.kr/#languages) · [다운로드](https://font.jennysoft.co.kr/#download) · [사용법](https://font.jennysoft.co.kr/#usage) · 라이선스

> 자체 CDN·다운로드, GitHub 저장소(`gjh999/jennysans`), npm(`jennysans`), jsDelivr 모두 **동작 중**입니다(2026-10-24 공개).

---

## 1. 한눈에 보기

**8차 빌드**(`build/BUILD-REPORT.md` 2026-09-09, 확정본) 실측입니다. KB·MB = 1,000·1,000,000 bytes.

| 항목 | 값 |
|---|---|
| 이름 | 영문 **JennySans** · 한국어 **제니산스** (변수 폰트는 별도 패밀리 "JennySans Variable") |
| 문자 수 | 정적 9종·변수 폰트 모두 **글립 13,983 · cmap 13,257** |
| 내역(Regular cmap) | 한글 음절 11,172 · 첫가끝 자모 256 · 호환 자모 94 · 라틴 318 · 키릴 98 · 그리스 69 · KS X 1001 기호 666 등 |
| 웨이트 | 정적 **9종**(Thin 100 · ExtraLight 200 · Light 300 · Regular 400 · Medium 500 · SemiBold 600 · Bold 700 · ExtraBold 800 · Black 900) + **변수 1종**(`wght` 100–900). **이탤릭 없음** |
| 형식 | **TTF**(glyf) · **WOFF2** 전체본 + `unicode-range` 99 조각 분할본 · **CSS 4종**. OTF(CFF)는 1.1 이후 |
| 용량 | 정적 1웨이트 **2,553,816–2,700,344 bytes**(Regular 2,617,580, 9종 합 23,462,992) · 변수 **7,009,656 bytes** · WOFF2 전체본 647,572–764,252(변수 2,239,472) · 웹 첫 화면은 **페이지에 실제로 쓰인 글자에 따라** 31,144–158,320 bytes(→ §5-1) |
| 수직 메트릭 | UPM 2048, typo = hhea = win **1950 / −494 / 0** + `USE_TYPO_METRICS` — 9 웨이트·변수 전부 동일(굵기를 바꿔도 줄 높이 불변) |
| 라이선스 | **SIL OFL 1.1**, RFN `JennySans`·`제니산스`, `fsType` 0(설치·임베드 제한 없음) |
| 배포 | **홈페이지·CDN·다운로드**(`font.jennysoft.co.kr`) · **GitHub** `gjh999/jennysans`(Release v1.0.1) · **npm** `jennysans@1.0.1` · **jsDelivr**(`cdn.jsdelivr.net/npm/jennysans@1.0.1/…`) — 모두 동작 중 |

### 1-1. 웨이트와 파일 이름

| 스타일 | `font-weight` | 정적 TTF (`dist/static/`) | 웹 WOFF2 (`dist/web/`) |
|---|---|---|---|
| Thin | 100 | `JennySans-Thin.ttf` | `JennySans-Thin.woff2` |
| ExtraLight | 200 | `JennySans-ExtraLight.ttf` | `JennySans-ExtraLight.woff2` |
| Light | 300 | `JennySans-Light.ttf` | `JennySans-Light.woff2` |
| Regular | 400 | `JennySans-Regular.ttf` | `JennySans-Regular.woff2` |
| Medium | 500 | `JennySans-Medium.ttf` | `JennySans-Medium.woff2` |
| SemiBold | 600 | `JennySans-SemiBold.ttf` | `JennySans-SemiBold.woff2` |
| Bold | 700 | `JennySans-Bold.ttf` | `JennySans-Bold.woff2` |
| ExtraBold | 800 | `JennySans-ExtraBold.ttf` | `JennySans-ExtraBold.woff2` |
| Black | 900 | `JennySans-Black.ttf` | `JennySans-Black.woff2` |
| Variable(`wght` 100–900) | 100 900 | `dist/variable/JennySansVariable.ttf` | `JennySansVariable.woff2` |

분할본은 `dist/web/subset/JennySans-<Weight>.subset.<n>.woff2`(웨이트당 99 조각, 라틴은 **#123**).
변수 폰트는 데스크톱에 설치하면 별도 패밀리 **"JennySans Variable"** 로 보입니다(정적 9종과 함께 설치해도 충돌하지 않게 — Pretendard 선례).
이탤릭은 없습니다. 가짜 기울임을 막으려면 CSS `font-synthesis: none;`.

---

## 2. 지원 언어

**총 38개 언어**(표 37행 — "덴마크어·노르웨이어"가 한 행에 2언어)입니다.
판정 기준은 **정서법 필수 문자 + 대표 샘플 문장의 모든 글자가 산출물 cmap 에 실제로 있을 때만 "지원"으로 셈**하는 것입니다.
재현: `PYTHONUTF8=1 python tools/lang_support.py` (→ `site/assets/languages.json`, 대상 `dist/static/JennySans-Regular.ttf`).

| 문자권 | 담긴 것(실측) | 지원 언어 |
|---|---|---|
| **한글** | 현대 한글 완성형 **11,172자 전부**(U+AC00–D7A3) + 첫가끝 자모 **256**(U+1100–11FF, NFD 분해 표시용) + 호환 자모 **94**(U+3131–318E) | **한국어** — 조합 가능한 모든 현대 음절 |
| **라틴** | ASCII · Latin-1 Supplement **96자 전부** · Latin Extended-A **127자 전부** + 결합 악센트 · 유럽 구두점·화폐 | **영어** + **29개 언어**(28행): 스페인어 · 포르투갈어 · 프랑스어 · 독일어 · 이탈리아어 · 네덜란드어 · 폴란드어 · 체코어 · 슬로바키아어 · 헝가리어 · 터키어 · 크로아티아어 · 슬로베니아어 · 루마니아어 · 리투아니아어 · 라트비아어 · 에스토니아어 · 핀란드어 · 스웨덴어 · **덴마크어·노르웨이어** · 아이슬란드어 · 카탈루냐어 · 갈리시아어 · 바스크어 · 몰타어 · 웨일스어 · 아일랜드어 · 에스페란토 <br> 그 밖에 기본 라틴만 쓰는 인도네시아어 · 말레이어 · 스와힐리어 · 타갈로그어 등도 문제없이 표시됩니다(별도 검증 대상은 아님) |
| **키릴** | U+0400–045F **96자 전부** + Ґ ґ(U+0490/0491) = 98자 | **러시아어 · 우크라이나어 · 벨라루스어 · 불가리아어 · 세르비아어 · 마케도니아어 6개 언어 — 알파벳 100% 커버**(누락 0) |
| **그리스** | U+0370–03FF 중 **69자** — 대소문자 전체 + 종형 시그마 ς + 악센트 결합형(ά έ ή ί ό ύ ώ ΐ ΰ ϊ ϋ) 전부 | **현대 그리스어**. 미보유는 단독 악센트 기호 ΄(U+0384) ΅(U+0385) · 아노텔레이아 ·(U+0387) · 고대 KAI 기호 ϗ(U+03CF) 와 **유니코드 미할당 코드포인트 3자**(U+038B·U+038D·U+03A2)뿐이라 본문 표기에는 지장이 없습니다 |

언어별 판정 근거와 샘플 문장은 홈페이지 **[지원 언어](https://font.jennysoft.co.kr/#languages)** 절에서 실제로 렌더된 상태로 볼 수 있습니다.

### 지원하지 않는 것 (숨기지 않고 밝힙니다)

| 언어·문자 | 상태 |
|---|---|
| **일본어(가나·한자)** · **중국어(간체·번체)** | **JennySans 에는 없습니다.** 별도 패밀리 `JennySans JP` / `SC` / `TC` 로 예정 → [§3 패밀리 구조](#3-패밀리-구조) |
| **한국 문서용 한자**(KS X 1001 4,620자) | 1.000 에는 없음. **1.100 에서 JennySans 본 패밀리에 포함** 예정 → [§10 로드맵](#10-로드맵) |
| **베트남어** | **현재 미지원** — 성조 결합 글자(U+1EA0–1EF9 등) 48자가 없어 판정에서 제외됐습니다. **1.100 에 포함** 예정([§10](#10-로드맵)) |
| **태국어 · 아랍어 · 히브리어 · 데바나가리** 등 | **범위 밖**. 결합·연결·우횡서 등 셰이핑 규칙이 근본적으로 다르고 원본도 보유하지 않아, 요구가 생기면 **별도 프로젝트**로 다룹니다 |
| 옛한글 조합(첫가끝 조합 피처) · 이탤릭 · 이모지 컬러 글립 | 범위 밖(자모 **단독 글립**은 들어 있습니다) |

---

## 3. 패밀리 구조

**JennySans 는 한국어판입니다.** 일본어·중국어는 같은 파일에 넣지 않고 **별도 패밀리**로 냅니다.

| 패밀리 | 담는 문자 | 상태 |
|---|---|---|
| **JennySans** (한국어판) | 한글 11,172 · 자모 · 라틴 · 키릴 · 그리스 · KS X 1001 기호 (+ 1.100 부터 **한국식 자형의 한자** · 베트남어 · 확장 키릴) | **1.000 릴리스 준비 중** |
| **JennySans JP** | 가나 + 일본식 자형의 한자(JIS 제1·2수준) | 예정(1.100 이후) |
| **JennySans SC** | 간체자(GB 2312) | 예정 |
| **JennySans TC** | 번체자(Big5) | 예정 |

**왜 나누나 — 용량이 아니라 자형 때문입니다.**
같은 한자 코드포인트라도 한국·일본·중국의 **표준 자형이 서로 다릅니다**(예: 骨·直·今 계열의 획 처리). 한 파일에 여러 지역 자형을 넣으면 `locl` 피처와 언어 태그가 있어야 올바른 자형이 나오는데, **언어 태그를 넘기지 않는 앱·엔진이 많아** 엉뚱한 지역의 자형이 표시됩니다.
그래서 Noto Sans CJK·Source Han Sans 도 KR / JP / SC / TC 를 **별개 패밀리**로 배포합니다. JennySans 도 같은 구조를 따릅니다.

JP/SC/TC 는 **라틴·숫자·기호·수직 메트릭을 JennySans 와 동일하게** 맞출 계획이라, 폴백 체인으로 섞어 써도 이질감이 없습니다.

```css
font-family: "JennySans", "JennySans JP", "JennySans SC", sans-serif;   /* JP/SC 공개 후 */
```

---

## 4. 다운로드

zip 4종 + `SHA256SUMS.txt`. 실측치는 릴리스 패키지(`dist/packages/index.json` 2026-10-24 15:04, 1.001) 기준입니다.

| 패키지 | 내용 | 크기 | SHA-256(앞 8자리) |
|---|---|---|---|
| **`JennySans-1.001-desktop.zip`** | 정적 TTF 9종 + 설치 안내 + LICENSE 류 (13 파일) | 10,064,037 B (10.1 MB) | `9eb23f74` |
| **`JennySans-1.001-web.zip`** | WOFF2 전체본 9 + 변수 1 + 분할본 + CSS 4종 + LICENSE 류 (1,008 파일) | 23,415,240 B (23.4 MB) | `47c8415a` |
| **`JennySans-1.001-variable.zip`** | `JennySansVariable.ttf` + `.woff2` + `jennysans-variable.css` + LICENSE 류 (7 파일) | 5,434,264 B (5.4 MB) | `91748e45` |
| **`JennySans-1.001-all.zip`** | 위 전부 + 문서 (1,021 파일) | 약 36.7 MB | `SHA256SUMS.txt` 참조(이 README 를 담고 있어 여기 적을 수 없음) |

> zip 의 크기·SHA-256 은 **서버의 [`/download/SHA256SUMS.txt`](https://font.jennysoft.co.kr/download/SHA256SUMS.txt) 가 정본**입니다. `all.zip` 은 문서를 담고 있어 문서를 고치면 값이 달라지므로, 받은 파일을 검증할 때는 서버의 그 파일과 대조하세요.

- **홈페이지(동작 중)**: `https://font.jennysoft.co.kr/download/<파일명>` · 체크섬 `https://font.jennysoft.co.kr/download/SHA256SUMS.txt`
- **CDN(동작 중)**: `https://font.jennysoft.co.kr/v/1.001/…` (1.001 배포 후 · 1.000 경로도 유지, 버전 고정, 1년 immutable) · `https://font.jennysoft.co.kr/latest/…`
- GitHub Releases: `https://github.com/gjh999/jennysans/releases` (1.0.1 부터 공개) · npm: `npm i jennysans` (1.0.1 부터 공개)

전체 SHA-256 은 `SHA256SUMS.txt` 와 `dist/packages/index.json` 에 있습니다(폰트 파일 개별 해시 포함).

---

## 5. 빠른 사용법

자세한 것은 **[docs/INSTALL.md](docs/INSTALL.md)** 에 플랫폼별로 있습니다.

### 5-1. 웹 — CSS 4종 중 하나를 고르세요

| CSS | 내려받는 것 (8차 빌드 실측) | 이럴 때 |
|---|---|---|
| **`jennysans-dynamic-subset.css`** | 페이지에 **실제로 쓰인 글자가 든 조각만** — 웨이트당 99 조각(전 웨이트 2,264–31,340 B). 실제 전송량은 아래 실측표 참조. 단 **CSS 파일 자체가 448,127 B(gzip 101,348 B)** — 9 웨이트 × 99 조각 = `@font-face` 891개이기 때문 | **한국어 웹페이지 기본 권장.** 9 웨이트를 다 쓰지 않는다면 아래 권고 참고 |
| `jennysans.css` | 웨이트별 전체본 1 파일(647,572–764,252 B, Regular 726,032 B) | 인트라넷·오프라인, 쓰는 웨이트가 1~2개일 때 |
| `jennysans-variable.css` | 변수 폰트 전체본 1 파일(2,239,472 B, `wght` 100–900). CSS 자체는 679 B | 한 페이지에서 웨이트를 4개 이상 쓸 때 총량 최소 |
| `jennysans-variable-dynamic-subset.css` | 변수 폰트를 99 조각으로(조각당 3,408–90,472 B, 라틴 69,304 B). CSS 69,422 B(gzip 12,454 B) | 변수 + 한국어 페이지. 조각이 정적의 2~3배라 웨이트 4개 이상일 때만 이득 |

```html
<!-- 자체 CDN (동작 중) -->
<link rel="preload" href="https://font.jennysoft.co.kr/v/1.000/web/subset/JennySans-Regular.subset.123.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="https://font.jennysoft.co.kr/v/1.000/css/jennysans-dynamic-subset.css">

<!-- jsDelivr(npm) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jennysans@1.0.0/dist/css/jennysans-dynamic-subset.css">

<style>
  :root {
    font-family: "JennySans", "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif;
    font-synthesis: none;            /* 가짜 기울임·가짜 굵게 금지 */
  }
  table, .tabular { font-variant-numeric: tabular-nums; }   /* 표 숫자 자릿수 맞춤 */
</style>
```

**첫 화면에 실제로 내려가는 양**(`PYTHONUTF8=1 python tools/first_paint.py` 실측 — 페이지에 쓰인 글자에 따라 달라집니다):

| 페이지 | 조각 수 | 전송량 |
|---|---|---|
| 라틴 전용 · 한 웨이트 | 1 | **31,144 B (30.4 KB)** |
| 한국어 한 문장 · 한 웨이트 | 7 | **85,420 B (83.4 KB)** |
| 한국어 소개문 한 문단 · 한 웨이트 | 9 | **105,312 B (102.8 KB)** |
| 한국어 두 문단 + 제목 · 두 웨이트(400·700) | 13 | **158,320 B (154.6 KB)** |

(KB = 1,024 bytes. 같은 페이지를 전체본 CSS 로 받으면 웨이트당 726,032 B 이므로, 한글 페이지에서도 분할본이 약 7~23배 가볍습니다.)

> **9 웨이트가 전부 필요하지 않다면** `jennysans-variable.css`(변수 폰트, CSS 679 B)를 쓰거나, `jennysans-dynamic-subset.css` 에서 **쓰는 웨이트의 `@font-face` 블록만 남겨** 쓰세요.
> 분할 CSS 는 9 웨이트 × 99 조각 = `@font-face` 891개라 **CSS 파일 자체가 448,127 B(gzip 101,348 B)** 입니다. 폰트 전송량(위 표)과는 별개로 CSS 파싱 비용이 듭니다.

- `preload` 는 라틴 조각 **#123** 하나만(한글 조각은 페이지마다 달라 브라우저에 맡깁니다).
- self-host 는 `dist/css/` 와 `dist/web/` 를 같은 상대 구조로 올리면 CSS 수정이 필요 없습니다. **다른 도메인에서 폰트를 받아 쓰면 서버가 `Access-Control-Allow-Origin` 헤더를 내야 합니다**(`docs/INSTALL.md` §5, `deploy/nginx-font.conf`).
- 줄 높이 기본값(`line-height: normal`)은 약 **1.19**(= (1950 + 494) / 2048). 본문은 1.5~1.7 을 권장합니다.

### 5-2. 데스크톱(Windows · macOS · 한글 · MS Office · Photoshop/Illustrator)

`JennySans-1.000-desktop.zip` 의 TTF 9개를 설치합니다.
Windows 의 옛 폰트 API(GDI)를 쓰는 앱에서는 Regular·Bold 외 웨이트가 "JennySans Light" 처럼 **별도 패밀리로 보입니다**(OpenType 관례, 정상). 설치 방법·기존 버전 교체 주의·프로그램별 웨이트 선택은 [docs/INSTALL.md](docs/INSTALL.md) §1~§4.

### 5-3. Flutter

```yaml
flutter:
  fonts:
    - family: JennySans
      fonts:
        - { asset: assets/fonts/JennySans-Regular.ttf,  weight: 400 }
        - { asset: assets/fonts/JennySans-Medium.ttf,   weight: 500 }
        - { asset: assets/fonts/JennySans-Bold.ttf,     weight: 700 }
```

```dart
ThemeData(fontFamily: 'JennySans');
Text('제니산스 ¿Qué tal, señor?', style: TextStyle(fontWeight: FontWeight.w600));
```

정적 TTF 1개가 약 2.6 MB 이므로 **실제로 쓰는 웨이트만** 선언하세요(9종 전부는 약 24 MB). 9 웨이트가 모두 필요하면 변수 TTF 1개(7.0 MB)가 더 작습니다. 웹 빌드 팁은 `docs/INSTALL.md` §6.

### 5-4. Unity(TextMesh Pro) · Godot 4

- **Unity**: `dist/static/JennySans-<Weight>.ttf` → Font Asset Creator. 한글 11,172자를 정적 아틀라스로 굽지 말고 **Dynamic 모드(+ Multi Atlas Textures)** 또는 KS X 1001 2,350자 정적 아틀라스를 쓰세요(`docs/INSTALL.md` §7).
- **Godot 4**: TTF 를 그대로 임포트(`FontFile`), 변수 TTF 는 `FontVariation.variation_opentype` 에 `wght`(`docs/INSTALL.md` §8).

---

## 6. 문자 범위

유니코드 기준으로 범위를 정의하고(`charset/required.txt` 12,602 코드포인트 + `recommended.txt` 898 + `korean-old.txt` 103 = 빌드 대상 13,603), 전 웨이트에서 빠짐없이 들어 있는지 검사합니다 — **8차 빌드 required 12,602/12,602, 누락 0**(정적 9종·변수 전부).

| 영역 | 내용 |
|---|---|
| 한글 | 현대 한글 완성형 **11,172자 전부**(U+AC00–D7A3) · 호환 자모 94(U+3131–318E) · 첫가끝 자모 256(U+1100–11FF) · 자모 확장 A/B 101 |
| 라틴 | ASCII · **Latin-1 Supplement 96 전부** · **Latin Extended-A 127 전부** · 결합 악센트 13종(NFD 입력 대응) · 크로아티아어 합자 Ǆǅǆ Ǉǈǉ Ǌǋǌ |
| 키릴·그리스 | 키릴 U+0400–045F 96 전부 + Ґґ · 그리스 69 |
| 기호 | KS X 1001 기호(※ ① ㉠ ㈜ ㎏ ㎡ ℃ ← → ★ ○ ■ 「」『』 등 행 1~3·6~9 전부) · 괘선 U+2500–257F 128 · 블록 요소 32 · 일반 구두점 · 화폐(₩ € ₹ 등) · 화살표 · 기본 수학 · 도형 · 로마숫자 · 분수 · 상하첨자 · 전각 영숫자 |
| 자체 합성 | 원본에서 그대로 가져올 수 없어 **부품 조합·미러로 만든 11자** — 두 원본 어디에도 없던 KS 기호 6자 **￢ ￣ ￤**(U+FFE2–FFE4) · **⅔**(U+2154) · **≒**(U+2252) · **◈**(U+25C8), Noto ∽ 를 좌우 반전한 **∼**(U+223C), `D`+`Zcaron` 컴포지트 **DŽ**(U+01C4), 그리고 1.001 의 체크박스 **☐ ☑ ☒**(U+2610–2612 — 같은 웨이트의 □ 그대로 + ✓ / × 를 축소해 속공간 중앙 배치). 근거 `docs/spec/07-supplement.md` §5 · `CHANGELOG.md` 1.001 |
| 범위 밖 | 한자(1.100 예정) · 가나 · 중국어 · 베트남어(1.100 예정) · 옛한글 조합 · 이탤릭 · 이모지 |

**OpenType 기능**은 원본 Pretendard 의 것을 그대로 보존합니다 — 실측(Regular, 49개):
GSUB `aalt calt case ccmp clig cv01–cv05 cv07–cv13 dlig dnom frac fwid locl numr ordn pnum pwid salt sinf ss01–ss03 ss05–ss08 ss10–ss15 subs sups tnum zero`, GPOS `cpsp kern mark mkmk`.
(`ss16` 은 원본의 PUA 아이콘 전용이라 서브셋 후 빈 피처가 되어 제거됐습니다.)
숫자는 기본 **가변폭 라이닝**입니다. 표·시계처럼 자릿수를 맞추려면 `tnum`(CSS `font-variant-numeric: tabular-nums`).
**세로쓰기는 지원하지 않습니다** — 8차 빌드에서 `vhea`·`vmtx`·`VVAR`·`VORG` 를 10개 파일 전부에서 제거해 가로쓰기 전용임을 명확히 했습니다.

---

## 7. 품질·검증

릴리스 게이트 8항목(커버리지·셰이핑·fontbakery·패밀리 묶임·메트릭·파일 크기·렌더 실측·라이선스, `AGENTS.md` §4)을 기준으로,
**fontbakery(정적·변수) · HarfBuzz 전수 셰이핑 · 커버리지 전수 · 메트릭 · name/RFN 전수 · Windows 설치 실측 · 브라우저 실측 · 패키지 검사**를 거쳤습니다.
빌더 자체 점검은 **PASS**(WARN 0, 항목 112 — `build/verify-report.md`)이고, **fontbakery 는 정적·변수 패밀리 각각 FAIL 0**(승인 예외를 쓰지 않고)입니다.
남은 WARN 63건(9개 검사 ID)은 원본에서 물려받은 정보성 항목이며 사유가 기록돼 있습니다.

8차 빌드에서 마지막까지 남아 있던 지적을 전부 정리했습니다.

| 항목 | 조치 | 결과 |
|---|---|---|
| 변수 폰트 중첩 컴포넌트 | 평탄화 채택 기준을 글립 성격별로 정정(Noto 유래 ≤2 unit / 컴포지트 ≤8 unit) | **167건 전량 해소 → 0** (외곽선 불변, 평탄화 전후 bbox 차 ≤0.41 unit 로 증명) |
| 세로쓰기 테이블 비대칭 | `vhea`·`vmtx`·`VVAR`·`VORG` 를 10개 파일에서 제거 | Thin·ExtraLight·Light 에만 있던 비대칭 해소(각 −54 KB) |
| 고아 글립(어디서도 참조되지 않는 글립) | 정적 4자·변수 6자 제거(도달 가능 집합을 cmap·GSUB/GPOS·컴포넌트 폐포까지 계산해 보수적으로 판정) | fontbakery 경고 73 → **63건**, 새 경고 0, 셰이핑 영향 0 |

> QA 최종 판정은 **RELEASE OK(조건 없음 · 승인 예외 0)** 입니다 — 근거 전문 [`docs/qa/QA-REPORT-1.000.md`](docs/qa/QA-REPORT-1.000.md), 결함 티켓 이력 [`docs/qa/ISSUES.md`](docs/qa/ISSUES.md).

---

## 8. 원본과 무엇이 다른가 · 왜 저작권 문제가 없는가

가장 많이 받는 질문이라 구체적으로 적습니다.

### 8-1. 저작권 — 안전한 이유는 "닮지 않아서"가 아닙니다

- 한국 법에서 **글자체 도안 자체는 저작권 보호 대상이 아닙니다**(대법원 1996. 8. 23. 선고 **94누5632**). 반면 **폰트 파일은 컴퓨터프로그램저작물로 보호됩니다**(대법원 2001. 6. 29. 선고 **99다23246**).
  따라서 "다른 고딕과 닮았다"는 것은 저작권 쟁점이 아니며, 쟁점은 **파일을 쓸 권리가 있느냐**입니다.
- JennySans 가 안전한 진짜 이유는 **원본이 SIL OFL 1.1** 이고 그 조건을 전부 지켰기 때문입니다.
  1. **원저작권 고지 유지** — `LICENSE` 머리에 원본 저작권 5블록, 폰트 안 name ID 0·7·9 에 동일 고지
  2. **파생물도 OFL 1.1 로 배포** — 같은 자유를 그대로 넘깁니다
  3. **원본 Reserved Font Name 미사용** — `Pretendard` · `Source` · `Inter` · `M PLUS` · `Noto` 가 식별 레코드(name ID 1/2/3/4/6/16/17/18/21/22/25)·fvar 인스턴스명·STAT 이름·글립명 **어디에도 없음**(10개 파일 전수 검사 PASS)
  4. **폰트 파일 단독 판매 금지** — OFL 요구를 그대로 유지
- 후보 조사 단계에서 **수정 금지 조건의 무료 폰트, 라이선스 원문을 확인할 수 없는 폰트, 임베딩 제한(`fsType`)이 걸린 폰트는 전부 배제**했습니다(`docs/research/01-benchmark.md`).
- 자세한 법적 정리(저작권 등록·상표 출원·디자인권)는 [docs/LEGAL-REGISTRATION.md](docs/LEGAL-REGISTRATION.md), OFL 요지는 [docs/OFL-FAQ-ko.md](docs/OFL-FAQ-ko.md).

### 8-2. 원본과의 실제 차이 (Regular 기준 cmap 실측)

**글자 외곽선은 새로 그리지 않았습니다.** 차이는 "무엇을 담고 어떻게 조립했는가"입니다.

| 항목 | Pretendard 1.3.9 | JennySans 1.001 | 차이 |
|---|---|---|---|
| 첫가끝 자모 U+1100–11FF | 0 | 256 | **+256** |
| 옛 호환 자모(U+3130–318F) | 53 | 94 | **+41** |
| 자모 확장 A·B | 0 | 101 | **+101** |
| 괘선 U+2500–257F | 0 | 128 | **+128** |
| 블록 요소 U+2580–259F | 0 | 32 | **+32** |
| 원문자 · 괄호문자(U+2460–24FF · U+3200–32FF) | 59 | 253 | **+194** |
| 수학 기호 U+2200–22FF | 16 | 76 | **+60** |
| 도형·기타 기호(U+25A0–25FF, U+2600–26FF) | 31 | 77 | **+46** |
| 단위 U+3380–33DF | 80 | 96 | **+16** |
| 일본어 가나 U+3040–30FF | 184 | 1 | **−183 (제거)** |

합계: **한국 문서용 문자 +874자 추가, 쓰지 않는 가나 183자 제거.**
전체 관점으로는 **추가 912자 / 제외 1,991자**(cmap 14,336 → 13,257)입니다. 제외가 큰 것은 가나·한자 보조 글립 등 **범위 밖 문자를 덜어냈기** 때문입니다.
재현: `PYTHONUTF8=1 python tools/origin_diff.py --md`

- **자체 제작 글립 11자**: 1.001 의 체크박스 ☐ ☑ ☒(U+2610–2612, 같은 웨이트의 □ 그대로 + ✓ / × 축소 배치) 와 ￢ ￣ ￤(U+FFE2–FFE4) · ⅔(U+2154) · ≒(U+2252) · ◈(U+25C8) 은 **두 원본 어디에도 없어** Pretendard 부품에서 합성했고, ∼(U+223C) 은 Noto ∽ 좌우 반전, DŽ(U+01C4) 는 `D`+`Zcaron` 컴포지트입니다(`docs/spec/07-supplement.md` §5).
- **구조 개선**: 9 웨이트 + 변수 폰트의 **수직 메트릭 통일**(굵기를 바꿔도 줄 높이 불변) · 한 패밀리로 묶이는 이름 체계(name/STAT/fvar 재작성) · **웹 990 조각 분할**(페이지에 쓰인 글자만 내려받음 — §5-1) · fontbakery 지적 결함 수정(중첩 컴포넌트 전량 평탄화 · 스마트 드롭아웃 힌트(`prep`) 추가 · Mac name 레코드 제거 · DŽ(U+01C4) 보충 · 변수 폰트 변환 컴포넌트 분해 · 세로쓰기 테이블·고아 글립 제거) — **원본에는 남아 있는 항목들입니다**.

> **JennySans 는 새로 그린 서체가 아니라, 한국 문서·다국어 실무에 맞게 재구성하고 검증한 OFL 배포판입니다.**

### 8-3. 크레딧 — 이 글자들을 그린 사람들

OFL 조항 4 에 따라 기여를 밝히는 것이며, 원저작자가 JennySans 를 보증한다는 뜻이 아닙니다.

| 원본 | 저작권자·디자이너 | JennySans 에서의 역할 |
|---|---|---|
| **Pretendard** 1.3.9 | **Kil Hyung-jin (길형진)** — https://github.com/orioncactus/pretendard | **주원본**. 한글·라틴·기호·OpenType 기능·변수 축 |
| **Inter** | **Rasmus Andersson** / The Inter Project Authors — https://github.com/rsms/inter | Pretendard 의 라틴·그리스·키릴 골격 |
| **Source Han Sans / Noto Sans CJK** | **Adobe** — Ryoko Nishizuka 西塚涼子(가나·표의문자), Paul D. Hunt(라틴·그리스·키릴), **Sandoll Communications 산돌커뮤니케이션 · Jang Soo-young 장수영 · Kang Joo-yeon 강주연**(한글) | Pretendard 의 한글 골격 |
| **M PLUS 1p** | The M+ FONTS Project Authors — **Coji Morishita**, UNDERFOREST DESIGN — https://github.com/coz-m/MPLUS_FONTS | Pretendard 의 가나(JennySans 에서는 범위 밖으로 제외, **고지는 보존**) |
| **Noto Sans KR** 2.004 | **Adobe**(Google Fonts 변수 빌드) — https://github.com/notofonts/noto-cjk | **보충원본**. 첫가끝 자모·호환 자모 잔여·괘선·원문자·KS 기호 등 909 글립 |
| 도구 | fontTools · HarfBuzz(uharfbuzz) · fontbakery · brotli · Pillow · Playwright | 빌드·검사(배포물에 포함되지 않음) |

원문 그대로의 저작권 문구·SHA-256·우리가 한 변경 내역은 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) 에 있습니다.
편집·구성·엔지니어링: **JennySoft**(https://jennysoft.co.kr).

---

## 9. 라이선스

JennySans 는 **SIL Open Font License 1.1** 로 배포됩니다(Reserved Font Names: **"JennySans"**, **"제니산스"**).

- **상업적 이용 자유** — 유료 앱·게임·소프트웨어에 번들·임베드해 팔아도 되고, 이 폰트로 만든 인쇄물·영상·로고도 자유롭게 판매할 수 있습니다(조항 2·5, `fsType` 0).
- **수정·재배포 자유** — 서브셋·형식 변환·글립 수정 모두 가능. 단 배포본은 **OFL 로만** 배포하고 `LICENSE` 사본을 함께 둬야 합니다(조항 2·5).
- **폰트 파일 단독 판매만 금지**(조항 1) · **이름은 예약(RFN)** — 수정본에 "JennySans"·"제니산스" 이름을 쓸 수 없습니다(조항 3).

무엇이 되고 무엇이 안 되는지 조항 원문과 실무 표로 정리한 문서: **[docs/OFL-FAQ-ko.md](docs/OFL-FAQ-ko.md) 「상업적 이용」 절**.
전문 [LICENSE](LICENSE) · 원본 고지 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) · 상표·저작권 등록 안내 [docs/LEGAL-REGISTRATION.md](docs/LEGAL-REGISTRATION.md).

---

## 10. 로드맵

| 버전 | 내용 | 상태 |
|---|---|---|
| **1.000** | 정적 9종 + 변수 + 웹(WOFF2·분할·CSS 4종) | **2026-09-09 공개** |
| **1.001** | 체크박스 ☐ ☑ ☒(U+2610–2612) 9 웨이트·변수 폰트 추가, 소개 문구 "한글·영문(라틴)" | **2026-10-24** |
| **1.100** | **한자 KS X 1001 4,620자**(Noto Sans KR 에 4,619 보유) + **베트남어 92자** + **카자흐·몽골 키릴 18자**(둘 다 Inter 에 전량 존재 → 디자인 정합) | 1.000 공개 직후 착수 |
| 이후 | `JennySans JP` → `JennySans SC` / `TC` (별도 패밀리) · OTF(CFF) 검토 | 예정 |

**1.100 예상 용량**(팀장 실측 `build/hanja-measure.md`): 정적 1웨이트 약 **4.2 MB**(현재 2.6) · 정적 9웨이트 합 약 37 MB(현재 23.5) · 변수 약 **9.5 MB**(현재 7.0).
**웹 분할본은 영향이 없습니다** — 한자 슬라이스는 페이지에 한자가 실제로 나올 때만 내려갑니다.
베트남어·확장 키릴은 웨이트당 약 +35 KB 입니다.

자세한 계획은 [docs/ROADMAP.md](docs/ROADMAP.md).

---

## 11. 문서

| 문서 | 내용 |
|---|---|
| [CHANGELOG.md](CHANGELOG.md) | 버전별 변경 이력(1.000·1.001 상세, 1.100 예정) |
| [LICENSE](LICENSE) | OFL 1.1 전문 + 누적 저작권 헤더 |
| [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) | 원본별 버전·출처 URL·SHA-256·저작권 원문·우리가 한 변경 |
| [docs/INSTALL.md](docs/INSTALL.md) | 설치·사용 가이드(Windows·macOS·한글·Office·Adobe·웹·Flutter·Unity·Godot·문제 해결) |
| [docs/DISTRIBUTION.md](docs/DISTRIBUTION.md) | 배포 채널·버전 정책·CDN·캐시·릴리스 체크리스트·상표/npm 이름 조사 |
| [docs/ADOPTION.md](docs/ADOPTION.md) | 사내 솔루션(Q 시리즈 Flutter 앱·LatinBeat·Qaudio 등) 적용 절차 |
| [docs/LEGAL-REGISTRATION.md](docs/LEGAL-REGISTRATION.md) | 저작권 등록·상표 출원·디자인권 판단과 절차 |
| [docs/SEO_REGISTRATION.md](docs/SEO_REGISTRATION.md) | 검색엔진 등록(Google·네이버·다음·Bing) 절차 |
| [docs/OFL-FAQ-ko.md](docs/OFL-FAQ-ko.md) | OFL 1.1 한국어 요지(무엇이 되고 무엇이 안 되나) |
| [docs/ROADMAP.md](docs/ROADMAP.md) · [docs/PROGRESS.md](docs/PROGRESS.md) | 단계별 계획 · 진행 기록 |
| `docs/research/` | 원본 폰트 벤치마킹·라이선스 실측·커버리지 조사 |
| `docs/spec/` | 설계 스펙(문자집합·이름·메트릭·OpenType·웹·라이선스·보충 이식) |
| `docs/qa/` | QA 판정·티켓·fontbakery 리포트·셰이핑/렌더 결과 |
| `charset/README.md` | 문자집합 정의와 근거(`required` / `recommended` / `korean-old`) |
| [AGENTS.md](AGENTS.md) | 프로젝트 단일 원본 룰(제작 방식·품질 기준·결정 기록) |
| `site/` · `deploy/` · `tools/` | 홈페이지(`index.html` · **글자맵 `glyphs.html`** · QA 격자 `test.html`) · 서버 배포(nginx·인증서) · 빌드 파이프라인(`origin_diff.py` · `lang_support.py` · `first_paint.py` 로 이 문서의 수치를 재현) |

---

## Summary in English

**JennySans** (Korean name 제니산스) is a general-purpose sans-serif type family by **JennySoft** for Korean & English (Latin) text, released under the **SIL Open Font License 1.1** (Reserved Font Names "JennySans" and "제니산스"). It is not newly drawn: it is a curated, supplemented and verified OFL redistribution built from **Pretendard 1.3.9** (which itself builds on Inter, Source Han Sans / Noto Sans CJK and M PLUS 1p) and **Noto Sans KR 2.004**, with unified naming and vertical metrics, 909 supplemented glyphs the base font lacked, four glyphs synthesised from existing parts, and web packaging. All original copyright notices are preserved in `LICENSE` and `THIRD-PARTY-NOTICES.md`, and no source Reserved Font Name appears in any identifying record, glyph name, `fvar` instance or `STAT` entry.

Version 1.001 ships **9 static weights** (Thin 100 – Black 900, no italics) and **one variable font** (`wght` 100–900), each with **13,983 glyphs / 13,257 mapped code points**: all **11,172 modern Hangul syllables**, 256 conjoining jamo, 94 compatibility jamo, ASCII plus the complete Latin-1 Supplement and Latin Extended-A (verified against the orthographies of **38 languages in total** — Spanish, Portuguese, French, German, Italian, Dutch, Polish, Czech, Slovak, Hungarian, Turkish, Croatian, Slovene, Romanian, Lithuanian, Latvian, Estonian, Finnish, Swedish, Danish, Norwegian, Icelandic, Catalan, Galician, Basque, Maltese, Welsh, Irish, Esperanto and English), the full **Cyrillic U+0400–045F** block (100% of the Russian, Ukrainian, Belarusian, Bulgarian, Serbian and Macedonian alphabets), basic **Greek**, and the **KS X 1001** Korean document symbol set (circled and parenthesised forms, units, box drawing, arrows, geometric shapes, CJK punctuation). Formats are **TTF** for desktop, Flutter, Unity and Godot, and **WOFF2** — full files plus 99 `unicode-range` slices per weight, so a typical Korean page loads about **54 KB per weight** on first paint. Four ready-made CSS files are included.

**Not covered:** Japanese and Chinese (planned as the separate families `JennySans JP` / `SC` / `TC`, because the same Han code points have different regional standard forms and language-tag-dependent `locl` switching is unreliable), Han characters for Korean documents and Vietnamese (both planned for **1.100**), and scripts with different shaping models such as Thai, Arabic, Hebrew and Devanagari (out of scope). **In short:** free for commercial use, modification, redistribution, bundling and embedding; the font files may not be sold on their own; modified versions must not use the names "JennySans" or "제니산스" and must remain under the OFL. Homepage and downloads: **https://font.jennysoft.co.kr**.
