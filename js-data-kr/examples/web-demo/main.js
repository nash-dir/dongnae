import { DongnaeEngine } from '../../src/engine.js';

let engine = null;
const resultArea = document.getElementById('result-area');

// 1. 엔진 초기화
try {
    console.time("Engine Load");
    engine = new DongnaeEngine();
    console.timeEnd("Engine Load");

    // 초기화 성공 시 메시지 표시
    if (resultArea) {
        resultArea.innerHTML = `
            <div class="result-card" style="border-left-color: #10b981;">
                <div class="result-title">✅ 준비 완료</div>
                <div class="result-meta">
                    ${engine.count.toLocaleString()}개의 동네 데이터가 로드되었습니다.<br>
                    검색하거나 좌표를 입력해보세요.
                </div>
            </div>
        `;
    }
} catch (e) {
    console.error(e);
    if (resultArea) {
        resultArea.innerHTML = `<div class="result-card" style="border-left-color: #ef4444;">초기화 오류: ${e.message}</div>`;
    }
}

// 2. 전역 함수 등록 (HTML onclick에서 호출하기 위해 window 객체에 할당)
window.doSearch = () => {
    const keyword = document.getElementById('keyword').value;
    if (!keyword) return alert('검색어를 입력하세요');

    // 엔진 호출 (bestShot=False로 리스트 반환)
    const results = engine.search(keyword, 10, false);
    renderResults(results, '검색 결과');
};

window.doReverseGeo = () => {
    const lat = parseFloat(document.getElementById('lat').value);
    const lon = parseFloat(document.getElementById('lon').value);

    if (isNaN(lat) || isNaN(lon)) return alert('유효한 좌표를 입력하세요');

    // 엔진 호출 (가장 가까운 1개)
    const result = engine.where(lat, lon);

    if (result) {
        // where는 단일 객체를 반환하므로 배열로 감싸서 전달
        renderResults([result], '위치 확인 결과');
    } else {
        renderResults([], '위치 확인 결과');
    }
};

window.getGPS = () => {
    if (!navigator.geolocation) return alert('GPS를 지원하지 않는 브라우저입니다.');

    resultArea.innerHTML = '<div class="result-card">📍 위치 정보를 가져오는 중...</div>';

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            // 좌표 입력칸 업데이트
            document.getElementById('lat').value = pos.coords.latitude.toFixed(4);
            document.getElementById('lon').value = pos.coords.longitude.toFixed(4);
            // 즉시 조회 실행
            window.doReverseGeo();
        },
        (err) => {
            alert('위치 정보를 가져오는데 실패했습니다: ' + err.message);
            resultArea.innerHTML = '<div class="result-card">위치 정보 가져오기 실패</div>';
        },
        {
            enableHighAccuracy: true, // 정확도 우선
            timeout: 5000,            // 5초 대기
            maximumAge: 0             // 캐시된 위치 사용 안 함
        }
    );
};

// 3. 결과 렌더링 함수
function renderResults(list, title) {
    if (!resultArea) return;

    if (!list || list.length === 0) {
        resultArea.innerHTML = `<div class="result-card">"${title}"에 대한 결과가 없습니다.</div>`;
        return;
    }

    let html = `<div style="margin-bottom:8px; color:#64748b; font-size:0.9rem;">${title} (${list.length}건)</div>`;

    list.forEach(item => {
        // 거리 정보 표시 (검색 모드일 경우 score, 위치 모드일 경우 distance)
        let metaInfo = '';
        let badge = '';

        if (item.distance !== undefined) {
            const dist = item.distance;
            const distText = dist < 0 ? "동네 내부" : `${dist}km 외곽`;
            const color = dist < 0 ? "#15803d" : "#b45309"; // green-700 : amber-700
            metaInfo = `<span style="color:${color}; font-weight:bold;">${distText}</span>`;
        } else if (item.score !== undefined) {
            metaInfo = `<span>매칭 점수: ${item.score}</span>`;
        }

        if (item.dnradius) {
            badge = `<span class="badge">반경 ${item.dnradius}km</span>`;
        }

        html += `
            <div class="result-card">
                <div class="result-title">
                    ${item.dnname}
                    ${badge}
                </div>
                <div class="result-meta">
                    ${metaInfo} <br>
                    <span style="color:#94a3b8; font-size:0.8em;">ID: ${item.dnid}</span>
                </div>
            </div>
        `;
    });

    resultArea.innerHTML = html;
}