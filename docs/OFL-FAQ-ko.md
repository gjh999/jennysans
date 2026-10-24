# OFL 1.1 자주 묻는 질문 — 한국어 요지 (JennySans 사용자용)

> 이 문서는 **참고용 요약**이며 법률 자문이 아닙니다. 효력이 있는 것은 영문 원문뿐입니다.
> - 라이선스 원문: `LICENSE`(저장소 루트) 또는 https://openfontlicense.org/documents/OFL.txt
> - 공식 FAQ(영문): https://openfontlicense.org/ofl-faq/
> - 아래 조항 번호(1~5)는 OFL 1.1 "PERMISSION & CONDITIONS" 의 번호입니다.

## 한눈에 보기

| 하고 싶은 것 | 가능? | 근거·조건 |
|---|---|---|
| 회사 홈페이지·쇼핑몰·앱·게임·유튜브 자막·인쇄물에 사용(상업 포함) | **가능** | OFL 은 용도·상업 여부를 제한하지 않음. 사용 대가·신고·표기 의무 없음 |
| 로고·상표·BI/CI 제작에 사용 | **가능** | 문서/결과물은 폰트 라이선스의 적용을 받지 않음(조항 5 마지막 문장) |
| 웹폰트로 서버에 올려 서빙(self-host·CDN) | **가능** | 폰트 파일을 그대로 배포하는 것 = 재배포 → `LICENSE` 를 함께 두면 됨(조항 2) |
| 앱·게임·전자책·PDF 에 폰트 파일 임베드/번들 | **가능** | 조항 2. 유료 소프트웨어여도 됨 |
| 폰트를 수정(서브셋·웨이트 추가·글립 수정·형식 변환)해서 쓰기 | **가능** | 수정본도 OFL 로만 배포(조항 5). 수정본을 **밖에 배포**하면 이름을 바꿔야 함(조항 3) |
| **폰트 파일 자체를 유료로 판매** | **불가** | 조항 1 "may be sold by itself" 금지. 소프트웨어·서비스에 **포함해서** 파는 것은 가능 |
| 수정본을 "JennySans"/"제니산스" 이름으로 배포 | **불가** | Reserved Font Names(RFN) 'JennySans' 와 '제니산스' 둘 다 예약. 이름을 바꾸면 됨(조항 3) |
| 다른 라이선스(MIT·Apache·상용 EULA 등)로 재배포 | **불가** | 조항 5 — 폰트와 파생물은 OFL 로만 |
| 제니소프트 이름으로 수정본을 홍보 | **불가** | 조항 4 — 기여 사실을 밝히는 것만 가능 |

## 상업적 이용 — 무엇이 되고 무엇이 안 되나

가장 많이 받는 질문입니다. 먼저 **판단의 근거가 되는 조항 원문**(우리 `LICENSE` 71~102행에서 그대로 인용)을 보고, 그 아래 실무 표로 풉니다.

```
PERMISSION & CONDITIONS
Permission is hereby granted, free of charge, to any person obtaining
a copy of the Font Software, to use, study, copy, merge, embed, modify,
redistribute, and sell modified and unmodified copies of the Font
Software, subject to the following conditions:

1) Neither the Font Software nor any of its individual components,
in Original or Modified Versions, may be sold by itself.

2) Original or Modified Versions of the Font Software may be bundled,
redistributed and/or sold with any software, provided that each copy
contains the above copyright notice and this license. These can be
included either as stand-alone text files, human-readable headers or
in the appropriate machine-readable metadata fields within text or
binary files as long as those fields can be easily viewed by the user.

5) The Font Software, modified or unmodified, in part or in whole,
must be distributed entirely under this license, and must not be
distributed under any other license. The requirement for fonts to
remain under this license does not apply to any document created
using the Font Software.
```

