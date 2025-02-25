# 식품의약품안전처 API와 통신하는 기능을 제공합니다.
import requests
import json
from config import API_KEY

def get_product_info(barcode):
    """
    식품의약품안전처 API를 사용하여 바코드에 해당하는 제품 정보를 가져옵니다.
    """
    url = f"http://openapi.foodsafetykorea.go.kr/api/{API_KEY}/C005/json/1/5/BAR_CD={barcode}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()

        if json_data['C005']['result']['code'] == 'INFO-000':
            return json_data['C005']['row'][0]
        else:
            print("API Error:", json_data['C005']['result']['msg'])
            return None

    except requests.exceptions.RequestException as e:
        print("API Request Error:", e)
        return None
    except json.JSONDecodeError as e:
        print("JSON Parsing Error:", e)
        return None
    except KeyError:
        print("잘못된 데이터 구조")
        return None

def is_refrigerated_or_frozen(product_info):
    """
    제품 정보가 냉장/냉동 제품인지 확인합니다.
    """
    if product_info and 'PRDLST_DCNM' in product_info:
        product_type = product_info['PRDLST_DCNM']
        return "냉장" in product_type or "냉동" in product_type
    return False
