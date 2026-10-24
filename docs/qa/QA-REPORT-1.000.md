# RELEASE OK

> 게이트 8항목 **전부 PASS**. fontbakery 정적 9종·변수 폰트 **모두 FAIL 0 · ERROR 0** — **승인 예외를 하나도 쓰지 않았다.**
> 열린 티켓 0건, 릴리스 차단 요소 0건. 1.000 을 릴리스해도 된다.

작성 2026-09-09, font-qa. 검사 대상 **8차 빌드**(`dist/` 2026-09-09 09:41~09:45).

- 산출물: 정적 TTF 9종 글립 **13,980** · VF **13,980** · cmap **13,254** · 정적 2,553,816–2,700,344 B · VF 7,009,656 B
- 검사 스크립트: `docs/qa/scripts/` — 빌더 `tools/verify_build.py` 와 **독립**(공용은 `tools/charset.py` 파서뿐)
- 티켓 대장: `docs/qa/ISSUES.md` (1~11 전부 종결)

---

## 1. 게이트 8항목 (AGENTS §4)

| # | 항목 | 판정 | 근거 파일 | 실측 요약 |
|---|---|---|---|---|
| 1 | 커버리지 | **PASS** | `results/coverage.md` | `charset/required.txt` 12,602 코드포인트 × **20 파일**(정적 TTF 9 + VF + WOFF2 10) 전부 cmap 존재·비-`.notdef`·외곽선 있음(공백류 7 제외), 누락 **0**. 한글 음절 **11,172/11,172**. 정적 9종 cmap 집합 완전 동일(**13,254**), VF·WOFF2 도 동일 — 8차 글립 제거(13,984→13,980) 후에도 **cmap 불변** |
| 2 | 셰이핑 | **PASS** | `results/shaping.md` | uharfbuzz: 11,172 음절 각 1글립·**gid0 0건**(20 파일). ko/en/**es**/pl/cs/tr/de/ro/**el**/ru + 숫자·기호 12 문단 gid0 0. 스페인어 결합 시퀀스 12종 **ccmp 합성 12·실패 0**(프리컴포즈와 동일 결과). 한글 NFD→음절 합성 동일 |
| 3 | fontbakery | **PASS** | `docs/qa/fontbakery-1.000.md` | **정적 9종 FAIL 0**(검사 1,047 실행) · **VF FAIL 0**(127 실행). ERROR 0. **승인 예외 사용 0건** — `win_ascent_and_descent` 는 CJK 폰트로 분류돼 전부 SKIP. WARN 63건/9 검사 ID(전부 원본 유래·정보성, §3 표) |
| 4 | 패밀리 묶임 | **PASS** | `results/win-install.md`·`names.md`·`metrics.md` | Windows 사용자 범위 실설치: **DirectWrite `JennySans` 1패밀리 = 9 typeface** + **`JennySans Variable`** 별도 1패밀리. GDI 16 패밀리(RIBBI 규칙대로 `JennySans` 가 Regular+Bold style-link). 요청 10종 전부 의도한 패밀리로 해석(OK 10/10). name 20 파일 spec 02 문자열 **완전 일치**, PostScript 이름 18개 유일, fsSelection 0x1C0(USE_TYPO+WWS)·macStyle 0·usWeightClass 100–900 |
| 5 | 메트릭 | **PASS** | `results/metrics.md`·`render.md` | 20 파일 전부 동일 튜플 `UPM 2048 · typo 1950/−494/0 · hhea 1950/−494/0 · win 1950/494` + `USE_TYPO_METRICS`, underline −258/139, 한글 진행폭 1770. **WARN 0**(8차에서 `vhea/vmtx` 제거로 12건 소멸). 렌더: 같은 문장 100/400/900 줄 간격 **픽셀 동일(34px)** |
| 6 | 파일 크기 | **PASS** | `results/sizes.md`·`web.md`·`browser.md` | 정적 TTF 9종 원본 Pretendard 대비 **−5.9~−6.0%**(6차 −4.0% → 세로 테이블 제거로 개선). 웹 첫 화면(한국어 페이지 A, 분할 CSS) **62,300 B / 요청 2건**. 스펙 05 §4 목표 **전 항목 충족**(CSS gzip 101,344 ≤110 KB · VF 슬라이스 90,472 ≤95 KB · VF 라틴 69,304 ≤70 KB — 티켓 10 조정 반영) |
| 7 | 렌더 실측 | **PASS** | `docs/qa/shots/` 41장 · `render.md`·`browser.md`·`win-install.md` | PIL/FreeType 9 웨이트 + VF 시트, 괘선 연결 픽셀 검사 **27/27**(빈 행·열 0, 축 중간값 250·650 포함), Chromium 4 모드 스크린샷 `faces declared=9 loaded=9`, Windows GDI 실설치 렌더 10종. 8차 글립 제거 후에도 **6차와 시각적으로 동일** |
| 8 | 라이선스 | **PASS** | `results/names.md` | 20 파일 name ID 0 1행 == `LICENSE` 1행(**UTF-8 112 bytes 바이트 동일**). ID 0 에 원본 저작권 4블록 원문 포함, ID 7 상표 4건·ID 9 크레딧 유지, ID 13/14 정확 일치. **식별 레코드(1/2/3/4/6/16/17/25)·fvar·STAT·글립명 13,980개에 원본 RFN 문자열 0건**. OFL 본문 SHA-256 = openfontlicense.org 원문 일치. THIRD-PARTY 표 2행 = AGENTS §5-1 채택 2건, MANIFEST SHA-256 4건 일치 |

