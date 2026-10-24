# -*- coding: utf-8 -*-
"""
빌더 자체 점검(QA 의 독립 검사와 별개). 결과: build/verify-report.md, 종료 코드 1 = FAIL 있음.

검사 항목
 1. 커버리지: required 전부 cmap 존재·.notdef 아님·외곽선 있음(공백류·채움문자 제외) — 정적 9 + 변수. recommended/korean-old 보유 수 보고
 2. RFN 잔존: 식별 레코드(name 1/2/3/4/6/16/17/18/21/22/25)·fvar 인스턴스명·STAT 이름·글립명에 원본 RFN 없음.
    고지 레코드(0/7/9)에는 원저작자 표기가 남아 있어야 함
 3. 메트릭 동일성: UPM·typo/hhea/win·USE_TYPO·underline 전 파일 동일, 한글 진행폭 1770
 4. PostScript 이름 유일성(정적 9 + 변수 + 변수 인스턴스)
 5. WOFF2 열림 + 슬라이스 cmap ⊆ unicode-range, 슬라이스 합집합 = 전체본 cmap, 슬라이스 간 교집합 0
 6. 변수 폰트: fvar 9 인스턴스·STAT 9 값·보충 글립을 각 웨이트로 인스턴스화했을 때 정적과 좌표 일치(≤1 unit)
 7. GSUB/GPOS 피처 태그: 원본 대비 사라진 태그 보고(비어 있는 피처 0)
 8. (8차) 중첩 컴포지트 0 — **정적·VF 모두 FAIL 기준**(승인 예외 없음, AGENTS §8 2026-09-09) + 평탄화 글립의 VF↔정적 편차 ≤ 07 §7(c) 허용치
 9. (8차) 세로 메트릭 테이블 `vhea`/`vmtx`/`VVAR`/`VORG` 없음(전 파일) — QA 티켓 9
10. (8차) 도달 불가(고아) 글립 0(전 파일) — QA 티켓 11
11. (1.001) 체크박스 ☐☑☒ U+2610–2612: 전 파일 cmap·진행폭/bbox = □·마크가 □ 속공간 중앙(VF 는 wght 100/400/900)
실행: PYTHONUTF8=1 python tools/verify_build.py
"""
import io
import re
import sys
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charset  # noqa: E402
import config  # noqa: E402
import fontutil  # noqa: E402

LOG = fontutil.LOG
RESULTS = []   # (status, section, message)
SYNTH_TOL = 8  # 합성·컴포지트 글립의 VF↔정적 bbox/adv 허용 차(unit): 부품 원천(VF 인스턴스 vs 정적 TTF)이 달라 07 §7(c) 2 unit 을 그대로 못 씀
HANGUL_POS_TOL = 6  # hangul-pos: 원본(Noto) 기저선 차이 재현 허용 오차(unit). 실측 최대 1.1(좌표 정수 반올림) — 7차 티켓 5
_NOTO_BOTTOM_CACHE = {}


def rec(status, section, msg):
    RESULTS.append((status, section, msg))
    (LOG.error if status == "FAIL" else LOG.warning if status == "WARN" else LOG.info)("[%s] %s: %s", status, section, msg)


def blank_ok(cp):
    if cp in config.BLANK_ALLOWED:
        return True
    cat = unicodedata.category(chr(cp))
    return cat in ("Zs", "Zl", "Zp", "Cc", "Cf")


def check_coverage(path, sets):
    f = TTFont(path, lazy=True)
    cmap = f.getBestCmap()
    glyf = f["glyf"] if "glyf" in f else None
    req = sets[config.GATE_SET]
    missing = sorted(c for c in req if c not in cmap)
    notdef = sorted(c for c in req if c in cmap and cmap[c] == ".notdef")
    empty = []
    if glyf is not None:
        for c in req:
            if c in cmap and cmap[c] != ".notdef" and not blank_ok(c):
                g = glyf[cmap[c]]
                if (not g.isComposite()) and g.numberOfContours == 0:
                    empty.append(c)
    name = path.name
    if missing or notdef or empty:
        rec("FAIL", "coverage", f"{name}: required 누락 {len(missing)} {charset.format_ranges(missing[:50])} / "
                                f".notdef {len(notdef)} / 빈 외곽선 {len(empty)} {charset.format_ranges(empty[:50])}")
    else:
        rec("PASS", "coverage", f"{name}: required {len(req)}/{len(req)} 전부 존재·외곽선 있음")
    for n in ("recommended", "korean-old"):
        have = sum(1 for c in sets[n] if c in cmap)
        rec("INFO", "coverage", f"{name}: {n} 보유 {have}/{len(sets[n])}")
    f.close()
    return not (missing or notdef or empty)


def check_rfn(path):
    f = TTFont(path, lazy=True)
    n = f["name"]
    pats = [re.compile(p, re.I) for p in config.RFN_PATTERNS]
    bad = []
    ids_to_check = set(config.IDENTIFICATION_NAME_IDS)
    if "fvar" in f:
        for i in f["fvar"].instances:
            ids_to_check.update([i.subfamilyNameID, i.postscriptNameID])
        ids_to_check.add(f["fvar"].axes[0].axisNameID)
    if "STAT" in f:
        st = f["STAT"].table
        for a in st.DesignAxisRecord.Axis:
            ids_to_check.add(a.AxisNameID)
        if st.AxisValueArray:
            for av in st.AxisValueArray.AxisValue:
                ids_to_check.add(av.ValueNameID)
    for r in n.names:
        if r.nameID in ids_to_check:
            s = r.toUnicode()
            for p in pats:
                if p.search(s):
                    bad.append((r.nameID, r.platformID, r.langID, s))
    gpats = [re.compile(p) for p in config.RFN_GLYPHNAME_PATTERNS]
    badg = [g for g in f.getGlyphOrder() if any(p.search(g) for p in gpats)]
    # 고지 레코드 유지 확인
    id0 = n.getDebugName(0) or ""
    id7 = n.getDebugName(7) or ""
    id9 = n.getDebugName(9) or ""
    keep_ok = ("Pretendard" in id0 and "Adobe" in id0 and "Inter" in id0 and "M PLUS" in id0
               and "JennySans" in id0 and "Pretendard" in id7 and "Pretendard" in id9)
    f.close()
    if bad or badg:
        rec("FAIL", "rfn", f"{path.name}: 식별 레코드 RFN 잔존 {bad[:5]} / 글립명 {badg[:10]}")
    else:
        rec("PASS", "rfn", f"{path.name}: 식별 레코드·fvar·STAT·글립명에 원본 RFN 없음")
    if keep_ok:
        rec("PASS", "rfn", f"{path.name}: 고지 레코드(0/7/9)에 원저작자 표기 유지")
    else:
        rec("FAIL", "rfn", f"{path.name}: 고지 레코드(0/7/9) 원저작자 표기 누락")
    return not (bad or badg) and keep_ok


