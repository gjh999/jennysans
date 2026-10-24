# 02 — 이름 테이블(name)·STAT·fvar 스펙 (JennySans)

> 소유: font-architect · 상태: **P2 2차 — 원본 확정·팀장 결정 ③④⑤·저작권 정본 반영(2026-09-06)**.
> 원칙: **원본 name 테이블은 전부 버리고 이 스펙대로 새로 쓴다**(빌더 `build_static.py`). 단 GSUB FeatureParams(cv/ss UI 이름)·fvar·STAT 가 참조하는 ID ≥ 256 문자열은 보존·재매핑(`04-features.md` §2). 원본 RFN 은 §6 규칙에 따라 고지 레코드(0·5·7·9·13) 외에는 어디에도 남지 않는다.

## 1. 플랫폼·인코딩·언어 레코드

| 플랫폼 | platformID/encodingID/languageID | 기록 대상 ID | 비고 |
|---|---|---|---|
| Windows 영어 | 3 / 1 / 0x0409 | 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,17 (+25 변수, +256… fvar/STAT/cv·ss 이름) | **필수** |
| Windows 한국어 | 3 / 1 / 0x0412 | 1,4,16 (+ cv/ss UI 이름의 ko 레코드 보존) | 현지화명 「제니산스」 |
| ~~Macintosh Roman 영어 (1 / 0 / 0)~~ | — | **기록하지 않음** | **6차 빌드에서 전부 제거**(QA 티켓 3 `no_mac_entries`, 2026-09-08). Pretendard 는 (1,0,0)·(1,3,35) 를 갖지만 우리는 **platformID 3 레코드만** 쓴다 — 현대 macOS·앱은 Windows 플랫폼 레코드를 읽으며, Mac 레코드는 중복·불일치 위험만 남는다(fontbakery 권고) |

- 앞뒤 공백·빈 레코드 금지. ID 10 에 저작권 문구 금지. (Mac 플랫폼 레코드를 쓰지 않으므로 Windows/Mac 문자열 일치 규칙은 해당 없음 — §2-2.)
- 버전 표기 규칙(AGENTS §8): 폰트 `1.000`(ID 5·head) ↔ git 태그 `v1.0.0` ↔ npm `1.0.0` (`X.YZZ ↔ X.Y.ZZ`).

## 2. 정적 폰트 name ID 값 (영문 0x409) — 확정 문자열

`<W>` = 스타일명, `<psname>` = `JennySans-<W>`.

| ID | 값 (Regular / Bold / Light 예) | 규칙 |
|---|---|---|
| 0 | §5 정본(5행, `\n` 구분) | 전 파일 동일. **1행이 LICENSE 1행과 한 글자도 다르지 않아야 함** |
| 1 | `JennySans` / `JennySans` / `JennySans Light` | Regular·Bold 만 `JennySans`; 그 외 `JennySans <W>` |
| 2 | `Regular` / `Bold` / `Regular` | |
| 3 | `1.000;JNSF;JennySans-Regular` 등 | `<ver>;JNSF;<psname>` |
| 4 | `JennySans Regular` / `JennySans Bold` / `JennySans Light` | 항상 `<ID16> <ID17>` |
| 5 | **`Version 1.000 (based on Pretendard 1.309; Noto Sans KR 2.004)`** | `Version d.ddd` 로 시작, `head.fontRevision` 1.0 과 일치. 괄호 안은 AGENTS §7 "(based on …)" — 고지 목적의 원본명 언급(§6 허용) |
| 6 | `JennySans-Regular` / `JennySans-Bold` / `JennySans-Light` | 파일 stem 과 동일 |
| 7 | **`JennySans is a trademark of JennySoft; Pretendard is a trademark of Kil Hyung-jin; Inter UI and Inter is a trademark of rsms; Source is a trademark of Adobe in the United States and/or other countries.`** | Pretendard 선례(원본 상표 고지 누적) |
| 8 | `JennySoft` | |
| 9 | **`Base glyphs from Inter by Rasmus Andersson; Hangeul glyphs from Noto Sans CJK (Source Han Sans) by Jang Soo-young and Kang Joo-yeon, Sandoll Communications; combined and redesigned as Pretendard by Kil Hyung-jin; supplementary Hangul jamo and symbol glyphs from Noto Sans KR (Adobe: Ryoko Nishizuka, Paul D. Hunt, Sandoll Communications); composed and engineered as JennySans by JennySoft.`** | 원본 디자이너 누적(Pretendard ID 9 + Noto KR ID 9 요약). 가나(M PLUS) 글립은 제외되므로 ID 9 에서는 생략(LICENSE 에는 유지 — `06-license.md`) |
| 10 | `JennySans is a general-purpose sans-serif type family for Korean (all 11,172 modern Hangul syllables and jamo), Latin (Western and Central European including Spanish), basic Greek and Cyrillic, and Korean document symbols (KS X 1001). Derived from Pretendard and Noto Sans KR under the SIL Open Font License 1.1; see LICENSE.` | |
| 11 | `https://font.jennysoft.co.kr` | |
| 12 | `https://jennysoft.co.kr` | |
| 13 | `This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org` | |
| 14 | `https://openfontlicense.org` | |
| 16 | `JennySans` | 전 웨이트 동일, 항상 기록 |
| 17 | `Regular` / `Bold` / `Light` | |
| 18, 19, 20, 21, 22 | 기록 안 함 | 21/22 는 `fsSelection.WWS=1` 로 대체 |
| 25 | 정적에는 기록 안 함 | |
| ≥256 | Pretendard 의 cv01–cv13·ss01–ss16 UI 이름(en 0x409 + ko 0x412 + mac) 재매핑 보존 | `04-features.md` §2 |