| 하고 싶은 일 | 가능 | 근거 |
|---|---|---|
| 유료 소프트웨어·앱·게임에 번들·임베드해 판매 | **✅ 가능** | 조항 2 "may be bundled, redistributed and/or sold with any software" |
| 이 폰트로 만든 인쇄물·전자책·영상·로고를 판매 | **✅ 가능** | 조항 5 "does not apply to any document created using the Font Software" |
| 사내 전 제품에 무제한 사용·서버 배포·웹 임베드 | **✅ 가능** | `fsType` 0(임베딩 제한 없음) + 조항 2 |
| 기업 커스터마이징·기술지원 용역 판매 | **✅ 가능** | 폰트 판매가 아니라 **서비스** 대가 |
| 유료 CDN·호스팅으로 제공 | **✅ 가능** | 서비스 대가이지 폰트 단독 판매가 아님 |
| **폰트 파일 자체를 상품으로 판매** | **❌ 불가** | 조항 1 "may not be sold by itself" |
| 특정 고객 전용 **독점** 라이선스 판매 | **❌ 불가** | 조항 1·5 — OFL 유지 의무를 벗어날 수 없음 |
| OFL 을 떼고 다른 라이선스(상용 EULA·MIT 등)로 배포 | **❌ 불가** | 조항 5 "must be distributed entirely under this license" |
| 제3자의 무료 재배포를 막기 | **❌ 불가** | OFL 이 근본적으로 허용하는 자유 |

> **⚠ 비가역성 — 되돌릴 수 없습니다.**
> JennySans 는 OFL 원본(Pretendard · Noto Sans KR)의 **파생물**이므로 **영원히 OFL** 이고, 제니소프트라 해도 나중에 라이선스를 상용으로 바꿀 수 없습니다(조항 5).
> **유료로 팔 수 있는 폰트 상품이 필요하면, 모든 글립을 자체 디자인한 완전히 별개의 폰트**여야 합니다.

**이름 보호는 라이선스와 별개입니다.** OFL 로 누구나 수정·재배포할 수 있어도, 수정본은 「JennySans」·「제니산스」라는 **이름을 쓸 수 없습니다**(조항 3, Reserved Font Name). 여기에 **상표 등록**을 더하면 폰트 밖(서비스명·홍보)에서의 이름 사용도 통제할 수 있습니다 — 절차는 [LEGAL-REGISTRATION.md](LEGAL-REGISTRATION.md).

관련 공식 FAQ(영문 원문, `docs/research/02-licenses.md` §0 재인용):
- 3.1 "You are not allowed to remove the copyright statement(s) from the font, but you could put additional information into it that covers your contribution."
- 3.2 "Yes, but if you distribute that font to others it must be under the OFL, and include the information mentioned in condition 2 of the license."

## Q&A

### Q1. 상업적으로 써도 되나요? 비용이나 표기 의무가 있나요?
됩니다. 개인·기업·관공서·영리·비영리 구분 없이 무료입니다. 결과물(문서·이미지·영상·웹페이지)에 "JennySans 사용" 같은 표기를 할 의무는 없습니다.
표기 의무가 생기는 경우는 **폰트 파일 자체를 다시 나눠 줄 때**(조항 2: 저작권 고지와 라이선스를 함께)뿐입니다.

### Q2. 웹사이트에 올려 쓰면 "재배포"인가요?
네. 브라우저가 폰트 파일을 내려받으므로 재배포에 해당합니다. 하지만 요구사항은 간단합니다 — 폰트 파일과 같은 곳(저장소·패키지·서버 디렉터리)에 `LICENSE` 를 두거나, 폰트 내부 메타데이터(name ID 0/13/14 — JennySans 는 이미 채워져 있음)로 충족됩니다(조항 2 "machine-readable metadata fields").
`dist/web/` 의 WOFF2 는 내부에 고지가 들어 있고, 우리 CDN·npm 패키지에도 `LICENSE` 가 동봉됩니다.

### Q3. 게임(Unity·Godot·Flutter)에 넣어서 팔아도 되나요?
됩니다. 폰트를 **소프트웨어의 일부로** 번들·임베드해 판매하는 것은 조항 2 가 명시적으로 허용합니다.
TextMesh Pro 처럼 폰트를 **아틀라스 텍스처(SDF)로 변환**해 넣는 것도 "Modified Version" 의 일종이지만, 게임 밖으로 폰트 파일을 따로 배포하는 게 아니므로 실무상 문제되지 않습니다. 배포 패키지 어딘가(크레딧 화면·THIRD-PARTY 파일)에 `LICENSE` 사본을 넣어 두면 충분합니다.

