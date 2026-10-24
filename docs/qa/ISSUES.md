# QA 티켓 (font-qa 소유)

> 심각도: blocker(릴리스 차단) / major / minor. 상태: open → fixed(빌드 n차) → verified(QA 재검) → closed.
> 재검 기준 빌드: **8차(dist 2026-09-09 09:41~09:45, 정적 글립 13,980 · VF 13,980 · cmap 13,254)**.
> 근거: `docs/qa/results/*.md|json`(2026-09-09 재실행), `docs/qa/fontbakery-1.000.md`, `docs/qa/QA-REPORT-1.000.md`.
> **열린 티켓 0건 · 릴리스 차단 요소 0건.**

## 1. 티켓 총괄 (1~11)

| # | 심각도 | 대상 | 증상 | 조치 | 담당 | 상태 |
|---|---|---|---|---|---|---|
| 1 | major | 정적 9·VF | fontbakery `case_mapping`: U+01C5/01C6 은 있는데 **U+01C4 DŽ** 없음 | U+01C4 = D + Zcaron 컴포지트 합성(6차) | builder | **verified** |
| 2 | major | 정적 9·VF | fontbakery `nested_components`: 컴포지트가 컴포지트를 참조하는 글립 113개 | 6차 정적 전량 평탄화·VF 5 잔존 → **8차에서 판정 허용치를 07 §7(c) 로 분리(Noto ≤2u / 컴포지트 ≤8u)해 167 전량 채택** | builder | **verified**(정적·VF 모두 0) |
| 3 | minor | 정적 9·VF | fontbakery `no_mac_entries`: platformID 1 레코드 잔존 | platformID 1 레코드 전부 제거(6차) | builder | **verified** |
| 4 | minor | 정적 9·VF | fontbakery `smart_dropout`: `prep` 없음 | `prep` = `PUSHW[] 511 SCANCTRL[] PUSHB[] 4 SCANTYPE[]` 추가(6차) | builder | **verified** |
| 5 | minor | Bold·ExtraBold·Black | 보충 `hangul-pos`: ㅥ(U+3165) 하단이 ㄴ 보다 19/21/25 unit 낮음(옛 허용치 ±15) | **결함 아님 — 원본 재현.** 글립 이동 없이 QA 검사식 정정 | qa | **closed(not-a-defect)** |
| 6 | minor | VF | fontbakery `transformed_components`: 변환 컴포넌트 사용 글립 | VF 에서 외곽선 분해 + gvar 재생성(6차 94 → 8차 100 전량) | builder | **verified** |
| 7 | minor | `docs/spec/07-supplement.md` §7(c) | 합성·컴포지트 목록이 7자 — 6차에 추가된 **U+01C4 가 누락** | §7(c) 를 **8자**로 갱신(Ǆ U+01C4 추가) + 평탄화 허용치 분리 근거 명문화 | architect | **closed(스펙 반영 확인)** |
| 8 | minor | `docs/spec/02-naming.md`·`03-metrics.md` | 스펙이 6차 변경 미반영(02 Mac 레코드 유지 / 03 `prep` 없음) | 02 §2-2 "Macintosh 레코드 — 없음", 03 `prep` 행을 실제 프로그램으로 정정 + QA 기준에 세로 테이블 부재 추가 | architect | **closed(스펙 반영 확인)** |
| 9 | minor | 정적·WOFF2 Thin/EL/Light | `vhea`/`vmtx` 가 3 웨이트에만 존재(원본 Pretendard 유래 비대칭) | `vhea`·`vmtx`·`VVAR`·`VORG` 를 **10 파일 전부에서 제거**(8차) | builder | **verified** |
| 10 | minor | `dist/css`·VF 분할 | 스펙 05 §4 크기 목표 초과(CSS gzip 101 KB / VF 라틴 69 KB) | 팀장 결정(AGENTS §8 2026-09-09): **목표를 실측에 맞춰 조정**(CSS ≤110 KB, VF 슬라이스 ≤95 KB·라틴 ≤70 KB) + 소비자 권고 문구. QA `web.py` 임계값도 갱신 | 팀장·architect | **closed(목표 조정)** |
| 11 | minor | 정적 9·VF | fontbakery `unreachable_glyphs`: 고아 글립(정적 4 / VF 6) | 서브셋 단계에서 제거(8차). `.null` 은 예약 글립이라 유지 | builder | **verified** |

