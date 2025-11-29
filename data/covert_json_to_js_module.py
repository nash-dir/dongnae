import json
import os

# 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 입력: 기존 컬럼형 JSON 파일
INPUT_JSON = os.path.join(BASE_DIR, '..', 'js-data-kr', 'src', 'dongnae_cols.json')
# 출력: JS 모듈 파일
OUTPUT_JS = os.path.join(BASE_DIR, '..', 'js-data-kr', 'src', 'dongnae_data.js')

def json_to_es_module():
    print(f"🔄 Converting JSON to JS Module...")
    try:
        with open(INPUT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # JS 모듈 문법(export default)으로 감싸기
        # separators=(',', ':')로 공백을 제거하여 용량을 줄입니다.
        js_content = f"const data = {json.dumps(data, separators=(',', ':'), ensure_ascii=False)};\nexport default data;"
        
        with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
            f.write(js_content)
            
        print(f"✅ 변환 완료: {OUTPUT_JS}")
        print("   이제 engine.js에서 import 오류가 사라질 것입니다.")
        
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {INPUT_JSON}")
        print("   경로를 확인하거나 이전 단계의 JSON 변환이 수행되었는지 확인하세요.")

if __name__ == "__main__":
    json_to_es_module()