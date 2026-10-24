# -*- coding: utf-8 -*-
"""
게이트 4·8 — name 테이블 전 레코드 덤프, spec 02 문자열 완전 일치, RFN 잔존(식별 레코드·fvar·STAT·글립명·파일명), 고지 레코드 유지,
LICENSE 1행 == name ID 0 1행(바이트 비교), ID 0 2–5행 ↔ LICENSE 원문(spec 06 §2(d)), Pretendard/Noto 고지 부분문자열(06 §2(b)),
OFL 본문 SHA-256 ↔ openfontlicense.org(06 §2(c), 네트워크), THIRD-PARTY 행 수·MANIFEST SHA ↔ sources 실파일(06 §3),
PS 이름 유일성, 파일명 정규식(01 §5), Italic/Oblique 문자열 없음(01 §3), cv/ss FeatureParams UI 이름 존재(04 §2).
덤프: docs/qa/name-dump-1.000.md
실행: PYTHONUTF8=1 python docs/qa/scripts/names.py [--offline]
"""
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402

VENDOR_URL = "https://font.jennysoft.co.kr"
COPYRIGHT_LINES = [
    "Copyright (c) 2026 JennySoft (https://jennysoft.co.kr), with Reserved Font Names 'JennySans' and '제니산스'.",
    "Portions Copyright (c) 2021, Kil Hyung-jin (https://github.com/orioncactus/pretendard), with Reserved Font Name 'Pretendard'.",
    "Portions Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'.",
    "Portions Copyright (c) 2016 The Inter Project Authors (https://github.com/rsms/inter), with Reserved Font Name 'Inter'.",
    "Portions Copyright 2021 The M+ FONTS Project Authors (https://github.com/coz-m/MPLUS_FONTS), with Reserved Font Name 'M PLUS 1'.",
]
VERSION_STR = f"Version {Q.VERSION} (based on Pretendard 1.309; Noto Sans KR 2.004)"
TRADEMARK = ("JennySans is a trademark of JennySoft; Pretendard is a trademark of Kil Hyung-jin; Inter UI and Inter is a trademark of rsms; "
             "Source is a trademark of Adobe in the United States and/or other countries.")
DESIGNER = ("Base glyphs from Inter by Rasmus Andersson; Hangeul glyphs from Noto Sans CJK (Source Han Sans) by Jang Soo-young and Kang Joo-yeon, "
            "Sandoll Communications; combined and redesigned as Pretendard by Kil Hyung-jin; supplementary Hangul jamo and symbol glyphs from Noto Sans KR "
            "(Adobe: Ryoko Nishizuka, Paul D. Hunt, Sandoll Communications); composed and engineered as JennySans by JennySoft.")
DESCRIPTION = ("JennySans is a general-purpose sans-serif type family for Korean (all 11,172 modern Hangul syllables and jamo), Latin (Western and Central "
               "European including Spanish), basic Greek and Cyrillic, and Korean document symbols (KS X 1001). Derived from Pretendard and Noto Sans KR "
               "under the SIL Open Font License 1.1; see LICENSE.")
LICENSE_TXT = "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org"
LICENSE_URL = "https://openfontlicense.org"
EN, KO = (3, 1, 0x409), (3, 1, 0x412)
MAC = (1, 0, 0)
IDENT_IDS = (1, 2, 3, 4, 6, 16, 17, 18, 21, 22, 25)
RFN_PATTERNS = [r"pretendard", r"\bnoto\b", r"\bsource\b", r"\binter\b", r"m ?plus", r"\bplex\b", r"spoqa", r"nanum", r"\bsuit\b",
                r"adobe", r"rsms", r"orioncactus", r"source ?han", r"wanted", r"gothic ?a1"]
FILENAME_RE = re.compile(r"^JennySans(-(Thin|ExtraLight|Light|Regular|Medium|SemiBold|Bold|ExtraBold|Black)|Variable)(\.subset\.\d+)?\.(ttf|woff2)$")


