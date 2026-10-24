# -*- coding: utf-8 -*-
"""
JennySans 빌드 진입점.

  PYTHONUTF8=1 python tools/build.py fetch      # 원본 다운로드·SHA 검증(tools/fetch.py)
  PYTHONUTF8=1 python tools/build.py static     # 정적 9 웨이트 TTF → dist/static
  PYTHONUTF8=1 python tools/build.py variable   # 변수 TTF → dist/variable
  PYTHONUTF8=1 python tools/build.py web        # WOFF2 + 분할 + CSS → dist/web, dist/css
  PYTHONUTF8=1 python tools/build.py verify     # 자체 점검 → build/verify-report.md
  PYTHONUTF8=1 python tools/build.py report     # build/BUILD-REPORT.md
  PYTHONUTF8=1 python tools/build.py preview    # build/preview/JennySans-Regular.png
  PYTHONUTF8=1 python tools/build.py all        # static → variable → web → verify → report → preview

로그: build/logs/<step>-<시각>.log. 캐시: build/cache/(Noto 인스턴스).
"""
import subprocess
import sys
import time
from pathlib import Path

from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
import fontutil  # noqa: E402

PY = sys.executable
TOOLS = Path(__file__).resolve().parent


def run(script, *args):
    cmd = [PY, str(TOOLS / script), *args]
    print(">>", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=str(config.ROOT))
    return r.returncode


