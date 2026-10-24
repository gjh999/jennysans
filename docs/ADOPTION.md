# JennySans 사내 적용 가이드 (제니소프트 앱별 절차)

> 대상: Q시리즈 Flutter 앱(QDance·QLove·QStudy·QMoim·QSports·QPass·QBap·QDream·LatinBeat), LatinBeat 웹, Qaudio(정적 홈페이지·Electron 앱·라이브 보드), Idol(React/Vite).
> 전제: JennySans 1.000 이 QA RELEASE OK 이고 `font.jennysoft.co.kr` 이 살아 있거나(§7 검증 후) 파일을 앱에 번들한다.
> 파일럿(ROADMAP P8)은 **앱 하나**로 시작해 실화면 스크린샷을 남긴 뒤 확산한다.

## 0. 공통 원칙

1. **버전 고정**: CDN 은 `/v/1.000/`(또는 npm `@1.0.0`) 고정 경로만. `latest` 는 데모·QA 용.
2. **오프라인이 있어야 하는 표면(Electron·게임·모바일 앱)은 파일을 번들**한다. CDN 의존 금지.
3. **폴백 스택**을 항상 둔다: `"JennySans", "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif`.
   JennySans 는 **한국어판**이라 1.000 에는 한자·가나·중국어·베트남어가 없다 — **폴백이 그린다**(한자·베트남어는 1.100 에 포함 예정, 일본어·중국어는 별도 패밀리 `JennySans JP`/`SC`/`TC` 예정. `README.md` §3). 이모지도 폴백 담당.
4. `font-synthesis: none;` — 이탤릭이 없는 서체라 가짜 기울임을 막는다. 굵기는 선언한 웨이트만 쓴다.
5. **실화면 확인**이 완료 기준(브라우저 새로고침/기기). `curl` 200·빌드 성공은 검증이 아니다(상위 상위 폴더의 사내 규칙(CLAUDE.md, 비공개) §2·§9).
6. 웨이트는 필요한 만큼만: 앱 UI 는 보통 400·500·700(+600). 9종 전부 번들하면 정적 TTF 9 = **23,462,992 bytes ≈ 23.5 MB**(8차 빌드 실측; 4 웨이트(400·500·600·700) = 10,327,984 bytes ≈ 10.3 MB, 변수 TTF 1개 7,009,656 bytes ≈ 7.0 MB).
   **웹 표면도 같다** — 9 웨이트를 다 쓰지 않으면 `jennysans-variable.css`(CSS 679 B)를 쓰거나 `jennysans-dynamic-subset.css` 에서 쓰는 웨이트 블록만 남긴다. 분할 CSS 는 `@font-face` 891개라 CSS 자체가 448,127 B(gzip 101,348 B)다.
7. **유료 제품에 번들·판매해도 라이선스상 문제가 없다.** OFL 조항 2 가 "may be bundled, redistributed and/or sold with any software" 를 명시하고, `fsType` 0 이라 임베딩 제한도 없다(근거·경계는 `docs/OFL-FAQ-ko.md` 「상업적 이용」 절). **단 조항 2 의 조건이 하나 붙는다 — 배포본마다 `LICENSE` 사본(또는 앱 안에서 볼 수 있는 라이선스 고지)을 포함해야 한다.** 스택별로 넣을 자리:

   | 스택 | 넣을 자리 |
   |---|---|
   | **Flutter**(Q시리즈·LatinBeat) | `LICENSE` 를 `assets/licenses/JennySans-LICENSE.txt` 로 번들 + `main()` 에서 `LicenseRegistry.addLicense()` 로 등록 → 앱 내 `showLicensePage()`(또는 `showAboutDialog`)에 자동 노출 |
   | **Electron**(Qaudio) | `app/THIRD-PARTY-NOTICES.txt` 에 OFL 전문·저작권 블록 추가 + 앱 메뉴 「정보 → 오픈소스 라이선스」에서 열람 |
   | **Unity · Godot** | `Assets/Fonts/JennySans/LICENSE.txt`(Godot 은 `fonts/JennySans/LICENSE.txt`)를 함께 두고, 크레딧 화면에 "JennySans — SIL OFL 1.1" 한 줄 |
   | **웹**(정적 HTML·React·self-host) | 폰트 파일과 같은 디렉터리에 `LICENSE` 를 두고 푸터에서 링크(CDN·npm 패키지에는 이미 동봉됨) |

   폰트 파일 자체를 상품으로 파는 것만 금지다(조항 1). 자세한 경계표는 `docs/OFL-FAQ-ko.md`.

