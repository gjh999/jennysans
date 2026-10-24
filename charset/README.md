# charset/ — JennySans 문자집합 정의 (font-architect 소유)

> 정본은 `required.txt` · `recommended.txt` · `korean-old.txt` 세 파일이다. 이 README 는 형식·판단 근거·검증 방법·집계표·원본 커버리지를 담는다.
> 상태: **P2 2차(원본 확정 반영, 2026-09-06)** — 팀장 결정 ①②(AGENTS §8) 적용: Hangul Jamo 256 전부 required, 그리스 기본 56·키릴 96·루마니아어 4자 required 승격, ŉ U+0149 recommended 강등, ◌ U+25CC required.

## 1. 파일과 의미

| 파일 | 코드포인트 | 빌더 | QA |
|---|---|---|---|
| `required.txt` | **12,602** | 전부 포함. 주원본(Pretendard)에 없으면 보충원본(Noto Sans KR VF)에서 이식(`docs/spec/07-supplement.md`), 둘 다 없는 4자는 합성 | 게이트 1: 모든 웨이트 cmap 존재 + `.notdef` 아님 + (공백류 제외) 외곽선 있음 |
| `recommended.txt` | 898 | `(주원본 ∪ 보충원본) ∩ 파일` 만 유지. 3차 원본에서 채우지 않음 | 보유 수 보고(기대 548) |
| `korean-old.txt` | 103 | 상동(전부 Noto 보유) | 보고만(범위 밖 후보) |

**빌드 대상 = required ∪ recommended ∪ korean-old (∩ 원본 보유)**, 게이트는 required 100% 만(팀장 결정 ①). 세 파일은 서로 겹치지 않는다(`count.py` 검사).

## 2. 형식 규약 (빌더 `tools/charset.py` · QA 커버리지 스크립트의 계약)

```
# 주석 줄
U+XXXX          # 설명            ← 단일 코드포인트
U+XXXX-U+YYYY   # 설명            ← 폐구간(양끝 포함). 시작 ≤ 끝
```
- 16진 4~6자리, 대소문자 무관. 구간은 반드시 `U+XXXX-U+YYYY`(끝값에도 `U+`). CSS `unicode-range`(`U+AC00-D7A3`) 와 다르니 빌더가 변환.
- `#` 이후 주석. 빈 줄 무시. 설명에 언어 코드(ISO 639-1)·용도·근거(`[KS r/c]` = KS X 1001 행/열).
- 파일 내 중복은 경고(집합 합침), 파일 간 겹침은 오류(종료 코드 1). 미할당 코드포인트는 경고 — 현재 세 파일 모두 **미할당 0**.
- 참조 구현: `scripts/count.py` 의 `parse_file()`.

## 3. 설계 판단과 근거

### 3-1. 한글
| 판단 | 근거 |
|---|---|
| 완성형 U+AC00–D7A3 11,172자 required | AGENTS §1. KS 완성형 2,350(cp949 행16~40 실측)도 포함 |
| 호환 자모 U+3131–318E 94자 required(U+3164 채움 포함) | KS 행4 전체(cp949 실측 94; euc_kr 코덱은 U+3164 만 못 읽음) |
| **Hangul Jamo U+1100–11FF 256자 전부 required** | 팀장 결정 ①(보충원본 전량 보유, 비용 없음). 현대 자모 67+채움 2 는 NFD 텍스트(macOS 파일명) 표시용(unicodedata 실측: 11,172자 NFD 가 쓰는 자모는 정확히 그 67자), 옛자모 187 은 단독 글립만(`ljmo/vjmo/tjmo` 조합은 범위 밖) |
| 자모확장 A/B(A960–A97C, D7B0–D7C6, D7CB–D7FB)·방점(302E–302F) → korean-old | 옛한글 전용, 빌드 대상이나 게이트 밖 |
| 반각 자모 U+FFA0–FFDC → recommended | 레거시 반각 텍스트용(Noto 는 FFA0 만 보유) |
| 한양 PUA 옛한글 → 미포함 | 유니코드 표준 아님 |