## 2. 검사 13종 결과 (전부 FAIL 0)

| 스크립트 | 결과 | FAIL | WARN | PASS | 6차 대비 |
|---|---|---|---|---|---|
| `tickets.py` | PASS | 0 | 0 | 90 | 티켓 9·11 검사 추가(49→90) |
| `coverage.py` | PASS | 0 | 0 | 52 | 동일 |
| `shaping.py` | PASS | 0 | 4 | 536 | 동일(설명된 WARN) |
| `names.py` | PASS | 0 | 0 | 273 | 동일 |
| `metrics.py` | PASS | 0 | **0** | 683 | **WARN 12 → 0**(티켓 9) |
| `supplement.py` | PASS | 0 | 0 | 140 | 동일 |
| `variable.py` | PASS | 0 | 1 | 34 | 동일(설명된 WARN) |
| `web.py` | PASS | 0 | **0** | 40 | **WARN 2 → 0**(티켓 10 목표 조정) |
| `packages.py` | PASS | 0 | 0 | 31 | 동일 |
| `sizes.py` | PASS | 0 | 0 | 9 | 원본 대비 −4.0% → **−5.9%** |
| `render.py` | PASS | 0 | 0 | 30 | 동일 |
| `browser.py` | PASS | 0 | 0 | 7 | 동일 |
| `win-install-test.ps1` | PASS | — | — | — | 설치→열거→렌더→제거, 잔존 0 |
| **fontbakery 정적** | **PASS** | **0** | 55 | 647 | FAIL 0 유지, WARN −9 |
| **fontbakery 변수** | **PASS** | **0** | 8 | 96 | **FAIL 1 → 0** |

`dist/packages/` 는 font-site 가 8차 기준으로 재생성한 뒤(2026-09-09 10:10 > `dist/static` 09:41) 검사했다 — zip 4종 안의 폰트 바이트가 `dist/` 와 동일함을 확인.

## 3. 승인 예외 — **fontbakery FAIL 을 만드는 예외 0건**

6차에 남아 있던 **VF `nested_components` 예외는 8차에서 해소**됐다(팀장 결정 AGENTS §8 2026-09-09 — 승인 예외를 늘리지 않고 고침).
QA 가 권고한 대로 평탄화 판정 허용치를 스펙 07 §7(c) 로 분리하니 중첩 167이 전량 채택돼 **VF 중첩 컴포지트 0** 이 됐다.

### 3-1. 발동하지 않은 지정 예외
- **`family/win_ascent_and_descent`**(AGENTS §8 2026-09-06·스펙 03 §2 지정): fontbakery 1.1 이 이 폰트를 CJK 로 분류해
  정적 9·VF 전부 **SKIP**(`Unfulfilled Conditions: not is_cjk_font`). **예외를 쓰지 않고도 FAIL 0.**
  OS/2 win 1950/494 유지 결정 자체는 유효하다(`family/vertical_metrics` PASS).

