# Dongnae Engine Benchmark

This document details the performance benchmark results of `dongnae 0.2.0` engine compared to a standard HTTP Reverse-geocoding API (*VWorld*).

## 1. Test Environment

* **Dataset**: CSV dictionary included in PyPI `dongnae-kr 2025.11.30` dataset package (South Korea Regional Data, Carved from Government SHP)
* **Sample Size**: 10,000 Random Coordinates (Lat/Lon) generated within South Korea's territory.
* **Comparison Target**: `VWorld` [http://api.vworld.kr/req/address?] Standard ROK Government Reverse Geocoding API
* **Hardware**: Intel i7-13700F / 16.0GB RAM / Windows 11 Pro / 500 mbps wired network


## 2. Method

* **Data Collection Loop**
  * Create random point within Lat/Lon grid.
  * Lookup coordiate's real address with `VWorld` reverse-geocoding API, checking response time in millisecond scale, and record if its address is valid.
  * Retrieve 3 `nearest` dongnae candidates from that coordiate with `dongnae-kr 0.1.0` package, checking response time in millisecond scale.

* **Evaluation**
  * For accuracy real address falls within 3 `nearest` dongnae candidates.
  * In CSV dictionary of `dongnae-kr`, `dnname` of addresses located in `세종특별자치시` are recorded as `세종특별자치시 세종시`. Substitution of string `세종특별자치시 세종시` to `세종특별자치시` was specifically required for this labeling error handling.
  * When Data Collection Loops reaches limit, compare average latency of API request and dongnae engine retrieval.


## 3. Result

### 3.A. Speed

**Result**: `dongnae` is approximately **15x faster** than the external API.

* **Latency Analysis**:
  * `VWorld API` : Network latency + Server processing time (Typically 50ms ~ 200ms per request)
    * To eliminate effect from external traffic, benchmark was executed in midnight in Korea.
  * `dongnae`: Pure CPU calculation time (Zero network latency)

### 3.B. Accuracy

Since `dongnae` uses a simplified circular model (Radius) instead of precise polygon geometry, there is a slight trade-off in accuracy. However, practical accuracy for "Near Me" context is extremely high.

| Metric | Accuracy | Description |
| :--- | :--- | :--- |
| **Top-1 Accuracy** | **71.67%** | Best-shot was exact match with the official administrative district retrieved from *VWorld* API |
| **Top-3 Accuracy** | **97.31%** | The correct district is within the top 3 candidates. |
| **Miss Rate** | **2.69%** | The correct district was not included in the top 3 candidates. |

### 💡 Interpretation
* **Pinpoint Precision (71.67%)**: Due to irregular shapes of boundaries, the nearest center point might not always be the correct district in border areas.
* **Practical Precision (97.31%)**: For most location-based services (delivery, recommendations, tagging), considering the top-3 nearest neighborhoods covers **97.31%** of user intent.
* **Conclusion**: `dongnae` provides a massive speed advantage (~15x) with a tolerable practical error rate (2.69%) for non-critical mile-sclae spatial applications.

---
*Last Updated: 2025-12-03*