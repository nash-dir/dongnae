export interface DongnaeResult {
    dnid: string;        // ID는 문자열로 관리 (예: "1111010100")
    dnname: string;      // 동네 이름
    dnlatitude: number;  // 위도
    dnlongitude: number; // 경도
    dnradius: number;    // 반경 (km)
    distance?: number;   // 계산된 거리 (요청 시 포함됨)
    score?: number;      // 매칭 점수 (resolve/search 사용 시 포함됨)
}

export class DongnaeEngine {
    constructor();

    /**
     * 특정 좌표에 가장 가까운 동네 1곳을 찾습니다.
     */
    where(lat: number, lon: number): DongnaeResult | null;

    /**
     * 특정 좌표에서 가까운 동네 k개를 거리순으로 반환합니다.
     */
    nearest(lat: number, lon: number, k?: number, radiusKm?: number): DongnaeResult[];

    /**
     * 특정 반경(radiusKm) 안에 겹치는 모든 동네를 찾습니다.
     */
    within(lat: number, lon: number, radiusKm: number, limit?: number): DongnaeResult[];

    /**
     * 특정 좌표가 동네 영역에 포함되는지(혹은 근접한지) 판정합니다.
     * @param threshold - 반경 임계값 (기본 1.0 = 100%)
     */
    resolve(lat: number, lon: number, threshold?: number): DongnaeResult[];

    /**
     * 키워드로 동네를 검색합니다.
     */
    search(keyword: string, limit?: number, bestShot?: boolean): DongnaeResult[] | DongnaeResult | null;

    /**
     * 동네 ID로 정보를 직접 조회합니다.
     */
    get(dnid: string | number): DongnaeResult | null;

    /**
     * [New] 특정 좌표와 특정 동네 사이의 거리를 계산합니다.
     * 반환값: (중심 거리) - (반경). 음수면 반경 내 포함.
     */
    howfar(lat: number, lon: number, dnid: string | number): number | null;
}