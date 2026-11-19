"""カード一覧用の小さい画像（1枚ずつ）を作る：th/<officialId>.webp（160×223）。
まとめ画像（sprites/）から切り出すので、カードを追加したあとに実行する。Usage: python3 tools/thumbs.py data.json"""
import json, os, re, sys
from PIL import Image
p = sys.argv[1]; d = json.load(open(p, encoding="utf-8"))
S = d["sprites"]; os.makedirs("th", exist_ok=True)
sheets, n = {}, 0
for c in d["cards"]:
    sp, cid = c.get("sp"), c.get("officialId")
    if not sp or not cid or not re.fullmatch(r"[\w-]+", cid): continue
    out = f"th/{cid}.webp"
    if os.path.exists(out): continue
    im = sheets.get(sp[0]) or sheets.setdefault(sp[0], Image.open(f"sprites/{sp[0]}.webp").convert("RGB"))
    W, H = im.size[0] // S["cols"], im.size[1] // S["rows"]
    x, y = (sp[1] % S["cols"]) * W, (sp[1] // S["cols"]) * H
    im.crop((x, y, x + W, y + H)).resize((160, 223), Image.LANCZOS).save(out, "WEBP", quality=65, method=6); n += 1
    if len(sheets) > 40: sheets.clear()
d["thumbs"] = True
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("thumbnails made", n, "total", len(os.listdir("th")))
