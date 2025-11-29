export interface DongnaeResult {
    dnid: number;
    dnname: string;
    dnlatitude: number;
    dnlongitude: number;
    dnradius: number;
    distance?: number;
    score?: number;
}

export class DongnaeEngine {
    constructor();
    count: number;

    // Lookup one nearest Dongnae from given coordinate
    where(lat: number, lon: number): DongnaeResult | null;

    // Lookup k-best Dongnae(s) from given coordinate
    nearest(lat: number, lon: number, k?: number, radiusKm?: number): DongnaeResult[];

    // search Dongnae(s) within certain radius
    within(lat: number, lon: number, radiusKm: number, limit?: number): DongnaeResult[];

    // search by keyword
    search(keyword: string, limit?: number, bestShot?: boolean): DongnaeResult | DongnaeResult[] | null;

    // get Dongnae by dnid
    get(dnid: number | string): DongnaeResult | null;
}