### 3-2. 라틴·그리스·키릴 — 언어별 커버 검증 (`scripts/lang_check.py --md`, 2026-09-06)

Latin-1 Supplement(96) + Latin Extended-A(127, ŉ 제외) + Latin Ext-B 4(Șș Țț) 로 아래 언어의 정서법 필수 문자가 전부 required 에 든다. 베트남어만 범위 밖.

| 언어 | 필수 | 블록 | 판정 | 선택 문자 |
|---|---|---|---|---|
| 스페인어 es | 21 | Latin-1+€ | required 전부 | — |
| 포르투갈어 pt | 25 | Latin-1+€ | required 전부 | Ü ü(required) |
| 프랑스어 fr | 35 | Latin-1+Ext-A(Œœ Ÿ)+€ | required 전부 | ‹ ›(required) |
| 독일어 de | 12 | Latin-1+„“+€ | required 전부 | ẞ(U+1E9E, recommended) |
| 이탈리아어 it | 21 | Latin-1+€ | required 전부 | — |
| 네덜란드어 nl | 21 | Latin-1+€ | required 전부 | Ĳ ĳ(required) |
| 폴란드어 pl | 20 | Ext-A(ĄąĆćĘęŁłŃńŚśŹźŻż)+Latin-1 | required 전부 | — |
| 체코어 cs | 32 | Ext-A(ČčĎďĚěŇňŘřŠšŤťŮůŽž)+Latin-1 | required 전부 | — |
| 슬로바키아어 sk | 34 | Ext-A(ĹĺĽľŔŕ …)+Latin-1 | required 전부 | — |
| 헝가리어 hu | 20 | Ext-A(ŐőŰű)+Latin-1 | required 전부 | — |
| 터키어 tr | 12 | Ext-A(ĞğİıŞş)+Latin-1 | required 전부 | — |
| 크로아티아어 hr | 10 | Ext-A | required 전부 | Ǆ–ǌ 9자(recommended) |
| 슬로베니아어 sl | 6 | Ext-A | required 전부 | — |
| **루마니아어 ro** | 10 | Ext-A+**Ext-B(Ș ș Ț ț)**+Latin-1 | **required 전부**(결정 ② 승격) | Ş ş Ţ ţ 세디야형(required) |
| 리투아니아어 lt / 라트비아어 lv / 에스토니아어 et | 18 / 22 / 12 | Ext-A | required 전부 | — |
| 핀란드어 fi / 스웨덴어 sv / 덴마크·노르웨이어 da,no / 아이슬란드어 is | 6 / 6 / 6 / 20 | Latin-1 | required 전부 | Š š Ž ž(required) |
| 카탈루냐어 ca / 갈리시아어 gl / 바스크어 eu | 21 / 14 / 2 | Latin-1 | required 전부 | Ŀ ŀ(required) |
| 몰타어 mt / 웨일스어 cy / 아일랜드어 ga / 에스페란토 eo | 8 / 26 / 10 / 12 | Ext-A·Latin-1 | required 전부 | — |
| 그리스어 el(모노토닉) | 56 기본 required + 악센트 대문자 등 13 recommended | Greek | 기본 required(결정 ②) | Ά Έ Ή Ί Ό Ύ Ώ ΐ ϊ ϋ ό ύ ώ(recommended) |
| 러시아어·우크라이나어 등 키릴 | 96 required | Cyrillic | required(결정 ②) | Ґ ґ(recommended) |
| **베트남어 vi** | 74 | Ext-Add 1EA0–1EF9 + ƠơƯư | **범위 밖** | — |

- 결합문자 13개(U+0300–0304, 0306–0308, 030A–030C, 0327–0328) = Latin-1+Ext-A 전 글자의 NFD 분해에 필요한 집합(unicodedata 계산, 게이트 2 근거).
- ŉ U+0149(KS 9/16)는 유니코드 비권장 문자·Inter/Pretendard 미보유 → 팀장 결정으로 recommended.

