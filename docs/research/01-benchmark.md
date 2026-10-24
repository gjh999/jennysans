# 01 — 후보 폰트 벤치마킹 (font-researcher, 실측일 2026-09-05)

> 근거 파일: `docs/research/measurements.md`(전 파일 실측 표) · `measurements.json`(원자료·SHA-256) · `name-tables.md`(name/fvar/STAT 덤프)
> 실측 스크립트: `docs/research/scripts/measure_fonts.py`, `dump_names.py` · 원본: `sources/<이름>/` (`sources/MANIFEST.md`)
> 측정 집합: 한글 U+AC00–D7A3(11,172) · 호환자모 U+3131–318E(94) · 자모 U+1100–11FF(256) · 자모확장A U+A960–A97C(29) · 자모확장B U+D7B0–D7C6,D7CB–D7FB(72)
> · ASCII(95) · Latin-1 Supplement(96) · Latin Ext-A(128) · 스페인어 필수 `ñÑáéíóúÁÉÍÓÚüÜ¿¡ªº€«»`(21 코드포인트) · 그리스 U+0391–03C9(56) · 키릴 U+0410–044F(64)
> · KS X 1001 기호 샘플 79자(`※○●◎◇◆□■△▲▽▼☆★①…⑩㉠㉡㉢㈜㎏㎡㎜㎝㎞㎖℃℉→←↑↓↔±×÷≠≤≥∞∴√∠∑「」『』【】〔〕、。・…‥‘’“”§¶†‡‰₩€£¥¢`).
> "빈 글립" = cmap 에는 있으나 외곽선이 없는 글립(BoundsPen 으로 실제 그려 판정; 공백 문자 제외).

## 1. 한글 고딕 후보 — 개요·상태

