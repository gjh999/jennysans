# JennySans 설치·사용 가이드 (플랫폼별)

> 대상 버전 1.000. 파일 이름·경로는 `README.md` §1-1 표를 따릅니다. 실측 수치(파일 크기 등)는 **8차 빌드 확정본** `build/BUILD-REPORT.md`(2026-09-09, 빌더 자체 점검 PASS · fontbakery FAIL 0)와 `dist/packages/index.json`(10:10 재생성) 기준이며 KB = 1,000 bytes 입니다.
> 이 문서의 "확인 못 함" 표시는 제니소프트가 직접 실측하지 못한 항목입니다.

## 0. 어떤 파일을 쓰나

| 쓰는 곳 | 파일 | 비고 |
|---|---|---|
| Windows·macOS 설치, 한글(HWP)·MS Office·Photoshop/Illustrator·인쇄 | `dist/static/JennySans-<Weight>.ttf` (9개) | 1.000 은 TTF 만. OTF(CFF)는 1.1 이후 |
| 변수 폰트 지원 앱(Adobe·Figma·브라우저·Godot) | `dist/variable/JennySansVariable.ttf` | 설치하면 패밀리 "JennySans Variable" 로 정적과 따로 보임 |
| 웹 | `dist/css/*.css` + `dist/web/*.woff2` (+ `dist/web/subset/`) | §4 |
| Flutter·Unity·Godot | `dist/static/*.ttf` (Godot 은 변수 TTF 도 가능) | §6~§8 |

> **JennySans 는 한국어판입니다.** 1.000 에는 한자·가나·중국어·베트남어가 없습니다(한자·베트남어는 1.100, 일본어·중국어는 별도 패밀리 `JennySans JP`/`SC`/`TC` 예정). 지원 언어·패밀리 구조는 `README.md` §2·§3 을 보세요. 범위 밖 글자는 **폴백 폰트**가 그립니다 — 폴백 스택을 항상 지정하세요.

---

## 1. Windows 10 / 11

### 1-1. 설치
- **사용자 설치**(관리자 권한 불필요): TTF 파일을 선택 → 마우스 오른쪽 → **설치**. 여러 파일을 한꺼번에 선택해도 됩니다.
  설치 위치 `%LOCALAPPDATA%\Microsoft\Windows\Fonts`. 이 PC 의 **내 계정에서만** 보입니다.
- **모든 사용자용 설치**(관리자 권한): 오른쪽 클릭 → **모든 사용자용으로 설치**. 위치 `C:\Windows\Fonts`. 공용 PC·서버·다른 계정으로 실행되는 서비스(예: 서버에서 PDF 를 만드는 프로그램)에는 이쪽이 필요합니다.
- 설정 앱: **설정 → 개인 설정 → 글꼴** 창에 TTF 파일을 끌어다 놓아도 됩니다.

### 1-2. 기존 버전을 교체할 때 (중요)
1. 폰트를 쓰고 있는 프로그램을 **전부 종료**합니다(한글, Word/Excel/PowerPoint, 브라우저, Photoshop, 메신저 등). 사용 중인 폰트 파일은 잠겨서 교체가 실패하거나 옛 파일이 남습니다.
2. **설정 → 개인 설정 → 글꼴** 에서 `JennySans`, `JennySans Light` … 항목을 찾아 **제거**합니다(웨이트별로 항목이 따로 있습니다 — §3-4 참고).
3. 새 TTF 를 설치합니다.
4. 프로그램을 다시 열었는데도 옛 모양·옛 버전이 보이면 **재부팅**하거나 관리자 PowerShell 에서 폰트 캐시를 재시작합니다:
   ```powershell
   Stop-Service FontCache; Start-Service FontCache
   ```
5. 사용자 설치본과 모든 사용자용 설치본이 **같은 이름으로 둘 다** 있으면 어느 쪽이 쓰이는지 프로그램마다 달라집니다. **한 곳에만** 설치하세요.

### 1-3. 설치 확인
```powershell
Add-Type -AssemblyName System.Drawing
[System.Drawing.Text.InstalledFontCollection]::new().Families | Where-Object Name -like 'JennySans*' | Select-Object -ExpandProperty Name
```
`JennySans`, `JennySans Thin`, `JennySans ExtraLight`, `JennySans Light`, `JennySans Medium`, `JennySans SemiBold`, `JennySans ExtraBold`, `JennySans Black` 가 보이면 정상입니다(GDI 기준 8개 패밀리명 — Regular 와 Bold 는 `JennySans` 하나로 묶임. 이유는 §3-4).

