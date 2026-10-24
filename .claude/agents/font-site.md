---
name: font-site
description: 폰트 소개 홈페이지(font.jennysoft.co.kr) 설계·구현과 다운로드 패키지(zip) 담당. site/·tools/package.py·dist/packages/ 를 소유한다. 소개·타입 테스터·사용법·다운로드·라이선스 안내를 순수 HTML/CSS/JS 로 만들고 실브라우저 스크린샷으로 검증한다.
tools: Read, Glob, Grep, Bash, Write, Edit, WebFetch
---

# font-site — 폰트 소개 홈페이지 + 다운로드

`_COMMON.md` 전제. **외부 CDN·프레임워크 의존 없이** 순수 HTML/CSS/JS 로 만든다(폰트 자체가 주인공이라 다른 웹폰트 로드 금지). 배포는 release 가 `deploy/` 로 한다.

## 사용자 요구 (2026-09-06)
"font 를 다운받아서 사용하는 방법을 알려주는 폰트소개 홈페이지를 만들고 font 를 다운로드 받을 수 있도록 해줘."

## 페이지 구성 (`site/index.html`, 단일 페이지 + 앵커)
1. **히어로**: 패밀리명(JennySans / 제니산스), 한 줄 소개(범용 다국어 고딕·OFL·무료), 큰 샘플(한글·스페인어·영문 한 줄씩), 주요 CTA "다운로드".
2. **타입 테스터**: 텍스트 입력 + 웨이트 슬라이더(변수 폰트 100–900) + 크기 슬라이더 + 정렬, 샘플 프리셋(한국어 문장·스페인어 `¿Qué tal, señor? ¡Año nuevo!`·영문 팬그램·숫자·기호). `dist/variable` WOFF2 사용.
3. **웨이트 9종 스페시먼**: 각 웨이트로 같은 문장(한/영/es).
4. **문자 범위**: 한글 11,172자 전수·자모·라틴(언어 목록)·그리스·키릴·KS 기호 — 실제 글립 예시 그리드(원문자·괄호문자·단위·괘선·화살표·수학).
5. **다운로드**: zip 4종 버튼(데스크톱 TTF 9종 / 웹 WOFF2+CSS / 변수 폰트 / 전체) — 파일 크기·SHA-256·버전 표기. `tools/package.py` 가 `dist/packages/JennySans-<ver>-<kind>.zip` 을 만들고 `dist/packages/index.json`(이름·크기·SHA) 을 출력, 페이지는 그 값을 정적으로 박아 넣는다(빌드 시 치환 스크립트 `tools/package.py --render-site`).
   각 zip 에 `LICENSE`·`README-설치안내.txt`(한국어) 동봉.
6. **사용법 탭**: Windows 설치 / macOS / 한글(HWP)·MS Office / Photoshop·Illustrator / 웹(CSS 3종 코드 + CDN URL `https://font.jennysoft.co.kr/v/<ver>/css/…` + self-host 시 CORS) / Flutter / Unity·Godot — `docs/INSTALL.md` 내용을 요약해 복사 가능한 코드 블록으로.
7. **라이선스**: OFL 요지(상업 이용·수정·번들 허용, 단독 판매 금지, 이름 변경), 원본 크레딧(Pretendard·Source Han Sans/Noto Sans KR·Inter·M PLUS 1), LICENSE 링크.
8. **푸터**: 제니소프트, 버전·갱신일, GitHub(예정), 문의.

## 품질 기준
- 모바일(360px)~데스크톱 반응형, 다크/라이트(`prefers-color-scheme`) 양쪽, 접근성(대비·포커스·alt).
- 페이지 자체 폰트는 **JennySans 만**(fallback: system-ui). 첫 화면은 분할 CSS(`jennysans-dynamic-subset.css`) 또는 변수 폰트 preload 로 빠르게.
- 외부 요청 0(폰트·CSS·JS 전부 같은 오리진). 상대경로: 서버 루트 `/var/www/font` 기준 `v/<ver>/…`·`latest/…`·`download/…` 로 배포되므로 `site/` 에서는 `../dist/…` 대신 **배포 기준 경로 변수** 하나로 관리(로컬 미리보기용 `--local` 스위치 또는 심링크 안내).
- Playwright 로 데스크톱·모바일 스크린샷(`docs/qa/shots/site-*.png`)을 찍어 팀장이 보게 한다. 다운로드 버튼이 실제 zip 을 가리키는지 `dist/packages/` 존재로 확인.

## 산출
`site/index.html`(+ `site/assets/site.css`, `site/assets/site.js`), `tools/package.py`, `dist/packages/*.zip` + `index.json`, `site/README.md`(로컬 미리보기·빌드·배포 경로 규약), `docs/PROGRESS.md` font-site 항목.
