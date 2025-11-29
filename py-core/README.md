# **dongnae** 

## **Ultra lightweight, self contained, Quasi-Geocoding Engine**

* **dongnae** is a dependency-free, pure Python library designed for **high-performance reverse geocoding, radius search, and spatial lookups**. It operates from self-contained native script & pre-rendered CSV dataframe. Designed for high-performance microservices and client-side applications.

* **Zero backend**
* **Zero auth**
* **Zero dependencies**

* It is optimized for **local/regional datasets** (e.g., Neighborhoods in a specific country) using latitude-based auto-calibration instead of expensive spherical trigonometry for every calculation.

## **Key Features**

* **Quasi-Geocoding to "Dongnae""**

  * Sometimes you just want to lookup which neighborhood you are in.
  
  * Instead of precise street-level addresses, it maps coordinates to the nearest "Dongnae" (Neighborhood/District node), which is not quite precise but still good enough for some applications.

  * Key concept of this engine is **"dongnae"** - an object that has ID(dnid), Name(dnname), 2D coordinates(dnlatitude, dnlongitude), and radius(dnradius).

  * Dictionary of dongnaes should be loaded from CSV / JS prior to using this engine.

* **Zero Dependencies** 

  * **Pure Python**: Runs on pure Python & essential libraries (csv, math). No pip install required for dependencies. 
  
  * **Ultra lightweight** : Does not require heavy GIS libraries (pandas, geopandas, or shapely)

* **Lightning Fast**

  * **Auto-Calibration**: Calculates Haversine coefficients once upon loading, avoiding repeated trigonometric operations (cos, sin) during queries.  

  * **Spatial Indexing**: Uses dynamic Bounding Box (BBox) filtering to minimize search space.  

  * $O(1)$ **ID Lookup**: Instant retrieval by ID using an internal Hash Map.  

* **Self-contained**

  * **Zero backend** : No networking, GIS server required

  * **Zero dependencies** : Runs on Python standard libraries (csv, math), 

  * **Zero authentication** : No authentication, API key required

  * **Zero vulnerability** : No external connections means no attack surface. (You can't hack what doesn't quack.)

* **Business-Ready Logic**:  
  * **Boundary Distance**: Calculates distance from the *edge* of a neighborhood, not just the center.  

  * **Soft Geofencing**: Determines if a point is "roughly" inside a neighborhood with an adjustable threshold.  

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

``` bash
pip install dongnae
```

\# Initialize and load data  
engine \= DongnaeEngine("data.csv")

## **Usage Examples**

### **1\. Reverse Geocoding (where)**

Find the nearest neighborhood for a given coordinate.

lat, lon \= 37.5665, 126.9780  
result \= engine.where(lat, lon)

if result:  
    print(f"You are in: {result\['dnname'\]}")

### **2\. K-Nearest Neighbors (nearest)**

Find the 3 nearest neighborhoods.

\# Get 3 closest nodes within 10km  
neighbors \= engine.nearest(lat, lon, k=3, radius\_km=10.0)

for n in neighbors:  
    print(f"{n\['dnname'\]} \- {n\['distance'\]}km away")

### **3\. Radius Search (within)**

Find all neighborhoods within a 2km radius.

nearby\_spots \= engine.within(lat, lon, radius\_km=2.0)

### **4\. Soft Geofencing (resolve)**

Determines if a coordinate falls within a neighborhood's effective radius, with an optional tolerance buffer (fuzziness).

* threshold=1.0: Strict boundary.  
* threshold=1.2: 20% buffer zone (Loose).

\# Check if point is effectively inside the area  
matches \= engine.resolve(lat, lon, threshold=1.2)

### **5\. Text Search (search)**

Search by name. Supports "Best Shot" (Geocoding mode) or List return.

\# Geocoding Mode (Returns single best match Dict)  
best\_match \= engine.search("Pangyo", best\_shot=True)

\# Search Mode (Returns List\[Dict\])  
candidates \= engine.search("Gangnam", best\_shot=False)

### **6\. ID Lookup (get)**

Instant lookup by ID ($O(1)$).

data \= engine.get("1168010100")

## **API Reference**

### **DongnaeEngine**

#### **\_\_init\_\_(csv\_path: str \= None)**

Initializes the engine. If csv\_path is provided, it calls load().

#### **load(csv\_path: str)**

Loads CSV data, detects encoding (utf-8/cp949), builds the ID index, and auto-calculates distance coefficients based on the dataset's average latitude.

#### **where(lat: float, lon: float) \-\> Optional\[DongnaeData\]**

Returns the single nearest node. Returns None if no data is loaded.

#### **nearest(lat: float, lon: float, k: int \= 1, radius\_km: float \= None) \-\> List\[DongnaeData\]**

Returns a list of k nearest nodes sorted by distance.

* radius\_km: Optimization parameter. Only searches within this radius (+ buffer).

#### **within(lat: float, lon: float, radius\_km: float, limit: int \= None) \-\> List\[DongnaeData\]**

Returns all nodes strictly within radius\_km.

#### **resolve(lat: float, lon: float, threshold: float \= 1.0) \-\> List\[DongnaeData\]**

Determines spatial inclusion.

* Returns nodes where distance \<= radius \* (threshold \- 1.0).  
* Useful for checking "Is the user inside this district?".

#### **search(keyword: str, limit: int \= 5, best\_shot: bool \= True) \-\> Union\[List\[DongnaeData\], Optional\[DongnaeData\]\]**

Performs a text-based search.

* **best\_shot=True**: Returns a single DongnaeData object (or None).  
* **best\_shot=False**: Returns a list of candidates sorted by relevance score.

#### **get(dnid: str) \-\> Optional\[DongnaeData\]**

Retrieves a node by its dnid using a Hash Map ($O(1)$ complexity).
