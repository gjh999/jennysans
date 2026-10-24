# -*- coding: utf-8 -*-
"""
QA 티켓 1·2·3·4·6·9·11 재검(6차·8차 빌드 수정 확인) — fontbakery·빌더 코드와 **독립**으로 폰트 바이너리를 직접 읽어 판정한다.

 1 case_mapping   : U+01C4 DŽ 존재 + D+Zcaron 컴포지트(티켓 2 평탄화로 Zcaron 이 Z+caron 으로 풀려 D·Z·caron 3부품)
                   + 진행폭 = adv(D) + adv(Zcaron), U+01C5/01C6 도 존재
 2 nested_components: 컴포넌트가 다시 컴포지트를 참조하는 글립 수 — **8차부터 정적·VF 모두 0 기대**
 3 no_mac_entries : platformID 1 name 레코드 0
 4 smart_dropout  : prep 프로그램 == PUSHW[] 511 SCANCTRL[] PUSHB[] 4 SCANTYPE[], gasp 0xFFFF→0x000F
 6 transformed_components: 2x2 변환(스케일·회전·반전)이 걸린 컴포넌트를 쓰는 글립 수(정적·VF 0 기대)
 9 vertical-tables: vhea/vmtx/VVAR/VORG 가 **전 파일(TTF 10 + WOFF2 10)에 없음**(8차 제거)
11 orphan-glyphs  : 고아 글립 0. 도달성 = cmap(UVS 포함) ∪ GSUB/GPOS/GDEF/MATH/BASE 객체 트리 등장 ∪ 컴포넌트 폐포
                   ∪ 예약(.notdef/.null/NULL/nonmarkingreturn/CR). **QA 자체 구현**(빌더 fontutil.reachable_glyphs 미사용).
                   제거 대상이던 글립이 실제로 사라졌는지 + `.null` 은 남았는지도 확인.

실행: PYTHONUTF8=1 python docs/qa/scripts/tickets.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402

PREP_EXPECT = ["PUSHW[]", "511", "SCANCTRL[]", "PUSHB[]", "4", "SCANTYPE[]"]
VERTICAL_TABLES = ("vhea", "vmtx", "VVAR", "VORG")
RESERVED = {".notdef", ".null", "NULL", "nonmarkingreturn", "CR"}
REMOVED_STATIC = ["casedieresis.cn", "casetilde.cn", "tonos", "uniE118"]
REMOVED_VF = REMOVED_STATIC + ["uni0189", "cyrillictic.cn"]


def _walk_names(obj, out, seen):
    """레이아웃 테이블 객체 트리를 재귀 순회하며 등장하는 모든 글립명을 모은다(QA 자체 구현)."""
    if id(obj) in seen:
        return
    seen.add(id(obj))
    if isinstance(obj, str):
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str):
                out.add(k)
            if isinstance(v, str):
                out.add(v)
            else:
                _walk_names(v, out, seen)
        return
    if isinstance(obj, (list, tuple, set)):
        for v in obj:
            if isinstance(v, str):
                out.add(v)
            else:
                _walk_names(v, out, seen)
        return
    if hasattr(obj, "__dict__"):
        for v in vars(obj).values():
            if isinstance(v, str):
                out.add(v)
            else:
                _walk_names(v, out, seen)


def reachable(f):
    """도달 가능한 글립명 집합 — QA 독립 구현."""
    order = f.getGlyphOrder()
    reach = set(RESERVED) & set(order)
    # 1) cmap: 모든 서브테이블(UVS 포함)
    if "cmap" in f:
        for st in f["cmap"].tables:
            if getattr(st, "format", None) == 14:
                for _sel, mapping in (getattr(st, "uvsDict", {}) or {}).items():
                    for pair in mapping:
                        # (unicodeValue, glyphName) — glyphName 이 None 이면 기본 글립 사용
                        if len(pair) > 1 and pair[1]:
                            reach.add(pair[1])
            else:
                reach.update((st.cmap or {}).values())
    # 2) 레이아웃 테이블에 이름이 등장하는 글립(입력·출력·클래스·앵커 전부 — fontbakery 보다 보수적)
    names = set()
    for tag in ("GSUB", "GPOS", "GDEF", "MATH", "BASE", "JSTF"):
        if tag in f:
            _walk_names(f[tag].table, names, set())
    reach |= names & set(order)
    # 3) 컴포넌트 폐포
    if "glyf" in f:
        glyf = f["glyf"]
        stack = list(reach)
        while stack:
            gn = stack.pop()
            if gn not in glyf:
                continue
            g = glyf[gn]
            if g.isComposite():
                for c in g.components:
                    if c.glyphName not in reach:
                        reach.add(c.glyphName)
                        stack.append(c.glyphName)
    return reach


def composite_report(f):
    """(중첩 컴포지트 글립, 변환 컴포넌트 글립) 목록."""
    glyf = f["glyf"]
    nested, transformed = [], []
    for gn in glyf.keys():
        g = glyf[gn]
        if not g.isComposite():
            continue
        for c in g.components:
            sub = glyf[c.glyphName]
            if sub.isComposite() and gn not in nested:
                nested.append(gn)
            t = getattr(c, "transform", None)
            if t and (abs(t[0][0] - 1) > 1e-6 or abs(t[1][1] - 1) > 1e-6 or abs(t[0][1]) > 1e-6 or abs(t[1][0]) > 1e-6):
                if gn not in transformed:
                    transformed.append(gn)
    return nested, transformed


def main():
    rep = Q.Report("QA 티켓 1·2·3·4·6·9·11 재검 (8차 빌드)")
    for p in Q.ALL_TTFS:
        f = TTFont(p)
        n = p.name
        cmap = f.getBestCmap()
        hm = f["hmtx"].metrics
        glyf = f["glyf"]
        # --- 티켓 1: U+01C4
        missing = [f"U+{c:04X}" for c in (0x01C4, 0x01C5, 0x01C6) if c not in cmap]
        if missing:
            rep.fail("t1-case_mapping", f"{n}: 결손 {missing}")
        else:
            g = glyf[cmap[0x01C4]]
            comps = [c.glyphName for c in g.components] if g.isComposite() else []
            adv = hm[cmap[0x01C4]][0]
            gD, gZc, gZ = cmap[0x0044], cmap[0x017D], cmap[0x005A]
            # 티켓 2(중첩 평탄화)로 Zcaron(=Z+caron 컴포지트)이 한 단계 풀려 D·Z·caron 으로 실린다 — 둘 다 정상으로 인정
            ok_comp = comps in ([gD, gZc], [gD, gZ, "caron"], [gD, gZ, "uni030C"])
            exp_adv = hm[gD][0] + hm[gZc][0]
            ok = ok_comp and adv == exp_adv
            (rep.passed if ok else rep.fail)(
                "t1-case_mapping", f"{n}: U+01C4 컴포지트 {comps} adv {adv} (기대 adv(D)+adv(Zcaron) = {hm[gD][0]}+{hm[gZc][0]} = {exp_adv}), U+01C5/01C6 존재")
        # --- 티켓 2·6: 중첩 / 변환 컴포넌트
        nested, transformed = composite_report(f)
        # 8차부터는 VF 도 0 이어야 한다(팀장 결정 AGENTS §8 2026-09-09 — 승인 예외를 늘리지 않고 고침)
        (rep.passed if not nested else rep.fail)("t2-nested", f"{n}: 중첩 컴포지트 {len(nested)} {nested[:10]}")
        (rep.passed if not transformed else rep.fail)("t6-transformed", f"{n}: 변환 컴포넌트 사용 글립 {len(transformed)} {transformed[:10]}")
        # --- 티켓 3: Mac 레코드
        n_mac = sum(1 for r in f["name"].names if r.platformID == 1)
        (rep.passed if n_mac == 0 else rep.fail)("t3-no_mac_entries", f"{n}: platformID 1 레코드 {n_mac}")
        # --- 티켓 4: prep / gasp
        # getAssembly() 는 각 명령에 "[ ]\t/* 주석 */" 이 붙으므로 니모닉만 뽑아 비교한다.
        prep = [t.split("[")[0] + ("[]" if "[" in t else "") for t in
                (x.split("\t")[0].strip() for x in f["prep"].program.getAssembly())] if "prep" in f else None
        gasp = f["gasp"].gaspRange if "gasp" in f else None
        ok = prep == PREP_EXPECT and gasp == {0xFFFF: 0x000F}
        (rep.passed if ok else rep.fail)("t4-smart_dropout", f"{n}: prep {prep} · gasp {gasp}")
        # --- 티켓 9: 세로쓰기 테이블 제거
        vt = [t for t in VERTICAL_TABLES if t in f]
        (rep.passed if not vt else rep.fail)("t9-vertical", f"{n}: vhea/vmtx/VVAR/VORG 잔존 {vt} (기대 없음)")
        # --- 티켓 11: 고아 글립
        order = set(f.getGlyphOrder())
        reach = reachable(f)
        orphans = sorted(order - reach)
        removed = REMOVED_VF if "fvar" in f else REMOVED_STATIC
        still = [g for g in removed if g in order]
        null_kept = ".null" in order
        (rep.passed if not orphans else rep.fail)(
            "t11-orphans", f"{n}: 글립 {len(order)} 중 도달 불가 {len(orphans)} {orphans[:10]} (QA 독립 도달성 계산)")
        (rep.passed if not still else rep.fail)(
            "t11-removed", f"{n}: 제거 대상 {len(removed)}자 잔존 {still} · `.null` 유지 {null_kept}")
        f.close()
    # WOFF2 도 세로 테이블이 없어야 한다(웹 산출물)
    for p in Q.STATIC_WOFF2 + [Q.VF_WOFF2]:
        f = TTFont(p)
        vt = [t for t in VERTICAL_TABLES if t in f]
        (rep.passed if not vt else rep.fail)("t9-vertical", f"{p.name}: vhea/vmtx/VVAR/VORG 잔존 {vt} (기대 없음)")
        f.close()
    rep.write("tickets")


if __name__ == "__main__":
    main()
