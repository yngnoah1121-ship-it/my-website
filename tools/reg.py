"""Parse official 殿堂 page into data.json 'reg'. Usage: reg.py REG_HTML DATA_JSON"""
import re, sys, html, json, unicodedata
s = open(sys.argv[1], encoding="utf-8", errors="replace").read()
t = re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S)
t = re.sub(r'<(h\d|li|tr|p|div)[^>]*>', '\n', t); t = html.unescape(re.sub(r'<[^>]+>', '', t))
L = [l.strip() for l in t.split('\n') if l.strip()]
def sect(start, end):
    a = L.index(start); b = L.index(end, a + 1); return L[a:b]
names = lambda ls: [m for l in ls for m in re.findall(r'[《≪](.+?)[》≫]', l)]
prem = names(sect("プレミアム殿堂入りカード", "殿堂入りカード"))
hall = names(sect("殿堂入りカード", "殿堂解除カード"))
combo_l = sect("プレミアム殿堂コンビカード", "プレミアム殿堂超次元コンビカード")
combo = [names([l]) for l in combo_l if "＋" in l]
at = re.search(r'(\d{4})/(\d+)/(\d+)より適用', t)
def norm(x): return re.sub(r"\s+", "", unicodedata.normalize("NFKC", x).replace("’", "'").replace("“", '"').replace("”", '"'))
d = json.load(open(sys.argv[2], encoding="utf-8"))
idx = {}
for c in d["cards"]:
    idx.setdefault(norm(c["name"]), c["name"])
    idx.setdefault(norm(c["name"].split(" / ")[0]), c["name"])
def res(n): return idx.get(norm(n)) or idx.get(norm(n.split(" / ")[0]))
reg = {"premium": [], "hall": [], "combo": [], "at": f"{at.group(1)}-{int(at.group(2)):02d}-{int(at.group(3)):02d}" if at else None,
       "allPremium": sorted(set(prem)), "allHall": sorted(set(hall))}
for n in set(prem):
    if res(n): reg["premium"].append(res(n))
for n in set(hall):
    if res(n) and res(n) not in reg["premium"]: reg["hall"].append(res(n))
for pair in combo:
    reg["combo"].append([res(x) or x for x in pair])
d["reg"] = reg
json.dump(d, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("premium", len(set(prem)), "in data", len(reg["premium"]), reg["premium"])
print("hall", len(set(hall)), "in data", len(reg["hall"]), reg["hall"])
print("combo", reg["combo"], "at", reg["at"])
