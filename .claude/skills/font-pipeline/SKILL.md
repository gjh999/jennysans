---
name: font-pipeline
description: JennySans 폰트 빌드·검증 절차의 단일 원본. 원본 다운로드→검증→서브셋/보충 병합→이름변경→정적/변수/WOFF2/분할→CSS→자체점검까지의 실제 명령. 빌드나 QA 를 실행하기 전에 반드시 읽는다.
---

# font-pipeline — 빌드·검증 절차 (v0.3, 2026-09-09 8차 빌드 실제 명령 기준)

> **v0.3 에서 바뀐 것(8차 = QA 티켓 2·9·11)**
> 1. **VF 평탄화 채택 판정 = spec 07 §7(c)** — 글립 성격에 따라 허용치가 다르다.
>    Noto 유래 보충 글립 ≤`config.FLATTEN_TOL_NOTO`(2 unit) / 합성·컴포지트 평탄화 ≤`config.FLATTEN_TOL_COMPOSITE`(8 unit).
>    6차까지 전부 2 unit 으로 재서 12 글립을 되돌렸고 VF 에 `nested_components` FAIL 이 남았다 → 8차에서 **전량 평탄화, VF 중첩 0**.
> 2. **`vhea`/`vmtx`(+`VVAR`/`VORG`)를 전 파일에서 제거**(`fontutil.DROP_TABLES_EXTRA`) — 세로쓰기 미지원(spec 03), 3 웨이트에만 있던 비대칭 해소.
> 3. **고아 글립 제거**(`fontutil.prune_unreachable`) — 평탄화·분해로 참조가 사라진 글립을 정적·VF 모두에서 제거.
> 4. `verify_build` 새 검사 3종: `vertical`(세로 테이블 없음) · `orphans`(고아 0) · `flatten`(평탄화 글립 VF↔정적 편차 ≤ 07 §7(c)).
>    그리고 **중첩 컴포지트 0 은 이제 VF 에도 FAIL 기준**(승인 예외 없음 — AGENTS §8 2026-09-09).

## 환경
- Python 3.12 (`python`), fontTools 4.64, brotli, uharfbuzz, fontbakery 1.1, Pillow 12, playwright(python).
- 실행은 항상 프로젝트 루트 `<repo>` 에서 `PYTHONUTF8=1 python tools/<script>.py`.
- FontForge 없음. 글립 외곽선은 건드리지 않는다(스케일·이식·서브셋·메타데이터만).

## 디렉터리
- `sources/<이름>/` 원본(비커밋) · `sources/MANIFEST.md` 출처·버전·SHA-256
  - 기반 `sources/Pretendard/alternative-ttf/Pretendard-<W>.ttf`(glyf 9종) · `sources/Pretendard/PretendardVariable.ttf`
  - 보충 `sources/NotoSansKR/NotoSansKR[wght].ttf`
- `charset/*.txt` 문자집합(`U+XXXX` / `U+XXXX-U+YYYY  # 설명`) — 파서 `tools/charset.py`(QA 도 임포트)
- `tools/` 파이프라인 · `tools/config.py` 상수(웨이트·메트릭·도메인·RFN 패턴·규칙 보정·**평탄화 허용치 `FLATTEN_TOL_NOTO`/`FLATTEN_TOL_COMPOSITE`**) ·
  `tools/config/supplement.json`(07 §6 규칙표) ·
  `tools/naming.py` name 문자열 · `tools/supplement.py` 보충 엔진 · `tools/data/korean-slices.google.json` 슬라이스 정의
- `build/` 중간물: `cache/`(Noto 서브셋 VF·웨이트별 인스턴스, Pretendard VF 부품 인스턴스 — 코드포인트 해시로 무효화) · `logs/<step>-<시각>.log` ·
  `static-summary.json` · `variable-summary.json` · `web-summary.json` · `verify-report.md` · `BUILD-REPORT.md` ·
  `preview/JennySans-Regular.png` · `supplement-sheet-<W>.png` · `supplement-refs-<W>.json` · `supplement-measure.md` · `ticket5-measure.md`
- `dist/{static,variable,web,web/subset,css}` 릴리스 산출

