"""
Key concept of this engine is "dongnae" - an object that has 'ID(dnid), Name(dnname), 2D coordinates(dnlatitude, dnlongitude), and radius(dnradius).
Dictionary of dongnaes should be loaded from CSV prior to using this engine.
"""

import csv
import math
from typing import List, Dict, Optional, Union

class DongnaeEngine:
    def __init__(self, csv_path: str = None):
        self._dongnaes: List[Dict] = []
        
        # Default Haversine coefficients (Based on Korea, approx 37N)
        # Will be updated automatically in load()
        self._lat_coef = 111.0
        self._lon_coef = 88.8
        
        # load CSV if path provided
        if csv_path:
            self.load(csv_path)

    def load(self, csv_path: str):
        """
        Loads the optimized CSV file into memory with automatic encoding detection.
        Also auto-calculates Haversine coefficients based on the dataset's latitude.
        """
        encodings = ['utf-8-sig', 'cp949', 'utf-8']
        loaded = False
        
        for enc in encodings:
            try:
                with open(csv_path, mode='r', encoding=enc) as f:
                    reader = csv.DictReader(f)
                    temp_data = []
                    for row in reader:
                        temp_data.append({
                            'dnid': row['dnid'],
                            'dnname': row['dnname'],
                            'dnlatitude': float(row['dnlatitude']),
                            'dnlongitude': float(row['dnlongitude']),
                            'dnradius': float(row['dnradius'])
                        })
                    self._dongnaes = temp_data
                    loaded = True
                    break

            except (UnicodeDecodeError, KeyError, ValueError):
                continue
        
        if not loaded:
            raise ValueError(f"Failed to load CSV: {csv_path}. Tried encodings: {encodings}.")

        # -------------------------------------------------------
        # [Auto-Calibration] Calculate Haversine coefficients
        # -------------------------------------------------------
        if self._dongnaes:
            # 1. Extract all latitudes
            lats = [d['dnlatitude'] for d in self._dongnaes]
            
            # 2. Find the center latitude of the dataset
            min_lat, max_lat = min(lats), max(lats)
            avg_lat = (min_lat + max_lat) / 2.0
            
            # 3. Update coefficients (Round to 2 decimal places)
            # Latitude: Approx 111 km per degree (Constant)
            # Longitude: 111 * cos(lat) km per degree (Varies by latitude)
            self._lat_coef = 111.0
            self._lon_coef = round(111.0 * math.cos(math.radians(avg_lat)), 2)

    def _calc_dist(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        [Geometric Distance] Calculates distance between two points (Haversine approximation).
        Uses dynamically calculated coefficients based on the loaded dataset's center latitude.
        """
        d_lat = (lat2 - lat1) * self._lat_coef
        d_lon = (lon2 - lon1) * self._lon_coef
        return math.sqrt(d_lat**2 + d_lon**2)

    def _dongnae_dist(self, lat: float, lon: float, dn: Dict) -> float:
        """
        [Business Metric] Calculates 'Boundary Distance' from a point to a Dongnae.
        Returns: (Geometric Distance to Center) - (Radius of Dongnae)
        """
        # Delegate geometric calculation to _calc_dist
        center_dist = self._calc_dist(lat, lon, dn['dnlatitude'], dn['dnlongitude'])
        
        # Apply Radius adjustment
        return center_dist - dn['dnradius']

    def where(self, lat: float, lon: float) -> Optional[Dict]:
        """
        [Reverse Geocoding] Returns the single nearest 'Dongnae' (neighborhood).
        """
        nearest = self.nearest(lat, lon, k=1)
        return nearest[0] if nearest else None

    def nearest(self, lat: float, lon: float, k: int = 1, radius_km: float = None) -> List[Dict]:
        """
        Returns the K nearest Dongnaes sorted by 'Boundary Distance'.
        :param radius_km: Used to limit the search range (performance optimization)
        """
        # 1. Primary filtering (Bounding Box)
        # Search range = (Requested Radius OR Default 10km) + Max Dongnae Radius Buffer(5km)
        scan_radius = (radius_km if radius_km else 10.0) + 5.0
        
        # Dynamic bbox calculation using current coefficients
        lat_delta = scan_radius / self._lat_coef
        lon_delta = scan_radius / self._lon_coef
        
        candidates = [
            dn for dn in self._dongnaes
            if (lat - lat_delta <= dn['dnlatitude'] <= lat + lat_delta) and
               (lon - lon_delta <= dn['dnlongitude'] <= lon + lon_delta)
        ]
        
        if not candidates and radius_km is None:
            candidates = self._dongnaes

        # 2. Calculate Boundary Distance
        results = []
        for dn in candidates:
            b_dist = self._dongnae_dist(lat, lon, dn)
            
            if radius_km is None or b_dist <= radius_km:
                dn_res = dn.copy()
                dn_res['distance'] = round(b_dist, 4)
                results.append(dn_res)

        results.sort(key=lambda x: x['distance'])
        return results[:k]

    def within(self, lat: float, lon: float, radius_km: float, limit: int = None) -> List[Dict]:
        """
        [Radius Search] Returns all Dongnaes whose boundaries are within R km.
        """
        return self.nearest(lat, lon, k=limit if limit else len(self._dongnaes), radius_km=radius_km)

    def resolve(self, lat: float, lon: float, threshold: float = 1.0) -> List[Dict]:
        """
        [Soft Geofencing] Determine if coordinates fall within a specific Dongnae's effective radius.
        """
        max_scan = 15.0 * threshold
        lat_delta = max_scan / self._lat_coef
        lon_delta = max_scan / self._lon_coef

        candidates = [
            dn for dn in self._dongnaes
            if (lat - lat_delta <= dn['dnlatitude'] <= lat + lat_delta) and
               (lon - lon_delta <= dn['dnlongitude'] <= lon + lon_delta)
        ]

        matches = []
        for dn in candidates:
            b_dist = self._dongnae_dist(lat, lon, dn)
            
            if b_dist <= dn['dnradius'] * (threshold - 1.0):
                dn_res = dn.copy()
                dn_res['distance'] = round(b_dist, 4)
                
                raw_dist = b_dist + dn['dnradius']
                limit_dist = dn['dnradius'] * threshold
                
                dn_res['score'] = round(raw_dist / limit_dist, 2)
                matches.append(dn_res)
        
        matches.sort(key=lambda x: x['score'])
        return matches


    def search(self, keyword: str, limit: int = 5, best_shot: bool = True) -> Union[List[Dict], Optional[Dict]]:
        """
        [Text Search & Geocoding] Search by Dongnae name (Bag of Words similarity).
        
        :param keyword: Search query (e.g., "Pangyo")
        :param limit: Max number of candidates (only used when best_shot=False)
        :param best_shot: If True, returns the single best match (Geocoding mode).
                          If False, returns a list of candidates (Search mode).
        """
        query_tokens = keyword.strip().split()
        if not query_tokens:
            return None if best_shot else []

        scored_list = []
        for dn in self._dongnaes:
            score = 0
            name = dn['dnname']
            for token in query_tokens:
                if token in name:
                    score += 1
            
            if score > 0:
                scored_list.append({
                    'data': dn,
                    'score': score,
                    'len': len(name) # Prefer shorter names (tie-breaker)
                })
        
        # Sort: High score -> Short name length
        scored_list.sort(key=lambda x: (-x['score'], x['len']))
        
        # Inject score into results
        results = []
        # If best_shot is True, we only need the top 1, otherwise up to limit
        target_slice = scored_list[:1] if best_shot else scored_list[:limit]
        
        for item in target_slice:
            dn_res = item['data'].copy()
            dn_res['score'] = item['score']
            results.append(dn_res)
            
        if not results:
            return None if best_shot else []

        # Return Logic based on best_shot flag
        if best_shot:
            return results[0]  # Return single Dict (Geocoding Mode)
        else:
            return results     # Return List[Dict] (Search Mode)


    def get(self, dnid: str) -> Optional[Dict]:
        """
        [ID Lookup] Direct lookup by dnid (legal dong code)
        """
        for dn in self._dongnaes:
            if dn['dnid'] == str(dnid):
                return dn
        return None