def eighth_build_section(ss, vs):
    """BUILD-REPORT '8차 빌드 — 티켓 2·9·11' 절(팀장 결정 AGENTS §8 2026-09-09)."""
    before = fontutil.read_json(config.BUILD / "size-before-8.json", {})
    w0 = (ss.get("weights") or [{}])[0]
    adopted = vs.get("flatten_adopted") or []
    reverted = vs.get("flatten_reverted") or []
    top = sorted(adopted, key=lambda r: -r[1])[:12]
    L = ["## 8차 빌드 — 티켓 2·9·11 (2026-09-09, 팀장 결정 AGENTS §8)", "",
         "QA 1차 판정은 RELEASE OK 였지만 변수 폰트에 `nested_components` FAIL 1건이 남아 있었다. "
         "팀장 결정은 **승인 예외를 늘리지 않고 고치는 것**(AGENTS §8 2026-09-09) — 세 티켓을 한 번의 전체 재빌드로 처리했다.", ""]

    # ── 티켓 2
    L += ["### 티켓 2 — VF 중첩 컴포지트(nested_components) 잔여 5글립", "",
          "- **원인**: `build_variable.flatten_variable` 이 평탄화 채택 여부를 **정적 대비 ≤2 unit** 으로 판정했다. "
          "그 2 unit 은 spec 07 §7(c) 의 *Noto 유래 보충 글립* 허용치인데, 평탄화 대상은 전부 **Pretendard 유래 컴포지트**라 "
          "부품 원천이 다르다(VF = Pretendard VF 보간 / 정적 = Pretendard 정적 TTF) → 반올림으로 2.0~2.4 unit 이 생겼고 12 글립이 되돌려졌다.",
          "- **조치**: 판정 기준을 spec 07 §7(c) 그대로 **글립 성격에 따라 둘로 나눴다** — "
          f"Noto 유래 보충 글립 ≤{config.FLATTEN_TOL_NOTO} unit(`config.FLATTEN_TOL_NOTO`), "
          f"합성·컴포지트 평탄화 ≤{config.FLATTEN_TOL_COMPOSITE} unit(`config.FLATTEN_TOL_COMPOSITE`). "
          "외곽선은 손대지 않는다 — 평탄화는 `outer∘inner` 변환 합성이라 결과 외곽선이 같고, 그것을 bbox 로 증명한다.",
          f"- **결과**: {vs.get('flatten_detail', '(변수 요약 없음)')}",
          f"- **VF 중첩 컴포지트 잔존: {len(vs.get('nested_left') or [])}개** {vs.get('nested_left') or ''} "
          f"(6차: 5개 `uni01CB` `uni01C6` `uniFF20` `twodotenleader.hang` `uni2105`)",
          f"- 정적 9종은 6차와 동일하게 서브셋 후 전량 평탄화(웨이트당 {w0.get('flattened')}글립, bbox 불일치 {len(w0.get('flatten_bbox_mismatch', []))}).",
          f"- 되돌린 글립: {len(reverted)}개 {[r[0] for r in reverted] or '없음'}", ""]
    if top:
        L += ["평탄화 채택 글립 중 **9 웨이트 인스턴스 bbox·adv 를 정적과 비교**했을 때 편차가 큰 순서(unit):", "",
              "| 글립 | 정적 대비 bbox 최대차 | 진행폭 최대차 | 평탄화 전후 차 | 허용치(07 §7(c)) |", "|---|---|---|---|---|"]
        for r in top:
            L.append(f"| `{r[0]}` | {r[1]} | {r[3]} | {r[2]} | {r[4]} |")
        L += ["", f"- 전체 최대: bbox {vs.get('flatten_worst')} unit · adv {vs.get('flatten_worst_adv')} unit "
                  f"(둘 다 07 §7(c) 컴포지트 허용치 {config.FLATTEN_TOL_COMPOSITE} unit 안). "
                  "`verify_build.check_flatten` 이 같은 기준으로 독립 재측정한다.", ""]

    # ── 티켓 9
    st_vt = sorted({t for r in ss.get("weights", []) for t in (r.get("vertical_tables") or [])})
    L += ["### 티켓 9 — `vhea`/`vmtx` 웨이트 간 비대칭", "",
          "- **실측(6차 산출물)**: `vhea`·`vmtx` 가 **Thin·ExtraLight·Light 3 웨이트에만** 있었다(Regular~Black·VF 에는 없음). "
          "원본 `Pretendard-Thin/ExtraLight/Light.ttf` 자체가 이 두 테이블을 갖고 있어 그대로 실려 온 것이다.",
          "- **조치**: JennySans 는 세로쓰기를 지원하지 않으므로(spec 03) "
          f"`fontutil.DROP_TABLES_EXTRA` 에 `{list(fontutil.VERTICAL_TABLES)}` 를 추가해 **9 웨이트·VF 전부에서 제거**했다. "
          "서브셋 단계에서 드롭되고 `fix_tables` 가 한 번 더 확인한다.",
          f"- **결과**: 정적 9종 잔존 세로 테이블 {st_vt or '없음'} · VF {vs.get('vertical_tables') or '없음'} "
          "→ `verify_build.check_vertical` 이 전 파일에서 0 을 확인(FAIL 기준).", ""]

    # ── 티켓 11
    st_pruned = sorted({n for r in ss.get("weights", []) for n in (r.get("pruned") or [])})
    vf_pruned = vs.get("pruned") or []
    L += ["### 티켓 11 — `unreachable_glyphs` 고아 글립", "",
          "- **재확인 방법**: 제거 전에 `fontutil.reachable_glyphs()` 로 도달 가능 집합을 계산한다 — "
          "cmap(UVS 포함) ∪ **GSUB/GPOS/GDEF/MATH/BASE/JSTF 객체 트리에 이름이 한 번이라도 등장** ∪ 컴포넌트 폐포 ∪ 예약 글립"
          f"{list(fontutil.KEEP_GLYPHS_ALWAYS)}. "
          "fontbakery 는 룩업의 *출력*만 도달로 보지만 우리는 입력·클래스·앵커까지 도달로 인정하므로 **더 보수적**이다(잘못 지울 위험이 낮다).",
          f"- **제거한 글립** — 정적 9종 각 {len(st_pruned)}개: {st_pruned or '없음'} / VF {len(vf_pruned)}개: {vf_pruned or '없음'}",
          "- 정적 4자(`casedieresis.cn` `casetilde.cn` `tonos` `uniE118`)는 fontbakery WARN 과 일치. "
          "VF 는 여기에 `uni0189`·`cyrillictic.cn` 이 더 있었다(티켓 6 의 변환 컴포넌트 분해로 부품 참조가 사라진 것) — "
          "fontbakery VF WARN 이 실제로 6자였고 티켓 11 본문의 4자보다 많다.",
          "- `.null` 은 남긴다: fontTools 서브세터의 `recommended_glyphs` 정책(`.notdef`/`.null`/`nonmarkingreturn`/`CR`)이고 "
          "fontbakery 도 도달 검사에서 제외한다.",
          "- 검증: `verify_build.check_orphans` 가 전 파일에서 고아 0 을 FAIL 기준으로 확인한다.", ""]

    # ── 크기·글립 수 변화
    if before:
        L += ["### 산출물 크기·글립 수 변화 (6·7차 → 8차)", "",
              "| 파일 | 글립 6→8차 | bytes 6차 | bytes 8차 | 차이 |", "|---|---|---|---|---|"]
        rows = [(config.DIST_STATIC / f"JennySans-{w}.ttf") for w in config.WEIGHT_NAMES]
        rows += [config.DIST_VARIABLE / "JennySansVariable.ttf"]
        rows += [config.DIST_WEB / f"JennySans-{w}.woff2" for w in config.WEIGHT_NAMES]
        rows += [config.DIST_WEB / "JennySansVariable.woff2"]
        for p in rows:
            b = before.get(p.name)
            if not b or not p.exists():
                continue
            now = p.stat().st_size
            g = ""
            if p.suffix == ".ttf":
                f = TTFont(p, lazy=True)
                g = f"{b.get('numGlyphs')} → {f['maxp'].numGlyphs}"
                f.close()
            L.append(f"| {p.name} | {g} | {b['bytes']:,} | {now:,} | {now - b['bytes']:+,} |")
        L.append("")
    L += ["- **`dist/` 전 파일의 SHA-256 이 바뀐다.** `font-site` 는 `tools/package.py --render-site` 를 다시 돌려야 하고, "
          "`font-release` 는 문서(README·DISTRIBUTION·SHA256SUMS 등)의 크기·해시 수치를 다시 적어야 한다.", ""]
    L += ["### 참고 — 빌더가 돌려본 fontbakery·셰이핑 (정식 판정은 QA 몫)", "",
          "- `check-universal` 을 정적 9 + VF **한 번에** 실행: FAIL 4 · WARN 63 · INFO 30 · SKIP 335 · PASS 730 (`build/logs/fontbakery8.txt`). "
          "FAIL 4 는 전부 `All fonts:` 패밀리 단위 검사(`opentype/family/consistent_family_name` · `typographic_family_name` · "
          "`opentype/varfont/family_axis_ranges` · `family/single_directory`)이고, **정적(JennySans)과 변수(JennySans Variable)를 한 실행에 섞었기 때문**이다"
          "(AGENTS §7 이 정한 별도 패밀리 + 별도 디렉터리). 패밀리별로 나눠 돌리면(QA 방식) **네 검사 모두 PASS/SKIP** — 실측 확인.",
          "- WARN 은 6차 73건 / 10 검사 ID → **63건 / 9 검사 ID**. 줄어든 10건이 정확히 `unreachable_glyphs`(티켓 11)이고 **새로 생긴 WARN 종류는 없다**.",
          "- 티켓 관련 검사 6종(`nested_components` `unreachable_glyphs` `transformed_components` `case_mapping` `smart_dropout` `no_mac_entries`)을 "
          "Regular·Thin·VF 에 실행 → **18/18 PASS**.",
          "- 셰이핑 스모크(uharfbuzz, 한글·영문·스페인어·그리스·키릴·중유럽·괘선·합성·결합문자 9 샘플 × 정적 3 + VF): `.notdef` 는 "
          "**U+0149 ŉ 하나뿐**(AGENTS §8 2026-09-06 required 제외 결정) → 고아 글립 제거가 렌더에 영향 없음을 확인.", ""]
    return L