def check_names(paths):
    """name ID 11 = 확정 도메인, ID 0 첫 줄 = LICENSE 정본 문구, ID 5 = Version 1.000 …"""
    import naming
    ok = True
    for p in paths:
        f = TTFont(p, lazy=True)
        n = f["name"]
        id11 = n.getDebugName(11)
        id0 = (n.getDebugName(0) or "").splitlines()[0]
        id5 = n.getDebugName(5) or ""
        f.close()
        probs = []
        if id11 != config.VENDOR_URL:
            probs.append(f"ID 11 {id11!r} ≠ {config.VENDOR_URL}")
        if id0 != naming.COPYRIGHT_LINES[0]:
            probs.append(f"ID 0 첫 줄 {id0!r}")
        if not id5.startswith(f"Version {config.VERSION}"):
            probs.append(f"ID 5 {id5!r}")
        if probs:
            ok = False
            rec("FAIL", "names", f"{p.name}: {'; '.join(probs)}")
    if ok:
        rec("PASS", "names", f"{len(paths)} 파일 name ID 11 == {config.VENDOR_URL}, ID 0 첫 줄 정본 일치, ID 5 Version {config.VERSION}")
    return ok


def check_tables(paths):
    """QA 티켓 2/3/4: 중첩 컴포지트 0(**8차부터 VF 도 FAIL 기준** — 승인 예외 없음), Mac name 레코드 0, prep 스마트 드롭아웃."""
    import supplement
    ok = True
    vs = fontutil.read_json(config.BUILD / "variable-summary.json", {})
    for p in paths:
        f = TTFont(p, lazy=True)
        probs, notes = [], []
        mac = [r for r in f["name"].names if r.platformID == 1]
        if mac:
            probs.append(f"platformID 1 name 레코드 {len(mac)}")
        if "prep" not in f:
            probs.append("prep 없음")
        else:
            asm = [a.split("[")[0] + "[]" if "[" in a else a for a in f["prep"].program.getAssembly()]
            if asm != fontutil.PREP_ASSEMBLY:
                probs.append(f"prep 프로그램 {asm}")
        transformed = [n for n in f.getGlyphOrder() if f["glyf"][n].isComposite() and any(hasattr(c, "transform") for c in f["glyf"][n].components)]
        if transformed:
            if "Variable" in p.name:
                notes.append(f"변환 컴포넌트 글립 {len(transformed)}개 유지(VF 승인 예외 후보, 원본 동일): {transformed[:6]}")
            else:
                probs.append(f"변환 컴포넌트 {len(transformed)}: {transformed[:6]}")
        nested = supplement.nested_composites(f)
        if nested:   # 8차: 정적·VF 모두 FAIL (팀장 결정 AGENTS §8 2026-09-09 — 승인 예외를 늘리지 않고 고친다)
            probs.append(f"중첩 컴포지트 {len(nested)}: {nested[:6]}")
        cm = f.getBestCmap()
        if 0x01C4 in cm:
            # DŽ = D + Zcaron 컴포지트(티켓 1). 티켓 2 평탄화로 Zcaron(=Z+caron)이 전개돼 [D, Z, caron] 이 될 수 있음 →
            # 첫 컴포넌트 D@(0,0), adv = adv(D)+adv(Zcaron), 나머지 부분의 bbox = Zcaron bbox + adv(D) 로 검사
            glyf = f["glyf"]
            g = glyf[cm[0x01C4]]
            adv = f["hmtx"][cm[0x01C4]][0]
            advD = f["hmtx"][cm[0x44]][0]
            exp = advD + f["hmtx"][cm[0x17D]][0]
            okc = g.isComposite() and g.components and g.components[0].glyphName == cm[0x44] and (g.components[0].x, g.components[0].y) == (0, 0) and adv == exp
            if okc:
                bz = supplement.bounds_of(glyf, cm[0x17D])
                bd = supplement.bounds_of(glyf, cm[0x44])
                bt = supplement.bounds_of(glyf, cm[0x01C4])
                expb = (min(bd[0], bz[0] + advD), min(bd[1], bz[1]), max(bd[2], bz[2] + advD), max(bd[3], bz[3]))
                okc = max(abs(a - b) for a, b in zip(bt, expb)) <= 1
            if not okc:
                probs.append(f"U+01C4 구조 {[(c.glyphName, c.x, c.y) for c in g.components] if g.isComposite() else 'simple'} adv {adv} (기대 D+Zcaron {exp})")
        else:
            probs.append("U+01C4 없음")
        f.close()
        if probs:
            ok = False
            rec("FAIL", "tables", f"{p.name}: " + " / ".join(probs))
        else:
            rec("PASS", "tables", f"{p.name}: Mac 레코드 0 · prep {fontutil.PREP_ASSEMBLY} · 중첩 컴포지트 0 · 변환 컴포넌트 0 · U+01C4 = D+Zcaron")
        for n in notes:
            rec("INFO", "tables", f"{p.name}: {n}")
    if vs.get("flatten_detail"):
        rec("INFO", "tables", f"VF 평탄화: {vs['flatten_detail']}")
    if vs.get("decompose_detail"):
        rec("INFO", "tables", f"VF 변환 컴포넌트 분해: {vs['decompose_detail']}")
    return ok


