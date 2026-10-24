# -*- coding: utf-8 -*-
"""
결손 글립 보충 엔진 — docs/spec/07-supplement.md §3~§6 구현.

입력: 같은 웨이트의 P(Pretendard 좌표계 폰트: 정적 TTF 또는 변수 폰트의 부품 인스턴스)와 N(Noto Sans KR 인스턴스, UPM 1000).
규칙표: tools/config/supplement.json (07 §6 그대로) + config.SUPPLEMENT_RULE_PATCHES(스펙 누락 코드포인트 보정).
모드: fixed(한글류) · ref(참조쌍, adv=ref|fit) · ref-baseline · affine · empty · composites(부품 조합) · mirror.
허용 조작은 아핀 변환·컴포지트·분해뿐(외곽선 신규 제작 없음).

Noto VF 서브셋·인스턴스와 Pretendard VF 부품 인스턴스는 build/cache 에 캐시(코드포인트 집합 해시).
"""
import hashlib
import json
import sys
from pathlib import Path

from fontTools.misc.roundTools import otRound
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import flagOverlapSimple
from fontTools.varLib import instancer

try:
    from . import config, fontutil
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import config
    import fontutil

LOG = fontutil.LOG


# ------------------------------------------------------------------ 규칙표
def parse_range(s):
    a, _, b = s.partition("-")
    lo = int(a[2:], 16)
    hi = int(b[2:], 16) if b else lo
    return lo, hi


def cp_of(s):
    return int(s[2:], 16)


class Rules:
    def __init__(self, path=None):
        path = Path(path or config.SUPPLEMENT_JSON)
        self.raw = json.loads(path.read_text(encoding="utf-8"))
        self.rules = []
        for r in (list(getattr(config, "SUPPLEMENT_RULE_PATCHES_FIRST", [])) + self.raw["rules"]
                  + list(getattr(config, "SUPPLEMENT_RULE_PATCHES", []))):
            r = dict(r)
            r["_ranges"] = [parse_range(x) for x in r["ranges"]]
            self.rules.append(r)
        self.composites = {cp_of(k): v for k, v in self.raw.get("composites", {}).items()}
        for k, v in getattr(config, "SUPPLEMENT_COMPOSITE_PATCHES", {}).items():   # QA 티켓 등으로 추가된 합성
            self.composites[cp_of(k)] = v
        self.mirror = {cp_of(k): v for k, v in self.raw.get("mirror", {}).items()}
        self.by_name = {r["name"]: r for r in self.rules}

    def rule_for(self, cp):
        for r in self.rules:
            for lo, hi in r["_ranges"]:
                if lo <= cp <= hi:
                    return r
        return None

    def ref_cps(self):
        return sorted({cp_of(r["ref"]) for r in self.rules if "ref" in r})

    def part_names(self):
        """컴포지트가 이름으로 참조하는 부품 글립(PUA 분자·분모 등)."""
        out = set()
        for v in self.composites.values():
            for k in ("numerator", "denominator"):
                if k in v:
                    out.add(v[k])
        return sorted(out)

    def part_cps(self):
        out = set()
        for v in self.composites.values():
            if "component" in v:
                out.add(cp_of(v["component"]))
            if "from_pattern" in v:
                out.add(cp_of(v["from_pattern"]))
            for p in v.get("parts", []):
                out.add(cp_of(p[0] if isinstance(p, list) else p))
            for p in v.get("sequence", []):
                out.add(cp_of(p))
            for k in ("box", "mark"):
                if v.get(k):
                    out.add(cp_of(v[k]))
        return sorted(out)


def inner_contour_bbox(glyphset, name):
    """윤곽 2개 이상인 글립(□ 등)에서 가장 작은 윤곽의 bbox(제어점 포함 — □ 모서리 곡선은 bbox 안쪽) = 속공간."""
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    rp = DecomposingRecordingPen(glyphset)
    glyphset[name].draw(rp)
    boxes, pts = [], []
    for op, args in rp.value:
        if op in ("moveTo", "lineTo", "qCurveTo", "curveTo"):
            pts.extend(a for a in args if a is not None)
        if op in ("closePath", "endPath") and pts:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            boxes.append((min(xs), min(ys), max(xs), max(ys)))
            pts = []
    if len(boxes) < 2:
        raise ValueError(f"{name}: 속공간 윤곽 없음(윤곽 {len(boxes)})")
    return min(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))


