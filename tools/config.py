# -*- coding: utf-8 -*-
"""
JennySans 빌드 상수 (font-builder 소유). 팀장 결정(AGENTS §7·§8)과 docs/spec/ 의 값을 한 곳에 모은다.

- 실행: 항상 프로젝트 루트에서 `PYTHONUTF8=1 python tools/build.py ...`
- 원본(sources/)은 읽기 전용. 중간물은 build/, 릴리스는 dist/.
- 보충 글립 스케일·진행폭은 SUPPLEMENT_CATEGORIES(카테고리별 dict)로 관리한다.
  docs/spec/07-supplement.md 가 확정되면 그 표를 여기에 그대로 옮긴다.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
BUILD = ROOT / "build"
CACHE = BUILD / "cache"
LOGS = BUILD / "logs"
PREVIEW_DIR = BUILD / "preview"
DIST = ROOT / "dist"
DIST_STATIC = DIST / "static"
DIST_VARIABLE = DIST / "variable"
DIST_WEB = DIST / "web"
DIST_WEB_SUBSET = DIST_WEB / "subset"
DIST_CSS = DIST / "css"
CHARSET_DIR = ROOT / "charset"
TOOLS_DATA = ROOT / "tools" / "data"

MANIFEST = SOURCES / "MANIFEST.md"

# ---- 원본 (AGENTS §5-1) ----------------------------------------------------
PRETENDARD_DIR = SOURCES / "Pretendard"
PRETENDARD_TTF_DIR = PRETENDARD_DIR / "alternative-ttf"      # glyf 판 정적 9종 (zip public/static/alternative)
PRETENDARD_VF = PRETENDARD_DIR / "PretendardVariable.ttf"
PRETENDARD_ZIP_URL = "https://github.com/orioncactus/pretendard/releases/download/v1.3.9/Pretendard-1.3.9.zip"
PRETENDARD_ZIP_SHA256 = "04be351a74d6bf7d60c480a3087e51d185485d35a52023142af1df19eb8c428a"
PRETENDARD_VERSION = "1.3.9"          # 릴리스 태그
PRETENDARD_FONT_VERSION = "1.309"     # 원본 name ID 5 (spec 02 §2 "based on Pretendard 1.309")

NOTO_DIR = SOURCES / "NotoSansKR"
NOTO_VF = NOTO_DIR / "NotoSansKR[wght].ttf"
NOTO_VF_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf"
NOTO_VF_SHA256 = "194018e6b2b293a7964f037b25c0249ce1418bc9ab3c971060a03aa57861e252"
NOTO_VERSION = "2.004"

# ---- 패밀리·웨이트 (AGENTS §7, spec 01 §2) -----------------------------------
WEIGHTS = [
    ("Thin", 100), ("ExtraLight", 200), ("Light", 300), ("Regular", 400), ("Medium", 500),
    ("SemiBold", 600), ("Bold", 700), ("ExtraBold", 800), ("Black", 900),
]
WEIGHT_NAMES = [w for w, _ in WEIGHTS]
WEIGHT_VALUE = dict(WEIGHTS)
PANOSE_WEIGHT = {100: 2, 200: 3, 300: 4, 400: 5, 500: 6, 600: 7, 700: 8, 800: 9, 900: 10}

VERSION = "1.001"
FONT_REVISION = 1.001

# ---- 메트릭 (AGENTS §8 2026-09-06, spec 03) ----------------------------------
UPM = 2048
TYPO_ASCENDER, TYPO_DESCENDER, TYPO_LINEGAP = 1950, -494, 0
WIN_ASCENT, WIN_DESCENT = 1950, 494
UNDERLINE_POSITION, UNDERLINE_THICKNESS = -258, 139   # Pretendard-Regular.ttf 실측값으로 전 웨이트 통일(spec 03 §7)
HANGUL_ADVANCE = 1770                                 # Pretendard 한글/호환자모 진행폭 실측
GASP_RANGES = {0xFFFF: 0x000F}                        # 무힌트 TTF 권장값(spec 03 §7)
VENDOR_ID = "JNSF"
HEAD_FLAGS = 0x0003

# ---- 문자집합 ---------------------------------------------------------------
CHARSET_FILES = {
    "required": CHARSET_DIR / "required.txt",
    "recommended": CHARSET_DIR / "recommended.txt",
    "korean-old": CHARSET_DIR / "korean-old.txt",
}
# 빌드 대상 = required ∪ recommended ∪ korean-old (∩ 원본 보유) — 팀장 결정 2026-09-06. 게이트는 required 100%.
BUILD_SETS = ("required", "recommended", "korean-old")
GATE_SET = "required"
# 보충(Noto Sans KR VF 이식) 대상 집합 — 빌드 대상 전부(원본 Pretendard 에 없고 Noto 에 있는 것).
SUPPLEMENT_SETS = BUILD_SETS

# 외곽선이 없어도 되는(공백류·채움문자·default-ignorable) 코드포인트 — 커버리지 검사에서 "빈 글립" 허용
BLANK_ALLOWED = {
    0x0020, 0x00A0, 0x00AD, 0x115F, 0x1160, 0x3000, 0x3164, 0xFFA0, 0xFEFF, 0x2060,
    *range(0x2000, 0x200E), 0x202F, 0x205F, 0x200B, 0x200C, 0x200D,
}

# ---- 보충 글립 규칙 (docs/spec/07-supplement.md §6 → tools/config/supplement.json 그대로) -------------
SUPPLEMENT_JSON = ROOT / "tools" / "config" / "supplement.json"
# 07 §6 규칙표가 덮지 않는 코드포인트 보정(규칙표 뒤에 이어 붙음 = 우선순위 낮음). 아키텍트 확인 요청 사항.
#  - U+2228 ∨ (required): §4-6 표에는 ∧∨ 가 있으나 JSON ranges 가 U+221F–2227, 2229–222A 로 2228 누락
#  - U+25CC ◌ · U+25CE ◎ (required), U+25C9 ◉ (rec): 원형 → circle 규칙(○ 참조)
#  - U+25E2–25E5 ◢◣◤◥ (rec): 삼각 → triangle 규칙(△ 참조)
#  - U+2127 ℧ · U+2135 ℵ (rec): 문자형 → math-letter 규칙(H 참조, 베이스라인)
SUPPLEMENT_RULE_PATCHES = [
    {"name": "math-rel+", "mode": "ref", "ref": "U+2260", "adv": "fit", "sb": 150, "ranges": ["U+2228"]},
    {"name": "circle+", "mode": "ref", "ref": "U+25CB", "adv": "ref", "ranges": ["U+25C9", "U+25CC", "U+25CE"]},
    {"name": "triangle+", "mode": "ref", "ref": "U+25B3", "adv": "ref", "ranges": ["U+25E2-U+25E5"]},
    {"name": "math-letter+", "mode": "ref-baseline", "ref": "U+0048", "adv": "fit", "sb": 150, "ranges": ["U+2127", "U+2135"]},
]
# 규칙표 앞에 끼워 넣는 보정(우선순위 높음). 지금은 비어 있다.
# QA 티켓 5(ㅥ U+3165 하단이 ㄴ 보다 19~25 unit 낮음)로 6차 빌드에 `hangul-compat-baseline`(align_bottom/align_tol) 규칙을 넣었으나,
# 7차에서 **되돌렸다**. 팀장·빌더 실측(`build/ticket5-measure.md`): Noto Sans KR 자신이 ㅥ 을 ㄴ 보다 아래에 그리고(굵을수록 커짐,
# ㄴ 두 개를 붙인 글자의 광학 보정), 우리 결과 편차는 전부 sy(1.965) × Noto 편차와 ≤1.1 unit 으로 일치한다 = 이식이 정확하다는 증거.
# 여기서 ㅥ 을 ㄴ 에 맞춰 올리면 원본 디자인을 임의로 바꾸는 것이라 AGENTS §1-1·§5(외곽선·디자인 변경 금지)에 어긋난다.
# → 결함 아님. 검사식은 `verify_build.check_supplement_spec` 의 hangul-pos 에서 "원본 기저선 차이를 재현했는가"로 정정했다.
SUPPLEMENT_RULE_PATCHES_FIRST = []
# 합성 추가(QA 티켓 1): DŽ U+01C4 = D(U+0044) + Zcaron(U+017D) 컴포지트, 진행폭 = 합 (Pretendard 의 Dž U+01C5 = D + zcaron 와 같은 방식)
SUPPLEMENT_COMPOSITE_PATCHES = {
    "U+01C4": {"sequence": ["U+0044", "U+017D"]},
    # 1.001 (AGENTS §8 2026-10-24) 체크박스 — Pretendard·Noto Sans KR·Source Han Sans KR 모두 미보유(실측) → 자체 부품 합성.
    #   박스 = 같은 웨이트 □ 그대로, 마크 = 같은 웨이트 ✓ / × 균등 축소해 □ 속공간 중앙(여백 max(0.4×박스 획, 72 unit)).
    #   gap 0.3/0.4/0.5 × 9 웨이트 견본 비교 후 0.4 채택(굵은 웨이트에서 마크가 너무 작아지지 않는 값).
    "U+2610": {"box": "U+25A1"},
    "U+2611": {"box": "U+25A1", "mark": "U+2713", "gap": 0.4, "gap_min": 72},
    "U+2612": {"box": "U+25A1", "mark": "U+00D7", "gap": 0.4, "gap_min": 72},
}
# ---- VF 평탄화 채택 판정 (QA 티켓 2, 8차 빌드 — 판정 기준을 spec 07 §7(c) 로 맞춤) -------------
# 07 §7(c) 는 "VF 를 100…900 으로 인스턴스화해 정적 9종과 비교" 할 때 허용치를 **글립 성격에 따라** 둘로 나눈다.
#   · Noto 유래 보충 글립(같은 외곽선의 아핀 변환) → ≤2 unit
#   · 합성·컴포지트(부품이 Pretendard VF 보간 vs 정적 TTF 라 반올림이 누적) → ≤8 unit
# 6차까지는 중첩 컴포지트 평탄화에도 2 unit 을 썼기 때문에 편차 2.0~2.4 unit 인 12 글립을 되돌렸고
# VF 에 `nested_components` FAIL 이 1건 남았다. 평탄화 대상은 전부 **Pretendard 유래 컴포지트**이므로 8 unit 이 맞는 기준이다
# (팀장 결정 AGENTS §8 2026-09-09, QA 권고 docs/qa/ISSUES.md §4-1).
FLATTEN_TOL_NOTO = 2        # Noto 유래 보충 글립
FLATTEN_TOL_COMPOSITE = 8   # 컴포지트 평탄화·분해
SUPPLEMENT_REFS_JSON = BUILD / "supplement-refs-{W}.json"
SUPPLEMENT_SHEET_PNG = BUILD / "supplement-sheet-{W}.png"

# ---- 웹 -------------------------------------------------------------------
GOOGLE_SLICES_CSS = ROOT / "docs" / "research" / "google-kr-slices.css"
SLICES_JSON = TOOLS_DATA / "korean-slices.google.json"
CSS_FAMILY = "JennySans"            # spec 05 §5: 정적·변수 모두 같은 font-family 문자열
CSS_VENDOR_URL = "https://font.jennysoft.co.kr"   # 확정 도메인(사용자 등록·DNS 실측, 2026-09-06)
VENDOR_URL = CSS_VENDOR_URL                         # name ID 11 — naming.py 가 참조
WOFF2_HINTING = False               # 원본이 무힌트 TTF 라 의미 없음(옵션만 유지)

# ---- RFN 검사 (spec 02 §6, 팀장 지시 4) --------------------------------------
# 식별 레코드(name 1/2/3/4/6/16/17/18/21/22/25, fvar 인스턴스명, STAT 이름, 글립명)에서 금지.
# 고지 레코드(0/5/7/9/13/14)에는 원저작자 표기를 유지한다.
RFN_PATTERNS = [
    r"pretendard", r"\bnoto\b", r"\bsource\b", r"\binter\b", r"m ?plus", r"\bplex\b", r"spoqa", r"nanum",
    r"\bsuit\b", r"wanted", r"freesentation", r"paperlogy", r"gothic ?a1",
]
RFN_GLYPHNAME_PATTERNS = [r"Pretendard", r"Noto", r"SourceHan", r"SourceSans", r"\bInter\b", r"MPLUS", r"M PLUS"]
IDENTIFICATION_NAME_IDS = (1, 2, 3, 4, 6, 16, 17, 18, 21, 22, 25)
NOTICE_NAME_IDS = (0, 5, 7, 9, 13, 14)

# 렌더 미리보기
PREVIEW_PNG = PREVIEW_DIR / "JennySans-Regular.png"
