"""Write collected shop prices into data.json.  Usage: merge_prices.py DATA_JSON PRICES_JSON"""
import json, sys
data_path, prices_path = sys.argv[1], sys.argv[2]
d = json.load(open(data_path, encoding="utf-8"))
pr = json.load(open(prices_path, encoding="utf-8"))
stat = {}
for c in d["cards"]:
    c.setdefault("prices", {})
    pst = {}
    for shop in ("dragonstar", "pao"):
        r = pr.get(shop, {}).get(c["name"])
        if not r: continue
        if r.get("st") == "ok": c["prices"][shop] = r["p"]
        else:
            c["prices"].pop(shop, None)
            if r.get("st") in ("soldout", "none"): pst[shop] = r["st"]
        stat[(shop, r.get("st"))] = stat.get((shop, r.get("st")), 0) + 1
    if pst: c["pst"] = pst
    else: c.pop("pst", None)
d["priceAt"] = {k: v for k, v in pr.get("at", {}).items()}
d["sample"] = False
d["updatedAt"] = max(d["priceAt"].values()) if d["priceAt"] else d.get("updatedAt")
json.dump(d, open(data_path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(sorted(stat.items()), d["priceAt"])
