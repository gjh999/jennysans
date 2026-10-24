# QA 보고서 — JennySans 1.001 (v1.0.1)

- 일자: 2026-10-24 · 대상: `dist/static/*.ttf` 9종 · `dist/variable/JennySansVariable.ttf` · `dist/web` · `dist/css` · `dist/packages`
- 변경 범위: 체크박스 ☐ U+2610 · ☑ U+2611 · ☒ U+2612 추가(자체 부품 합성), 소개 문구 "한글·영문(라틴)", 홈페이지 diff-table CSS 정렬
- 실행: 팀장이 독립 QA 스크립트(`docs/qa/scripts/*`)를 그대로 재실행. 재부팅으로 1차 실행이 끊겨 **파이프라인 전체 재빌드 후 처음부터 다시** 돌렸다.
- **판정: RELEASE OK** — FAIL 0, 새 WARN 0(WARN 은 1.000 과 같은 항목·같은 수), 승인 예외 0

## 1. 체크박스 3자 (이번 변경)

| 확인 | 결과 |
|---|---|
| cmap 존재 | 정적 9 + VF 모두 U+2610/2611/2612 → `uni2610`·`uni2611`·`uni2612` |
| cmap 수 | 13,254 → **13,257**(+3, 10 파일 동일) · 글립 13,980 → **13,983** |
| 진행폭·박스 | 진행폭 = □ U+25A1, bbox = □ (±1 unit) — 정적 9 + VF wght 100/400/900 (`verify_build` `ballot` 12건 PASS) |
| 마크 위치 | ✓ / × 가 □ 속공간 안, bbox 중심 = 속공간 중심 ±2 unit (같은 검사) |
| VF↔정적 | 9 웨이트 인스턴스 bbox·adv 차 ≤2 unit(합성 허용치 8 이내) — `variable.py` 합성 목록에 U+2610–2612 추가 후 PASS |
| 셰이핑·렌더 | fontbakery·shaping·render 에 새 글립 관련 경고 없음 |
| 육안 | `build/preview/ballot-static.png`(9 웨이트) · `build/preview/ballot-variable.png`(VF 100/400/900): 박스 위·아래가 □ 와 같은 선, 마크가 속공간 중앙 |

설계 메모: 마크는 아핀 축소라 박스보다 획이 가늘다(Regular 약 0.7배, Black 약 0.45배). 문서 체크 칸 판독에는 문제 없음. 새 외곽선을 그리지 않는다는 원칙(AGENTS §1-1)을 지킨 결과다.

## 2. 회귀 (기존 글립·메트릭 불변)

`tools/regress_snapshot.py diff build/regress-1.000.json build/regress-1.001.json` → **REGRESSION: PASS**
- 10 파일 모두: cmap 추가 3(U+2610–2612)·제거 0·재매핑 0 · 새 글립 3 · 기존 글립 외곽선(gvar 포함)·진행폭·LSB 변경 **0** · 수직 메트릭 동일
- 버전: head.fontRevision 1.0 → 1.001(16.16 고정소수 표현 1.00100708), name ID 5 `Version 1.001 (based on Pretendard 1.309; Noto Sans KR 2.004)`

## 3. 독립 QA 스크립트

| 스크립트 | 결과 |
|---|---|
| tickets | PASS (FAIL 0 · WARN 0 · PASS 90) |
| coverage (required 12,602 × TTF 10 + WOFF2 10) | PASS (FAIL 0 · WARN 0 · PASS 52) |
| shaping | PASS (FAIL 0 · WARN 4 · PASS 536) — WARN 4 = 1.000 과 같은 `vf-phantom` 1 unit 차 |
| names | PASS (FAIL 0 · PASS 272) |
| metrics | PASS (FAIL 0 · PASS 683) |
| supplement | PASS (FAIL 0 · PASS 140) |
| variable | PASS (FAIL 0 · WARN 1 · PASS 34) — WARN 1 = 1.000 과 같은 `static-interp`(정적 부품 점 수 차, VF 는 자체 일관) |
| web | PASS (FAIL 0 · PASS 40) |
| sizes | PASS (PASS 9) |
| render | PASS (PASS 30) |
| browser (Playwright) | PASS (PASS 7) |
| site/check_site.py | ALL PASS |
| fontbakery 1.1.0 check-universal | 정적 FAIL 0 · WARN 55 / 변수 FAIL 0 · WARN 8 — **1.000 과 같은 수·같은 9 검사 ID**, 새 글립 언급 0 (`docs/qa/fontbakery-1.001.md`) |

QA 스크립트 수정(버전 하드코딩 제거, 내용 판정 기준은 그대로): `qa_common.VERSION` 1.001, `names.py` ID 3/5 기대값을 `Q.VERSION` 으로, `metrics.py` fontRevision 을 `VERSION ±0.0005`(16.16 고정소수), `variable.py` 합성 목록 8 → 11자, `fontbakery_summary.py`·`render.py` 표기.

## 4. 패키지

`tools/package.py` 로 zip 4종 + `index.json` + `SHA256SUMS.txt` 재생성, `docs/qa/scripts/packages.py` 로 검사(결과 `docs/qa/results/packages.md`). 크기·SHA 정본은 `dist/packages/SHA256SUMS.txt`.
