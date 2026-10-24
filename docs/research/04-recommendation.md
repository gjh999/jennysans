# 04 — 추천안 (font-researcher, 2026-09-05) — 결정은 팀장

근거: `01-benchmark.md`(실측) · `02-licenses.md`(원문) · `03-web-and-platform.md`(기술).

## 1. 한글 원본

| 순위 | 원본 | 근거 | 결손(우리 범위 기준) | 리스크 |
|---|---|---|---|---|
| **1** | **Pretendard 1.3.9** (Inter + Source Han Sans 한글 재조정) | 9 웨이트 + 변수 + OTF/TTF 모두 존재 · 한글·라틴·수직 메트릭 조화 완료(USE_TYPO, 한글 4% 축소·진행폭 조정) · Latin-1/Ext-A/스페인어/그리스/키릴 완비 · OpenType 기능 풍부(tnum, case, ss01–16) · 라이선스 누적 고지 선례가 name 테이블에 있음 | 호환자모 41(U+3165–318E) · 첫가끝 자모 256+29+72 · KS 기호 6(∠∴◎㉠㉡㉢) · ŉ(U+0149) | 마지막 릴리스 2023-11(저장소는 활동 중) · RFN 4개 누적 관리 · TTF/VF 무힌팅 |
| 2 | **Noto Sans KR 2.004 변수 TTF**(Google Fonts) / Source Han Sans KR 2.005R | 자모·옛한글 조합(ljmo/vjmo/tjmo)·KS 기호 전량 · 웨이트 100–900 연속 · Adobe 유지보수(2025) | Latin Ext-A 98자 · 그리스 악센트 7 · 라틴은 Source Sans 계열(Inter 대비 UI 인상 약함) · hhea/typo 불일치·USE_TYPO 미설정 → 정규화 필요 · 한자 8k 서브셋 필요 | 파일 큼 · 정적 TTF 없음(변수에서 인스턴싱) |
| 3 | Gothic A1 2.50 | 자모확장 제외 전 범위 보유 · 9 웨이트 · TT 힌팅 · RFN 없음 | 자모확장 A/B · 변수 없음 · 기능 빈약 | 2017 이후 미갱신 · 한양 고딕 인상·라틴 품질 |

## 2. 라틴 원본

| 순위 | 원본 | 근거 |
|---|---|---|
| **1** | **Inter 4.1** (Pretendard 안에 이미 포함된 형태로 사용) | UI·본문 가독성 표준급, opsz/wght 변수, 그리스·키릴 포함, Pretendard 가 이미 한글과 크기·메트릭 맞춰 놓음. 별도 병합 불필요 |
| 2 | Source Sans 3 (3.052R) | Source Han Sans 라틴과 동일 디자이너 → 2순위 한글(Noto KR)과 자연스러운 조합. Latin Ext-A 128 완비. 단 wght 200–900(Thin 100 없음) |
| 보조 | Noto Sans (LGC) 2.015 | 그리스·키릴 확장(악센트 그리스 U+03AA–03B0 등) 보충용. wght 100–900 |

## 3. 조합 방식

| 방식 | 내용 | 장점 | 단점 | 권고 |
|---|---|---|---|---|
| **A. Pretendard 파생 + 결손 보충** | Pretendard(한글+라틴)를 기반으로 이름·메타데이터 변경, 결손 글립(자모·옛 호환자모·KS 기호 6자)을 **Noto Sans KR 변수 TTF 를 각 웨이트(100–900)로 인스턴싱**해 UPM 2048 로 스케일(≈×1.966, 01 §3)·진행폭 1770 맞춰 병합. 가나(184자)는 범위 밖이므로 제거 가능 | 작업량 최소 · 품질 검증된 조화 · 9 웨이트/변수 즉시 확보 · 결손 글립도 같은 골격(SHS)이라 이질감 없음 | Pretendard 갱신에 종속 · RFN 4개 누적 · 변수 폰트에 글립 추가 시 gvar 마스터 정합 작업 필요(정적 9종 먼저, 변수는 2단계) | **채택 권고** |
| B. Source Han Sans KR + Inter 직접 병합 | 한글은 SHS/Noto KR, 라틴은 Inter 를 fontTools.merge 로 병합, 크기·메트릭 직접 조정 | 원본 최신판 직접 사용 · Pretendard 비종속 | Pretendard 가 이미 한 작업(스케일·진행폭·수직 메트릭·기능 통합·9 웨이트 매칭: SHS 는 250/350 등 웨이트 체계가 달라 인스턴싱 필요)을 재현해야 함 · 품질 리스크 큼 | 비권고(A 불가 시 대안) |
| C. Noto Sans KR 변수 단일 원본 + Source Sans 3 보충 | Noto KR VF 를 인스턴싱해 9 웨이트, Latin Ext-A 98자·그리스 7자를 Source Sans 3 에서 보충, 메트릭 정규화 | 라이선스 단순(Adobe 'Source' 하나 + Source Sans 동일 저작권자) · 옛한글 조합 지원 | 라틴 인상이 Inter 보다 문서체에 가까움 · hhea/typo 정규화·한자 제거 등 손질 필요 | 2순위(라이선스 단순화를 우선하면 선택) |

