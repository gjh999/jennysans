# 03 — 메트릭·OS/2·head·hhea·post 스펙 (JennySans)

> 소유: font-architect · 상태: **P2 2차 — Pretendard 1.3.9 실측 반영(2026-09-06)**. 실측: `charset/scripts/measure_sources.py`(Pretendard-Regular/Bold.ttf·PretendardVariable.ttf·NotoSansKR[wght].ttf).
> 원칙: 글립 외곽선과 Pretendard 의 수직 메트릭을 유지하고, 테이블 간 정합·웨이트 간 동일성만 강제한다(AGENTS §4-5, §8).

## 1. UPM

| 항목 | 값 |
|---|---|
| `head.unitsPerEm` | **2048** (Pretendard 실측; 정적·VF 동일) |
| 규칙 | 전 웨이트·변수·WOFF2 동일. 보충 글립(Noto UPM 1000)은 `07-supplement.md` 규칙으로 2048 좌표계로 변환해 넣는다 |

**QA 합격 기준**: 전 파일 `unitsPerEm == 2048`, fontbakery `opentype/unitsperem` PASS.

## 2. 수직 메트릭 (팀장 결정: typo = hhea = win = 1950 / −494 / 0 + USE_TYPO_METRICS)

| 테이블.필드 | 값 | 실측 근거 |
|---|---|---|
| `OS/2.sTypoAscender` | **1950** | Pretendard VF 1950(정적 OTF/TTF 는 1949 → 1950 으로 정정, AGENTS §8) |
| `OS/2.sTypoDescender` | **−494** | 동일 |
| `OS/2.sTypoLineGap` | **0** | 동일 |
| `hhea.ascent` / `descent` / `lineGap` | **1950 / −494 / 0** | Pretendard 정적·VF 모두 1950/−494/0 |
| `OS/2.usWinAscent` / `usWinDescent` | **1950 / 494 — 확정(AGENTS §8 2026-09-06)** | Pretendard 정적 1949/494 → 1950. 전 글립 yMax 최대는 head.bbox 기준 Regular 2172·Bold 2214(라틴 악센트 대문자 등) > 1950 → Windows 에서 해당 글립 상단이 잘릴 수 있으나 **Pretendard 와 동일한 상태**. fontbakery `family/win_ascent_and_descent` 의 FAIL/WARN 은 **문서화된 승인 예외**(팀장 결정) — QA 보고서에 예외 항목으로 기록하고 게이트 FAIL 로 세지 않는다 |
| `OS/2.fsSelection` bit 7 USE_TYPO_METRICS | **1** | Pretendard 0xC0(REGULAR+USE_TYPO) |
| 보충 글립 | 괘선·블록은 정확히 [−494, 1950] 에 맞춤(`07-supplement.md` §4-5); 그 외 이식 글립 yMax ≤ 1950 확인 | |
| `vhea`/`vmtx`/`VVAR`/`VORG` | **명시적으로 제거**(전 파일) | 세로쓰기 미지원. 실측: 원본 **Pretendard-Thin/ExtraLight/Light 3종이 `vhea`·`vmtx` 를 갖고 있어** 6차까지 그 3 웨이트에만 실려 웨이트 간 비대칭이 있었다(QA 티켓 9) → 8차에서 `fontutil.DROP_TABLES_EXTRA` 로 **9 웨이트·VF 전부에서 제거**(웨이트당 약 54 KB 감소). Noto 의 세로 테이블도 가져오지 않는다 |

- 줄높이 = (1950 + 494 + 0) / 2048 = **1.193 em**. CSS `line-height: normal` 이 1.19; 한국어 본문은 1.5–1.7 권장(`05-web.md`).
- 한글·라틴 조화는 Pretendard 가 이미 맞춘 상태(가 bbox −162..1616, H 0..1448, x-height 1086) — 외곽선을 만지지 않으므로 그대로.