## 2. 8차 재검 근거 (fontbakery·빌더 코드와 독립 측정)

### fontbakery 재실행 (`docs/qa/fontbakery-1.000.md`, 2026-09-09)

| | 5차 | 6차 | **8차** |
|---|---|---|---|
| 정적 9종 FAIL | `case_mapping` 9 · `nested_components` 9 · `no_mac_entries` 486 · `smart_dropout` 9 = **513** | **0** | **0** |
| VF FAIL | 위 4종 + `transformed_components` = **58** | `nested_components` **1** | **0** |
| WARN(검사 인스턴스) | — | 73 / 10 검사 ID | **63 / 9 검사 ID** |

- **정적·VF 모두 FAIL 0 · ERROR 0 → 게이트 3 을 승인 예외 없이 통과한다.**
- 줄어든 WARN 10건은 정확히 `unreachable_glyphs`(티켓 11). **새로 생긴 WARN 종류 0** — 빌더 보고(73→63)와 일치.
- `family/win_ascent_and_descent` 는 정적·VF 전부 **SKIP**(`Unfulfilled Conditions: not is_cjk_font`) — 승인 예외를 쓰지 않았다.

### 독립 측정 (`docs/qa/scripts/tickets.py` → `docs/qa/results/tickets.md`, PASS 90 / FAIL 0)

- **티켓 1**: 10 파일 전부 U+01C4/01C5/01C6 존재. U+01C4 = `['D','Z','caron']`, adv = `adv(D)+adv(Zcaron)` 정확 일치(VF 1404+1218 = 2622).
- **티켓 2**: **중첩 컴포지트 정적 9종 0 · VF 0**(6차 VF 5 → 8차 0). `variable.py` 인스턴스 비교: Noto 유래 909글립 bbox ≤2u·adv 동일 위반 0, 컴포지트 8자 ≤8u 위반 0.
- **티켓 3**: 10 파일 platformID 1 레코드 **0**(`names.md` `mac-records` 20/20 PASS).
- **티켓 4**: 10 파일 prep 니모닉 `['PUSHW[]','511','SCANCTRL[]','PUSHB[]','4','SCANTYPE[]']` · gasp `{0xFFFF:0x000F}` 동일.
- **티켓 5**: U+3165–318E 보충 41자 × 10 파일, `|J차 − 1.965×N차| ≤ 6u` **최대 1.5u, 위반 0**(N 은 QA 가 Noto VF 를 웨이트별 인스턴스해 직접 측정).
- **티켓 6**: 10 파일 변환(2×2 행렬) 컴포넌트 사용 글립 **0**.
- **티켓 9**: `vhea`/`vmtx`/`VVAR`/`VORG` 가 **TTF 10 + WOFF2 10 = 20 파일 전부에 없음**. `metrics.py` WARN 12 → **0**.
- **티켓 11**: **도달 불가 글립 0** — 도달성을 QA 가 자체 계산(cmap+UVS ∪ GSUB/GPOS/GDEF/MATH/BASE/JSTF 객체 트리 등장 ∪ 컴포넌트 폐포 ∪ 예약 5종).
  빌더 `fontutil.reachable_glyphs()` 를 쓰지 않은 독립 구현이며 fontbakery(룩업 *출력*만 도달로 봄)보다 보수적이다.
  제거 대상(정적 4 / VF 6) 전부 부재 · `.null` 유지 확인.

### 티켓 11 — 제거가 렌더에 영향 없음(실증)

- 제거된 글립은 **cmap 에 매핑된 적이 없다**(U+0189·U+0384 등 실측 `in cmap: False`) → 어떤 코드포인트도 잃지 않았다.
- **cmap 13,254 불변**(정적 9종 동일 · VF 동일 · WOFF2 동일), required 12,602/12,602, 한글 11,172/11,172.
- 셰이핑: 11,172 음절 + 12개 언어 문단(그리스 `el` 71자 포함) **gid0 0건**. `tonos`(그리스 악센트) 제거가 그리스 조판에 영향 없음을 실측.
- 렌더: `docs/qa/shots/render-all-weights.png` 가 6차와 동일(줄높이 34px 불변), 괘선 연결 27/27 PASS, 브라우저 9/9 로드.

