# 04 — OpenType 기능(GSUB/GPOS/GDEF)·셰이핑 스펙 (JennySans)

> 소유: font-architect · 상태: **P2 2차 — Pretendard 1.3.9 실측 반영(2026-09-06)**. 실측: `charset/scripts/measure_sources.py`.
> 원칙: **Pretendard 의 GSUB/GPOS/GDEF 를 그대로 보존**한다. 새 기능을 만들지 않고, 서브셋으로 깨뜨리지 않는다. **Noto 유래 이식 글립에는 Noto 의 룩업을 가져오지 않는다.**

## 1. 실측 기능 목록 (Pretendard-Regular.ttf = 전 정적 웨이트 동일; VF 는 `rlig` 1개 추가)

| 테이블 | 태그 | 스크립트/언어 |
|---|---|---|
| GSUB (83 룩업) | `aalt calt case ccmp clig cv01 cv02 cv03 cv04 cv05 cv07 cv08 cv09 cv10 cv11 cv12 cv13 dlig dnom frac fwid locl numr ordn pnum pwid salt sinf ss01 ss02 ss03 ss05 ss06 ss07 ss08 ss10 ss11 ss12 ss13 ss14 ss15 ss16 subs sups tnum zero` (46) — VF 에 `rlig` 추가(88 룩업) | `DFLT`, `latn` (`CAT MOL ROM`; VF 는 `CAT ROM`) |
| GPOS (26 룩업) | `cpsp kern mark mkmk` | `DFLT`, `latn` (`CAT MOL ROM`; VF `latn` 언어 없음) |
| GDEF | GlyphClassDef ✓, MarkGlyphSetsDef ✓, MarkAttachClassDef ✗ | |

- `hang` 스크립트 없음(한글은 셰이핑 기능 불필요). `fwid/pwid` 는 전각↔비례폭 전환(Pretendard 의 전각 컴포지트). `cv01–cv13`·`ss01–ss16` 의 UI 이름은 name ID 274+ 에 있음("Straight-sided six and nine", "Open four", "Vertically centered colon", "Korean localization", "High legibility", "One storey a" …) → **보존·재매핑 필수**(§2).
- Noto Sans KR VF 의 기능(`ljmo tjmo vjmo vert vrt2 ruby hist palt halt vpal vhal vkrn …`)은 **가져오지 않는다**(AGENTS §8: 옛한글 조합 범위 밖; 세로쓰기 범위 밖).

## 2. 보존 원칙과 서브셋 규칙 (빌더)

- `fontTools.subset` 옵션: `--layout-features='*'` `--layout-scripts='*'` `--glyph-names` `--notdef-outline` `--notdef-glyph` `--recommended-glyphs` `--name-IDs='*'` `--name-languages='*'` `--recalc-bounds` `--recalc-average-width` `--recalc-max-context` `--drop-tables+=DSIG`. 레이아웃 클로저(기본 on)로 GSUB 도달 글립(`.numr/.dnom` PUA 부품, `ss##` 대체형, 전각 컴포지트 부품)이 자동 포함된다.
- 서브셋 대상 코드포인트 = required ∪ (recommended ∩ 원본) ∪ (korean-old ∩ 원본). Pretendard 의 가나(U+3041–30F6 등 M PLUS 유래 184자)·한자·기타 범위 밖 글립은 서브셋으로 빠진다. **단 `.notdef`·`space`·PUA 부품(uniE0xx)** 은 클로저로 남는다 — 남지 않으면 빌드 FAIL.
- 이식 글립(908)은 서브셋 **후** 추가하고, 어떤 GSUB/GPOS 룩업에도 넣지 않는다(커닝·mark 없음). 예외: ⅔(U+2154)은 `frac` 관련 룩업에 넣지 않아도 되며(프리컴포즈 글립), Pretendard 의 `frac` 룩업이 `2/3` 시퀀스를 자체 처리하는지는 QA 확인 항목.
- name 테이블 전면 교체 시 **GSUB FeatureParams(cv/ss UI 이름)·STAT·fvar 가 참조하는 ID ≥256** 을 수집 → 문자열 보존 → 새 ID 로 재매핑 → 참조 갱신. Pretendard VF 실측: 인스턴스명 257–272, STAT "Italic" 273, cv/ss 이름 274–279+ (mac·win·ko 4중 레코드) → **보존은 Windows(3/1) 레코드로만** 한다(Mac 플랫폼 레코드 미기록, `02-naming.md` §2-2).
- 글립 이름에 원본 RFN 문자열이 있으면(`post` 2.0) 제거·정규화. Pretendard 글립명은 `uniXXXX`/AGL 이름이라 해당 없음 예상(QA 검색).
- **고아 글립 제거(8차 도입, QA 티켓 11)**: 서브셋·평탄화·분해가 끝난 뒤 `reachable_glyphs()` = cmap(UVS 포함) ∪ GSUB/GPOS/GDEF/MATH/BASE/JSTF 객체 트리에 등장하는 이름 ∪ 컴포넌트 폐포 ∪ 예약 글립(`.notdef` `.null` `nonmarkingreturn` `CR`) 을 계산해 그 밖의 글립을 제거한다. fontbakery 는 룩업의 *출력*만 도달로 보지만 우리는 입력·클래스·앵커까지 도달로 인정해 **더 보수적**이다. 8차 제거 실적: 정적 9종 각 4개(`casedieresis.cn` `casetilde.cn` `tonos` `uniE118`), VF 6개(+`uni0189` `cyrillictic.cn` — 변환 컴포넌트 분해의 부작용). `.null` 은 서브세터 `--recommended-glyphs` 정책상 남긴다.
- 결과 규모(8차 실측): 정적 9종·VF 모두 **글립 13,980 · cmap 13,254**.

