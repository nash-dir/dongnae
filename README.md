# **dongnae v.0.2.0** 

[![Live Demo](https://img.shields.io/badge/Live_Demo-Try_it_Now-blue?style=for-the-badge&logo=githubpages)](https://nash-dir.github.io/dongnae/)

[![CI](https://github.com/nash-dir/dongnae/actions/workflows/ci.yml/badge.svg)](https://github.com/nash-dir/dongnae/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/dongnae.svg)](https://badge.fury.io/py/dongnae)
[![Python Versions](https://img.shields.io/pypi/pyversions/dongnae.svg)](https://pypi.org/project/dongnae/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **▶ Try it live (no install):** **<https://nash-dir.github.io/dongnae/>**

## **Lightest Possible Spatial Engine**

* **dongnae** is a dependency-free, pure Python library designed for **high-performance reverse geocoding, radius search, spatial lookup, and Area-of-Effect lookup**. It operates from self-contained native script & pre-rendered CSV dataframe. Designed for high-performance microservices and client-side applications.

  * **Zero backend**
  * **Zero auth**
  * **Zero dependencies**

* It is optimized for **local/regional datasets** (e.g., Neighborhoods in a specific country) using latitude-based auto-calibration instead of expensive spherical trigonometry for every calculation.

## **Key Features**

* **Quasi-Geocoding to `Dongnae`**

  * Traditional Geocoding APIs (Google Maps, VWorld) are powerful but often **overkill** for many business logic scenarios. They introduce network latency, API costs, and heavy dependencies. Especially when you just want to lookup `roughly which neighborhood` you are in.
  
  * `dongnae` takes a different approach. It trades "pinpoint street-level precision" for **"neighborhood-level semantic accuracy"**, gaining **extreme speed** and **portability** in return. Instead of precise street-level addresses, it maps coordinates to the nearest `Dongnae` (Neighborhood/District node), which is not quite precise but still good enough for some applications. 

  * Key concept of this engine is **"dongnae"** - an object that has ID(dnid), Name(dnname), 2D coordinates(dnlatitude, dnlongitude), and radius(dnradius).

  * Dictionary of dongnaes should be pre-baked and loaded from CSV / JS prior to using this engine.

  * Recommended for lightweight, suggestion-based frontends(e.g. Web / PWAs); ML & DS preprocessing; serverless or edge computing backend(e.g., AWS Lambda, Cloudflare Workers)


* **Name and Location based lookup to pre-baked `Dongnae` dictioary**

  * Calculates the ballpark 'Boundary Distance' from a specific coordinate to a target Dongnae.


* **Boundary Distance calculation**

  * Calculates the ballpark 'Boundary Distance' from a specific coordinate to a target Dongnae.

  * Great for quickly looking up geopoints within Area-of-Effect from certain `dongnae` in kilometer scale.

  * Recommended for microsystem backend, AWS Lambda, embedded, push service, etc.


* **Zero Dependencies** 

  * **Pure Python**: Runs on pure Python & essential libraries (csv, math). No pip install required for dependencies. 
  
  * **Ultra lightweight** : Does not require heavy GIS libraries (pandas, geopandas, or shapely)


* **Lightning Fast & Practical Accuracy**

  * **Auto-Calibration**: Calculates Haversine coefficients once upon loading, avoiding repeated trigonometric operations (cos, sin) during queries.  

  * **Spatial Indexing**: Uses dynamic Bounding Box (BBox) filtering to minimize search space.  

  * $O(1)$ **ID Lookup**: Instant retrieval by ID using an internal Hash Map.  

  * **Proven Performance**: In an `benchmark` with `dongnae-kr 2025.11.30` dataset package (carved from ROK Regional Geometry data) & 10k random points, `dongnae` was **~15x faster (in midnight environment)** than `VWorld API response`.
      * **Top-1 Accuracy**: 71.67% (Pinpoint precision)
      * **Top-3 Accuracy**: **97.31%** (Practical precision)
      * **Miss Rate**: 2.69% (Not within top 3)
      * *`Benchmark` results are based on random coordinate sampling within South Korea and string-matching against VWorld API address responses. Results may vary depending on dataset and evaluation criteria.*


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

---

## ✨ Key Capabilities

`dongnae` is not just a coordinate calculator; it is a spatial decision engine.

### 📍 Reverse Geocoding (`where`)
> *"Where am I roughly?"*
* **Function**: Returns the nearest neighborhood node for a given coordinate.
* **Why use it**: Perfect for identifying user context (e.g., "You are in Gangnam-gu") without triggering expensive API calls.

### 📏 Service Availability Check (`howfar`)
> *"Is this point inside our service area?"*
* **Function**: Calculates the **Boundary Distance** from a specific coordinate to a target neighborhood's edge.
    * **Negative (-)**: Inside the boundary.
    * **Positive (+)**: Outside the boundary.
* **Why use it**: Determines immediate service availability (e.g., Delivery, Pickup) with a single line of code. $O(1)$ complexity via ID lookup.

### 🔍 Zero-Latency Search (`search`)
> *"Find 'Pangyo' instantly."*
* **Function**: Converts text queries into spatial objects without any network request.
* **Why use it**: Provides instant "Quasi-Geocoding" for search bars. Delivers a zero-latency UX for users typing in locations, even offline.

### 🎯 Soft Geofencing (`resolve`)
> *"Are they close enough?"*
* **Function**: Determines if a coordinate falls within a neighborhood's effective radius with an adjustable tolerance threshold.
* **Why use it**: Useful for loose boundary checks (e.g., "Allow users within 20% buffer of the district").

### 📡 Radius Search (`nearest`, `within`)
> *"What's nearby?"*
* **Function**: Finds $K$-nearest neighbors or all nodes within a specific radius.
* **Why use it**: optimized spatial indexing ensures high performance even with thousands of nodes.

---

## 📦 Packages & Installation

This project is architected as a **monorepo** supporting multiple languages, as it may be useful for both backend & frontend applications. Please refer to the specific documentation for installation and API usage.

| Language | Package | Description | Documentation |
| :--- | :--- | :--- | :--- |
| **Python** | `dongnae` | Pure Python Engine for Backend/Data Ops | [👉 Go to Python Docs](./py-core/README.md) |
| **JavaScript** | `@dongnae-js/data-kr` | JS Engine for Frontend/Edge | [👉 Go to JS Docs](./js-data-kr/README.md) |

---

## 📊 Performance

In internal benchmarks against public Government APIs (VWorld), `dongnae`:
* **Speed**: ~20x Faster (0.009s vs 0.16s)
* **Accuracy**: **97.3%** Top-3 Hit Rate for neighborhood identification.

> *`dongnae` is designed to be "Good Enough" for ~95% of semantic spatial problems, while being "Orders of Magnitude" faster and cheaper.*