### Q4. 폰트만 따로 팔 수 없다는 게 정확히 무슨 뜻인가요?
"폰트 파일 그 자체"를 상품으로 파는 것(폰트 마켓에 올려 판매, 유료 다운로드)이 금지입니다(조항 1).
폰트가 **포함된** 상품(앱·게임·템플릿·설치 프로그램·유료 웹서비스)을 파는 것은 됩니다. 핵심은 구매자가 사는 것이 "폰트"인지 "폰트가 들어 있는 다른 것"인지입니다.

### Q5. 서브셋만 잘라 쓰거나 웨이트를 바꿔 써도 되나요?
됩니다(수정 허용). 회사 내부·자기 서비스에서만 쓰면 이름을 바꿀 필요도 없습니다.
단 그 수정본을 **외부에 배포**(공개 저장소 커밋·CDN 공개·패키지 배포 포함 — OFL FAQ 3.8)하면 **'JennySans' 이름을 쓸 수 없고**(조항 3) OFL 로만 배포해야 합니다(조항 5). 원본 저작권 고지는 그대로 남겨야 합니다.

### Q6. 이름을 바꿔야 할 때 어떻게 바꾸나요?
RFN 'JennySans' 와 '제니산스' 를 폰트의 **주 이름**(사용자에게 보이는 패밀리명·현지화 패밀리명·PostScript 이름)에 쓰지 않으면 됩니다. "JennySans Custom"·"제니산스 커스텀" 처럼 RFN 을 포함하는 이름도 안 됩니다(OFL FAQ 5 참고). 예: `MyCorpSans`.
JennySans 는 원본(Pretendard·Source·Inter·M PLUS 1)의 RFN 을 똑같은 이유로 쓰지 않고 있습니다.

### Q7. 폰트가 들어간 문서(PDF·PPT·이미지)는 OFL 을 따라야 하나요?
아니요. 조항 5 마지막 문장: "The requirement for fonts to remain under this license does not apply to any document created using the Font Software." 문서·이미지·영상은 자유롭게 어떤 라이선스로든 배포·판매할 수 있습니다.

### Q8. 다른 OFL 폰트와 합쳐서 새 폰트를 만들 수 있나요?
됩니다(OFL FAQ 3.2). 결과물은 OFL 로 배포하고, 합친 모든 원본의 저작권 고지·RFN 을 누적 보존하며, 어느 원본의 RFN 도 새 이름에 쓰지 않습니다. JennySans 자체가 이렇게 만들어졌습니다(`THIRD-PARTY-NOTICES.md`).

### Q9. 보증·책임은요?
없습니다(DISCLAIMER). "있는 그대로" 제공되며 사용으로 인한 손해에 제니소프트·원저작권자는 책임지지 않습니다. 인쇄·공식 문서에 쓰기 전에 필요한 글자가 다 있는지 직접 확인하세요(문자 범위는 `README.md`).

### Q10. 폰트 내부에서 라이선스를 확인하려면?
Windows: 파일 우클릭 → 속성 → 자세히. macOS: 서체 관리자에서 폰트 선택 → 정보(⌘I). 또는 `fontTools`:
```
python -c "from fontTools.ttLib import TTFont; f=TTFont('JennySans-Regular.ttf'); n=f['name']; print(n.getDebugName(0)); print(n.getDebugName(13)); print(n.getDebugName(14))"
```

## 제니소프트가 지키는 것 (파생물 제작자로서)
- 원본 저작권 고지 전부 보존(`LICENSE` 머리·name ID 0) · 원본 RFN 을 이름에 쓰지 않음 · OFL 1.1 로만 배포 · 폰트 단독 판매 안 함.
- 원문·근거: `docs/research/02-licenses.md`, `docs/spec/06-license.md`.
