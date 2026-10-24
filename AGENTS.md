# JennySans 「제니산스」 — 제니소프트 범용 다국어 고딕 폰트 프로젝트 (단일 원본 룰)

> 어느 세션(Claude Code·Codex)이 열어도 이 문서가 컨텍스트의 원본이다.
> 진행 상황은 `docs/PROGRESS.md`, 로드맵은 `docs/ROADMAP.md`, 조사 근거는 `docs/research/`,
> 설계 스펙은 `docs/spec/`, QA 결과는 `docs/qa/`, 결정 변경은 이 문서 §8 에 기록한다.

## 1. 무엇을 만드나 (2026-09-05 사용자 지시 요약)

**제니소프트의 모든 솔루션(웹앱·게임·데스크톱·문서)과 웹에서 공통으로 쓸 범용 고딕(산세리프) 폰트 패밀리.**

- **문자 범위**: 한글(현대 한글 **11,172자 전부** + 자모·호환자모) + 영어 + **스페인어**(ñ, ¿¡, 악센트 모음, ü, ª º, €)
  + 서유럽·중앙유럽 라틴(Latin-1 Supplement·Latin Extended-A 전부) + 한국 문서용 기호(KS X 1001 기호·원문자·괄호문자·단위)
  + 일반 구두점·화폐·화살표·기본 수학·도형 + 그리스·키릴 기본(원본에 있으면 유지).
  **유니코드 기준으로 범위를 정의**하고(`charset/*.txt`), 빠지는 조합이 없도록 QA 가 전수 검사한다.
- **스타일**: 화려하거나 특이하지 않은 **가독성 좋은 본문용 고딕**. 범용이므로 개성보다 중립성·판독성 우선.
- **쓰임새**: ① 웹(WOFF2 + `unicode-range` 분할, CSS) ② 데스크톱 문서(한글·MS Office·Photoshop·Illustrator 설치용 OTF/TTF)
  ③ 게임·앱(Unity·Godot·Flutter·Flame 용 TTF, 변수 폰트) ④ 인쇄.
- **저작권 무결**: 처음부터 끝까지 **SIL OFL 1.1** 로만 구성한다. 원본 폰트의 Reserved Font Name 을 침해하지 않는
  새 이름(JennySans)으로 배포하고, 원저작권 고지를 name 테이블·LICENSE·README 에 유지한다. 상업적 사용·수정·재배포·번들 전부 허용되는 형태로 낸다.
- **QA 는 품질을 책임진다**: fontbakery + 전수 커버리지(11,172자 + 라틴 + 기호) + HarfBuzz 셰이핑 + 실제 렌더 이미지 + Windows 설치 실측 + 브라우저 스크린샷.
- **배포 계획까지**: GitHub 릴리스·npm·CDN(jsDelivr + 자체 `font.jennysoft.co.kr`)·설치 가이드(Windows/macOS/한글/Photoshop/웹/Flutter/Unity)·버전 정책.

### 1-1. 현실적 제작 방식 (팀장 결정 — 반드시 이해하고 작업할 것)

현대 한글 11,172자를 글립 단위로 **새로 그리는 것은 이 프로젝트 범위 밖**이다(전문 디자이너 수 년 작업).
따라서 JennySans 는 **OFL 원본 폰트를 조합·선별·재구성·최적화한 파생(derivative) 폰트**로 만든다.
OFL 은 이를 명시적으로 허용한다(파생물 제작·재배포·상업 이용 가능, 단 RFN 사용 금지 + OFL 유지).

우리가 더하는 가치는 다음이다.
1. **벤치마킹으로 최적 원본 선정**(한글·라틴 각각) — `docs/research/`
2. **문자 집합을 유니코드 기준으로 명시적으로 정의**하고 빠짐없이 채움(원본에 없는 문자는 다른 OFL 원본에서 보충)
3. **한 이름·한 패밀리·일관된 메타데이터**(name/OS/2/STAT/fvar) — 한글·Photoshop·Windows·macOS·브라우저에서 같은 패밀리로 묶임
4. **웹 최적화**(WOFF2, 한글 빈도 기반 unicode-range 분할, 변수 폰트) 와 **게임/앱 최적화**(TTF, 필요 시 경량 서브셋)
5. **전수 QA** 와 **설치·배포·문서**까지 완성된 패키지

## 2. 실행환경 (2026-09-05 실측)

