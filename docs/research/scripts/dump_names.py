#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dump_names.py — name 테이블 전 레코드 + fvar/STAT 요약 덤프 (라이선스·RFN·원본 고지 실측용)

사용: PYTHONUTF8=1 python docs/research/scripts/dump_names.py <font> [<font> ...] [--md 출력.md]
"""
import sys, os, argparse
from fontTools.ttLib import TTFont

PLAT = {0: "uni", 1: "mac", 3: "win"}


def dump(path):
    f = TTFont(path, lazy=True)
    out = [f"## {os.path.basename(path)}", "", f"`{path}`", ""]
    out.append("| nameID | plat | lang | 값 |")
    out.append("|---|---|---|---|")
    seen = set()
    for rec in sorted(f["name"].names, key=lambda r: (r.nameID, r.platformID, r.langID)):
        try:
            s = rec.toUnicode()
        except Exception:
            s = "<decode error>"
        key = (rec.nameID, rec.platformID, rec.langID)
        if key in seen:
            continue
        seen.add(key)
        s = s.replace("|", "\\|").replace("\n", " ⏎ ")
        if len(s) > 400:
            s = s[:400] + " …(truncated)"
        out.append(f"| {rec.nameID} | {PLAT.get(rec.platformID, rec.platformID)} | 0x{rec.langID:04X} | {s} |")
    if "fvar" in f:
        out.append("")
        out.append("**fvar**: " + "; ".join(f"{a.axisTag} {a.minValue:g}/{a.defaultValue:g}/{a.maxValue:g}" for a in f["fvar"].axes))
        inst = []
        for i in f["fvar"].instances:
            nm = f["name"].getDebugName(i.subfamilyNameID)
            ps = f["name"].getDebugName(i.postscriptNameID) if i.postscriptNameID not in (None, 0xFFFF) else "-"
            inst.append(f"{nm}({','.join(f'{k}={v:g}' for k, v in i.coordinates.items())}; ps={ps})")
        out.append(f"**named instances ({len(inst)})**: " + ", ".join(inst))
    if "STAT" in f:
        st = f["STAT"].table
        axes = [f"{a.AxisTag}(nameID {a.AxisNameID}='{f['name'].getDebugName(a.AxisNameID)}')" for a in st.DesignAxisRecord.Axis] if st.DesignAxisRecord else []
        n_av = len(st.AxisValueArray.AxisValue) if st.AxisValueArray else 0
        out.append(f"**STAT** v{st.Version:#x}: axes={axes}, axisValues={n_av}, elidedFallbackNameID={getattr(st, 'ElidedFallbackNameID', None)}")
        if st.AxisValueArray:
            vals = []
            for av in st.AxisValueArray.AxisValue:
                nm = f["name"].getDebugName(av.ValueNameID)
                if av.Format == 1:
                    vals.append(f"F1 {nm}={av.Value:g} flags={av.Flags}")
                elif av.Format == 2:
                    vals.append(f"F2 {nm}={av.NominalValue:g}[{av.RangeMinValue:g}-{av.RangeMaxValue:g}] flags={av.Flags}")
                elif av.Format == 3:
                    vals.append(f"F3 {nm}={av.Value:g}->{av.LinkedValue:g} flags={av.Flags}")
                elif av.Format == 4:
                    vals.append(f"F4 {nm} flags={av.Flags}")
            out.append("STAT axisValues: " + "; ".join(vals))
    os2 = f["OS/2"]
    out.append(f"**OS/2**: usWeightClass={os2.usWeightClass}, fsSelection=0b{os2.fsSelection:010b} (bit0 ITALIC={bool(os2.fsSelection&1)}, bit5 BOLD={bool(os2.fsSelection&32)}, bit6 REGULAR={bool(os2.fsSelection&64)}, bit7 USE_TYPO={bool(os2.fsSelection&128)}, bit8 WWS={bool(os2.fsSelection&256)}), fsType={os2.fsType}, achVendID={os2.achVendID!r}")
    out.append(f"**head.macStyle**={f['head'].macStyle}, **post.italicAngle**={f['post'].italicAngle}")
    out.append("")
    f.close()
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fonts", nargs="+")
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    txt = "# name 테이블 덤프 (자동 생성: docs/research/scripts/dump_names.py)\n\n" + "\n".join(dump(p) for p in a.fonts)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