| 후보 | 버전 / 최신 릴리스 | 1차 출처 | 라이선스 / RFN (원문은 02 문서) | 정적 웨이트 | 변수 | 형식 | UPM | 유지보수(저장소 마지막 push) | 판정 |
|---|---|---|---|---|---|---|---|---|---|
| **Pretendard** | 1.3.9 / 2023-11-05 | github.com/orioncactus/pretendard | OFL 1.1 · RFN `Pretendard` (+원본 RFN `Source`,`Inter`,`M PLUS 1` 누적) | 9 (100–900) | wght 45–930 (인스턴스 100–900) | OTF(CFF) + TTF(glyf, "alternative") + VF(glyf) | 2048 | 2026-07-23 (★3,561) | **한글 1순위** |
| **Source Han Sans KR** (Subset OTF) | 2.005R / 2025-06-18 | github.com/adobe-fonts/source-han-sans | OFL 1.1 · RFN `Source` | 7 (250,300,350,400,500,700,900) | 별도 VF 배포(888 MB zip, 미다운로드) | OTF(CFF, CID) | 1000 | 2025-06-25 (★17,184) | **한글 2순위 · 결손 보충** |
| **Noto Sans KR** | 2.004 / 2022-01-27 (Google Fonts 변수 TTF 2.004-H2) | github.com/notofonts/noto-cjk · google/fonts `ofl/notosanskr` | OFL 1.1 · 저작권 Adobe, RFN `Source`(GF OFL.txt) / `Noto` 는 Google 상표 | 7 (100,300,350,400,500,700,900) | wght 100–900 (GF TTF, 9 인스턴스) | OTF(CFF) + VF TTF(glyf) | 1000 | 2025-12-16 (★4,040) | **결손 보충 1순위(VF 인스턴싱)** |
| IBM Plex Sans KR | 1.1.0(font 1.003) / 2024-11-13 | github.com/IBM/plex | OFL 1.1 · RFN `Plex` | 8 (100–700, Text 450) — 800·900 없음 | 없음 | OTF(CFF)+TTF | 1000 | 2026-07-30 | 제외(라틴 부족) |
| Spoqa Han Sans Neo | 3.3.0(font 1.100) / 2021-06-07 | github.com/spoqa/spoqa-han-sans | OFL 1.1 · RFN `Spoqa Han Sans`, `… JP`, `… Neo` | 5 (250,300,400,500,700) | 없음 | OTF(CFF)+TTF | 1000 | 2022-06-15 | 제외(웨이트·갱신) |
| 나눔바른고딕 | TTF 1.000~1.0.1.0 / 2013–2015 | hangeul.naver.com (zip) | **OFL 원문 확인 못 함**(name ID13=`NHN Corporation`, zip 에 LICENSE 없음) | 4 (UltraLight·Light 모두 300, 400, Bold 600) | 없음 | TTF(힌팅)+OTF | 1000 | — | 제외 |
| Nanum Gothic (GF) | 3.020 / GF 2012 | google/fonts `ofl/nanumgothic` | OFL 1.1 · RFN `Nanum, Naver Nanum, NanumGothic, …` | 3 (400,700,800) | 없음 | TTF | 1000 | 2011 | 제외 |
| 나눔스퀘어 네오 | 1.000 / 2022 | hangeul.naver.com (zip) | **OFL 원문 확인 못 함**(name ID13/14 없음) | 5 (350,400,700,800,900) | wght 100–900(인스턴스 이름·값 불일치) | OTF+VF TTF | 1000 | — | 제외 |
| **Gothic A1** | 2.50 / GF 2018-02-24 (upstream 2017-12) | google/fonts `ofl/gothica1` · github.com/hanyangfont/Gothic | OFL 1.1 · 저작권 HanYang I&C, **RFN 선언 없음** | 9 (100–900) | 없음 | TTF(TT 힌팅) | 1024 | 2017 (2 commits) | **한글 3순위** |
| Wanted Sans | 1.0.3 / 2024-03-05 | github.com/wanteddev/wanted-sans | OFL 1.1 · OFL.txt 에 RFN 없음(상표는 name ID7) | 7 (400–1000) | wght 400–1000 | OTF+TTF+VF | 2048 | 2024-05-27 | 제외(경량 웨이트 없음) |
| SUIT | 2.0.5(font 2.040) / 2024-07-24 | github.com/sun-typeface/SUIT | OFL 1.1 · RFN `SUIT` · **fsType=4** | 9 | wght 100–900 | OTF+VF | 1000 | 2024-07-13 | 제외(한글 8,504자 빈 글립) |
| Freesentation | 2.001 / 2024 | github.com/Freesentation/freesentation | OFL 1.1(RFN 없음) · **라틴 원본 Roboto = Apache-2.0** | 9 | VF 있음 | — | — | — | 제외(§5 위배, 미다운로드) |
| Paperlogy | 1.001 / 2024 | github.com/Freesentation/paperlogy | OFL 1.1(RFN 없음) · 한글 Gmarket Sans, 라틴 Montserrat | 9 | — | — | — | — | 제외(디스플레이체, 미다운로드) |

## 2. 커버리지 실측 (Regular 기준; 다른 웨이트도 동일 — `measurements.md`)