| 도구 | 위치 | 비고 |
|---|---|---|
| Python 3.12.10 | PATH `python` | `PYTHONUTF8=1 python …` 로 실행(cp949 깨짐 방지) |
| fontTools 4.64 · brotli · Pillow 12 | 설치됨 | 병합·서브셋·이름변경·WOFF2·렌더 |
| uharfbuzz 0.56 · fontbakery 1.1 | 2026-09-05 설치 | 셰이핑 검사·품질 검사 |
| playwright(python) | 설치됨 | 브라우저 스크린샷(웹 검증) |
| git 2.55 | `C:\Program Files\Git` | 로컬 커밋 가능. **푸시(외부 전파)는 사용자 승인 후** |
| FontForge · Glyphs | **없음** | 글립 편집은 fontTools 로만(필요 시 `fontTools.pens`) |
| 서버 | `ssh debc-dev` (<server>:<ssh-port>) — nginx · Python 3.12 | **`font.jennysoft.co.kr`**(DNS A 등록 완료 2026-09-06, 사용자) → `/var/www/font` 정적 서빙. 인증서 acme.sh `--alpn --server letsencrypt`(qaudio 패턴) |
| 인터넷 | 가능 | GitHub 릴리스·Google Fonts 에서 원본 다운로드 |

원본 폰트 파일은 `sources/<폰트>/` 에 **버전·출처 URL·SHA-256** 과 함께 둔다(`sources/MANIFEST.md`).
`sources/`·`build/` 는 git 에 넣지 않는다(`.gitignore`). `dist/` 는 릴리스 산출물이며 태그 시점에만 커밋한다.

## 3. 팀 운영 (사용자 지시: 팀장이 기획·설계·로드맵, 팀원 스폰·스킬 장착, 완료까지 자율 진행)

- **세션 = 팀장.** 로드맵(`docs/ROADMAP.md`)을 세우고 결정을 내리며 Agent 툴로 팀원을 스폰한다.
- **팀원 정의**는 `.claude/agents/font-*.md` — 스폰 프롬프트에 **"AGENTS.md 와 `_COMMON.md`, 자기 역할 파일을 먼저 읽어라"** 를 명시한다.

| 팀원 | 역할 | 산출 |
|---|---|---|
| `font-researcher` | OFL 한글·라틴 폰트 벤치마킹, 라이선스(RFN) 실측, 커버리지·메트릭 실측 | `docs/research/` |
| `font-architect` | 문자집합(유니코드)·패밀리 구조·이름·메트릭·OpenType 기능·라이선스 스펙 | `docs/spec/`, `charset/` |
| `font-builder` | 빌드 파이프라인(다운로드→검증→병합/서브셋→이름변경→정적/변수/WOFF2/분할→CSS) | `tools/`, `build/`, `dist/` |
| `font-qa` | fontbakery·커버리지 전수·셰이핑·렌더 이미지·Windows 설치·브라우저 스크린샷, 결함 티켓 | `docs/qa/` |
| `font-release` | LICENSE/README/THIRD-PARTY·설치 가이드·npm/CDN·서버(nginx·인증서)·배포 스크립트·버전 정책 | `README.md`, `deploy/`, `docs/DISTRIBUTION.md`, `docs/INSTALL.md` |
| `font-site` | **폰트 소개 홈페이지**(`font.jennysoft.co.kr`) 설계·구현 — 소개·타입 테스터·사용법·**다운로드 패키지(zip)**·라이선스 안내 | `site/`, `tools/package.py`, `dist/packages/` |

- 팀원 산출물은 반드시 **파일로** 남긴다. 결정은 팀장이 내리고 §8 에 기록.
- **반복 검증 규칙**: 빌드가 나올 때마다 `font-qa` 를 투입한다. 결함은 `docs/qa/ISSUES.md` 에 번호를 붙여 기록하고
  `font-builder`/`font-architect` 에게 되돌린다. **QA 통과 없이는 릴리스하지 않는다.**
- 스킬 `.claude/skills/font-pipeline/SKILL.md` 가 빌드·검증 명령의 단일 원본이다. 빌더가 갱신한다.

### 3-1. 소유 구역

| 구역 | 소유 |
|---|---|
| `AGENTS.md` §8 결정, `docs/ROADMAP.md` | 팀장 |
| `docs/research/` | researcher |
| `docs/spec/`, `charset/` | architect |
| `tools/`, `build/`, `dist/`, `.claude/skills/font-pipeline/` | builder |
| `docs/qa/` | qa |
| `README.md`, `LICENSE*`, `THIRD-PARTY*`, `deploy/`, `docs/DISTRIBUTION.md`, `docs/INSTALL*.md` | release |
| `site/`(test.html 은 QA 공용), `tools/package.py`, `dist/packages/` | font-site |
| `docs/PROGRESS.md` | 각자 자기 항목만 |

## 4. 품질 기준 (릴리스 게이트)

