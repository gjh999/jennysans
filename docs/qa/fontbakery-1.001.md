# fontbakery 1.1.0 check-universal — JennySans 1.001

실행: 정적 9종 한 묶음 + 변수 1종 별도(패밀리 검사가 두 패밀리를 섞지 않도록; `JennySans` ≠ `JennySans Variable` 은 팀장 결정 ③).
원본 HTML: `docs/qa/fontbakery-1.001-static.html`, `docs/qa/fontbakery-1.001-variable.html` · JSON: `docs/qa/results/fontbakery-{static,variable}.json`

- **static**: INFO 27, PASS 647, SKIP 318, WARN 55 (검사 실행 1047)
- **variable**: INFO 3, PASS 96, SKIP 20, WARN 8 (검사 실행 127)

## 집계

| 상태 | 수 |
|---|---|
| INFO | 30 |
| PASS | 743 |
| SKIP | 338 |
| WARN | 63 |

## FAIL — 승인 예외 제외 0 검사 ID (전부 티켓 대상)

## FAIL — 승인 예외

- (해당 검사 FAIL 없음 — 아래 WARN 절 참조)

## WARN 9 검사 ID (사유·판단)

### `cjk_chws_feature`

- 설명: Does the font contain chws and vchw features?
- [static] JennySans-Black.ttf: `missing-chws-feature` chws feature not found in font. Use chws_tool (https://github.com/googlefonts/chws_tool) to add it.
- [static] JennySans-Black.ttf: `missing-vchw-feature` vchw feature not found in font. Use chws_tool (https://github.com/googlefonts/chws_tool) to add it.

### `contour_count`

- 설명: Check if each glyph has the recommended amount of contours.
- [static] JennySans-Black.ttf: `contour-count` This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are infered from the typical ammounts of contours observed in a large collection of reference font families. The divergences listed below may simply indicate a significantly different design on some of your glyphs. On the other hand, some of t…

### `file_size`

- 설명: Ensure files are not too large.
- [static] JennySans-Black.ttf: `large-font` Font file is 2.4Mb; ideally it should be less than 1.0Mb
- [static] JennySans-ExtraLight.ttf: `large-font` Font file is 2.5Mb; ideally it should be less than 1.0Mb
- [static] JennySans-Thin.ttf: `large-font` Font file is 2.6Mb; ideally it should be less than 1.0Mb
- [variable] JennySansVariable.ttf: `large-font` Font file is 6.7Mb; ideally it should be less than 1.0Mb

### `interpolation_issues`

- 설명: Detect any interpolation issues in the font.
- [variable] JennySansVariable.ttf: `interpolation-issues` Interpolation issues were found in the font: - Contour order differs in glyph 'uni030B': [0, 1] in wght=100, [1, 0] in wght=199. - Contour order differs in glyph 'uni030B': [0, 1] in wght=600, [1, 0] in wght=699. - Contour 0 start point differs in glyph 'uniE117' between location wght=400 and location wght=100 - Contour 1 start point differs in glyph 'uniE11…

### `mandatory_avar_table`

- 설명: Ensure variable fonts include an avar table.
- [variable] JennySansVariable.ttf: `missing-avar` This variable font does not have an avar table. Most variable fonts should include an avar table to correctly define axes progression rates.

### `math_signs_width`

- 설명: Check math signs have the same width.
- [static] JennySans-Black.ttf: `width-outliers` The most common width is 1374 among a set of 13 math glyphs. The following math glyphs have a different width, though: Width = 1198: logicalnot Width = 1468: uni2284, uni2287, uni228B, uni2209, uni228A, uni2208, uni2282, uni2285, uni220B, uni2286, uni2283 Width = 1387: uni2213, uni2261, uni2262 Width = 1598: uni221D Width = 1404: uni221F Width = 1539: uni227…
- [static] JennySans-Bold.ttf: `width-outliers` The most common width is 1338 among a set of 13 math glyphs. The following math glyphs have a different width, though: Width = 1138: logicalnot Width = 1439: uni2284, uni2287, uni228B, uni2209, uni228A, uni2208, uni2282, uni2285, uni220B, uni2286, uni2283 Width = 1378: uni2213, uni2261, uni2262 Width = 1560: uni221D Width = 1380: uni221F Width = 1501: uni227…
- [static] JennySans-ExtraBold.ttf: `width-outliers` The most common width is 1356 among a set of 13 math glyphs. The following math glyphs have a different width, though: Width = 1168: logicalnot Width = 1452: uni2284, uni2287, uni228B, uni2209, uni228A, uni2208, uni2282, uni2285, uni220B, uni2286, uni2283 Width = 1383: uni2213 Width = 1577: uni221D Width = 1391: uni221F Width = 1518: uni2220 Width = 1313: un…
- [static] JennySans-ExtraLight.ttf: `width-outliers` The most common width is 1250 among a set of 13 math glyphs. The following math glyphs have a different width, though: Width = 992: logicalnot Width = 1390: uni2284, uni2287, uni228B, uni2209, uni228A, uni2208, uni2282, uni2285, uni220B, uni2286, uni2283 Width = 1391: uni2213 Width = 1483: uni221D Width = 1340: uni221F Width = 1423: uni2220 Width = 1299: uni…
- [static] JennySans-Light.ttf: `width-outliers` The most common width is 1266 among a set of 13 math glyphs. The following math glyphs have a different width, though: Width = 1018: logicalnot Width = 1395: uni2284, uni2287, uni228B, uni2209, uni228A, uni2208, uni2282, uni2285, uni220B, uni2286, uni2283 Width = 1390: uni2213 Width = 1492: uni221D Width = 1345: uni221F Width = 1432: uni2220 Width = 1301: un…
- [static] JennySans-Medium.ttf: `width-outliers` The most common width is 1302 among a set of 13 math glyphs. The following math glyphs have a different width, though: Width = 1076: logicalnot Width = 1416: uni2284, uni2287, uni228B, uni2209, uni228A, uni2208, uni2282, uni2285, uni220B, uni2286, uni2283 Width = 1377: uni2213 Width = 1527: uni221D Width = 1360: uni221F, uni3012 Width = 1469: uni2273, uni227…
- [static] JennySans-Regular.ttf: `width-outliers` The most common width is 1284 among a set of 13 math glyphs. The following math glyphs have a different width, though: Width = 1046: logicalnot Width = 1402: uni2284, uni2287, uni228B, uni2209, uni228A, uni2208, uni2282, uni2285, uni220B, uni2286, uni2283 Width = 1376: uni2213 Width = 1506: uni221D Width = 1348: uni221F Width = 1445: uni2220 Width = 1293: un…
- [static] JennySans-SemiBold.ttf: `width-outliers` The most common width is 1320 among a set of 13 math glyphs. The following math glyphs have a different width, though: Width = 1106: logicalnot Width = 1429: uni2284, uni2287, uni228B, uni2209, uni228A, uni2208, uni2282, uni2285, uni220B, uni2286, uni2283 Width = 1379: uni2213 Width = 1545: uni221D Width = 1372: uni221F Width = 1486: uni2220, uni3012 Width =…
- [static] JennySans-Thin.ttf: `width-outliers` The most common width is 1232 among a set of 13 math glyphs. The following math glyphs have a different width, though: Width = 966: logicalnot Width = 1387: uni2284, uni2287, uni2262, uni2209, uni228B, uni228A, uni2208, uni2285, uni220B, uni2286, uni2283, uni2282, uni2261 Width = 1396: uni2213 Width = 1479: uni221D Width = 1339: uni221F Width = 1417: uni2220…
- [variable] JennySansVariable.ttf: `width-outliers` The most common width is 1284 among a set of 13 math glyphs. The following math glyphs have a different width, though: Width = 1046: logicalnot Width = 1402: uni2285, uni2209, uni228B, uni2283, uni220B, uni2208, uni2284, uni2282, uni228A, uni2286, uni2287 Width = 1376: uni2213 Width = 1506: uni221D Width = 1348: uni221F Width = 1445: uni2220 Width = 1293: un…

### `opentype/gdef_mark_chars`

- 설명: Check mark characters are in GDEF mark glyph class.
- [static] JennySans-Bold.ttf: `mark-chars` The following mark characters could be in the GDEF mark glyph class: gravecomb (U+0300), uni0306 (U+0306) and uni0327 (U+0327)

### `overlapping_path_segments`

- 설명: Check there are no overlapping path segments
- [static] JennySans-Black.ttf: `overlapping-path-segments` The following glyphs have overlapping path segments: * uniB6CC (U+B6CC): L<<1338.0,448.0>--<1338.0,446.0>> has the same coordinates as a previous segment. * uniB6E8 (U+B6E8): L<<1340.0,436.0>--<1340.0,434.0>> has the same coordinates as a previous segment. * uniB870 (U+B870): L<<734.0,424.0>--<734.0,418.0>> has the same coordinates as a previous segment. * u…
- [variable] JennySansVariable.ttf: `overlapping-path-segments` The following glyphs have overlapping path segments: * uniAEF4 (U+AEF4): L<<1538.0,-162.0>--<1384.0,-162.0>> has the same coordinates as a previous segment. * uniAEF4 (U+AEF4): L<<1384.0,-162.0>--<1384.0,1616.0>> has the same coordinates as a previous segment. * uniAEF4 (U+AEF4): L<<1384.0,1616.0>--<1538.0,1616.0>> has the same coordinates as a previous segm…

### `soft_hyphen`

- 설명: Does the font contain a soft hyphen?
- [static] JennySans-Black.ttf: `softhyphen` This font has a 'Soft Hyphen' character.

