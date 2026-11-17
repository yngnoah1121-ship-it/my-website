"""Write collected shop prices into data.json.  Usage: merge_prices.py DATA_JSON PRICES_JSON"""
import json, sys
data_path, prices_path = sys.argv[1], sys.argv[2]
# 3つ目の引数で反映するショップを指定（例: "pao"）。取得に失敗したショップの価格は前のまま残す
SHOPS = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else ["dragonstar", "pao"]
d = json.load(open(data_path, encoding="utf-8"))
pr = json.load(open(prices_path, encoding="utf-8"))
stat = {}
for c in d["cards"]:
    c.setdefault("prices", {})
    pst = {}
    for shop in SHOPS:
        r = pr.get(shop, {}).get(c["name"])
        if not r: continue
        if r.get("st") == "ok": c["prices"][shop] = r["p"]; (c.get("pst") or {}).pop(shop, None)
        elif r.get("st") in ("soldout", "none"):
            c["prices"].pop(shop, None); pst[shop] = r["st"]
        else: continue  # 取得エラーは前の値を残す
        stat[(shop, r.get("st"))] = stat.get((shop, r.get("st")), 0) + 1
        if r.get("st") in ("ok", "soldout", "none"): c["pAt"] = max(c.get("pAt", ""), (pr.get("at", {}).get(shop) or pr.get("started", ""))[:10])
    keep = {k: v for k, v in (c.get("pst") or {}).items() if k not in pst and k not in c["prices"]}
    if pst or keep: c["pst"] = {**keep, **pst}
    else: c.pop("pst", None)
d["priceAt"] = {**d.get("priceAt", {}), **{k: v for k, v in pr.get("at", {}).items() if k in SHOPS}}
d["sample"] = False
d["updatedAt"] = max(d["priceAt"].values()) if d["priceAt"] else d.get("updatedAt")
json.dump(d, open(data_path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(sorted(stat.items()), d["priceAt"])