1. **커버리지**: `charset/required.txt` 의 모든 코드포인트가 모든 웨이트에서 cmap 에 존재하고 `.notdef` 가 아니다. 한글 11,172자 전수.
2. **셰이핑**: HarfBuzz 로 11,172자 + 라틴·스페인어 샘플 문장을 셰이핑했을 때 `.notdef`(gid 0) 0건. 스페인어 `¿¡ñáéíóúü` 컴포즈/프리컴포즈 모두 정상.
3. **fontbakery**: `universal` 프로파일 **FAIL 0** (WARN 은 사유를 `docs/qa/` 에 기록). name/OS/2/head/hhea/post/STAT/fvar 정합.
4. **패밀리 묶임**: Windows(GDI/DirectWrite)·macOS·브라우저·한글·Photoshop 에서 9 웨이트가 **한 패밀리**로 묶이고 웨이트 선택이 된다. (RIBBI 규칙: Regular/Bold 만 style-linking, 나머지는 typographic family 로)
5. **메트릭**: 모든 웨이트가 같은 UPM·ascender/descender/lineGap(hhea = OS/2 typo, `USE_TYPO_METRICS` 세트) → 웨이트 바꿔도 줄 높이 불변. 한글·라틴 베이스라인·크기 조화(원본 기준 유지).
6. **파일 크기**: 정적 TTF 웨이트당 원본 대비 증가 없음, 웹은 `unicode-range` 분할로 첫 화면 로드 ≤ 수십 KB 수준(측정치 기록).
7. **렌더 실측**: Windows GDI/DirectWrite 렌더 이미지, Chromium 스크린샷(9 웨이트·변수·분할 CSS), 한글·스페인어·영어·숫자·기호 샘플. 팀장이 눈으로 본다.
8. **라이선스**: LICENSE(OFL 1.1 + RFN 'JennySans'·'제니산스'), 원본 저작권 고지 전부 포함, name ID 0/7/9/13/14 정확. 원본 RFN(`Pretendard`·`Source`·`Inter`·`M PLUS`·`Noto`)이 **식별 레코드**(name ID 1/2/3/4/6/16/17/18/21/22/25, fvar 인스턴스명, STAT 이름, CFF FontName, 글립명, 파일명)에 없음. ID 0/7/9/13 **고지 레코드에는 원저작자·원본 이름 표기를 유지**(OFL 조건 2 의무·Pretendard 선례).

## 5. 라이선스·법무 무결 원칙

1. **OFL 1.1 원본만** 쓴다. Apache-2.0 폰트는 혼합 시 OFL 로 재배포 불가할 수 있어 원칙적으로 제외(필요하면 팀장 승인·법적 검토 기록).
   "무료지만 수정 금지" 폰트(예: Gmarket Sans·배민 계열 일부·상업 폰트의 무료판)는 **절대 제외**.
2. 원본의 **Reserved Font Name** 을 어떤 형태로도 우리 이름에 쓰지 않는다(`Pretendard`, `Noto`, `Source Han`, `Nanum`, `Plex`, `Spoqa` 등). name 테이블 전 레코드 검색으로 확인.
3. 파생물도 OFL 1.1 로 배포하고 **RFN "JennySans"** 를 선언한다. 원본 저작권 문구는 모두 누적 표기(OFL 요구).
4. 폰트 **자체를 단독 판매하지 않는다**(OFL 금지). 소프트웨어·문서·게임에 번들·임베드는 자유.
5. 상표: "JennySans" 는 제니소프트 표기. 유사 상표 검색은 배포 단계에서 기록.

### 5-1. 원본·의존성 대장 (여기 없는 것을 넣지 말 것 — 팀원은 추가 시 이 표를 갱신)

| 항목 | 출처 | 라이선스 | RFN | 용도 | 상태 |
|---|---|---|---|---|---|
| **Pretendard 1.3.9** (정적 OTF/TTF 9종 + PretendardVariable.ttf) | https://github.com/orioncactus/pretendard (릴리스 zip) | OFL 1.1 | 'Pretendard' + 누적 'Source'·'Inter'·'M PLUS 1' (저장소 main LICENSE 기준) | **주원본** — 한글 11,172·라틴·그리스·키릴·기호·OpenType 기능·변수 | 채택 2026-09-06 |
| **Noto Sans KR 2.004 변수 TTF** `NotoSansKR[wght].ttf` | Google Fonts (google/fonts ofl/notosanskr) | OFL 1.1 | 'Source' (Adobe) | **보충원본** — Pretendard 결손 글립(첫가끝 자모 U+1100–11FF·옛 호환자모·자모확장 A/B·KS 기호 일부)을 웨이트별 인스턴스 후 스케일 이식 | 채택 2026-09-06 |
| (예비) Source Han Sans KR 2.005 OTF · Gothic A1 · Source Sans 3 · Noto Sans | `sources/MANIFEST.md` | OFL 1.1 | 'Source' / 없음 / 'Source' / 'Noto' | 대안·비교용. 산출물에 미포함 | 보관만 |
| ⛔ 사용 금지 | IBM Plex Sans KR(라틴 결손)·Spoqa(크기)·나눔 계열(OFL 원문 미확인·fsType)·SUIT(빈 글립 8,504)·Freesentation(Apache 라틴)·Wanted Sans(웨이트) | — | — | `docs/research/01-benchmark.md` 제외 사유 | — |
| fontTools · brotli · uharfbuzz · fontbakery · Pillow · playwright | PyPI | MIT/Apache/BSD | — | 빌드·QA 도구(배포물에 포함 안 됨) | 사용 중 |

