# Changelog — JennySans

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 를 따르고, 버전은 폰트 관례 `X.YZZ`(name ID 5 / head.fontRevision)를 씁니다.
npm 은 SemVer 만 받으므로 `1.000 ↔ 1.0.0`, `1.001 ↔ 1.0.1`, `1.100 ↔ 1.1.0` 으로 대응합니다(`docs/DISTRIBUTION.md` §1).

## [Unreleased]

## [1.001] — 2026-10-24 (패치 · npm 1.0.1 · git tag `v1.0.1` · 회사 버전 표기 v1.0.1)

검사성적서·리포트 같은 업무 문서(PDF·엑셀)의 체크 칸을 위해 **체크박스 기호 3자**를 9 웨이트와 변수 폰트 전부에 넣었습니다.
기존 글립·메트릭은 바뀌지 않았습니다(회귀 비교: 기존 글립 외곽선·진행폭 변경 0, 수직 메트릭 동일).

### Added
- **☐ U+2610 BALLOT BOX · ☑ U+2611 BALLOT BOX WITH CHECK · ☒ U+2612 BALLOT BOX WITH X** — cmap 13,254 → **13,257**, 글립 13,980 → **13,983**.
  - 원본 Pretendard 1.3.9·Noto Sans KR 2.004·(예비) Source Han Sans KR 2.005 **어디에도 없어**(실측) 제니산스 자체 부품으로 **합성**했습니다 — 새 원본·새 라이선스 고지 없음.
  - 박스 = 같은 웨이트의 **□ U+25A1 외곽선 그대로**(크기·획 굵기·진행폭이 □ 와 같아 표 정렬이 맞습니다).
  - ☑ 은 같은 웨이트의 **✓ U+2713**, ☒ 은 **× U+00D7** 을 균등 축소(아핀 변환만)해 □ 속공간의 **시각 중앙**에 놓았습니다. 여백 = max(0.4 × 박스 획 두께, 72 unit).
  - 변수 폰트는 Pretendard VF 부품 인스턴스로 9 웨이트를 각각 만들어 피크 gvar 로 넣었습니다(점 수·윤곽 순서 동일 → 보간 안전).

### Changed
- 소개 문구를 **"범용 한글·영문(라틴) 고딕"** / **"Korean & English (Latin)"** 으로 바꿔 영문 지원이 바로 보이게 했습니다(README·홈페이지·package.json·배포 문서).
- 홈페이지 원본 대비 차이 표(diff-table) 정렬 수정 — 숫자 열 머리글 오른쪽 정렬·폭 고정·모바일 규칙(`site/assets/site.css`).
- 빌더 자체 점검에 `ballot` 검사 추가(정적 9 + VF wght 100/400/900: cmap·진행폭/bbox = □·마크가 속공간 중앙), 릴리스 간 회귀 비교 도구 `tools/regress_snapshot.py` 추가.

### 알려진 한계
- ✔ U+2714 · ✕ U+2715 · ✖ U+2716 · ✘ U+2718 은 여전히 미보유(`charset/recommended.txt` 대상, 원본에 없음).

## [1.100] — 예정 (한국어판 확장, npm 1.1.0, git tag v1.1.0)

1.000 공개 직후 착수합니다. 범위는 확정됐고(`AGENTS.md` §8 2026-09-08) 빌드는 시작 전입니다.

### 들어갈 것
- **한자 KS X 1001 4,620자**(U+4E00–9F9C 범위, cp949 디코딩 실측) — Noto Sans KR 2.004 VF 가 **4,619자 보유**, 기존 07 보충 규칙 그대로 이식. Pretendard 는 한자 0자라 전량 보충원본에서 온다.
- **베트남어 92자** — Latin Extended Additional U+1EA0–1EF9 + Ơơ Ưư(U+01A0/01A1/01AF/01B0).
- **카자흐·몽골 키릴 18자**.
- 베트남어·확장 키릴은 **Inter(= Pretendard 의 라틴 원본)에 전량 존재**하므로 디자인 정합이 완전하고, 웨이트당 약 **+35 KB** 에 그친다.

