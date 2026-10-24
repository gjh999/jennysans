# 02 — 라이선스 원문 인용·RFN·파생 요구사항 (font-researcher, 2026-09-05)

> 인용 원칙: 1차 출처(공식 GitHub 저장소 raw LICENSE, 배포 zip 동봉 LICENSE, 폰트 name 테이블)에서 **그대로** 인용. 요약·추측 없음.
> 로컬 사본: `sources/<이름>/LICENSE*`·`OFL*.txt` (SHA-256 은 `sources/MANIFEST.md`). name 테이블 전문: `docs/research/name-tables.md`.
> WebFetch 로만 확인한 항목(사이트 문구·FAQ)은 "(WebFetch)" 로 표시.

## 0. OFL 1.1 핵심 조항 (원문 — `sources/Pretendard/LICENSE.txt` 및 모든 후보의 LICENSE 에 동일하게 수록)

```
1) Neither the Font Software nor any of its individual components,
in Original or Modified Versions, may be sold by itself.

2) Original or Modified Versions of the Font Software may be bundled,
redistributed and/or sold with any software, provided that each copy
contains the above copyright notice and this license. These can be
included either as stand-alone text files, human-readable headers or
in the appropriate machine-readable metadata fields within text or
binary files as long as those fields can be easily viewed by the user.

3) No Modified Version of the Font Software may use the Reserved Font
Name(s) unless explicit written permission is granted by the corresponding
Copyright Holder. This restriction only applies to the primary font name as
presented to the users.

4) The name(s) of the Copyright Holder(s) or the Author(s) of the Font
Software shall not be used to promote, endorse or advertise any
Modified Version, except to acknowledge the contribution(s) of the
Copyright Holder(s) and the Author(s) or with their explicit written
permission.

5) The Font Software, modified or unmodified, in part or in whole,
must be distributed entirely under this license, and must not be
distributed under any other license. The requirement for fonts to
remain under this license does not apply to any document created
using the Font Software.
```

OFL FAQ(openfontlicense.org/ofl-faq, WebFetch 요약 인용):
- 3.1 "You are not allowed to remove the copyright statement(s) from the font, but you could put additional information into it that covers your contribution."
- 3.2 (다른 폰트와 합쳐 새 폰트를 만들 수 있는가) "Yes, but if you distribute that font to others it must be under the OFL, and include the information mentioned in condition 2 of the license."
- 3.3 "Derivative fonts must be released under the OFL and cannot be sold by themselves… permitted… to include them in a larger software package… even if the larger package is sold."
- 3.8 "Making a public commit or publishing a public branch is effectively redistributing your modifications, so any change to the font will require that you do not use the RFNs."
- 5.2 "Reserved Font Names ensure that the only fonts that have the original names are the unmodified Original Versions."

## 1. 후보별 원문 인용

### 1-1. Pretendard — `https://raw.githubusercontent.com/orioncactus/pretendard/main/LICENSE` (4,816 bytes)
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
```
- ⚠ 배포 zip `Pretendard-1.3.9.zip` 안의 `LICENSE.txt`(4,419 bytes, `sources/Pretendard/LICENSE.txt`)는 구판으로 첫 줄이 `with Reserved Font Name Pretendard.` 뿐이고 Adobe/Inter/M PLUS 줄이 없다. **저장소 main 의 LICENSE 를 기준으로 삼는다.**
- name 테이블(Pretendard-Regular.otf / PretendardVariable.ttf, `name-tables.md`):
  - ID 0: `Copyright © 2023 Kil Hyung-jin`
  - ID 7: `Pretendard is a trademark of Kil Hyung-jin; Inter UI and Inter is a trademark of rsms; Source is a trademark of Adobe in the United States and/or other countries.`
  - ID 9: `Base glyphs from Inter by Rasmus Andersson; Hangeul glyphs from Noto Sans CJK(Source Han Sans) by Jang Soo-young and Kang Joo-yeon, Sandoll Communications; Kana glyphs from M PLUS 1p by Coji Morishita, UNDERFOREST DESIGN; Combined and redesigned to Pretendard by Kil Hyung-jin.`
  - ID 13: `This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL` · ID 14: `http://scripts.sil.org/OFL`
  - "Pretendard" 가 들어간 레코드: ID 1,3,4,6,7,9,16(+VF 25, 인스턴스 이름 258–272). "Source"/"Inter" 는 ID 7·9(고지 목적)에만.
