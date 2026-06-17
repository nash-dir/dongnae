import csv
import json
import os

INPUT_FILENAME = "dongnaeKR_251130.csv"
OUTPUT_FILENAME = "dongnae_cols.json"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, '..', 'data', INPUT_FILENAME)
OUTPUT_PATH = os.path.join(BASE_DIR, '..', 'js-data-kr', 'src', OUTPUT_FILENAME)

def convert_csv_to_column_oriented():
    print(f"🔄 Reading CSV: {INPUT_PATH} ...")
    
    encodings = ['utf-8-sig', 'cp949', 'utf-8']
    cols = None

    # Build into a fresh dict per attempt and only commit on success, so a
    # mid-file decode/parse failure can't leave half-appended rows that the next
    # encoding attempt would then duplicate. Catch the same errors as the engine
    # loader (decode / missing column / bad number) for consistent fallback.
    for enc in encodings:
        try:
            temp = {"ids": [], "names": [], "lats": [], "lons": [], "rads": []}
            with open(INPUT_PATH, 'r', encoding=enc) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    temp["ids"].append(row['dnid'])
                    temp["names"].append(row['dnname'])
                    # Coordinates are quantized to 4 decimals (~11 m). This is a
                    # deliberate size/gzip optimization; the engine targets
                    # neighbourhood-level accuracy where ~11m is well within
                    # tolerance. (Note: the Python core ships full-precision CSV,
                    # so JS results can differ from Python by up to this much.)
                    temp["lats"].append(round(float(row['dnlatitude']), 4))
                    temp["lons"].append(round(float(row['dnlongitude']), 4))
                    temp["rads"].append(float(row['dnradius']))
            cols = temp
            break
        except (UnicodeDecodeError, KeyError, ValueError):
            continue

    if cols is None:
        print(f"❌ Failed to load CSV (tried {encodings}).")
        return

    print(f"💾 Writing Column-oriented JSON to: {OUTPUT_PATH} ...")
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        # separators=(',', ':')로 공백 제거
        json.dump(cols, f, ensure_ascii=False, separators=(',', ':'))

    # 결과 리포트
    csv_size = os.path.getsize(INPUT_PATH) / 1024
    json_size = os.path.getsize(OUTPUT_PATH) / 1024
    
    print("-" * 50)
    print(f"📊 Total Records: {len(cols['ids'])}")
    print(f"📉 CSV Size: {csv_size:.1f}KB")
    print(f"📉 JSON Size: {json_size:.1f}KB (구조 변경으로 약간 줄거나 비슷할 수 있음)")
    print(f"🚀 [핵심] 이 파일은 Gzip 압축 시 효율이 2~3배 더 좋습니다.")
    print("-" * 50)

if __name__ == "__main__":
    convert_csv_to_column_oriented()