---

## 2. macOS

- TTF 를 더블클릭 → **서체 설치**(Font Book/서체 관리자). 여러 파일을 선택해 Font Book 창에 끌어다 놓아도 됩니다.
- 위치: **사용자**(`~/Library/Fonts`, 내 계정) / **컴퓨터**(`/Library/Fonts`, 모든 계정 — 관리자 암호). Font Book **설정 → 기본 설치 위치**에서 바꿉니다.
- 교체: Font Book 에서 기존 `JennySans` 패밀리를 선택 → **제거**(Remove) → 새 파일 설치 → 앱 재시작. Font Book 의 **파일 → 서체 확인**(Validate) 으로 중복·손상 여부를 볼 수 있습니다.
- macOS 는 name ID 16/17(typographic family)을 읽으므로 **"JennySans" 패밀리 하나에 9 스타일**로 보입니다.

---

## 3. 프로그램별 — 패밀리·웨이트 고르기

### 3-1. 한글(HWP, 한컴오피스)
- 글꼴 목록에 **「제니산스」**(한국어 이름) 또는 **JennySans** 로 보입니다. 한글은 Windows GDI 방식으로 폰트를 나열하므로 웨이트가 **따로**(「제니산스 Light」, 「제니산스 Medium」…) 보입니다.
- **굵기는 목록에서 고르세요.** 「제니산스」(Regular)에서 **진하게(Ctrl+B)** 를 누르면 실제 Bold 파일로 바뀌지만, 「제니산스 Light」에서 진하게를 누르면 한글이 **선을 두껍게 덧그린 합성 굵게**를 만들어 품질이 떨어집니다.
- 변수 폰트(`JennySansVariable.ttf`)의 웨이트 축 지원 여부는 **확인 못 함** — 문서용은 정적 TTF 를 설치하세요.

### 3-2. MS Office (Word · Excel · PowerPoint)
- 글꼴 상자에 `JennySans`, `JennySans Light`, `JennySans SemiBold` … 로 **웨이트별 항목**이 나옵니다(한글과 같은 이유). 원하는 굵기 항목을 직접 고르세요.
- `JennySans` 에서 **B**(굵게)를 누르면 진짜 Bold(700) 파일이 쓰입니다. 다른 항목에서 B 를 누르면 합성 굵게입니다.
- Office 는 변수 폰트의 축 조절을 지원하지 않습니다(명명 인스턴스만). 정적 TTF 권장.
- 문서를 다른 PC 로 보낼 때: Word **옵션 → 저장 → 파일에 글꼴 포함** 을 켤 수 있습니다(OFL 은 임베딩을 허용하며 폰트의 fsType 이 0 이라 Office 가 거부하지 않습니다).

### 3-3. Photoshop · Illustrator · InDesign · Figma · 브라우저
- **패밀리 "JennySans" 하나**에 스타일 9개(Thin … Black)가 스타일 메뉴에 나옵니다(name ID 16/17 사용).
- 변수 폰트를 설치하면 "JennySans Variable" 패밀리가 따로 생기고 굵기 슬라이더가 붙습니다. 정적과 변수를 **동시에** 설치해도 이름이 달라 충돌하지 않습니다.
- 가짜 기울임(Faux Italic)은 쓰지 마세요 — 이탤릭이 없는 서체입니다.

### 3-4. 왜 "JennySans Light" 가 따로 보이나 (GDI · RIBBI 규칙)
Windows 의 옛 폰트 API(GDI)는 한 패밀리 이름 아래 **Regular / Bold / Italic / Bold Italic 4개(RIBBI)** 만 둘 수 있습니다. 그래서 Regular·Bold 이외의 웨이트는 OpenType 관례대로 **"JennySans Light" 같은 별도 패밀리명(name ID 1)** 을 갖고, 진짜 패밀리명은 name ID 16("JennySans")에 따로 적습니다.
- GDI 를 쓰는 프로그램(한글, MS Office 글꼴 목록, 구형 프로그램): 웨이트별로 따로 보임.
- DirectWrite·macOS·Adobe·브라우저: ID 16/17 을 읽어 **한 패밀리 9 스타일**로 보임.
Pretendard·Noto Sans KR 등 다른 9 웨이트 폰트도 똑같이 동작합니다. 결함이 아니라 호환성을 위한 표준 구조입니다(`docs/spec/02-naming.md` §3).

---

## 4. 웹

