#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
언어별 필수 문자가 charset 파일(required/recommended)에 들어 있는지 검증한다.
추측 대신 실제 코드포인트 집합 연산으로 확인하고, 각 언어의 문자가 어느 유니코드 블록에
속하는지(Latin-1 Supplement / Latin Extended-A / 그 밖)와 어느 charset 파일에 있는지 표로 낸다.

실행: PYTHONUTF8=1 python charset/scripts/lang_check.py [--md]
  --md : README 에 붙일 Markdown 표 출력

언어 알파벳 목록은 각 언어 정서법의 표준 문자(기본 라틴 제외, 대소문자 포함)를 적은 것이다.
"""
import argparse
import os
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from count import parse_file, CHARSET_DIR  # noqa: E402

# 기본 ASCII 를 제외한, 각 언어에서 표준적으로 쓰이는 문자(대소문자·구두점). "선택"은 정서법상 선택/드묾.
LANGS = [
    # (언어, 필수 문자열, 선택 문자열)
    ("스페인어 es",   "áéíóúüñÁÉÍÓÚÜÑ¿¡ªº€«»", ""),
    ("포르투갈어 pt", "áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ€", "üÜ"),
    ("프랑스어 fr",   "àâæçéèêëîïôœùûüÿÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ«»€", "‹›"),
    ("독일어 de",     "äöüßÄÖÜ„“‚‘€", "ẞ"),
    ("이탈리아어 it", "àèéìíîòóùúÀÈÉÌÍÎÒÓÙÚ€", ""),
    ("네덜란드어 nl", "éëïóöüèêáàÉËÏÓÖÜÈÊÁÀ€", "ĳĲ"),
    ("폴란드어 pl",   "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ„”", ""),
    ("체코어 cs",     "áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ„“", ""),
    ("슬로바키아어 sk", "áäčďéíĺľňóôŕšťúýžÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽ", ""),
    ("헝가리어 hu",   "áéíóöőúüűÁÉÍÓÖŐÚÜŰ„”", ""),
    ("터키어 tr",     "çğıİöşüÇĞÖŞÜ", ""),
    ("크로아티아어 hr", "čćđšžČĆĐŠŽ", "ǄǅǆǇǈǉǊǋǌ"),
    ("슬로베니아어 sl", "čšžČŠŽ", ""),
    ("루마니아어 ro", "ăâîșțĂÂÎȘȚ", "şţŞŢ"),
    ("리투아니아어 lt", "ąčęėįšųūžĄČĘĖĮŠŲŪŽ", ""),
    ("라트비아어 lv", "āčēģīķļņšūžĀČĒĢĪĶĻŅŠŪŽ", ""),
    ("에스토니아어 et", "äöüõšžÄÖÜÕŠŽ", ""),
    ("핀란드어 fi",   "äöåÄÖÅ", "šžŠŽ"),
    ("스웨덴어 sv",   "åäöÅÄÖ", ""),
    ("덴마크어/노르웨이어 da/no", "æøåÆØÅ", ""),
    ("아이슬란드어 is", "áðéíóúýþæöÁÐÉÍÓÚÝÞÆÖ", ""),
    ("카탈루냐어 ca", "àéèíïóòúüçÀÉÈÍÏÓÒÚÜÇ·", "ŀĿ"),
    ("갈리시아어 gl", "áéíóúüñÁÉÍÓÚÜÑ", ""),
    ("바스크어 eu",   "ñÑ", ""),
    ("몰타어 mt",     "ċġħżĊĠĦŻ", ""),
    ("웨일스어 cy",   "âêîôûŵŷäëïöüÿÂÊÎÔÛŴŶÄËÏÖÜŸ", "àèìòùÀÈÌÒÙ"),
    ("아일랜드어 ga", "áéíóúÁÉÍÓÚ", ""),
    ("에스페란토 eo", "ĉĝĥĵŝŭĈĜĤĴŜŬ", ""),
    ("베트남어 vi(범위 밖)", "ăâđêôơưĂÂĐÊÔƠƯàảãáạằẳẵắặầẩẫấậèẻẽéẹềểễếệìỉĩíịòỏõóọồổỗốộờởỡớợùủũúụừửữứựỳỷỹýỵ", ""),
]


def block_of(cp):
    if cp < 0x80:
        return "ASCII"
    if cp <= 0xFF:
        return "Latin-1"
    if cp <= 0x17F:
        return "Ext-A"
    if cp <= 0x24F:
        return "Ext-B"
    if 0x1E00 <= cp <= 0x1EFF:
        return "Ext-Add"
    if 0x2000 <= cp <= 0x206F:
        return "GenPunct"
    if 0x20A0 <= cp <= 0x20CF:
        return "Currency"
    if 0x01C4 <= cp <= 0x01CC:
        return "Ext-B"
    return "Other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true")
    args = ap.parse_args()

    req = parse_file(os.path.join(CHARSET_DIR, "required.txt"))["cps"]
    rec = parse_file(os.path.join(CHARSET_DIR, "recommended.txt"))["cps"]

    rows = []
    for lang, must, opt in LANGS:
        must_cps = sorted({ord(c) for c in must})
        opt_cps = sorted({ord(c) for c in opt})
        miss_req = [c for c in must_cps if c not in req]
        miss_all = [c for c in must_cps if c not in req and c not in rec]
        opt_where = []
        for c in opt_cps:
            w = "required" if c in req else ("recommended" if c in rec else "없음")
            opt_where.append(f"{chr(c)}(U+{c:04X},{w})")
        blocks = sorted({block_of(c) for c in must_cps})
        if not miss_req:
            verdict = "required 로 전부 커버"
        elif not miss_all:
            verdict = "recommended 로 커버: " + " ".join(f"{chr(c)}(U+{c:04X})" for c in miss_req)
        else:
            verdict = "범위 밖: " + " ".join(f"{chr(c)}(U+{c:04X})" for c in miss_all)
        rows.append((lang, len(must_cps), "+".join(blocks), verdict, " ".join(opt_where) or "—"))

    if args.md:
        print("| 언어 | 필수 문자 수 | 블록 | 판정 | 선택 문자(위치) |")
        print("|---|---|---|---|---|")
        for r in rows:
            print("| " + " | ".join(str(x) for x in r) + " |")
    else:
        for r in rows:
            print(f"{r[0]:26s} n={r[1]:<3d} {r[2]:22s} {r[3]}")
            if r[4] != "—":
                print(f"{'':26s} 선택: {r[4]}")


if __name__ == "__main__":
    main()
