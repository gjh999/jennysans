# -*- coding: utf-8 -*-
"""
name 테이블·fvar·STAT 문자열 (spec 02-naming.md, AGENTS §7, 팀장 지시 2026-09-06).
원본 name 은 전부 버리고 여기 값으로 새로 쓴다. 단 GSUB FeatureParams(ss01~·cv01~ UI 이름)가 참조하는
name ID ≥256 문자열은 보존해 새 ID 로 재매핑한다(spec 04 §1).
"""
import sys
from pathlib import Path

try:
    from . import config
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import config

FAMILY = "JennySans"
FAMILY_KO = "제니산스"
VF_FAMILY = "JennySans Variable"          # 팀장 결정 3 (공백 포함)
VF_FAMILY_KO = "제니산스 Variable"
VF_PS_PREFIX = "JennySansVariable"        # name ID 25, 인스턴스 PS `JennySansVariable-<W>`
VENDOR_ID = config.VENDOR_ID
MANUFACTURER = "JennySoft"
VENDOR_URL = config.VENDOR_URL                  # https://font.jennysoft.co.kr (확정 도메인, tools/config.py)
DESIGNER_URL = "https://jennysoft.co.kr"
# spec 02 §2 확정(2026-09-06): 괄호 안은 원본 폰트의 name ID 5 버전(Pretendard 1.309 = 릴리스 1.3.9)
VERSION_STRING = (f"Version {config.VERSION} (based on Pretendard {config.PRETENDARD_FONT_VERSION}; "
                  f"Noto Sans KR {config.NOTO_VERSION})")

# ID 0 — 원본 저작권 누적(AGENTS §8: Pretendard 저장소 LICENSE 4줄 + Noto KR 은 Adobe 줄과 동일하므로 합침) + 우리 줄.
COPYRIGHT_LINES = [
    # 첫 줄은 LICENSE 정본 문구와 한 글자도 다르지 않아야 한다(팀장 지시 2026-09-06, AGENTS §8)
    "Copyright (c) 2026 JennySoft (https://jennysoft.co.kr), with Reserved Font Names 'JennySans' and '제니산스'.",
    "Portions Copyright (c) 2021, Kil Hyung-jin (https://github.com/orioncactus/pretendard), "
    "with Reserved Font Name 'Pretendard'.",
    "Portions Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'.",
    "Portions Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter), "
    "with Reserved Font Name 'Inter'.",
    "Portions Copyright 2021 The M+ FONTS Project Authors (https://github.com/coz-m/MPLUS_FONTS), "
    "with Reserved Font Name 'M PLUS 1'.",
]
COPYRIGHT = "\n".join(COPYRIGHT_LINES)
# ID 7/9/10 — spec 02 §2 확정 문자열(2026-09-06) 그대로
TRADEMARK = ("JennySans is a trademark of JennySoft; Pretendard is a trademark of Kil Hyung-jin; "
             "Inter UI and Inter is a trademark of rsms; Source is a trademark of Adobe in the United States "
             "and/or other countries.")
DESIGNER = ("Base glyphs from Inter by Rasmus Andersson; Hangeul glyphs from Noto Sans CJK (Source Han Sans) by "
            "Jang Soo-young and Kang Joo-yeon, Sandoll Communications; combined and redesigned as Pretendard by "
            "Kil Hyung-jin; supplementary Hangul jamo and symbol glyphs from Noto Sans KR (Adobe: Ryoko Nishizuka, "
            "Paul D. Hunt, Sandoll Communications); composed and engineered as JennySans by JennySoft.")
DESCRIPTION = ("JennySans is a general-purpose sans-serif type family for Korean (all 11,172 modern Hangul "
               "syllables and jamo), Latin (Western and Central European including Spanish), basic Greek and "
               "Cyrillic, and Korean document symbols (KS X 1001). Derived from Pretendard and Noto Sans KR under "
               "the SIL Open Font License 1.1; see LICENSE.")
LICENSE_TEXT = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                "This license is available with a FAQ at: https://openfontlicense.org")
LICENSE_URL = "https://openfontlicense.org"
SAMPLE_TEXT = "제니산스 JennySans ¿Qué tal, señor? 0123456789"

WIN, WIN_ENC, EN, KO = 3, 1, 0x409, 0x412
MAC, MAC_ENC, MAC_LANG = 1, 0, 0

FEATURE_PARAM_ATTRS = ("UINameID", "FeatUILabelNameID", "FeatUITooltipTextNameID", "SampleTextNameID",
                       "FirstParamUILabelNameID")


