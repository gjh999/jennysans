# -*- coding: utf-8 -*-
"""
빌드 공용 헬퍼: 로그·SHA·서브셋·OS/2/head/hhea/post 정리·STAT·gasp·meta·코드페이지 비트·요약.
"""
import codecs
import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path

from fontTools import subset
from fontTools.otlLib import builder as otl_builder
from fontTools.ttLib import TTFont, newTable

try:
    from . import config, naming
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import config
    import naming

LOG = logging.getLogger("jennysans")


# ---------------------------------------------------------------- 로그/파일
def setup_logging(step):
    config.LOGS.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = config.LOGS / f"{step}-{ts}.log"
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for h in list(root.handlers):
        root.removeHandler(h)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S")
    fh = logging.FileHandler(path, encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    root.addHandler(fh)
    root.addHandler(sh)
    logging.getLogger("fontTools").setLevel(logging.WARNING)
    LOG.info("log: %s", path)
    return path


def sha256_of(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def read_json(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- 서브셋
# QA 티켓 9(8차): `vhea`/`vmtx`(+세로 변동 테이블 VVAR/VORG)는 **전 파일에서 제거**한다.
#   실측: 원본 Pretendard-Thin/ExtraLight/Light 만 vhea·vmtx 를 갖고 있어(Regular~Black·VF 는 없음) 그대로 실려 왔고,
#   그 결과 9 웨이트 사이가 비대칭이었다. JennySans 는 세로쓰기를 지원하지 않으므로(spec 03) 이 테이블은 불필요하다.
DROP_TABLES_EXTRA = ["DSIG", "FFTM", "TSI0", "TSI1", "TSI2", "TSI3", "TSI5", "prop", "Debg", "TTFA", "BASE",
                     "vhea", "vmtx", "VVAR", "VORG"]
VERTICAL_TABLES = ("vhea", "vmtx", "VVAR", "VORG")
# 도달 불가 글립 검사에서 항상 남기는 예약 글립(fontTools subset 의 recommended_glyphs 와 같은 목록).
KEEP_GLYPHS_ALWAYS = (".notdef", ".null", "NULL", "nonmarkingreturn", "CR")


def subset_options(unicodes, layout=True, hinting=True, glyph_names=True):
    """spec 04 §1 서브셋 옵션. layout=False 는 보충 원본(Noto)에서 외곽선만 가져올 때."""
    o = subset.Options()
    o.layout_features = ["*"] if layout else []
    o.layout_scripts = ["*"]
    o.layout_closure = layout
    o.glyph_names = glyph_names
    o.notdef_outline = True
    o.notdef_glyph = True
    o.recommended_glyphs = True
    o.name_IDs = ["*"]
    o.name_languages = ["*"]
    o.name_legacy = True
    o.hinting = hinting
    o.desubroutinize = False
    o.recalc_bounds = True
    o.recalc_average_width = True
    o.recalc_max_context = True
    o.recalc_timestamp = False
    o.prune_unicode_ranges = True
    o.prune_codepage_ranges = False   # 코드페이지 비트는 우리 규칙(spec 03 §4)으로 직접 계산
    o.drop_tables = list(o.drop_tables) + [t for t in DROP_TABLES_EXTRA if t not in o.drop_tables]
    o.no_subset_tables = list(o.no_subset_tables) + ["meta"]   # 분할본에도 meta(dlng/slng) 유지
    o.ignore_missing_unicodes = True
    o.ignore_missing_glyphs = True
    o.legacy_kern = True
    return o


def subset_font(font, unicodes, glyph_names=(), **kw):
    """font 를 in-place 서브셋. unicodes: iterable(int), glyph_names: 이름으로 추가 요청. 반환: 서브세터."""
    opts = subset_options(unicodes, **kw)
    s = subset.Subsetter(opts)
    s.populate(unicodes=set(unicodes), glyphs=list(glyph_names))
    s.subset(font)
    return s


# ---------------------------------------------------------------- 코드페이지 비트
# (bit, codec, 종류) — spec 03 §4. 한국어 두 비트는 한자·가나 제외(Pretendard 선례; 이유는 BUILD-REPORT 참고)
CODEPAGES = [
    (0, "cp1252", "sb"), (1, "cp1250", "sb"), (2, "cp1251", "sb"), (3, "cp1253", "sb"),
    (4, "cp1254", "sb"), (7, "cp1257", "sb"), (19, "cp949", "kr"), (21, "johab", "kr"), (29, "mac_roman", "sb"),
]
_CP_CACHE = {}


def _printable(cp):
    """제어(<0x20, 0x7F, C1)·PUA 는 코드페이지 판정에서 제외."""
    if cp < 0x20 or cp == 0x7F or 0x80 <= cp <= 0x9F:
        return False
    if 0xE000 <= cp <= 0xF8FF:
        return False
    return True


def codepage_chars(codec, kind):
    """코드페이지가 정의하는 인쇄 문자 집합(set(int)). kr 은 한자(U+4E00–9FFF·CJK 호환)·가나 제외(ROADMAP 범위 밖)."""
    key = (codec, kind)
    if key in _CP_CACHE:
        return _CP_CACHE[key]
    chars = set()
    if kind == "sb":
        for b in range(0x20, 0x100):
            try:
                ch = codecs.decode(bytes([b]), codec)
            except (UnicodeDecodeError, LookupError):
                continue
            if ch and _printable(ord(ch)):
                chars.add(ord(ch))
    else:
        for b in range(0x20, 0x7F):
            chars.add(b)
        for lead in range(0x81, 0xFF):
            for trail in range(0x31, 0xFF):
                try:
                    ch = codecs.decode(bytes([lead, trail]), codec)
                except UnicodeDecodeError:
                    continue
                if len(ch) != 1:
                    continue
                cp = ord(ch)
                if 0x4E00 <= cp <= 0x9FFF or 0xF900 <= cp <= 0xFAFF or (0x3040 <= cp <= 0x30FF and cp != 0x30FB):
                    continue  # 한자·가나 범위 밖(ROADMAP)
                if _printable(cp):
                    chars.add(cp)
    _CP_CACHE[key] = chars
    return chars


# spec 03 §4 (AGENTS §8 채택): (a) 단일바이트 코드페이지 누락 ≤2 → 세트 (b) cp949/johab 은 한자·가나 제외 누락 ≤8 → 세트
# (c) cp1258(bit 8) 은 세우지 않음(베트남어 범위 밖). 그 외 비트 0.
SB_CODEPAGE_TOLERANCE = 2
KR_CODEPAGE_TOLERANCE = 8


def compute_codepage_ranges(cmap_cps):
    r1 = 0
    detail = {}
    for bit, codec, kind in CODEPAGES:
        need = codepage_chars(codec, kind)
        missing = need - cmap_cps
        detail[codec] = (bit, len(need), len(missing), sorted(missing)[:20])
        tol = KR_CODEPAGE_TOLERANCE if kind == "kr" else SB_CODEPAGE_TOLERANCE
        if len(missing) <= tol:
            r1 |= 1 << bit
    return r1, 0, detail


# ---------------------------------------------------------------- 테이블 정리
PREP_ASSEMBLY = ["PUSHW[]", "511", "SCANCTRL[]", "PUSHB[]", "4", "SCANTYPE[]"]


def fix_tables(font, weight_name, weight_value, variable=False):
    """OS/2·head·hhea·post·gasp·meta 를 spec 03 대로. 서브셋·글립 추가가 끝난 뒤 호출."""
    os2 = font["OS/2"]
    head = font["head"]
    hhea = font["hhea"]
    post = font["post"]
    cmap_cps = set(font.getBestCmap())

    os2.usWeightClass = weight_value
    os2.usWidthClass = 5
    os2.fsType = 0
    os2.achVendID = config.VENDOR_ID
    bold = weight_name == "Bold" and not variable
    fs = 0
    if bold:
        fs |= 1 << 5
    else:
        fs |= 1 << 6
    fs |= 1 << 7   # USE_TYPO_METRICS
    fs |= 1 << 8   # WWS
    os2.fsSelection = fs
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = config.TYPO_ASCENDER, config.TYPO_DESCENDER, config.TYPO_LINEGAP
    os2.usWinAscent, os2.usWinDescent = config.WIN_ASCENT, config.WIN_DESCENT
    p = os2.panose
    p.bFamilyType = 2
    p.bSerifStyle = 11
    p.bWeight = config.PANOSE_WEIGHT[weight_value] if not variable else 5
    p.bProportion = 3
    os2.usDefaultChar = 0
    os2.usBreakChar = 0x20
    os2.usFirstCharIndex = min(cmap_cps)
    os2.usLastCharIndex = min(max(cmap_cps), 0xFFFF)
    os2.recalcUnicodeRanges(font)
    os2.ulCodePageRange1, os2.ulCodePageRange2, cp_detail = compute_codepage_ranges(cmap_cps)
    os2.recalcAvgCharWidth(font)
    try:
        from fontTools.otlLib.maxContextCalc import maxCtxFont
        os2.usMaxContext = maxCtxFont(font)
    except Exception as e:  # pragma: no cover
        LOG.warning("usMaxContext 재계산 실패: %s", e)

    hhea.ascent, hhea.descent, hhea.lineGap = config.TYPO_ASCENDER, config.TYPO_DESCENDER, config.TYPO_LINEGAP
    hhea.caretSlopeRise, hhea.caretSlopeRun, hhea.caretOffset = 1, 0, 0

    head.fontRevision = config.FONT_REVISION
    head.flags = config.HEAD_FLAGS
    head.macStyle = 1 if bold else 0

    post.italicAngle = 0.0
    post.underlinePosition = config.UNDERLINE_POSITION
    post.underlineThickness = config.UNDERLINE_THICKNESS
    post.isFixedPitch = 0

    if "prep" not in font:   # QA 티켓 4: 스마트 드롭아웃 제어(gftools fix-nonhinting 과 동일 프로그램)
        from fontTools.ttLib.tables import ttProgram
        prep = newTable("prep")
        prep.program = ttProgram.Program()
        prep.program.fromAssembly(PREP_ASSEMBLY)
        font["prep"] = prep
    if "gasp" not in font:
        gasp = newTable("gasp")
        gasp.version = 1
        gasp.gaspRange = dict(config.GASP_RANGES)
        font["gasp"] = gasp

    meta = newTable("meta")
    meta.data = {"dlng": "Kore, Latn", "slng": "Kore, Latn, Grek, Cyrl"}
    font["meta"] = meta

    for t in DROP_TABLES_EXTRA:
        if t in font:
            del font[t]
    return cp_detail


def build_stat(font, weight_name=None, weight_value=None):
    """STAT 재작성(spec 02 §4-3). weight_name 이 None 이면 변수 폰트(9 값)."""
    if "STAT" in font:
        del font["STAT"]
    values = []
    weights = config.WEIGHTS if weight_name is None else [(weight_name, weight_value)]
    for wn, wv in weights:
        d = dict(value=wv, name=wn)
        if wn == "Regular":
            d["linkedValue"] = 700
            d["flags"] = 0x0002
        values.append(d)
    axes = [dict(tag="wght", name={"en": "Weight", "ko": "굵기"}, ordering=0, values=values)]
    otl_builder.buildStatTable(font, axes, elidedFallbackName=2, windowsNames=True, macNames=False)


# ---------------------------------------------------------------- 글립 추가
def add_glyph(font, name, glyph, advance, lsb, codepoints):
    """glyf/hmtx/cmap/glyphOrder 에 새 글립 추가(서브셋 전에 호출)."""
    glyf = font["glyf"]
    order = font.getGlyphOrder()
    if name in glyf.glyphs:
        raise ValueError(f"글립명 중복: {name}")
    order = list(order) + [name]
    font.setGlyphOrder(order)
    glyf.glyphOrder = order
    glyf.glyphs[name] = glyph
    font["hmtx"].metrics[name] = (advance, lsb)
    if "vmtx" in font:
        font["vmtx"].metrics[name] = (font["head"].unitsPerEm, 0)
    for st in font["cmap"].tables:
        if not st.isUnicode():
            continue
        for cp in codepoints:
            if st.format == 4 and cp > 0xFFFF:
                continue
            st.cmap[cp] = name
    font["maxp"].numGlyphs = len(order)
    if "GDEF" in font and font["GDEF"].table.GlyphClassDef:
        font["GDEF"].table.GlyphClassDef.classDefs[name] = 1


# ---------------------------------------------------------------- 도달 불가 글립 (QA 티켓 11)
def _walk_glyph_names(obj, names, out, seen):
    """otData 객체 트리를 재귀 순회하며 글립명과 일치하는 문자열을 전부 수집한다(보수적 = 과다 포함 쪽으로 안전)."""
    if isinstance(obj, str):
        if obj in names:
            out.add(obj)
        return
    if obj is None or isinstance(obj, (int, float, bytes, bool)):
        return
    oid = id(obj)
    if oid in seen:
        return
    seen.add(oid)
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_glyph_names(k, names, out, seen)
            _walk_glyph_names(v, names, out, seen)
        return
    if isinstance(obj, (list, tuple, set)):
        for v in obj:
            _walk_glyph_names(v, names, out, seen)
        return
    d = getattr(obj, "__dict__", None)
    if d:
        for v in d.values():
            _walk_glyph_names(v, names, out, seen)


def reachable_glyphs(font):
    """실제로 쓰이는 글립 집합. cmap(UVS 포함) ∪ GSUB/GPOS/GDEF/MATH/BASE/JSTF 어디든 등장 ∪ 컴포넌트 폐포 ∪ 예약 글립.
    fontbakery `unreachable_glyphs` 보다 **넓게**(= 안전하게) 잡는다: fontbakery 는 룩업의 출력만 도달로 보지만
    여기서는 룩업의 입력·클래스·앵커 어디에 한 번이라도 이름이 나오면 도달로 친다."""
    order = font.getGlyphOrder()
    names = set(order)
    reach = {n for n in KEEP_GLYPHS_ALWAYS if n in names}
    if order:
        reach.add(order[0])
    for st in font["cmap"].tables:
        if st.format == 14:
            for _vs, d in getattr(st, "uvsDict", {}).items():
                for _base, gname in d:
                    if gname:
                        reach.add(gname)
        else:
            reach.update(st.cmap.values())
    seen = set()
    for tag in ("GSUB", "GPOS", "GDEF", "MATH", "BASE", "JSTF"):
        if tag in font:
            _walk_glyph_names(font[tag].table, names, reach, seen)
    glyf = font["glyf"]
    stack = [n for n in reach if n in names]
    while stack:                                    # 컴포넌트 폐포
        g = glyf[stack.pop()]
        if g.isComposite():
            for c in g.components:
                if c.glyphName not in reach:
                    reach.add(c.glyphName)
                    stack.append(c.glyphName)
    return reach & names


def prune_unreachable(font):
    """QA 티켓 11: 어디에서도 참조되지 않는 고아 글립을 제거한다(cmap·레이아웃·컴포넌트 어디에도 없는 것만).
    티켓 2 평탄화·티켓 6 분해로 부품 참조가 사라지면서 생긴다. 반환: 제거한 글립명 목록."""
    order = list(font.getGlyphOrder())
    reach = reachable_glyphs(font)
    orphans = [n for n in order if n not in reach]
    if not orphans:
        return []
    keep = [n for n in order if n in reach]
    font.setGlyphOrder(keep)                        # glyf.glyphOrder·_reverseGlyphOrderDict 도 함께 갱신됨
    glyf = font["glyf"]
    for n in orphans:
        glyf.glyphs.pop(n, None)
        font["hmtx"].metrics.pop(n, None)
        if "vmtx" in font:
            font["vmtx"].metrics.pop(n, None)
        if "gvar" in font:
            font["gvar"].variations.pop(n, None)
        if "GDEF" in font and getattr(font["GDEF"].table, "GlyphClassDef", None):
            font["GDEF"].table.GlyphClassDef.classDefs.pop(n, None)
    if "post" in font and getattr(font["post"], "glyphOrder", None) is not None:
        font["post"].glyphOrder = keep              # post 2.0 이름표도 남은 글립만 (compile 은 ttFont.getGlyphOrder() 사용)
    font["maxp"].numGlyphs = len(keep)
    LOG.info("고아 글립 제거 %d: %s", len(orphans), orphans)
    return orphans


# ---------------------------------------------------------------- 저장(재시도)
def save_font(font, path, retries=6, wait=5.0):
    """다른 프로세스(QA/release)가 파일을 잡고 있으면 Windows 에서 OSError(22/13)가 난다 → 임시 파일에 쓰고 os.replace, 재시도."""
    import os as _os
    import time as _time
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    font.save(tmp)
    last = None
    for i in range(retries):
        try:
            _os.replace(tmp, path)
            return path
        except OSError as e:
            last = e
            LOG.warning("저장 재시도 %d/%d (%s): %s", i + 1, retries, path.name, e)
            _time.sleep(wait)
    raise last


# ---------------------------------------------------------------- 요약
def glyph_is_empty(font, name):
    g = font["glyf"][name]
    if g.isComposite():
        return False
    return g.numberOfContours == 0


def font_summary(path):
    """BUILD-REPORT 용 요약."""
    p = Path(path)
    f = TTFont(p, lazy=True)
    cmap = f.getBestCmap()
    d = {
        "file": str(p), "bytes": p.stat().st_size, "sha256": sha256_of(p),
        "numGlyphs": f["maxp"].numGlyphs, "cmap": len(cmap), "upm": f["head"].unitsPerEm,
    }
    if "name" in f:
        n = f["name"]
        d["family"] = n.getDebugName(1)
        d["psname"] = n.getDebugName(6)
        d["version"] = n.getDebugName(5)
    if "OS/2" in f:
        o = f["OS/2"]
        d["weightClass"] = o.usWeightClass
        d["typo"] = [o.sTypoAscender, o.sTypoDescender, o.sTypoLineGap]
        d["win"] = [o.usWinAscent, o.usWinDescent]
    if "fvar" in f:
        d["fvar"] = [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in f["fvar"].axes]
        d["instances"] = len(f["fvar"].instances)
    f.close()
    return d


def gsub_feature_tags(font):
    tags = set()
    for tbl in ("GSUB", "GPOS"):
        if tbl in font and font[tbl].table.FeatureList:
            for fr in font[tbl].table.FeatureList.FeatureRecord:
                tags.add(f"{tbl}:{fr.FeatureTag}")
    return tags


def source_date_epoch():
    v = os.environ.get("SOURCE_DATE_EPOCH")
    return int(v) if v else None
