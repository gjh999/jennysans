# Third-party notices — JennySans 1.000

JennySans is derived from the following Font Software, all under the SIL Open Font License 1.1.
(제니산스는 아래 OFL 1.1 원본 폰트의 파생물(Modified Version)입니다. 원본의 저작권 고지와 Reserved Font Name 은 `LICENSE` 머리와 폰트 내부 name ID 0 에 그대로 보존됩니다.
JennySans 자신의 Reserved Font Names 는 **'JennySans' 와 '제니산스'** 두 이름입니다 — `LICENSE` 1행 = name ID 0 1행, AGENTS §8 2026-09-06 결정.)

> 이 표의 원본 목록은 `AGENTS.md` §5-1 대장 = `sources/MANIFEST.md` 와 1:1 이어야 한다(스펙 `docs/spec/06-license.md` §3).
> SHA-256 은 `sources/MANIFEST.md`(font-researcher 2026-09-05 실측) 값을 그대로 옮긴 것이다.

| 원본 | 버전 | 출처 URL | SHA-256(원본 파일) | 저작권·RFN(원문) | 사용 부분 | 우리가 한 변경 |
|---|---|---|---|---|---|---|
| **Pretendard** | 1.3.9 (2023-11-05) | https://github.com/orioncactus/pretendard — 릴리스 zip `Pretendard-1.3.9.zip`: https://github.com/orioncactus/pretendard/releases/download/v1.3.9/Pretendard-1.3.9.zip | zip `04be351a74d6bf7d60c480a3087e51d185485d35a52023142af1df19eb8c428a` · `PretendardVariable.ttf` `3090ccde0442bb347aa7685d9ba8b17436a60682df6e8f92a9a670de14056e22` · `alternative/Pretendard-Regular.ttf` `6d0af5258997aec7354a6e340fc2325ba321c410ca48b3af858c8c3d6e92a324` · `alternative/Pretendard-Bold.ttf` `c16b88c670d23e83fa1170c954cbc4822d3b8dad3c3cde15d798a94b43d97985` · 나머지 정적 TTF 7종(release 2026-09-06 `sha256sum` 실측, MANIFEST 미기재): Thin `5f65cfe7d99934ee73de983df26154666c65418d73a62f634110945f2ddc0caf` · ExtraLight `041fad1c6a532208d52def16576f0d1dd7f1b77b9306c657f69bf619f2b638cc` · Light `1ba73b22955754bb9ed6bbf7678416af647f90704e9064661f7924da578dad3e` · Medium `3bae579377eb8e9ac412cb4809ebc3de1d956ed75995c1e346f0c1311053f4e2` · SemiBold `5e1c548732af70873103066c16e1369b9a8a871f0b38c321a1d5bc73e43cea2d` · ExtraBold `eedbd2877218242323bdff816684f7f5c325e54ae820d5b78eec9a5e5c7edef6` · Black `0a7c1fd65a599f9d25de860cc832ea9ac40c207775e33eb4344a4647392a2b5d` | `Copyright (c) 2021, Kil Hyung-jin (https://github.com/orioncactus/pretendard), with Reserved Font Name 'Pretendard'.` + 누적 고지 3줄(Adobe 'Source' · The Inter Project Authors 'Inter' · The M+ FONTS Project Authors 'M PLUS 1') — 저장소 `main` 의 LICENSE 기준(zip 동봉 `LICENSE.txt` 는 구판으로 첫 줄만 있음) | **주원본** — 한글 완성형 11,172자·라틴(ASCII·Latin-1·Latin Ext-A)·그리스·키릴 기본·구두점·화폐·KS 기호 대부분·OpenType 기능(kern/mark/ccmp/liga/case/locl/frac/ordn/sups/subs/pnum/tnum/zero/ss01–16/cv01–13 등)·변수 폰트(`wght`) | ① 문자집합을 `charset/required.txt`(+`recommended`) 로 서브셋 — 가나(M PLUS 1 유래 184자) 등 범위 밖 글립 제외 ② name 테이블 전면 교체(패밀리 JennySans / 제니산스, PS `JennySans-<Weight>`), 원본 RFN 은 저작권(ID 0)·버전(ID 5 "based on …")·디자이너(ID 9) 고지에만 보존 ③ 수직 메트릭 전 웨이트 통일(typo=hhea=win 1950/-494/0, `USE_TYPO_METRICS`; OTF 의 1949 → 1950 정정) ④ OS/2(벤더 `JNSF`, fsType 0, fsSelection/WWS)·STAT·fvar 인스턴스 재작성 ⑤ 정적 9종은 원본 `alternative/*.ttf`(glyf) 기반, OTF(CFF) 산출은 1.1 이후 ⑥ WOFF2 + Google Fonts 한국어 124 슬라이스 정의 기반 `unicode-range` 분할본(웨이트당 99 조각) 생성 ⑦ 서브셋으로 참조 글립이 사라진 `ss16`(PUA 아이콘 전용)·변수 `rlig`(원본에서 이미 빈 피처) 제거 ⑧ 원본 두 폰트 모두 없는 KS 기호 6자(￢￣￤ U+FFE2–FFE4 · ⅔ U+2154 · ≒ U+2252 · ◈ U+25C8)를 Pretendard 자체 부품(¬ ¯ ¦ · ⅓ · = . · ◇ ◆)의 컴포지트/분해로 합성, DŽ U+01C4 는 `D`+`Zcaron` 컴포지트로 보충, (1.001) 체크박스 ☐☑☒ U+2610–2612 를 Pretendard 자체 부품(□ U+25A1 그대로 + ✓ U+2713 / × U+00D7 균등 축소)으로 합성 — 세 원본(Pretendard·Noto Sans KR·Source Han Sans KR) 모두 미보유 실측, 새 원본·고지 추가 없음 ⑨ 중첩 컴포지트를 한 단계 평탄화(`outer∘inner` 변환 합성, 외곽선 불변) ⑩ 세로쓰기 미지원이므로 `vhea`·`vmtx`·`VVAR`·`VORG` 제거, 참조되지 않는 고아 글립 제거 |
| **Noto Sans KR** (Noto Sans CJK KR, Google Fonts 변수 빌드) | 2.004 (`Version 2.004-H2`) | https://github.com/notofonts/noto-cjk · Google Fonts 빌드: https://github.com/google/fonts/tree/main/ofl/notosanskr — 파일 `NotoSansKR[wght].ttf`: https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf | `194018e6b2b293a7964f037b25c0249ce1418bc9ab3c971060a03aa57861e252` (10,414,588 bytes) | `Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'` (Google Fonts `OFL.txt` 및 폰트 name ID 0 원문). noto-cjk 저장소의 `Sans/LICENSE` 에는 저작권 줄이 없어 Google Fonts 배포본 문구를 채택. `Noto` 는 Google 의 상표(name ID 7) — 우리 이름에 쓰지 않음 | **보충원본** — Pretendard 에 없는 글립만, 8차 빌드 기준 **909 글립**(= Noto 901 + Pretendard 부품 컴포지트 3 + 합성 3 + 미러 1 + DŽ U+01C4 컴포지트 1; `build/BUILD-REPORT.md` 2026-09-09): 첫가끝 자모 전부(U+1100–11FF 256 + Ext-A U+A960– 29 + Ext-B U+D7B0– 72)·옛자모 호환형 등 호환자모 잔여 41자(U+3165–318E)·괘선 U+2500–257F 128·◌ U+25CC·괄호·원문자 U+3200–327F 127·단위 U+3380–33DF 중 16·KS X 1001 기호 일부(∠ U+2220·∴ U+2234·◎ U+25CE·㉠㉡㉢ U+3260–3262 등) | ① 변수 폰트를 `fontTools.varLib.instancer` 로 wght 100–900 9 인스턴스 생성 ② 필요한 글립만 서브셋 ③ `docs/spec/07-supplement.md` §6 규칙으로 UPM 2048 에 맞춤(한글·자모 1.982×1.965 고정·진행폭 1770, 괘선 affine 1.77×2.444, 기호는 Pretendard 참조 글립 크기·폭에 맞춤; ∼ U+223C 는 Noto ∽ U+223D 를 좌우 반전) 후 각 웨이트에 병합, 변수 폰트에는 9 인스턴스 피크 gvar 로 삽입 ④ 원본의 옛한글 조합 피처(ljmo/vjmo/tjmo)는 이식하지 않음(자모 단독 글립만) |

