# -*- coding: utf-8 -*-
"""
릴리스 간 회귀 비교(1.001 도입). dist/static·dist/variable 의 cmap·글립 외곽선 해시·진행폭/LSB·수직 메트릭을 스냅숏으로 저장하고,
두 스냅숏을 비교해 "추가된 코드포인트 외에 바뀐 것이 없는지" 확인한다.

  PYTHONUTF8=1 python tools/regress_snapshot.py save build/regress-1.000.json      # 빌드 전
  PYTHONUTF8=1 python tools/regress_snapshot.py diff build/regress-1.000.json build/regress-1.001.json

비교 대상: cmap(코드포인트→글립), 글립별 glyf 외곽선 해시(컴포지트는 컴포넌트·오프셋), hmtx(adv, lsb), VF 는 gvar 델타 해시,
head.unitsPerEm, hhea/OS/2 수직 메트릭. head·name 등 버전 표기는 비교하지 않는다(의도된 변경).
"""
import glob
import hashlib
import json
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


def _ghash(font, name):
    glyf = font["glyf"]
    g = glyf[name]
    h = hashlib.sha1()
    if g.isComposite():
        for c in g.components:
            h.update(f"C{c.glyphName}:{c.x}:{c.y}:{getattr(c, 'transform', None)};".encode())
    elif g.numberOfContours:
        coords, ends, flags = g.getCoordinates(glyf)
        h.update(repr((list(coords), list(ends), [f & 1 for f in flags])).encode())
    if "gvar" in font and name in font["gvar"].variations:
        for v in font["gvar"].variations[name]:
            h.update(repr((sorted(v.axes.items()), v.coordinates)).encode())
    return h.hexdigest()[:16]


def snapshot():
    out = {}
    for p in sorted(glob.glob(str(ROOT / "dist/static/*.ttf")) + glob.glob(str(ROOT / "dist/variable/*.ttf"))):
        f = TTFont(p)
        cm = f.getBestCmap()
        glyphs = {cp: cm[cp] for cp in cm}
        out[Path(p).name] = dict(
            cmap={f"{cp:04X}": n for cp, n in glyphs.items()},
            glyphs={n: [_ghash(f, n), *f["hmtx"][n]] for n in f.getGlyphOrder()},
            vmetrics=[f["head"].unitsPerEm, f["hhea"].ascent, f["hhea"].descent, f["hhea"].lineGap,
                      f["OS/2"].sTypoAscender, f["OS/2"].sTypoDescender, f["OS/2"].sTypoLineGap,
                      f["OS/2"].usWinAscent, f["OS/2"].usWinDescent, f["OS/2"].fsSelection & 0x80],
            version=[f["head"].fontRevision, f["name"].getDebugName(5)],
        )
        f.close()
    return out


def diff(a, b):
    ok = True
    lines = []
    for fn in sorted(set(a) | set(b)):
        if fn not in a or fn not in b:
            lines.append(f"- {fn}: 한쪽에만 존재"); ok = False
            continue
        A, B = a[fn], b[fn]
        added = sorted(set(B["cmap"]) - set(A["cmap"]))
        removed = sorted(set(A["cmap"]) - set(B["cmap"]))
        remapped = [k for k in A["cmap"] if k in B["cmap"] and A["cmap"][k] != B["cmap"][k]]
        changed = [n for n in A["glyphs"] if n in B["glyphs"] and A["glyphs"][n] != B["glyphs"][n]]
        gone = [n for n in A["glyphs"] if n not in B["glyphs"]]
        new_g = [n for n in B["glyphs"] if n not in A["glyphs"]]
        vm = A["vmetrics"] == B["vmetrics"]
        bad = removed or remapped or changed or gone or not vm
        ok &= not bad
        lines.append(f"- {fn}: cmap {len(A['cmap'])} → {len(B['cmap'])} (추가 {','.join('U+' + c for c in added) or '없음'}"
                     f", 제거 {len(removed)}, 재매핑 {len(remapped)}) · 글립 {len(A['glyphs'])} → {len(B['glyphs'])}"
                     f" (새 글립 {new_g}, 사라진 {len(gone)}, 외곽선/진행폭 변경 {len(changed)}{' ' + str(changed[:5]) if changed else ''})"
                     f" · 수직 메트릭 {'동일' if vm else '변경!'} · 버전 {A['version'][0]} → {B['version'][0]}")
    return ok, lines


def main(argv):
    if argv[:1] == ["save"]:
        Path(argv[1]).write_text(json.dumps(snapshot(), ensure_ascii=False), encoding="utf-8")
        print("saved", argv[1])
        return 0
    if argv[:1] == ["diff"]:
        a = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        b = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
        ok, lines = diff(a, b)
        print("\n".join(lines))
        print("REGRESSION:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
