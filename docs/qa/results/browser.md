# 브라우저 실측 (Playwright Chromium) — test.html 4 모드 + spec 05 §4 페이지 A/B/C

결과: **PASS** (FAIL 0 · WARN 0 · PASS 7 · INFO 27)

| 상태 | 항목 | 내용 |
|---|---|---|
| INFO | server | http.server 8765 기동 (root <repo>) |
| INFO | env | Chromium 151.0.7922.34 |
| PASS | test.html | mode=static: faces 9/loaded 9, check() 실패 [], 폰트 요청 9개 6,539,392 B, 콘솔 오류 0 [] → docs\qa\shots\browser-static.png |
| INFO | test.html | mode=static 상태줄: mode=static · faces declared=9 loaded=9 · 100:ok 200:ok 300:ok 400:ok 500:ok 600:ok 700:ok 800:ok 900:ok |
| PASS | test.html | mode=variable: faces 1/loaded 1, check() 실패 [], 폰트 요청 10개 8,779,268 B, 콘솔 오류 0 [] → docs\qa\shots\browser-variable.png |
| INFO | test.html | mode=variable 상태줄: mode=variable · faces declared=1 loaded=1 · 100:ok 200:ok 300:ok 400:ok 500:ok 600:ok 700:ok 800:ok 900:ok |
| PASS | test.html | mode=subset: faces 891/loaded 287, check() 실패 [], 폰트 요청 287개 3,095,800 B, 콘솔 오류 0 [] → docs\qa\shots\browser-subset.png |
| INFO | test.html | mode=subset 상태줄: mode=subset · faces declared=891 loaded=287 · 100:ok 200:ok 300:ok 400:ok 500:ok 600:ok 700:ok 800:ok 900:ok |
| PASS | test.html | mode=variable-subset: faces 99/loaded 46, check() 실패 [], 폰트 요청 55개 7,965,964 B, 콘솔 오류 0 [] → docs\qa\shots\browser-variable-subset.png |
| INFO | test.html | mode=variable-subset 상태줄: mode=variable-subset · faces declared=99 loaded=46 · 100:ok 200:ok 300:ok 400:ok 500:ok 600:ok 700:ok 800:ok 900:ok |
| INFO | page | page-A static: 요청 2, 1,483,316 B, 오류 0 [] |
| INFO | page | page-A static 파일: [('JennySans-Bold.woff2', 756768), ('JennySans-Regular.woff2', 726548)] |
| INFO | page | page-A variable: 요청 1, 2,239,876 B, 오류 0 [] |
| INFO | page | page-A variable 파일: [('JennySansVariable.woff2', 2239876)] |
| PASS | page | page-A subset: 요청 2, 62,324 B (목표 ≤70 KB, ≤2 요청) 오류 0 |
| INFO | page | page-A subset 파일: [('JennySans-Bold.subset.123.woff2', 31212), ('JennySans-Regular.subset.123.woff2', 31112)] |
| INFO | page | page-A variable-subset: 요청 1, 69,360 B, 오류 0 [] |
| INFO | page | page-A variable-subset 파일: [('JennySansVariable.subset.123.woff2', 69360)] |
| INFO | page | page-B static: 요청 2, 1,483,316 B, 오류 0 [] |
| INFO | page | page-B static 파일: [('JennySans-Bold.woff2', 756768), ('JennySans-Regular.woff2', 726548)] |
| INFO | page | page-B variable: 요청 1, 2,239,876 B, 오류 0 [] |
| INFO | page | page-B variable 파일: [('JennySansVariable.woff2', 2239876)] |
| PASS | page | page-B subset: 요청 24, 279,700 B (목표 ≤300 KB, ≤30 요청) 오류 0 |
| INFO | page | page-B subset 파일: [('JennySans-Bold.subset.118.woff2', 9324), ('JennySans-Regular.subset.118.woff2', 9340), ('JennySans-Bold.subset.119.woff2', 3044), ('JennySans-Bold.subset.114.woff2', 10248), ('JennySans-Bold.subset.108.woff2', 11492), ('JennySans-Bold.subset.117.woff2', 9436), ('JennySans-Bold.subset.123.woff2', 31212), ('JennySans-Regular.subset.123.woff2', 31112), ('JennySans-Regular.subset.116.woff2', 9876), ('JennySans-Regular.subset.119.woff2', 3028), ('JennySans-Regular.subset.113.woff2', 10452), ('JennySans-Regular.subset.114.woff2', 10312), ('JennySans-Regular.subset.117.woff2', 9476), ('JennySans-Regular.subset.111.woff2', 10692), ('JennySans-Regular.subset.107.woff2', 11492), ('JennySans-Regular.subset.108.woff2', 11492), ('JennySans-Regular.subset.115.woff2', 10084), ('JennySans-Regular.subset.110.woff2', 10952), ('JennySans-Regular.subset.63.woff2', 13272), ('JennySans-Bold.subset.116.woff2', 9756), ('JennySans-Regular.subset.109.woff2', 10660), ('JennySans-Regular.subset.106.woff2', 9696), ('JennySans-Regular.subset.112.woff2', 10288), ('JennySans-Regular.subset.122.woff2', 12964)] |
| INFO | page | page-B variable-subset: 요청 17, 468,596 B, 오류 0 [] |
| INFO | page | page-B variable-subset 파일: [('JennySansVariable.subset.123.woff2', 69360), ('JennySansVariable.subset.118.woff2', 21108), ('JennySansVariable.subset.114.woff2', 25388), ('JennySansVariable.subset.108.woff2', 28376), ('JennySansVariable.subset.119.woff2', 5200), ('JennySansVariable.subset.117.woff2', 22000), ('JennySansVariable.subset.116.woff2', 23420), ('JennySansVariable.subset.113.woff2', 25228), ('JennySansVariable.subset.110.woff2', 25960), ('JennySansVariable.subset.111.woff2', 25732), ('JennySansVariable.subset.63.woff2', 35320), ('JennySansVariable.subset.107.woff2', 28960), ('JennySansVariable.subset.115.woff2', 23872), ('JennySansVariable.subset.109.woff2', 26064), ('JennySansVariable.subset.112.woff2', 24672), ('JennySansVariable.subset.106.woff2', 25088), ('JennySansVariable.subset.122.woff2', 32848)] |
| INFO | page | page-C static: 요청 1, 726,548 B, 오류 0 [] |
| INFO | page | page-C static 파일: [('JennySans-Regular.woff2', 726548)] |
| INFO | page | page-C variable: 요청 1, 2,239,876 B, 오류 0 [] |
| INFO | page | page-C variable 파일: [('JennySansVariable.woff2', 2239876)] |
| PASS | page | page-C subset: 요청 27, 310,256 B (목표 ≤400 KB) 오류 0 |
| INFO | page | page-C subset 파일: [('JennySans-Regular.subset.117.woff2', 9476), ('JennySans-Regular.subset.118.woff2', 9340), ('JennySans-Regular.subset.123.woff2', 31112), ('JennySans-Regular.subset.114.woff2', 10312), ('JennySans-Regular.subset.110.woff2', 10952), ('JennySans-Regular.subset.116.woff2', 9876), ('JennySans-Regular.subset.119.woff2', 3028), ('JennySans-Regular.subset.115.woff2', 10084), ('JennySans-Regular.subset.112.woff2', 10288), ('JennySans-Regular.subset.113.woff2', 10452), ('JennySans-Regular.subset.107.woff2', 11492), ('JennySans-Regular.subset.111.woff2', 10692), ('JennySans-Regular.subset.109.woff2', 10660), ('JennySans-Regular.subset.50.woff2', 13080), ('JennySans-Regular.subset.106.woff2', 9696), ('JennySans-Regular.subset.2.woff2', 12200), ('JennySans-Regular.subset.39.woff2', 13412), ('JennySans-Regular.subset.108.woff2', 11492), ('JennySans-Regular.subset.97.woff2', 18468), ('JennySans-Regular.subset.94.woff2', 10948), ('JennySans-Regular.subset.104.woff2', 9368), ('JennySans-Regular.subset.63.woff2', 13272), ('JennySans-Regular.subset.93.woff2', 5396), ('JennySans-Regular.subset.105.woff2', 9968), ('JennySans-Regular.subset.102.woff2', 8960), ('JennySans-Regular.subset.58.woff2', 13432), ('JennySans-Regular.subset.54.woff2', 12800)] |
| INFO | page | page-C variable-subset: 요청 27, 825,044 B, 오류 0 [] |
| INFO | page | page-C variable-subset 파일: [('JennySansVariable.subset.123.woff2', 69360), ('JennySansVariable.subset.114.woff2', 25388), ('JennySansVariable.subset.117.woff2', 22000), ('JennySansVariable.subset.110.woff2', 25960), ('JennySansVariable.subset.119.woff2', 5200), ('JennySansVariable.subset.118.woff2', 21108), ('JennySansVariable.subset.116.woff2', 23420), ('JennySansVariable.subset.115.woff2', 23872), ('JennySansVariable.subset.113.woff2', 25228), ('JennySansVariable.subset.112.woff2', 24672), ('JennySansVariable.subset.111.woff2', 25732), ('JennySansVariable.subset.109.woff2', 26064), ('JennySansVariable.subset.107.woff2', 28960), ('JennySansVariable.subset.106.woff2', 25088), ('JennySansVariable.subset.2.woff2', 32624), ('JennySansVariable.subset.39.woff2', 35376), ('JennySansVariable.subset.50.woff2', 36496), ('JennySansVariable.subset.108.woff2', 28376), ('JennySansVariable.subset.97.woff2', 72056), ('JennySansVariable.subset.63.woff2', 35320), ('JennySansVariable.subset.104.woff2', 22372), ('JennySansVariable.subset.105.woff2', 24572), ('JennySansVariable.subset.93.woff2', 11664), ('JennySansVariable.subset.94.woff2', 62000), ('JennySansVariable.subset.102.woff2', 20376), ('JennySansVariable.subset.58.woff2', 36532), ('JennySansVariable.subset.54.woff2', 35228)] |

## 폰트 요청·전송량 (Playwright response body 합산, 로컬 http.server)

| 페이지 | CSS 모드 | 폰트 요청 | bytes | 목표 | 판정 |
|---|---|---|---|---|---|
| test.html | static | 9 | 6,539,392 | - | - |
| test.html | variable | 10 | 8,779,268 | - | - |
| test.html | subset | 287 | 3,095,800 | - | - |
| test.html | variable-subset | 55 | 7,965,964 | - | - |
| page-A | static | 2 | 1,483,316 | - | - |
| page-A | variable | 1 | 2,239,876 | - | - |
| page-A | subset | 2 | 62,324 | ≤70 KB | PASS |
| page-A | variable-subset | 1 | 69,360 | - | - |
| page-B | static | 2 | 1,483,316 | - | - |
| page-B | variable | 1 | 2,239,876 | - | - |
| page-B | subset | 24 | 279,700 | ≤300 KB | PASS |
| page-B | variable-subset | 17 | 468,596 | - | - |
| page-C | static | 1 | 726,548 | - | - |
| page-C | variable | 1 | 2,239,876 | - | - |
| page-C | subset | 27 | 310,256 | ≤400 KB | PASS |
| page-C | variable-subset | 27 | 825,044 | - | - |