### 2-1. 한국어 레코드 (3/1/0x0412)

| ID | Regular | Bold | Light(비RIBBI 대표) |
|---|---|---|---|
| 1 | `제니산스` | `제니산스` | `제니산스 Light` |
| 4 | `제니산스 Regular` | `제니산스 Bold` | `제니산스 Light` |
| 16 | `제니산스` | `제니산스` | `제니산스` |

- ID 2/17 ko 는 기록하지 않는다(굵기명은 영문 유지; 앱이 현지화). 「제니고딕」으로 바뀌면 상수 하나만 치환.

### 2-2. Macintosh 레코드 — **없음**

`platformID 1` 레코드는 기록하지 않는다(6차 빌드에서 제거, QA 티켓 3). GSUB FeatureParams(cv/ss UI 이름) 보존도 Windows(3/1/0x409·0x412) 레코드로만 한다.

## 3. RIBBI style-linking 규칙 (AGENTS §4-4; Pretendard·Inter 관행과 동일)

| 폰트 | ID 1 | ID 2 | fsSelection | macStyle |
|---|---|---|---|---|
| Regular | JennySans | Regular | REGULAR(6)=1, USE_TYPO(7)=1, WWS(8)=1 → 0x1C0 | 0 |
| Bold | JennySans | Bold | BOLD(5)=1, USE_TYPO=1, WWS=1 → 0x1A0 | 0x1 |
| 나머지 7종 | JennySans `<W>` | Regular | 0x1C0 | 0 |

- ID 1 그룹당 ≤ 4개(`max_4_fonts_per_family_name`), (bold, italic) 유일. GDI 앱의 합성 굵게 한계는 설치 가이드에 안내.

## 4. 변수 폰트(JennySans Variable) — 팀장 결정 ③

### 4-1. name
| ID | 값 |
|---|---|
| 1 | `JennySans Variable` |
| 2 | `Regular` |
| 3 | `1.000;JNSF;JennySansVariable-Regular` |
| 4 | `JennySans Variable Regular` |
| 6 | `JennySansVariable-Regular` |
| 16 | `JennySans Variable` |
| 17 | `Regular` |
| 25 | `JennySansVariable` → 인스턴스 PS `JennySansVariable-<W>` |
| ko 1/4/16 | `제니산스 Variable` / `제니산스 Variable Regular` / `제니산스 Variable` |
| 0,5,7,8,9,10,11,12,13,14 | 정적과 동일(ID 5 도 동일 문자열) |

### 4-2. fvar (Pretendard VF 실측: 축 wght 45/400/930, avar 없음, 인스턴스 9)
- 축 1개 `wght`: **100 / 400 / 900 — 확정**(AGENTS §8 2026-09-06, 원본 45–930 을 L4 절단; `07-supplement.md` §7-2). axisNameID → `Weight`(en) / `굵기`(ko). Pretendard 의 축 이름 레코드(256)는 재작성.
- 명명 인스턴스 9: subfamilyNameID → `Thin`…`Black`(Regular 는 ID 2 재사용 가능), postscriptNameID → `JennySansVariable-<W>`. Pretendard 인스턴스 이름 레코드(257–272 "Pretendard…") 는 전부 교체.

### 4-3. STAT (변수·정적 모두)
- `Version 0x00010002`, `ElidedFallbackNameID` → "Regular".
- DesignAxis: **`wght` 1개만** — Pretendard VF 의 `ital` 축(Format 3 "Regular" 0→1, name ID 273 "Italic")은 **제거**(이탤릭 없음, `01-family.md` §3).
- AxisValue(변수): Thin 100·ExtraLight 200·Light 300(Format 1) · **Regular Format 3 (400 → LinkedValue 700, Flags 0x0002 ELIDABLE)** · Medium 500·SemiBold 600·Bold 700·ExtraBold 800·Black 900(Format 1). Pretendard 의 "Regular Format 1 + Format 3 중복" 은 Format 3 하나로 정리.
- AxisValue(정적): 그 파일의 값 1개(Regular 는 Format 3, 나머지 Format 1).