### 3-2. WARN 63건 / 9 검사 ID — 사유 판단
| 검사 ID | 건수 | 사유 |
|---|---|---|
| `cjk_chws_feature` | 20 | `chws`/`vchw`(CJK 문맥 자간) 미보유. 원본 Pretendard 도 없음. 한국어 본문 조판에 필수 아님 — 1.1 이후 검토 |
| `contour_count` | 9 | fontbakery 의 "일반적 윤곽 수" 통계(라틴 위주 표본)와 다른 한글·KS 기호 글립 |
| `file_size` | 10 | 2.6 MB(정적)·6.7 MB(VF) > 권고 1 MB. 한글 11,172자 폰트의 필연 — 웹은 분할 WOFF2 로 해결(첫 화면 62 KB) |
| `math_signs_width` | 10 | 수학 기호 진행폭 불균일. Pretendard(라틴계 폭) + Noto 이식(전각계 폭) 혼재 — 스펙 07 §6 `math-rel` 규칙대로 이식한 결과 |
| `opentype/gdef_mark_chars` | 10 | U+0300·0306·0327 이 GDEF mark 클래스에 없음. **원본 Pretendard 동일** — 결합문자 셰이핑은 실측 PASS(ccmp 12/12) |
| `soft_hyphen` | 10 | U+00AD 보유. required 문자이므로 의도적 |
| `overlapping_path_segments` | 2 | 한글 음절 일부(uniAEF4 등)에 같은 좌표의 중복 선분. **원본 Pretendard 유래**, 외곽선 편집 금지(AGENTS §1-1) |
| `interpolation_issues` | 1(VF) | `uni030B` 윤곽 순서 차이 등. 원본 `PretendardVariable` 유래 |
| `mandatory_avar_table` | 1(VF) | `avar` 없음 — 축을 100–900 으로 절단(AGENTS §8 2026-09-06)하며 원본 avar 미사용. 9 인스턴스가 정적과 일치함을 `variable.py` 로 실측(보충 909글립 bbox ≤2u·adv 동일 위반 0) |

**새로 생긴 WARN 종류 0.** 6차 대비 사라진 것은 `unreachable_glyphs` 10건(티켓 11)뿐이다.

### 3-3. 그 밖의 유지 항목
- **괘선 가로/세로 획 두께비 1.38**: 셀 종횡비 1000:1000 → 1770:2444 비균등 스케일의 필연(AGENTS §8 2026-09-06, 스펙 07 §4-5). 렌더 연결 27/27 PASS.
- **합성·컴포지트 8자(U+01C4 포함)의 VF↔정적 편차 ≤8 unit**: 티켓 7 로 **스펙 07 §7(c) 에 명문화**돼 더는 예외가 아니라 스펙 허용치다. 8차 실측 bbox ≤4.804u·adv ≤4u.
- **티켓 5(ㅥ U+3165 하단)**: 결함 아님 — 원본 재현. 41자 × 10 파일에서 `|J차 − 1.965×N차| ≤ 6u` **최대 1.5u, 위반 0**.
- QA 스크립트 자체 WARN 5건(`shaping` 4 = VF 극단 웨이트 ㉠ adv 1 unit 차 / `variable` 1 = U+2252 웨이트별 점 수 차)은 전부 원인이 설명된 정보성이다.

## 4. 티켓 상태 (1~11 전부 종결)

| # | 상태 | 8차 실측 확인 |
|---|---|---|
| 1 | **verified** | U+01C4 = `['D','Z','caron']`, adv = adv(D)+adv(Zcaron) 정확 일치. `case_mapping` PASS |
| 2 | **verified** | 중첩 컴포지트 **정적 0 · VF 0**(6차 VF 5 → 0). `nested_components` PASS |
| 3 | **verified** | platformID 1 레코드 0(20 파일). `no_mac_entries` PASS |
| 4 | **verified** | prep 4명령·gasp 0x000F 동일. `smart_dropout` PASS |
| 5 | **closed(not-a-defect)** | 원본 재현 재확인(최대 1.5u ≤ 6u) |
| 6 | **verified** | 변환 컴포넌트 사용 글립 0(VF 포함). `transformed_components` PASS |
| 7 | **closed** | 스펙 07 §7(c) 가 8자(Ǆ U+01C4 포함) + 평탄화 허용치 분리로 갱신됨 — QA 확인 |
| 8 | **closed** | 스펙 02 §2-2 "Macintosh 레코드 — 없음", 03 `prep` 행 정정 — QA 확인 |
| 9 | **verified** | `vhea`/`vmtx`/`VVAR`/`VORG` 가 TTF 10 + WOFF2 10 **전부에 없음**. `metrics.py` WARN 0 |
| 10 | **closed(목표 조정)** | 스펙 05 §4 목표 갱신 확인, `web.py` 임계값 반영 후 **WARN 0** |
| 11 | **verified** | 도달 불가 글립 **0**(QA 자체 도달성 계산). 제거 글립은 cmap 미매핑이었고 cmap·셰이핑·렌더 전부 불변 |

