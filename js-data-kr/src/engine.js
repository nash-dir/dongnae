import rawData from './dongnae_data.js';

export class DongnaeEngine {
    constructor() {
        // 1. 데이터 바인딩 (메모리 복사 없이 참조만 함)
        // SoA (Structure of Arrays) 패턴
        this.ids = rawData.ids;
        this.names = rawData.names;
        this.lats = rawData.lats;
        this.lons = rawData.lons;
        this.rads = rawData.rads;
        this.count = this.ids.length;

        // 2. 계수 자동 보정 (Auto-Calibration)
        // 데이터 전체를 순회하지 않고 min/max만 빠르게 찾아서 평균 계산
        let minLat = 90, maxLat = -90;
        // 샘플링으로 속도 최적화 (100개 단위)
        for (let i = 0; i < this.count; i += 100) {
            const val = this.lats[i];
            if (val < minLat) minLat = val;
            if (val > maxLat) maxLat = val;
        }
        const avgLat = (minLat + maxLat) / 2.0;

        this.latCoef = 111.0;
        // JS의 Math.cos는 라디안을 받습니다.
        this.lonCoef = +(111.0 * Math.cos(avgLat * (Math.PI / 180))).toFixed(2);

        // 3. ID 검색용 인덱스 생성 (O(1) Lookup)
        this.idMap = new Map();
        for (let i = 0; i < this.count; i++) {
            this.idMap.set(this.ids[i], i);
        }
    }

    /**
     * [Internal] 특정 인덱스의 데이터를 객체로 변환하여 반환
     * 필요할 때만 객체를 생성하므로 메모리를 절약함 (Lazy Generation)
     */
    _getAt(i, distance = null, score = null) {
        const obj = {
            dnid: this.ids[i],
            dnname: this.names[i],
            dnlatitude: this.lats[i],
            dnlongitude: this.lons[i],
            dnradius: this.rads[i]
        };
        if (distance !== null) obj.distance = distance;
        if (score !== null) obj.score = score;
        return obj;
    }

    /**
     * [Internal] 거리 계산 (Haversine approximation)
     */
    _calcDist(lat1, lon1, lat2, lon2) {
        const dLat = (lat2 - lat1) * this.latCoef;
        const dLon = (lon2 - lon1) * this.lonCoef;
        return Math.sqrt(dLat * dLat + dLon * dLon);
    }

    /**
     * [Internal] 동네 경계 거리 계산
     * (중심점 거리) - (반경)
     */
    _dongnaeDist(lat, lon, idx) {
        const centerDist = this._calcDist(lat, lon, this.lats[idx], this.lons[idx]);
        return centerDist - this.rads[idx];
    }

    /**
     * [Reverse Geocoding] Lookup one nearest Dongnae from given coordinate
     */
    where(lat, lon) {
        const results = this.nearest(lat, lon, 1);
        return results.length > 0 ? results[0] : null;
    }

    /**
     * [Nearest Neighbor] Lookup k-best Dongnae(s) from given coordinate
     */
    nearest(lat, lon, k = 1, radiusKm = null) {
        // 1. Bounding Box Filtering
        const scanRadius = (radiusKm || 10.0) + 5.0;
        const latDelta = scanRadius / this.latCoef;
        const lonDelta = scanRadius / this.lonCoef;

        const candidates = [];

        for (let i = 0; i < this.count; i++) {
            const tLat = this.lats[i];
            const tLon = this.lons[i];

            // check radius (BBox)
            if (tLat >= lat - latDelta && tLat <= lat + latDelta &&
                tLon >= lon - lonDelta && tLon <= lon + lonDelta) {

                const bDist = this._dongnaeDist(lat, lon, i);

                if (radiusKm === null || bDist <= radiusKm) {
                    candidates.push({ idx: i, dist: parseFloat(bDist.toFixed(4)) });
                }
            }
        }

        // 2. Sort by Distance
        candidates.sort((a, b) => a.dist - b.dist);

        // 3. Map to Objects
        return candidates.slice(0, k).map(c => this._getAt(c.idx, c.dist));
    }

    /**
     * [Radius Search] search Dongnae(s) within certain radius
     */
    within(lat, lon, radiusKm, limit = null) {
        const results = this.nearest(lat, lon, this.count, radiusKm);
        return limit ? results.slice(0, limit) : results;
    }

    /**
     * [Soft Geofencing] 특정 영역 포함 여부 판정
     */
    resolve(lat, lon, threshold = 1.0) {
        const maxScan = 15.0 * threshold;
        const latDelta = maxScan / this.latCoef;
        const lonDelta = maxScan / this.lonCoef;

        const matches = [];

        for (let i = 0; i < this.count; i++) {
            const tLat = this.lats[i];
            const tLon = this.lons[i];

            if (tLat >= lat - latDelta && tLat <= lat + latDelta &&
                tLon >= lon - lonDelta && tLon <= lon + lonDelta) {

                const bDist = this._dongnaeDist(lat, lon, i);
                const radius = this.rads[i];

                // 판정 로직
                if (bDist <= radius * (threshold - 1.0)) {
                    const rawDist = bDist + radius;
                    const limitDist = radius * threshold;
                    const score = parseFloat((rawDist / limitDist).toFixed(2));

                    matches.push(this._getAt(i, parseFloat(bDist.toFixed(4)), score));
                }
            }
        }

        matches.sort((a, b) => a.score - b.score);
        return matches;
    }

    /**
     * [Text Search] 키워드 검색
     */
    search(keyword, limit = 5, bestShot = true) {
        const queryTokens = keyword.trim().split(/\s+/);
        if (queryTokens.length === 0) return bestShot ? null : [];

        const scoredList = [];

        for (let i = 0; i < this.count; i++) {
            let score = 0;
            const name = this.names[i];

            for (const token of queryTokens) {
                if (name.includes(token)) score++;
            }

            if (score > 0) {
                scoredList.push({
                    idx: i,
                    score: score,
                    len: name.length
                });
            }
        }

        // Sort: Score Desc -> Length Asc
        scoredList.sort((a, b) => {
            if (b.score !== a.score) return b.score - a.score;
            return a.len - b.len;
        });

        const targetSlice = bestShot ? scoredList.slice(0, 1) : scoredList.slice(0, limit);
        const results = targetSlice.map(item => this._getAt(item.idx, null, item.score));

        if (results.length === 0) return bestShot ? null : [];
        return bestShot ? results[0] : results;
    }

    /**
     * [ID Lookup] ID로 직접 조회 (O(1))
     */
    get(dnid) {
        const idx = this.idMap.get(String(dnid)); // 문자열로 안전하게 변환
        return idx !== undefined ? this._getAt(idx) : null;
    }
}