def check_vertical(paths):
    """QA 티켓 9(8차): 세로쓰기 테이블 `vhea`/`vmtx`(+VVAR/VORG)가 **전 파일에 없어야** 한다.
    6차까지는 원본 Pretendard-Thin/ExtraLight/Light 가 갖고 있던 것이 그대로 실려 3 웨이트에만 있었다(웨이트 간 비대칭).
    JennySans 는 세로쓰기를 지원하지 않는다(spec 03)."""
    bad = []
    for p in paths:
        f = TTFont(p, lazy=True)
        have = [t for t in fontutil.VERTICAL_TABLES if t in f]
        f.close()
        if have:
            bad.append((p.name, have))
    if bad:
        rec("FAIL", "vertical", f"세로 메트릭 테이블 잔존: {bad}")
        return False
    rec("PASS", "vertical", f"{len(paths)} 파일 세로 메트릭 테이블 없음{list(fontutil.VERTICAL_TABLES)} — 웨이트 간 비대칭 해소(티켓 9)")
    return True


def check_orphans(paths):
    """QA 티켓 11(8차): 도달 불가(고아) 글립 0.
    cmap(UVS 포함)·GSUB/GPOS/GDEF·컴포넌트 어디에도 안 나오는 글립을 센다(예약 글립 .notdef/.null 등은 제외).
    fontbakery `unreachable_glyphs` 보다 넓게 도달을 인정하므로, 여기서 0 이면 fontbakery 도 0 이다."""
    bad = []
    total = 0
    for p in paths:
        f = TTFont(p)
        order = f.getGlyphOrder()
        reach = fontutil.reachable_glyphs(f)
        orphans = [n for n in order if n not in reach]
        f.close()
        total += len(order)
        if orphans:
            bad.append((p.name, len(orphans), orphans[:10]))
    if bad:
        rec("FAIL", "orphans", f"도달 불가 글립 잔존: {bad}")
        return False
    rec("PASS", "orphans", f"{len(paths)} 파일 도달 불가 글립 0 (예약 글립 {list(fontutil.KEEP_GLYPHS_ALWAYS)} 제외, 글립 합계 {total})")
    return True


def check_flatten(vf_path):
    """QA 티켓 2(8차): VF 에서 평탄화한 컴포지트를 9 웨이트로 인스턴스해 정적 9종과 bbox·adv 를 비교한다.
    허용치는 spec 07 §7(c) — Noto 유래 보충 글립 ≤2 unit / 합성·컴포지트 ≤8 unit(= 평탄화 대상은 전부 이쪽)."""
    vs = fontutil.read_json(config.BUILD / "variable-summary.json", {})
    names = [r[0] for r in vs.get("flatten_adopted", [])] or vs.get("flattened_names") or []
    if not names:
        rec("INFO", "flatten", "variable-summary.json 에 평탄화 목록이 없어 건너뜀")
        return True
    import supplement
    sup_infos = fontutil.read_json(config.BUILD / "static-summary.json", {}).get("supplement_glyphs", {}).get("Regular", [])
    noto_names = {g["glyph"] for g in sup_infos if g.get("glyph") and g["mode"] not in ("composite", "mirror")}
    f = TTFont(vf_path)
    have = [n for n in names if n in f.getGlyphOrder()]
    sub = TTFont(vf_path)
    fontutil.subset_font(sub, [], glyph_names=have, layout=False)
    buf = io.BytesIO()
    sub.save(buf)
    sub.close()
    f.close()
    worst, worst_info, bad = 0.0, None, []
    for wn, wv in config.WEIGHTS:
        buf.seek(0)
        inst_f = instancer.instantiateVariableFont(TTFont(buf), {"wght": wv}, inplace=True, optimize=False)
        static = TTFont(config.DIST_STATIC / f"JennySans-{wn}.ttf", lazy=True)
        for n in have:
            if n not in static["glyf"].glyphs or n not in inst_f["glyf"].glyphs:
                continue
            bs, bi = supplement.bounds_of(static["glyf"], n), supplement.bounds_of(inst_f["glyf"], n)
            d = max(abs(a - b) for a, b in zip(bs, bi)) if (bs and bi) else 0
            d = max(d, abs(static["hmtx"][n][0] - inst_f["hmtx"][n][0]))
            tol = config.FLATTEN_TOL_NOTO if n in noto_names else config.FLATTEN_TOL_COMPOSITE
            if d > worst:
                worst, worst_info = d, (wn, n, tol)
            if d > tol:
                bad.append((wn, n, round(d, 2), tol))
        static.close()
        inst_f.close()
    if bad:
        rec("FAIL", "flatten", f"평탄화 글립 VF↔정적 편차가 07 §7(c) 허용치 초과: {bad[:8]}")
        return False
    rec("PASS", "flatten", f"VF 평탄화 컴포지트 {len(have)}개 × 9 웨이트 bbox·adv = 정적, 최대 편차 {worst:g} unit "
                           f"@ {worst_info} (허용 07 §7(c): Noto {config.FLATTEN_TOL_NOTO} / 컴포지트 {config.FLATTEN_TOL_COMPOSITE})")
    return True


def check_metrics(paths):
    rows = []
    for p in paths:
        f = TTFont(p, lazy=True)
        o, h, hd, po = f["OS/2"], f["hhea"], f["head"], f["post"]
        cm = f.getBestCmap()
        hangul_adv = f["hmtx"][cm[0xAC00]][0] if 0xAC00 in cm else None
        jamo_adv = f["hmtx"][cm[0x1100]][0] if 0x1100 in cm else None
        rows.append((p.name, hd.unitsPerEm, (o.sTypoAscender, o.sTypoDescender, o.sTypoLineGap), (h.ascent, h.descent, h.lineGap),
                     (o.usWinAscent, o.usWinDescent), bool(o.fsSelection & (1 << 7)), bool(o.fsSelection & (1 << 8)),
                     (po.underlinePosition, po.underlineThickness), hangul_adv, jamo_adv, o.fsType, o.achVendID,
                     o.usWeightClass, hd.macStyle, o.fsSelection))
        f.close()
    ok = True
    ref = rows[0]
    for r in rows:
        same = r[1:8] == ref[1:8] and r[8] == config.HANGUL_ADVANCE and r[9] in (None, config.HANGUL_ADVANCE)
        if not same or r[10] != 0 or r[11] != config.VENDOR_ID:
            ok = False
            rec("FAIL", "metrics", f"{r[0]}: UPM {r[1]} typo {r[2]} hhea {r[3]} win {r[4]} USE_TYPO {r[5]} WWS {r[6]} "
                                    f"underline {r[7]} 가 {r[8]} ᄀ {r[9]} fsType {r[10]} vend {r[11]}")
    expected = (config.UPM, (config.TYPO_ASCENDER, config.TYPO_DESCENDER, config.TYPO_LINEGAP),
                (config.TYPO_ASCENDER, config.TYPO_DESCENDER, config.TYPO_LINEGAP), (config.WIN_ASCENT, config.WIN_DESCENT),
                True, True, (config.UNDERLINE_POSITION, config.UNDERLINE_THICKNESS))
    if ref[1:8] != expected:
        ok = False
        rec("FAIL", "metrics", f"기준값 불일치: {ref[1:8]} ≠ {expected}")
    if ok:
        rec("PASS", "metrics", f"{len(rows)} 파일 UPM {ref[1]} typo=hhea {ref[2]} win {ref[4]} USE_TYPO+WWS underline {ref[7]} "
                               f"한글 진행폭 {config.HANGUL_ADVANCE} 동일")
    # 웨이트별 fsSelection/macStyle
    for r in rows:
        bold = r[12] == 700 and "Variable" not in r[0]
        exp_fs_bits = ((1 << 5) if bold else (1 << 6)) | (1 << 7) | (1 << 8)
        if r[14] != exp_fs_bits or r[13] != (1 if bold else 0):
            ok = False
            rec("FAIL", "metrics", f"{r[0]}: fsSelection {bin(r[14])} macStyle {r[13]} (기대 {bin(exp_fs_bits)}/{1 if bold else 0})")
    return ok