**티켓 7·8·10 은 문서·목표 문제였고 architect·팀장이 처리를 마쳤다 — 릴리스 차단 요소가 아니었고, 지금은 전부 종결됐다.**

## 5. 팀장이 눈으로 볼 스크린샷 3장

1. **`docs/qa/shots/render-all-weights.png`** — PIL/FreeType 9 웨이트(한글·영문·스페인어·숫자·KS 기호·괘선·자모) + 100/400/900 줄높이 비교(세 블록 모두 34px)
2. **`docs/qa/shots/win-gdi-all-weights.png`** — Windows 실제 설치 후 GDI(ClearType) 렌더, 9 웨이트 + 변수, 각 4줄
3. **`docs/qa/shots/browser-static.png`** — Chromium `site/test.html` 정적 CSS, 9 웨이트 × 6열 + 줄높이·분할 커버 검사

보조: `browser-pageB-subset.png`(분할 로드 실문단) · `box-Regular-48px.png`(괘선 연결) · `render-variable.png`.

## 6. 팀장이 결정할 것

**릴리스를 막는 항목은 없다.** 아래는 릴리스 이후 판단 사항이다.

1. **1.000 릴리스 진행 여부** — QA 관점에서는 승인. 다음 단계는 본배포(nginx conf 교체 → `deploy.sh` → 사이트 확인) → git 태그 `v1.0.0` → 사용자 승인 후 GitHub/npm.
2. **`font-release` 문서 수치 재기입 필요** — 8차에서 `dist/` 전 파일의 크기·SHA-256 이 바뀌었다(정적 −54,352 B ×3 / VF +1,580 B 등).
   README·DISTRIBUTION·CHANGELOG·SHA256SUMS 의 수치가 **7차 이전 값이면 갱신해야 한다**(QA 구역 밖이라 확인만 함).
3. **1.1 이후 백로그**(전부 원본 유래 WARN, 1.000 비차단): `chws`/`vchw` 추가 여부 · `avar` 도입 여부 · `gdef_mark_chars` 보정 여부.
4. **실화면 확인**(QA 가 못 한 것): 한글(HWP)·MS Word·Photoshop **앱 UI 목록**에서 「제니산스」 9 굵기가 한 패밀리로 보이는지.
   QA 는 그 앱들이 쓰는 GDI/DirectWrite API 열거·렌더로 대리 검증만 했다. macOS 는 기기가 없어 미검증.

---

### 부록 — QA 스크립트 변경 이력
**2026-09-08(6차 재검)**
- `supplement.py`: hangul-pos 를 고정 ±15 → `|(J대상하단 − J ㄴ하단) − sy(1.965)×(N대상하단 − N ㄴ하단)| ≤ 6 unit`(U+3165–318E 보충 41자).
  N 은 `noto_bbox()` 가 Noto VF 를 서브셋 → `varLib.instancer` 인스턴스해 직접 측정(캐시 `%TEMP%/jennysans-qa-noto`). 빌더 `_noto_bottoms()` 와 독립.
  참조쌍(07 §8-3) 기대비도 하드코딩 → Noto 실측으로 교체.
- `names.py`: Mac(1/0/0) 기대 삭제 → `platformID 1 == 0` 검사(티켓 3). `metrics.py`: `prep` 존재를 PASS(티켓 4), WOFF2 `head.flags 0x0803` 정상 처리.
- `variable.py`: 합성·컴포지트 목록에 U+01C4 추가(티켓 7). 신규 `tickets.py`.

**2026-09-09(8차 재검)**
- `tickets.py`: 티켓 **9**(vhea/vmtx/VVAR/VORG 부재, TTF+WOFF2 20 파일)·**11**(고아 글립 0) 검사 추가. 도달성은 **QA 자체 구현**
  (cmap+UVS ∪ GSUB/GPOS/GDEF/MATH/BASE/JSTF 객체 트리 ∪ 컴포넌트 폐포 ∪ 예약 5종) — 빌더 `fontutil.reachable_glyphs()` 미사용.
  티켓 2 판정을 VF 포함 **중첩 0 FAIL 기준**으로 강화(6차의 VF INFO 처리 폐기).
- `web.py`: 크기 목표를 스펙 05 §4 개정판에 맞춤(CSS gzip ≤110 KB · VF 슬라이스 ≤95 KB · VF 라틴 ≤70 KB, 정적 ≤40/35 KB). 단위는 KB = 1,000 bytes 로 통일.
