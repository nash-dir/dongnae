import time
import random
import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# ==========================================
# [Setup] Environment and Paths
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

VWORLD_API_KEY = os.getenv("API_KEY")
TARGET_COUNT = 10000  # Target sample count

RESULT_DIR = os.path.join(BASE_DIR, 'result')

# Load Dongnae Engine
try:
    from dongnae_kr import dongnaekr
    print("Initializing engine...")
    t_init_start = time.perf_counter()
    engine = dongnaekr()
    t_init_end = time.perf_counter()
    init_time_ms = (t_init_end - t_init_start) * 1000
    print(f"dongnae-KR ready (Init: {init_time_ms:.2f}ms)")
except ImportError:
    print("dongnae-kr package is not installed.")
    exit()

# Approximate boundary of South Korea
LAT_MIN, LAT_MAX = 34.0, 38.5
LON_MIN, LON_MAX = 126.0, 130.0

def get_random_coordinate():
    lat = random.uniform(LAT_MIN, LAT_MAX)
    lon = random.uniform(LON_MIN, LON_MAX)
    return lat, lon

def query_vworld_api(lat, lon):
    """
    Calls VWorld API to get the address and response latency (ms).
    """
    if not VWORLD_API_KEY:
        # Simulation mode if no API key
        fake_latency = random.uniform(0.1, 0.5)
        time.sleep(fake_latency)
        return True, "Test Address City Dongnae-Test", fake_latency * 1000

    url = "http://api.vworld.kr/req/address?"
    params = {
        "service": "address",
        "request": "getaddress",
        "version": "2.0",
        "crs": "epsg:4326",
        "point": f"{lon},{lat}",
        "format": "json",
        "type": "both",
        "zipcode": "false",
        "simple": "false",
        "key": VWORLD_API_KEY
    }
    
    t_start = time.perf_counter()
    try:
        resp = requests.get(url, params=params, timeout=2)
        t_end = time.perf_counter()
        duration_ms = (t_end - t_start) * 1000
        
        data = resp.json()
        if data['response']['status'] == 'OK':
            return True, data['response']['result'][0]['text'], duration_ms
    except Exception:
        pass
        
    return False, None, 0.0

def run_benchmark():
    print(f"\nStarting benchmark (Target: {TARGET_COUNT})...")
    
    results = []
    collected = 0
    
    # 1. Data Collection Loop
    while collected < TARGET_COUNT:
        lat, lon = get_random_coordinate()
        
        # [API] Call Ground Truth
        is_valid, api_address, api_time_ms = query_vworld_api(lat, lon)
        if not is_valid:
            continue
            
        collected += 1
        if collected % 100 == 0:
            print(f"   - Progress: {collected}/{TARGET_COUNT}")

        # [Dongnae] Call Engine
        t_start = time.perf_counter()
        candidates = engine.nearest(lat, lon, k=3)
        t_end = time.perf_counter()
        dn_time_ms = (t_end - t_start) * 1000

        # [Correction] Handle 'Sejong' special case
        # If dnname contains '세종특별자치시 세종시', replace with '세종특별자치시'
        for cand in candidates:
            if '세종특별자치시 세종시' in cand['dnname']:
                cand['dnname'] = cand['dnname'].replace('세종특별자치시 세종시', '세종특별자치시')

        # Result Analysis
        n1 = candidates[0]['dnname'] if len(candidates) > 0 else None
        n2 = candidates[1]['dnname'] if len(candidates) > 1 else None
        n3 = candidates[2]['dnname'] if len(candidates) > 2 else None

        # --- [Evaluation Logic: Top-1 & Top-3] ---
        is_top1 = False
        is_top3 = False

        if n1 and n1 in api_address:
            is_top1 = True
            is_top3 = True
        elif (n2 and n2 in api_address) or (n3 and n3 in api_address):
            is_top3 = True
        
        # Save Data
        row = {
            'latitude': lat, 'longitude': lon,
            'api_address': api_address, 'api_time_ms': api_time_ms,
            'dongnae_time_ms': dn_time_ms,
            'nearest_1': n1, 'nearest_2': n2, 'nearest_3': n3,
            'top1_match': is_top1, 'top3_match': is_top3
        }
        results.append(row)

    # 2. Statistics Calculation
    df = pd.DataFrame(results)
    
    avg_api_time = df['api_time_ms'].mean()
    avg_dn_time = df['dongnae_time_ms'].mean()
    
    # Accuracy Calculation
    top1_count = len(df[df['top1_match'] == True])
    top3_count = len(df[df['top3_match'] == True])
    
    top1_accuracy = (top1_count / TARGET_COUNT) * 100
    top3_accuracy = (top3_count / TARGET_COUNT) * 100
    miss_rate = 100.0 - top3_accuracy
    
    # Comparison Metrics
    speed_multiplier = avg_api_time / avg_dn_time if avg_dn_time > 0 else 0

    # 3. Generate Report (TXT)
    timestamp = datetime.now().strftime('%y%m%d_%H%M')
    file_base_name = f"benchmark_strict_{timestamp}"
    
    # Save CSV
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)
    csv_path = os.path.join(RESULT_DIR, f"{file_base_name}.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    # Write TXT Report
    report_text = f"""
==================================================
[Benchmark Report]
==================================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Samples: {TARGET_COUNT}

--------------------------------------------------
1. Speed (Average Latency)
   - API (Network)   : {avg_api_time:.2f} ms
   - Local (Dongnae) : {avg_dn_time:.4f} ms

2. Accuracy (Performance)
   - Top-1 Accuracy : {top1_accuracy:.2f}%
   - Top-3 Accuracy : {top3_accuracy:.2f}%
   - Miss Rate      : {miss_rate:.2f}%

--------------------------------------------------
[Conclusion]
dongnae-kr is approximately {speed_multiplier:.1f}x faster than the external API.
Top-3 accuracy stands at {top3_accuracy:.2f}%.
==================================================
    """.strip()

    # Save TXT File
    txt_path = os.path.join(RESULT_DIR, f"{file_base_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    # 4. Print Result
    print("\n" + report_text)
    print(f"\nReport files generated:")
    print(f"   - {csv_path}")
    print(f"   - {txt_path}")

if __name__ == "__main__":
    run_benchmark()