## 1. Q시리즈 Flutter 앱 (웹 + Android + iOS 공용 코드베이스)

현황(2026-09-06 실측): QDance `app_flutter/pubspec.yaml` 에 `fonts:` 없음, `lib/core/theme.dart` 25·99행 `fontFamily: 'Roboto'`. LatinBeat(`<사내 저장소 QRhythm>`)는 이미 Pretendard 4 웨이트(Regular/Medium/SemiBold/…)를 `assets/fonts/` 에 번들.

### 1-1. 절차
1. `dist/static/` 에서 쓰는 웨이트의 TTF 를 `app_flutter/assets/fonts/` 로 복사(권장 400·500·600·700).
2. `pubspec.yaml`:
   ```yaml
   flutter:
     fonts:
       - family: JennySans
         fonts:
           - { asset: assets/fonts/JennySans-Regular.ttf,  weight: 400 }
           - { asset: assets/fonts/JennySans-Medium.ttf,   weight: 500 }
           - { asset: assets/fonts/JennySans-SemiBold.ttf, weight: 600 }
           - { asset: assets/fonts/JennySans-Bold.ttf,     weight: 700 }
   ```
3. 테마: `ThemeData(fontFamily: 'JennySans', …)` — QDance 는 `lib/core/theme.dart` 의 `'Roboto'` 두 곳을 `'JennySans'` 로. `GoogleFonts`/`TextTheme` 을 따로 만든 앱은 `textTheme.apply(fontFamily: 'JennySans')`.
4. `flutter pub get` → 서버에서 `flutter analyze lib/`(error·warning 0) → 웹 빌드·앱 빌드.
5. **세 표면 동기 배포**(백엔드 무관하면 웹 정적 + 앱 새 빌드 둘 다). 웹은 브라우저 강력 새로고침으로, 앱은 기기에서 확인.

### 1-2. 웹 표면 주의
- Flutter 웹은 CSS `@font-face` 가 아니라 **에셋 TTF** 를 CanvasKit 이 직접 읽는다. `web/index.html` 에 CDN CSS 를 넣어도 Flutter 위젯 텍스트에는 영향이 없다(스플래시 HTML 에는 영향 있음 — §2).
- `FontManifest.json` 의 폰트는 앱 시작 시 전부 내려받으므로 웹 대상 앱은 웨이트 3~4개로 제한하거나 서브셋본으로 교체(`docs/INSTALL.md` §6-2).
- 웹 교체 전 기존본을 `/var/www/<app>.bak.<ts>` 로 백업(상위 규칙).

### 1-3. LatinBeat(QRhythm) 특이
- 이미 `family: Pretendard` 로 4 웨이트 번들 → 파일 교체 + `family: JennySans` + 코드의 `'Pretendard'` 문자열 치환. JennySans 는 Pretendard 파생이라 **글자 모양·줄 높이가 사실상 같아 레이아웃 회귀 위험이 가장 낮다** → **파일럿 1순위 후보**.
- `app_flutter/web/index.html` 48행 스플래시 CSS `font: 500 15px/1.4 Pretendard, …` 는 §2 처럼 CSS 링크를 추가하거나 시스템 폰트 스택만 남긴다.

## 2. LatinBeat 웹 정적 페이지 · 기타 정적 HTML (`/var/www/<app>`)