- README(packages/pretendard/README.md): "Pretendard는 SIL 오픈 폰트 라이선스로 배포됩니다. 글꼴 단독 판매를 제외한 모든 상업적 행위 및 수정, 재배포가 가능합니다." 크레딧 절에 Inter / Source Han Sans / M PLUS 1p 명시.
- **파생 시 의무**: 우리 LICENSE 에 위 4개 저작권·RFN 줄을 모두 유지하고 우리 줄(RFN JennySans)을 추가. `Pretendard`·`Source`·`Inter`·`M PLUS 1` 을 주 이름(name ID 1/2/4/6/16/17/21/22/25·fvar 인스턴스명)에 쓰지 않음. ID 0/7/9 에는 고지 목적 언급 가능(Pretendard 자신이 그렇게 함 = 선례).

### 1-2. Source Han Sans — `https://raw.githubusercontent.com/adobe-fonts/source-han-sans/master/LICENSE.txt` (= zip 동봉 `sources/SourceHanSansKR/LICENSE.txt`)
```
Copyright 2014-2025 Adobe (http://www.adobe.com/), with Reserved Font
Name 'Source'. Source is a trademark of Adobe in the United States
and/or other countries.

This Font Software is licensed under the SIL Open Font License,
Version 1.1.
```
- name ID 0 (SourceHanSansKR-Regular.otf): `© 2014-2025 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'.` · ID 7: `Source is a trademark of Adobe …` · ID 13/14: OFL.
- RFN = **`Source`** (단어 자체). 우리 이름에 "Source" 금지.

### 1-3. Noto Sans KR (Noto CJK) — `https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE` (= zip 동봉 `sources/NotoSansKR/LICENSE`)
```
This Font Software is licensed under the SIL Open Font License,
Version 1.1.

This license is copied below, and is also available with a FAQ at:
http://scripts.sil.org/OFL
```
- ⚠ 이 LICENSE 파일에는 **저작권 줄·RFN 줄이 없다.** 폰트 내부: NotoSansKR-Regular.otf ID 0 `© 2014-2021 Adobe (http://www.adobe.com/).`, ID 7 `Noto is a trademark of Google Inc.`
- Google Fonts 배포본 OFL.txt(`https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/OFL.txt`, `sources/NotoSansKR/OFL-googlefonts.txt`): `Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'` — 변수 TTF `NotoSansKR[wght].ttf` ID 0 도 `(c) 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'.`, ID 7 `Source is a trademark of Adobe …`.
- `Sans/README-third_party.md`: "License: SIL Open Font License v1.1 … Note: prior releases of the CJK fonts were issued under the Apache 2 license. This was changed to the SIL OFL v1.1 starting with Version 1.002." / "The copyright is held by Adobe, while the trademarks on the names are held by Google."
- 결론: 저작권자 Adobe, RFN `Source`(GF 본·VF 기준), `Noto` 는 Google 상표 → 둘 다 우리 이름에 쓰지 않음. 고지는 Adobe 저작권 줄로 충족(Pretendard 의 Adobe 줄과 동일 문구).

### 1-4. IBM Plex (Sans KR 포함) — `https://raw.githubusercontent.com/IBM/plex/master/LICENSE.txt` (= zip `sources/IBMPlexSansKR/LICENSE.txt`)
```
Copyright © 2017 IBM Corp. with Reserved Font Name "Plex"

This Font Software is licensed under the SIL Open Font License, Version 1.1.
```
- name ID 0 `Copyright 2018 IBM Corp. All rights reserved.` · ID 7 `IBM Plex® is a trademark of IBM Corp, registered in many jurisdictions worldwide.` RFN `Plex`. (후보 제외)

### 1-5. Spoqa Han Sans Neo — `https://raw.githubusercontent.com/spoqa/spoqa-han-sans/main/LICENSE` (= zip `sources/SpoqaHanSansNeo/LICENSE`)
```
Copyright (c) 2015-10-09 Spoqa (spoqa.com), with Reserved Font Name Spoqa Han Sans.
Copyright (c) 2015-10-09 Spoqa (spoqa.com), with Reserved Font Name Spoqa Han Sans JP.
Copyright (c) 2020-11-30 Spoqa (spoqa.com), with Reserved Font Name Spoqa Han Sans Neo.

This Font Software is licensed under the SIL Open Font License, Version 1.1.
```
- ⚠ 원본(Noto Sans CJK/Adobe, Lato) 저작권 줄이 LICENSE 에 없고 name ID 9/10 에만 `[Noto Sans] … [Lato] Lukasz Dziedzic …` 로 기재. 원본 고지 누락 사례(우리는 따라 하지 않음). (후보 제외)

### 1-6. 나눔 계열
- **Nanum Gothic (Google Fonts)** — `https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/OFL.txt` (`sources/NanumGothic/OFL.txt`):
  ```
  Copyright (c) 2010, NHN Corporation (http://www.nhncorp.com),
  with Reserved Font Name Nanum, Naver Nanum, NanumGothic, Naver 
  NanumGothic, NanumMyeongjo, Naver NanumMyeongjo, NanumBrush, Naver
  NanumBrush, NanumPen, Naver NanumPen.

  This Font Software is licensed under the SIL Open Font License, Version 1.1.
  ```
