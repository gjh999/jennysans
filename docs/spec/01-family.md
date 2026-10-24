# 01 — 패밀리 구조 스펙 (JennySans)

> 소유: font-architect · 상태: **P2 2차 — 원본 확정 반영(2026-09-06)**. 실측값은 `charset/scripts/measure_sources.py`·`docs/research/measurements.md` 기준.
> 상위 규칙: `AGENTS.md` §1·§4·§7·§8. 각 절 끝의 **QA 합격 기준**은 `font-qa` 가 검증한다.

## 1. 패밀리 정체성

| 항목 | 값 |
|---|---|
| 영문 패밀리명 | **JennySans** (한 단어, 공백·하이픈 없음) — RFN |
| 한국어 현지화명 | **제니산스** (name ID 1/16 ko-KR) — RFN(팀장 결정 ⑤). 「제니고딕」 대안은 사용자 결정 대기 |
| 분류 | 범용 본문 고딕(산세리프), 한글 + 라틴(서유럽·중앙유럽·그리스·키릴 기본) + 한국 문서 기호 |
| 제작 방식 | **방식 A** — Pretendard 파생 + Noto Sans KR VF 결손 보충 (AGENTS §8 2026-09-06, `docs/research/04-recommendation.md`) |
| 주원본 | **Pretendard 1.3.9** — `sources/Pretendard/alternative-ttf/Pretendard-<W>.ttf`(glyf, UPM 2048, 9종은 zip `public/static/alternative/` 에서 추출) + `PretendardVariable.ttf`(wght 45–930) |
| 보충원본 | **Noto Sans KR 2.004 VF** — `sources/NotoSansKR/NotoSansKR[wght].ttf`(glyf, UPM 1000, wght 100–900) → 결손 904글립을 웨이트별 인스턴스 후 스케일 이식(`07-supplement.md`) |
| 3차 원본 | **없음(권고)** — 두 원본 모두 없는 required 4자(⅔ ∼ ≒ ◈)는 Pretendard 부품 합성·미러로 해결(`07-supplement.md` §5). 폴백 Gothic A1 은 팀장 결정 시 |
| 라이선스 | SIL OFL 1.1, RFN "JennySans"·"제니산스"; 원본 RFN 누적 고지 Pretendard·Source·Inter·M PLUS 1 (`06-license.md`) |
| 첫 릴리스 버전 | **1.000** (`head.fontRevision` 1.0, name ID 5 "Version 1.000 …") ↔ git 태그 **v1.0.0** ↔ npm **1.0.0** — 규칙 `X.YZZ ↔ X.Y.ZZ` (예: 1.001 ↔ v1.0.1, 1.100 ↔ v1.1.0) |

## 2. 웨이트 축 — 정적 9종 (Pretendard 9종 실보유, 웨이트 축소 없음)

| # | 스타일명(ID 17) | usWeightClass | RIBBI 그룹(ID 1) | ID 2 | PostScript(ID 6) | 파일 stem | 원본 파일 |
|---|---|---|---|---|---|---|---|
| 1 | Thin | 100 | JennySans Thin | Regular | JennySans-Thin | `JennySans-Thin` | Pretendard-Thin.ttf |
| 2 | ExtraLight | 200 | JennySans ExtraLight | Regular | JennySans-ExtraLight | `JennySans-ExtraLight` | Pretendard-ExtraLight.ttf |
| 3 | Light | 300 | JennySans Light | Regular | JennySans-Light | `JennySans-Light` | Pretendard-Light.ttf |
| 4 | Regular | 400 | JennySans | Regular | JennySans-Regular | `JennySans-Regular` | Pretendard-Regular.ttf |
| 5 | Medium | 500 | JennySans Medium | Regular | JennySans-Medium | `JennySans-Medium` | Pretendard-Medium.ttf |
| 6 | SemiBold | 600 | JennySans SemiBold | Regular | JennySans-SemiBold | `JennySans-SemiBold` | Pretendard-SemiBold.ttf |
| 7 | Bold | 700 | JennySans | Bold | JennySans-Bold | `JennySans-Bold` | Pretendard-Bold.ttf |
| 8 | ExtraBold | 800 | JennySans ExtraBold | Regular | JennySans-ExtraBold | `JennySans-ExtraBold` | Pretendard-ExtraBold.ttf |
| 9 | Black | 900 | JennySans Black | Regular | JennySans-Black | `JennySans-Black` | Pretendard-Black.ttf |