## 3. 티켓 5 상세 — 결함이 아님(닫음)

- Noto Sans KR 자신이 ㅥ 을 ㄴ 보다 아래에 그린다(Regular −3 → Black −13, Thin~Light 는 +2~+4). 우리 편차는 전부 `sy(1.965) × Noto 편차` 와
  오차 ≤1.5 unit 으로 일치 → **이식이 정확하다는 증거**. 옮기면 원본 디자인 변경(AGENTS §1-1·§5 위반). 팀장 판정 AGENTS §8 2026-09-07, 실측 `build/ticket5-measure.md`.
- QA 검사식 정정(`docs/qa/scripts/supplement.py`): 고정 ±15 폐기 → `|(J대상하단 − J ㄴ하단) − sy(1.965)×(N대상하단 − N ㄴ하단)| ≤ 6 unit`,
  대상 U+3165–U+318E 보충 41자 전부. N 은 `noto_bbox()` 가 Noto VF 를 서브셋 → `varLib.instancer` 로 웨이트별 인스턴스해 직접 측정(빌드 기록 미사용).
- 참조쌍(07 §8-3) 기대 비율도 하드코딩 → **Noto 원본 실측**으로 교체 → 5차에서 WARN 이던 4쌍(◐~○·⊂~≠·♠~♥·◌~○) 전부 PASS. ◌~○ 의 실제 Noto 비는 **1.031**.

## 4. 승인 예외 — 게이트 집계에서 제외한 항목

> **VF `nested_components` 예외는 8차에서 해소돼 삭제했다**(팀장 결정 AGENTS §8 2026-09-09 = 승인 예외를 늘리지 않고 고침).
> 현재 **fontbakery FAIL 을 발생시키는 승인 예외는 0건**이다.

1. **`family/win_ascent_and_descent`** — AGENTS §8 2026-09-06·스펙 03 §2 가 승인 예외로 지정했으나, **이번 빌드에서는 발동하지 않았다**:
   fontbakery 1.1 이 이 폰트를 CJK 로 분류해 정적 9·VF 전부 **SKIP**(`Unfulfilled Conditions: not is_cjk_font`).
   즉 예외를 쓰지 않고도 FAIL 0 이다. OS/2 win 1950/494 유지 결정 자체는 유효(`family/vertical_metrics` PASS).
2. **fontbakery WARN 63건 / 9 검사 ID** — 전부 원본 유래이거나 정보성. 검사별 사유표는 `docs/qa/QA-REPORT-1.000.md` §3.
   (`cjk_chws_feature` · `contour_count` · `file_size` · `math_signs_width` · `opentype/gdef_mark_chars` · `soft_hyphen` ·
   `overlapping_path_segments` · `interpolation_issues`(VF) · `mandatory_avar_table`(VF))
3. **괘선 가로/세로 획 두께비 1.38** — 셀 종횡비 1000:1000 → 1770:2444 비균등 스케일의 필연(AGENTS §8 2026-09-06, 스펙 07 §4-5).
   렌더 연결 검사 27/27 PASS 로 실사용 영향 없음을 확인.
4. **합성·컴포지트 8자(U+01C4 포함)의 VF↔정적 편차 ≤8 unit** — 부품이 Pretendard VF 보간이라 생기는 반올림.
   티켓 7 로 **스펙 07 §7(c) 에 명문화**됐으므로 더는 "예외"가 아니라 스펙 허용치다. 8차 실측 bbox ≤4.804u · adv ≤4u.

## 5. QA 스크립트 자체 WARN (fontbakery 밖, 전부 설명됨 — 티켓 아님)

- `shaping.py` 4건: VF wght 650·900 에서 ㉠ adv 가 ① 보다 **1 unit** 작음(VF 의 ① 은 Pretendard VF 보간, ㉠ 은 정적 참조값 유래). 1 unit = 0.05%.
- `variable.py` 1건: U+2252(≒) 의 점 수가 웨이트별로 다름 — 부품 `period` 점 수가 원본 Pretendard 에서 웨이트마다 다르기 때문(정상).

## 6. 닫힌 티켓
**1·2·3·4·5·6·7·8·9·10·11 전부 종결** — verified 7건(1·2·3·4·6·9·11), closed 4건(5 not-a-defect · 7·8 스펙 반영 · 10 목표 조정).
