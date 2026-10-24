# 06 — 라이선스 메타데이터·고지 파일 스펙 (JennySans)

> 소유: font-architect · 상태: **P2 2차 — 원본 확정·저작권 정본 반영(2026-09-06)**. 원문 근거: `docs/research/02-licenses.md`, `sources/Pretendard/LICENSE-repo-main.txt`, `sources/NotoSansKR/OFL-googlefonts.txt`, 폰트 내부 name ID 0/7/9 실측.
> 상위 규칙: AGENTS §5·§4-8(보정본)·§8. 파일 작성은 release 소유이지만 **내용 규격은 이 문서**다.

## 1. 법적 구조

| 항목 | 값 |
|---|---|
| 라이선스 | SIL Open Font License 1.1. 원본 둘 다 OFL 1.1(Pretendard 저장소 LICENSE, Noto Sans KR GF OFL.txt) |
| 파생물 지위 | OFL "Modified Version" — 서브셋·이식·병합·이름 변경·메트릭/테이블 재작성 |
| 우리 저작권·RFN | `Copyright (c) 2026 JennySoft (https://jennysoft.co.kr), with Reserved Font Names 'JennySans' and '제니산스'.` — 팀장 결정 ⑤(RFN 2개) |
| 원본 RFN(누적 고지) | `Pretendard`(Kil Hyung-jin) · `Source`(Adobe; Pretendard 경유 + Noto Sans KR 직접) · `Inter`(Inter Project Authors) · `M PLUS 1`(M+ FONTS) — 우리 이름에 사용 금지, 고지에 유지. `Noto` 는 Google 상표(RFN 아님)이나 역시 미사용 |
| SPDX | `OFL-1.1-RFN` |
| 단독 판매 | 금지(OFL §1). 번들·임베드·웹폰트·상업 사용 허용 |

## 2. `LICENSE` 파일 규격 (저장소 루트·릴리스 zip 루트·npm 패키지 루트; UTF-8·LF)

```
Copyright (c) 2026 JennySoft (https://jennysoft.co.kr), with Reserved Font Names 'JennySans' and '제니산스'.

This Font Software ("JennySans") is a Modified Version, under the terms of the SIL Open Font
License, Version 1.1, of the following Font Software. The copyright notices and Reserved Font
Names of the original Font Software are preserved below as required by the license:

Pretendard 1.3.9 — https://github.com/orioncactus/pretendard
Copyright (c) 2021, Kil Hyung-jin (https://github.com/orioncactus/pretendard),
with Reserved Font Name 'Pretendard'.

Copyright 2014-2021 Adobe (http://www.adobe.com/),
with Reserved Font Name 'Source'.
Source is a trademark of Adobe in the United States and/or other countries.

Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter),
with Reserved Font Name 'Inter'.

Copyright 2021 The M+ FONTS Project Authors (https://github.com/coz-m/MPLUS_FONTS),
with Reserved Font Name 'M PLUS 1'.

Noto Sans KR 2.004 (variable) — https://github.com/google/fonts/tree/main/ofl/notosanskr
Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at: https://openfontlicense.org

-----------------------------------------------------------
SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007
-----------------------------------------------------------

[OFL 1.1 본문 — https://openfontlicense.org/documents/OFL.txt 원문 verbatim]
```

- **1행 = name ID 0 1행**(한 글자도 다르지 않게, AGENTS §8). 원본 고지는 LICENSE 에서 **원문 그대로**(줄바꿈 포함; Pretendard 저장소 LICENSE 4블록, Noto GF OFL.txt 1행) — name ID 0 에서만 `Portions ` 접두 + 한 줄 합침 허용(`02-naming.md` §5).
- M PLUS 1 줄: 가나 글립을 서브셋에서 제외하므로 엄밀히는 불필요하지만 Pretendard 파생 사실을 보수적으로 고지(AGENTS §8). Adobe 줄은 Pretendard 블록과 Noto 블록에 각각 원문대로 두 번 나온다(원문 유지 원칙; 중복 허용).
- OFL 본문 verbatim, 번역본 금지.

**QA 합격 기준 (2)**: (a) `LICENSE` 1행 == 모든 산출물 name ID 0 1행(바이트 비교); (b) Pretendard `LICENSE-repo-main.txt` 의 저작권 4블록과 Noto `OFL-googlefonts.txt` 1행이 **부분 문자열로 정확히** 포함; (c) `-----` 구분선 이후 본문 SHA-256 이 QA 당일 내려받은 `https://openfontlicense.org/documents/OFL.txt` 본문과 일치(줄끝 정규화); (d) name ID 0 의 2–5행에서 `Portions ` 를 떼면 LICENSE 의 해당 원문(개행을 공백으로 합친 것)과 일치.

## 3. `THIRD-PARTY-NOTICES.md` 규격