Flutter 로드 전 스플래시·랜딩·404 등 순수 HTML 에서 쓸 때:
```html
<link rel="stylesheet" href="https://font.jennysoft.co.kr/v/1.000/css/jennysans-dynamic-subset.css">
<style>html { font-family: "JennySans", "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif; font-synthesis: none; }</style>
```
- 다른 오리진(`latinbeat.jennysoft.co.kr` → `font.jennysoft.co.kr`)이므로 **CORS 헤더가 있어야 폰트가 적용**된다(§7).
- CDN 없이 가려면 `dist/css` + `dist/web` 을 `/var/www/<app>/fonts/` 로 복사하고 `href="/fonts/css/jennysans-dynamic-subset.css"`. 같은 오리진이라 CORS 불필요.

## 3. Qaudio

### 3-1. 정적 홈페이지 `site/`(`/var/www/qaudio`)
- `site/styles.css` 는 `font-family: var(--q-font-sans)` 토큰을 쓴다(116행). 토큰 정의에 `"JennySans"` 를 맨 앞에 추가하고 `site/index.html` `<head>` 에 위 §2 의 `<link>` 를 넣는다(또는 `site/public/fonts/` 에 복사해 같은 오리진 서빙 — `deploy/deploy-site.sh` 가 `site/dist` 를 그대로 올리므로 `public/` 경유 여부는 빌드 설정 확인).
- CSS 선택: 소개 페이지는 한국어 짧은 문장 위주 → `jennysans-dynamic-subset.css`.

### 3-2. Electron 앱 (renderer, 오프라인 필수)
- CDN 금지. `dist/web/JennySans-{Regular,Medium,SemiBold,Bold}.woff2`(또는 `JennySansVariable.woff2` 1개)를 `app/src/renderer/assets/fonts/` 에 넣고 렌더러 전역 CSS 에 `@font-face` 를 직접 선언(경로는 electron-vite 가 처리하는 상대 import 또는 `/assets/fonts/…`):
  ```css
  @font-face { font-family: "JennySans"; font-weight: 100 900; font-display: swap;
               src: url("./assets/fonts/JennySansVariable.woff2") format("woff2"); }
  :root { font-family: "JennySans", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif; font-synthesis: none; }
  ```
  변수 1 파일이 가장 단순(Electron 43/Chromium 은 변수 WOFF2 지원). 전체 문자집합이 필요하면 전체본, 설치본 크기가 중요하면 서브셋본(사내 배포물에 포함되는 것이라 이름 변경 불필요 — `docs/OFL-FAQ-ko.md` Q5; 단 **설치본을 외부에 판매·배포**하므로 폰트 파일은 수정 없이 넣거나, 서브셋본이면 THIRD-PARTY 에 "JennySans 의 서브셋" 으로 명기).
- `app/THIRD-PARTY-NOTICES.txt` 에 JennySans 항목(OFL 1.1, LICENSE 전문) 추가 — Qaudio 는 **상용 판매** 제품이므로 OFL 조항 2(번들 시 고지 동봉) 준수가 특히 중요. 폰트 자체를 파는 것이 아니므로 판매 자체는 허용.
- 듀얼 모니터 전체화면 보드(오프라인)도 같은 렌더러 자산을 쓰므로 별도 조치 없음.

### 3-3. 라이브 보드 웹 (`app/live/`, 릴레이가 서빙)
- `app/live/live.css` 에 §2 의 `<link>`(CDN) 또는 릴레이 정적 경로에 `dist/web` 복사. 댄서용 외부 접속 페이지라 CDN 사용이 자연스럽다.

## 4. Idol (React/TS/Vite, `<사내 저장소 Idol>\app`)

