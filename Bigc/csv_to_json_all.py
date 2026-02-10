import csv
import json
from pathlib import Path
import re

INPUT_DIR = Path(r"D:\newscaping\Bigc")
OUTPUT_DIR = INPUT_DIR / "json_out"
OUTPUT_DIR.mkdir(exist_ok=True)

# แปลง "฿79.00" / "79.00" / "79" -> 79.0
def parse_price(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    s = s.replace("฿", "").replace(",", "").strip()
    try:
        return float(s)
    except:
        return None

def normalize_row(row: dict):
    # กัน key ว่าง + trim
    row = {(k or "").strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}

    # === map ให้เหมือน Lotus ===
    name = row.get("data") or row.get("name") or row.get("product") or row.get("title")
    url = row.get("web_scraper_start_url") or row.get("url") or row.get("link")
    image = row.get("image") or row.get("img") or row.get("image_url")

    # BigC: price = ราคาขาย, price2 = ราคาเต็ม (จากรูปคุณ)
    price = parse_price(row.get("price"))
    original_price = parse_price(row.get("price2")) or parse_price(row.get("original_price"))

    # ถ้าราคาเต็มน้อยกว่าราคาขาย ให้สลับ (กันข้อมูลกลับด้าน)
    if price is not None and original_price is not None and original_price < price:
        price, original_price = original_price, price

    out = {}

    if url:
        out["url"] = url
    if image:
        out["image"] = image
    if name:
        out["name"] = name

    # ใส่ราคา (ถ้ามี)
    if price is not None:
        # ถ้าอยากเป็น int เมื่อไม่มีทศนิยม
        out["price"] = int(price) if price.is_integer() else price
    if original_price is not None:
        out["original_price"] = int(original_price) if original_price.is_integer() else original_price

    return out

def read_csv_rows(csv_path: Path):
    # รองรับ UTF-8 BOM / UTF-8 / ไทย cp874
    for enc in ("utf-8-sig", "utf-8", "cp874"):
        try:
            with csv_path.open("r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                return [normalize_row(r) for r in reader], enc
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("decode failed", b"", 0, 1, "Cannot decode")

def main():
    csv_files = list(INPUT_DIR.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files in BigC")

    for csv_file in csv_files:
        try:
            rows, used_enc = read_csv_rows(csv_file)

            # ลบแถวที่ว่าง (ไม่มี name และไม่มี price และไม่มี url)
            rows = [r for r in rows if r.get("name") or r.get("price") or r.get("url")]

            out_path = OUTPUT_DIR / f"{csv_file.stem}.json"
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)

            print(f"✅ {csv_file.name} ({used_enc}) -> json_out/{out_path.name} rows={len(rows)}")
        except Exception as e:
            print(f"❌ {csv_file.name} -> {e}")

    print("🎉 DONE")

if __name__ == "__main__":
    main()