# ------------------------------------------------------------------ 캐시된 인스턴스
def _key(cps):
    return hashlib.sha256(",".join(f"{c:X}" for c in sorted(cps)).encode()).hexdigest()[:10]


def _subset_vf(src, cps, out, glyph_names=()):
    from fontTools import subset
    f = TTFont(src)
    opts = fontutil.subset_options(cps, layout=False, hinting=False)
    opts.drop_tables += ["GSUB", "GPOS", "GDEF", "vhea", "vmtx", "VORG", "prep", "cvt ", "fpgm", "gasp", "STAT", "MVAR", "VVAR"]
    s = subset.Subsetter(opts)
    s.populate(unicodes=set(cps), glyphs=list(glyph_names))
    s.subset(f)
    f.save(out)
    f.close()


def _instance(vf_path, weight_value, out):
    vf = TTFont(vf_path)
    inst = instancer.instantiateVariableFont(vf, {"wght": weight_value}, inplace=True, optimize=True,
                                             overlap=instancer.OverlapMode.KEEP_AND_SET_FLAGS)
    inst.save(out)
    inst.close()


def noto_subset_vf(cps):
    config.CACHE.mkdir(parents=True, exist_ok=True)
    out = config.CACHE / f"NotoSansKR-sup-{_key(cps)}[wght].ttf"
    if not out.exists():
        LOG.info("Noto VF 서브셋 생성(%d cps) → %s", len(cps), out.name)
        _subset_vf(config.NOTO_VF, cps, out)
    return out


def noto_instance(cps, weight_value):
    vf = noto_subset_vf(cps)
    out = config.CACHE / f"NotoSansKR-sup-{_key(cps)}-{weight_value}.ttf"
    if not out.exists():
        LOG.info("Noto 인스턴스 wght=%d → %s", weight_value, out.name)
        _instance(vf, weight_value, out)
    return out


def pretendard_parts_instance(cps, weight_value, glyph_names=()):
    """변수 폰트 빌드용: Pretendard VF 에서 참조·부품 글립(코드포인트 + 이름)만 뽑아 해당 wght 로 인스턴스(캐시)."""
    config.CACHE.mkdir(parents=True, exist_ok=True)
    key = _key(list(cps) + [int(hashlib.sha256(n.encode()).hexdigest()[:4], 16) for n in glyph_names])  # 결정적 키
    vf = config.CACHE / f"PretendardVF-parts-{key}[wght].ttf"
    if not vf.exists():
        LOG.info("Pretendard VF 부품 서브셋(%d cps + %d names) → %s", len(cps), len(glyph_names), vf.name)
        _subset_vf(config.PRETENDARD_VF, cps, vf, glyph_names)
    out = config.CACHE / f"PretendardVF-parts-{key}-{weight_value}.ttf"
    if not out.exists():
        LOG.info("Pretendard VF 부품 인스턴스 wght=%d → %s", weight_value, out.name)
        _instance(vf, weight_value, out)
    return out


# ------------------------------------------------------------------ 측정 헬퍼
class Metrics:
    """폰트 하나의 cmap/bbox/adv 조회."""

    def __init__(self, font):
        self.font = font
        self.cmap = font.getBestCmap()
        self.glyphset = font.getGlyphSet()
        self.hmtx = font["hmtx"].metrics
        self._bbox = {}

    def name(self, cp):
        return self.cmap.get(cp)

    def has(self, cp):
        return cp in self.cmap

    def bbox_name(self, name):
        if name not in self._bbox:
            p = BoundsPen(self.glyphset)
            self.glyphset[name].draw(p)
            self._bbox[name] = p.bounds
        return self._bbox[name]

    def bbox(self, cp):
        return self.bbox_name(self.cmap[cp])

    def adv(self, cp):
        return self.hmtx[self.cmap[cp]][0]

    def adv_name(self, name):
        return self.hmtx[name][0]

    def measure(self, cp):
        b = self.bbox(cp)
        adv = self.adv(cp)
        if b is None:
            return dict(adv=adv, bbox=None)
        x0, y0, x1, y1 = b
        return dict(adv=adv, bbox=[round(v, 1) for v in b], w=round(x1 - x0, 1), h=round(y1 - y0, 1),
                    cx=round((x0 + x1) / 2, 1), cy=round((y0 + y1) / 2, 1), lsb=round(x0, 1), rsb=round(adv - x1, 1))