### 3-3. 한국 문서용 기호 — KS X 1001 전 영역 매핑 (`scripts/check_ks.py --md`, cp949 디코딩 실측)

| KS X 1001 영역 | 자수 | required | recommended | korean-old | 없음(범위 밖) |
|---|---|---|---|---|---|
| 행1 구두점·수학·특수기호 | 94 | 94 | 0 | 0 | 0 |
| 행2 괄호·화살표·기호·전각 | 71 | 71 | 0 | 0 | 0 |
| 행3 전각 ASCII(FF01–FF5E, ￦) | 94 | 94 | 0 | 0 | 0 |
| 행4 한글 호환 자모(3131–318E) | 94 | 94 | 0 | 0 | 0 |
| 행5 로마숫자·그리스 | 68 | **68** | 0 | 0 | 0 |
| 행6 괘선(박스 드로잉) | 68 | 68 | 0 | 0 | 0 |
| 행7 단위 기호(㎏㎡ 등)·기타 | 79 | 79 | 0 | 0 | 0 |
| 행8 원문자·괄호문자·분수·상첨자 | 91 | 91 | 0 | 0 | 0 |
| 행9 원숫자·괄호숫자·단위 | 94 | 93 | 1 (ŉ) | 0 | 0 |
| 행10 히라가나 | 83 | 0 | 0 | 0 | 83 (범위 밖) |
| 행11 가타카나 | 86 | 0 | 0 | 0 | 86 (범위 밖) |
| 행12 키릴 | 66 | **66** | 0 | 0 | 0 |
| 행16~40 한글 완성형 | 2,350 | 2,350 | 0 | 0 | 0 |
| 행42~93 한자 | 4,888 | 0 | 0 | 0 | 4,888 (범위 밖) |

- KS X 1001 기호·문자 영역(행1~9·12)은 ŉ 1자만 빼고 **전부 required** — KS 완전 호환(결정 ②). 가나·한자는 ROADMAP 범위 밖.
- KS X 1001:2002 추가분 ㉾(U+327E, 0xA2E8)은 Python 코덱이 못 읽어 수동 추가. ㉼㉽(327C–327D)·㈝㈞(321D–321E)는 recommended.
- KS 외 required 추가분: − U+2212, ≈ U+2248, ◌ U+25CC(fontbakery `dotted_circle`, 팀장 승인), ₩ U+20A9, ₹ U+20B9, ⑯–⑳, 2010–2027 구간 완성분, ‹ ›, ⁄ U+2044, ˆ ˜(MacRoman), 결합문자 13, ・ U+30FB.

### 3-4. 전각·반각·CJK 기호·기타 판단
| 범위 | 판단 | 근거 |
|---|---|---|
| 전각 FF01–FF5E(94) + ￠￡￢￣(FFE0–FFE3) + ￥￦(FFE5–FFE6) | required 100 | KS 행3 전체 + 행1·2 의 ＼ ～ ￠￡￢￥ |
| ￤ FFE4, ｟｠ FF5F–60, 반각 기호 FFE8–FFEE, � FFFD | recommended | KS 외 |
| 반각 가타카나 FF61–FF9F | 범위 밖 | 가나 |
| CJK 기호 3000–303F | required 17(KS) / recommended 17 / korean-old 2(방점) | |
| ・ U+30FB | required(가타카나 블록 유일 예외) | 역할 파일 지정·한국어 병렬 표기 관행. Pretendard 보유 |
| 일반 구두점 | required 31 / 나머지 recommended | |
| 공백류 2000–200A·202F·205F, ZW 200B–200D·2060 | recommended | 셰이퍼 기본 무시 또는 공백류 |
| 화폐 | required 3(₩ € ₹) / recommended 30 | |
| 수학·화살표·도형·기타·문자형·숫자형·괘선·블록·원문자·단위 | KS 포함분 required, 블록 잔여 recommended(겹침 없이 계산) | |
| 기술 기호 2300–23FF | required 1(⌒) / recommended 12(⌘ ⌥ ⌫ 등 UI) | |
| 딩뱃 2713–2718 등 12 | recommended | |
| Latin Ext-B/Additional 나머지(ƒ, hr 디그래프, ȷ, cy, ẞ, Ỳỳ) | recommended 20 | |

