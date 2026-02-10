import json
from pathlib import Path
import re

INPUT_DIR = Path(r"D:\newscaping\MAKRO")
OUTPUT_DIR = INPUT_DIR / "cleaned"
OUTPUT_DIR.mkdir(exist_ok=True)

def parse_price(v):
    if not v:
        return None
    s = str(v).replace("฿", "").replace(",", "").strip()
    try:
        return float(s)
    except:
        return None

def map_product(obj):
    out = {}

    for k, v in obj.items():
        kl = k.lower()
        val = str(v)

        # url
        if "href" in kl:
            out["url"] = v

        # image
        elif "src" in kl:
            out["image"] = v

        # name
        elif "css-" in kl:
            out["name"] = v

        # discount %
        elif "%" in val:
            out["discount"] = v

        # unit / shipping info
        elif "วัน" in val:
            out["unit"] = v

        # price numbers
        elif re.search(r"\d", val):
            price = parse_price(val)
            if price:
                if "price" in out:
                    out["original_price"] = price
                else:
                    out["price"] = price

    return out

def clean(data):
    if isinstance(data, list):
        return [map_product(x) for x in data]
    elif isinstance(data, dict):
        return map_product(data)
    return data

def main():
    # 🔥 อ่าน JSON ทุกโฟลเดอร์ย่อย
    files = list(INPUT_DIR.rglob("*.json"))
    print(f"Found {len(files)} JSON files")

    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            cleaned = clean(data)

            # เอาชื่อหมวดมาเป็นชื่อไฟล์
            category = f.parent.name
            out_name = f"{category}_{f.name}"
            out = OUTPUT_DIR / out_name

            out.write_text(
                json.dumps(cleaned, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            print("✅", out_name)
        except Exception as e:
            print("❌", f.name, e)

    print("🎉 DONE")

if __name__ == "__main__":
    main()