# ------------------------------------------------------------------ 엔진
class Engine:
    """P: 부품(컴포지트·분해) 원천 폰트, P_ref: 참조쌍 측정용 폰트(기본 = P). 변수 폰트 빌드는 P=VF 부품 인스턴스, P_ref=정적 Pretendard-<W>.ttf
    (정적 빌드와 같은 참조값을 쓰기 위해 — Pretendard 정적 TTF 와 VF 인스턴스는 미세하게 달라 fit 진행폭이 어긋난다)."""

    def __init__(self, P, N, rules, weight_value, P_ref=None):
        self.P = Metrics(P)
        self.P_ref = Metrics(P_ref) if P_ref is not None else self.P
        self.N = Metrics(N)
        self.rules = rules
        self.w = weight_value
        self.refs = {}

    # ---- 참조 측정
    def ref_pair(self, rule):
        rcp = cp_of(rule["ref"])
        if rcp in self.refs:
            return self.refs[rcp]
        if not self.P_ref.has(rcp) or not self.N.has(rcp):
            raise KeyError(f"참조 글립 U+{rcp:04X} 이 P/N 에 없음 (rule {rule['name']})")
        pm, nm = self.P_ref.measure(rcp), self.N.measure(rcp)
        if pm["bbox"] is None or nm["bbox"] is None:
            raise KeyError(f"참조 글립 U+{rcp:04X} 외곽선 없음")
        self.refs[rcp] = (pm, nm)
        return pm, nm

    # ---- 아핀 결정: 반환 (a, d, e, f, adv, info)
    def transform_for(self, cp, rule):
        mode = rule["mode"]
        ncp = cp
        n_adv = self.N.adv(ncp)
        nb = self.N.bbox(ncp)
        info = dict(rule=rule["name"], mode=mode, src_adv=n_adv)
        if mode == "fixed":
            sx, sy, dy = rule["sx"], rule["sy"], float(rule.get("dy", 0))
            adv = otRound(n_adv * rule["adv_ratio"])
            e = adv / 2.0 - sx * n_adv / 2.0
            info.update(scale=(sx, sy))
            # (7차) 글립별 기저선 재정렬(align_bottom/align_tol)은 제거했다 — QA 티켓 5 결론: Noto 가 ㅥ 을 ㄴ 보다
            #   아래에 그리는 것은 원본 디자인이고 우리는 그것을 sy 배로 정확히 재현한다(`build/ticket5-measure.md`).
            #   재정렬은 외곽선 위치를 임의로 바꾸는 것이라 AGENTS §1-1·§5 위반. 규칙표는 균등 스케일 + 고정 dy 만 쓴다.
            return sx, sy, e, dy, adv, info
        if mode == "affine":
            sx, sy = rule["sx"], rule["sy"]
            tx, ty = rule.get("tx", 0), rule.get("ty", 0)
            if "center_x" in rule:
                e = rule["center_x"] - sx * n_adv / 2.0 + tx
            else:
                e = float(tx)
            info.update(scale=(sx, sy))
            return sx, sy, e, float(ty), int(rule["adv"]), info
        if mode in ("ref", "ref-baseline"):
            pm, nm = self.ref_pair(rule)
            if rule.get("scale_by") == "width":
                s = pm["w"] / nm["w"]
            else:
                s = pm["h"] / nm["h"]
            info.update(ref=rule["ref"], scale=(s, s), ref_P=pm, ref_N=nm)
            f = 0.0 if mode == "ref-baseline" else pm["cy"] - s * nm["cy"]
            adv_policy = rule.get("adv", "ref")
            if adv_policy == "ref":
                e = pm["cx"] - s * nm["cx"]
                return s, s, e, f, int(pm["adv"]), info
            # fit
            if nb is None:
                return s, s, 0.0, f, otRound(2 * 150), info
            w = s * (nb[2] - nb[0])
            sb = rule.get("sb", 150)
            if sb == "ref-lsb":
                l = r = pm["lsb"]
            elif isinstance(sb, list):
                l, r = sb
            else:
                l = r = float(sb)
            adv = otRound(w + l + r)
            e = l - s * nb[0]
            info.update(sb=(l, r))
            return s, s, e, f, adv, info
        raise ValueError(f"알 수 없는 mode {mode}")

    # ---- 글립 생성
    def _finish(self, pen, adv, info, src_glyph=None):
        glyph = pen.glyph()
        if src_glyph is not None and (not src_glyph.isComposite()) and src_glyph.numberOfContours > 0 \
                and (src_glyph.flags[0] & flagOverlapSimple) and glyph.numberOfContours > 0:
            glyph.flags[0] |= flagOverlapSimple
        glyph.recalcBounds(self.P.font["glyf"] if glyph.isComposite() else None)
        lsb = glyph.xMin if glyph.numberOfContours != 0 else 0
        info.update(adv=adv, contours=glyph.numberOfContours,
                    bbox=[glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax] if glyph.numberOfContours != 0 else None)
        return glyph, adv, lsb, info

    def make_noto(self, cp, rule):
        """Noto 글립을 규칙대로 변환한 단순 글립."""
        if rule["mode"] == "empty":
            pen = TTGlyphPen(None)
            return self._finish(pen, int(rule["adv"]), dict(rule=rule["name"], mode="empty", cp=cp))
        a, d, e, f, adv, info = self.transform_for(cp, rule)
        info["cp"] = cp
        name = self.N.name(cp)
        info["src"] = name
        nb = self.N.bbox(cp)
        info["src_bbox"] = [round(v, 1) for v in nb] if nb else None
        pen = TTGlyphPen(self.N.glyphset)
        self.N.glyphset[name].draw(TransformPen(pen, (a, 0, 0, d, e, f)))
        return self._finish(pen, adv, info, self.N.font["glyf"][name])

    def make_mirror(self, cp, spec):
        """spec: {"from": "U+223D", "rule": "math-rel", "axis": "x"} — 변환 후 bbox 중심 x 기준 좌우 반전 + 윤곽 방향 복원."""
        src = cp_of(spec["from"])
        rule = self.rules.by_name[spec["rule"]]
        a, d, e, f, adv, info = self.transform_for(src, rule)
        nb = self.N.bbox(src)
        cx = a * (nb[0] + nb[2]) / 2.0 + e
        name = self.N.name(src)
        pen = TTGlyphPen(self.N.glyphset)
        rev = ReverseContourPen(pen)
        self.N.glyphset[name].draw(TransformPen(rev, (-a, 0, 0, d, 2 * cx - e, f)))
        info.update(cp=cp, mode="mirror", src=name, mirror_of=spec["from"], src_bbox=[round(v, 1) for v in nb])
        return self._finish(pen, adv, info, self.N.font["glyf"][name])

    def make_composite(self, cp, spec):
        """07 §5·§4-11 합성. 반환 glyph(컴포지트 또는 분해된 단순 글립)."""
        P = self.P
        info = dict(cp=cp, mode="composite", rule="composite")
        if "component" in spec:   # ￢ ￣ ￤ — Pretendard 자체 컴포지트, 셀 중앙
            comp = P.name(cp_of(spec["component"]))
            cell = int(spec["cell"])
            x = otRound((cell - P.adv_name(comp)) / 2.0)
            pen = TTGlyphPen(P.glyphset)
            pen.addComponent(comp, Transform(1, 0, 0, 1, x, 0))
            info.update(components=[(comp, x, 0)])
            return self._finish(pen, cell, info)
        if "sequence" in spec:   # 예: DŽ U+01C4 = D + Zcaron 나란히(진행폭 = 합) — QA 티켓 1
            pen = TTGlyphPen(P.glyphset)
            x = 0
            comps = []
            for part in spec["sequence"]:
                nm = P.name(cp_of(part))
                pen.addComponent(nm, Transform(1, 0, 0, 1, x, 0))
                comps.append((nm, x, 0))
                x += P.adv_name(nm)
            info.update(components=comps)
            return self._finish(pen, x, info)
        if "from_pattern" in spec:   # ⅔ — ⅓ 컴포지트 구조 재현
            pat = P.font["glyf"][P.name(cp_of(spec["from_pattern"]))]
            comps = [(c.glyphName, c.x, c.y) for c in pat.components]
            if len(comps) != 3:
                raise ValueError(f"패턴 글립 컴포넌트 수 {len(comps)} ≠ 3")
            num_pat, frac, den_pat = comps
            x_f, x_d = frac[1], den_pat[1]
            k = P.adv_name(num_pat[0]) - x_f
            j = x_f + P.adv_name(frac[0]) - x_d
            num, den = spec["numerator"], spec["denominator"]
            x_f2 = P.adv_name(num) - k
            x_d2 = x_f2 + P.adv_name(frac[0]) - j
            adv = x_d2 + P.adv_name(den)
            pen = TTGlyphPen(P.glyphset)
            pen.addComponent(num, Transform(1, 0, 0, 1, 0, 0))
            pen.addComponent(frac[0], Transform(1, 0, 0, 1, x_f2, 0))
            pen.addComponent(den, Transform(1, 0, 0, 1, x_d2, 0))
            info.update(components=[(num, 0, 0), (frac[0], x_f2, 0), (den, x_d2, 0)], pattern=comps)
            return self._finish(pen, adv, info)
        if "box" in spec:   # ☐ ☑ ☒ = □ 그대로 + (✓ | ×) 를 □ 속공간 안에 균등 축소·시각 중앙 배치 (분해)
            return self.make_ballot(cp, spec, info)
        parts = spec["parts"]
        if cp == 0x2252 or (len(parts) == 3 and parts[0] == "U+003D"):   # ≒ = equal + period×2 (분해)
            eq, per = P.name(cp_of(parts[0])), P.name(cp_of(parts[1]))
            xl, yb, xr, yt = P.bbox_name(eq)
            px0, py0, px1, py1 = P.bbox_name(per)
            cx_p, cy_p, r = (px0 + px1) / 2.0, (py0 + py1) / 2.0, (px1 - px0) / 2.0
            g = float(spec.get("gap", 40))
            pen = TTGlyphPen(P.glyphset)
            P.glyphset[eq].draw(TransformPen(pen, (1, 0, 0, 1, 0, 0)))
            P.glyphset[per].draw(TransformPen(pen, (1, 0, 0, 1, xr - r - cx_p, yt + g + r - cy_p)))
            P.glyphset[per].draw(TransformPen(pen, (1, 0, 0, 1, xl + r - cx_p, yb - g - r - cy_p)))
            info.update(parts=[eq, per, per], gap=g)
            return self._finish(pen, P.adv_name(eq), info)
        if isinstance(parts[0], list):   # ◈ = ◇ + ◆×0.5 (분해, ◇ 중심 기준)
            base_name = P.name(cp_of(parts[0][0]))
            bx0, by0, bx1, by1 = P.bbox_name(base_name)
            cx, cy = (bx0 + bx1) / 2.0, (by0 + by1) / 2.0
            pen = TTGlyphPen(P.glyphset)
            for pname, k in parts:
                nm = P.name(cp_of(pname))
                P.glyphset[nm].draw(TransformPen(pen, (k, 0, 0, k, cx - k * cx, cy - k * cy)))
            info.update(parts=[(P.name(cp_of(p[0])), p[1]) for p in parts], about=(cx, cy))
            return self._finish(pen, P.adv_name(base_name), info)
        raise ValueError(f"합성 규칙 해석 불가: U+{cp:04X} {spec}")

    def make_ballot(self, cp, spec, info):
        """체크박스 ☐ ☑ ☒ (1.001, AGENTS §8 2026-10-24).
        spec: {"box": "U+25A1", "mark": "U+2713" | "U+00D7" | 없음, "gap": 박스 획 두께 배수, "gap_min": 최소 여백(unit)}
        - 박스 = 같은 웨이트의 □ 외곽선을 변환 없이 그대로 → 크기·획 굵기·진행폭 = □.
        - 마크 = 같은 웨이트의 ✓ / × 를 **균등 축소**(아핀만 — 새 외곽선 없음)해, □ 속공간(안쪽 윤곽 bbox)에서
          사방 여백 g = max(gap × 박스 획 두께, gap_min) 을 두고 들어가는 최대 크기로, bbox 중심을 속공간 중심에 맞춘다.
        - 마크는 속공간 안에 있어 박스 윤곽과 겹치지 않는다. 점 수·윤곽 순서 = □ + 마크 원본 그대로라
          변수 폰트 9 인스턴스가 서로 호환된다(모두 같은 VF 부품 인스턴스에서 나옴)."""
        P = self.P
        box = P.name(cp_of(spec["box"]))
        inner = inner_contour_bbox(P.glyphset, box)
        stroke = inner[0] - P.bbox_name(box)[0]
        pen = TTGlyphPen(P.glyphset)
        P.glyphset[box].draw(pen)
        info.update(parts=[box], box_inner=[round(v, 1) for v in inner], box_stroke=round(stroke, 1))
        if spec.get("mark"):
            mark = P.name(cp_of(spec["mark"]))
            mx0, my0, mx1, my1 = P.bbox_name(mark)
            g = max(float(spec.get("gap", 0.5)) * stroke, float(spec.get("gap_min", 0)))
            k = min((inner[2] - inner[0] - 2 * g) / (mx1 - mx0), (inner[3] - inner[1] - 2 * g) / (my1 - my0))
            if k <= 0:
                raise ValueError(f"U+{cp:04X} 마크가 속공간에 들어가지 않음 (k={k:.3f})")
            icx, icy = (inner[0] + inner[2]) / 2.0, (inner[1] + inner[3]) / 2.0
            mcx, mcy = (mx0 + mx1) / 2.0, (my0 + my1) / 2.0
            P.glyphset[mark].draw(TransformPen(pen, (k, 0, 0, k, icx - k * mcx, icy - k * mcy)))
            info["parts"].append(mark)
            info.update(mark_scale=round(k, 4), gap=round(g, 1))
        return self._finish(pen, P.adv_name(box), info)

    def make(self, cp):
        """cp 하나 → (glyph, adv, lsb, info) 또는 None(규칙 없음/원본 없음)."""
        if cp in self.rules.composites:
            return self.make_composite(cp, self.rules.composites[cp])
        if cp in self.rules.mirror:
            return self.make_mirror(cp, self.rules.mirror[cp])
        if not self.N.has(cp):
            return None
        rule = self.rules.rule_for(cp)
        if rule is None:
            return None
        return self.make_noto(cp, rule)

    def refs_report(self):
        return {f"U+{cp:04X}": dict(P=pm, N=nm, s_h=round(pm["h"] / nm["h"], 4), s_w=round(pm["w"] / nm["w"], 4))
                for cp, (pm, nm) in sorted(self.refs.items())}