```
# Third-party notices — JennySans 1.000

| 원본 | 버전 | 출처 URL | SHA-256 | 저작권·RFN | 사용 부분 | 우리가 한 변경 |
|---|---|---|---|---|---|---|
| Pretendard | 1.3.9 | https://github.com/orioncactus/pretendard/releases/download/v1.3.9/Pretendard-1.3.9.zip | 04be351a74d6bf7d60c480a3087e51d185485d35a52023142af1df19eb8c428a (zip) | Copyright (c) 2021, Kil Hyung-jin … 'Pretendard' (+ Adobe 'Source', Inter, M PLUS 1) | 한글 11,172·라틴·그리스·키릴·기호·OpenType 기능·변수 폰트 전체 골격 | 서브셋(가나·한자·PUA 제외), 이름 전면 교체, typo 1949→1950, underline 통일, gasp 추가, DSIG 제거, STAT ital 축 제거, 보충 글립 908 추가 |
| Noto Sans KR (variable) | 2.004-H2 | https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf | 194018e6b2b293a7964f037b25c0249ce1418bc9ab3c971060a03aa57861e252 | Copyright 2014-2021 Adobe … 'Source' | 첫가끝 자모 256·옛 호환자모 41·자모확장 101·방점 2·KS 기호(괘선·원문자·괄호문자·수학·도형·기타) 등 904글립 | 9 웨이트 인스턴스 → UPM 2048 아핀 변환(07-supplement)·진행폭 재설정; GSUB/GPOS 미이식 |

## Full license notices
### Pretendard  — sources/Pretendard/LICENSE-repo-main.txt 머리 4블록 원문
### Noto Sans KR — sources/NotoSansKR/OFL-googlefonts.txt 머리 1행 원문 (+ noto-cjk LICENSE 에는 저작권 줄이 없음을 명시)

## Build tools (not distributed)
fontTools (MIT), brotli (MIT), uharfbuzz (Apache-2.0), fontbakery (Apache-2.0), Pillow (MIT-CMU), playwright (Apache-2.0)
```
- 표의 원본 = AGENTS §5-1 대장 = `sources/MANIFEST.md`. 3차 원본은 없다(`07-supplement.md` §5 합성안). Gothic A1 폴백을 채택하면 행 추가.

**QA 합격 기준 (3)**: §5-1 대장 채택 원본 수(2) = THIRD-PARTY 표 행 수 = MANIFEST 채택 항목; SHA-256 이 `sources/` 실제 파일과 일치.

## 4. 폰트 내부 라이선스 메타데이터 (`02-naming.md` §2 와 동일 값)

| name ID | 값 |
|---|---|
| 0 | `02-naming.md` §5 정본 5행 |
| 7 | `JennySans is a trademark of JennySoft; Pretendard is a trademark of Kil Hyung-jin; Inter UI and Inter is a trademark of rsms; Source is a trademark of Adobe in the United States and/or other countries.` |
| 9 | `02-naming.md` §2 ID 9 |
| 13 | `This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org` |
| 14 | `https://openfontlicense.org` |

**QA 합격 기준 (4)**: 전 파일 ID 13/14 정확 일치, ID 0 §2(a)(d), ID 7 원본 상표 고지 4건 포함. 식별 레코드 RFN 0건은 `02-naming.md` §8-3.

## 5. README 라이선스 절 템플릿 (release)

```
## 라이선스
JennySans(제니산스)는 SIL Open Font License 1.1 로 배포됩니다(Reserved Font Names: "JennySans", "제니산스").
Pretendard(길형진)와 Noto Sans KR(Adobe)에서 파생했으며, 원본 저작권 고지는 LICENSE 와 THIRD-PARTY-NOTICES.md 에 있습니다.
- 상업적 사용·수정·재배포·소프트웨어/게임/문서 임베드·웹폰트: 허용(LICENSE 동봉)
- 폰트 파일 단독 판매: 금지 · 수정본을 "JennySans"/"제니산스" 이름으로 배포: 금지
```

## 6. 원본 선정 라이선스 게이트 (적용 결과)

| 원본 | 판정 | 근거 |
|---|---|---|
| Pretendard 1.3.9 | 사용 가능(OFL 1.1, RFN 4개 누적) | 저장소 main LICENSE(zip 동봉 LICENSE.txt 는 구판 → 저장소판 채택) |
| Noto Sans KR 2.004 VF | 사용 가능(OFL 1.1, 저작권 Adobe, RFN 'Source') | GF OFL.txt·VF ID 0. noto-cjk LICENSE 에 저작권 줄 없음 → GF 본으로 고지 |
| ⛔ IBM Plex Sans KR·Spoqa·나눔 계열·SUIT·Freesentation·Wanted Sans | 사용 금지 목록 유지 | AGENTS §5-1 |
| Gothic A1 2.50 (예비) | OFL 1.1·RFN 없음 — 필요 시 사용 가능하나 **현재 미사용** | `07-supplement.md` §5 폴백 |

## 7. 상표·이름
- `JennySans`·`제니산스` 는 제니소프트 표기(™, 미등록). 유사 상표 검색 결과는 release 가 `docs/DISTRIBUTION.md` 에 기록.
- 「제니산스」는 name ID 1/16 ko-KR 에만 쓰고 파일명·PS 이름·URL 에는 쓰지 않는다.

## 8. QA 합격 기준 (게이트 8 종합)
1. §2 (a)–(d). 2. §3 3자 일치. 3. §4 + `02-naming.md` §6 식별 레코드 RFN 0건. 4. 릴리스 zip·npm 루트 LICENSE 존재, README 라이선스 절 존재. 5. §6 표의 채택 원본 2건 근거가 `docs/research/02-licenses.md` 에 인용됨.

## 9. 갱신 이력
- 2026-09-06: 저작권 정본·RFN 2개·원본 고지 원문·THIRD-PARTY 행 확정.