- **나눔바른고딕** (hangeul.naver.com zip): zip 에 라이선스 파일 없음. name ID 0 `Copyright ⓒ 2013 NHN Corporation. All rights reserved. Font designed by FONTRIX Inc.`, ID 7 `NanumBarunGothic is a registered trademark of NHN Corporation.`, **ID 13 `NHN Corporation`**, ID 14 `http://www.nhncorp.com`, OS/2 fsType=8. 사이트 목록 문구: `저작권 : 오픈 라이선스 (상업적 사용 허용)`(hangeul.naver.com/fonts/search?f=barun, curl). OFL 원문은 확인 못 함 → **라이선스 확인 불가로 제외**.
- **나눔스퀘어 네오** (zip): 라이선스 파일 없음, name ID 13/14 없음, ID 0 `Copyright © 2022 NAVER Corp. All rights reserved. Font Designed by Sandoll Inc.`, ID 7 `NanumSquare Neo variable is a registered trademark of NAVER Corp.`, fsType=8 → 확인 불가로 제외.

### 1-7. Gothic A1 — `https://raw.githubusercontent.com/google/fonts/main/ofl/gothica1/OFL.txt` (`sources/GothicA1/OFL.txt`)
```
(C) Copyright HanYang I&C Co.,Ltd. All rights reserved.

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at:
http://scripts.sil.org/OFL
```
- **RFN 선언 없음.** name ID 0 동일, ID 7 없음, ID 13/14 OFL. 3순위 후보.

### 1-8. Wanted Sans — `https://raw.githubusercontent.com/wanteddev/wanted-sans/main/OFL.txt` (`sources/WantedSans/OFL.txt`)
```
Copyright 2024 The Wanted Sans Project Authors (https://github.com/wanteddev/wanted-sans)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
```
- RFN 줄 없음. name ID 7 `Wanted Sans is a trademark of Wanted Lab, Inc. / Wanted Logo is a trademark … / Source is a trademark of Adobe …`, ID 9 `… Hangeul from Source Han Sans by Jang Soo-young and Kang Joo-yeon, Sandoll Communications;`. (후보 제외)

### 1-9. SUIT — `https://raw.githubusercontent.com/sun-typeface/SUIT/main/LICENSE` (= zip `sources/SUIT/LICENSE`)
```
Copyright (c) 2022, SUNN (http://sun.fo/suit),
with Reserved Font Name SUIT.

This Font Software is licensed under the SIL Open Font License, Version 1.1.
```
- README: "한글 글리프는 본고딕을 기초로 합니다." name ID 9 `Sun; Korean Glyphs from Source Han Sans (…)`. ⚠ OS/2 **fsType=4**(Preview & Print embedding) — OFL 이 허용하는 임베딩과 상충. (후보 제외)

### 1-10. Freesentation — `https://raw.githubusercontent.com/Freesentation/freesentation/main/OFL%20license.txt`
```
Copyright 2024 The Freesentation Authors (https://freesentation.blog/)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
```
- 공식 페이지(freesentation.blog/freesentation, WebFetch): 한글 = Noto Sans(본고딕, 산돌), **라틴 = Roboto(Christian Robertson)**. Roboto 는 Apache-2.0 → AGENTS §5.1 원칙상 제외. 파일 미다운로드.

### 1-11. Paperlogy — `https://raw.githubusercontent.com/Freesentation/paperlogy/main/OFL%20license.txt`
```
Copyright 2024 The PAPERLOGY Authors (https://freesentation.blog/paperlogy)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
```
- 공식 페이지(WebFetch): 한글 = G마켓 산스, 라틴 = Montserrat, 일본어 = M PLUS 2. "SIL 오픈폰트라이선스(OFL)에 따라 글꼴 단독 판매 또는 글꼴 라이선스 변경을 제외한 모든 상업적 행위 및 수정, 재배포가 가능합니다." Gmarket Sans 배포 페이지(corp.gmarket.com/fonts, WebFetch): "Gmarket Sans는 'SIL Open Font License'에 따라 … 자유롭게 사용할 수 있습니다". 원본 파일의 OFL 헤더·RFN 은 미확인. 스타일 사유로 제외.

### 1-12. 라틴 후보
- **Inter** — `https://raw.githubusercontent.com/rsms/inter/master/LICENSE.txt` (= zip `sources/Inter/LICENSE.txt`):
  ```
  Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter)

  This Font Software is licensed under the SIL Open Font License, Version 1.1.
  ```
  ⚠ LICENSE 에 RFN 줄이 없다. 그러나 name ID 7 `Inter UI and Inter is a trademark of rsms.`, Pretendard LICENSE 는 `with Reserved Font Name 'Inter'` 로 기재 → **`Inter` 를 예약명으로 취급**(보수적).