def glyph_name_for(cp, existing):
    base = f"uni{cp:04X}" if cp <= 0xFFFF else f"u{cp:05X}"
    name = base
    i = 0
    while name in existing:
        i += 1
        name = f"{base}.sup" if i == 1 else f"{base}.sup{i}"
    return name


def supplement_targets(base_cps, sets, rules):
    """빌드 대상 중 Pretendard 미보유 → (Noto 보유 ∪ 합성/미러 정의) 목록과 '어디에도 없음' 목록."""
    tgt = set()
    for n in config.SUPPLEMENT_SETS:
        tgt |= sets[n]
    missing = sorted(tgt - set(base_cps))
    noto = TTFont(config.NOTO_VF, lazy=True)
    noto_cps = set(noto.getBestCmap())
    noto.close()
    synth = set(rules.composites) | set(rules.mirror)
    doable = [c for c in missing if c in noto_cps or c in synth]
    neither = [c for c in missing if c not in noto_cps and c not in synth]
    latin = [c for c in doable if (c < 0x0250 or 0x1E00 <= c <= 0x1EFF) and c not in synth]   # 합성(DŽ 등)은 Pretendard 부품이라 제외 안 함
    if latin and rules.raw.get("policy", {}).get("latin-letters-from-noto") == "never":
        LOG.warning("라틴 문자를 Noto 에서 가져오지 않음(policy): %s", [f"U+{c:04X}" for c in latin])
        doable = [c for c in doable if c not in latin]
    # Noto 인스턴스에 필요한 것: 이식 글립 + 미러 원본 + 참조쌍(ref) 글립(P/N 양쪽 bbox 비교용)
    noto_needed = sorted(set(c for c in doable if c in noto_cps) | {cp_of(m["from"]) for m in rules.mirror.values()}
                         | (set(rules.ref_cps()) & noto_cps))
    return doable, neither, noto_needed