def static_names(weight_name, weight_value):
    """정적 폰트 name 문자열(spec 02 §2·§2-1·§2-2). 반환: {(nameID, plat, enc, lang): str}"""
    ribbi = weight_name in ("Regular", "Bold")
    fam1 = FAMILY if ribbi else f"{FAMILY} {weight_name}"
    fam1_ko = FAMILY_KO if ribbi else f"{FAMILY_KO} {weight_name}"
    sub2 = weight_name if ribbi else "Regular"
    ps = f"{FAMILY}-{weight_name}"
    full = f"{FAMILY} {weight_name}"
    full_ko = f"{FAMILY_KO} {weight_name}"
    uid = f"{config.VERSION};{VENDOR_ID};{ps}"
    return _assemble(fam1, sub2, uid, full, ps, FAMILY, weight_name, fam1_ko, full_ko, FAMILY_KO, variable=False)


def variable_names():
    """변수 폰트 name 문자열(spec 02 §4-1 + 팀장 결정 3)."""
    ps = f"{VF_PS_PREFIX}-Regular"
    uid = f"{config.VERSION};{VENDOR_ID};{ps}"
    full = f"{VF_FAMILY} Regular"
    return _assemble(VF_FAMILY, "Regular", uid, full, ps, VF_FAMILY, "Regular",
                     VF_FAMILY_KO, f"{VF_FAMILY_KO} Regular", VF_FAMILY_KO, variable=True)


def _assemble(fam1, sub2, uid, full, ps, fam16, sub17, fam1_ko, full_ko, fam16_ko, variable):
    en = {
        0: COPYRIGHT, 1: fam1, 2: sub2, 3: uid, 4: full, 5: VERSION_STRING, 6: ps, 7: TRADEMARK,
        8: MANUFACTURER, 9: DESIGNER, 10: DESCRIPTION, 11: VENDOR_URL, 12: DESIGNER_URL,
        13: LICENSE_TEXT, 14: LICENSE_URL, 16: fam16, 17: sub17, 19: SAMPLE_TEXT,
    }
    if variable:
        en[25] = VF_PS_PREFIX
    ko = {1: fam1_ko, 2: sub2, 4: full_ko, 16: fam16_ko, 17: sub17}
    # Macintosh(platformID 1) 레코드는 기록하지 않는다 — QA 티켓 3(fontbakery no_mac_entries). Windows 레코드만.
    recs = {}
    for nid, s in en.items():
        recs[(nid, WIN, WIN_ENC, EN)] = s
    for nid, s in ko.items():
        recs[(nid, WIN, WIN_ENC, KO)] = s
    return recs


def collect_feature_param_names(font):
    """GSUB FeatureParams 가 참조하는 name ID → [(plat, enc, lang, string)] (보존 대상)."""
    out = {}
    if "GSUB" not in font:
        return out
    name = font["name"]
    for fr in font["GSUB"].table.FeatureList.FeatureRecord:
        fp = fr.Feature.FeatureParams
        if fp is None:
            continue
        ids = []
        for attr in FEATURE_PARAM_ATTRS:
            v = getattr(fp, attr, None)
            if v:
                ids.append(v)
        n = getattr(fp, "NumNamedParameters", 0) or 0
        first = getattr(fp, "FirstParamUILabelNameID", 0) or 0
        if n and first:
            ids.extend(range(first, first + n))
        for nid in ids:
            if nid in out:
                continue
            out[nid] = [(r.platformID, r.platEncID, r.langID, r.toUnicode()) for r in name.names
                        if r.nameID == nid and r.platformID == WIN]   # Mac 레코드는 보존하지 않음(티켓 3)
    return out


def apply_names(font, records, preserved=None, first_free=256):
    """name 테이블 전면 교체. records: {(nameID, plat, enc, lang): str}. preserved: collect_feature_param_names() 결과.
    반환: {old_id: new_id} (FeatureParams 재매핑에 사용) 와 다음 빈 ID."""
    name = font["name"]
    name.names = []
    for (nid, plat, enc, lang), s in sorted(records.items()):
        name.setName(s, nid, plat, enc, lang)
    remap = {}
    nxt = first_free
    for old in sorted(preserved or {}):
        remap[old] = nxt
        for plat, enc, lang, s in preserved[old]:
            name.setName(s, nxt, plat, enc, lang)
        nxt += 1
    if remap and "GSUB" in font:
        for fr in font["GSUB"].table.FeatureList.FeatureRecord:
            fp = fr.Feature.FeatureParams
            if fp is None:
                continue
            for attr in FEATURE_PARAM_ATTRS:
                v = getattr(fp, attr, None)
                if v and v in remap:
                    setattr(fp, attr, remap[v])
    return remap, nxt


def add_name(font, string, name_id=None, ko=None):
    """≥256 새 레코드(Windows en-US, 선택 ko-KR) 추가 후 ID 반환."""
    name = font["name"]
    if name_id is None:
        name_id = name._findUnusedNameID(256)
    name.setName(string, name_id, WIN, WIN_ENC, EN)
    if ko:
        name.setName(ko, name_id, WIN, WIN_ENC, KO)
    return name_id
