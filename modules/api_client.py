import requests
import os
import json
from urllib.parse import quote
import streamlit as st
from elasticsearch import Elasticsearch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

# FastAPI 애플리케이션 생성 (하나의 앱 인스턴스로 통합)
app = FastAPI()

# 데이터 모델 예시 (검색 API 용)
class Product(BaseModel):
    barcode: str
    product_name: str
    expiration_date: str

# SQLite 데이터베이스 연결 함수
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# SQLite 검색 엔드포인트: 바코드 또는 제품명으로 검색
@app.get("/search")
async def search_product(query: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM product_table WHERE barcode LIKE ? OR product_name LIKE ?",
        (f"%{query}%", f"%{query}%")
    )
    products = cursor.fetchall()
    conn.close()
    if not products:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")
    return [dict(product) for product in products]

# Elasticsearch 검색 엔드포인트
es = Elasticsearch("http://localhost:9200")

@app.get("/es-search")
async def es_search(query: str):
    res = es.search(index="products", body={
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["barcode", "product_name"]
            }
        }
    })
    return res["hits"]["hits"]

# 외부 API 호출을 위한 API 키 함수들
def get_B_API_KEY():
    """바코드연계제품정보 API용 키를 환경 변수 또는 st.secrets에서 가져옵니다."""
    return os.getenv("B_API_KEY") or st.secrets.get("B_API_KEY")

def get_H_API_KEY():
    """식품이력추적 관리품목 등록정보 조회 API용 키를 환경 변수 또는 st.secrets에서 가져옵니다."""
    return os.getenv("H_API_KEY") or st.secrets.get("H_API_KEY")

# 기본 URL 설정
BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"
BASE_HIST_URL = "http://apis.data.go.kr/1471000/FoodHistTrckMngPrdlstRegInfo"

def get_product_info(barcode: str):
    """
    바코드를 이용해 식품의약품안전처 API(C005)에서 제품 정보를 가져옵니다.
    요청 URL 예: {BASE_URL}/{B_API_KEY}/C005/json/1/5/BAR_CD={barcode}
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

def get_food_hist_info(barcode: str):
    """
    바코드를 이용해 식품이력추적 관리품목 등록정보 조회 API에서 제품 정보를 가져옵니다.
    요청 URL 예: {BASE_HIST_URL}/getFoodHistTrckMngPrdlstRegInfo?serviceKey={H_API_KEY}&pdtBarcd={barcode}&pageNo=1&numOfRows=5
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

        header = json_data.get("header", {})
        resultCode = header.get("resultCode", "")
        if resultCode == "00":
            body = json_data.get("body", {})
            items = body.get("items", [])
            if items and len(items) > 0:
                return items[0]  # 첫 번째 항목 반환 (필요에 따라 전체 리스트 반환)
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
{"C005":{"total_count":"0","RESULT":{"MSG":"해당하는 데이터가 없습니다.","CODE":"INFO-200"}}}