### 예상 크기 (팀장 실측 `build/hanja-measure.md`)
| 항목 | 1.000 | 1.100(근사) | 배수 |
|---|---|---|---|
| 정적 1웨이트 TTF | 2,617,580 B | 약 4,109,962 B (4.2 MB) | 1.6× |
| 정적 9웨이트 합 | 23,462,992 B (23.5 MB) | 약 36,989,658 B (37 MB) | 1.6× |
| 변수 TTF | 7,009,656 B | 약 9,491,012 B (9.5 MB) | 1.4× |
| **웹 분할본** | — | **영향 없음** | 1.0× |

웹은 `unicode-range` 분할이라 한자 슬라이스가 **페이지에 한자가 실제로 나올 때만** 내려갑니다.

### 들어가지 않는 것
- 일본어·중국어 — **별도 패밀리** `JennySans JP` / `SC` / `TC`(같은 한자 코드포인트의 지역별 표준 자형이 달라 한 파일에 넣으면 `locl`·언어 태그 없는 앱에서 틀린 자형이 나온다. Noto Sans CJK·Source Han Sans 동일 구조 — `AGENTS.md` §8 2026-09-08, 사용자 확정).
- 태국어·아랍어·히브리어·데바나가리 등 — 범위 밖(셰이핑 규칙이 다르고 원본 미보유).

## [1.000] — **2026-09-09 공개** (8차 빌드 확정본 · QA 판정 **RELEASE OK**(조건 없음 · 승인 예외 0) · git tag `v1.0.0`, npm 1.0.0)

**공개 URL**: https://font.jennysoft.co.kr — 홈페이지·글자맵·[다운로드](https://font.jennysoft.co.kr/#download) · CDN `https://font.jennysoft.co.kr/v/1.000/…`(버전 고정, 1년 immutable) · `https://font.jennysoft.co.kr/latest/…` · 체크섬 [`/download/SHA256SUMS.txt`](https://font.jennysoft.co.kr/download/SHA256SUMS.txt).
GitHub 저장소 공개와 npm 배포는 2026-10-24 대표 승인 — 1.001(`v1.0.1`)부터 공개합니다.

첫 릴리스. 빌드는 8차가 확정본입니다 — 6차에서 QA 티켓 1~6 을 처리했고, 7차는 티켓 5 재검토로 검사식만 정정했으며(재빌드 불필요), **8차에서 티켓 2·9·11 을 전체 재빌드로 마무리**했습니다.