| 폰트 | 한글 11,172 | 호환자모 94 | 자모 256 | 확A 29 | 확B 72 | ASCII 95 | Latin-1 96 | Ext-A 128 | 스페인어 21 | 그리스 56 | 키릴 64 | KS기호 79 | 결손 요약 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Pretendard-Regular.otf | **11172** | 53 | 0 | 0 | 0 | 95 | **96** | 127 | **21** | **56** | **64** | 73 | 호환자모 U+3165–318E(옛 자모 41자) · 자모 전부 · ŉ U+0149 · ∠∴◎㉠㉡㉢ |
| SourceHanSansKR-Regular.otf | **11172** | **94** | **256** | **29** | **72** | 95 | **96** | 30 | **21** | 49 | **64** | **79** | Latin Ext-A 98자(KS X 1001 에 있는 30자만 보유) · 그리스 악센트 U+03AA–03B0 |
| NotoSansKR[wght].ttf (GF VF) | **11172** | **94** | **256** | **29** | **72** | 95 | **96** | 30 | **21** | 49 | **64** | **79** | SHS KR 과 동일 |
| SpoqaHanSansNeo-Regular.otf | **11172** | **94** | **256** | **29** | **72** | 95 | 95 | 30 | **21** | 48 | **64** | **79** | U+00A0(NBSP) 없음 · Ext-A 98자 · ς U+03C2 |
| GothicA1-Regular.ttf | **11172** | **94** | **256** | 0 | 0 | 95 | **96** | **128** | **21** | **56** | **64** | **79** | 자모확장 A/B 만 없음 (커버리지 최상) |
| IBMPlexSansKR-Regular.otf | **11172** | **94** | 0 | 0 | 0 | 95 | 21 | 0 | **3** | 0 | 0 | 77 | 라틴 악센트 전무(ñáéíóú 없음) |
| WantedSans-Regular.otf | **11172** | 52 | 0 | 0 | 0 | 95 | 96(U+00AD 빈) | 112 | **21** | 0 | 0 | 52 | 그리스·키릴 없음 · KS 기호 27자 |
| NanumBarunGothic.ttf | **11172** | **94** | 0 | 0 | 0 | 95 | 40 | 18 | **7** | 48 | **64** | 78 | 스페인어 악센트 모음·ñ 전부 없음 |
| NanumSquareNeo-Variable.ttf | **11172** | **94** | 0 | 0 | 0 | 95 | 22 | 0 | **3** | 0 | 0 | 77 | 라틴 악센트 전무 |
| NanumGothic-Regular.ttf | **11172** | 93 | 0 | 0 | 0 | 95(` 빈) | 38 | 16 | **7** | 0 | 0 | 56 | 라틴·그리스·키릴·원문자 부족 |
| SUIT-Regular.otf | 11172 **(빈 8,504)** | 51 | 0 | 0 | 0 | 95 | 14 | 0 | **1** | 0 | 0 | 54 | **실제 그려진 한글 2,668자**(HarfBuzz 로도 빈 글립 진행폭 874 확인) |

라틴 후보:

| 폰트 | ASCII | Latin-1 | Ext-A | 스페인어 | 그리스 | 키릴 | KS기호 | 비고 |
|---|---|---|---|---|---|---|---|---|
| Inter-Regular.ttf / InterVariable.ttf | 95 | 95 (U+00AD 없음) | 127 (U+0149 없음) | **21** | **56** | **64** | 54 | Pretendard 라틴의 원본. opsz 14–32 × wght 100–900 |
| NotoSans[wdth,wght].ttf 2.015 | 95 | **96** | **128** | **21** | **56** | **64** | 22 | wght 100–900 × wdth 62.5–100 |
| SourceSans3VF-Upright.ttf 3.052R | 95 | **96** | **128** | **21** | **56** | **64** | 38 | wght **200**–900(100 없음). SHS 라틴과 같은 디자이너(Paul D. Hunt) |

## 3. 메트릭·비례 실측

| 폰트 | UPM | typo asc/desc/gap | hhea asc/desc/gap | win asc/desc | USE_TYPO(bit7) | capH/UPM | xH/UPM | 가 진행폭/UPM | 한글(가) 높이/UPM | 한글높이/capH | H 진행폭 | 0 진행폭 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Pretendard-Regular.otf | 2048 | 1949/-494/0 | **1950**/-494/0 | 1949/494 | Y | 0.707 | 0.530 | 0.864 (1770) | 0.868 | 1.228 | 1446 | 1220 |
| PretendardVariable.ttf | 2048 | 1950/-494/0 | 1950/-494/0 | 1950/494 | Y | 0.707 | 0.530 | 0.864 | 0.868 | 1.228 | | |
| SourceHanSansKR-Regular.otf | 1000 | 880/-120/0 | 1160/-288/0 | 1160/288 | N | 0.733 | 0.543 | 0.920 (920) | 0.904 | 1.233 | 728 | 555 |
| NotoSansKR (OTF/VF) | 1000 | 880/-120/0 | 1160/-288/0 | 1160/288 | N | 0.733 | 0.543 | 0.920 | 0.904 | 1.233 | 728 | 555 |
| SpoqaHanSansNeo-Regular.otf | 1000 | 970/-282/0 | 970/-282/0 | 1100/310 | Y | 0.733 | 0.543 | 0.920 | 0.897 | 1.224 | 728 | 596 |
| GothicA1-Regular.ttf | 1024 | 817/-207/**256** | 817/-207/256 | 1238/378 | Y | 0.731 | 0.525 | 0.961 (984) | 0.891 | 1.218 | 736 | 569 |
| WantedSans-Regular.otf | 2048 | 1752/-296/0 | **1950/-494**/0 (불일치) | 1950/494 | N | 0.707 | 0.504 | 0.864 | 0.867 | 1.227 | 1404 | 1280 |
| IBMPlexSansKR-Regular.otf | 1000 | 780/-220/**500** | 1085/-415/0 | 1085/415 | N | 0.698 | 0.516 | 0.892 | 0.868 | 1.244 | 707 | 600 |
| NanumBarunGothic.ttf | 1000 | 850/-300/0 | 850/-299/0 | 850/300 | N | 0.700 | 0.500 | 0.892 | 0.913 | 1.304 | 718 | 583 |
| Inter-Regular.ttf | 2048 | 1984/-494/0 | 1984/-494/0 | 1984/494 | Y | 0.728 | 0.546 | — | — | — | 1522 | 1292 |
| NotoSans[wdth,wght].ttf | 1000 | 1069/-293/0 | 1069/-293/0 | 1124/395 | Y | 0.714 | 0.536 | — | — | — | 741 | 572 |
| SourceSans3VF-Upright.ttf | 1000 | 1000/-326/0 | 1000/-326/0 | 1000/326 | N | 0.660 | 0.478 | — | — | — | 634 | 472 |

관찰:
- Pretendard 정적 OTF 는 `OS/2.sTypoAscender=1949` 인데 `hhea.ascent=1950`(1 유닛 불일치). VF 는 둘 다 1950. 파생 시 1950 으로 통일 필요(fontbakery 가 지적할 항목).
- Pretendard 의 한글은 Source Han Sans 한글을 **약 4 % 축소**(높이비 0.868 vs 0.904)하고 진행폭을 0.92→0.864 로 좁혀 라틴(Inter)과 맞춘 것. 무작위 200자 정규화 bbox 비교에서 SHS 와 최대 편차 평균 0.040·최대 0.042 UPM 비율 — 동일 골격의 축소·재조정임을 뒷받침(name ID 9 도 "Hangeul glyphs from Noto Sans CJK(Source Han Sans)" 로 명시).
  → SHS/Noto KR 에서 결손 글립(자모·기호)을 가져올 때 **스케일 ≈ 2.048 × 0.96 ≈ 1.966**, 진행폭은 Pretendard 한글 1770 에 맞추는 것이 출발점(architect 가 시각 확인 후 확정).
- SHS/Noto KR 은 `hhea`(1160/-288) 와 `typo`(880/-120) 가 다르고 USE_TYPO 미설정 → 플랫폼별 줄 높이가 달라지는 원본. 파생 시 정규화 필수.

## 4. 파일 크기·힌팅·기능·글립 수

| 폰트 | 글립 수 | cmap | 파일 크기 | 힌팅 | GSUB 주요 기능 | GPOS | 비고 |
|---|---|---|---|---|---|---|---|
| Pretendard OTF / TTF / VF | 14,716 / 14,716 / 14,757 | 14,336 | 1.45–1.60 MB / 2.6–2.9 MB / 6.6 MB | CFF BlueValues 만, TTF·VF 는 무힌팅(fpgm 없음) | calt case ccmp clig cv01–13 dlig frac locl pnum tnum ss01–16 subs sups zero fwid pwid | cpsp kern mark mkmk | 가나 184자 포함(M PLUS 1p 기반), 한자 없음 |
| SourceHanSansKR OTF | 24,973 | 23,185 | 4.1–5.0 MB | CFF 힌트 | aalt calt ccmp dlig fwid hwid pwid liga **ljmo vjmo tjmo** locl ruby vert vrt2 | halt kern mark palt vert vkrn | 한자 8,139자·가나 189자 포함, CID-keyed, BASE/vhea/vmtx |
| NotoSansKR OTF / GF VF | 24,964 | 23,174 | 4.2–5.0 MB / 10.4 MB | CFF 힌트 / VF 무힌팅 | SHS 와 동일(ljmo/vjmo/tjmo) | 동일 | VF 는 glyf+gvar, STAT 9 값 |
| SpoqaHanSansNeo OTF | 44,007 | 44,647 | 12.3–12.9 MB | CFF 힌트 | (GSUB 피처 없음) | kern | 일본어 한자·가나 포함 → 무거움 |
| GothicA1 TTF | 22,709 | 14,719 | 2.2 MB | TT 힌팅(fpgm/prep/cvt) | aalt nalt | kern | 한자 포함 |
| IBMPlexSansKR | 12,283 | 12,183 | OTF 0.8–1.05 MB / TTF 2.5 MB | CFF 힌트 / TTF 무힌팅 | ccmp liga salt ss01–04 fwid pwid vert | kern | |
| WantedSans | 12,660 | 12,032 | OTF 1.3 MB / TTF 2.3 MB / VF 4.6 MB | 무힌팅 | calt case ccmp cv01–22 ss01–16 tnum … | kern mark | |
| SUIT | 11,460 | 11,437 | OTF 0.34 MB / VF 1.5 MB | — | aalt fwid pnum ss01 ss17 ss18 tnum … | kern | 한글 대부분 빈 글립이라 작음 |
| Inter | 2,937 | 2,852 | TTF 0.4 MB / OTF 0.6 MB / VF 0.86 MB | 정적 TTF 힌팅 있음, VF 무힌팅 | calt case ccmp cv01–14 ss01–08 tnum pnum zero … | cpsp kern mark mkmk | |
| NotoSans (LGC) VF | 4,515 | 3,094 | 2.0 MB | 무힌팅 | 다수(smcp c2sc onum …) | kern mark mkmk | |
| SourceSans3 VF | 2,478 | 1,615 | TTF 0.63 MB / OTF(CFF2) 0.53 MB | 무힌팅 | smcp c2sc cv01–19 ss01–10 … | kern mark mkmk size | |

## 5. 후보별 요점 (근거 포함)

### Pretendard 1.3.9 — 한글 1순위
- 원본 구성이 name ID 9 에 명시: "Base glyphs from Inter by Rasmus Andersson; Hangeul glyphs from Noto Sans CJK(Source Han Sans) …; Kana glyphs from M PLUS 1p …; Combined and redesigned to Pretendard by Kil Hyung-jin." (`name-tables.md`)
- 9 웨이트 + 변수(wght 45–930, 9 인스턴스, STAT 정합) + OTF/TTF 동시 제공 → 우리가 원하는 출력 형식 대부분이 이미 존재.
- 이미 한글·라틴 조화(높이·진행폭·수직 메트릭 정규화, USE_TYPO 설정)가 끝난 상태. 방식 B(직접 병합)로 같은 품질을 재현하려면 상당한 튜닝 필요.
- 결손: 옛 호환자모 41자(U+3165–318E), 첫가끝 자모 전부(256+29+72), KS 기호 6자(∠ ∴ ◎ ㉠ ㉡ ㉢), ŉ(U+0149, 유니코드 폐기 권고 문자). 모두 Source Han Sans/Noto Sans KR(동일 골격)에서 보충 가능.
- 리스크: 마지막 릴리스 2023-11(저장소는 2026-07 까지 활동, 태그는 v1.3.9 가 최신). 라이선스는 누적 RFN 4개(02 문서).

### Source Han Sans KR 2.005R / Noto Sans KR 2.004 — 2순위·보충
- 자모 완비 + `ljmo/vjmo/tjmo` 로 옛한글 조합까지 지원. KS X 1001 기호 전량. Latin-1·스페인어 완비.
- Latin Ext-A 는 30/128(KS X 1001 수록분만) → 중앙유럽 라틴은 Source Sans 3 등에서 보충해야 함. 그리스 악센트 7자 결손.
- 정적은 CFF 만(TTF 없음). Google Fonts 의 `NotoSansKR[wght].ttf` 는 glyf 변수 TTF(10.4 MB)이며 `fontTools.varLib.instancer` 로 100–900 임의 웨이트 인스턴스 생성 가능 → **Pretendard 결손 보충용으로 최적**(Pretendard 의 Thin 100 ~ Black 900 과 1:1 매칭).
- 파일이 큼(한자 8k 포함) → 서브셋 필수.

### Gothic A1 2.50 — 3순위
- 측정 집합 중 자모확장 A/B 만 빼고 전부 보유(Latin Ext-A 128, 그리스·키릴, KS 기호 79 전량). 9 웨이트, TT 힌팅.
- 그러나 2017 이후 갱신 없음, 변수 폰트 없음, OpenType 기능 빈약(aalt/nalt/kern), UPM 1024, 한양 계열 고딕 특유의 인상·라틴 품질은 Inter 급이 아님.
- RFN 이 선언돼 있지 않아 이름 제약은 가장 느슨.

### 제외 사유 요약
- **IBM Plex Sans KR**: 라틴 악센트 전무(스페인어 3/21), 800/900 없음 → 라틴을 Plex Sans 에서 병합해야 하며 이점이 없음.
- **Spoqa Han Sans Neo**: 5 웨이트, 2021 이후 갱신 없음, 12 MB/웨이트(일본어 포함), LICENSE 에 원본(Adobe/Google, Lato) 고지 미포함, GSUB 피처 없음.
- **나눔바른고딕·나눔스퀘어 네오**: OFL 원문을 1차 출처에서 확인 못 함(폰트 내부 라이선스 필드 없음/`NHN Corporation`, fsType=8), 스페인어 악센트 전무, 웨이트 부족. Nanum Gothic 은 OFL 이나 3 웨이트·라틴 부족.
- **Wanted Sans**: 400–1000 만 존재(Thin/Light 없음), 그리스·키릴 없음, hhea/typo 불일치.
- **SUIT**: cmap 은 11,172 를 모두 가리키지만 8,504 글립이 비어 있음(2,668자만 실제 외곽선). 빈 글립은 폴백도 일어나지 않아 위험. fsType=4(Preview & Print) 도 OFL 과 상충.
- **Freesentation**: 라틴이 Roboto(Apache-2.0) 파생 → AGENTS §5.1 위배. **Paperlogy**: Gmarket Sans 기반 기하학적 디스플레이체 → 본문용 중립성 기준 미달(라이선스 사슬은 OFL 로 표기돼 있으나 검증 안 함).

## 6. Google Fonts 한국어 슬라이싱 실측 (03 문서에 상세)
`docs/research/google-kr-slices.css` — Noto Sans KR 변수 요청 시 **@font-face 124 블록**, 전체 WOFF2 합계 3,519,780 bytes, 슬라이스당 17–56 KB, 한글 포함 슬라이스 84개(슬라이스당 한글 13–155자).
