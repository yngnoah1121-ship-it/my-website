"""カード名の読み（カタカナ）を data.json の各カードに "y" として入れる。ひらがな検索用。
読みは2つの辞書（pykakasi と Sudachi）で自動生成するので完全ではない。両方の読みを「|」区切りで入れ、どちらかに合えば見つかる。
Usage: pip install pykakasi sudachipy sudachidict_core && python3 tools/yomi.py data.json"""
import json, re, sys
import pykakasi
from sudachipy import dictionary
K = pykakasi.kakasi()
T = dictionary.Dictionary(dict="core").create()
KANJI = re.compile(r"[㐀-鿿々〆ヶ]")
def word_reading(s): return "".join(x["kana"] for x in K.convert(s))
def sudachi_reading(s):
    # 漢字を含む語だけ読みにする（空白や英字を「キゴウ」「エスアール」などと読まないように）
    return "".join(m.reading_form() if KANJI.search(m.surface()) else m.surface() for m in T.tokenize(s))
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
n = 0
for c in d["cards"]:
    if not KANJI.search(c["name"]): c.pop("y", None); continue
    rs = list(dict.fromkeys([word_reading(c["name"]), sudachi_reading(c["name"])]))
    y = "|".join(rs)
    if c.get("y") != y: c["y"] = y; n += 1
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("readings updated", n, "cards with reading", sum(1 for c in d["cards"] if c.get("y")))