## 명령
```
PYTHONUTF8=1 python tools/build.py fetch      # MANIFEST 기준 다운로드·SHA 검증. zip → alternative TTF 9종 추출 (--tmp DIR, --force)
PYTHONUTF8=1 python tools/build.py static     # 정적 9 웨이트 → dist/static/JennySans-<W>.ttf  (--weights Regular,Bold 로 일부만)
PYTHONUTF8=1 python tools/build.py variable   # 변수 → dist/variable/JennySansVariable.ttf     (--stage 9|2|0)
PYTHONUTF8=1 python tools/build.py web        # WOFF2 전체 + Google 124 슬라이스(+rest) 분할 + CSS 4종 (--jobs N, --no-subset)
PYTHONUTF8=1 python tools/build.py verify     # 자체 점검 → build/verify-report.md (FAIL 있으면 rc=1)
PYTHONUTF8=1 python tools/build.py report     # build/BUILD-REPORT.md
PYTHONUTF8=1 python tools/build.py preview    # build/preview/JennySans-Regular.png (Pillow)
PYTHONUTF8=1 python tools/build.py sheets     # build/supplement-sheet-<W>.png (보충 글립 전수 시트, 07 §8-8)
PYTHONUTF8=1 python tools/build.py measure    # build/supplement-measure.md (Pretendard vs Noto bbox 실측, 07 스펙 근거)
PYTHONUTF8=1 python tools/build.py all        # static → variable → web → verify → report → preview → sheets (약 9분)
```
- 재현 빌드: `SOURCE_DATE_EPOCH` 를 주면 head.created/modified 고정(fontTools 지원).
- 개별 스크립트 직접 실행도 가능: `tools/build_static.py`, `build_variable.py`, `build_web.py`, `verify_build.py`.

## 단계별 내용 (무엇을 어떻게)
1. **정적**(`build_static.py`): `Pretendard-<W>.ttf` 로드 → 보충 계획(`supplement.supplement_targets`: 빌드 대상 − Pretendard cmap,
   Noto 보유 + 합성/미러 정의) → Noto VF 를 필요한 코드포인트(+참조쌍 글립)로 서브셋(캐시) → `varLib.instancer` 로 해당 wght 인스턴스(캐시)
   → **07-supplement 규칙표**(`tools/config/supplement.json` + `config.SUPPLEMENT_RULE_PATCHES`)를 `supplement.Engine` 이 적용:
   `fixed`(한글류 1.982×1.965, adv 1770 중앙) · `ref`(같은 웨이트의 Pretendard 참조 글립 높이비로 균등 스케일, adv=ref|fit) ·
   `ref-baseline` · `affine`(괘선 1.770×2.444 셀) · `empty` · 합성(￢￣￤ 컴포지트, ⅔ ⅓-구조 컴포지트, ≒ ◈ 분해) · 미러(∼ ← ∽ + ReverseContourPen)
   → 글립명 `uniXXXX` 로 추가 → `fontTools.subset`(빌드 대상 = required ∪ recommended ∪ korean-old, `layout_features='*'`,
   `notdef_outline`, `glyph_names`, `name_IDs='*'`, recalc-*, meta 통과) → **중첩 컴포지트 평탄화**(`supplement.flatten_nested`, outer∘inner
   변환 합성, bbox 불변 검증 — QA 티켓 2) → **고아 글립 제거**(`fontutil.prune_unreachable` — 평탄화로 참조가 사라진 글립, QA 티켓 11)
   → name 전면 교체(`naming.py`, Windows 레코드만 — Mac 레코드 없음(티켓 3), GSUB FeatureParams UI 이름 보존·재매핑)
   → OS/2·head·hhea·post·prep(스마트 드롭아웃, 티켓 4)·gasp·meta·STAT(`fontutil.fix_tables/build_stat`) → 저장 → 다시 열어 실측.
   서브셋·`fix_tables` 는 `fontutil.DROP_TABLES_EXTRA` 로 `vhea`/`vmtx`/`VVAR`/`VORG` 도 떨군다(세로쓰기 미지원, QA 티켓 9 — 원본
   Pretendard-Thin/ExtraLight/Light 만 갖고 있어 3 웨이트에만 실려 있었다).
   참조값은 `build/supplement-refs-<W>.json`. QA 티켓 1(DŽ U+01C4 = D+Zcaron 합성)은 `config.SUPPLEMENT_COMPOSITE_PATCHES`.
   `config.SUPPLEMENT_RULE_PATCHES_FIRST`(규칙표 앞에 끼우는 우선 보정)는 **비어 있다** — 6차에 넣었던 옛 호환자모 기저선 재정렬은
   7차에서 되돌렸다(티켓 5 = 결함 아님, `build/ticket5-measure.md`). **보충 글립을 원본과 다른 위치로 옮기는 규칙은 넣지 않는다.**
