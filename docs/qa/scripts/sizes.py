# -*- coding: utf-8 -*-
"""
게이트 6 — 파일 크기 표: 전 산출물 크기 + 원본(Pretendard alternative TTF·VF) 대비, 원본 WOFF2 압축 크기(참고).
실행: PYTHONUTF8=1 python docs/qa/scripts/sizes.py
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402


def woff2_size(path):
    f = TTFont(path)
    f.flavor = "woff2"
    b = io.BytesIO()
    f.save(b)
    f.close()
    return len(b.getvalue())


def main():
    rep = Q.Report("파일 크기 (게이트 6)")
    rows = []
    for (w, _), t, wf in zip(Q.WEIGHTS, Q.STATIC_TTFS, Q.STATIC_WOFF2):
        op = Q.PRETENDARD_TTF / f"Pretendard-{w}.ttf"
        osz = op.stat().st_size if op.exists() else None
        ts, ws = t.stat().st_size, wf.stat().st_size
        og = TTFont(op, lazy=True)["maxp"].numGlyphs if op.exists() else None
        ng = TTFont(t, lazy=True)["maxp"].numGlyphs
        (rep.passed if osz and ts <= osz else rep.fail)("static", f"{t.name}: {ts:,} B vs 원본 {osz:,} B ({(ts / osz - 1) * 100:+.1f}%), 글립 {ng} vs {og}")
        rows.append((t.name, f"{ts:,}", f"{osz:,}" if osz else "-", f"{(ts / osz - 1) * 100:+.1f}%" if osz else "-", f"{ws:,}", ng, og))
    vs = Q.VF_TTF.stat().st_size
    ovs = Q.PRETENDARD_VF.stat().st_size if Q.PRETENDARD_VF.exists() else None
    (rep.info)("variable", f"{Q.VF_TTF.name}: {vs:,} B vs PretendardVariable.ttf {ovs:,} B ({(vs / ovs - 1) * 100:+.1f}%) — 보충 908 글립 gvar 추가로 증가 허용(게이트 6 은 정적 기준)")
    rows.append((Q.VF_TTF.name, f"{vs:,}", f"{ovs:,}", f"{(vs / ovs - 1) * 100:+.1f}%", f"{Q.VF_WOFF2.stat().st_size:,}", TTFont(Q.VF_TTF, lazy=True)["maxp"].numGlyphs, TTFont(Q.PRETENDARD_VF, lazy=True)["maxp"].numGlyphs))
    rep.md("## 정적·변수 (원본 대비)\n\n" + Q.table(["파일", "bytes", "원본 bytes", "증감", "WOFF2 bytes", "글립", "원본 글립"], rows))
    # 원본 Regular/Bold WOFF2 참고
    ref = []
    for w in ("Regular", "Bold"):
        op = Q.PRETENDARD_TTF / f"Pretendard-{w}.ttf"
        if op.exists():
            s = woff2_size(op)
            ours = (Q.WEB_DIR / f"JennySans-{w}.woff2").stat().st_size
            ref.append((w, f"{s:,}", f"{ours:,}", f"{(ours / s - 1) * 100:+.1f}%"))
    rep.md("## 원본 전체 WOFF2 (fontTools 압축, 참고) vs 우리 WOFF2\n\n" + Q.table(["웨이트", "Pretendard TTF→WOFF2", "JennySans WOFF2", "증감"], ref))
    # 디렉터리 합계
    dr = []
    for d in (Q.STATIC_DIR, Q.VARIABLE_DIR, Q.WEB_DIR, Q.SUBSET_DIR, Q.CSS_DIR, Q.PKG_DIR):
        files = [p for p in d.iterdir() if p.is_file()]
        dr.append((str(d.relative_to(Q.ROOT)), len(files), f"{sum(p.stat().st_size for p in files):,}"))
    rep.md("## 디렉터리 합계\n\n" + Q.table(["디렉터리", "파일 수", "bytes"], dr))
    rep.write("sizes")


if __name__ == "__main__":
    main()