### 2-1. 서브셋 후 사라져도 되는 피처 (GSUB 룩업 실측, 2026-09-06)

| 피처 | 원본 내용(실측) | 서브셋 후 | 판정 |
|---|---|---|---|
| `ss16` (정적·VF, 룩업 67/63, 단일치환) | 글립 6개: `uF0001`·`uF0002`(보조 PUA-A U+F0001–F0002 아이콘) ↔ `iconDot.fill.large/small`, `iconDot.large/small` — Pretendard 의 **PUA 아이콘 전용** | 참조 글립이 전부 빠져 피처 제거 | **사라져도 됨**(우리 문자집합과 무관) |
| `rlig` (VF 만) | FeatureRecord 에 **룩업 0개(빈 피처)** | 제거 | **사라져도 됨** |
| `ss14`·`ss15` (룩업 65/66) | 554글립: U+1F130–1F189 사각·원 라틴(Enclosed Alphanumeric Supplement, 범위 밖), U+F021 등 PUA, 24BC 등 원문자 일부 + `.squared.medium` 대체형 | 우리 문자집합 해당 58글립 분만 남아 **축소된 채 잔존** | 정상(빈 룩업 아님) |
| `salt` (룩업 11/12) | 194글립 중 PUA(uniE0xx 부품)·Latin Ext Additional 다수 | 39글립 분 잔존 | 정상 |
| `aalt` (룩업 0, 대체집합) | 1,215글립(PUA·`.squared.medium` 등 포함) | 축소 잔존 | 정상 |
| `calt`·`clig` (룩업 14–21) | 가나 184글립 포함 문맥 룩업 | 가나 제거분만 축소 | 정상 |

- 위 표 밖의 피처가 사라지면 빌드 FAIL. 빌더 `verify_build.py` 의 "사라진 피처" 목록은 `{ss16}`(정적) / `{ss16, rlig}`(VF) 만 허용.

**QA 합격 기준**: 서브셋 후 GSUB/GPOS `FeatureList` 태그 집합 = 원본 − {`ss16`}(정적) / − {`ss16`, `rlig`}(VF) — 즉 정적 GSUB 45 + GPOS 4 = **49**, VF 동일 49; 빈 룩업/빈 피처 0; cv/ss FeatureParams UINameID 가 name 에 존재(en+ko); fontbakery `layout_valid_*`·`gdef_*`·`unreachable_glyphs` PASS.

## 3. 기능별 정책 (Pretendard 보유분 그대로)

| 태그 | 정책 | 기본 상태 | QA |
|---|---|---|---|
| `kern` (GPOS PairPos, 라틴) | 유지 | 켜짐 | `AV` `To` `Ya` `¿Q` 쌍 x-advance 합 ≠ 개별 합 |
| `mark` `mkmk` | 유지 | 켜짐 | `n`+U+0303 → 합성 ñ 또는 mark 배치(y>0), gid 0 없음 |
| `ccmp` `clig` `calt` `rlig`(VF) | 유지 | 켜짐 | |
| `liga` | **없음**(Pretendard 는 `clig/dlig` 만) | — | fi/fl 리거처 없음 — 문서화 |
| `dlig` | 유지 | 꺼짐 | |
| `case` `cpsp` | 유지 | 꺼짐(앱이 켬) | `case` 시 `¿` 글립 변경 |
| `locl` | 유지 (`latn`: CAT ŀ·MOL/ROM ş→ș) | 켜짐(lang) | ROM 태그로 `ş` 셰이핑 시 콤마형 글립 |
| `frac` `numr` `dnom` | 유지 (PUA 부품 uniE0Bx/uniE0Cx/uniE0Dx) | 꺼짐 | `1/2` → ½ 형 |
| `sups` `subs` `sinf` `ordn` | 유지 | 꺼짐 | `ordn`: `1a` → 상첨자 a |
| `pnum` `tnum` | 유지 | §4 | |
| `lnum` `onum` | **없음** | — | 라이닝만 |
| `zero` | 유지 | 꺼짐 | |
| `salt` `ss01–ss16` `cv01–cv13` | 유지 + UI 이름(en·ko) 보존 | 꺼짐 | FeatureParams 이름 존재 |
| `fwid` `pwid` | 유지 | 꺼짐 | 전각 컴포지트 ↔ 비례폭 |
| `aalt` | 유지 | 꺼짐 | |
| `vert/vrt2/palt/halt/chws/ljmo/vjmo/tjmo` | 없음(만들지 않음) | — | fontbakery `cjk_chws_feature` WARN → 사유 기록 |
| `smcp c2sc titl` | 없음 | — | |

