# docs/qa/scripts — font-qa 독립 검사 스크립트 (재실행 순서)

저장소 루트에서 실행. 결과는 `docs/qa/results/<이름>.md/.json`, 이미지는 `docs/qa/shots/`. 빌더 코드(`tools/verify_build.py`)와 독립이며 `tools/charset.py`(문자집합 파서)만 임포트한다.

```
PYTHONUTF8=1 python docs/qa/scripts/tickets.py       # ISSUES 티켓 1·2·3·4·6·9·11 재검(fontbakery·빌더 코드와 독립: U+01C4 합성·중첩 컴포지트·Mac 레코드·prep/gasp·변환 컴포넌트·세로 테이블 부재·고아 글립 0)
PYTHONUTF8=1 python docs/qa/scripts/coverage.py      # 게이트 1  required 12,602 × 20 파일(TTF 10 + WOFF2 10) cmap·notdef·외곽선, cmap 동일성
PYTHONUTF8=1 python docs/qa/scripts/shaping.py       # 게이트 2  uharfbuzz: 11,172 음절 각 1자·다국어 문단·결합 시퀀스·NFD·kern/tnum/pnum/frac (WOFF2 는 fontTools 로 풀어 전달)
PYTHONUTF8=1 python docs/qa/scripts/names.py         # 게이트 4·8 name 전 레코드 덤프(docs/qa/name-dump-1.000.md)·spec 02 일치·RFN·LICENSE 1행 바이트 비교·OFL 본문 SHA(네트워크; --offline)
PYTHONUTF8=1 python docs/qa/scripts/metrics.py       # 게이트 5  UPM/typo/hhea/win/fsSelection/macStyle/Panose/underline/gasp/DSIG/피처 49/STAT/fvar/한글 adv 1770
PYTHONUTF8=1 python docs/qa/scripts/supplement.py    # spec 07 §8 보충 글립: 한글류 adv, hangul-pos(원본 기저선차 재현), 참조쌍 비율(기대비 = Noto 실측), 괘선 bbox, 합성 4자, 미러 방향, 룩업 미참조
PYTHONUTF8=1 python docs/qa/scripts/variable.py      # VF: fvar/STAT, instancer 9 웨이트 vs 정적, gvar 튜플, 축 중간값 괘선 (약 4분)
PYTHONUTF8=1 python docs/qa/scripts/web.py           # spec 05  CSS 4종 파싱·url 실존, 슬라이스 정합(⊆·겹침 0·합집합), 크기 목표
PYTHONUTF8=1 python docs/qa/scripts/packages.py      # dist/packages zip 4종: 목록·LICENSE 동봉·SHA256SUMS·index.json·dist 바이트 동일
PYTHONUTF8=1 python docs/qa/scripts/sizes.py         # 게이트 6  파일 크기 표(원본 대비)
PYTHONUTF8=1 python docs/qa/scripts/render.py        # 게이트 7  PIL/FreeType 렌더 시트 9+VF, 괘선 연결 픽셀 검사(07 §4-5(d)), 줄높이 동일
PYTHONUTF8=1 python docs/qa/scripts/browser.py       # 게이트 7  Playwright Chromium: site/test.html 4 모드 스크린샷, docs/qa/pages/page-{A,B,C} 전송량(spec 05 §4)
powershell -ExecutionPolicy Bypass -File docs/qa/scripts/win-install-test.ps1   # 게이트 4·7 Windows 사용자 설치→GDI/DirectWrite 열거→GDI 렌더→제거 확인
python -m fontbakery check-universal dist/static/*.ttf -J 4 --html docs/qa/fontbakery-1.000-static.html --json docs/qa/results/fontbakery-static.json -l WARN
python -m fontbakery check-universal dist/variable/JennySansVariable.ttf -J 1 --html docs/qa/fontbakery-1.000-variable.html --json docs/qa/results/fontbakery-variable.json -l WARN
PYTHONUTF8=1 python docs/qa/scripts/fontbakery_summary.py   # → docs/qa/fontbakery-1.000.md + .html(인덱스)
```

주의
- fontbakery 는 정적 9종과 변수 폰트를 **따로** 돌린다(같이 돌리면 `consistent_family_name`·`family_axis_ranges`·`single_directory` 가 두 패밀리를 섞어 FAIL). `-J` 멀티프로세스는 Windows 에서 끝에서 멈추는 경우가 있어(2회 재현) 변수 폰트는 `-J 1`.
- `win-install-test.ps1` 은 UTF-8 BOM 필수(PowerShell 5.1 이 BOM 없는 UTF-8 을 ANSI 로 읽음). 사용자 범위만 설치하고 끝에 제거·재열거한다. `-KeepInstalled` 로 남겨 둘 수 있다(수동 확인 후 스크립트 재실행으로 제거).
- `browser.py` 는 `python -m http.server 8765` 를 자체 기동한다(이미 떠 있으면 재사용).
- `supplement.py` 는 보충원본 **Noto Sans KR VF 를 웨이트별로 직접 인스턴스**해 기준값을 만든다(서브셋 → `varLib.instancer`,
  캐시 `%TEMP%/jennysans-qa-noto`). 빌더 `tools/verify_build.py:_noto_bottoms()` 와 독립 구현이고 `build/` 를 읽지 않는다.
  첫 실행은 인스턴스 생성으로 1~2분 더 걸리고, 이후 실행은 캐시를 쓴다.
- 2026-09-08 갱신 이력(6차 빌드 반영): `supplement.py` hangul-pos 를 고정 ±15 → `|J차 − 1.965×N차| ≤ 6u`(티켓 5·AGENTS §8),
  참조쌍 기대비를 하드코딩 → Noto 실측; `names.py` 의 Mac(1/0/0) 레코드 기대를 삭제하고 **platformID 1 == 0** 검사로 교체(티켓 3);
  `metrics.py` 는 `prep` 존재를 PASS 로(티켓 4), WOFF2 의 `head.flags 0x0803`(fontTools 압축해제 시 bit 11)을 정상으로;
  `variable.py` 의 합성·컴포지트 목록에 **U+01C4** 추가(티켓 7).
- 2026-09-09 갱신 이력(8차 빌드 반영): `tickets.py` 에 티켓 **9**(vhea/vmtx/VVAR/VORG 가 TTF 10 + WOFF2 10 전부에 없음)·**11**(고아 글립 0) 추가.
  도달성은 **QA 자체 구현**(cmap+UVS ∪ GSUB/GPOS/GDEF/MATH/BASE/JSTF 객체 트리 등장 ∪ 컴포넌트 폐포 ∪ 예약 5종)으로,
  빌더 `fontutil.reachable_glyphs()` 를 쓰지 않고 fontbakery(룩업 출력만 도달로 봄)보다 보수적이다.
  티켓 2 판정을 **VF 포함 중첩 0 = FAIL 기준**으로 강화(6차의 VF INFO 처리 폐기).
  `web.py` 크기 목표를 스펙 05 §4 개정판(CSS gzip ≤110 KB · VF 슬라이스 ≤95 KB · VF 라틴 ≤70 KB)에 맞추고 단위를 KB = 1,000 bytes 로 통일.