**QA 합격 기준**: 전 파일(정적 9·VF·WOFF2)에서 7개 값 동일(1950/−494/0, 1950/494), USE_TYPO_METRICS=1, fontbakery `family/vertical_metrics`·`os2_metrics_match_hhea`·`linegaps` PASS. **승인 예외**: `family/win_ascent_and_descent` 의 FAIL/WARN(yMax 2172/2214 > 1950)은 AGENTS §8(2026-09-06) 결정으로 허용 — QA-REPORT "승인 예외" 절에 검사 ID·실측 yMax·결정 일자를 적고 게이트 3(fontbakery FAIL 0) 집계에서 제외한다. 렌더: 같은 문장 100/400/900 세 줄의 줄 간격 픽셀 동일.

## 3. 수평 메트릭

| 항목 | 값·규칙 | 실측 |
|---|---|---|
| 한글 음절 advance | **1770** 고정(11,172자 전부, 전 웨이트) | Pretendard `hmtx` 집합 {1770} 확인 |
| 호환 자모 advance | 1770 | 집합 {1770} |
| 보충 자모(1100–11FF·Ext-A/B) | 1770 (Noto 920 × 1.9239) | `07-supplement.md` §4-1 |
| 공백 | U+0020·U+00A0 같은 글립 `space`, adv 514(R)/472(B) — 웨이트별 상이 허용 | Pretendard 실측 |
| `hhea.advanceWidthMax`·`minLSB`·`minRSB`·`xMaxExtent` | 서브셋·이식 후 재계산 | |
| `OS/2.xAvgCharWidth` | 재계산(`opentype/xavgcharwidth`) | Pretendard 1693(R) — 서브셋 후 변동 |
| `post.isFixedPitch` | 0 | |

**QA 합격 기준**: `whitespace_widths`·`whitespace_ink`·`xavgcharwidth`·`opentype/monospace` PASS; 한글 11,172 + 이식 자모 400 의 advance 전부 1770.

## 4. OS/2 테이블 (Pretendard 실측 → 우리 값)

| 필드 | Pretendard(R/B) | JennySans 값 | 비고 |
|---|---|---|---|
| `version` | 4 | **4** | |
| `usWeightClass` | 400/700 | 100…900 (`01-family.md` §2); VF 400 | `opentype/weight_class_fvar` |
| `usWidthClass` | 5 | 5 | |
| `fsType` | 0 | **0** | 전 파일 |
| `fsSelection` | R 0xC0 / B 0xA0 | REGULAR(bit6, Regular·비RIBBI 7종·VF) / BOLD(bit5, Bold) · USE_TYPO(bit7)=1 · **WWS(bit8)=1 추가** · ITALIC/OBLIQUE 0 → Regular 0x1C0, Bold 0x1A0, 나머지 0x1C0 | Pretendard 는 WWS 미설정; ID 21/22 생략 근거로 세운다 |
| `achVendID` | `CTUS` | **`JNSF`** | |
| `ulUnicodeRange1–4` | 0xE10002FF, 0x13D7E5FF, 0x04000011, 0x00100000 | **cmap 기준 재계산**(`fontTools` `recalcUnicodeRanges`) — 이식으로 Hangul Jamo(bit 28)·Box Drawing(42)·Block Elements(43)·Enclosed CJK(54) 등이 추가됨 | |
| `ulCodePageRange1–2` | 0x2008019F, 0 (bit 0·1·2·3·4·7·8·19·29) | **규칙(AGENTS §8 채택, 빌더 실측 기준)**: Python `codecs` 로 코드페이지의 인쇄 문자를 디코딩해 cmap 과 대조. (a) 단일바이트 cp1252(0)·cp1250(1)·cp1251(2)·cp1253(3)·cp1254(4)·cp1257(7)·MacRoman(29): 누락 ≤ 2 이면 세트(Pretendard 선례 — cp1253·MacRoman 은 각 2자 누락에도 세트; 빌더 실측 Regular: 0/0/0/2/0/0/2). (b) 한국어 cp949(19)·Johab cp1361(21): **한자(행42–93)·가나(행10–11) 를 제외**한 12,086자 중 누락 ≤ 8 이면 세트(실측 누락 5 → 세트; Pretendard 도 한자 없이 세움). (c) cp1258 베트남어(8): Pretendard 는 세웠으나 우리는 **해제**(베트남어 범위 밖·cp1258 필수 문자 다수 누락). 그 외 비트 0 | `opentype/code_pages` |
| `sxHeight` / `sCapHeight` | 1086 / 1448 (R·B 동일) | **1086 / 1448** (웨이트별 실측값 유지 — Pretendard 는 전 웨이트 동일) | |
| `sTypo*` / `usWin*` | §2 | §2 | |
| `yStrikeoutSize` / `Position` | 139/652 (R), 188/652 (B) | Pretendard 웨이트별 값 유지 | |
| `ySubscript*` / `ySuperscript*` | 1330·1230·0·155 / 1330·1230·0·715 | 유지(전 웨이트 동일) | |
| `usDefaultChar` / `usBreakChar` | 0 / 32 | 0 / 32 | |
| `usMaxContext` | 12 | 재계산 | |
| `usFirstCharIndex` / `usLastCharIndex` | 0x20 / 0xFFFF | 재계산(0x20 / 0xFFFF) | |
| `panose` | [2,0,5,3,0,0,0,2,0,4] (R) / [2,0,8,3,0,0,0,2,0,4] (B) / VF [2,0,0,3,…] | §5 | |