### 4-1. CSS 4종 선택 기준

| CSS | 동작 | 권장 상황 |
|---|---|---|
| `jennysans-dynamic-subset.css` | 웨이트별로 폰트를 99 조각(`unicode-range`; Google Fonts 한국어 124 슬라이스 정의 중 우리 문자집합에 해당하는 것 + 나머지 조각)으로 나눠 선언. 브라우저는 **페이지에 실제로 나타난 글자가 속한 조각만** 내려받음(라틴 1조각 + 한글은 빈도순 조각) | **한국어 페이지 기본.** 실제 전송량(`tools/first_paint.py` 실측): 라틴 전용 31,144 B · 한국어 한 문장 85,420 B · 한 문단 105,312 B · 두 문단 2웨이트 158,320 B (조각당 2,264–31,340 B). **단 CSS 파일 자체가 448,127 B(gzip 101,348 B)** — `@font-face` 891개 |
| `jennysans.css` | 웨이트별 전체본 1파일(647,572–764,252 B, Regular 726,032 B) | 인트라넷/오프라인, HTTP/1.1 서버, 쓰는 웨이트 1~2개, 캐시가 한 번 되면 끝인 앱 |
| `jennysans-variable.css` | 변수 폰트 전체본 1파일(2,239,472 B)로 100–900 전부. CSS 자체 679 B | 한 페이지에 웨이트 4개 이상. Chrome 62+·Firefox 62+·Safari 11+·Edge 17+ |
| `jennysans-variable-dynamic-subset.css` | 변수 폰트를 99 조각으로(조각당 3,408–90,472 B, 라틴 69,304 B). CSS 69,422 B | 변수 + 한국어 페이지, 웨이트 4개 이상일 때 |

> **9 웨이트를 전부 쓰지 않는다면** `jennysans-variable.css`(변수 폰트, CSS 679 B)를 쓰거나 `jennysans-dynamic-subset.css` 에서 **쓰는 웨이트의 `@font-face` 블록만 남겨** 쓰세요. 분할 CSS 는 9 웨이트 × 99 조각 = `@font-face` 891개라 CSS 자체가 448,127 B(gzip 101,348 B)입니다(폰트 전송량과 별개인 파싱 비용).

네 파일 모두 `font-family: "JennySans"` 로 같은 이름을 선언하므로 **하나만** 링크하세요(둘 이상 링크하면 이중 다운로드). 폴백 스택은 `"JennySans", "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif` 를 권장합니다.

### 4-2. `unicode-range` 가 하는 일
- 각 `@font-face` 블록에 "이 파일에 든 코드포인트 범위"가 적혀 있고, 브라우저는 렌더할 글자가 그 범위에 있을 때만 해당 파일을 요청합니다. 요청 수는 늘지만(HTTP/2 권장) 전송량은 크게 줄어듭니다.
- 조각에 없는 글자(한자·가나·중국어·베트남어 등 범위 밖 — `README.md` §2·§3)는 다음 폴백 폰트로 그려집니다. `charset/required.txt` 의 모든 글자는 어느 한 조각에 반드시 들어 있습니다(QA 게이트).
- 조각 파일명은 `JennySans-<Weight>.subset.<n>.woff2` 이고 CSS 안의 경로는 `../web/subset/` 상대경로입니다. `css/` 와 `web/` 을 **같은 상대 구조로** 올리면 CSS 를 고칠 필요가 없습니다.