- **Noto Sans (LGC)** — `https://raw.githubusercontent.com/notofonts/latin-greek-cyrillic/main/OFL.txt` (`sources/NotoSans/OFL.txt`): `Copyright 2022 The Noto Project Authors (https://github.com/notofonts/latin-greek-cyrillic)` / OFL 1.1. RFN 줄 없음, ID 7 `Noto is a trademark of Google LLC.`
- **Source Sans 3** — `https://raw.githubusercontent.com/adobe-fonts/source-sans/release/LICENSE.md` (`sources/SourceSans3/LICENSE.md`): `Copyright 2010-2024 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'. All Rights Reserved. Source is a trademark of Adobe in the United States and/or other countries.` / OFL 1.1.

## 2. RFN 요약표

| 원본 | RFN(원문) | 우리 이름 "JennySans" 충돌 | 고지 필요 줄 |
|---|---|---|---|
| Pretendard | `'Pretendard'` | 없음 | Kil Hyung-jin 줄 |
| Source Han Sans / Noto Sans KR / Source Sans 3 | `'Source'` (+`Noto` 상표) | 없음 | Adobe 줄 |
| Inter | LICENSE 에 없음(Pretendard 는 `'Inter'` 로 표기, 상표 고지 있음) | 없음 | Inter Project Authors 줄 |
| M PLUS 1 | `'M PLUS 1'` | 없음 | M+ FONTS Project Authors 줄(가나를 뺄 때도 누적 유지 권고) |
| IBM Plex | `"Plex"` | — | (미사용) |
| Spoqa Han Sans (Neo) | `Spoqa Han Sans`, `… JP`, `… Neo` | — | (미사용) |
| Nanum (GF) | `Nanum, Naver Nanum, NanumGothic, …` | — | (미사용) |
| Gothic A1 | (없음) | — | HanYang I&C 줄(사용 시) |
| SUIT | `SUIT` | — | (미사용) |

## 3. JennySans 파생 시 요구사항 (release/architect 가 스펙에 반영)

1. **LICENSE 파일**(OFL 1.1 전문 + 헤더): 헤더에 아래를 **누적**한다(순서: 우리 → 원본).
   ```
   Copyright (c) 2026, JennySoft (https://github.com/…/JennySans), with Reserved Font Name 'JennySans'.
   Copyright (c) 2021, Kil Hyung-jin (https://github.com/orioncactus/pretendard), with Reserved Font Name 'Pretendard'.
   Copyright 2014-2025 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'. Source is a trademark of Adobe in the United States and/or other countries.
   Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter), with Reserved Font Name 'Inter'.
   Copyright 2021 The M+ FONTS Project Authors (https://github.com/coz-m/MPLUS_FONTS), with Reserved Font Name 'M PLUS 1'.
   ```
   (Adobe 연도는 실제로 병합한 파일의 ID 0 기준: Pretendard 경유분 2014-2021, SHS 2.005R/Noto KR 직접 사용분 2014-2025/2014-2021 — 넓은 범위 `2014-2025` 로 표기.)
2. **name 테이블**: ID 0 = 위 저작권 누적(줄바꿈 대신 `;` 연결 가능) · ID 7 = 우리 상표 문구 + 원본 상표 고지(Pretendard 선례 그대로: "… Inter is a trademark of rsms; Source is a trademark of Adobe …") · ID 9 = 원본 기여 크레딧 · ID 13 = OFL 문구 · ID 14 = `https://openfontlicense.org` 또는 `http://scripts.sil.org/OFL`.
   ID 1/2/3/4/6/16/17/21/22/25 및 fvar 인스턴스 subfamily/psName, STAT 값 이름에는 `Pretendard`·`Source`·`Inter`·`Noto`·`M PLUS`·`Plex`·`Spoqa`·`Nanum`·`SUIT` 가 **한 글자도 없어야** 함(QA 게이트 8).
3. **THIRD-PARTY-NOTICES**: 각 원본의 LICENSE 전문 사본(Pretendard 저장소 main 판, SHS LICENSE.txt, Noto CJK LICENSE + GF OFL.txt, Inter LICENSE.txt, M PLUS OFL) 첨부.
4. **금지**: 폰트 단독 판매(OFL 1), 다른 라이선스로 재배포(OFL 5). 허용: 앱·게임·문서 번들·임베드(OFL 2), 상업적 사용.
5. **fsType = 0**(Installable) 로 설정 — 원본 Pretendard/SHS/Inter 모두 0.
6. DSIG 테이블은 수정 후 무효이므로 제거(SHS OTF 에 있음).