2. **변수**(`build_variable.py`): `PretendardVariable.ttf` → 서브셋 → wght 축 45–930 → 100/400/900 제한(instancer L4)
   → 같은 규칙표로 9 웨이트 외곽선을 만들되 P(참조·부품)는 **Pretendard VF 부품 인스턴스**(캐시)에서, N 은 Noto 인스턴스에서 →
   400 기본 외곽선 + **9 인스턴스 피크 gvar**(각 웨이트 정규화 좌표에 피크, 이웃 웨이트를 start/end 로 하는 tent, 팬텀 4점 포함 델타,
   컴포지트는 컴포넌트 오프셋 델타, IUP 최적화, 델타 0 텐트 생략) → 실패 시 2마스터(100/900) → 최후 rename-only
   → **VF 중첩 컴포지트 평탄화**(`build_variable.flatten_variable`: mini VF 9 인스턴스에서 전개한 오프셋으로 gvar 재생성.
   채택 판정은 **spec 07 §7(c)** — 9 인스턴스 bbox·adv 가 정적과 Noto 유래 보충 글립 ≤2 unit / **컴포지트 ≤8 unit** 이면 채택.
   평탄화 대상은 전부 Pretendard 유래 컴포지트라 8 unit 이 맞는 기준이다: 부품 원천이 VF 보간 vs 정적 TTF 라 반올림 2~3 unit 이 필연.
   8차부터 되돌림 0·**VF 중첩 0**) → **변환 컴포넌트 분해**(`decompose_transformed`, 티켓 6)
   → **고아 글립 제거**(`fontutil.prune_unreachable`, 티켓 11 — VF 는 분해 부작용으로 정적보다 2개 더 나온다) → name/fvar/STAT 교체 → 정리 → 저장.
   달성 단계는 `build/variable-summary.json` 의 `stage`·`flatten_detail`·`flatten_adopted`·`flatten_reverted`·`nested_left`·`pruned` 와 BUILD-REPORT 에 기록.