**QA 합격 기준**: 전 파일 표와 일치; `opentype/fsselection`·`opentype/mac_style`·`opentype/code_pages`·`opentype/weight_class_fvar`·`opentype/family/panose_familytype` PASS; `fsType == 0`.

## 5. Panose

| 바이트 | Pretendard | JennySans |
|---|---|---|
| bFamilyType | 2 | **2** |
| bSerifStyle | 0 (Any) | **11** (Normal Sans) — 원본은 Any; 명시로 개선 |
| bWeight | 5(R)/8(B)/0(VF) | Thin 2·ExtraLight 3·Light 4·Regular 5·Medium 6·SemiBold 7·Bold 8·ExtraBold 9·Black 10 / **VF 5** |
| bProportion | 3 | **3** (9 금지) |
| bContrast | 0 | 0 |
| bStrokeVariation | 0 | 0 |
| bArmStyle | 0 | 0 |
| bLetterform | 2 | 2 |
| bMidline | 0 | 0 |
| bXHeight | 4 | 4 |

**QA 합격 기준**: bFamilyType 2·bSerifStyle 11·bProportion 3 전 파일, bWeight 웨이트 순 단조 증가, VF bWeight 5.

## 6. head 테이블

| 필드 | Pretendard | JennySans |
|---|---|---|
| `fontRevision` | 1.309 | **1.0** (name ID 5 "Version 1.000") |
| `flags` | 0x0003 | **0x0003** (bit 0·1; 무힌팅이므로 bit 3 = 0) |
| `macStyle` | R 0 / B 1 | Bold 만 bit 0; 그 외 0 |
| `unitsPerEm` | 2048 | 2048 |
| `xMin/yMin/xMax/yMax` | R (−1494,−602,5460,2172) | 재계산(서브셋·이식 후) |
| `lowestRecPPEM` | 7 | 7 |
| `created/modified` | — | 빌드 시각(`SOURCE_DATE_EPOCH` 지원) |

**QA 합격 기준**: `opentype/font_version` PASS(ID 5 ↔ 1.0), `family/equal_font_versions` PASS, macStyle 표와 일치.

## 7. hhea·post·기타 테이블

