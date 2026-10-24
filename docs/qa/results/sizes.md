# 파일 크기 (게이트 6)

결과: **PASS** (FAIL 0 · WARN 0 · PASS 9 · INFO 1)

| 상태 | 항목 | 내용 |
|---|---|---|
| PASS | static | JennySans-Thin.ttf: 2,700,868 B vs 원본 2,868,924 B (-5.9%), 글립 13983 vs 14716 |
| PASS | static | JennySans-ExtraLight.ttf: 2,671,068 B vs 원본 2,838,808 B (-5.9%), 글립 13983 vs 14716 |
| PASS | static | JennySans-Light.ttf: 2,646,100 B vs 원본 2,813,692 B (-6.0%), 글립 13983 vs 14716 |
| PASS | static | JennySans-Regular.ttf: 2,618,068 B vs 원본 2,725,828 B (-4.0%), 글립 13983 vs 14716 |
| PASS | static | JennySans-Medium.ttf: 2,593,172 B vs 원본 2,701,192 B (-4.0%), 글립 13983 vs 14716 |
| PASS | static | JennySans-SemiBold.ttf: 2,564,392 B vs 원본 2,671,468 B (-4.0%), 글립 13983 vs 14716 |
| PASS | static | JennySans-Bold.ttf: 2,554,304 B vs 원본 2,661,752 B (-4.0%), 글립 13983 vs 14716 |
| PASS | static | JennySans-ExtraBold.ttf: 2,561,880 B vs 원본 2,669,648 B (-4.0%), 글립 13983 vs 14716 |
| PASS | static | JennySans-Black.ttf: 2,557,572 B vs 원본 2,665,004 B (-4.0%), 글립 13983 vs 14716 |
| INFO | variable | JennySansVariable.ttf: 7,012,840 B vs PretendardVariable.ttf 6,739,336 B (+4.1%) — 보충 908 글립 gvar 추가로 증가 허용(게이트 6 은 정적 기준) |

## 정적·변수 (원본 대비)

| 파일 | bytes | 원본 bytes | 증감 | WOFF2 bytes | 글립 | 원본 글립 |
|---|---|---|---|---|---|---|
| JennySans-Thin.ttf | 2,700,868 | 2,868,924 | -5.9% | 647,204 | 13983 | 14716 |
| JennySans-ExtraLight.ttf | 2,671,068 | 2,838,808 | -5.9% | 688,436 | 13983 | 14716 |
| JennySans-Light.ttf | 2,646,100 | 2,813,692 | -6.0% | 713,452 | 13983 | 14716 |
| JennySans-Regular.ttf | 2,618,068 | 2,725,828 | -4.0% | 726,548 | 13983 | 14716 |
| JennySans-Medium.ttf | 2,593,172 | 2,701,192 | -4.0% | 737,832 | 13983 | 14716 |
| JennySans-SemiBold.ttf | 2,564,392 | 2,671,468 | -4.0% | 745,684 | 13983 | 14716 |
| JennySans-Bold.ttf | 2,554,304 | 2,661,752 | -4.0% | 756,768 | 13983 | 14716 |
| JennySans-ExtraBold.ttf | 2,561,880 | 2,669,648 | -4.0% | 759,324 | 13983 | 14716 |
| JennySans-Black.ttf | 2,557,572 | 2,665,004 | -4.0% | 764,144 | 13983 | 14716 |
| JennySansVariable.ttf | 7,012,840 | 6,739,336 | +4.1% | 2,239,876 | 13983 | 14757 |

## 원본 전체 WOFF2 (fontTools 압축, 참고) vs 우리 WOFF2

| 웨이트 | Pretendard TTF→WOFF2 | JennySans WOFF2 | 증감 |
|---|---|---|---|
| Regular | 766,020 | 726,548 | -5.2% |
| Bold | 790,564 | 756,768 | -4.3% |

## 디렉터리 합계

| 디렉터리 | 파일 수 | bytes |
|---|---|---|
| dist\static | 9 | 23,467,424 |
| dist\variable | 1 | 7,012,840 |
| dist\web | 10 | 8,779,268 |
| dist\web\subset | 990 | 14,394,004 |
| dist\css | 4 | 520,325 |
| dist\packages | 6 | 75,704,084 |
