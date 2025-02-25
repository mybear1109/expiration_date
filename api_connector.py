import requests
import json
import os
import streamlit as st
from urllib.parse import quote

def get_B_API_KEY():
    """
    바코드연계제품정보 API용 키를 환경 변수 또는 st.secrets에서 가져옵니다.
    """
    return os.getenv("B_API_KEY") or st.secrets.get("B_API_KEY")

def get_H_API_KEY():
    """
    식품이력추적 관리품목 등록정보 조회 API용 키를 환경 변수 또는 st.secrets에서 가져옵니다.
    """
    return os.getenv("H_API_KEY") or st.secrets.get("H_API_KEY")

# ---------------------------
# Service 1: 바코드연계제품정보 (C005)
# ---------------------------
BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"

def get_product_info(barcode):
    """
    바코드를 사용하여 식품의약품안전처 API(C005 서비스)에서 제품 정보를 가져옵니다.
    요청 URL: {BASE_URL}/{B_API_KEY}/C005/json/1/5/BAR_CD={barcode}
    """
    b_api_key = get_B_API_KEY()
    if not b_api_key:
        st.error("B_API_KEY가 설정되어 있지 않습니다.")
        return None

    encoded_b_api_key = quote(b_api_key)
    url = f"{BASE_URL}/{encoded_b_api_key}/C005/json/1/5/BAR_CD={barcode}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        st.write("디버그 - 응답 내용:", response.text)
        json_data = response.json()

        if 'C005' in json_data:
            result = json_data['C005'].get('RESULT', {})
            result_code = result.get('CODE', '')
            if result_code == 'INFO-000':
                rows = json_data['C005'].get('row')
                if rows and len(rows) > 0:
                    return rows[0]
                else:
                    st.error("API 결과에 제품 정보가 포함되어 있지 않습니다.")
                    return None
            elif result_code == 'INFO-200':
                st.info("해당하는 데이터가 없습니다. 입력한 바코드를 확인해주세요.")
                return None
            else:
                error_msg = result.get('MSG', '알 수 없는 오류')
                st.error(f"API 오류: {error_msg}")
                return None
        else:
            st.error("API 응답 구조가 예상과 다릅니다.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 오류: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSON 파싱 오류: {e}")
        st.write("응답 내용:", response.text)
        return None
    except KeyError as e:
        st.error(f"데이터 구조 오류: {e}")
        return None

# ---------------------------
# Service 2: 식품이력추적 관리품목 등록정보 조회
# ---------------------------
BASE_HIST_URL = "http://apis.data.go.kr/1471000/FoodHistTrckMngPrdlstRegInfo"

def get_food_hist_info(barcode):
    """
    바코드를 사용하여 식품이력추적 관리품목 등록정보 조회 API에서 제품 정보를 가져옵니다.
    요청 URL 예시:
      http://apis.data.go.kr/1471000/FoodHistTrckMngPrdlstRegInfo/getFoodHistTrckMngPrdlstRegInfo
      ?serviceKey={H_API_KEY}&pdtBarcd={barcode}&pageNo=1&numOfRows=5
    """
    h_api_key = get_H_API_KEY()
    if not h_api_key:
        st.error("H_API_KEY가 설정되어 있지 않습니다.")
        return None

    encoded_h_api_key = quote(h_api_key)
    endpoint = "/getFoodHistTrckMngPrdlstRegInfo"
    url = f"{BASE_HIST_URL}{endpoint}?serviceKey={encoded_h_api_key}&pdtBarcd={barcode}&pageNo=1&numOfRows=5"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        st.write("디버그 - 응답 내용 (식품 이력):", response.text)
        json_data = response.json()

        # 새로운 응답 구조: header, body 로 구성됨
        header = json_data.get("header", {})
        resultCode = header.get("resultCode", "")
        if resultCode == "00":
            body = json_data.get("body", {})
            items = body.get("items", [])
            if items and len(items) > 0:
                # 첫 번째 항목 반환 (필요에 따라 전체 리스트 반환 가능)
                return items[0]
            else:
                st.error("조회된 식품 이력 정보가 없습니다.")
                return None
        else:
            resultMsg = header.get("resultMsg", "알 수 없는 오류")
            st.error(f"API 오류: {resultMsg}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 오류: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSON 파싱 오류: {e}")
        st.write("응답 내용:", response.text)
        return None
    except KeyError as e:
        st.error(f"데이터 구조 오류: {e}")
        return None

# ---------------------------
# 부가 기능: 냉장/냉동 제품 판별 함수
# ---------------------------
def is_refrigerated_or_frozen(product_info):
    """
    제품이 냉장/냉동 제품인지 확인하는 함수.
    C005 서비스의 제품 정보에서 'PRDLST_DCNM' 필드를 확인합니다.
    """
    if product_info and 'PRDLST_DCNM' in product_info:
        product_type = product_info['PRDLST_DCNM']
        return "냉장" in product_type or "냉동" in product_type
    return False
