"""OpenRouter-Client fuer alle KI-Schritte. Modell aus ENV MODEL (Default deepseek/deepseek-v4.1-flash)."""
import json, os, re, time, urllib.request, urllib.error
MODEL = os.environ.get("MODEL", "deepseek/deepseek-v4.1-flash")
COST = {"usd": 0.0, "calls": 0}

def _post(body, key):
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "X-Title": "d01-treppenlift-magazin"})
    return json.load(urllib.request.urlopen(req, timeout=900))

def chat(prompt, model=None, web=False, as_json=False):
    body = {"model": model or MODEL, "messages": [{"role": "user", "content": prompt}], "usage": {"include": True}}
    if web: body["plugins"] = [{"id": "web", "max_results": 8}]
    if as_json: body["response_format"] = {"type": "json_object"}
    keys = [k for k in (os.environ.get("OPENROUTER_API_KEY"), os.environ.get("OPENROUTER_BACKUP_API_KEY")) if k]
    for i in range(4):
        try:
            r = _post(body, keys[0]); break
        except urllib.error.HTTPError as e:
            if e.code in (401, 402) and len(keys) > 1: keys.pop(0); continue
            if i == 3: raise
        except Exception:
            if i == 3: raise
        time.sleep(5 * (i + 1))
    COST["usd"] += (r.get("usage") or {}).get("cost") or 0; COST["calls"] += 1
    txt = r["choices"][0]["message"]["content"] or ""
    return parse_json(txt) if as_json else strip_fence(txt)

def strip_fence(t):
    t = t.strip()
    t = re.sub(r"^```[a-zA-Z]*\n", "", t); t = re.sub(r"\n```$", "", t)
    return t.strip()

def parse_json(t):
    t = strip_fence(t)
    return json.loads(t[t.find("{"): t.rfind("}") + 1])
