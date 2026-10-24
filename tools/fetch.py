# -*- coding: utf-8 -*-
"""
원본 다운로드·검증 (sources/MANIFEST.md 의 URL·SHA-256 기준).

- 이미 있는 파일은 SHA-256 만 확인하고 재사용한다(불일치면 오류).
- Pretendard 1.3.9 zip 은 스크래치패드(또는 --tmp 지정 폴더)에 받아 `public/static/alternative/*.ttf` 9종을
  `sources/Pretendard/alternative-ttf/` 로 추출한다(현재 Regular/Bold 만 있던 것을 9종으로 채움).
- Noto Sans KR VF 는 Google Fonts 저장소 raw URL 에서 받는다.

실행: PYTHONUTF8=1 python tools/fetch.py [--tmp DIR] [--force]
"""
import argparse
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
import fontutil  # noqa: E402

LOG = fontutil.LOG

ALT_TTF_IN_ZIP = "public/static/alternative/Pretendard-{w}.ttf"
VF_IN_ZIP = "public/variable/PretendardVariable.ttf"


def manifest_sha(relpath):
    """MANIFEST.md 표에서 `relpath` 의 SHA-256 을 찾는다(없으면 None)."""
    text = config.MANIFEST.read_text(encoding="utf-8")
    for line in text.splitlines():
        if f"`{relpath}`" in line and "|" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            for c in cells:
                c2 = c.strip("`")
                if len(c2) == 64 and all(ch in "0123456789abcdef" for ch in c2):
                    return c2
    return None


def download(url, dest, expected_sha=None, force=False):
    dest = Path(dest)
    if dest.exists() and not force:
        if expected_sha:
            got = fontutil.sha256_of(dest)
            if got != expected_sha:
                raise SystemExit(f"SHA-256 불일치: {dest}\n  기대 {expected_sha}\n  실제 {got}")
            LOG.info("재사용(SHA OK): %s", dest)
        else:
            LOG.info("재사용(SHA 미검증): %s", dest)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    LOG.info("다운로드: %s → %s", url, dest)
    req = urllib.request.Request(url, headers={"User-Agent": "JennySans-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    if expected_sha:
        got = fontutil.sha256_of(dest)
        if got != expected_sha:
            raise SystemExit(f"SHA-256 불일치(다운로드 후): {dest}\n  기대 {expected_sha}\n  실제 {got}")
    LOG.info("완료 %s (%d bytes)", dest.name, dest.stat().st_size)
    return dest


def extract_pretendard(zip_path, force=False):
    config.PRETENDARD_TTF_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        names = set(z.namelist())
        for w in config.WEIGHT_NAMES:
            member = ALT_TTF_IN_ZIP.format(w=w)
            dest = config.PRETENDARD_TTF_DIR / f"Pretendard-{w}.ttf"
            if member not in names:
                raise SystemExit(f"zip 에 없음: {member}")
            if dest.exists() and not force:
                sha = manifest_sha(f"Pretendard/alternative-ttf/Pretendard-{w}.ttf")
                if sha and fontutil.sha256_of(dest) != sha:
                    raise SystemExit(f"SHA 불일치(기존 파일): {dest}")
                LOG.info("있음: %s", dest.name)
                continue
            with z.open(member) as src, open(dest, "wb") as f:
                shutil.copyfileobj(src, f)
            LOG.info("추출: %s (%d bytes, sha256 %s)", dest.name, dest.stat().st_size, fontutil.sha256_of(dest))
        vf_dest = config.PRETENDARD_VF
        if not vf_dest.exists() or force:
            with z.open(VF_IN_ZIP) as src, open(vf_dest, "wb") as f:
                shutil.copyfileobj(src, f)
            LOG.info("추출: %s", vf_dest.name)
        lic = config.PRETENDARD_DIR / "LICENSE.txt"
        if not lic.exists() and "LICENSE.txt" in names:
            with z.open("LICENSE.txt") as src, open(lic, "wb") as f:
                shutil.copyfileobj(src, f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tmp", help="zip 다운로드 폴더(기본: 스크래치패드/CLAUDE_SCRATCHPAD 또는 시스템 temp)")
    ap.add_argument("--force", action="store_true", help="있어도 다시 받고 다시 추출")
    a = ap.parse_args(argv)
    fontutil.setup_logging("fetch")
    tmp = Path(a.tmp or os.environ.get("CLAUDE_SCRATCHPAD") or tempfile.gettempdir()) / "jennysans-dl"
    tmp.mkdir(parents=True, exist_ok=True)

    # 1) Pretendard zip → alternative TTF 9종 + VF
    need_zip = a.force or not all((config.PRETENDARD_TTF_DIR / f"Pretendard-{w}.ttf").exists() for w in config.WEIGHT_NAMES) \
        or not config.PRETENDARD_VF.exists()
    if need_zip:
        zp = download(config.PRETENDARD_ZIP_URL, tmp / "Pretendard-1.3.9.zip", config.PRETENDARD_ZIP_SHA256, force=False)
        extract_pretendard(zp, force=a.force)
    else:
        LOG.info("Pretendard alternative TTF 9종·VF 모두 있음 — zip 생략")
        for w in config.WEIGHT_NAMES:
            p = config.PRETENDARD_TTF_DIR / f"Pretendard-{w}.ttf"
            sha = manifest_sha(f"Pretendard/alternative-ttf/Pretendard-{w}.ttf")
            if sha:
                got = fontutil.sha256_of(p)
                if got != sha:
                    raise SystemExit(f"SHA 불일치: {p} 기대 {sha} 실제 {got}")
        LOG.info("Pretendard 정적 TTF SHA 검증(MANIFEST 기재분) OK")
    vf_sha = manifest_sha("Pretendard/PretendardVariable.ttf")
    if vf_sha and fontutil.sha256_of(config.PRETENDARD_VF) != vf_sha:
        raise SystemExit("PretendardVariable.ttf SHA 불일치")
    LOG.info("PretendardVariable.ttf SHA OK")

    # 2) Noto Sans KR VF
    download(config.NOTO_VF_URL, config.NOTO_VF, config.NOTO_VF_SHA256, force=a.force)

    # 요약
    for w in config.WEIGHT_NAMES:
        p = config.PRETENDARD_TTF_DIR / f"Pretendard-{w}.ttf"
        LOG.info("%-28s %9d bytes  %s", p.name, p.stat().st_size, fontutil.sha256_of(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