3. **웹**(`build_web.py`): 정적 9 + 변수 → WOFF2 전체본. `docs/research/google-kr-slices.css` 의 124 `unicode-range` 를 파싱
   (`tools/data/korean-slices.google.json` 저장, 겹침은 뒤 블록에 남김, 어느 블록에도 없는 cmap 은 `rest` #124) → 폰트별 병렬 서브셋
   → `dist/web/subset/<stem>.subset.<n>.woff2`(빈 슬라이스 생략) → CSS: `jennysans.css`(정적 9) · `jennysans-variable.css` ·
   `jennysans-dynamic-subset.css` · `jennysans-variable-dynamic-subset.css`(선택), `font-display: swap`, 상대경로 `../web/…`.
4. **자체 점검**(`verify_build.py`): required 커버리지(존재·비-notdef·외곽선, 공백류 제외) · RFN 잔존(식별 레코드·fvar·STAT·글립명) +
   고지 레코드 유지 · name(ID 11 도메인·ID 0 첫 줄 정본·ID 5) · 메트릭 동일성(UPM·typo=hhea=win·USE_TYPO·WWS·underline·한글 1770) ·
   PS 이름 유일 · 테이블(Mac 레코드 0·prep 프로그램·**중첩 컴포지트 0 — 8차부터 VF 포함 FAIL 기준**·DŽ 구조) ·
   **`vertical`(vhea/vmtx/VVAR/VORG 없음, 전 파일 — 티켓 9)** · **`orphans`(도달 불가 글립 0, 전 파일 — 티켓 11)** ·
   피처 태그(허용 소실 정적 {ss16} / VF {ss16, rlig})·빈 피처 ·
   07 §8(한글류 adv·**hangul-pos**·참조 관계·괘선 셀·합성 4자 구조·미러 방향·Noto 피처 미유입) ·
   변수(fvar 9·STAT 9·gvar 튜플 점 수·보충 글립 9 웨이트 인스턴스 = 정적 ≤2 unit, 합성은 bbox/adv ±8) ·
   **`flatten`(VF 평탄화 컴포지트 9 웨이트 인스턴스 bbox·adv = 정적, 허용 07 §7(c) Noto 2 / 컴포지트 8 — 티켓 2)** ·
   WOFF2 열림·슬라이스 정합(cmap⊆range, 겹침 0, 합집합 = 전체본, 라틴 슬라이스에 U+0020/00A0).
   - **도달 판정(`fontutil.reachable_glyphs`)**: cmap(UVS 포함) ∪ GSUB/GPOS/GDEF/MATH/BASE/JSTF 객체 트리에 이름이 한 번이라도 등장 ∪
     컴포넌트 폐포 ∪ 예약 글립(`.notdef` `.null` `nonmarkingreturn` `CR`). fontbakery 는 룩업의 *출력*만 도달로 보므로 우리 쪽이 **더 보수적**이다
     (여기서 0 이면 fontbakery `unreachable_glyphs` 도 0). 글립을 지우기 전에 반드시 이 함수로 재확인한다 — 잘못 지우면 렌더 결함.
   - **hangul-pos(7차 정정)**: 옛 호환자모 U+3165–U+318E 보충 41자가 **원본의 기저선 차이를 재현**했는지 본다 —
     `|(J대상하단 − J ㄴ하단) − sy × (N대상하단 − N ㄴ하단)| ≤ HANGUL_POS_TOL(6 unit)`.
     N 값은 `verify_build._noto_bottoms` 가 Noto VF 를 웨이트별로 인스턴스(build/cache 재사용)해 **직접 측정**한다.
     6차까지 쓰던 "ㄴ 하단 ±15 고정"은 틀린 전제였다: Noto 자신이 ㅥ 을 ㄴ 보다 아래에 그리고(Regular −3 → Black −13)
     그걸 옮기면 원본 디자인 변경(AGENTS §1-1·§5 위반)이다. 근거 `build/ticket5-measure.md`, QA 티켓 5 = not-a-defect.
5. **시트/미리보기**: `preview.py`(한글·es·en·숫자·보충 샘플 + 9 웨이트) · `supplement_sheet.py`(웨이트별 보충 글립 전수, 참조 글립 나란히).

## 설정 바꿀 때
- 보충 규칙: `tools/config/supplement.json`(= spec 07 §6, 그대로 복사) + `tools/config.py` `SUPPLEMENT_RULE_PATCHES`(스펙이 덮지 않는
  코드포인트 보정). 규칙 순서 = 우선순위. 바꾼 뒤 `build.py all`.
- 이름·저작권·상표·디자이너 문구: `tools/naming.py`(spec 02). 메트릭·웨이트·도메인(`VENDOR_URL`)·RFN 패턴·코드페이지 허용치: `tools/config.py`, `fontutil.py`.
- charset 이 바뀌면 캐시 키(코드포인트 해시)가 바뀌어 Noto/Pretendard 부품 인스턴스가 자동 재생성된다.
- **검사식만 고쳤을 때는 `verify` + `report` 만 재실행**하면 된다(7차 사례). 단 규칙표·config 를 손댔다면
  "산출물이 정말 안 바뀌는지" 먼저 증명하고(같은 규칙으로 대상 글립을 다시 만들어 `dist/` 의 bbox·adv 와 비교) 그 결과를 리포트에 남긴다.
  `dist/` 를 다시 만들면 파일 SHA·크기가 바뀌므로 font-site 가 `tools/package.py --render-site` 를 다시 돌려야 한다.

## QA (독립 검사 — font-qa 소유, 아래는 빌더 자체 점검이 아님)
```
python docs/qa/scripts/coverage.py
python docs/qa/scripts/shaping.py
python -m fontbakery check-universal dist/static/*.ttf dist/variable/*.ttf --html docs/qa/fontbakery.html
python docs/qa/scripts/render.py        # PIL 렌더 이미지
python docs/qa/scripts/browser.py       # Playwright 스크린샷
powershell -File docs/qa/scripts/win-install-test.ps1
```
