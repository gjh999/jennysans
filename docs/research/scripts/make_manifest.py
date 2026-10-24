#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_manifest.py — sources/MANIFEST.md 생성 (font-researcher 작성, builder 의 fetch.py 가 URL·SHA 를 재사용)

입력: docs/research/measurements.json (파일별 sha256) + 아래 META (출처 URL·버전·아카이브 SHA)
출력: sources/MANIFEST.md
사용: PYTHONUTF8=1 python docs/research/scripts/make_manifest.py
"""
import json, os, hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MEAS = os.path.join(ROOT, "docs", "research", "measurements.json")
OUT = os.path.join(ROOT, "sources", "MANIFEST.md")

# 아카이브 SHA-256 은 2026-09-05 다운로드 직후 sha256sum 으로 실측 (스크래치패드 dl/ 기준)
META = [
    dict(dir="Pretendard", name="Pretendard", version="1.3.9", released="2023-11-05",
         home="https://github.com/orioncactus/pretendard",
         archives=[("Pretendard-1.3.9.zip", "https://github.com/orioncactus/pretendard/releases/download/v1.3.9/Pretendard-1.3.9.zip",
                    "04be351a74d6bf7d60c480a3087e51d185485d35a52023142af1df19eb8c428a", 47304526)],
         extracted="public/static/*.otf(9), public/variable/PretendardVariable.ttf, public/static/alternative/{Regular,Bold}.ttf, LICENSE.txt",
         license="OFL 1.1 — RFN 'Pretendard' (+누적: 'Source', 'Inter', 'M PLUS 1')",
         license_src="https://raw.githubusercontent.com/orioncactus/pretendard/main/LICENSE (zip 안 LICENSE.txt 는 구판·RFN Pretendard 만 기재)",
         status="한글 1순위 후보 (방식 A 기반)"),
    dict(dir="SourceHanSansKR", name="Source Han Sans KR (Region-specific Subset OTF)", version="2.005R", released="2025-06-18",
         home="https://github.com/adobe-fonts/source-han-sans",
         archives=[("18_SourceHanSansKR.zip", "https://github.com/adobe-fonts/source-han-sans/releases/download/2.005R/18_SourceHanSansKR.zip",
                    "ada0398122ebfebcae9efc1c6bb1dc5512c03b8f54035a8f527cd82a3c0441ac", 26022476)],
         extracted="SubsetOTF/KR/*.otf(7), LICENSE.txt",
         license="OFL 1.1 — RFN 'Source'", license_src="https://raw.githubusercontent.com/adobe-fonts/source-han-sans/master/LICENSE.txt",
         status="한글 2순위·결손 보충용(자모·기호)"),
    dict(dir="NotoSansKR", name="Noto Sans KR (noto-cjk Sans2.004 정적 OTF + Google Fonts 변수 TTF)", version="2.004 / 2.004-H2(GF)", released="2022-01-27 (GF 온보딩 2022-12-09)",
         home="https://github.com/notofonts/noto-cjk · https://github.com/google/fonts/tree/main/ofl/notosanskr",
         archives=[("17_NotoSansKR.zip", "https://github.com/notofonts/noto-cjk/releases/download/Sans2.004/17_NotoSansKR.zip",
                    "ac7eeb4e2b0d41de8ff31b2d6e1e2a41caf253fd5cefb380bfa1f40f1747b612", 26036461),
                   ("NotoSansKR[wght].ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf",
                    "194018e6b2b293a7964f037b25c0249ce1418bc9ab3c971060a03aa57861e252", 10414588)],
         extracted="NotoSansKR-*.otf(7), LICENSE, NotoSansKR[wght].ttf, OFL-googlefonts.txt",
         license="OFL 1.1 — 저작권 Adobe, RFN 'Source'(GF OFL.txt·VF name ID 0), 'Noto' 는 Google 상표(name ID 7)",
         license_src="https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE (저작권 줄 없음) · https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/OFL.txt",
         status="결손 보충 1순위(변수 TTF → 웨이트별 인스턴스), 한글 2순위 대안"),
    dict(dir="IBMPlexSansKR", name="IBM Plex Sans KR", version="@ibm/plex-sans-kr@1.1.0 (font Version 1.003)", released="2024-11-13",
         home="https://github.com/IBM/plex",
         archives=[("ibm-plex-sans-kr.zip", "https://github.com/IBM/plex/releases/download/%40ibm/plex-sans-kr%401.1.0/ibm-plex-sans-kr.zip",
                    "9837800c8e5aedf4123775e1d767afa482c983321bd2fc606c985f405d24562e", 73268731)],
         extracted="fonts/complete/ttf/hinted/*.ttf(8), fonts/complete/otf/*.otf(8), LICENSE.txt",
         license="OFL 1.1 — RFN \"Plex\"", license_src="https://raw.githubusercontent.com/IBM/plex/master/LICENSE.txt",
         status="제외(라틴 커버리지 부족: Latin-1 21/96·스페인어 3/21, 900 웨이트 없음)"),
    dict(dir="SpoqaHanSansNeo", name="Spoqa Han Sans Neo (OTF original)", version="v3.3.0 (font Version 1.100)", released="2021-06-07",
         home="https://github.com/spoqa/spoqa-han-sans",
         archives=[("SpoqaHanSansNeo_OTF_original.zip", "https://github.com/spoqa/spoqa-han-sans/releases/download/v3.3.0/SpoqaHanSansNeo_OTF_original.zip",
                    "cad46c24224ceb53181a8026c86a6c41abf740c67a7b14b15f722a79387bc644", 48012251)],
         extracted="SpoqaHanSansNeo-*.otf(5), LICENSE",
         license="OFL 1.1 — RFN 'Spoqa Han Sans', 'Spoqa Han Sans JP', 'Spoqa Han Sans Neo'", license_src="https://raw.githubusercontent.com/spoqa/spoqa-han-sans/main/LICENSE",
         status="제외(5 웨이트, 2021 이후 갱신 없음, 원본 고지 누락)"),
    dict(dir="NanumBarunGothic", name="나눔바른고딕 (Naver)", version="TTF 1.000/1.0.0.3/1.0.1.0, OTF 1.001 (2013–2015)", released="2013–2015",
         home="https://hangeul.naver.com/fonts/search?f=barun",
         archives=[("nanum-barun-gothic.zip", "https://hangeul.naver.com/hangeul_static/webfont/zips/nanum-barun-gothic.zip",
                    "950975a416c20ff7aabfeaf549d741a95f69eaf4a86dce2d7845fab909df6b68", 15416063)],
         extracted="*.ttf(4), *.otf(4) — zip 에 LICENSE 없음",
         license="확인 못 함 — 폰트 name ID 13='NHN Corporation', fsType=8, 사이트 표기 '오픈 라이선스(상업적 사용 허용)'. OFL 원문을 1차 출처에서 찾지 못함",
         license_src="(없음) 참고: Google Fonts nanumgothic OFL.txt 는 RFN 'Nanum, Naver Nanum, NanumGothic, …' 선언",
         status="제외(OFL 미확인, 스페인어 7/21, 4 웨이트)"),
    dict(dir="NanumGothic", name="Nanum Gothic (Google Fonts 배포본)", version="3.020", released="GF 2012-05-09",
         home="https://github.com/google/fonts/tree/main/ofl/nanumgothic",
         archives=[("NanumGothic-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Regular.ttf",
                    "76f45ef4a6bcff344c837c95a7dcc26e017e38b5846d5ae0cdcb5b86be2e2d31", 2054744),
                   ("NanumGothic-Bold.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/NanumGothic-Bold.ttf",
                    "f96298f9fb18e364d2370f4c3ce948ac67a2b61af992d7234bc15c42b033c674", 2073868)],
         extracted="NanumGothic-Regular.ttf, NanumGothic-Bold.ttf, OFL.txt",
         license="OFL 1.1 — RFN 'Nanum, Naver Nanum, NanumGothic, Naver NanumGothic, NanumMyeongjo, …'", license_src="https://raw.githubusercontent.com/google/fonts/main/ofl/nanumgothic/OFL.txt",
         status="제외(3 웨이트, 라틴·그리스·키릴 부족)"),
    dict(dir="NanumSquareNeo", name="나눔스퀘어 네오 (Naver)", version="1.000", released="2022",
         home="https://hangeul.naver.com/fonts/search?f=square",
         archives=[("nanum-square-neo.zip", "https://hangeul.naver.com/hangeul_static/webfont/zips/nanum-square-neo.zip",
                    "18d435f7fb9a46e39db7cdac1206c95dc65e7f6fc2a707588843baf8996c209a", 9765932)],
         extracted="NanumSquareNeo-Variable.ttf, OTF/*.otf(5) — zip 에 LICENSE 없음",
         license="확인 못 함 — name ID 13/14 없음, fsType=8", license_src="(없음)",
         status="제외(OFL 미확인, 스퀘어 스타일, 라틴 부족)"),
    dict(dir="GothicA1", name="Gothic A1 (HanYang I&C, Google Fonts 배포본)", version="2.50", released="GF 2018-02-24 (upstream 2017-12-07)",
         home="https://github.com/google/fonts/tree/main/ofl/gothica1 · https://github.com/hanyangfont/Gothic",
         archives=[("GothicA1-Regular.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/gothica1/GothicA1-Regular.ttf",
                    "211151bea98098c579610ab1114bb1bfe909057207db561f357b896d076c21ac", 2295400),
                   ("GothicA1-Bold.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/gothica1/GothicA1-Bold.ttf",
                    "2e883fa0ae548000996258b4101f2bb732a28b197264f49621a2cb16d6e9f126", 2287068)],
         extracted="GothicA1-Regular.ttf, GothicA1-Bold.ttf, OFL.txt (9 웨이트 중 2 개만 실측용으로 받음)",
         license="OFL 1.1 — 저작권 HanYang I&C, RFN 선언 없음", license_src="https://raw.githubusercontent.com/google/fonts/main/ofl/gothica1/OFL.txt",
         status="한글 3순위(커버리지 최상이나 2017 이후 미갱신·변수폰트 없음)"),
    dict(dir="WantedSans", name="Wanted Sans", version="1.0.3", released="2024-03-05",
         home="https://github.com/wanteddev/wanted-sans",
         archives=[("WantedSans-1.0.3.zip", "https://github.com/wanteddev/wanted-sans/releases/download/v1.0.3/WantedSans-1.0.3.zip",
                    "e0734c1e29426d2a6213650383fec37051145fccaed8360c8fe30d75321d98ab", 21656532)],
         extracted="ttf/*.ttf(7), otf/*.otf(7), variable/WantedSansVariable.ttf, OFL.txt",
         license="OFL 1.1 — 'The Wanted Sans Project Authors', OFL.txt 에 RFN 선언 없음(상표 고지는 name ID 7)", license_src="https://raw.githubusercontent.com/wanteddev/wanted-sans/main/OFL.txt",
         status="제외(400–1000 만 존재, 그리스·키릴 없음)"),
    dict(dir="SUIT", name="SUIT", version="v2.0.5 (font Version 2.040)", released="2024-07-24",
         home="https://github.com/sun-typeface/SUIT",
         archives=[("SUIT-otf.zip", "https://github.com/sun-typeface/SUIT/releases/download/v2.0.5/SUIT-otf.zip",
                    "c832868eb7b403b9d0af4a513ae50e8a0b1b7781471247fca71f1efef84b96aa", 2137873),
                   ("SUIT-Variable-ttf.zip", "https://github.com/sun-typeface/SUIT/releases/download/v2.0.5/SUIT-Variable-ttf.zip",
                    "ba6ae5cce0190698ae7b830886d98e34557b36f688a4f06c833efb267f5157c1", 812043)],
         extracted="SUIT-*.otf(9), SUIT-Variable.ttf, LICENSE",
         license="OFL 1.1 — RFN 'SUIT' (fsType=4 Preview&Print — OFL 과 상충)", license_src="https://raw.githubusercontent.com/sun-typeface/SUIT/main/LICENSE",
         status="제외(한글 11,172 중 8,504 자가 빈 글립, 라틴 부족)"),
    dict(dir="Inter", name="Inter", version="4.1 (font Version 4.001)", released="2024-11-16",
         home="https://github.com/rsms/inter",
         archives=[("Inter-4.1.zip", "https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip",
                    "9883fdd4a49d4fb66bd8177ba6625ef9a64aa45899767dde3d36aa425756b11e", 33707794)],
         extracted="InterVariable.ttf, InterVariable-Italic.ttf, extras/ttf/Inter-{Thin,Regular,Bold,Black}.ttf, extras/otf/Inter-Regular.otf, LICENSE.txt",
         license="OFL 1.1 — 'The Inter Project Authors', LICENSE.txt 에 RFN 줄 없음(Pretendard LICENSE 는 RFN 'Inter' 로 기재 → 예약명으로 취급)", license_src="https://raw.githubusercontent.com/rsms/inter/master/LICENSE.txt",
         status="라틴 1순위(Pretendard 내부 라틴의 원본)"),
    dict(dir="NotoSans", name="Noto Sans (Latin/Greek/Cyrillic, Google Fonts 변수 TTF)", version="2.015", released="2024-11-20",
         home="https://github.com/notofonts/latin-greek-cyrillic",
         archives=[("NotoSans[wdth,wght].ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosans/NotoSans%5Bwdth%2Cwght%5D.ttf",
                    "bfb7bb691513f12e734dc346c03a03f784912432d7e3fa8e56efcf906fe86b3d", 2049096)],
         extracted="NotoSans[wdth,wght].ttf, OFL.txt",
         license="OFL 1.1 — 'The Noto Project Authors', RFN 줄 없음('Noto' 는 Google 상표)", license_src="https://raw.githubusercontent.com/notofonts/latin-greek-cyrillic/main/OFL.txt",
         status="라틴 보조(그리스·키릴 확장 보충 후보)"),
    dict(dir="SourceSans3", name="Source Sans 3 (VF)", version="3.052R", released="2023-04-04",
         home="https://github.com/adobe-fonts/source-sans",
         archives=[("VF-source-sans-3.052R.zip", "https://github.com/adobe-fonts/source-sans/releases/download/3.052R/VF-source-sans-3.052R.zip",
                    "d8e2ac355e06e6a0f0e0a0b1ac0c2451afa707584d7bb9d6b11ef9e4b749904c", 795927)],
         extracted="VF/SourceSans3VF-Upright.ttf, VF/SourceSans3VF-Upright.otf, LICENSE.md",
         license="OFL 1.1 — RFN 'Source'", license_src="https://raw.githubusercontent.com/adobe-fonts/source-sans/release/LICENSE.md",
         status="라틴 2순위(Source Han Sans 계열 한글과 동일 디자이너 라틴; Latin Ext-A 보충 후보)"),
]

NOT_DOWNLOADED = [
    ("Freesentation 2.001", "https://github.com/Freesentation/freesentation", "OFL 1.1 ('The Freesentation Authors')", "제외 — 라틴이 Roboto(Apache-2.0) 기반이라 AGENTS §5 원칙 위배. 파일 미다운로드"),
    ("Paperlogy 1.001", "https://github.com/Freesentation/paperlogy", "OFL 1.1 ('The PAPERLOGY Authors')", "제외 — 한글이 Gmarket Sans(기하학적 디스플레이) 기반, 본문용 중립성 부족. 파일 미다운로드"),
    ("IBM Plex Sans (Latin)", "https://github.com/IBM/plex/releases/tag/%40ibm/plex-sans%401.1.0", "OFL 1.1 RFN \"Plex\"", "미측정 — Plex Sans KR 제외로 불필요"),
    ("Source Han Sans VF / OTC 전체", "https://github.com/adobe-fonts/source-han-sans/releases/tag/2.005R", "OFL 1.1 RFN 'Source'", "미다운로드(02_…VF.zip 888MB) — KR 서브셋 OTF 와 Google Fonts NotoSansKR[wght].ttf 로 대체"),
]


def main():
    meas = json.load(open(MEAS, encoding="utf-8"))
    by_dir = {}
    for r in meas:
        if "error" in r:
            continue
        rel = os.path.relpath(os.path.join(ROOT, r["file"]), os.path.join(ROOT, "sources")).replace("\\", "/")
        by_dir.setdefault(rel.split("/")[0], []).append((rel, r["size_bytes"], r["sha256"], r["name"].get("version", "")))
    lines = ["# sources/MANIFEST.md — 원본 폰트 대장 (font-researcher 2026-09-05 실측, `docs/research/scripts/make_manifest.py` 로 생성)", "",
             "`sources/` 는 git 에 넣지 않는다. 빌더의 `tools/fetch.py` 는 이 표의 URL·SHA-256 을 기준으로 재다운로드·검증한다.",
             "파일별 SHA-256 은 `docs/research/measurements.json` 의 `sha256` 필드와 동일하다.", ""]
    for m in META:
        lines.append(f"## {m['dir']}/ — {m['name']}")
        lines.append("")
        lines.append(f"- 버전: {m['version']} · 릴리스: {m['released']} · 홈: {m['home']}")
        lines.append(f"- 라이선스: {m['license']}")
        lines.append(f"- 라이선스 원문 출처: {m['license_src']}")
        lines.append(f"- 추출 내용: {m['extracted']}")
        lines.append(f"- 상태: **{m['status']}**")
        lines.append("")
        lines.append("| 다운로드 아카이브 | URL | 크기(bytes) | SHA-256 |")
        lines.append("|---|---|---|---|")
        for fn, url, sha, size in m["archives"]:
            lines.append(f"| `{fn}` | {url} | {size} | `{sha}` |")
        lines.append("")
        lines.append("| 추출 파일 | 크기(bytes) | SHA-256 | name ID 5 |")
        lines.append("|---|---|---|---|")
        for rel, size, sha, ver in sorted(by_dir.get(m["dir"], [])):
            lines.append(f"| `{rel}` | {size} | `{sha}` | {ver} |")
        # license files
        d = os.path.join(ROOT, "sources", m["dir"])
        for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if fn.lower().startswith(("license", "ofl")):
                p = os.path.join(d, fn)
                h = hashlib.sha256(open(p, "rb").read()).hexdigest()
                lines.append(f"| `{m['dir']}/{fn}` | {os.path.getsize(p)} | `{h}` | (라이선스 원문) |")
        lines.append("")
    lines.append("## 미다운로드·미측정 항목")
    lines.append("")
    lines.append("| 이름 | 출처 | 라이선스 | 사유 |")
    lines.append("|---|---|---|---|")
    for n, u, l, why in NOT_DOWNLOADED:
        lines.append(f"| {n} | {u} | {l} | {why} |")
    lines.append("")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", OUT, len(lines), "lines")


if __name__ == "__main__":
    main()
