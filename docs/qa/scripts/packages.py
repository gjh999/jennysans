# -*- coding: utf-8 -*-
"""
배포 zip 4종 검사 (dist/packages): 압축 해제 목록, LICENSE·LICENSE.txt·THIRD-PARTY-NOTICES.md·README-설치안내.txt 동봉,
SHA256SUMS.txt 일치, index.json 의 bytes/sha256 일치, zip 안 폰트 파일 바이트 == dist/ 파일(SHA-256), zip 안 LICENSE == 루트 LICENSE.
실행: PYTHONUTF8=1 python docs/qa/scripts/packages.py
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qa_common as Q  # noqa: E402

EXPECT = {
    "desktop": {"fonts": [f"static/JennySans-{w}.ttf" for w in Q.WEIGHT_NAMES]},
    "variable": {"fonts": ["variable/JennySansVariable.ttf"]},
    "web": {"fonts": [f"web/JennySans-{w}.woff2" for w in Q.WEIGHT_NAMES] + ["web/JennySansVariable.woff2"]},
    "all": {"fonts": [f"static/JennySans-{w}.ttf" for w in Q.WEIGHT_NAMES] + ["variable/JennySansVariable.ttf"] + [f"web/JennySans-{w}.woff2" for w in Q.WEIGHT_NAMES] + ["web/JennySansVariable.woff2"]},
}
REQUIRED_DOCS = ["LICENSE", "LICENSE.txt", "THIRD-PARTY-NOTICES.md", "README-설치안내.txt"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    rep = Q.Report("배포 패키지 zip 4종")
    sums = {}
    for line in (Q.PKG_DIR / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            h, n = line.split(maxsplit=1)
            sums[n.strip().lstrip("*")] = h
    index = json.loads((Q.PKG_DIR / "index.json").read_text(encoding="utf-8"))
    rep.info("index", f"index.json version {index.get('version')} generated {index.get('generated')} packages {list(index.get('packages', {}))}")
    lic_root = (Q.ROOT / "LICENSE").read_bytes()
    rows = []
    for kind in ("desktop", "web", "variable", "all"):
        zp = Q.PKG_DIR / f"JennySans-{Q.VERSION}-{kind}.zip"
        if not zp.exists():
            rep.fail("zip", f"{zp.name} 없음")
            continue
        data = zp.read_bytes()
        h = sha(data)
        (rep.passed if sums.get(zp.name) == h else rep.fail)("sha256sums", f"{zp.name}: SHA256SUMS {'일치' if sums.get(zp.name) == h else '불일치 ' + str(sums.get(zp.name))[:16]} ({h[:16]}…), {len(data):,} B")
        ij = index["packages"].get(kind, {})
        (rep.passed if ij.get("sha256") == h and ij.get("bytes") == len(data) else rep.fail)("index", f"{zp.name}: index.json bytes/sha {'일치' if ij.get('sha256') == h and ij.get('bytes') == len(data) else '불일치'}")
        z = zipfile.ZipFile(zp)
        names = z.namelist()
        top = {n.split("/", 1)[0] for n in names}
        (rep.passed if top == {f"JennySans-{Q.VERSION}-{kind}"} else rep.fail)("zip", f"{zp.name}: 최상위 폴더 {top}")
        base = f"JennySans-{Q.VERSION}-{kind}/"
        inner = [n[len(base):] for n in names if n.startswith(base) and not n.endswith("/")]
        miss_docs = [d for d in REQUIRED_DOCS if d not in inner]
        (rep.passed if not miss_docs else rep.fail)("docs", f"{zp.name}: 동봉 문서 {REQUIRED_DOCS} {'전부 있음' if not miss_docs else '누락 ' + str(miss_docs)}")
        # LICENSE 내용 == 루트
        if "LICENSE" in inner:
            zl = z.read(base + "LICENSE")
            (rep.passed if zl == lic_root else rep.fail)("docs", f"{zp.name}: zip LICENSE {'==' if zl == lic_root else '≠'} 루트 LICENSE ({len(zl)} B)")
        if "LICENSE.txt" in inner:
            zl = z.read(base + "LICENSE.txt")
            (rep.passed if zl.replace(b"\r\n", b"\n") == lic_root else rep.warn)("docs", f"{zp.name}: LICENSE.txt {'== LICENSE(CRLF 정규화)' if zl.replace(b'\r\n', b'\n') == lic_root else '≠ LICENSE'}")
        if "README-설치안내.txt" in inner:
            rd = z.read(base + "README-설치안내.txt").decode("utf-8", "replace")
            rep.info("docs", f"{zp.name}: README-설치안내.txt {len(rd)}자, 첫 줄 {rd.splitlines()[0][:60]!r}")
        # 폰트 파일 == dist
        expected = EXPECT[kind]["fonts"]
        bad, ok_n = [], 0
        for rel in expected:
            src = Q.DIST / rel
            inner_name = rel.split("/", 1)[1] if kind != "web" and kind != "all" else rel
            if kind == "desktop" or kind == "variable":
                inner_name = Path(rel).name
            cands = [n for n in inner if n.endswith(Path(rel).name)]
            if not cands:
                bad.append(("없음", rel))
                continue
            zb = z.read(base + cands[0])
            if sha(zb) != sha(src.read_bytes()):
                bad.append(("불일치", rel))
            else:
                ok_n += 1
        (rep.passed if not bad else rep.fail)("fonts", f"{zp.name}: 폰트 {ok_n}/{len(expected)} dist 와 SHA-256 동일, 문제 {bad[:5]}")
        # 웹 zip: 분할 990 + css 4
        if kind in ("web", "all"):
            n_sub = sum(1 for n in inner if "/subset/" in n and n.endswith(".woff2"))
            n_css = sum(1 for n in inner if n.startswith("css/") and n.endswith(".css"))
            (rep.passed if n_sub == 990 and n_css == 4 else rep.fail)("web", f"{zp.name}: 분할 woff2 {n_sub} (기대 990), css {n_css} (기대 4)")
            # css 내용 == dist
            for c in Q.CSS_DIR.glob("*.css"):
                zc = z.read(base + "css/" + c.name) if (base + "css/" + c.name) in names else None
                if zc is None or sha(zc) != sha(c.read_bytes()):
                    rep.fail("web", f"{zp.name}: css/{c.name} dist 와 {'없음' if zc is None else '다름'}")
        rows.append((zp.name, f"{len(data):,}", len(inner), ij.get("files"), h[:16] + "…", ", ".join(sorted(set(REQUIRED_DOCS) & set(inner)))))
        z.close()
    extra = [p.name for p in Q.PKG_DIR.iterdir() if p.suffix == ".zip" and p.name not in sums]
    (rep.passed if not extra else rep.warn)("files", f"SHA256SUMS 에 없는 zip {extra}")
    rep.md("## zip 목록\n\n" + Q.table(["zip", "bytes", "파일 수(실측)", "index.json files", "SHA-256", "동봉 문서"], rows))
    rep.write("packages")


if __name__ == "__main__":
    main()
