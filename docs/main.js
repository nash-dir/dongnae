import { DongnaeEngine } from './src/engine.js';

let engine = null;
const resultArea = document.getElementById('result-area');

// [Helper] 시간 측정
function measureTime(callback) {
    const start = performance.now();
    const result = callback();
    const end = performance.now();
    return { result, elapsed: (end - start).toFixed(2) };
}

// 1. 엔진 초기화
try {
    const { elapsed } = measureTime(() => {
        engine = new DongnaeEngine();
    });
    if (resultArea) {
        resultArea.innerHTML = `
            <div class="result-card" style="border-left-color: #10b981;">
                <div class="result-title">✅ 준비 완료</div>
                <div class="result-meta">
                    ${engine.count.toLocaleString()}개 데이터 로드됨 (${elapsed}ms)<br>
                    입력하는 즉시 결과가 계산됩니다.
                </div>
            </div>
        `;
    }
} catch (e) {
    console.error(e);
    if (resultArea) resultArea.innerHTML = `<div class="result-card" style="color:red;">오류: ${e.message}</div>`;
}

// 2. 검색 (Real-time)
window.doSearch = () => {
    const keyword = document.getElementById('keyword').value.trim();
    if (!keyword) {
        resultArea.innerHTML = ''; // 입력 없으면 결과 클리어
        return;
    }

    const { result, elapsed } = measureTime(() => engine.search(keyword, 10, false));
    renderResults(result, `검색 결과 <small style="color:#2563eb;">(${elapsed}ms)</small>`);
};

// 3. 좌표 역지오코딩 (Real-time)
window.doReverseGeo = () => {
    const lat = parseFloat(document.getElementById('lat').value);
    const lon = parseFloat(document.getElementById('lon').value);

    if (isNaN(lat) || isNaN(lon)) return;

    const { result, elapsed } = measureTime(() => engine.where(lat, lon));

    // where는 단일 객체 반환하므로 배열화
    const list = result ? [result] : [];
    renderResults(list, `위치 확인 결과 <small style="color:#2563eb;">(${elapsed}ms)</small>`);
};

// 4. 주변 탐색 (Real-time)
window.doNearest = () => {
    const lat = parseFloat(document.getElementById('lat-near').value);
    const lon = parseFloat(document.getElementById('lon-near').value);
    const k = parseInt(document.getElementById('input-k').value, 10);
    const radius = parseFloat(document.getElementById('input-rad').value);

    if (isNaN(lat) || isNaN(lon)) return;

    const { result, elapsed } = measureTime(() => engine.nearest(lat, lon, k, radius));
    renderResults(result, `주변 ${radius}km 탐색 <small style="color:#2563eb;">(${elapsed}ms)</small>`);
};


// 5. [Fixed] 좌표 동기화 핸들러
window.syncCoord = (srcId, value, mode) => {
    let targetId;

    // 1. 현재 조작된 게 슬라이더인지 텍스트인지 판단하여 반대편 ID 찾기
    if (srcId.endsWith('-range')) {
        // 슬라이더 조작됨 -> 텍스트박스를 찾아 업데이트
        targetId = srcId.replace('-range', '');
    } else {
        // 텍스트박스 조작됨 -> 슬라이더를 찾아 업데이트
        targetId = srcId + '-range';
    }

    // 2. 반대편 요소 값 동기화
    const targetElem = document.getElementById(targetId);
    if (targetElem) {
        targetElem.value = value;
    }

    // 3. 변경된 값으로 엔진 즉시 실행
    if (mode === 'gps') window.doReverseGeo();
    if (mode === 'near') window.doNearest();
};

// 6. GPS 가져오기
window.getGPS = (target) => {
    if (!navigator.geolocation) return alert('GPS 미지원');

    // 로딩 표시
    resultArea.innerHTML = '<div class="result-card">📍 위치 파악 중...</div>';

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude.toFixed(4);
            const lon = pos.coords.longitude.toFixed(4);

            if (target === 'near') {
                // Nearest 탭 업데이트
                window.syncCoord('lat-near', lat, 'near'); // sync 함수 재사용
                window.syncCoord('lon-near', lon, 'near');
                // 슬라이더도 강제 동기화
                document.getElementById('lat-near-range').value = lat;
                document.getElementById('lon-near-range').value = lon;
            } else {
                // GPS 탭 업데이트
                window.syncCoord('lat', lat, 'gps');
                window.syncCoord('lon', lon, 'gps');
                document.getElementById('lat-range').value = lat;
                document.getElementById('lon-range').value = lon;
            }
        },
        (err) => {
            resultArea.innerHTML = `<div class="result-card">위치 실패: ${err.message}</div>`;
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
};

// 7. 렌더링 함수
function renderResults(list, titleHtml) {
    if (!resultArea) return;
    if (!list || list.length === 0) {
        resultArea.innerHTML = `<div class="result-card" style="color:#64748b;">결과가 없습니다.</div>`;
        return;
    }

    let html = `<div style="margin-bottom:8px; color:#64748b; font-size:0.9rem;">${titleHtml} - ${list.length}건</div>`;

    list.forEach(item => {
        let metaInfo = '';
        let badge = '';

        // 거리 정보가 있는 경우 (GPS / Nearest 탭)
        if (item.distance !== undefined) {
            const dist = item.distance;

            // 포맷팅: 양수면 '+', 음수면 '-' (toFixed가 자동으로 처리) 붙이기
            const sign = dist >= 0 ? "+" : "";
            const distText = `howfar : ${sign}${dist.toFixed(2)}km`;

            // 색상: 내부는 녹색(#15803d), 외부는 주황색(#b45309)
            const color = dist < 0 ? "#15803d" : "#b45309";
            metaInfo = `<span style="color:${color}; font-weight:bold; font-family:monospace;">${distText}</span>`;
        }
        // 검색 점수가 있는 경우 (이름 검색 탭)
        else if (item.score !== undefined) {
            metaInfo = `<span>매칭 점수: ${item.score}</span>`;
        }

        if (item.dnradius) badge = `<span class="badge">R ${item.dnradius}km</span>`;

        html += `
            <div class="result-card">
                <div class="result-title">${item.dnname}${badge}</div>
                <div class="result-meta">
                    ${metaInfo} <br>
                    <span style="color:#94a3b8; font-size:0.8em;">ID: ${item.dnid}</span>
                </div>
            </div>
        `;
    });
    resultArea.innerHTML = html;
}