# **dongnae v.0.2.0** 

[![PyPI version](https://badge.fury.io/py/dongnae.svg)](https://badge.fury.io/py/dongnae)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/dongnae.svg)](https://pypi.org/project/dongnae/)

## **Lightest Possible Spatial Engine**

* **dongnae** is a dependency-free, pure Python library designed for **high-performance reverse geocoding, radius search, spatial lookup, and Area-of-Effect lookup**. It operates from self-contained native script & pre-rendered CSV dataframe. Designed for high-performance microservices and client-side applications.

  * **Zero backend**
  * **Zero auth**
  * **Zero dependencies**

* It is optimized for **local/regional datasets** (e.g., Neighborhoods in a specific country) using latitude-based auto-calibration instead of expensive spherical trigonometry for every calculation.

## **Key Features**

* **Quasi-Geocoding to `Dongnae`**

  * Sometimes you just want to lookup `roughly which neighborhood` you are in.
  
  * Instead of precise street-level addresses, it maps coordinates to the nearest "Dongnae" (Neighborhood/District node), which is not quite precise but still good enough for some applications.

  * Key concept of this engine is **"dongnae"** - an object that has ID(dnid), Name(dnname), 2D coordinates(dnlatitude, dnlongitude), and radius(dnradius).

  * Dictionary of dongnaes should be loaded from CSV / JS prior to using this engine.

  * Recommended for lightweight, suggestion-based frontends; e.g. Web / PWAs.


* **Boundary Distance calculation**

  * Calculates the ballpark 'Boundary Distance' from a specific coordinate to a target Dongnae.

  * Great for quickly looking up geopoints within Area-of-Effect from certain `dongnae` in kilometer scale.

  * Recommended for microsystem backend, AWS Lambda, embedded, push service, etc.


* **Zero Dependencies** 

  * **Pure Python**: Runs on pure Python & essential libraries (csv, math). No pip install required for dependencies. 
  
  * **Ultra lightweight** : Does not require heavy GIS libraries (pandas, geopandas, or shapely)


* **Lightning Fast**

  * **Auto-Calibration**: Calculates Haversine coefficients once upon loading, avoiding repeated trigonometric operations (cos, sin) during queries.  

  * **Spatial Indexing**: Uses dynamic Bounding Box (BBox) filtering to minimize search space.  

  * $O(1)$ **ID Lookup**: Instant retrieval by ID using an internal Hash Map.  

  * In internal benchmark with ROK Regional Geometry data, `dongnae` guessing was ~20x faster than `VWorld API response` in the cost of ~20% lesser accuracy.


* **Self-contained**

  * **Zero backend** : No networking, GIS server required

  * **Zero dependencies** : Runs on Python standard libraries (csv, math), 

  * **Zero authentication** : No authentication, API key required

  * **Zero vulnerability** : No external connections means no attack surface. (You can't hack what doesn't quack.)


* **Business-Ready Logic**:  
  * **Boundary Distance**: Calculates distance from the *edge* of a neighborhood, not just the center.  

  * **Soft Geofencing**: Determines if a point is "roughly" within neighborhood with an adjustable threshold.  

  * **Text Search**: Built-in keyword search functionality.

  * **Privacy by Design** : No Personal Information including Geolocation sent outside.
 

## **Getting Started**

### **1\. Prerequisite: Data Format**

You need a CSV file containing your local spatial nodes. The file **must** have the following headers:

| Column | Type | Description |
| :---- | :---- | :---- |
| dnid | String | Unique Identifier (e.g., Zipcode, Legal Code) |
| dnname | String | Name of the area (e.g., "Gangnam-gu") |
| dnlatitude | Float | Y Coordinate |
| dnlongitude | Float | X Coordinate |
| dnradius | Float | Effective radius of the area (km) |


### **2\. Installation**

  * `dongnae-kr` package containing ready-made Korean Regional data CSV available in `pip`

``` bash
pip install dongnae
```

### **3\. Initiate Dongnae Engine & Load up Dongnae Dictionary**

```python
import sys
from dongnae import DongnaeEngine

csv_path = r"./data/dongnaeKR.csv" # Example path

try:
    engine = DongnaeEngine() 
    engine.load(csv_path)
    print(f"Successfully loaded engine from {csv_path}")

    count = len(engine._dongnaes)
    print(f"   - Number of Dongnaes: {count:,}")
    print(f"   - Latitude Coefficient: {engine._lat_coef}")
    print(f"   - Longitude Coefficient: {engine._lon_coef}")

except Exception as e:
    print(f"[Fatal] Engine initiation failure: {e}")
    sys.exit(1)

## **Usage Examples**

### **1\. Reverse Geocoding (where)**

Find the nearest neighborhood for a given coordinate.

```python
lat, lon = 37.5665, 126.9780
town = engine.where(lat, lon)
if town:
    print(f"Welcome to {town['dnname']}!")
```

### **2\. K-Nearest Neighbors (nearest)**

Returns a list of `k nearest nodes` sorted by distance.

Find 3 nearest neighborhoods.

```python
neighbors = engine.nearest(lat, lon, k=3)
for n in neighbors:
    print(f"- {n['dnname']} is {n['distance']}km away")
```

### **3\. Radius Search (within)**

Find all neighborhoods within a 2km radius.

```python
spots = engine.within(lat, lon, radius_km=2.0)
print(f"Found {len(spots)} neighborhoods nearby.")
```

### **4\. Soft Geofencing (resolve)**

Determines if a coordinate falls within a neighborhood's effective radius, with an optional tolerance buffer (fuzziness).
Useful for checking "if the user is inside certain district, with some padded buffer", e.g.;
* threshold=1.0: Strict boundary.
* threshold=1.2: 20% buffer zone (Loose).

```python
matches = engine.resolve(lat, lon, threshold=1.2)
if matches:
    print(f"You are inside {matches[0]['dnname']}'s area.")
```

### **5\. Text Search (search)**

Search by name. Supports "Best Shot" (quasi-geocoding mode) or List return.

* **best_shot = True (default)**: Returns a single DongnaeData object. Can be utilized as approximate quasi-geocoding tool. 
* **best_shot = False**: Returns a list of candidates sorted by relevance score.

```python
# 1. Best Shot (quasi-geocoding Mode)
best = engine.search("PalletTown", best_shot=True)
if best:
    print(f"Found: {best['dnname']}")

# 2. Search Mode
candidates = engine.search("PalletTown", best_shot=False)
for c in candidates:
    print(f"- {c['dnname']}")
```

### **6\. ID Lookup (get)**

Instant lookup by ID ($O(1)$).

```python
info = engine.get("12345467890")
if info:
    print(f"Loaded: {info['dnname']} (Radius: {info['dnradius']}km)")
```

### **7. Boundary Distance Calculator (howfar)**

Calculates the distance from a specific coordinate to the *boundary* of a target Dongnae.
(Negative value means inside the boundary, Positive means outside)

```python
target_id = "1234567890"
distance = engine.howfar(lat, lon, dnid=target_id)

if distance is not None:
    dn_info = engine.get(target_id)
    if distance < 0:
        print(f"You are INSIDE {dn_info['dnname']} ({-distance:.2f}km from edge)")
    else:
        print(f"You are OUTSIDE {dn_info['dnname']} ({distance:.2f}km to edge)")
```

## **API Reference**

### **DongnaeEngine**

#### **\_\_init\_\_(csv\_path: str \= None)**

Initializes the engine. If csv\_path is provided, it calls load().

#### **load(csv\_path: str)**

Loads CSV data, detects encoding (utf-8/cp949), builds the ID index, and auto-calculates distance coefficients based on the dataset's average latitude.

#### **where(lat: float, lon: float) \-\> Optional\[DongnaeData\]**

Returns the single nearest node. Returns None if no data is loaded.

#### **nearest(lat: float, lon: float, k: int \= 1, radius\_km: float \= None) \-\> List\[DongnaeData\]**

Returns a list of `k nearest nodes` sorted by distance.

* radius\_km: Optimization parameter. Only searches within this radius (+ buffer).

#### **within(lat: float, lon: float, radius\_km: float, limit: int \= None) \-\> List\[DongnaeData\]**

Returns all nodes strictly within radius\_km.

#### **resolve(lat: float, lon: float, threshold: float \= 1.0) \-\> List\[DongnaeData\]**

Determines spatial inclusion.

* Returns nodes where distance \<= radius \* (threshold \- 1.0).  

#### **search(keyword: str, limit: int \= 5, best\_shot: bool \= True) \-\> Union\[List\[DongnaeData\], Optional\[DongnaeData\]\]**

Performs a text-based search.

* **best\_shot=True (default)**: Returns a single DongnaeData object. 
* **best\_shot=False**: Returns a list of candidates sorted by relevance score.
If keyword is not within dictionary, returns `None`.

#### **get(dnid: str) \-\> Optional\[DongnaeData\]**

Retrieves a node by its dnid using a Hash Map ($O(1)$ complexity).
If dnid is not within dictionary, returns `None`.

####  **howfar(lat: float, lon: float, dnid: str) \-\> Optional\[float\]**

Calculates the distance from a specific coordinate to the *boundary* of a target Dongnae. (Negative value means inside the boundary, Positive means outside)
If dnid is not within dictionary, returns `None`.