def expected_static(w):
    ribbi = w in ("Regular", "Bold")
    fam1 = "JennySans" if ribbi else f"JennySans {w}"
    ps = f"JennySans-{w}"
    en = {0: "\n".join(COPYRIGHT_LINES), 1: fam1, 2: w if ribbi else "Regular", 3: f"{Q.VERSION};JNSF;{ps}", 4: f"JennySans {w}",
          5: VERSION_STR, 6: ps, 7: TRADEMARK, 8: "JennySoft", 9: DESIGNER, 10: DESCRIPTION, 11: VENDOR_URL,
          12: "https://jennysoft.co.kr", 13: LICENSE_TXT, 14: LICENSE_URL, 16: "JennySans", 17: w}
    ko = {1: "제니산스" if ribbi else f"제니산스 {w}", 4: f"제니산스 {w}", 16: "제니산스"}
    return en, ko


def expected_vf():
    ps = "JennySansVariable-Regular"
    en = {0: "\n".join(COPYRIGHT_LINES), 1: "JennySans Variable", 2: "Regular", 3: f"{Q.VERSION};JNSF;{ps}", 4: "JennySans Variable Regular",
          5: VERSION_STR, 6: ps, 7: TRADEMARK, 8: "JennySoft", 9: DESIGNER, 10: DESCRIPTION, 11: VENDOR_URL,
          12: "https://jennysoft.co.kr", 13: LICENSE_TXT, 14: LICENSE_URL, 16: "JennySans Variable", 17: "Regular", 25: "JennySansVariable"}
    ko = {1: "제니산스 Variable", 4: "제니산스 Variable Regular", 16: "제니산스 Variable"}
    return en, ko


def rec_map(font):
    out = {}
    for r in font["name"].names:
        out[(r.nameID, r.platformID, r.platEncID, r.langID)] = r.toUnicode()
    return out