## 6. 저장소 구조

```
JennySans/
  AGENTS.md  CLAUDE.md  README.md  LICENSE(OFL)  THIRD-PARTY-NOTICES.md
  docs/{ROADMAP,PROGRESS,DISTRIBUTION}.md  docs/research/  docs/spec/  docs/qa/
  charset/      유니코드 범위 정의(required.txt 등)  ← architect
  sources/      원본 폰트(비커밋) + MANIFEST.md(출처·버전·SHA)
  tools/        Python 파이프라인(fetch/verify/build/test)  ← builder
  build/        중간 산출(비커밋)
  dist/         릴리스 산출: static/ variable/ web/ css/
  site/         스페시먼·테스트 페이지(정적)
  deploy/       nginx conf·배포 스크립트·.env.example(키 이름만)
  .claude/agents/ 팀원 정의   .claude/skills/font-pipeline/ 빌드·검증 절차
```

## 7. 이름·버전 정책 (팀장 확정, 변경 시 §8)

- 패밀리 영문 **JennySans**, 한글 현지화 이름 **제니산스**(name ID 1/16 ko-KR 레코드). 둘 다 RFN 으로 선언. 대안 「제니고딕」은 사용자 결정 대기.
- 변수 폰트 패밀리명은 **"JennySans Variable"**(공백 포함, ko "제니산스 Variable") — 정적 9종과 같은 PC 에 함께 설치해도 충돌하지 않게(Pretendard 선례). PS `JennySansVariable-<Weight>`, 파일 `JennySansVariable.ttf`.
- 정적 웨이트 이름: Thin(100)·ExtraLight(200)·Light(300)·Regular(400)·Medium(500)·SemiBold(600)·Bold(700)·ExtraBold(800)·Black(900).
  PostScript 이름 `JennySans-<Weight>`, 변수 폰트 `JennySansVariable` / PS `JennySansVariable-Regular`.
- 버전: `Version <major>.<minor>[.<patch>]` (head.fontRevision 동기). 첫 릴리스 **1.000**. 원본 버전은 name ID 5 뒤에 `(based on …)` 로 기록.
- 파일명: `JennySans-Bold.ttf`, `JennySans-Bold.otf`, `JennySansVariable.ttf`, 웹 `JennySans-Bold.woff2`, 분할 `JennySans-Bold.subset.<n>.woff2`.

## 8. 결정 기록