## 4. 집계표 (`scripts/count.py --md`, 2026-09-06)

| 파일 | 코드포인트(구간 나열) | 할당된 코드포인트 | 미할당 |
|---|---|---|---|
| `required.txt` | 12,602 | **12,602** | 0 |
| `recommended.txt` | 898 | **898** | 0 |
| `korean-old.txt` | 103 | **103** | 0 |

| 블록 | required | recommended | korean-old |
|---|---|---|---|
| ASCII (Basic Latin) | 95 |  |  |
| Latin-1 Supplement | 96 |  |  |
| Latin Extended-A | 127 | 1 |  |
| Latin Extended-B | 4 | 11 |  |
| Spacing Modifier Letters | 9 | 2 |  |
| Combining Diacritical Marks | 13 | 1 |  |
| Greek and Coptic | 56 | 13 |  |
| Cyrillic | 96 | 2 |  |
| Hangul Jamo | 256 |  |  |
| Latin Extended Additional |  | 9 |  |
| General Punctuation | 31 | 27 |  |
| Superscripts and Subscripts | 6 | 36 |  |
| Currency Symbols | 3 | 30 |  |
| Letterlike Symbols | 8 | 20 |  |
| Number Forms | 26 | 23 |  |
| Arrows | 12 | 100 |  |
| Mathematical Operators | 39 | 217 |  |
| Miscellaneous Technical | 1 | 12 |  |
| Enclosed Alphanumerics | 87 | 73 |  |
| Box Drawing | 68 | 60 |  |
| Block Elements | 1 | 31 |  |
| Geometric Shapes | 26 | 70 |  |
| Miscellaneous Symbols | 19 | 18 |  |
| Dingbats |  | 12 |  |
| CJK Symbols and Punctuation | 17 | 17 | 2 |
| Katakana (예외 1자) | 1 |  |  |
| Hangul Compatibility Jamo | 94 |  |  |
| Enclosed CJK Letters and Months | 59 | 34 |  |
| CJK Compatibility | 80 | 16 |  |
| Hangul Jamo Extended-A |  |  | 29 |
| Hangul Syllables | 11,172 |  |  |
| Hangul Jamo Extended-B |  |  | 72 |
| Halfwidth and Fullwidth Forms | 100 | 62 |  |
| Specials |  | 1 |  |

required 12,602 = 한글 11,172 + 호환자모 94 + 자모 256 + 라틴 322(95+96+127+4) + 그리스 56 + 키릴 96 + 결합·악센트 22 + 기호 384 + 전각 100.

## 5. 검증 방법

```
PYTHONUTF8=1 python charset/scripts/count.py                 # 파싱·겹침·미할당 검사 + 집계(오류면 종료코드 1)
PYTHONUTF8=1 python charset/scripts/count.py --md            # §4 표
PYTHONUTF8=1 python charset/scripts/count.py --font <TTF>    # cmap 대비 파일별 커버·누락(블록별) — §6 표의 근거, QA 게이트 1
PYTHONUTF8=1 python charset/scripts/lang_check.py --md       # §3-2 표
PYTHONUTF8=1 python charset/scripts/check_ks.py --md         # §3-3 표 (+ --dump-2350 로 완성형 2,350 목록)
PYTHONUTF8=1 python charset/scripts/ksx1001_symbols.py --codec cp949 --out build/ks-rows.txt   # KS 행1~12 전 셀 덤프
PYTHONUTF8=1 python charset/scripts/measure_sources.py       # 원본 head/hhea/OS/2/post/name/fvar/STAT/GSUB/GPOS 실측(docs/spec 01~06 근거)
PYTHONUTF8=1 python charset/scripts/supplement_ratios.py --wght 400 --md   # 보충 글립 카테고리별 비율(07 근거; --pv 로 100·900)
PYTHONUTF8=1 python charset/scripts/supplement_refs.py 400   # 참조 글립 bbox·사이드베어링·괘선 획(07 근거)
```
QA 게이트 1 = `count.py --font` 를 `dist/static/*.ttf`·`dist/variable/*.ttf` 전부에 돌려 **required 누락 0**.