def check_font(path, rep, dump, license_line1_bytes, license_text):
    f = TTFont(path)
    name = path.name
    recs = rec_map(f)
    stem = path.name.rsplit(".", 1)[0]
    is_vf = "fvar" in f
    if is_vf:
        en, ko = expected_vf()
    else:
        w = stem.split("-", 1)[1]
        en, ko = expected_static(w)
    # 덤프
    dump.append(f"\n### {name}\n\n| ID | plat/enc/lang | 문자열 |\n|---|---|---|")
    for (nid, p, e, l), s in sorted(recs.items()):
        dump.append(f"| {nid} | {p}/{e}/0x{l:X} | {s.replace(chr(10), ' ⏎ ').replace('|', '\\|')} |")
    # spec 02 완전 일치
    mism = []
    for table_, exp in ((EN, en), (KO, ko)):
        for nid, s in exp.items():
            got = recs.get((nid,) + table_)
            if got != s:
                mism.append((nid, table_[2], got, s))
    extra_ids = sorted({k[0] for k in recs if k[0] < 256} - set(en) - {19})
    if mism:
        rep.fail("spec02", f"{name}: 불일치 {len(mism)}건 " + "; ".join(f"ID{n}/0x{l:X}: got={g!r}" for n, l, g, _ in mism[:6]))
    else:
        rep.passed("spec02", f"{name}: en {len(en)}·ko {len(ko)} 레코드 spec 02 문자열 완전 일치")
    if extra_ids:
        rep.warn("spec02", f"{name}: spec 밖 ID<256 레코드 {extra_ids}")
    # Macintosh(platformID 1) 레코드: QA 티켓 3(fontbakery no_mac_entries)에 따라 6차 빌드에서 전부 제거됨 → 0 이어야 한다.
    # ⚠ spec 02 표 6행·§2-2 는 아직 "Mac (1/0/0) ID 1·2·4·6 유지"로 남아 있다 → QA 티켓 8(architect 문서 정정).
    n_mac = sum(1 for k in recs if k[1] == 1)
    (rep.passed if n_mac == 0 else rep.fail)("mac-records", f"{name}: platformID 1(Macintosh) 레코드 {n_mac}건 (기대 0 — 티켓 3)")
    if (19,) + EN in recs:
        rep.info("spec02", f"{name}: ID 19(샘플) = {recs[(19,) + EN]!r} (spec 02 표에 없음, 무해)")
    for k in (18, 21, 22):
        if any(kk[0] == k for kk in recs):
            rep.fail("spec02", f"{name}: ID {k} 기록됨(spec: 기록 안 함)")
    if not is_vf and any(kk[0] == 25 for kk in recs):
        rep.fail("spec02", f"{name}: 정적에 ID 25 기록됨")
    # ID 0 1행 == LICENSE 1행 (바이트)
    id0 = recs.get((0,) + EN, "")
    first = id0.split("\n")[0].encode("utf-8")
    if first == license_line1_bytes:
        rep.passed("license-line1", f"{name}: name ID 0 1행 == LICENSE 1행 (UTF-8 {len(first)} bytes 동일)")
    else:
        rep.fail("license-line1", f"{name}: ID0 1행 {first!r} ≠ LICENSE {license_line1_bytes!r}")
    # ID 0 2–5행: 'Portions ' 떼면 LICENSE 원문(개행→공백) 에 포함
    lic_joined = re.sub(r"\s+", " ", license_text)
    for ln in id0.split("\n")[1:]:
        body = ln[len("Portions "):] if ln.startswith("Portions ") else ln
        if body in lic_joined or body.rstrip(".") in lic_joined:
            rep.passed("license-lines", f"{name}: ID0 '{body[:40]}…' LICENSE 원문 포함")
        else:
            rep.fail("license-lines", f"{name}: ID0 줄 LICENSE 에 없음: {body!r}")
    # RFN 잔존 — 식별 레코드, fvar, STAT, 글립명, 파일명
    pats = [re.compile(p, re.I) for p in RFN_PATTERNS]
    ids = set(IDENT_IDS)
    if is_vf:
        for i in f["fvar"].instances:
            ids.update([i.subfamilyNameID, i.postscriptNameID])
        for a in f["fvar"].axes:
            ids.add(a.axisNameID)
    if "STAT" in f:
        st = f["STAT"].table
        for a in st.DesignAxisRecord.Axis:
            ids.add(a.AxisNameID)
        if st.AxisValueArray:
            for av in st.AxisValueArray.AxisValue:
                ids.add(av.ValueNameID)
        ids.add(st.ElidedFallbackNameID)
    bad = [(k[0], k[3], s) for k, s in recs.items() if k[0] in ids and any(p.search(s) for p in pats)]
    gbad = [g for g in f.getGlyphOrder() if re.search(r"pretendard|noto|sourcehan|sourcesans|\binter\b|mplus|m plus", g, re.I)]
    if bad or gbad:
        rep.fail("rfn", f"{name}: 식별 레코드/fvar/STAT RFN 잔존 {bad[:5]} 글립명 {gbad[:5]}")
    else:
        rep.passed("rfn", f"{name}: 식별 레코드 {sorted(ids)} · 글립명 {len(f.getGlyphOrder())}개 에 원본 RFN 문자열 0건")
    if FILENAME_RE.match(name):
        rep.passed("filename", f"{name}: 파일명 규칙(01 §5) 일치, stem == ID 6 {recs.get((6,) + EN) == stem}")
    else:
        rep.fail("filename", f"{name}: 파일명 규칙 불일치")
    # 고지 레코드 유지
    id7, id9, id13, id14 = recs.get((7,) + EN, ""), recs.get((9,) + EN, ""), recs.get((13,) + EN, ""), recs.get((14,) + EN, "")
    keep = all(k in id0 for k in ("Pretendard", "Adobe", "Inter", "M PLUS 1", "JennySans", "제니산스")) and \
        all(k in id7 for k in ("JennySans", "Pretendard", "Inter", "Source")) and "Pretendard" in id9 and "Noto Sans KR" in id9
    if keep:
        rep.passed("notice", f"{name}: 고지 레코드 ID0(5행)·ID7(상표 4건)·ID9(크레딧) 원저작자 표기 유지")
    else:
        rep.fail("notice", f"{name}: 고지 레코드 누락")
    if id13 == LICENSE_TXT and id14 == LICENSE_URL:
        rep.passed("notice", f"{name}: ID 13/14 정확 일치")
    else:
        rep.fail("notice", f"{name}: ID 13/14 불일치")
    # Italic/Oblique 문자열
    ital = [k for k, s in recs.items() if re.search(r"italic|oblique", s, re.I)]
    if ital:
        rep.fail("italic", f"{name}: Italic/Oblique 문자열 {ital[:3]}")
    else:
        rep.passed("italic", f"{name}: name 에 Italic/Oblique 없음")
    # cv/ss FeatureParams UI 이름
    if "GSUB" in f:
        missing = []
        cnt = 0
        for fr in f["GSUB"].table.FeatureList.FeatureRecord:
            fp = fr.Feature.FeatureParams
            if fp is None:
                continue
            for attr in ("UINameID", "FeatUILabelNameID", "FeatUITooltipTextNameID", "SampleTextNameID"):
                v = getattr(fp, attr, None)
                if v:
                    cnt += 1
                    if (v,) + EN not in recs:
                        missing.append((fr.FeatureTag, attr, v, "en"))
                    if (v,) + KO not in recs:
                        missing.append((fr.FeatureTag, attr, v, "ko"))
        if missing:
            rep.warn("featureparams", f"{name}: FeatureParams 이름 누락 {missing[:6]}")
        else:
            rep.passed("featureparams", f"{name}: cv/ss FeatureParams 참조 {cnt}개 en+ko 레코드 존재")
    # 트레일링 공백·빈 레코드
    tw = [k for k, s in recs.items() if s != s.strip() or s == ""]
    if tw:
        rep.fail("whitespace", f"{name}: 앞뒤 공백/빈 레코드 {tw[:5]}")
    ps = recs.get((6,) + EN)
    inst_ps = []
    if is_vf:
        for i in f["fvar"].instances:
            inst_ps.append(recs.get((i.postscriptNameID,) + EN))
    f.close()
    return ps, inst_ps