- 스타일명은 AGENTS §7 확정값. Pretendard 의 스타일명(Thin…Black, usWeightClass 100…900)과 1:1 — 이름만 바꾼다.
- Pretendard 정적 TTF(alternative)의 `OS/2.sTypoAscender` 는 1949 로 VF(1950)와 1 unit 다르다 → 1950 으로 정정(AGENTS §8, `03-metrics.md`).
- 보충 글립은 웨이트마다 Noto VF 를 같은 wght 로 인스턴스해 넣는다(Thin 은 Noto 100, Black 은 Noto 900).

**QA 합격 기준 (2)**: `dist/static/` 9 파일 존재, `usWeightClass` 표와 일치, name ID 17 정확 일치, 9 파일 cmap 코드포인트 집합 동일(보충 글립 포함 12,602 required 전부 + recommended 548 + korean-old 103).

## 3. 이탤릭 없음 (사유)

- Pretendard·Noto Sans KR 모두 이탤릭이 없다(한글 조판 관행). 라틴만 기울이면 한·라틴 혼용에서 어긋난다. 합성 오블리크는 외곽선 수정이라 범위 밖.
- 전 파일 `fsSelection.ITALIC=0`, `macStyle.italic=0`, `post.italicAngle=0`, `hhea.caretSlope 1/0`. Pretendard VF 의 STAT `ital` 축 레코드는 **제거**하고 `wght` 단일 축으로 쓴다(`02-naming.md` §4-3).
- 소비자 안내: CSS `font-synthesis: none;`(`05-web.md`).

**QA 합격 기준 (3)**: ITALIC/OBLIQUE 비트 0, italicAngle 0, name·STAT·fvar 에 "Italic"/"Oblique" 문자열 없음.

## 4. 파일 형식과 산출 목록 (AGENTS §8: 1.000 = TTF 정적 9 + 변수 TTF + WOFF2 전체·분할 + CSS 3종; OTF 는 1.1 이후)

| 용도 | 형식 | 경로 | 수량 | 비고 |
|---|---|---|---|---|
| 데스크톱 설치(Windows·한글·MS Office·macOS·Adobe·Unity·Flutter) | **TTF** (glyf, 무힌팅) | `dist/static/JennySans-<Weight>.ttf` | 9 | Pretendard alternative TTF 기반 + 보충 글립. Pretendard TTF·Noto VF 모두 TT 힌트 없음(`fpgm/prep` 없음) → 무힌팅 유지 |
| 변수 폰트 | **TTF** (glyf+gvar) | `dist/variable/JennySansVariable.ttf` | 1 | PretendardVariable 기반. 축 `wght` **100–900 확정**(원본 45–930 을 L4 절단, AGENTS §8 2026-09-06, `07-supplement.md` §7-2) |
| 웹 전체본 | **WOFF2** | `dist/web/JennySans-<Weight>.woff2` | 9 | |
| 웹 변수 전체본 | WOFF2 | `dist/web/JennySansVariable.woff2` | 1 | |
| 웹 분할본 | WOFF2 | `dist/web/subset/JennySans-<Weight>.subset.<n>.woff2` | 9 × ≤124 | Google Fonts 한국어 124 슬라이스 재사용(`05-web.md`) |
| 웹 변수 분할본 | WOFF2 | `dist/web/subset/JennySansVariable.subset.<n>.woff2` | ≤124 | |
| CSS | text | `dist/css/jennysans.css`, `jennysans-variable.css`, `jennysans-dynamic-subset.css` (+선택 `jennysans-variable-dynamic-subset.css`) | 3(+1) | |
| OTF(CFF) | — | (1.1 이후) | 0 | CFF 이식은 qu2cu·별도 QA 필요(AGENTS §8) |

**QA 합격 기준 (4)**: 표의 파일 전부 존재·`TTFont` 로 열림·`ttx_roundtrip` PASS; 정적 TTF 에 `glyf/loca` 존재·`CFF ` 없음; 같은 웨이트의 TTF/WOFF2 cmap 동일; DSIG 없음(Pretendard TTF 의 DSIG 제거).

## 5. 파일명 규칙 (AGENTS §7)

```
JennySans-<Weight>.ttf / .woff2               Weight ∈ {Thin, ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black}
JennySansVariable.ttf / .woff2
JennySans-<Weight>.subset.<n>.woff2           n = Google 슬라이스 번호(0…123; 빈 슬라이스는 결번) + 124 = rest
JennySansVariable.subset.<n>.woff2
```
- 파일명 = PostScript 이름(ID 6) + 확장자. 공백·괄호·`[wght]` 사용 안 함.
- 릴리스 압축본: `JennySans-1.000.zip`(폰트 버전 표기) — git 태그 `v1.0.0`, npm `@jennysoft/jennysans@1.0.0`.