- 전역 스타일 `app/src/styles/global.css`·토큰 `tokens.css`. 방법 A(CDN): `app/index.html` `<head>` 에 §2 의 `<link>`, 토큰의 sans 폰트 스택 맨 앞에 `"JennySans"`.
- 방법 B(self-host, 권장 — 게임 로딩이 폰트 서버에 묶이지 않게): `dist/css/jennysans-dynamic-subset.css` + `dist/web/` 을 `app/public/fonts/jennysans/{css,web}` 에 복사(Vite 의 `public/` 은 해시 없이 그대로 서빙되어 CSS 의 `../web/` 상대경로가 유지됨) → `index.html` 에 `<link rel="stylesheet" href="/fonts/jennysans/css/jennysans-dynamic-subset.css">`.
- 캐릭터 대사·이벤트 텍스트가 많아 한글 슬라이스가 여러 개 필요 → **분할 CSS** 가 유리. 타이틀·로고용 Black(900)은 쓰는 곳만.
- 서버(Fastify)가 정적을 직접 내면 `font/woff2` MIME 과 캐시 헤더를 설정(§7 nginx 앞단이면 nginx 가 처리).

## 5. 게임(Unity·Godot)·Flame

- Unity: `docs/INSTALL.md` §7 (TMP Dynamic, KS 2,350 정적 + Dynamic). Godot: §8. Flame(Flutter): §1 과 동일.

## 6. 서버 self-host 시 CORS 가 필수인 이유 (사고 교훈)

- 브라우저는 **웹폰트를 항상 CORS 모드로 요청**한다(CSS Fonts 스펙). 페이지 오리진과 폰트 오리진이 다르면 응답에 `Access-Control-Allow-Origin` 이 없을 때 폰트를 **폐기하고 폴백으로 그린다**. 오류 상태코드가 아니라 **200 응답을 받고도** 적용되지 않는다.
- 전역 규칙(`~/.claude/CLAUDE.md` "저장소/외부 연결 전환")의 실제 사고: S3 공개 객체가 `curl` 200 이었지만 **버킷 CORS 미설정으로 Flutter 웹(CanvasKit)에서 이미지가 그려지지 않았다.** 폰트도 같은 부류(크로스오리진 캔버스/폰트 자원)다. **`<img>`·`curl` 로 판단하지 말고 실제 앱 화면에서 확인.**
- 따라서 `font.jennysoft.co.kr` 은 `deploy/nginx-font.conf` 대로 `Access-Control-Allow-Origin: *` 를 **모든 폰트·CSS 응답에 `always`** 로 붙인다(nginx `add_header` 는 자식 `location` 에 `add_header` 가 하나라도 있으면 부모 것을 상속하지 않으므로 location 마다 반복해 둠).
- 각 앱 서버가 폰트를 직접 낼 때(같은 오리진)는 CORS 가 필요 없지만, 서브도메인 분리(`www` ↔ `app`)나 `preload crossorigin` 이 있으면 필요하다. 그냥 붙인다.
- 확인 절차: ① DevTools → Network → Fonts 필터 → 상태 200 + Response Headers 에 `access-control-allow-origin` ② Console 에 "blocked by CORS policy" 없음 ③ `document.fonts.check('400 16px "JennySans"')` 가 `true` 이고 실제 글자 모양이 바뀜(`site/test.html` 은 폴백을 세리프로 두어 눈에 띄게 함).

## 7. 파일럿 체크리스트 (P8)

- [ ] 대상 앱 결정(권고: LatinBeat 웹 — 회귀 위험 최소·Pretendard 비교 용이 / 차선: Idol 방법 B)
- [ ] 폰트 파일·CSS 반영, 폴백 스택·`font-synthesis` 설정
- [ ] `LICENSE` 사본을 앱 서드파티 고지에 추가
- [ ] 로컬/스테이징 실화면 스크린샷(한글·영문·스페인어·숫자·기호 각 1)
- [ ] 다른 오리진이면 CORS 헤더 실측(§6 ①②③)
- [ ] 세 표면 동기 배포(해당 시) + 운영 실화면 확인
- [ ] 피드백(글립 결손·크기·줄높이)을 `docs/qa/ISSUES.md` 에 티켓 → 1.001 반영
