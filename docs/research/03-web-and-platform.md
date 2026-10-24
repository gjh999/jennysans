# 03 — 웹·변수·플랫폼 기술 조사 (font-researcher, 2026-09-05)

> 실측/1차 출처 표시: (실측) = 이 PC 에서 실행해 얻은 값, (원문) = 공식 문서 인용(WebFetch), (확인 못 함) = 출처를 못 찾음.

## 1. 한글 웹폰트 `unicode-range` 분할 — Google Fonts 실측

- (실측) `curl -A "Mozilla/5.0 … Chrome/128"` 로 `https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100..900&display=swap` 을 받으면 **@font-face 124 블록**(WOFF2, `font-weight: 100 900`) 이 온다. 저장본: `docs/research/google-kr-slices.css`(범위 데이터는 사실 정보라 재사용 가능).
  - 정적 2 웨이트 요청(`wght@400;700`) → 248 블록(=124×2). Nanum Gothic → 92 블록, IBM Plex Sans KR → 94 블록(패밀리별 글립 집합에 따라 슬라이스 수가 다름).
  - 124 슬라이스 WOFF2 총합 **3,519,780 bytes**(HEAD content-length 합산). 슬라이스당 17–56 KB. 마지막 슬라이스(#123, `U+0000-00FF, …` 라틴) 26,004 bytes.
  - 커버 코드포인트 18,998개, 한글 완성형 11,172 전부 포함. 한글이 든 슬라이스 84개(슬라이스당 한글 13–155자, 총 코드포인트 100–155). 슬라이스 #0–1 은 CJK 호환한자, #66–99 는 한자·가나·기호, #120–123 은 키릴·베트남어·Latin-Ext·Latin.
  - 배열은 **빈도 역순**: 번호가 큰 슬라이스가 고빈도. `가`·`이` 는 #119(ASCII 일부와 같은 슬라이스), `한`·`는` 은 #118, `ㄱ` #109, `①` #108, `※` #111(+#123), `€`·`ñ`·`¿` 는 라틴 슬라이스 #123.
  - 시사점: 첫 화면(라틴 + 고빈도 한글 2–3 슬라이스)은 약 26 + 3×30 ≈ 110–120 KB 수준. 우리 분할도 "라틴 1 + 한글 빈도순 N" 구조를 따르고, 범위는 Google 것을 그대로 쓰거나(한국어 코퍼스 빈도 기반으로 검증된 분할) 자체 코퍼스로 재계산.
- (실측) 도구: `fontTools.subset`(`--unicodes=<범위> --flavor=woff2 --layout-features='*'`)로 슬라이스별 WOFF2 생성 가능, `fontTools.ttLib.woff2` + brotli 설치 확인. 변수 폰트 서브셋도 지원(gvar 유지).
- 주의: 슬라이스에 없는 문자를 만나면 브라우저는 다음 `src` 가 아니라 **폴백 폰트**로 렌더 → `charset/required.txt` 의 모든 코드포인트가 어느 한 슬라이스에는 반드시 들어가야 함(QA 항목).

## 2. 변수 폰트 이름 변경 시 손봐야 할 테이블 (실측 덤프 `name-tables.md` 기준)

| 테이블 | 무엇을 | 근거(실측) |
|---|---|---|
| `name` | ID 1/2/3/4/6/16/17 + **ID 25(Variations PostScript Name Prefix)** + fvar 인스턴스가 참조하는 ID ≥256 문자열(PretendardVariable: 258–272 에 "Pretendard…" 인스턴스명) + STAT 축/값 이름(ID 256, 273 등) + ID 0/7/9/13/14 고지 | PretendardVariable.ttf 에서 "Pretendard" 가 ID 1,3,4,6,7,9,16,25,258…272 에 존재 |
| `fvar` | `instances[].subfamilyNameID` / `postscriptNameID` 가 가리키는 문자열(위 name 레코드) — psName 은 `JennySansVariable-<Weight>` 형식 | Pretendard 인스턴스 ps=`PretendardVariable-Thin` … |
| `STAT` | `DesignAxisRecord.AxisNameID`, `AxisValue.ValueNameID`, `ElidedFallbackNameID`(Pretendard = 2) — 값 자체(Format 1/3, Regular 400→Bold 700 링크, ital 0→1)는 유지 | Pretendard STAT v1.1: wght 10값 + ital F3 |
| `OS/2` | `achVendID`(CTUS→우리 4글자), usWeightClass(정적), fsSelection(REGULAR/BOLD/USE_TYPO/WWS 비트), fsType=0 | |
| `head` | fontRevision(1.000), modified 시각 | |
| `CFF `(OTF) | `cff.fontNames[0]`(PS 이름), TopDict `FamilyName`/`FullName`/`Notice`/`Copyright` — CID 폰트(SHS)는 ROS 유지 | SHS/Pretendard OTF 는 CFF |
| `DSIG` | 수정 후 무효 → 제거 | SHS KR/Plex/NanumSquare 에 존재, Pretendard 에는 없음 |
| `post` | `underlinePosition` 등은 유지, 글립명(TTF format 2)은 그대로 | |
| `meta`/`gasp` | 있으면 유지 | |

- 정적 인스턴스 생성: `fontTools.varLib.instancer`(설치 확인) — `instantiateVariableFont(vf, {"wght": 300})`. STAT·name 은 인스턴스화 뒤 다시 정리(instancer 가 인스턴스 이름을 name 에 붙이는 `updateFontNames=True` 옵션 있음).
- 변수 폰트에 글립 추가(결손 보충)는 마스터별 외곽선이 필요 → 마스터 2개(100/900)로 `varLib.build` 하거나 gvar 를 수작업 생성해야 함. 1차 릴리스 범위 판단은 04 §4-5.

## 3. CFF → TTF(glyf) 변환 품질

- (실측) `fontTools.cu2qu`, `fontTools.pens.cu2quPen`, `fontTools.qu2cu`, `fontTools.pens.qu2cuPen` 모두 import 성공(fontTools 4.64). `otf2ttf` CLI 는 없음 → fontTools `Snippets/otf2ttf.py` 와 같은 10여 줄 스크립트(Cu2QuPen → glyf/loca/maxp 생성, `head.glyphDataFormat`, `post` 형식 유지)로 빌더가 구현.
- 품질: 3차 베지어 → 2차 근사, 기본 `max_err = 1.0`(UPM 1000 기준 1 유닛, Pretendard 2048 이면 상대 오차 절반) — 육안 차이 없음. 점 수는 증가(파일 커짐: Pretendard OTF 1.5 MB ↔ 공식 TTF 2.6 MB 실측). CFF 힌트(BlueValues)는 소실, TT 힌팅은 생기지 않음(무힌팅 TTF — Pretendard 공식 TTF 도 fpgm 없음, 동일 상태).
- 권고: 변환 대신 **원본이 이미 제공하는 glyf 판**을 우선 사용 — Pretendard `public/static/alternative/*.ttf`(9종), `PretendardVariable.ttf`, Google Fonts `NotoSansKR[wght].ttf`. OTF(CFF) 산출은 Pretendard OTF + SHS KR OTF(보충 글립)로 구성하면 변환 자체가 거의 필요 없다. 보충 글립을 TTF→CFF 로 넣어야 할 때는 `qu2cu`(2차→3차, 무손실에 가까움) 사용.

## 4. Windows·앱 패밀리 묶임 — RIBBI vs Typographic family

- (원문) OpenType `name` 스펙(learn.microsoft.com/typography/opentype/spec/name):
  - ID 1: "The Font Family name is used in combination with Font Subfamily name (name ID 2), and should be shared among at most four fonts that differ only in weight or style (italic/oblique)… it is strongly recommended that name IDs 16 and 17 be used in fonts to create an extended, typographic grouping."
  - ID 2: "This should be used for weight and style (italic/oblique) variants only… Fonts that are not part of an extended typographic family and with no distinctive weight or style… should use "Regular" as the Font Subfamily name."
  - 예시: "the Font Family name for the Arial Black font is “Arial Black”… name ID 16 should also be included with a shared name (e.g., "Arial")". ID 21/22(WWS) 는 "in case the entries for IDs 16 and 17 do not conform to the WWS model" 에만; fsSelection bit 8 과 상호배타.
- (실측) 후보 폰트들의 실제 관행 — 전부 위 권고를 따름:

| 폰트(웨이트) | ID 1 | ID 2 | ID 16 | ID 17 | fsSelection | macStyle |
|---|---|---|---|---|---|---|
| Pretendard Light | `Pretendard Light` | `Regular` | `Pretendard` | `Light` | REGULAR+USE_TYPO | 0 |
| Pretendard Regular | `Pretendard` | `Regular` | `Pretendard` | `Regular` | REGULAR+USE_TYPO | 0 |
| Pretendard Bold | `Pretendard` | `Bold` | `Pretendard` | `Bold` | BOLD+USE_TYPO | 1 |
| Pretendard Black | `Pretendard Black` | `Regular` | `Pretendard` | `Black` | REGULAR+USE_TYPO | 0 |
| Source Han Sans KR Light / Bold | `Source Han Sans KR Light` / `Source Han Sans KR` | `Regular` / `Bold` | `Source Han Sans KR` / (없음) | `Light` / (없음) | (REGULAR 없음) / BOLD | 0 / 1 |
| Inter Thin / Bold | `Inter Thin` / `Inter` | `Regular` / `Bold` | `Inter` / (없음) | `Thin` / (없음) | REGULAR+USE_TYPO / BOLD+USE_TYPO | 0 / 1 |
| IBM Plex Sans KR Light | `IBM Plex Sans KR Light` | `Regular` | `IBM Plex Sans KR` | `Light` | WWS(bit8) 만 | 0 |

- JennySans 권고(architect 스펙에 반영): Regular(400)·Bold(700) 만 ID1=`JennySans` + ID2 `Regular`/`Bold` 로 스타일 링크(fsSelection REGULAR/BOLD, macStyle bold 비트, OS/2 usWeightClass 400/700). 나머지 7 웨이트는 ID1=`JennySans <Weight>`, ID2=`Regular`, ID16=`JennySans`, ID17=`<Weight>`. 모든 파일에 ID 16/17 을 넣는다(Regular/Bold 도). ko-KR(0x0412) 레코드로 ID 1/16=`제니산스`(AGENTS §7).
  - 결과: Windows GDI·한글(HWP)·구형 앱은 "JennySans", "JennySans Light", … 로 따로 보이고(Pretendard·Noto 와 같은 경험), DirectWrite·macOS·Photoshop·브라우저는 ID 16/17 로 한 패밀리 9 스타일로 묶임. 변수 폰트는 named instance 로 9 스타일 노출.
  - USE_TYPO_METRICS(bit 7) 세트 + hhea = typo = win 정합(Pretendard 방식) → 웨이트 간 줄 높이 불변.

## 5. 게임엔진·앱 형식 선호

| 플랫폼 | 지원 형식(원문) | 권고 산출 |
|---|---|---|
| **Unity** | Unity Manual(create-meshes-text-strings): "Import a TrueType font by dragging a .ttf file into the Project window." TextMesh Pro Font Asset Creator(ugui 2.0 매뉴얼): "make sure that you've already imported the font (usually a TrueType .ttf file)"; "You can use it to create both Signed Distance Field (SDF) fonts and bitmap fonts." OTF/변수 폰트 지원 여부는 문서에 명시 없음(**확인 못 함**) | 정적 **TTF(glyf)** 9종. TMP 는 SDF 아틀라스 생성 시 힌팅 무관. 동적 아틀라스용으로 한글 11,172 포함 전체 TTF 제공, 경량 버전(KS X 1001 2,350자) 별도 |
| **Godot 4** | FontFile 문서: "TrueType (.ttf), TrueType collection (.ttc), OpenType (.otf), OpenType collection (.otc), WOFF (.woff), WOFF2 (.woff2), Type 1 (.pfb, .pfm)"; 변수 좌표 `variation_coordinates` 지원; MSDF 렌더 지원("font hinting is not available with MSDF") | TTF 정적 + 변수 TTF 모두 사용 가능. MSDF 쓰면 힌팅 불필요 |
| **Flutter** | docs.flutter.dev/cookbook/design/fonts: 지원 `.ttc`, `.ttf`, `.otf`; "Flutter does not support fonts in the Web Open Font Format, .woff and .woff2, on desktop platforms." pubspec 에 `weight` 를 100–900 정수로 선언; "If a TextStyle object specifies a weight or style without a corresponding font file, the engine uses a generic file … Avoid relying on this capability." | 정적 TTF 9종을 pubspec `fonts:` 에 weight 별로 선언(웹 빌드도 같은 TTF 사용). 변수 폰트는 `FontVariation` API 로 가능하나 pubspec weight 매핑은 정적 파일 기준 |
| **Flame**(Flutter 위) | Flutter 와 동일 | 동일 |
| 웹 | WOFF2 + `unicode-range`(§1) + 변수 WOFF2 1개(`font-weight: 100 900`) | 정적 9×슬라이스 + 변수 1×슬라이스 두 세트 CSS |
| Windows/macOS 설치·Office·한글·Adobe | OTF(CFF) 또는 TTF 모두 설치 가능. Adobe 앱은 CFF/TTF 무관하게 ID 16/17 로 묶음 | 설치 패키지는 **OTF(CFF, 힌트 유지)** + TTF 둘 다 제공, 한글(HWP)·Office 용은 TTF 권장(GDI 힌팅·굵기 합성 호환) |

## 6. 빌드 도구 가용성 (실측, 2026-09-05)
- fontTools 4.64.0: `subset`, `merge`, `varLib.instancer`, `varLib.mutator`, `varLib.interpolatable`, `cu2qu`, `qu2cu`, `ttLib.woff2`, `otlLib.builder`, `feaLib` 모두 import OK. `fonttools` CLI 존재(`%USERPROFILE%\AppData\Local\Programs\Python\Python312\Scripts\fonttools.exe`).
- fontbakery 1.1.0, uharfbuzz 0.56.1(셰이핑 실측에 사용 — SUIT 빈 글립 확인), Pillow 12.3.0, brotli OK.
- FontForge 없음 → 외곽선 편집은 fontTools pen 계열로만.