### Added
- 정적 TTF 9 웨이트(Thin 100 – Black 900) `dist/static/JennySans-<Weight>.ttf`, 변수 TTF `dist/variable/JennySansVariable.ttf`(`wght` 100–900, 명명 인스턴스 9).
- 웹: WOFF2 전체본 9(647,572–764,252 B) + 변수 전체본(2,239,472 B), Google Fonts 한국어 124 슬라이스 정의 기반 `unicode-range` 분할본(웨이트당 **99 조각**, 정적 조각 2,264–31,340 B · 변수 조각 3,408–90,472 B, 라틴 조각 **#123**), CSS 4종(`jennysans.css` · `jennysans-variable.css` · `jennysans-dynamic-subset.css` · `jennysans-variable-dynamic-subset.css`).
  첫 화면 전송량 실측(`tools/first_paint.py`): 라틴 전용 페이지 31,144 B · 한국어 한 문장 85,420 B · 한 문단 105,312 B · 두 문단 2웨이트 158,320 B(전체본은 웨이트당 726,032 B).
  분할 CSS 자체 크기: `jennysans-dynamic-subset.css` 448,127 B(gzip 101,348 B, `@font-face` 891개) · `jennysans-variable-dynamic-subset.css` 69,422 B · `jennysans.css` 1,887 B · `jennysans-variable.css` 679 B.
- 문자집합 `charset/required.txt` 12,602 코드포인트(+ `recommended.txt` 898 · `korean-old.txt` 103 = 빌드 대상 13,603) — 현대 한글 11,172 전부 · 첫가끝 자모 256 · 호환 자모 94 · ASCII/Latin-1/Latin Ext-A 전부 · 결합 악센트 · KS X 1001 기호(행 1~3·6~9) · 전각 영숫자 등. 그리스 69 · 키릴 98(U+0400–045F 96 전부 + Ґґ)은 원본 보유분 유지.
- 패밀리명 JennySans / 제니산스(ko-KR name 레코드), PostScript `JennySans-<Weight>`, OS/2 벤더 `JNSF`, `fsType` 0(설치·임베드 제한 없음).
- 라이선스 패키지: `LICENSE`(OFL 1.1 + 누적 저작권 헤더, Reserved Font Names 'JennySans'·'제니산스'), `THIRD-PARTY-NOTICES.md`, `docs/OFL-FAQ-ko.md`.
- 문서: `README.md`, `docs/INSTALL.md`, `docs/DISTRIBUTION.md`, `docs/ADOPTION.md`, `docs/LEGAL-REGISTRATION.md`, `docs/SEO_REGISTRATION.md`; 소개 홈페이지 `site/`(타입 테스터·웨이트 견본·글자맵·문자 범위·지원 언어·다운로드·사용법), QA 격자 `site/test.html`; 배포 `deploy/`.
- 다운로드 패키지 `dist/packages/`: zip 4종 + `SHA256SUMS.txt` + `index.json`(홈페이지가 읽음).

### Added (원본 Noto Sans KR 2.004 에서 보충)
- Pretendard 에 없는 **909 글립**을 웨이트별 인스턴스(`wght` 100–900) 후 `docs/spec/07-supplement.md` §6 규칙으로 UPM 2048 에 맞춰 이식 — 한글·자모 1.982×1.965 고정(진행폭 1770), 괘선 affine 1.77×2.444, 기호는 Pretendard 참조 글립(① ○ △ ◇ → ※ ㎏ 등) 크기·폭에 맞춤.
  내역: 첫가끝 자모 전부(U+1100–11FF 256 + Ext-A 29 + Ext-B 72), 호환 자모 잔여 41(U+3165–318E), 괘선 U+2500–257F 128, 블록 요소 32, ◌ U+25CC, 괄호·원문자 U+3200–327F, 단위 U+3380–33DF 중 16, 화살표·수학·도형·KS 기호 일부.
- **합성 8자**: ￢￣￤(U+FFE2–FFE4, Pretendard 부품 컴포지트) · ⅔(U+2154, ⅓ 구조 재현) · ≒(U+2252, equal+period 분해) · ◈(U+25C8, ◇+◆) · ∼(U+223C, Noto ∽ 좌우 반전) · **DŽ(U+01C4, D+Zcaron 컴포지트 — 6차 추가)**.
- 변수 폰트에는 **9 인스턴스 피크 gvar**(중간 마스터)로 보충 909 글립 전부 삽입, 실패 0.

### Changed (원본 Pretendard 1.3.9 대비)
- 수직 메트릭을 전 웨이트 typo = hhea = win = **1950 / −494 / 0** + `USE_TYPO_METRICS` 로 통일(원본 OTF 의 typo/win ascender 1949 → 1950).
- name/STAT/fvar/OS/2 를 스펙(`docs/spec/02-naming.md`, `03-metrics.md`)대로 전면 재작성. 원본 RFN(Pretendard·Source·Inter·M PLUS 1)은 저작권(ID 0)·버전(ID 5 "based on …")·디자이너(ID 9) **고지 레코드에만** 남김 — 식별 레코드·fvar 인스턴스명·STAT 이름·글립명 전수 검사 PASS.
- 범위 밖 글립(가나 184자 등)을 서브셋에서 제외.
- 변수 폰트 `wght` 축을 원본 45–930 → **100–400–900** 으로 제한(`varLib.instancer` L4).

### Fixed (QA 1차 티켓 → 6차 빌드, `docs/qa/ISSUES.md`)
- **티켓 1** `case_mapping`: U+01C4 **DŽ** 누락 → `D` + `Zcaron` 컴포지트로 합성(진행폭 = 두 부품의 합).
- **티켓 2** `nested_components`: 컴포넌트가 다시 컴포지트를 참조하는 글립 113개 → 정적 9종 **한 단계 평탄화**(외곽선·bbox 불변 검증, 중첩 0). 변수 폰트는 167 중 155 채택·12 되돌림(잔여 5는 승인 예외).
- **티켓 3** `no_mac_entries`: platformID 1(Macintosh) name 레코드 **전부 제거**.
- **티켓 4** `smart_dropout`: `prep` = `PUSHW[] 511 SCANCTRL[] PUSHB[] 4 SCANTYPE[]` 추가(gftools `fix-nonhinting` 과 동일), `gasp` 0x000F 유지.
- **티켓 6** `transformed_components`(변수): 변환 컴포넌트 사용 글립 **94개를 외곽선으로 분해**(반전 글립은 윤곽 방향 복원) + gvar 델타 재생성.
- **티켓 5**(ㅥ U+3165 하단 편차)는 **결함이 아님(closed, not-a-defect)** — Noto Sans KR 자신이 ㅥ 을 ㄴ 보다 아래에 그리고(Regular −3 → Black −13), 우리 편차는 전부 `sy(1.965) × 원본 편차` 와 오차 ≤1.5 unit 으로 일치했다(= 이식이 정확하다는 증거). 글립을 옮기면 원본 디자인 변경이라 **옮기지 않고 검사식을 정정**했다(`build/ticket5-measure.md`, `AGENTS.md` §8 2026-09-07).

### Fixed (QA 2차 티켓 → 8차 빌드, 2026-09-09)
- **티켓 2 마무리** `nested_components`(변수): 6차에 남아 있던 잔여 5글립의 원인은 평탄화 채택 기준(정적 대비 ≤2 unit)이 **Noto 유래 보충 글립용 허용치를 Pretendard 유래 컴포지트에도 적용**한 것이었다. 스펙 07 §7(c) 대로 기준을 분리(Noto 유래 ≤2 unit / 합성·컴포지트 ≤8 unit)해 **중첩 167건 전량 평탄화 → 잔존 0**. 외곽선은 손대지 않았고(평탄화는 `outer∘inner` 변환 합성), 9 인스턴스 bbox 로 증명했다(정적 대비 최대 4.804 unit, 평탄화 전후 최대 0.406 unit).
- **티켓 9** `vhea`/`vmtx` 웨이트 간 비대칭: 원본 Pretendard 의 Thin·ExtraLight·Light 에만 있던 세로 메트릭 테이블이 그대로 실려 왔었다. JennySans 는 세로쓰기를 지원하지 않으므로 **`vhea`·`vmtx`·`VVAR`·`VORG` 를 10개 파일 전부에서 제거**(Thin·ExtraLight·Light 각 −54 KB).
- **티켓 11** `unreachable_glyphs`: 어디서도 참조되지 않는 고아 글립을 정적 9종 각 4개(`casedieresis.cn` `casetilde.cn` `tonos` `uniE118`)·변수 6개(+`uni0189` `cyrillictic.cn`) 제거. 도달 가능 집합을 cmap(UVS 포함) ∪ GSUB/GPOS/GDEF/MATH/BASE/JSTF 참조 ∪ 컴포넌트 폐포 ∪ 예약 글립으로 **fontbakery 보다 보수적으로** 계산했다. `.null` 은 서브세터 권장 글립이라 유지. **셰이핑 스모크 결과 `.notdef` 는 U+0149 ŉ 하나뿐**(required 제외 결정 문자)이라 렌더 영향 0.

### 실측치 (8차 빌드 확정본, `build/BUILD-REPORT.md` 2026-09-09)
- 정적 TTF 9종: 글립 **13,980** · cmap **13,254** · required 12,602/12,602 누락 0 · **2,553,816–2,700,344 bytes**(Regular 2,617,580, 9종 합 23,462,992).
- 변수 TTF: 글립 **13,980** · cmap 13,254 · **7,009,656 bytes** · SHA-256 `648b9c08d7095f2102ecf54c4a514b46e39d968f3b47cdf52147fd2a882667ca`.
- 웹 분할 합계: 정적 웨이트당 1,179,952–1,233,500 bytes(99 조각), 변수 3,401,592 bytes.
- 다운로드 zip(릴리스본, `dist/packages/index.json` 2026-09-09 10:27): desktop 10,061,879 B(`6b8d52bd…`) · web 23,408,367 B(`5ca42626…`) · variable 5,432,526 B(`e05769a8…`) · all 36,679,359 B(`f1b1243e…`). **정본은 서버의 [`/download/SHA256SUMS.txt`](https://font.jennysoft.co.kr/download/SHA256SUMS.txt)** — `all.zip` 은 문서를 담아 문서를 고치면 값이 달라진다.
- 빌더 자체 점검 **PASS**(WARN 0, 항목 112 — `build/verify-report.md`). fontbakery `check-universal` 은 정적·변수 **패밀리별로 나눠 실행하면 FAIL 0**(한 실행에 섞으면 패밀리 단위 검사 4건이 FAIL — 정적 `JennySans` 와 변수 `JennySans Variable` 이 별도 패밀리·별도 디렉터리이기 때문). WARN 63건 / 9개 검사 ID, 새 WARN 종류 0.

### Known limitations
- **한자·가나·중국어·베트남어 없음**(한자·베트남어는 1.100, 일본어·중국어는 별도 패밀리 예정). 옛한글 조합 피처 없음(자모 단독 글립만). 이탤릭 없음. **세로쓰기 미지원**(`vhea`/`vmtx` 없음). OTF(CFF) 미제공(1.1 이후 검토).
- 그리스는 단독 악센트 기호 ΄(U+0384) ΅(U+0385) · 아노텔레이아 ·(U+0387) · 고대 KAI ϗ(U+03CF) 미보유(악센트 결합형 글자는 전부 있어 현대 그리스어 본문 표기는 가능).
- Windows GDI 계열 앱(구형 한글 등)에서는 Regular/Bold 외 웨이트가 "JennySans Light" 처럼 별도 패밀리로 보임(`docs/INSTALL.md` §3).
- `jennysans-dynamic-subset.css` 는 `@font-face` 891개(9 웨이트 × 99 조각)라 CSS 파일 자체가 448,127 B(gzip 101,348 B)입니다. 9 웨이트가 다 필요하지 않으면 변수 폰트 CSS 를 쓰거나 필요한 웨이트 블록만 남기세요(`README.md` §5-1).
- fontbakery·전수 커버리지·셰이핑·렌더·설치·브라우저 실측 결과와 **최종 판정은 `docs/qa/QA-REPORT-1.000.md`** 에 기록되며, **QA RELEASE OK 전에는 릴리스하지 않습니다.**

[Unreleased]: https://github.com/gjh999/jennysans/compare/v1.0.0...HEAD
[1.100]: https://github.com/gjh999/jennysans/releases/tag/v1.1.0
[1.000]: https://github.com/gjh999/jennysans/releases/tag/v1.0.0
[홈페이지]: https://font.jennysoft.co.kr