- 산출물에 **포함되지 않는** 비교·예비 원본(Source Han Sans KR 2.005R · Gothic A1 · Source Sans 3 · Noto Sans 등)은 `sources/MANIFEST.md` 에만 기록되며 여기 표에 넣지 않는다.
- 폰트 내부 고지: name ID 0 = `LICENSE` 머리의 저작권 줄들, ID 7 = `JennySans is a trademark of JennySoft.` + 원본 상표 고지, ID 9 = 원본 디자이너 크레딧, ID 13/14 = OFL 문구·`https://openfontlicense.org` (`docs/spec/02-naming.md` §2·§5).

## Full license notices

각 원본의 LICENSE/OFL.txt **머리 부분(저작권·RFN 문장)** 을 원문 그대로 인용한다. OFL 1.1 본문은 모든 원본에서 동일하며(`LICENSE` 의 구분선 이하와 같은 텍스트, 공식 https://openfontlicense.org/documents/OFL.txt) 여기서는 반복하지 않는다.

### Pretendard 1.3.9 — `https://raw.githubusercontent.com/orioncactus/pretendard/main/LICENSE`

```
Copyright (c) 2021, Kil Hyung-jin (https://github.com/orioncactus/pretendard),
with Reserved Font Name 'Pretendard'.

Copyright 2014-2021 Adobe (http://www.adobe.com/),
with Reserved Font Name 'Source'.
Source is a trademark of Adobe in the United States and/or other countries.

Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter),
with Reserved Font Name 'Inter'.

Copyright 2021 The M+ FONTS Project Authors (https://github.com/coz-m/MPLUS_FONTS),
with Reserved Font Name 'M PLUS 1'.

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at:
https://scripts.sil.org/OFL
```

Pretendard 폰트 내부 크레딧(name ID 9, 원문): `Base glyphs from Inter by Rasmus Andersson; Hangeul glyphs from Noto Sans CJK(Source Han Sans) by Jang Soo-young and Kang Joo-yeon, Sandoll Communications; Kana glyphs from M PLUS 1p by Coji Morishita, UNDERFOREST DESIGN; Combined and redesigned to Pretendard by Kil Hyung-jin.`

### Noto Sans KR 2.004 (Google Fonts build) — `https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/OFL.txt`

```
Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at:
https://scripts.sil.org/OFL
```

noto-cjk 저장소 원본 `Sans/LICENSE`(`https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE`) 머리(원문, 저작권 줄 없음):

```
This Font Software is licensed under the SIL Open Font License,
Version 1.1.

This license is copied below, and is also available with a FAQ at:
http://scripts.sil.org/OFL
```

noto-cjk `Sans/README-third_party.md`(원문 발췌): "The copyright is held by Adobe, while the trademarks on the names are held by Google."

### 간접 원본(Pretendard 를 통해 포함) — 고지 보존 대상

| 원본 | 저작권 줄(원문) | 출처 |
|---|---|---|
| Source Han Sans / Noto Sans CJK(한글 골격) | `Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'.` | Pretendard LICENSE 2번째 블록 |
| Inter(라틴·그리스·키릴 골격) | `Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter), with Reserved Font Name 'Inter'.` | Pretendard LICENSE 3번째 블록 (Inter 자체 LICENSE.txt 에는 RFN 줄이 없으나 name ID 7 상표 고지·Pretendard 표기를 따라 예약명으로 취급) |
| M PLUS 1(가나 — 산출물에서 제외했으나 고지는 보수적으로 유지) | `Copyright 2021 The M+ FONTS Project Authors (https://github.com/coz-m/MPLUS_FONTS), with Reserved Font Name 'M PLUS 1'.` | Pretendard LICENSE 4번째 블록 · AGENTS §8 2026-09-06 결정 |

## Build tools (not distributed with the fonts)

fontTools (MIT) · brotli (MIT) · uharfbuzz (Apache-2.0) · fontbakery (Apache-2.0) · Pillow (MIT-CMU) · playwright (Apache-2.0).
빌드·검사에만 쓰이며 배포 파일(TTF/WOFF2/CSS)에 포함되지 않는다.

## Data (facts, not copyrighted works)

- 웹 분할 `unicode-range` 구간: Google Fonts 가 Noto Sans KR 을 서빙할 때 쓰는 124개 코드포인트 구간(`https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100..900&display=swap` 응답, 2026-09-05 수신, `docs/research/google-kr-slices.css`). 구간 목록은 사실 데이터이며 Google 의 폰트 파일은 사용하지 않는다.