## 4. 숫자 형태 정책

- Pretendard 는 `pnum` 과 `tnum` 을 둘 다 갖는다(Inter 유래). **기본 = 프로포셔널 라이닝(a) — 실측 확정**: Regular `0–9` advance [1220, 898, 1202, 1264, 1278, 1222, 1256, 1130, 1242, 1256](9종 상이), Bold [1352, 960, 1250, …](9종 상이). 따라서 표에는 `font-variant-numeric: tabular-nums`(`tnum`)를 안내(`05-web.md` §5-4 반영).
- 전각 숫자 `０–９`(U+FF10–FF19)는 Pretendard 전각 컴포지트(adv 1920 고정).

**QA 합격 기준**: 기본 상태 판정 기록; `tnum` 켰을 때 10자 advance 동일; `pnum` 켰을 때 서로 다름; 전각 숫자 adv 1920 동일.

## 5. 한글 관련 특이사항

1. 완성형 11,172자 cmap 1:1, 셰이핑 기능 없음. HarfBuzz `hangul` 셰이퍼가 자모 시퀀스 L+V(+T)를 완성형으로 합성 → NFD 텍스트 정상. 이식 자모 256자는 단독 표시용(옛한글 시퀀스는 나란히 찍힘 — `07-supplement.md` §4-1).
2. 호환 자모 94자 단독 글립(Pretendard 53 + Noto 이식 41), adv 1770.
3. 한글 advance 1770 고정, 웨이트 무관.
4. **U+005C 백슬래시**: Pretendard `backslash` 글립은 백슬래시 형태(bbox 30..654 × −218..1516, adv 684) — 원 기호 아님 ✓. 그대로.
5. 전각 형식 FF01–FF5E·FFE0·FFE1·FFE5·FFE6 은 Pretendard 가 **라틴 글립을 1920 셀에 센터링한 컴포지트**로 만든다(＾=asciicircum@508, ￠=cent@418, ￦=uni20A9@28). ￢ ￣ 도 같은 방식으로 합성(`07-supplement.md` §4-11).
6. ZWJ/ZWNJ/ZWSP 는 셰이퍼가 기본 무시 — recommended.
7. `.notdef` gid 0 외곽선 유지(Pretendard 것).
8. GDEF: 결합문자 class 3(mark) ✓, 스페이싱 악센트(¨ ´ ¸ ˆ ˇ ˘ ˙ ˚ ˛ ˜ ˝ ː)는 class 1·advance > 0 — fontbakery `legacy_accents` 확인.

## 6. 라틴·스페인어 특이사항
- `¿ ¡` 기본형은 베이스라인 아래(questiondown bbox −384..1096) ✓, `case` 로 상향형.
- `ñ ü á é í ó ú ª º « » ‹ › € ¿ ¡` 전부 Pretendard 보유(라틴-1 96/96). 결합문자 13개 보유(mark/mkmk).
- 터키어 `İ ı` 프리컴포즈 보유; `locl TRK` 는 없음(대소문자 변환은 앱 몫).
- 폴란드어·체코어 등 Ext-A 127/128 보유(ŉ 제외). `Ľ ľ ď ť` 캐런 형태는 QA 렌더로 확인(fontbakery `alt_caron` WARN 시 기록).
- 그리스 56·키릴 96 (Inter 유래) 보유 — required 승격분 전부 Pretendard 에 있음(`count.py --font` 실측).

**QA 합격 기준**: 게이트 2 — HarfBuzz (a) 11,172자 (b) `¿Qué tal, señor? ¡Año nuevo! Ñandú, pingüino, 1ª 2º, 12,50 €` (c) 결합 시퀀스 5종 (d) pl·cs·tr·de·ro(Ș ș)·el·ru 샘플 → gid 0 **0건**.

## 7. 스크립트·언어 시스템
- 유지: `DFLT`, `latn`(`CAT MOL ROM`). 새 언어 시스템 추가 없음. 이식 글립은 어느 스크립트 룩업에도 속하지 않음.

## 8. 갱신 이력
- 2026-09-06: Pretendard 실측 기능 목록(46+4)·언어 시스템·PUA 부품·전각 컴포지트 구조 반영, Noto 룩업 미이식 원칙, `liga/lnum/onum` 없음 명시.