def main():
    offline = "--offline" in sys.argv
    rep = Q.Report("name·RFN·라이선스 (게이트 4·8)")
    lic_path = Q.ROOT / "LICENSE"
    lic_bytes = lic_path.read_bytes()
    lic_line1 = lic_bytes.split(b"\n")[0].rstrip(b"\r")
    lic_text = lic_bytes.decode("utf-8")
    rep.info("license", f"LICENSE 1행: {lic_line1.decode('utf-8')!r} ({len(lic_line1)} bytes, BOM {lic_bytes[:3] == b'\\xef\\xbb\\xbf'}, CRLF {b'\\r\\n' in lic_bytes})")
    dump = [f"# name 테이블 전 레코드 덤프 — JennySans {Q.VERSION}", "", "스크립트: docs/qa/scripts/names.py"]
    ps_names = []
    for p in Q.ALL_FONTS:
        if not p.exists():
            rep.fail("file", f"{p} 없음")
            continue
        ps, inst = check_font(p, rep, dump, lic_line1, lic_text)
        if p.suffix == ".ttf":
            ps_names.append(ps)
            ps_names += inst
    # VF 의 name ID 6(JennySansVariable-Regular)과 기본(400) 인스턴스 PS 이름은 같은 폰트를 가리키므로 하나로 센다(spec 02 §4-1)
    uniq = []
    for x in ps_names:
        if x not in uniq:
            uniq.append(x)
    dup = {x for x in ps_names if ps_names.count(x) > 1} - {"JennySansVariable-Regular"}
    if dup or None in ps_names or len(uniq) != 18:
        rep.fail("psname", f"PostScript 이름 중복/누락 {dup} (유일 {len(uniq)}, 기대 18)")
    else:
        rep.passed("psname", f"PostScript 이름 18개(정적 9 + VF 인스턴스 9; VF ID 6 = Regular 인스턴스) 전부 유일: {uniq}")
    # 06 §2(b): Pretendard 저장소 LICENSE 4블록·Noto GF OFL 1행 부분 문자열 포함
    pret = (Q.SOURCES / "Pretendard" / "LICENSE-repo-main.txt").read_text(encoding="utf-8")
    noto = (Q.SOURCES / "NotoSansKR" / "OFL-googlefonts.txt").read_text(encoding="utf-8")
    head_pret = pret.split("This Font Software is licensed")[0].strip()
    blocks = [b.strip() for b in head_pret.split("\n\n") if b.strip()]
    for b in blocks:
        if b.replace("\r\n", "\n") in lic_text:
            rep.passed("license-blocks", f"Pretendard LICENSE 블록 원문 포함: {b.splitlines()[0][:60]}…")
        else:
            rep.fail("license-blocks", f"Pretendard LICENSE 블록 원문 미포함: {b[:60]!r}")
    noto_line = noto.strip().splitlines()[0].strip()
    if noto_line in lic_text:
        rep.passed("license-blocks", f"Noto GF OFL 1행 원문 포함: {noto_line[:70]}")
    else:
        rep.fail("license-blocks", f"Noto GF OFL 1행 미포함: {noto_line!r}")
    # 06 §2(c): OFL 본문 SHA-256 ↔ openfontlicense.org
    body = lic_text.split("-----------------------------------------------------------", 1)[1]
    body = "-----------------------------------------------------------" + body
    norm = lambda t: "\n".join(l.rstrip() for l in t.replace("\r\n", "\n").strip().splitlines())  # noqa: E731
    ours = hashlib.sha256(norm(body).encode("utf-8")).hexdigest()
    rep.info("ofl-body", f"LICENSE OFL 본문(구분선 이후, 줄끝 정규화) SHA-256 {ours}")
    if not offline:
        try:
            import urllib.request
            req = urllib.request.Request("https://openfontlicense.org/documents/OFL.txt", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JennySans-QA/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                remote = r.read().decode("utf-8")
            rb = remote.split("-----------------------------------------------------------", 1)[1]
            rb = "-----------------------------------------------------------" + rb
            theirs = hashlib.sha256(norm(rb).encode("utf-8")).hexdigest()
            if ours == theirs:
                rep.passed("ofl-body", f"OFL 본문 == openfontlicense.org/documents/OFL.txt (SHA-256 {theirs[:16]}…)")
            else:
                # 차이 위치
                a, b = norm(body).splitlines(), norm(rb).splitlines()
                diff = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
                rep.fail("ofl-body", f"OFL 본문 SHA 불일치 ours {ours[:16]} theirs {theirs[:16]}, 첫 차이 줄 {diff}: {a[diff] if diff is not None else ''!r} vs {b[diff] if diff is not None else ''!r}; 줄 수 {len(a)} vs {len(b)}")
        except Exception as e:
            rep.warn("ofl-body", f"openfontlicense.org 다운로드 실패({e}) — 미검증")
    # 06 §3: THIRD-PARTY 표 행 수 = 2, MANIFEST SHA ↔ sources 실파일
    tp = (Q.ROOT / "THIRD-PARTY-NOTICES.md").read_text(encoding="utf-8")
    rows = [l for l in tp.splitlines() if l.startswith("| **")]
    if len(rows) == 2:
        rep.passed("third-party", "THIRD-PARTY-NOTICES 표 원본 행 2 (= AGENTS §5-1 채택 2)")
    else:
        rep.fail("third-party", f"THIRD-PARTY 표 행 {len(rows)}")
    for rel, exp in (("Pretendard/PretendardVariable.ttf", "3090ccde0442bb347aa7685d9ba8b17436a60682df6e8f92a9a670de14056e22"),
                     ("Pretendard/alternative-ttf/Pretendard-Regular.ttf", "6d0af5258997aec7354a6e340fc2325ba321c410ca48b3af858c8c3d6e92a324"),
                     ("Pretendard/alternative-ttf/Pretendard-Bold.ttf", "c16b88c670d23e83fa1170c954cbc4822d3b8dad3c3cde15d798a94b43d97985"),
                     ("NotoSansKR/NotoSansKR[wght].ttf", "194018e6b2b293a7964f037b25c0249ce1418bc9ab3c971060a03aa57861e252")):
        p = Q.SOURCES / rel
        if p.exists():
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            (rep.passed if h == exp else rep.fail)("manifest-sha", f"{rel}: {'일치' if h == exp else '불일치 ' + h[:16]} (THIRD-PARTY/MANIFEST {exp[:16]}…)")
        else:
            rep.warn("manifest-sha", f"{rel} 없음 — 미검증")
    # README 라이선스 절
    readme = (Q.ROOT / "README.md").read_text(encoding="utf-8")
    (rep.passed if ("## 라이선스" in readme or "License" in readme) else rep.fail)("readme", "README.md 라이선스 절 존재")
    (Q.QA_DIR / f"name-dump-{Q.VERSION}.md").write_text("\n".join(dump) + "\n", encoding="utf-8")
    rep.md(f"전 레코드 덤프: `docs/qa/name-dump-{Q.VERSION}.md`")
    rep.write("names")


if __name__ == "__main__":
    main()