### 4-3. preload · font-display
```html
<link rel="preload" as="font" type="font/woff2" crossorigin
      href="https://font.jennysoft.co.kr/v/1.000/web/subset/JennySans-Regular.subset.123.woff2">
<link rel="stylesheet" href="https://font.jennysoft.co.kr/v/1.000/css/jennysans-dynamic-subset.css">
```
- preload 는 **첫 화면에 반드시 쓰이는 조각**(라틴 조각 #123, 로고 등 고정 텍스트 조각)만. 한글 조각은 페이지마다 달라 브라우저에 맡깁니다. `crossorigin` 속성이 없으면 preload 한 파일을 다시 받습니다(폰트는 항상 CORS 모드로 요청되기 때문).
- CSS 는 `font-display: swap` 으로 선언돼 있습니다(글자가 먼저 시스템 폰트로 보였다가 교체). 깜빡임을 피하려면 `optional` 로 바꾼 사본을 쓰세요.
- 줄 높이 기본값(`line-height: normal`)은 약 1.19. 본문 1.5~1.7 권장. 폰트가 늦게 도착할 때 레이아웃이 튀는 것을 줄이려면 폴백 폰트와 `size-adjust`/`ascent-override` 를 조정한 `@font-face` 를 추가할 수 있습니다(선택).

### 4-4. 오프라인·인트라넷
`dist/css` + `dist/web` 을 그대로 복사해 두고 `<link rel="stylesheet" href="/fonts/css/jennysans.css">` 처럼 씁니다. 외부 CDN 을 못 쓰는 환경(사내망·키오스크·Electron)은 반드시 이 방식.

---

## 5. 직접 서빙(self-host)할 때 서버 설정 — CORS 필수

- 폰트는 브라우저가 **CORS 자원**으로 취급합니다. 페이지 오리진(`https://qdance.jennysoft.co.kr`)과 폰트 오리진(`https://font.jennysoft.co.kr`)이 다르면 서버가 `Access-Control-Allow-Origin: *`(또는 해당 오리진)을 내야 하고, **없으면 폰트가 조용히 무시되어 폴백 폰트로 그려집니다.** `curl` 로 200 이 떨어져도 화면에는 안 나옵니다 — 전역 규칙의 S3 CORS 사고와 같은 종류입니다. 반드시 **실제 브라우저에서** 확인하세요(DevTools → Network → 폰트 요청 → Response Headers).
- 같은 오리진에서 서빙하면 CORS 헤더가 필요 없지만, 어차피 붙여 두는 편이 안전합니다(서브도메인 분리·CDN 전환 대비).
- MIME: `font/woff2`, `font/ttf`, `font/otf`. 캐시: 경로에 버전을 넣고(`/v/1.000/`) `Cache-Control: public, max-age=31536000, immutable`. WOFF2 는 이미 Brotli 압축이라 gzip 하지 않습니다(CSS 는 gzip).
- 준비된 nginx 설정: [`deploy/nginx-font.conf`](../deploy/nginx-font.conf). 검증 명령:
  ```bash
  curl -sI -H "Origin: https://example.com" https://font.jennysoft.co.kr/v/1.000/web/JennySans-Regular.woff2 | grep -i -E "access-control|content-type|cache-control"
  ```
  그리고 **다른 도메인에 올린 `site/test.html`** 에서 폰트가 실제로 적용되는지 스크린샷으로 확인합니다(`docs/spec/05-web.md` §7-4).

---

## 6. Flutter (Android · iOS · Web · Windows · macOS · Linux)

### 6-1. 선언
`assets/fonts/` 에 TTF 를 복사하고 `pubspec.yaml` 에 웨이트를 매핑합니다(전체 9종은 `README.md` §4-2). Flutter 는 `.ttf`/`.otf`/`.ttc` 만 지원하고 **WOFF2 는 데스크톱에서 지원하지 않습니다**(Flutter 공식 문서).

| Dart `FontWeight` | pubspec `weight` | 파일 |
|---|---|---|
| w100 | 100 | JennySans-Thin.ttf |
| w200 | 200 | JennySans-ExtraLight.ttf |
| w300 | 300 | JennySans-Light.ttf |
| w400 (normal) | 400 | JennySans-Regular.ttf |
| w500 | 500 | JennySans-Medium.ttf |
| w600 | 600 | JennySans-SemiBold.ttf |
| w700 (bold) | 700 | JennySans-Bold.ttf |
| w800 | 800 | JennySans-ExtraBold.ttf |
| w900 | 900 | JennySans-Black.ttf |

```dart
MaterialApp(theme: ThemeData(fontFamily: 'JennySans', useMaterial3: true));
// 개별 스타일
Text('제니산스', style: TextStyle(fontFamily: 'JennySans', fontWeight: FontWeight.w600));
```
- **선언하지 않은 웨이트**를 `TextStyle` 이 요구하면 엔진이 가장 가까운 선언 파일을 씁니다(공식 문서는 "이 동작에 의존하지 말라"고 안내). 실제 쓰는 웨이트만 선언하되, 쓰는 것은 빠짐없이 선언하세요.
- 앱 크기: 정적 TTF 1개 2,553,816–2,700,344 bytes(Regular 2,617,580), 9종 전부 23,462,992 bytes, 변수 TTF 7,009,656 bytes. 모바일 앱은 보통 400·500·700(+600) 정도면 충분합니다(4 웨이트 10,327,984 bytes ≈ 10.3 MB).
- 변수 폰트 1개로 대체하려면 `JennySansVariable.ttf` 를 하나만 선언하고 `TextStyle(fontVariations: [FontVariation('wght', 600)])` 를 씁니다(Flutter 3.x). 이때 `fontWeight` 는 웨이트 선택에 쓰이지 않으므로 테마 전반에 일괄 적용하기엔 정적 9종 선언이 단순합니다.

### 6-2. 웹 빌드 팁
- Flutter 웹(CanvasKit/skwasm)은 CSS 웹폰트가 아니라 **에셋 TTF** 를 씁니다. `FontManifest.json` 에 선언된 폰트 파일을 **앱 시작 시 전부** 내려받으므로, 웹 대상 앱은 웨이트 수를 줄이는 것이 가장 큰 절감입니다.
- 더 줄이려면 웹 빌드 전에 에셋 파일을 **서브셋본으로 교체**합니다(파일명은 그대로, 내용만 작게). 예: 앱의 번역 문자열(ARB/JSON)에 나오는 글자 + KS X 1001 완성형 2,350자 + 라틴만 남기기.
  ```bash
  pip install fonttools brotli
  pyftsubset dist/static/JennySans-Regular.ttf \
    --output-file=app_flutter/assets/fonts/JennySans-Regular.ttf \
    --unicodes="U+0020-007E,U+00A0-00FF,U+0100-017F,U+2010-2027,U+20AC,U+20A9,U+3131-318E,U+AC00-D7A3" \
    --layout-features='*' --glyph-names --notdef-outline --recalc-bounds --recalc-average-width
  ```
  (`U+AC00-D7A3` 전체 대신 실제 쓰는 글자만 넣으면 더 작아집니다: `--text-file=strings.txt`.) 서브셋본은 사내 앱 안에서만 쓰고 **밖으로 재배포하지 않으면** 이름을 바꿀 필요가 없습니다(`docs/OFL-FAQ-ko.md` Q5).
- 세 표면(웹·앱·백엔드)을 함께 배포하는 규칙은 상위 상위 폴더의 사내 규칙(CLAUDE.md, 비공개) §2 그대로입니다.

---

## 7. Unity (TextMesh Pro)

### 7-1. 기본
1. `dist/static/JennySans-<Weight>.ttf` 를 `Assets/Fonts/` 에 넣습니다(TTF 권장 — Unity 매뉴얼은 TrueType 임포트를 기준으로 설명하며 변수 폰트 축은 TMP 가 지원하지 않습니다. 웨이트는 정적 파일로 각각).
2. **Window → TextMeshPro → Font Asset Creator**.
3. 권장 설정(2026-09 기준 TMP 3.x/UGUI 2.x):

| 항목 | 권장 | 이유 |
|---|---|---|
| Source Font File | JennySans-Regular.ttf (웨이트별로 에셋 생성) | |
| Sampling Point Size | **Auto Size**(정적 아틀라스) / 60~90(동적) | Auto 는 문자 집합이 아틀라스에 들어가는 최대 크기를 계산 |
| Padding | Sampling Point Size 의 약 1/10 (5~9) | SDF 여유. 너무 작으면 굵게·외곽선 효과가 깨짐 |
| Packing Method | Fast(반복 작업) → 최종은 Optimum | |
| Atlas Resolution | 2048×2048(모바일 UI, 2,350자) / 4096×4096(PC) | 아래 7-2 |
| Character Set | **Custom Characters** 또는 **Characters from File**(KS X 1001 2,350자 목록) | 전체 11,172자는 7-2 |
| Render Mode | SDFAA(기본) — 큰 제목은 SDF16/32 | |
| Atlas Population Mode | **Dynamic**(7-3) | |

4. 생성한 Font Asset 의 **Font Weights** 표에 Bold/SemiBold 등 다른 웨이트 에셋을 연결해 두면 `<b>` 태그·Bold 스타일이 합성 굵게가 아니라 진짜 Bold 파일을 씁니다.
5. 기호·이모지·범위 밖 문자(한자 등)는 **Fallback Font Assets** 에 다른 폰트 에셋을 추가해 처리합니다.

### 7-2. 한글 11,172자 정적 아틀라스 주의
- 4096×4096 아틀라스에 11,172자를 다 넣으면 글립당 셀이 약 **38 px**(4096 ÷ √11,172 ≈ 38.7, 패딩 포함)밖에 안 되어 SDF 품질이 부족합니다(작은 글자에서 뭉개짐). 8192×8192 면 약 77 px 로 쓸 만하지만 텍스처 메모리가 64 MB(Alpha8)로 모바일에 부담입니다.
- 따라서 **정적 아틀라스는 KS X 1001 완성형 2,350자**(일상 한국어 대부분)까지만 굽고, 나머지는 **Dynamic** 으로 채우는 방식을 권장합니다. 2,350자 + 라틴·기호 ≈ 2,600자 → 4096² 에서 글립당 약 80 px.

### 7-3. Dynamic 모드
- Font Asset 의 **Atlas Population Mode = Dynamic** + **Multi Atlas Textures** 켜기 → 실행 중 처음 만나는 글자를 아틀라스에 추가합니다. 폰트 원본(TTF)이 빌드에 포함되어야 하며(에셋이 참조하므로 자동 포함), 처음 나오는 글자마다 약간의 렌더 비용이 있습니다.
- 자주 쓰는 2,350자를 정적으로 먼저 굽고(Dynamic 에셋에서도 "Custom Characters" 로 미리 채우기 가능) 그 위에 Dynamic 을 켜는 것이 안정적입니다.
- 채팅·이름 입력처럼 어떤 글자가 올지 모르는 UI 는 반드시 Dynamic.

---

## 8. Godot 4

- TTF 를 프로젝트에 넣으면 `FontFile` 로 임포트됩니다(Godot 은 TTF/OTF/WOFF/WOFF2/변수 폰트 모두 지원). **Project Settings → GUI → Theme → Custom Font** 또는 Theme 리소스의 `default_font` 로 지정합니다.
- 웨이트: 정적 TTF 를 웨이트별 `FontFile` 로 쓰거나, `JennySansVariable.ttf` 하나를 `FontVariation` 으로 감싸 `variation_opentype = {"wght": 700}` 처럼 지정합니다(`Font → Variation → OpenType` 또는 코드에서 `FontVariation.variation_opentype`).
- 임포트 설정(Import 도크):
  - **Hinting**: `Light` 권장(작은 한글의 획 유지). 흐릿하면 `Normal`, 스케일 변화가 많은 UI 는 `None`.
  - **Antialiasing**: LCD Subpixel(데스크톱 UI) / Gray(모바일·회전 텍스트).
  - **Subpixel Positioning**: Auto.
  - **Multichannel Signed Distance Field(MSDF)**: 크기가 계속 변하는 텍스트·3D 텍스트에 켬. MSDF 에서는 **힌팅이 적용되지 않습니다**(Godot 문서).
  - **Oversampling**: 고DPI 에서 흐리면 조정.
- Godot 은 글립을 런타임에 그리므로 Unity 처럼 아틀라스를 미리 굽지 않습니다. 범위 밖 문자는 `FontFile.fallbacks` 에 다른 폰트를 넣어 처리합니다.

---

## 9. 문제 해결

| 증상 | 원인·조치 |
|---|---|
| 웹에서 폰트가 적용되지 않음(폴백으로 보임) | DevTools Network 에서 폰트 요청 상태 확인: **CORS 차단**(§5) · 404(CSS 의 `../web/` 상대경로 구조 깨짐) · MIME 오류 · `font-family` 이름 오타(`JennySans`, 대소문자 무관하지만 공백 없음) |
| 특정 글자만 다른 폰트로 보임 | 범위 밖 문자(한자·가나·옛한글) → 정상. 폴백 스택에 `Noto Sans KR`/`Malgun Gothic` 을 두세요. 필수 범위 글자라면 `docs/qa/ISSUES.md` 에 제보 |
| 한글(HWP)·Office 에서 웨이트가 흐리거나 뭉개짐 | Light 등에서 **진하게** 를 눌러 합성 굵게가 된 상태 → 목록에서 실제 웨이트 선택(§3-1) |
| 웨이트를 바꾸면 줄 간격이 달라짐 | JennySans 는 전 웨이트 줄 높이가 같습니다. 달라지면 그 줄에 **다른 폰트**가 섞인 것(폴백) |
| Windows 에서 옛 버전이 계속 보임 | §1-2 (프로그램 종료 → 제거 → 설치 → FontCache 재시작/재부팅) |
| 변수 폰트가 앱 목록에 안 보임 | 패밀리명이 "JennySans Variable" 로 따로 있음. 한글·Office 는 변수 축 미지원 → 정적 사용 |
| Flutter 에서 굵기가 안 바뀜 | pubspec `weight` 매핑 누락 → §6-1 표. 변수 TTF 는 `fontVariations` 로 지정 |