def missing_codepoints(base_cmap_cps, build_target):
    return sorted(set(build_target) - set(base_cmap_cps))


# ------------------------------------------------------------------ 중첩 컴포넌트 평탄화 (QA 티켓 2)
from fontTools.ttLib.tables._g_l_y_f import GlyphComponent  # noqa: E402


def _component_transform(c):
    if hasattr(c, "transform"):
        t = c.transform
        return Transform(t[0][0], t[0][1], t[1][0], t[1][1], c.x, c.y)
    return Transform(1, 0, 0, 1, c.x, c.y)


def expand_components(glyf, name, outer=None):
    """name 의 컴포넌트를 재귀 전개 → [(leaf_name, Transform, flags)] (outer∘inner: 안쪽 변환 먼저 적용)."""
    outer = outer or Transform()
    out = []
    for c in glyf[name].components:
        t = outer.transform(_component_transform(c))
        if glyf[c.glyphName].isComposite():
            out.extend(expand_components(glyf, c.glyphName, t))
        else:
            out.append((c.glyphName, t, c.flags))
    return out


def nested_composites(font):
    glyf = font["glyf"]
    return [n for n in font.getGlyphOrder()
            if glyf[n].isComposite() and any(glyf[c.glyphName].isComposite() for c in glyf[n].components)]


