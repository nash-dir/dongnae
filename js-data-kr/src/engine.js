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
        // 위도 전체를 순회하여 min/max와 최대 반경을 구합니다.
        // (100개 샘플링은 진짜 극값을 놓쳐 Python 코어와 계수가 달라질 수 있으므로
        //  전수 스캔으로 통일. 초기화 1회뿐이라 비용은 무시할 수준입니다.)
        let minLat = 90, maxLat = -90, maxRad = 0;
        for (let i = 0; i < this.count; i++) {
            const val = this.lats[i];
            if (val < minLat) minLat = val;
            if (val > maxLat) maxLat = val;
            if (this.rads[i] > maxRad) maxRad = this.rads[i];
        }
        const avgLat = (minLat + maxLat) / 2.0;

        this.latCoef = 111.0;
        // JS의 Math.cos는 라디안을 받습니다.
        this.lonCoef = +(111.0 * Math.cos(avgLat * (Math.PI / 180))).toFixed(2);

        // 데이터셋 내 최대 반경. bbox 버퍼가 이 값을 따라가도록 하여
        // 큰 반경 노드가 후보에서 누락되지 않게 합니다. (Python 코어와 동일)
        this.maxRadius = maxRad;

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

    howfar(lat, lon, dnid) {
        // 1. ID 존재 여부 확인 (O(1) Lookup)
        // 입력된 dnid를 문자열로 안전하게 변환하여 조회
        const idx = this.idMap.get(String(dnid));

        // 존재하지 않는 ID인 경우 null 반환
        if (idx === undefined) {
            return null;
        }

        // 2. 내부 메서드를 재사용하여 경계 거리 계산
        // (중심점까지의 거리) - (동네 반경)
        const dist = this._dongnaeDist(lat, lon, idx);

        // raw 값 반환 (Python 코어 howfar과 동일하게 반올림하지 않음)
        return dist;
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
        // 검색 범위 + 데이터셋 최대 반경(버퍼). 큰 반경 노드도 후보에 포함되도록 보장.
        // (?? 사용: radiusKm=0도 유효한 0 범위로 취급, falsy 함정 방지)
        const effectiveRange = radiusKm ?? 10.0;
        const scanRadius = effectiveRange + this.maxRadius;
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

        // Fallback parity with the Python core: if the bbox produced no
        // candidates and no radius limit was given, scan the whole dataset so
        // where()/nearest() stay total (never empty for a non-empty dataset).
        if (candidates.length === 0 && radiusKm === null) {
            for (let i = 0; i < this.count; i++) {
                const bDist = this._dongnaeDist(lat, lon, i);
                candidates.push({ idx: i, dist: parseFloat(bDist.toFixed(4)) });
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
        // limit != null: limit=0이면 빈 배열 (falsy 함정 방지)
        return limit != null ? results.slice(0, limit) : results;
    }

    /**
     * [Soft Geofencing] 특정 영역 포함 여부 판정
     */
    resolve(lat, lon, threshold = 1.0) {
        // 매칭 가능한 최대 중심거리 = maxRadius * threshold. (고정 15km 가정 제거)
        const maxScan = this.maxRadius * threshold;
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
                    // limitDist 0 (radius/threshold 0) => 정확히 중심점, score 0.0
                    // (Python 코어와 동일, NaN 방지)
                    const score = limitDist ? parseFloat((rawDist / limitDist).toFixed(2)) : 0.0;

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
        // filter(Boolean): 빈 문자열/공백 입력 시 [""]가 되어 모든 이름에
        // 매칭되는 버그 방지. 토큰이 없으면 결과 없음으로 처리.
        const queryTokens = keyword.trim().split(/\s+/).filter(Boolean);
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