## 4. 방식 A 상세 제안 (architect/builder 참고)

1. **정적 9 웨이트**: `sources/Pretendard/Pretendard-<W>.otf`(CFF) 와 `alternative/…ttf`(glyf; zip 에 9종 모두 있음 — 현재 Regular/Bold 만 추출, 빌더가 나머지 추출) 를 각각 OTF/TTF 산출의 기반으로 사용. 이름 변경은 03 §2 표.
2. **결손 보충 원본**: `sources/NotoSansKR/NotoSansKR[wght].ttf` → `fontTools.varLib.instancer` 로 wght=100…900 인스턴스 9개 생성 → 필요한 글립만 서브셋(U+1100–11FF, U+3165–318E, U+A960–A97C, U+D7B0–D7FB, U+2220, U+2234, U+25CE, U+3260–3262) → cu2qu 불필요(이미 glyf) · OTF 산출용은 SHS KR OTF(CFF) 7 웨이트에서 가장 가까운 웨이트를 취하거나 TTF 글립을 qu2cu 로 변환(03 §3).
   - 스케일: 2048/1000 × 0.96 ≈ 1.966(가 높이비 0.868/0.904) — **architect 가 렌더 비교로 확정**. 진행폭: 한글 계열 1770(Pretendard 한글/호환자모 진행폭), 기호는 Pretendard 기존 기호(※ 1234, ① 1784) 와 맞춤.
   - 첫가끝 자모의 `ljmo/vjmo/tjmo` 조합 규칙은 범위 밖(로드맵 "옛한글 조합 제외") — 자모 단독 글립만 넣고 조합 피처는 넣지 않는다(넣으려면 SHS GSUB 를 이식해야 함).
3. **U+0149 ŉ**: 유니코드가 사용을 권장하지 않는 문자. Noto Sans/Source Sans 3 에 있으나 Inter 에 없음 → architect 가 required 에서 제외할지 결정(제외 권고, optional 로).
4. **수직 메트릭**: Pretendard VF 값(typo=hhea=win: 1950/-494/0, USE_TYPO on)로 9 웨이트 통일(OTF 의 1949 정정).
5. **변수 폰트**: 1차 릴리스는 Pretendard VF 를 이름만 바꾼 것(결손 글립 없음) 또는 결손 글립을 2 마스터(100/900)로 넣어 재빌드 — 후자는 gvar 생성 작업이 커서 1.001 이후 권고. 팀장 결정 사항.
6. **웹**: Google 124 슬라이스 범위 재사용(03 §1) 또는 자체 빈도 분할. 첫 화면 = 라틴 슬라이스(≈26 KB) + 고빈도 한글 슬라이스 2–3개(각 25–35 KB).

## 5. 라이선스 리스크 정리
- Pretendard 저장소 LICENSE(4 RFN) 와 zip LICENSE.txt(1 RFN) 불일치 → 저장소판 채택, 누적 고지.
- Noto CJK LICENSE 에 저작권 줄 없음 → Adobe 줄(GF OFL.txt·VF ID 0 원문)로 고지.
- Inter LICENSE 에 RFN 없음 → 그래도 `Inter` 미사용.
- 나눔 계열·SUIT·Freesentation 은 라이선스 사유로 사용 금지 목록에 유지.

## 6. 커버리지 격차(방식 A 기준, 보충 후 남는 것)
- 보충 원본(Noto KR)에도 없는 것: 그리스 악센트 U+03AA–03B0 → Pretendard(Inter) 에 이미 있음(56/56) 문제 없음. Latin Ext-A → Pretendard 127/128 (ŉ 만). 즉 **A 방식은 측정 집합 전부를 채울 수 있다**(ŉ 제외 판단만 남음).
- 한자·가나는 범위 밖(로드맵). KS X 1001 기호 전체 목록(원문자·괄호문자·단위 ~ 1,000여 자)은 architect 가 `charset/` 로 정의 후 QA 가 재측정 — 샘플 79자 기준 Pretendard 73 + Noto KR 보충 6 = 79.