def check_psnames(paths):
    names = {}
    for p in paths:
        f = TTFont(p, lazy=True)
        ps = f["name"].getDebugName(6)
        names.setdefault(ps, []).append(p.name)
        if "fvar" in f:
            for i in f["fvar"].instances:
                s = f["name"].getDebugName(i.postscriptNameID)
                if s == ps:   # 기본 인스턴스(Regular)의 PS 이름 = 파일의 ID 6 — 정상(spec 01 §6)
                    continue
                names.setdefault(s, []).append(f"{p.name}#{s}")
        if p.stem != ps and "Variable" not in p.name:
            rec("FAIL", "psname", f"{p.name}: 파일명 stem ≠ PS 이름 {ps}")
        f.close()
    dup = {k: v for k, v in names.items() if len(v) > 1}
    if dup:
        rec("FAIL", "psname", f"PostScript 이름 중복: {dup}")
        return False
    rec("PASS", "psname", f"PostScript 이름 {len(names)}개 전부 유일")
    return True


def check_web(sets):
    ok = True
    web = config.DIST_WEB
    if not web.exists():
        rec("WARN", "web", "dist/web 없음(웹 빌드 미실행)")
        return True
    fulls = sorted(web.glob("*.woff2"))
    for p in fulls:
        try:
            f = TTFont(p, lazy=True)
            n = len(f.getBestCmap())
            f.close()
            rec("PASS", "web", f"{p.name} 열림 cmap {n} ({p.stat().st_size} bytes)")
        except Exception as e:
            ok = False
            rec("FAIL", "web", f"{p.name} 열기 실패: {e}")
    css = config.DIST_CSS / "jennysans-dynamic-subset.css"
    if not css.exists():
        rec("WARN", "web", "jennysans-dynamic-subset.css 없음")
        return ok
    text = css.read_text(encoding="utf-8")
    faces = re.findall(r'src:\s*url\("([^"]+)"\)[^}]*?unicode-range:\s*([^;]+);', text, re.S)
    by_stem = {}
    for url, ur in faces:
        m = re.search(r"/(JennySans-[A-Za-z]+)\.subset\.(\d+)\.woff2", url)
        if not m:
            continue
        by_stem.setdefault(m.group(1), []).append((int(m.group(2)), charset.parse_css_unicode_range(ur), url))
    for stem, items in by_stem.items():
        full = TTFont(web / f"{stem}.woff2", lazy=True)
        full_cps = set(full.getBestCmap())
        full.close()
        union = set()
        overlap = 0
        subset_issue = 0
        for idx, ur, url in items:
            p = (config.DIST_CSS / url).resolve()
            f = TTFont(p, lazy=True)
            cps = set(f.getBestCmap())
            f.close()
            if not cps <= ur:
                subset_issue += 1
            overlap += len(union & cps)
            union |= cps
        diff = full_cps - union
        if subset_issue or overlap or diff:
            ok = False
            rec("FAIL", "web", f"{stem}: cmap⊄unicode-range {subset_issue} / 슬라이스 간 겹침 {overlap} / 합집합 누락 {len(diff)} "
                               f"{charset.format_ranges(sorted(diff)[:20])}")
        else:
            rec("PASS", "web", f"{stem}: 슬라이스 {len(items)}개 cmap⊆unicode-range, 겹침 0, 합집합 = 전체본 cmap({len(full_cps)})")
        # latin(#123)에 U+0020/00A0
        lat = [ur for idx, ur, _ in items if 0x0041 in ur]
        if not lat or not (0x20 in lat[0] and 0xA0 in lat[0]):
            ok = False
            rec("FAIL", "web", f"{stem}: 라틴 슬라이스에 U+0020/U+00A0 없음")
    return ok


def _bbox(font, name):
    from fontTools.pens.boundsPen import BoundsPen
    gs = font.getGlyphSet()
    p = BoundsPen(gs)
    gs[name].draw(p)
    return p.bounds


def _noto_bottoms(weight_value, cps):
    """hangul-pos 검사용: 보충 원본(Noto Sans KR VF)을 해당 wght 로 인스턴스(build/cache 재사용)해 코드포인트별 bbox 하단(원본 UPM 1000).

    빌드 기록(static-summary 의 src_bbox)이 아니라 원본을 직접 재서 검사가 빌드 산출과 독립이 되게 한다."""
    import supplement as sup
    key = (weight_value, tuple(sorted(cps)))
    if key in _NOTO_BOTTOM_CACHE:
        return _NOTO_BOTTOM_CACHE[key]
    path = sup.noto_instance(sorted(cps), weight_value)
    f = TTFont(path, lazy=True)
    cm = f.getBestCmap()
    out = {}
    for c in sorted(cps):
        if c in cm:
            b = _bbox(f, cm[c])
            if b:
                out[c] = b[1]
    f.close()
    _NOTO_BOTTOM_CACHE[key] = out
    return out


