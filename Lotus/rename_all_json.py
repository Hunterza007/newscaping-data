import json
from pathlib import Path
import re

BASE = Path(r"D:\newscaping\Lotus")
OUT = BASE / "cleaned"
OUT.mkdir(exist_ok=True)

def map_key(key, value):
    k = key.lower()

    if "href" in k:
        return "url"

    if "src" in k and isinstance(value, str):
        v = value.lower()
        if "discount" in v:
            return "discount_image"
        return "image"

    if "typography" in k:
        return "name"

    if isinstance(value, str):
        if re.match(r"^\฿?\d+(\.\d+)?$", value.replace(",", "")):
            return "price"

    if "(2)" in k or "unit" in k:
        return "unit"

    return None

def clean(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            nk = map_key(k, v)
            if nk:
                out[nk] = clean(v)
        return out
    if isinstance(obj, list):
        return [clean(x) for x in obj]
    return obj

for f in BASE.glob("*.json"):
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        cleaned = clean(data)
        (OUT / f.name).write_text(
            json.dumps(cleaned, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print("✅", f.name)
    except Exception as e:
        print("❌", f.name, e)

print("🎉 DONE")