| 테이블.필드 | Pretendard | JennySans |
|---|---|---|
| `hhea.caretSlopeRise/Run/Offset` | 1/0/0 | 1/0/0 |
| `post.italicAngle` | 0 | 0 |
| `post.underlinePosition` / `Thickness` | **R −258/139, B −214/188 (웨이트별 상이)** | **전 파일 −258 / 139 로 통일** — fontbakery `opentype/family/underline_thickness` 가 패밀리 내 동일을 요구. 굵기별 밑줄 두께 차이는 앱이 무시하는 값이라 손실 없음 |
| `post.formatType` | 2.0 | 2.0(글립명 유지; 이식 글립은 `uniXXXX`) |
| `post.isFixedPitch` | 0 | 0 |
| `gasp` | 없음 | **추가**: 1 레코드 `0xFFFF → 0x000F`(무힌팅 TTF 권장값) |
| `DSIG` | 정적 TTF 에 있음 | **제거** |
| `GDEF/GSUB/GPOS` | 있음 | `04-features.md` |
| `maxp` | 14716(정적)/14757(VF) | 재계산(서브셋 −가나·한자 등, +이식 908, −고아 글립) → **8차 실측 13,980**(정적 9종·VF 동일), cmap 13,254 |
| `cvt`/`fpgm` | 없음 | 없음(무힌팅 유지) |
| `prep` | 없음 | **추가**: `PUSHW[] 511 SCANCTRL[] PUSHB[] 4 SCANTYPE[]` — 스마트 드롭아웃 제어(gftools `fix-nonhinting` 과 동일 프로그램). 6차 빌드에서 QA 티켓 4(`smart_dropout`) 대응으로 넣었다. 글립 힌팅이 아니라 래스터라이저 드롭아웃 정책만 지정하므로 무힌팅 원칙과 충돌하지 않는다. `gasp` 0x000F 와 함께 쓴다 |
| `meta` | 없음 | 선택 추가 `dlng=Kore, Latn` `slng=Kore, Latn, Grek, Cyrl` |
| `BASE` | 없음 | 없음(Noto 의 BASE 는 가져오지 않음) |

**QA 합격 기준**: `unwanted_tables`·`required_tables`·`post_table_version`·`family/underline_thickness`·`caret_slope`·`italic_angle`·`smart_dropout` PASS. 추가로 전 파일(정적 9·VF·WOFF2)에서 **`vhea`·`vmtx`·`VVAR`·`VORG` 가 존재하지 않고**(FAIL 기준), **`prep` 프로그램이 위 4 명령과 바이트 일치**하며, `cvt`/`fpgm` 은 없다.

## 8. 변수 폰트 (PretendardVariable 실측 기반)

| 항목 | Pretendard VF | JennySans Variable |
|---|---|---|
| 축 | `wght` 45 / 400 / 930, avar 없음 | **`wght` 100 / 400 / 900 — 확정**(AGENTS §8 2026-09-06; L4 부분 인스턴싱 `instantiateVariableFont(vf, {"wght": (100, 900)})`, `07-supplement.md` §7-2) |
| 인스턴스 | 9 (100…900, PS `PretendardVariable-<W>`) | 9 (`01-family.md` §6) |
| STAT | v1.1, 축 wght + **ital**(Format 3 0→1), 값 10 + Regular F3 400→700 | 축 **wght 만**, 값 9 (Regular Format 3 400→700 elidable), ElidedFallbackNameID → "Regular" |
| 테이블 | GDEF GPOS GSUB OS/2 STAT cmap fvar glyf gvar head hhea hmtx loca maxp name post — **HVAR·MVAR 없음** | 동일 구성. HVAR 없으므로 보충 글립 진행폭 변화는 gvar phantom 델타로(`07-supplement.md` §7-4). MVAR 없음 → 수직 메트릭 웨이트 불변 자동 충족 |
| OS/2 (기본 인스턴스) | wt 400, fsSel 0xC0, typo 1950/−494 | wt 400, REGULAR+USE_TYPO+WWS, 1950/−494/0, win 1950/494 |
| numGlyphs | 14757 | 서브셋 후 + 908 − 고아 → **13,980**(정적과 동일) |

**QA 합격 기준**: VF 를 100/400/900 으로 인스턴스화해 §2 값이 정적과 동일; fontbakery `opentype/varfont/*`(regular_wght_coord 400, bold_wght_coord 700, wght_valid_range, family_axis_ranges, STAT·fvar 정합) FAIL 0; `inconsistencies_between_fvar_STAT` PASS.

## 9. 보충원본(Noto Sans KR VF) 메트릭 — 참고(이식 계산에만 사용)
UPM 1000 · typo 880/−120/0 · hhea 1160/−288 · win 1160/288 · USE_TYPO 미설정 · sx 543 · cap 733 · 한글 adv 920 · 괘선 셀 0–1000 × −120–880. 이 값들은 우리 폰트에 들어가지 않는다.

## 10. 갱신 이력
- 2026-09-06: Pretendard/Noto 실측값 반영, 수직 메트릭 1950/−494/0 확정, underline 통일·gasp 추가·DSIG 제거·WWS 비트·Panose·codePage 규칙 확정, VF 축 100–900 권고.
