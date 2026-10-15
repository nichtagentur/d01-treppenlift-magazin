"""Python-Port von tools/linkcheck.sh: GET mit Browser-UA. OK / PRUEFEN (401/403/405/429, Bot-Sperre) / TOT."""
import re, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"

def one(u, versuch=0):
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "de"})
        return u, "OK", urllib.request.urlopen(req, timeout=20).status
    except urllib.error.HTTPError as e:
        return u, ("PRUEFEN" if e.code in (401, 403, 405, 429, 999) else "TOT"), e.code
    except Exception as e:
        if versuch == 0: return one(u, 1)
        # DNS-Fehler = Domain existiert nicht = TOT; sonstige Verbindungsfehler (Geo-/Rechenzentrums-Sperre) = PRUEFEN
        dns = "Name or service not known" in str(e) or "nodename nor servname" in str(e) or "No address associated" in str(e)
        return u, ("TOT" if dns else "PRUEFEN"), type(e).__name__

def check_html(html):
    urls = sorted(set(re.findall(r'href="(https?://[^"]+)"', html)))
    with ThreadPoolExecutor(8) as ex: return list(ex.map(one, urls))

if __name__ == "__main__":
    for u, s, c in check_html(open(sys.argv[1], encoding="utf-8").read()): print(f"{s}\t{c}\t{u}")