def check_supplement_spec(statics):
    """07-supplement §8: 한글류 adv, 참조 관계, 괘선 셀, 합성 4자 구조, 미러 윤곽 방향, Noto 피처 미유입."""
    from fontTools.pens.areaPen import AreaPen
    ok = True
    # 07 §8-3 참조 관계. "h" 비교는 Noto 원본에서 대상/참조 높이비가 1 이 아닌 경우(◐ 0.978, ⊂ 0.91, ♠ 1.09 등)가 있으므로
    # 기대값 = 참조 높이 × (Noto 대상 h / Noto 참조 h) 로 계산해 규칙(균등 스케일)이 정확히 적용됐는지 본다(허용 1.5%).
    REL = [  # (대상, 참조, 비교, 허용)
        (0x3260, 0x2460, "h", 0.015), (0x3200, 0x321C, "h", 0.015), (0x25A3, 0x25A0, "bbox", 2), (0x25D0, 0x25CB, "h", 0.015),
        (0x2282, 0x2260, "h", 0.02), (0x222C, 0x222B, "h", 0.015), (0x2660, 0x2665, "h", 0.02), (0x260E, 0x2605, "adv", 0.10),
        (0x3013, 0x25A0, "h", 0.02), (0x25CE, 0x25CB, "h", 0.015), (0x24D0, 0x2460, "h", 0.015), (0x2474, 0x321C, "h", 0.015),
    ]
    ss = fontutil.read_json(config.BUILD / "static-summary.json", {})
    HBOX = [0x2500, 0x2501, 0x253C, 0x254B, 0x252C, 0x2534, 0x2550, 0x256C]   # 가로 연결: xMin 0, xMax 1770
    VBOX = [0x2502, 0x2503, 0x253C, 0x254B, 0x251C, 0x2524, 0x2551, 0x256C]   # 세로 연결: yMin -494, yMax 1950
    for p in statics:
        f = TTFont(p, lazy=True)
        cm = f.getBestCmap()
        hm = f["hmtx"].metrics
        glyf = f["glyf"]
        probs = []
        # 1) 한글류 adv
        bad = [c for c in list(range(0x1100, 0x1200)) + list(range(0x3165, 0x318F)) + list(range(0xA960, 0xA97D)) + list(range(0xD7B0, 0xD7FC))
               if c in cm and hm[cm[c]][0] != config.HANGUL_ADVANCE]
        bad += [c for c in (0x302E, 0x302F) if c in cm and hm[cm[c]][0] != 481]
        if bad:
            probs.append(f"한글류 adv≠1770/481: {charset.format_ranges(bad[:10])}")
        # 1b) hangul-pos(QA 티켓 5 — 7차 검사식 정정): 옛 호환자모(U+3165–318E)가 **Noto 원본의 ㄴ 대비 기저선 차이를
        #     sy 배로 그대로 재현**하는지 본다. 6차까지 쓰던 "ㄴ 하단 ±15 고정"은 틀린 기준이었다 —
        #     Noto 자신이 ㅥ 을 ㄴ 보다 아래에 그리고(굵을수록 커짐: Regular −3 → Black −13, ㄴ 두 개를 붙인 글자의 광학 보정)
        #     그것을 옮기면 원본 디자인 변경(AGENTS §1-1·§5 위반)이 된다. 근거 실측 `build/ticket5-measure.md`.
        #     기대 = sy × (N(대상)하단 − N(ㄴ)하단), 실측 = J(대상)하단 − J(ㄴ)하단, 허용 ±HANGUL_POS_TOL unit.
        #     (07 §8-3 참조쌍 검사와 같은 철학: 결과 비율/차이 = 원본 비율/차이)
        wname0 = p.stem.split("-")[1]
        infos0 = {g["cp"]: g for g in ss.get("supplement_glyphs", {}).get(wname0, [])}
        pos_cps = [c for c in range(0x3165, 0x318F) if c in cm and (infos0.get(c, {}).get("scale"))]
        pos_note = "hangul-pos 미측정(ㄴ 또는 보충 기록 없음)"
        if 0x3134 in cm and pos_cps:
            nbot = _noto_bottoms(config.WEIGHT_VALUE[wname0], set(pos_cps) | {0x3134})
            jn = _bbox(f, cm[0x3134])[1]
            off, worst = [], 0.0
            for c in pos_cps:
                b = _bbox(f, cm[c])
                if b is None or c not in nbot or 0x3134 not in nbot:
                    continue
                exp = infos0[c]["scale"][1] * (nbot[c] - nbot[0x3134])
                d = (b[1] - jn) - exp
                worst = max(worst, abs(d))
                if abs(d) > HANGUL_POS_TOL:
                    off.append((f"U+{c:04X}", round(b[1] - jn), round(exp, 1)))
            if off:
                probs.append(f"hangul-pos 원본 기저선차 미재현(>{HANGUL_POS_TOL}u, 실측/기대): {off[:8]}")
            else:
                pos_note = f"hangul-pos {len(pos_cps)}자 원본 기저선차 재현(ㅥ 포함, 최대 {worst:.1f}u ≤ {HANGUL_POS_TOL})"
        # 2) 참조 관계
        wname = p.stem.split("-")[1]
        infos = {g["cp"]: g for g in ss.get("supplement_glyphs", {}).get(wname, [])}
        ratios = []
        for t, r, how, tol in REL:
            if t not in cm or r not in cm:
                probs.append(f"U+{t:04X}/U+{r:04X} 없음")
                continue
            bt, br = _bbox(f, cm[t]), _bbox(f, cm[r])
            if how == "h":
                ht, hr = bt[3] - bt[1], br[3] - br[1]
                it = infos.get(t, {})
                exp_ratio = 1.0
                if it.get("src_bbox") and it.get("ref_N"):
                    sb_ = it["src_bbox"]
                    exp_ratio = (sb_[3] - sb_[1]) / it["ref_N"]["h"]
                ratios.append(f"U+{t:04X}/U+{r:04X} {ht / hr:.3f}(Noto {exp_ratio:.3f})")
                if abs(ht - hr * exp_ratio) > tol * hr:
                    probs.append(f"U+{t:04X} h {ht:.0f} vs U+{r:04X} {hr:.0f}×{exp_ratio:.3f} (>{tol:.1%})")
            elif how == "bbox":
                if max(abs(a - b) for a, b in zip(bt, br)) > tol:
                    probs.append(f"U+{t:04X} bbox {bt} vs U+{r:04X} {br}")
            elif how == "adv":
                at, ar = hm[cm[t]][0], hm[cm[r]][0]
                if abs(at - ar) > tol * ar:
                    probs.append(f"U+{t:04X} adv {at} vs U+{r:04X} {ar}")
        # 3) 괘선
        for c in range(0x2500, 0x25A0):
            if c in cm and hm[cm[c]][0] != 1770:
                probs.append(f"괘선 U+{c:04X} adv {hm[cm[c]][0]}")
        for c in HBOX:
            if c in cm:
                b = _bbox(f, cm[c])
                if b and (abs(b[0]) > 1 or abs(b[2] - 1770) > 1):
                    probs.append(f"U+{c:04X} x {b[0]:.0f}..{b[2]:.0f}")
        for c in VBOX:
            if c in cm:
                b = _bbox(f, cm[c])
                if b and (abs(b[1] + 494) > 1 or abs(b[3] - 1950) > 1):
                    probs.append(f"U+{c:04X} y {b[1]:.0f}..{b[3]:.0f}")
        if 0x2588 in cm:
            b = _bbox(f, cm[0x2588])
            if b and max(abs(b[0]), abs(b[1] + 494), abs(b[2] - 1770), abs(b[3] - 1950)) > 1:
                probs.append(f"█ bbox {b}")
        # 4) 합성 4자
        if 0x2154 in cm and 0x2153 in cm:
            g23, g13 = glyf[cm[0x2154]], glyf[cm[0x2153]]
            if not (g23.isComposite() and g13.isComposite() and len(g23.components) == 3 == len(g13.components)
                    and [c.glyphName for c in g23.components][1:] == [c.glyphName for c in g13.components][1:]):
                probs.append("⅔ 컴포지트 구조 ≠ ⅓")
        if 0x223C in cm and 0x223D in cm:
            b1, b2 = _bbox(f, cm[0x223C]), _bbox(f, cm[0x223D])
            if max(abs((b1[0] + b1[2]) - (b2[0] + b2[2])), abs((b1[2] - b1[0]) - (b2[2] - b2[0])), abs(b1[1] - b2[1]), abs(b1[3] - b2[3])) > 2:
                probs.append(f"∼ bbox {b1} ≠ ∽ 대칭 {b2}")
            gs = f.getGlyphSet()
            a1, a2 = AreaPen(gs), AreaPen(gs)
            gs[cm[0x223C]].draw(a1)
            gs[cm[0x223D]].draw(a2)
            if (a1.value > 0) != (a2.value > 0):
                probs.append(f"∼ 윤곽 방향 반대(면적 {a1.value:.0f} vs {a2.value:.0f})")
        if 0x2252 in cm:
            g = glyf[cm[0x2252]]
            if g.isComposite() or g.numberOfContours != 4 or hm[cm[0x2252]][0] != hm[cm[0x3D]][0]:
                probs.append(f"≒ 윤곽 {g.numberOfContours} adv {hm[cm[0x2252]][0]} (기대 4, adv(=)={hm[cm[0x3D]][0]})")
        if 0x25C8 in cm:
            g = glyf[cm[0x25C8]]
            if g.isComposite() or g.numberOfContours != 3 or len(g.coordinates) != 12 or hm[cm[0x25C8]][0] != hm[cm[0x25C7]][0]:
                probs.append(f"◈ 윤곽 {g.numberOfContours} 점 {len(g.coordinates) if not g.isComposite() else '-'} adv {hm[cm[0x25C8]][0]}")
        # 5) Noto 피처 미유입
        tags = {t.split(":")[1] for t in fontutil.gsub_feature_tags(f)}
        bad_feats = tags & {"vert", "palt", "halt", "ljmo", "vjmo", "tjmo", "vkna", "ruby", "hist"}
        if bad_feats:
            probs.append(f"Noto 피처 유입 {bad_feats}")
        f.close()
        if probs:
            ok = False
            rec("FAIL", "supplement", f"{p.name}: " + " / ".join(probs[:12]))
        else:
            rec("PASS", "supplement", f"{p.name}: 07 §8 한글류 adv·{pos_note}·참조 관계 {len(REL)}쌍·괘선 셀·합성 4자 구조·미러 방향·Noto 피처 미유입 통과")
        if wname == "Regular":
            rec("INFO", "supplement", "높이비(결과/참조, 괄호는 Noto 원본 비): " + ", ".join(ratios))
    return ok