def bounds_of(glyf, name):
    coords, _, _ = glyf[name].getCoordinates(glyf)
    if not coords:
        return None
    xs = [x for x, _ in coords]
    ys = [y for _, y in coords]
    return (min(xs), min(ys), max(xs), max(ys))


def flatten_nested(font, names=None):
    """중첩 컴포지트를 한 단계(단순 글립만 참조)로 평탄화. 외곽선 불변 — 전개 전후 bbox 를 비교해 반환.
    반환: (평탄화한 글립명 목록, bbox 불일치 목록)"""
    glyf = font["glyf"]
    names = list(names) if names is not None else nested_composites(font)
    mismatched = []
    for n in names:
        before = bounds_of(glyf, n)
        leaves = expand_components(glyf, n)
        new = []
        for leaf, t, flags in leaves:
            comp = GlyphComponent()
            comp.glyphName = leaf
            comp.flags = (flags & 0x400) | 0x4     # ROUND_XY_TO_GRID (+UNSCALED_COMPONENT_OFFSET 유지)
            if (t.xx, t.xy, t.yx, t.yy) != (1, 0, 0, 1):
                comp.transform = [[t.xx, t.xy], [t.yx, t.yy]]
            comp.x, comp.y = otRound(t.dx), otRound(t.dy)
            new.append(comp)
        glyf[n].components = new
        after = bounds_of(glyf, n)
        if before != after:
            mismatched.append((n, before, after))
    return names, mismatched