**QA 합격 기준 (5)**: 정규식 `^JennySans(-(Thin|ExtraLight|Light|Regular|Medium|SemiBold|Bold|ExtraBold|Black)|Variable)(\.subset\.\d+)?\.(ttf|woff2)$`; stem = name ID 6.

## 6. 정적 ↔ 변수 인스턴스 대응

| 정적 파일 | 변수 `wght` 좌표 | fvar 인스턴스 subfamilyName | fvar postScriptName | Pretendard VF 원 인스턴스 |
|---|---|---|---|---|
| JennySans-Thin | 100 | Thin | JennySansVariable-Thin | Thin(100) |
| JennySans-ExtraLight | 200 | ExtraLight | JennySansVariable-ExtraLight | ExtraLight(200) |
| JennySans-Light | 300 | Light | JennySansVariable-Light | Light(300) |
| JennySans-Regular | 400 (default) | Regular | JennySansVariable-Regular | Regular(400) |
| JennySans-Medium | 500 | Medium | JennySansVariable-Medium | Medium(500) |
| JennySans-SemiBold | 600 | SemiBold | JennySansVariable-SemiBold | SemiBold(600) |
| JennySans-Bold | 700 | Bold | JennySansVariable-Bold | Bold(700) |
| JennySans-ExtraBold | 800 | ExtraBold | JennySansVariable-ExtraBold | ExtraBold(800) |
| JennySans-Black | 900 | Black | JennySansVariable-Black | Black(900) |

- 변수 폰트 패밀리명 **"JennySans Variable"**(ID 1/16), ko "제니산스 Variable", PS `JennySansVariable-<Weight>` (팀장 결정 ③, AGENTS §7).
- Pretendard VF 인스턴스 좌표가 정적과 정확히 일치(실측 fvar 9 인스턴스 100…900)하므로 `wght=400` 외곽선 = 정적 Regular(실측: 가·H·x·0 bbox 동일).
- 보충 글립은 9 인스턴스 피크 gvar 로 넣는다(`07-supplement.md` §7).

**QA 합격 기준 (6)**: fvar 인스턴스 9개 표와 일치, `defaultValue=400`, STAT 9 값(`02-naming.md` §4-3), fontbakery `opentype/varfont/*` PASS, 변수 폰트 400 인스턴스 vs 정적 Regular 대표 글립 20자 좌표 차 ≤ 1 unit.

## 7. 문자집합 (정본 `charset/`, 2026-09-06 팀장 결정 반영)

| 파일 | 코드포인트 | 게이트 | Pretendard 보유 | Noto 이식 | 합성 |
|---|---|---|---|---|---|
| `charset/required.txt` | **12,602** | 필수(게이트 1) | 12,054 | 544 | 4 |
| `charset/recommended.txt` | 898 | 원본 보유분 유지 | 291 | 257 | — (350 은 미보유) |
| `charset/korean-old.txt` | 103 | 원본 보유분 유지(범위 밖 후보) | 0 | 103 | — |

빌드 대상 = required ∪ recommended ∪ korean-old (∩ 두 원본 보유). 세부는 `charset/README.md`.

## 8. 범위 밖 (명시)

| 항목 | 사유 | 후속 |
|---|---|---|
| 이탤릭 | §3 | 없음 |
| 한자(KS X 1001 한자 4,888 포함) | 파일 크기·범용 목적 불일치 | `JennySans Hanja` 보조 폰트 |
| 일본어 가나(KS 행10·11; Pretendard 의 M PLUS 유래 가나 글립 포함) | 범위 밖 → 서브셋에서 제외(AGENTS §8) | 후속 검토 |
| 옛한글 조합(`ljmo/vjmo/tjmo`) | 자모 단독 글립만 실음 | `charset/korean-old.txt` |
| 베트남어(U+1EA0–1EF9) | 프리컴포즈 134자 설계 필요 | `charset/README.md` |
| OTF(CFF) | 1.1 이후 | AGENTS §8 |
| 이모지·컬러, 세로쓰기 신규, 모노스페이스 | 범위 밖 | 없음 |

## 9. 갱신 이력
- 2026-09-06: 원본 확정 반영(Pretendard + Noto KR VF, 방식 A), 산출 형식(OTF 제외), 변수 폰트명, 버전↔태그 규칙, 문자집합 수치 갱신.