## 6. 원본 커버리지 실측 (`count.py --font`, 2026-09-06) 과 보충 계획

| 파일 | 총 | Pretendard-Regular.ttf 커버 | Pretendard 누락 | NotoSansKR[wght].ttf 커버 | Noto 누락 | **둘 다 없음** |
|---|---|---|---|---|---|---|
| `required.txt` | 12,602 | 12,054 | 548 | 12,428 | 174 | **4** |
| `recommended.txt` | 898 | 291 | 607 | 391 | 507 | 350 |
| `korean-old.txt` | 103 | 0 | 103 | 103 | 0 | 0 |

**Pretendard 누락(required 548) 블록**: Hangul Jamo 256 · 호환자모(옛) 41 · 원문자·괄호문자(2474–2482, 249C–24B5, 24D0–24E9) 67 · 원·괄호 한글(3200–321B, 3260–327B, 327E, 327F) 58 · 괘선 68 · 수학 26(∀∃∇∈∋∝∠∥∧∨∩∪∬∮∴∵∽≡≪≫⊂⊃⊆⊇⊙⊥ …) · 기타기호 14(☎☏☜☞♀♂♠♣♤♧♨♩♬♭) · 도형 12(▣▤▥▦▧▨▩◈◐◑ …) · 블록 1(▒) · 기술 1(⌒) · CJK 기호 1(〓) · 숫자형 1(⅔) · 전각 2(￢￣). → 544 는 **Noto 에서 이식**, 4 는 합성.
**Noto 누락(required 174)**: Latin Ext-A 97 · Ext-B 4 · 악센트 7 · 결합 8 · 그리스 악센트 7 · 키릴 30 · 구두점 6 · 상하첨자 5 · ₹ · 숫자형 6 · 수학 2(∼ ≒) · 도형 1(◈) — **전부 Pretendard 가 보유**(∼ ≒ ◈ ⅔ 제외).
**둘 다 없음(required 4)**: ⅔ U+2154 · ∼ U+223C · ≒ U+2252 · ◈ U+25C8 → `docs/spec/07-supplement.md` §5: Pretendard 부품 합성(⅔ = 분자·분모 컴포지트, ≒ = = + ·· , ◈ = ◇ + 0.5◆) + ∼ = Noto ∽ 미러. 3차 원본 불필요(폴백 Gothic A1).
**recommended**: Pretendard 291 + Noto 257 = 548 보유 예상, 350 미보유(주로 수학 연산자·화살표 잔여·도형 잔여·문자형·딩뱃) — 채우지 않음.

## 7. 스크립트 목록 (`charset/scripts/`)
| 파일 | 역할 |
|---|---|
| `count.py` | 파서 참조 구현·검증·집계·`--font` 커버리지 |
| `ksx1001_symbols.py` | KS X 1001 행1~12 cp949/euc_kr 디코딩 덤프(근거) |
| `check_ks.py` | KS 전 영역 배치 검증(기호·완성형 2,350·한자) |
| `lang_check.py` | 언어별 정서법 문자 커버 검증 |
| `measure_sources.py` | 원본 폰트 테이블 실측(스펙 01~06 근거) |
| `supplement_ratios.py` | 보충 글립 카테고리별 비율 통계(스펙 07 근거) |
| `supplement_refs.py` | 참조 글립·사이드베어링·괘선 획·3차 후보 실측(스펙 07 근거) |
