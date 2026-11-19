"""カードの効果テキスト（text）を data.json から cardtext.json に移す。最初の表示を速くするため、
効果テキストはページを開いたあとに別で読み込む。カードを追加したあとに実行する。Usage: python3 tools/split_text.py data.json cardtext.json"""
import json, os, sys
dp, tp = sys.argv[1:3]
d = json.load(open(dp, encoding="utf-8"))
t = json.load(open(tp, encoding="utf-8")) if os.path.exists(tp) else {}
n = 0
for c in d["cards"]:
    if "text" in c:
        t[c["officialId"]] = c.pop("text"); n += 1
ids = {c["officialId"] for c in d["cards"]}
t = {k: v for k, v in t.items() if k in ids}
d["textFile"] = os.path.basename(tp)
json.dump(d, open(dp, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
json.dump(t, open(tp, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("moved", n, "texts", len(t))