def report():
    ss = fontutil.read_json(config.BUILD / "static-summary.json", {})
    vs = fontutil.read_json(config.BUILD / "variable-summary.json", {})
    ws = fontutil.read_json(config.BUILD / "web-summary.json", {})
    L = [f"# BUILD-REPORT — JennySans {config.VERSION} (생성 {time.strftime('%Y-%m-%d %H:%M')})", ""]
    L += ["## 입력", "",
          f"- 기반: Pretendard {config.PRETENDARD_VERSION} `alternative/*.ttf`(glyf) 9종 + `PretendardVariable.ttf`",
          f"- 보충: Noto Sans KR {config.NOTO_VERSION} `NotoSansKR[wght].ttf` → wght 100…900 인스턴스(build/cache)",
          f"- charset: {ss.get('charset')} → 빌드 대상 {ss.get('build_target')} 코드포인트 (BUILD_SETS={list(config.BUILD_SETS)}, 게이트={config.GATE_SET})",
          f"- Pretendard 미보유 {ss.get('pretendard_missing')} → Noto 에서 보충 {ss.get('supplement_candidates')}, 어디에도 없음: {ss.get('neither') or '없음'}",
          f"- **required 인데 Pretendard·Noto 모두 없음(팀장 결정 필요): {ss.get('required_neither') or '없음'}**", ""]
    L += ["### 보충 규칙표 (docs/spec/07-supplement.md §6 = tools/config/supplement.json + config.SUPPLEMENT_RULE_PATCHES)", "",
          "| 규칙 | mode | ref | adv | sb | scale | ranges |", "|---|---|---|---|---|---|---|"]
    for r in ss.get("rules", []):
        sc = r.get("scale")
        sc = "" if not sc or sc == [None, None] else f"{sc[0]}×{sc[1]}"
        L.append(f"| {r['name']} | {r['mode']} | {r.get('ref') or ''} | {r.get('adv') or ''} | {r.get('sb') if r.get('sb') is not None else ''} | {sc} | {' '.join(r['ranges'])} |")
    L += ["", "- `+` 접미 규칙은 07 §6 JSON 이 덮지 않는 코드포인트 보정(U+2228 ∨ required 누락, ◌◎◉→circle, ◢◣◤◥→triangle, ℧ℵ→math-letter) — 아키텍트 확인 요청.",
          f"- 합성(07 §5·§4-11): {', '.join(ss.get('composites', {}).keys())} — ￢￣￤ 는 Pretendard 부품 컴포지트(셀 1920 중앙), ⅔ 는 ⅓ 컴포지트 구조 재현(uniE0CF+fraction+uniE0B7), "
          "≒ 는 equal+period×2 분해(4윤곽), ◈ 는 ◇+◆×0.5 분해(3윤곽 12점); 미러: ∼ = Noto ∽ 를 math-rel 규칙으로 변환 후 좌우 반전 + ReverseContourPen.",
          f"- 규칙표에 없는 코드포인트: {ss.get('unruled') or '없음'}. 참조값 실측: `build/supplement-refs-<W>.json`, 전수 시트: `build/supplement-sheet-<W>.png`."]
    L += ["", "## 정적 TTF (dist/static)", "",
          "| 파일 | 웨이트 | 글립 | cmap | 보충 | required 누락 | 크기(bytes) | SHA-256 | name 1 / 6 | 사라진 피처 | 시간 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in ss.get("weights", []):
        L.append(f"| {Path(r['out']).name} | {r['value']} | {r['numGlyphs']} | {r['cmap']} | {r['supplement']} (합성 {len(r.get('synthesized', []))}) | {r['required_missing']} "
                 f"{r['required_missing_list']} | {r['bytes']:,} | `{r['sha256']}` | {r['name1']} / {r['name6']} | {', '.join(r['dropped_features']) or '-'} | {r['seconds']}s |")
    if ss.get("weights"):
        cpd = ss["weights"][0].get("codepages", {})
        cpbits = 0
        for codec, (bit, need, miss) in cpd.items():
            tol = fontutil.KR_CODEPAGE_TOLERANCE if codec in ("cp949", "johab") else fontutil.SB_CODEPAGE_TOLERANCE
            if miss <= tol:
                cpbits |= 1 << bit
        L += ["", f"- OS/2 codePageRange 판정(Regular; 코덱: bit, 필요 문자 수, 누락 수): {cpd}",
              f"- 코드페이지 규칙(spec 03 §4 확정): 단일바이트 누락 ≤{fontutil.SB_CODEPAGE_TOLERANCE} 세트, cp949/johab 은 한자·가나 제외 누락 ≤{fontutil.KR_CODEPAGE_TOLERANCE} 세트, cp1258 해제 → Regular ulCodePageRange1 = 0x{cpbits:08X}"]
    if vs:
        L += ["", "## 변수 TTF (dist/variable)", "",
              f"- `{Path(vs['out']).name}`: 글립 {vs['numGlyphs']}, cmap {vs['cmap']}, gvar 글립 {vs['gvar_glyphs']}, 크기 {vs['bytes']:,} bytes, SHA-256 `{vs['sha256']}`",
              f"- 축: {vs['axis']} (원본 45–930 → 100–400–900 으로 제한, instancer L4), 인스턴스: {[(i[0], int(i[1])) for i in vs['instances']]}",
              f"- **보충 글립 달성 단계: stage {vs['stage']} = {vs['stage_label']}** — 보충 {vs['supplement']}개 중 gvar 델타 생성 {vs['supplement_with_deltas']}개, 실패 {vs['supplement_failed'] or '0'}",
              f"- name 1 `{vs['name1']}` / 6 `{vs['name6']}` / 25 `{vs['name25']}`, required 누락 {vs['required_missing']} {vs['required_missing_list']}, 사라진 피처 {vs['dropped_features']}, {vs['seconds']}s"]
    if ws:
        L += ["", "## 웹 (dist/web, dist/css)", "", "| 전체 WOFF2 | bytes |", "|---|---|"]
        for k, v in ws.get("full", {}).items():
            L.append(f"| {k}.woff2 | {v:,} |")
        L += ["", "| 분할 | 슬라이스 수 | 합계 bytes | 최소 | 최대 | 라틴(#123) bytes | rest(#124) |", "|---|---|---|---|---|---|---|"]
        for k, v in ws.get("sliced", {}).items():
            sizes = [x["bytes"] for x in v]
            lat = [x["bytes"] for x in v if x["index"] == 123]
            rest = [x for x in v if x["index"] == 124]
            L.append(f"| {k} | {len(v)} | {sum(sizes):,} | {min(sizes):,} | {max(sizes):,} | {lat[0] if lat else '-'} | "
                     f"{(str(rest[0]['count']) + ' cps / ' + str(rest[0]['bytes']) + ' B') if rest else '-'} |")
        L.append(f"\n- CSS: {ws.get('css')} · 슬라이스 정의: `{config.SLICES_JSON.relative_to(config.ROOT)}` (docs/research/google-kr-slices.css 파싱)")
        L.append("- 분할 파일명은 AGENTS §7·spec 01 §5 의 `JennySans-<W>.subset.<n>.woff2`(팀장 프롬프트의 `.<n>.woff2` 대신) — 불일치 보고")
    vr = config.BUILD / "verify-report.md"
    if vr.exists():
        head = vr.read_text(encoding="utf-8").splitlines()[2]
        L += ["", "## 자체 점검", "", f"- {head} → `build/verify-report.md`"]
    neither = ss.get("required_neither") or ""
    L += ["", "## required 누락 규명 (2차 빌드까지 4자 → 3차 빌드에서 합성으로 해소)", "",
          f"- 현재 required 인데 채울 수 없는 코드포인트: {neither or '없음'}.",
          "- 2차 빌드까지 정적 9종·변수 모두 ⅔ U+2154 [KS 8/88]·∼ U+223C [KS 1/13]·≒ U+2252 [KS 1/54]·◈ U+25C8 [KS 2/34] 4자가 누락됐다. 원인: 기반 Pretendard 1.3.9 와 보충 Noto Sans KR 2.004 VF **둘 다 보유하지 않은 KS X 1001 기호**이고 AGENTS §5-1 대장 밖 원본(Gothic A1 4자 전부·SHS 2.005R ≒◈·Noto Sans/Source Sans 3 ⅔)은 쓰지 않았기 때문.",
          "- 3차 빌드: 07 §5 합성안(AGENTS §8 채택)으로 Pretendard 자체 부품에서 합성 — ⅔(⅓ 구조 컴포지트), ∼(Noto ∽ 미러), ≒(equal+period 분해), ◈(◇+◆×0.5 분해). 3차 원본 추가 없음 → 라이선스 고지 변화 없음.",
          f"- OS/2 cp949/johab 비트: 한자·가나 제외 누락 ≤{fontutil.KR_CODEPAGE_TOLERANCE} 허용(현재 누락은 ŉ U+0149 뿐 — required 제외 결정).", ""]
    w0 = (ss.get("weights") or [{}])[0]
    L += ["## 6차 빌드 — QA 1차 티켓(docs/qa/ISSUES.md) 처리 내역", "",
          "| # | 티켓 | 처리 | 근거/검증 |", "|---|---|---|---|",
          f"| 1 | U+01C4 DŽ 없음(case_mapping) | `D`+`Zcaron` 컴포지트 합성(진행폭 = 합), 정적·VF(컴포넌트 오프셋 델타) — `config.SUPPLEMENT_COMPOSITE_PATCHES` | verify `tables`: 구조·adv 검사 |",
          f"| 2 | 중첩 컴포넌트(nested_components) | 정적: 서브셋 후 `supplement.flatten_nested`(outer∘inner 변환 합성, 외곽선·bbox 불변 검증) {w0.get('flattened')}글립, bbox 불일치 {len(w0.get('flatten_bbox_mismatch', []))}. VF: 9 인스턴스에서 전개한 오프셋으로 gvar 재생성 → 6차는 중첩 167 중 155 채택·12 되돌림(정적 대비 2.0~2.4 unit)으로 **중첩 5 잔존** → **8차에서 판정 기준을 07 §7(c) 로 고쳐 전량 채택**(아래 8차 절) | verify `tables`: 중첩 0 FAIL 기준(8차부터 VF 포함) |",
          "| 3 | Mac name 레코드(no_mac_entries) | platformID 1 레코드 기록 안 함(정적·VF, FeatureParams 보존도 Windows 만) | verify `tables`: platformID 1 == 0 |",
          f"| 4 | prep 없음(smart_dropout) | `prep` = `{' '.join(fontutil.PREP_ASSEMBLY)}` 추가(gftools fix-nonhinting 동일), gasp 0x000F 유지 | verify `tables`: prep 프로그램 일치 |",
          f"| 6 | VF 변환(반전·스케일) 컴포넌트(transformed_components) | VF 에서 해당 글립을 외곽선으로 분해(반전은 윤곽 방향 복원), gvar = 9 인스턴스 분해 좌표(참조 델타에 같은 변환 + 오프셋 델타) → 최신 빌드: {vs.get('decompose_detail', '(변수 요약 없음)')} | verify `tables`: VF 잔존 시 '승인 예외 후보(원본 동일)' INFO |",
          "| 5 | ㅥ 하단 편차(hangul-pos) | 6차: 규칙 `hangul-compat-baseline`(U+3165–3186, Noto 기저선 ±25 판정, 웨이트별 dy = P ㄴ 하단 − sy·N ㄴ 하단) 추가 — 실제 정렬된 글립 0개. **7차에서 되돌림**(아래 절: 결함 아님) | — |",
          ""]
    L += ["## 7차 빌드 — 티켓 5 재검토: 결함 아님(원본 재현), 검사식 정정", "",
          "실측 근거 전문 `build/ticket5-measure.md`. 요약(bbox 하단 y, N=Noto 인스턴스 UPM 1000 · P/J UPM 2048, sy=1.965):", "",
          "| 웨이트 | N ㄴ | N ㅥ | N 차 | P ㄴ = J ㄴ | J ㅥ | J 차 | 기대 sy×N차 | 오차 |",
          "|---|---|---|---|---|---|---|---|---|",
          "| Thin | 143 | 147 | +4 | 270 | 279 | +9 | +7.9 | +1.1 |",
          "| ExtraLight | 143 | 146 | +3 | 270 | 277 | +7 | +5.9 | +1.1 |",
          "| Light | 143 | 145 | +2 | 272 | 275 | +3 | +3.9 | −0.9 |",
          "| Regular | 144 | 141 | −3 | 272 | 267 | −5 | −5.9 | +0.9 |",
          "| Medium | 144 | 139 | −5 | 272 | 263 | −9 | −9.8 | +0.8 |",
          "| SemiBold | 144 | 137 | −7 | 272 | 259 | −13 | −13.8 | +0.8 |",
          "| Bold | 145 | 135 | −10 | 274 | 255 | −19 | −19.7 | +0.7 |",
          "| ExtraBold | 145 | 134 | −11 | 274 | 253 | −21 | −21.6 | +0.6 |",
          "| Black | 145 | 132 | −13 | 274 | 249 | −25 | −25.5 | +0.5 |", "",
          "- **Noto Sans KR 자신이 ㅥ 을 ㄴ 보다 아래에 그린다**(Regular −3 → Black −13, 굵을수록 커짐 — ㄴ 두 개를 붙인 글자의 광학 보정). "
          "Thin~Light 는 반대로 +2~+4 로 웨이트마다 의도가 다르다.",
          "- 우리 산출물의 편차는 전부 **sy × Noto 편차와 오차 ≤1.1 unit**(좌표 정수 반올림 범위)으로 일치 = 이식이 정확하다는 증거. "
          "여기서 ㅥ 을 올리면 원본 디자인 변경이라 AGENTS §1-1·§5, font-builder §3(외곽선 임의 수정 금지)에 어긋난다 → **결함 아님**.",
          "- 조치 ① `config.SUPPLEMENT_RULE_PATCHES_FIRST = []` 로 되돌리고 `supplement.Engine` 의 align_bottom 재정렬 기능 제거. "
          "되돌린 규칙표로 U+3165–U+318E 보충 41자 × 9 웨이트 = 369 글립을 다시 생성해 비교 → **bbox 최대 차 0 unit·진행폭 불일치 0** "
          "(그래서 7차는 static/variable/web 재빌드 없이 verify·report 만 재실행, `dist/` 는 6차 그대로).",
          "- 조치 ② `verify_build` hangul-pos 검사식 정정: 고정 ±15 → **|(J대상하단 − J ㄴ하단) − sy×(N대상하단 − N ㄴ하단)| ≤ 6 unit**, "
          "대상은 U+3165–U+318E 보충 41자 전부, N 값은 Noto VF 를 웨이트별 인스턴스해 직접 측정(`verify_build._noto_bottoms`). "
          "스펙 07 §8-3 참조쌍 검사(결과비 = 원본비 ±2%)와 같은 철학.",
          "- QA 몫: `docs/qa/scripts/supplement.py` 의 hangul-pos 도 같은 식으로 갱신 필요(빌더는 QA 구역을 고치지 않음).", ""]
    L += eighth_build_section(ss, vs)
    L += ["## 팀장 공지(2026-09-06) 반영 여부", "",
          "1. 스케일 고정 해제 → `config.SUPPLEMENT_CATEGORIES` 카테고리(코드포인트 범위)별 dict. 임시값 한글·자모 2.03/1770 센터링, 기호 2.048/Noto 폭×스케일. "
          "`docs/spec/07-supplement.md` 미도착(빌드 시점) → 도착 시 표를 옮겨 재빌드. 빌더 실측(`build/supplement-measure.md`, 웨이트 일치 400/700): 한글 몸체 sx≈1.98·sy≈1.965, 진행폭비 1.924, 오프셋 dx≈-24·dy≈-10 — 2.03 은 Noto VF 기본(wght 100) 대비 값으로 추정.",
          f"2. 빌드 대상 = required ∪ recommended ∪ korean-old(∩ Pretendard·Noto 보유) = {ss.get('build_target')} → 게이트는 required 만. 갱신된 charset(required {ss.get('charset', {}).get('required')}) 반영.",
          "3. 변수 패밀리명 `JennySans Variable`(ko `제니산스 Variable`), PS `JennySansVariable-<W>`, 파일 `JennySansVariable.ttf`; RFN 두 개('JennySans', '제니산스')를 name ID 0 첫 줄(LICENSE 정본 문구)에 기재.",
          "4. RFN 검사: 식별 레코드(1/2/3/4/6/16/17/18/21/22/25)·fvar 인스턴스명·STAT 이름·글립명만 검사, 고지 레코드(0/7/9)의 원저작자 표기는 유지 여부를 별도 PASS 항목으로 확인(`verify_build.check_rfn`).", ""]
    L += ["## 스펙 대비 메모(빌더)", "",
          "- name ID 7 은 우리 상표 + 원본 상표 고지 누적(팀장 지시·리서치 02 §3). spec 02 §2 의 단문과 다름.",
          "- post.underline 은 Regular 값(-258/139)으로 전 웨이트 통일(spec 03 §7 '전 파일 동일'). 원본 Bold 는 -214/188.",
          "- STAT 은 정적에도 기록(spec 02 §4-3), Version 0x00010002. 변수 폰트 STAT 은 wght 축만(원본의 ital 축 제거).",
          "- 웹 분할은 AGENTS §8 결정(Google 124 슬라이스 그대로 + rest) — spec 05 §3-1 공통 슬라이스 0~7 계획과 다름.",
          "- 사라진 피처 사유(실측): `ss16` 은 룩업 63 하나가 PUA 아이콘 글립(uF0001/uF0002/iconDot.*)만 치환하므로 서브셋(charset 밖) 후 빈 피처가 되어 제거 — 가나와 무관. "
          "변수 폰트의 `rlig` 는 원본 PretendardVariable.ttf 에서 이미 **룩업이 0개인 빈 피처**(`LookupListIndex=[]`)라 서브세터가 정리한 것 — 기능 손실 없음.",
          f"- name ID 11 = {config.VENDOR_URL}(확정 도메인), ID 0 첫 줄 = LICENSE 정본 문구(verify `names` 항목으로 확인).",
          "- Noto 인스턴스는 build/cache 에 캐시(코드포인트 집합 해시로 무효화)."]
    out = config.BUILD / "BUILD-REPORT.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("→", out)
    return 0


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    config.BUILD.mkdir(parents=True, exist_ok=True)
    steps = {
        "fetch": lambda: run("fetch.py", *rest),
        "static": lambda: run("build_static.py", *rest),
        "variable": lambda: run("build_variable.py", *rest),
        "web": lambda: run("build_web.py", *rest),
        "verify": lambda: run("verify_build.py", *rest),
        "report": report,
        "preview": lambda: run("preview.py", *rest),
        "sheets": lambda: run("supplement_sheet.py", *rest),
        "measure": lambda: run("measure_supplement.py", *rest),
    }
    if cmd == "all":
        t0 = time.time()
        rc = 0
        for s in ("static", "variable", "web", "verify"):
            r = steps[s]()
            rc = rc or r
            if r and s != "verify":
                print(f"!! {s} 실패(rc={r}) — 중단")
                return r
        report()
        steps["preview"]()
        steps["sheets"]()
        print(f"all 완료 {time.time() - t0:.0f}s (verify rc={rc})")
        return rc
    if cmd not in steps:
        print(__doc__)
        return 2
    return steps[cmd]()


if __name__ == "__main__":
    sys.exit(main())
