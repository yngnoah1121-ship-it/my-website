"""Collect cheapest in-stock prices from Dragon Star and PAO for every card.
Usage: prices.py DATA_JSON OUT_JSON [limit]
Resumable: entries already in OUT_JSON are kept. One request at a time per shop, with a pause."""
import json, sys, re, time, html, unicodedata, urllib.request, urllib.parse, os, threading
from datetime import datetime, timezone, timedelta
DATA, OUT = sys.argv[1], sys.argv[2]
LIMIT = int(sys.argv[3]) if len(sys.argv) > 3 else None
UA = {"User-Agent": "Mozilla/5.0 (fan price comparison; 1 req/2s)"}
JST = timezone(timedelta(hours=9))
cards = json.load(open(DATA, encoding="utf-8"))["cards"][:LIMIT]
state = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"dragonstar": {}, "pao": {}, "at": {}}
lock = threading.Lock()

def norm(s):
    s = unicodedata.normalize("NFKC", html.unescape(s))
    s = s.replace("／", "/").replace("’", "'").replace("‘", "'").replace("＇", "'")
    return re.sub(r"\s+", "", s)

def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read()
        except Exception as e:
            last = e; time.sleep(5)
    raise RuntimeError(str(last))

def targets(card):
    full = norm(card["name"]); first = norm(card["name"].split(" / ")[0])
    return {full, first, full.replace("/", "")}

def ds_parse(page, card):
    s = page.decode("utf-8", "replace")
    T, items = targets(card), []
    for m in re.finditer(r'<li class="change_hight">\s*<a href="/duelmasters/product\?pid=(\d+)">\s*(.*?)\s*</a>.*?</li>\s*<li>([\d,]+)円</li>', s, re.S):
        pid, name, price = m.group(1), m.group(2), int(m.group(3).replace(",", ""))
        base = norm(re.sub(r"\([^()]*\)\s*$", "", name))
        if base not in T: continue
        head = s[max(0, m.start() - 1500):m.start()]
        soldout = f'product?pid={pid}" class="condition soldout"' in head
        items.append((price, soldout))
    return items

def pao_parse(page, card):
    s = page.decode("utf-8", "replace")
    T, items = targets(card), []
    for blk in re.findall(r'<li class="itemList__unit">(.*?)</li>\s*(?=<li class="itemList__unit">|</ul>)', s, re.S):
        nm = re.search(r'<p class="itemName">(.*?)</p>', blk, re.S)
        if not nm: continue
        name = html.unescape(re.sub(r"<[^>]+>", "", nm.group(1))).strip()
        base = re.sub(r"^(?:[★☆【〔\[].*?[★☆】〕\]]\s*)+", "", name)
        base = norm(re.split(r"\s\[", base)[0])
        if base not in T: continue
        sale = re.search(r'itemPrice--sale">\s*([\d,]+)円', blk)
        reg = re.search(r'itemPrice[^"]*">\s*(?:通常価格：)?([\d,]+)円', blk)
        p = sale or reg
        if not p: continue
        soldout = bool(re.search(r"SOLD\s*OUT|品切れ|在庫切れ|soldout", blk, re.I)) or "カートに入れる" not in blk
        items.append((int(p.group(1).replace(",", "")), soldout))
    return items

def short_kw(c):
    first = c["name"].split(" / ")[0]
    k = re.split(r"[’'＇「」＜＞<>()（）]", first)[0].strip()
    k = re.sub(r"[A-Za-z]+$", "", k).strip()
    return k if k and k != first and len(k) >= 3 else None
def eucq(k):
    return urllib.parse.quote(k.encode("euc_jp", errors="ignore"))
SHOPS = {
    "dragonstar": (lambda c, k=None: "https://dorasuta.jp/duelmasters/product-list?kw=" + urllib.parse.quote(k or c["name"].split(" / ")[0]), ds_parse),
    "pao": (lambda c, k=None: "https://pao-onlineshop.com/view/search?search_keyword=" + (eucq(k) if k else c.get("qe", "")), pao_parse),
}

def summarize(items):
    if not items: return {"st": "none"}
    instock = [p for p, so in items if not so]
    if instock: return {"p": min(instock), "n": len(items), "st": "ok"}
    return {"st": "soldout", "n": len(items), "last": min(p for p, so in items)}

def worker(shop):
    url_of, parse = SHOPS[shop]
    done = 0
    for c in cards:
        if c["name"] in state[shop]: continue
        try:
            items = parse(get(url_of(c)), c)
            if not items and short_kw(c):
                time.sleep(2); items = parse(get(url_of(c, short_kw(c))), c)
            res = summarize(items)
        except Exception as e:
            res = {"st": "error"}; print(shop, "fail", c["name"], e, file=sys.stderr, flush=True)
        with lock:
            state[shop][c["name"]] = res
            done += 1
            if done % 25 == 0:
                json.dump(state, open(OUT + ".tmp", "w", encoding="utf-8"), ensure_ascii=False); os.replace(OUT + ".tmp", OUT)
                print(shop, len(state[shop]), "/", len(cards), file=sys.stderr, flush=True)
        time.sleep(2)
    with lock:
        state["at"][shop] = datetime.now(JST).strftime("%Y-%m-%d %H:%M")

ths = [threading.Thread(target=worker, args=(s,)) for s in SHOPS]
[t.start() for t in ths]; [t.join() for t in ths]
json.dump(state, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
for shop in SHOPS:
    v = state[shop].values()
    print(shop, "ok", sum(1 for x in v if x["st"] == "ok"), "soldout", sum(1 for x in v if x["st"] == "soldout"),
          "none", sum(1 for x in v if x["st"] == "none"), "error", sum(1 for x in v if x["st"] == "error"), file=sys.stderr, flush=True)
print("ALL DONE", file=sys.stderr, flush=True)