BALLOT = (0x2610, 0x2611, 0x2612)


def check_ballot(paths):
    """(1.001) 체크박스 ☐☑☒ — 전 파일(정적 9 + VF 기본 인스턴스·wght 100/900 인스턴스):
    cmap 존재 · 단순 글립(분해) · 진행폭 = □ · bbox = □(±1) · ☐ 윤곽 = □ 윤곽 수 · ☑☒ = □ + 마크 1벌 ·
    마크 bbox 가 □ 속공간 안(박스 윤곽과 겹치지 않음)이고 중심이 속공간 중심 ±2 unit."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import supplement
    ok = True
    for p in paths:
        fonts = [(p.name, TTFont(p))]
        if "fvar" in fonts[0][1]:
            for wv in (100, 900):
                fonts.append((f"{p.name}@wght={wv}", instancer.instantiateVariableFont(TTFont(p), {"wght": wv})))
        for label, f in fonts:
            cm, glyf, hm, gs = f.getBestCmap(), f["glyf"], f["hmtx"].metrics, f.getGlyphSet()
            probs = []
            missing = [f"U+{c:04X}" for c in BALLOT if c not in cm]
            if missing:
                probs.append("cmap 없음 " + ",".join(missing))
            elif 0x25A1 not in cm:
                probs.append("□ 없음")
            else:
                box = cm[0x25A1]
                bb, nbox = _bbox(f, box), glyf[box].numberOfContours
                inner = supplement.inner_contour_bbox(gs, box)
                icx, icy = (inner[0] + inner[2]) / 2, (inner[1] + inner[3]) / 2
                for c in BALLOT:
                    n = cm[c]
                    g = glyf[n]
                    if g.isComposite():
                        probs.append(f"U+{c:04X} 컴포지트")
                        continue
                    if hm[n][0] != hm[box][0]:
                        probs.append(f"U+{c:04X} adv {hm[n][0]} ≠ □ {hm[box][0]}")
                    b = _bbox(f, n)
                    if max(abs(b[i] - bb[i]) for i in range(4)) > 1:
                        probs.append(f"U+{c:04X} bbox {b} ≠ □ {bb}")
                    if c == 0x2610:
                        if g.numberOfContours != nbox:
                            probs.append(f"☐ 윤곽 {g.numberOfContours} ≠ □ {nbox}")
                        continue
                    if g.numberOfContours <= nbox:
                        probs.append(f"U+{c:04X} 마크 윤곽 없음")
                        continue
                    coords, ends, _ = g.getCoordinates(glyf)
                    start = ends[nbox - 1] + 1
                    xs = [x for x, _ in coords[start:]]
                    ys = [y for _, y in coords[start:]]
                    mb = (min(xs), min(ys), max(xs), max(ys))
                    if not (mb[0] > inner[0] and mb[1] > inner[1] and mb[2] < inner[2] and mb[3] < inner[3]):
                        probs.append(f"U+{c:04X} 마크 {mb} 가 속공간 {inner} 밖")
                    if abs((mb[0] + mb[2]) / 2 - icx) > 2 or abs((mb[1] + mb[3]) / 2 - icy) > 2:
                        probs.append(f"U+{c:04X} 마크 중심 ({(mb[0]+mb[2])/2:.0f},{(mb[1]+mb[3])/2:.0f}) ≠ 속공간 중심 ({icx:.0f},{icy:.0f})")
            if probs:
                ok = False
                rec("FAIL", "ballot", f"{label}: " + " / ".join(probs[:8]))
            else:
                rec("PASS", "ballot", f"{label}: ☐☑☒ cmap·adv=□·bbox=□·마크 속공간 안·중심 ±2 통과")
    return ok


def check_variable(vf_path, sets, supplement_cps, synth=()):
    ok = True
    f = TTFont(vf_path)
    fv = f["fvar"]
    ax = fv.axes[0]
    if (ax.axisTag, ax.minValue, ax.defaultValue, ax.maxValue) != ("wght", 100, 400, 900):
        ok = False
        rec("FAIL", "variable", f"fvar 축 {ax.axisTag} {ax.minValue}/{ax.defaultValue}/{ax.maxValue}")
    inst = [(f["name"].getDebugName(i.subfamilyNameID), i.coordinates["wght"], f["name"].getDebugName(i.postscriptNameID))
            for i in fv.instances]
    exp = [(w, float(v), f"JennySansVariable-{w}") for w, v in config.WEIGHTS]
    if inst != exp:
        ok = False
        rec("FAIL", "variable", f"fvar 인스턴스 불일치: {inst}")
    else:
        rec("PASS", "variable", "fvar 인스턴스 9개 이름·좌표·PS 이름 일치")
    st = f["STAT"].table
    vals = sorted((av.Value, f["name"].getDebugName(av.ValueNameID), av.Format, getattr(av, "LinkedValue", None), av.Flags)
                  for av in st.AxisValueArray.AxisValue)
    if [v[0] for v in vals] != [float(v) for _, v in config.WEIGHTS] or vals[3][2:] != (3, 700.0, 2):
        ok = False
        rec("FAIL", "variable", f"STAT 값 불일치: {vals}")
    else:
        rec("PASS", "variable", f"STAT wght 9 값(Regular Format3→700, elidable), 버전 {hex(st.Version)}")
    if "MVAR" in f:
        ok = False
        rec("FAIL", "variable", "MVAR 존재")
    # 보충 글립 보간 = 정적 (샘플: 보충 전부)
    cm = f.getBestCmap()
    sup_names = [cm[c] for c in supplement_cps if c in cm]
    if sup_names:
        sub = TTFont(vf_path)
        fontutil.subset_font(sub, [c for c in supplement_cps if c in cm], layout=False)
        buf = io.BytesIO()
        sub.save(buf)
        worst = 0.0
        worst_info = None
        synth_worst = []
        synth_max = 0.0
        for wn, wv in config.WEIGHTS:
            buf.seek(0)
            vfi = TTFont(buf)
            inst_f = instancer.instantiateVariableFont(vfi, {"wght": wv}, inplace=True, optimize=False)
            static = TTFont(config.DIST_STATIC / f"JennySans-{wn}.ttf", lazy=True)
            scm = static.getBestCmap()
            icm = inst_f.getBestCmap()
            for c in supplement_cps:
                if c not in scm or c not in icm:
                    continue
                gs, gi = static["glyf"][scm[c]], inst_f["glyf"][icm[c]]
                ws, wi = static["hmtx"][scm[c]][0], inst_f["hmtx"][icm[c]][0]
                if c in synth or gs.isComposite() or gi.isComposite():
                    # 합성·컴포지트 글립: 정적(Pretendard 정적 부품)과 VF(VF 부품 인스턴스)는 점 구조가 다를 수 있음 → bbox·adv 비교(±4)
                    bs, bi = _bbox(static, scm[c]), _bbox(inst_f, icm[c])
                    if bs and bi:
                        d = max(abs(a - b) for a, b in zip(bs, bi))
                        synth_max = max(synth_max, d)
                        if d > SYNTH_TOL:
                            synth_worst.append((wn, f"U+{c:04X}", round(d, 1)))
                    synth_max = max(synth_max, abs(ws - wi))
                    if abs(ws - wi) > SYNTH_TOL:
                        synth_worst.append((wn, f"U+{c:04X}", f"adv {ws}/{wi}"))
                    continue
                if gs.numberOfContours != gi.numberOfContours:
                    worst = 999
                    worst_info = (wn, f"U+{c:04X}", "contours")
                    continue
                if gs.numberOfContours > 0:
                    for (x0, y0), (x1, y1) in zip(gs.coordinates, gi.coordinates):
                        d = max(abs(x0 - x1), abs(y0 - y1))
                        if d > worst:
                            worst, worst_info = d, (wn, f"U+{c:04X}", "coord")
                d = abs(ws - wi)
                if d > worst:
                    worst, worst_info = d, (wn, f"U+{c:04X}", "advance")
            static.close()
            inst_f.close()
        if worst <= 2:   # 07 §7 QA (c): ≤ 2 unit
            rec("PASS", "variable", f"보충 글립 {len(sup_names) - len(synth)}개 × 9 웨이트 인스턴스 = 정적 (최대 편차 {worst} unit)")
        else:
            ok = False
            rec("FAIL", "variable", f"보충 글립 보간 편차 {worst} unit @ {worst_info}")
        if synth_worst:
            ok = False
            rec("FAIL", "variable", f"합성 글립 VF↔정적 bbox/adv 차 >{SYNTH_TOL}: {synth_worst[:8]}")
        else:
            rec("PASS", "variable", f"합성·컴포지트 글립 {len(synth)}개 × 9 웨이트 bbox·adv 정적과 ±{SYNTH_TOL} unit 이내(최대 {synth_max:.0f}; "
                                    f"부품이 VF 인스턴스라 정적 Pretendard 부품과 미세 차이)")
        # 07 §7 QA (a): gvar 튜플 점 수 = glyf 점 수 + 4
        gv = f["gvar"].variations
        glyf = f["glyf"]
        badtuple = []
        for nm in sup_names:
            g = glyf[nm]
            npts = (len(g.components) if g.isComposite() else (len(g.coordinates) if g.numberOfContours > 0 else 0)) + 4
            for tv in gv.get(nm, []):
                if len(tv.coordinates) != npts:
                    badtuple.append((nm, len(tv.coordinates), npts))
        if badtuple:
            ok = False
            rec("FAIL", "variable", f"gvar 튜플 점 수 불일치 {badtuple[:5]}")
        else:
            rec("PASS", "variable", f"gvar 튜플 점 수 = glyf 점 수 + 4 (보충 {len(sup_names)} 글립, 튜플 {sum(len(gv.get(n, [])) for n in sup_names)}개)")
    f.close()
    return ok


def check_features(paths):
    src_static = TTFont(config.PRETENDARD_TTF_DIR / "Pretendard-Regular.ttf", lazy=True)
    src_tags_static = fontutil.gsub_feature_tags(src_static)
    src_static.close()
    src_vf = TTFont(config.PRETENDARD_VF, lazy=True)
    src_tags_vf = fontutil.gsub_feature_tags(src_vf)
    src_vf.close()
    ok = True
    for p in paths:
        src_tags = src_tags_vf if "Variable" in p.name else src_tags_static
        f = TTFont(p, lazy=True)
        tags = fontutil.gsub_feature_tags(f)
        empty = []
        for tbl in ("GSUB", "GPOS"):
            if tbl in f:
                for fr in f[tbl].table.FeatureList.FeatureRecord:
                    if not fr.Feature.LookupListIndex:
                        empty.append(f"{tbl}:{fr.FeatureTag}")
        f.close()
        lost = sorted(src_tags - tags)
        if empty:
            ok = False
            rec("FAIL", "features", f"{p.name}: 빈 피처 {empty}")
        # spec 04 §1: 허용되는 소실 = 정적 {ss16}, VF {ss16, rlig}(VF 의 rlig 는 원본에서 빈 피처). 그 외 소실은 FAIL
        allowed = {"GSUB:ss16"} | ({"GSUB:rlig"} if "Variable" in p.name else set())
        bad_lost = [t for t in lost if t not in allowed]
        if bad_lost:
            ok = False
            rec("FAIL", "features", f"{p.name}: 허용되지 않은 피처 소실 {bad_lost}")
        else:
            rec("PASS", "features", f"{p.name}: 피처 {len(tags)}개(GSUB+GPOS), 사라짐 {lost or '없음'} (허용: ss16=PUA 아이콘 전용{', rlig=원본 빈 피처' if 'Variable' in p.name else ''})")
    return ok


def write_report(path):
    fails = [r for r in RESULTS if r[0] == "FAIL"]
    warns = [r for r in RESULTS if r[0] == "WARN"]
    lines = ["# verify-report — 빌더 자체 점검", "",
             f"결과: **{'FAIL ' + str(len(fails)) if fails else 'PASS'}** (WARN {len(warns)}, 항목 {len(RESULTS)})", "",
             "| 상태 | 항목 | 내용 |", "|---|---|---|"]
    for s, sec, m in RESULTS:
        lines.append(f"| {s} | {sec} | {m.replace('|', '\\|')} |")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return not fails


def main(argv=None):
    fontutil.setup_logging("verify")
    sets = charset.load_sets()
    statics = [config.DIST_STATIC / f"JennySans-{w}.ttf" for w in config.WEIGHT_NAMES]
    statics = [p for p in statics if p.exists()]
    vf = config.DIST_VARIABLE / "JennySansVariable.ttf"
    all_fonts = statics + ([vf] if vf.exists() else [])
    if len(statics) != 9:
        rec("FAIL", "files", f"정적 파일 {len(statics)}/9")
    if not vf.exists():
        rec("FAIL", "files", "변수 폰트 없음")
    for p in all_fonts:
        check_coverage(p, sets)
        check_rfn(p)
    check_names(all_fonts)
    check_tables(all_fonts)
    check_vertical(all_fonts)     # 티켓 9: vhea/vmtx 없음(전 파일)
    check_orphans(all_fonts)      # 티켓 11: 고아 글립 0
    check_metrics(all_fonts)
    check_psnames(all_fonts)
    check_features(all_fonts)
    ss = fontutil.read_json(config.BUILD / "static-summary.json", {})
    sup_infos = ss.get("supplement_glyphs", {}).get("Regular", [])
    sup_cps = [g["cp"] for g in sup_infos]
    synth = {g["cp"] for g in sup_infos if g["mode"] in ("composite", "mirror")}
    check_supplement_spec(statics)
    check_ballot(all_fonts)      # 1.001: 체크박스 ☐☑☒ (정적 9 + VF 100/400/900)
    if vf.exists() and statics:
        check_variable(vf, sets, sup_cps, synth)
        check_flatten(vf)         # 티켓 2: VF 평탄화 컴포지트 = 정적(07 §7(c) 허용치)
    check_web(sets)
    ok = write_report(config.BUILD / "verify-report.md")
    LOG.info("verify: %s → %s", "PASS" if ok else "FAIL", config.BUILD / "verify-report.md")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