## 5. 저작권 문구(ID 0) — **정본**(AGENTS §8 2026-09-06)

```
Copyright (c) 2026 JennySoft (https://jennysoft.co.kr), with Reserved Font Names 'JennySans' and '제니산스'.
Portions Copyright (c) 2021, Kil Hyung-jin (https://github.com/orioncactus/pretendard), with Reserved Font Name 'Pretendard'.
Portions Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'.
Portions Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter), with Reserved Font Name 'Inter'.
Portions Copyright 2021 The M+ FONTS Project Authors (https://github.com/coz-m/MPLUS_FONTS), with Reserved Font Name 'M PLUS 1'.
```
- 1행 = `LICENSE` 1행(한 글자도 다르지 않게). 2–5행은 Pretendard 저장소 `LICENSE`(main) 의 저작권 줄 **원문에 `Portions ` 접두만** 붙인 것(줄 안의 개행은 한 줄로 합침). Adobe 줄은 Pretendard 경유분과 Noto Sans KR VF(ID 0 `(c) 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'.`) 직접 사용분을 함께 대표한다. M PLUS 줄은 가나 글립을 제외해도 **보수적으로 유지**(AGENTS §8).
- 5행을 `\n` 으로 이어 한 레코드에 넣는다. Adobe 의 상표 문장("Source is a trademark …")은 ID 7 에 있다.

## 6. 원본 RFN 잔존 금지 규칙 (AGENTS §4-8 보정 문구, 팀장 결정 ④)

| 위치 | 원본 RFN·원본명 |
|---|---|
| **식별 레코드**: name ID 1, 2, 3, 4, 6, 16, 17, 18, 21, 22, 25 · fvar 인스턴스명 · STAT 축/값 이름 · 글립명(`post`) · 파일명 | **금지** — 발견 시 FAIL |
| **고지 레코드**: ID 0(저작권), 5("based on"), 7(상표), 9(디자이너), 13 | **허용·유지 의무**(OFL 조건 2, Pretendard 선례) |
| ID 10(설명) | 원본명 언급 허용(파생 출처 설명) |

검색 문자열(대소문자 무시·부분 일치): `Pretendard`, `Source`, `Inter`, `M PLUS`, `MPLUS`, `Noto`, `Adobe`, `rsms`, `orioncactus`, `Plex`, `Spoqa`, `Nanum`, `SUIT`. 단 `Inter` 는 `International` 같은 단어 오탐이 가능하므로 단어 경계 검사.

## 7. 빌더 구현 메모
- name 전부 삭제 → 이 스펙 레코드 추가 → 보존 대상 ID ≥256(cv/ss UI 이름 en·ko·mac, 축·인스턴스 이름)을 새 번호로 추가하고 GSUB FeatureParams·fvar·STAT 참조를 갱신. 미사용 256+ 레코드는 남기지 않는다.
- 문자열 상수는 `tools/naming.py` 한 곳(패밀리명·현지화명·버전·ID 0/5/7/9/10 문자열).

## 8. QA 합격 기준
1. 정적 9 + 변수 1 + WOFF2 전부에서 §2·§2-1·§4-1 표와 **문자열 완전 일치**(덤프 자동 비교). ID 0 1행 == `LICENSE` 1행(바이트 비교). **§2-2: `platformID == 1` 레코드 수 0**(전 파일).
2. fontbakery universal name/STAT/fvar 검사 FAIL 0: `opentype/name/*`, `opentype/family/*`, `opentype/postscript_name`, `opentype/varfont/*`, `STAT_strings`, `STAT_in_statics`, `inconsistencies_between_fvar_STAT`, `name/family_and_style_max_length`, `name/trailing_spaces`.
3. §6 식별 레코드·글립명·파일명에 검색 문자열 0건; 고지 레코드에는 원본 고지 존재(ID 0 5행, ID 7 상표 4건, ID 9 크레딧).
4. Windows 설치 실측: DirectWrite 기준 패밀리 `JennySans` 1개·9 스타일(GDI 는 `JennySans`, `JennySans Light`… 그룹), `JennySans Variable` 별도 패밀리; macOS/브라우저 `font-weight: 100..900` 선택; 한글(HWP)·Word·Photoshop 목록에 「제니산스」 9 굵기(팀장 실화면, 게이트 4).
5. cv/ss FeatureParams UI 이름(en·ko)이 name 에 존재하고 참조 ID 가 유효(`04-features.md` §2).

## 9. 갱신 이력
- 2026-09-06: ID 0 정본·ID 5/7/9/10 확정, 변수 폰트명 "JennySans Variable", STAT ital 축 제거, RFN 규칙 보정, 버전↔태그 규칙.