| 일자 | 결정 | 근거 |
|---|---|---|
| 2026-09-05 | 프로젝트 착수. 파생 폰트 방식(§1-1). 폴더 `<repo>`. 이름 JennySans/제니산스 | 사용자 지시·현실적 범위 |
| 2026-09-05 | 도구는 fontTools 중심 순수 Python 파이프라인(FontForge 미사용) | 로컬에 FontForge 없음·재현성 |
| 2026-09-06 | **원본 확정: 방식 A** — Pretendard 1.3.9 파생 + Noto Sans KR VF(100–900 인스턴스, UPM 2048 스케일)로 결손 보충. 근거 `docs/research/04-recommendation.md` | 9웨이트·변수·한글/라틴 조화 완료·라이선스 선례(name ID 9 누적 고지) |
| 2026-09-06 | **1.000 산출 형식 = 정적 TTF(glyf) 9종 + 변수 TTF + WOFF2(전체·124분할) + CSS 3종.** OTF(CFF)는 1.1 이후(수요 확인 후) | CFF 이식은 qu2cu 변환·별도 QA 필요. TTF 는 한글·Office·Photoshop·Unity·Flutter·웹 전부 동작 |
| 2026-09-06 | 변수 폰트도 결손 글립 포함을 목표: 9 인스턴스 피크 gvar(중간 마스터) 방식 → 실패 시 2마스터(100/900) → 최후 rename-only(제한 문서화) | 게이트 1항(전 웨이트+변수 커버리지) |
| 2026-09-06 | 가나(M PLUS 1 유래)·한자 등 범위 밖 글립은 서브셋에서 제외. 단 LICENSE 저작권 4줄(Pretendard·Adobe Source·Inter·M PLUS 1)은 보수적으로 전부 유지 + JennySans 줄 추가 | OFL 조건 2·3 준수, 선례(Pretendard) 동일 |
| 2026-09-06 | U+0149 ŉ 는 required 제외(유니코드 비권장 문자, Inter 미보유). 옛한글 `ljmo/vjmo/tjmo` 조합 피처는 범위 밖(자모 단독 글립만) | 리서처 04 §4 |
| 2026-09-06 | 수직 메트릭 전 웨이트 typo=hhea=win 1950/-494/0 + USE_TYPO_METRICS (Pretendard OTF 1949 → 1950 정정) | 웨이트 전환 시 줄높이 불변 |
| 2026-09-06 | 웹 분할은 Google Fonts 한국어 124 슬라이스 unicode-range 데이터 재사용(`docs/research/google-kr-slices.css`) + 전체 WOFF2 병행 | 실측 슬라이스당 17–56 KB, 첫 화면 ≈ 라틴 26 KB + 한글 2–3 슬라이스 |
| 2026-09-06 | 아키텍트 결정요청 회신: ① Hangul Jamo U+1100–11FF **256자 전부 required**(보충원본이 전량 보유, 비용 없음), 자모확장 A/B 는 korean-old 유지하되 **빌드 대상 = required ∪ recommended ∪ korean-old(∩ 원본 보유)**, required 만 100% 게이트 ② 그리스 기본(U+0391–03C9, 03A2 제외)+악센트 7·키릴 U+0400–045F 96·루마니아어 Șș Țț → **required 승격**(Pretendard 실보유 확인) ③ 변수 폰트명 "JennySans Variable" ④ §4-8 RFN 문구 보정 ⑤ RFN 에 '제니산스' 추가 | 팀장 실측(Pretendard-Regular.ttf cmap) |
| 2026-09-06 | 보충 글립 스케일은 1.966 고정이 아니라 **카테고리별 실측**(한글 몸체 ≈2.03, 호환자모 ≈2.07, 진행폭 1770 고정)으로 `docs/spec/07-supplement.md` 에 표로 확정 → 빌더 config 반영 | 팀장 bbox 실측: 가 Pretendard 1652×1778 vs Noto 805×883 |
| 2026-09-06 | Pretendard 미보유로 확인된 required 블록: 괘선 U+2500–257F(0/128), ◌ U+25CC, 괄호·원문자 U+3200–327F(1/128), 단위 U+3380–33DF 중 16, Hangul Jamo 전부 → 전부 Noto Sans KR VF 에서 이식 | 팀장 실측 |
| 2026-09-06 | **저작권 첫 줄 정본**(LICENSE 1행 = name ID 0 1행, 한 글자도 다르지 않게): `Copyright (c) 2026 JennySoft (https://jennysoft.co.kr), with Reserved Font Names 'JennySans' and '제니산스'.` 원본 고지는 ID 0 에서 `Portions ` 접두 허용, LICENSE 에서는 원문 그대로 | 릴리스·빌더·스펙 3자 불일치 해소 |
| 2026-09-06 | 자체 CDN 경로 `https://font.jennysoft.co.kr/v/1.000/…` + `/latest/`(심링크). 분할 파일명 `JennySans-<W>.subset.<n>.woff2`. git 태그 `v1.0.0`(npm 1.0.0) ↔ 폰트 버전 1.000 (`X.YZZ ↔ X.Y.ZZ`) | 릴리스 부록 C |
| 2026-09-06 | Pretendard·Noto 모두 없는 required 4자(⅔ ∼ ≒ ◈)는 **3차 원본 없이 Pretendard 부품 합성**(07 §5: ⅔=⅓ 구조 재현 컴포지트, ∼=Noto ∽ 미러, ≒==+·· 합성, ◈=◇+◆×0.5). Gothic A1 폴백 미채택 | 원본·고지 추가 없음, 스타일 일관 |
| 2026-09-06 | 보충 이식은 07 §6 규칙표(`tools/config/supplement.json`)를 정본으로 — 참조 글립 기준(`mode: ref`) 스케일·진행폭. OS/2 codePageRange 한국어 비트는 Pretendard 선례(한자·가나 제외, 누락 ≤8 세트) 채택, 스펙 03 §4 를 이에 맞춤 | 빌더 실측·리포트 |
| 2026-09-06 | **도메인 확정 `font.jennysoft.co.kr`**(사용자 등록·DNS 175.127.49.246 실측). 이전 표기 `fonts.` 는 전부 교체. name ID 11·CSS 주석·nginx·문서 모두 | 사용자 지시 |
| 2026-09-06 | 사용자 지시: **폰트 소개 홈페이지 + 다운로드** 제작·공개. 팀원 `font-site` 신설(site/·패키지 zip). 서버 반영(nginx·인증서·/var/www/font)은 **승인된 것으로 간주**하되, 폰트 파일 공개는 QA RELEASE OK 후에(그 전엔 홈페이지 골격만 올릴 수 있음) | 사용자 지시 |
| 2026-09-06 | 서버 부트스트랩 완료(팀장 직접): `/var/www/font/{v,download}` + 임시 index, `/etc/nginx/conf.d/font.conf`(80→443, `/v/` 불변 1년+CORS, `/latest/`·`/download/` 300초, zip attachment), 인증서 `/etc/pki/tls/certs/font.crt`(acme.sh ALPN·Let's Encrypt, 만료 2026-12-04), 갱신 `renew-font-cert.sh` cron `7 5 * * *`. 스크립트 사본 `deploy/font-bootstrap.sh` | https://font.jennysoft.co.kr 200 실측 |
| 2026-09-06 | 아키텍트 결정 대기 회신: VF 축 100–900 절단 **채택**, 괘선 획 두께비 1.38 **허용**, OS/2 win 1950/494 **유지**(Pretendard 동일 — MS Word·한글은 win 메트릭으로 줄높이를 잡으므로 상향 시 Pretendard 대비 줄높이 변동). fontbakery `win_ascent_and_descent` 는 **문서화된 예외**로 처리(라틴 악센트 대문자 yMax 2172, GDI 극단 케이스) — 게이트 3항 "FAIL 0"의 유일한 승인 예외 | 원본 동작 호환 우선 |
| 2026-09-06 | 사용자 질의 회신: 다국어는 **언어판 분리**가 표준(Noto CJK·Pretendard JP 선례) — JP/SC/TC·Hanja 는 별도 패밀리로 후속(ROADMAP 후속 N1~N4). 저작권 등록은 프로그램저작물로 기여분만 가능(입증용), 실효적 보호는 **상표 출원(JennySans·제니산스, 9류)** — 절차 문서 `docs/LEGAL-REGISTRATION.md`(release) | 사용자 질의 |
| 2026-09-07 | QA 티켓 5(ㅥ U+3165 하단이 ㄴ보다 19~25 unit 낮음)는 **결함이 아니라 원본 재현**으로 판정 — 팀장 실측: Noto 자신이 ㅥ 을 ㄴ 보다 3(Regular)~13(Black) unit 아래에 그리며(ㄴ 두 개 결합 글자의 광학 보정), 우리 결과는 `sy(1.965) × 원본 차이` 와 오차 ≤1.3 unit 으로 일치. 글립을 옮기면 원본 디자인 변경(AGENTS §1-1·§5 위반)이므로 **이동하지 않고 검사식을 정정**(J 차이 ≈ sy × N 차이 ±6 unit). 근거 `build/ticket5-measure.md` | 팀장 실측·설계 원칙 |
| 2026-09-07 | SEO: 구글 소유확인 파일 `site/google85364fe7cc780e8d.html`(사용자 제공, 파일명 " (1)" 제거), 홈페이지 메타(robots·keywords·OG·Twitter·canonical·hreflang)·JSON-LD(Organization·WebSite·SoftwareApplication)·파비콘 세트·og-image 1200×630(`tools/seo_assets.py`)·`robots.txt`·`sitemap.xml` 추가. 등록 절차 `docs/SEO_REGISTRATION.md` | 사용자 지시 |
| 2026-09-07 | 서버 nginx 를 `deploy/nginx-font.conf` 완전판으로 교체·reload(백업 `font.conf.bak.20260907-010806`). 로컬 git 최초 커밋(민감정보 스캔 0건, 푸시 없음) | 팀장 |
| 2026-09-08 | **한자를 본 패밀리에 포함(1.100)** — 팀장 실측(`build/hanja-measure.md`): KS X 1001 한자 4,620자, Noto Sans KR VF 에 4,619 보유, 정적 1웨이트 +약 1.5 MB(2.6→4.2 MB, 1.6배)·9웨이트 22→35 MB·VF 7.0→9.5 MB, **웹 분할본은 영향 0**(한자 슬라이스는 필요할 때만 내려감). 앞서 말한 "웨이트당 15~20 MB"는 전체 CJK 2만 자 기준이었고 한국 문서용은 그 1/4 → 포함이 합리적. Pretendard 는 한자 0자라 전량 Noto 이식 | 사용자 요청·팀장 실측 |
| 2026-09-08 | **JennySans = 한국어판(한국식 한자 포함), JP/SC/TC 는 별도 패밀리** 유지 — 분리 근거는 용량이 아니라 **자형**: 같은 한자 코드포인트가 한·일·중에서 표준 자형이 다르고, 한 파일에 넣으면 `locl` + 언어 태그가 없는 앱에서 틀린 자형이 나온다(Noto Sans CJK·Source Han Sans 동일 구조) | 사용자 질의 회신 |
| 2026-09-08 | 릴리스 순서: **1.000 을 QA 통과 즉시 공개**(사이트 개통·SEO 색인 시작) → 곧바로 **1.100(한자판)** 빌드·QA 후 `latest` 를 1.100 으로. 버전 경로(`/v/<ver>/`)와 심링크가 있어 이중 릴리스 비용이 없다 | 팀장 |
| 2026-09-08 | 홈페이지에 **글자맵(전체 글립 탐색)·문장 견본·언어 커버리지(지원 언어 수·목록)** 섹션 추가 지시 | 사용자 요청 |
| 2026-09-08 | **사용자 확정**: 패밀리 구조 = `JennySans`(한국어판, 한국식 한자 포함) / `JennySans JP`·`JennySans SC`·`JennySans TC`(별도 패밀리). 이 구조는 변경 대상이 아니며 이후 모든 이름·문서·사이트 문구가 이를 따른다 | 사용자 승인 |
| 2026-09-08 | **1.100 범위 확정 = 한자(KS X 1001 4,620) + 베트남어(92자) + 카자흐·몽골 키릴(18자)** — 팀장 실측: 베트남어 U+1EA0–1EF9·U+01A0/01A1/01AF/01B0 92자와 확장 키릴 18자가 **Inter(=Pretendard 라틴 원본) 에 전량 존재** → 디자인 정합 완벽, 웨이트당 약 +35 KB. 그리스어는 이미 실질 완비(부족분은 미할당 코드포인트·고대 KAI 기호·아노텔레이아뿐) | 사용자 질의·팀장 실측 |
| 2026-09-08 | 범위 밖 확정: 태국어·아랍어·히브리어·데바나가리 등 **비라틴/비CJK 문자권**(결합·연결·우횡서라 셰이핑 규칙이 다름, 원본 미보유). 요구가 생기면 별도 프로젝트 | 팀장 |
| 2026-09-08 | 사용자 질의(저작권·원본과의 차이) 회신 및 **공개 문서화 지시**: (a) 한국 법상 글자체 도안은 저작권 비보호(대법원 94누5632), 폰트 파일은 프로그램저작물(99다23246) → "닮은 것"은 문제 아님, 우리가 안전한 이유는 **원본이 OFL 이고 4개 조건을 전부 지켰기 때문**. (b) 외곽선은 Pretendard 와 사실상 동일(디자인 변경 금지 원칙) — 실측 차이는 **한국 문서용 문자 +607자**(첫가끝 자모 256·괘선 128·원문자 179·수학 60·자모확장 101 등), **가나 183자 제거**, **⅔ ∼ ≒ ◈ 4자 자체 합성**, 메트릭 통일·패밀리 단일화·웹 990조각 분할·fontbakery 결함 6건 수정. → README·홈페이지에 **"원본과 무엇이 다른가"** 절을 넣어 크레딧과 차이를 명시(OFL 정신·사용자 신뢰) | 사용자 질의 |
| 2026-09-08 | 사용자 질의(상용 판매 가능 여부) 회신: OFL 1.1 은 **폰트 파일 단독 판매만 금지**(조항 1), **소프트웨어·제품에 번들해 판매하는 것은 명시 허용**(조항 2), 폰트로 만든 결과물에는 라이선스가 미치지 않음(조항 5). 따라서 제니소프트 유료 제품 번들·앱/게임 임베드·인쇄물 판매·커스터마이징 용역·유료 CDN 은 전부 가능. 불가: 폰트 단독 판매·독점 라이선스·라이선스 전환·재배포 차단. **OFL 파생물이라 라이선스 변경은 비가역** — 유료 폰트 사업을 하려면 원본부터 새로(전 글립 자체 디자인) 별도 프로젝트. 현 목표(전 솔루션 공용 + 대외 공개)에는 OFL 이 최적이며 상표 등록으로 이름 보호 병행 | 사용자 질의 |
| 2026-09-08 | **사용자 최종 방침 확정**: JennySans 는 **제니소프트 유료 솔루션에 번들·임베드해 쓰는 "방어형" 폰트**다(라이선스 비용·제약 제거 + 브랜드 일관성). OFL 단독 판매 금지 제약은 이 목적과 충돌하지 않으므로 **현 구조를 그대로 유지**한다. **상용 판매용 폰트는 별도 프로젝트**로 나중에 개발한다(전 글립 자체 디자인 필요 — OFL 파생물로는 불가). 지금은 **이 프로젝트를 먼저 마무리**하고, 완료 후 상용 폰트 프로젝트를 기획한다 | 사용자 지시 |
| 2026-09-08 | 실측 정정 3건(릴리스 교차검증): ① 그리스 미보유는 U+038B/038D/03A2(미할당)·U+03CF·U+0387 외에 **U+0384 ΄·U+0385 ΅(단독 악센트) 도 없음** — 결합형 글자는 전부 있어 본문 표기 지장 없음 ② **자체 제작 글립은 4자가 아니라 8자**(￢￣￤ ⅔ ≒ ◈ + 미러 ∼ + DŽ) ③ `all.zip` 은 문서를 담아 **문서 수정 시마다 SHA 변동** → 정본은 `SHA256SUMS.txt`, 릴리스 체크리스트에서 zip 생성은 문서 확정 후 마지막에 | 릴리스 실측 |
| 2026-09-09 | **QA 1차 판정 RELEASE OK 접수**(게이트 8항목 중 7 PASS, 정적 fontbakery FAIL 0 — 5차 513건 → 0). 남은 VF `nested_components` 5글립은 **승인 예외를 늘리지 않고 고친다**: 빌더가 되돌린 12건의 사유(정적 대비 2.0~2.4 unit)는 스펙 07 §7(c) 컴포지트 허용치(≤8 unit) 안이므로 판정 기준을 07 §7(c) 로 맞춰 전부 평탄화 → 예외 없이 FAIL 0. QA 권고안 채택 | 게이트를 지키는 쪽이 원칙(AGENTS §4-3) |
| 2026-09-09 | 같은 재빌드에 티켓 9(`vhea`/`vmtx` 가 Thin·ExtraLight·Light 3 웨이트에만 존재 — 원본 유래 비대칭)·11(`unreachable_glyphs` 고아 4자, 평탄화 부작용) 도 함께 처리해 **1.000 을 WARN 없이 낸다**. 사용자 지시 "QA 는 충분히 검수하고 책임지고 퀄리티를 보장" 에 따름 | 1.001 로 미루지 않음 |
| 2026-09-09 | 티켓 10(스펙 05 §4 크기 목표 초과) 팀장 결정: **목표를 실측에 맞춰 조정**한다. `jennysans-dynamic-subset.css` gzip 101 KB 는 9 웨이트 × 99 슬라이스 = 891 `@font-face` 의 필연 — 목표를 ≤110 KB 로 고치고, **"9 웨이트 전부가 필요 없으면 변수 폰트 CSS 나 필요한 웨이트만 쓰라"** 는 권고를 스펙·README·사이트 사용법에 명시. VF 슬라이스 ≤95 KB·라틴 ≤70 KB 로 조정(6차에서 보충 글립 gvar 증가분 반영). 게이트 6 자체는 PASS | 실측 기반 목표 재설정 |
| 2026-09-09 | **QA 최종 판정 RELEASE OK(조건 없음)** — 게이트 8항목 전부 PASS, 티켓 1~11 전부 종결(verified 7·closed 4), **승인 예외 0건**. fontbakery 정적·변수 모두 FAIL 0·ERROR 0. 8차 파일 크기 원본 대비 −5.9~−6.0% | `docs/qa/QA-REPORT-1.000.md` |
| 2026-09-09 | **1.000 서버 배포 완료** — `https://font.jennysoft.co.kr` 홈페이지·글자맵·다운로드 4종·CDN(`/v/1.000/`·`latest→v/1.000`) 공개. 실브라우저 검증 ALL PASS(데스크톱·모바일), 다운로드 zip SHA-256 원본 일치 대조 완료 | 팀장 |
| 2026-09-09 | ⚠ **배포 함정 발견·해결: SELinux 컨텍스트**. Rocky Linux(Enforcing)에서 `/tmp` 로 tgz 를 풀어 `/var/www/font` 에 복사하면 파일에 `user_tmp_t` 가 붙어 **nginx 가 못 읽고 전부 403**(`Permission denied`)이 된다. 파일·권한·소유자는 정상이라 원인 파악이 어렵다. 해결: `sudo restorecon -RF /var/www/font`. **`deploy/remote-install.sh` 마지막 단계에 restorecon 을 넣어 재발을 막을 것**(release 배정) | 팀장 실측(nginx error.log·`ls -Z`) |
| 2026-10-24 | **1.001(v1.0.1) = 체크박스 ☐☑☒ U+2610–2612 추가**(대표 지시 — 검사성적서·리포트 체크 칸). 원천 실측: Pretendard 1.3.9·Noto Sans KR 2.004·Source Han Sans KR 2.005 **모두 미보유** → 원천 보충 불가, **자체 부품 합성** 채택: 박스 = 같은 웨이트 □ U+25A1 외곽선 그대로(크기·획·진행폭 = □), 마크 = ✓ U+2713 / × U+00D7 를 **균등 축소(아핀만, 새 외곽선 없음)** 해 □ 속공간 중앙, 여백 max(0.4×박스 획, 72u)(0.3/0.4/0.5 견본 비교). ✗ U+2717 대신 × 를 쓴 이유: VF 의 ✗ 는 겹친 윤곽 2개(정적 12점과 구조가 다름), × 는 정적·VF 모두 단일 윤곽 12점. 마크 획은 축소로 박스보다 가늘어진다(Regular ≈0.7·Black ≈0.45배) — 아핀만 허용 원칙(§1-1)을 지키는 대가로 수용. charset 은 이미 `recommended.txt` 에 있어 변경 없음(required 12,602 유지), 대신 verify 에 `ballot` 검사(FAIL 기준) 추가. 같은 패치에 소개 문구 "한글·영문(라틴)" 교체(대표 지적). 대표가 배포·GitHub·npm 공개 승인 — 실행은 코디네이터 | 대표 지시·팀장 실측 |
