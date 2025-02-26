import os
import re
import io
import json
import requests
import streamlit as st
from urllib.parse import quote
from PIL import Image
from google.cloud import vision

# API 키 및 환경 변수 설정
def get_api_key(key_name):
    """환경 변수 또는 Streamlit secrets에서 API 키를 가져옵니다."""
    key = os.getenv(key_name) or (st.secrets.get(key_name) if hasattr(st, "secrets") else None)
    if not key:
        st.warning(f"{key_name}가 설정되어 있지 않습니다.")
    return key

# Google Cloud Vision 클라이언트 초기화
try:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".streamlit/secrets.toml"
    gcv_client = vision.ImageAnnotatorClient()
except Exception as e:
    st.warning(f"Google Cloud Vision 클라이언트 초기화 실패: {e}")
    gcv_client = None

# 식품이력추적 관리품목 등록정보 조회
BASE_HIST_URL = "http://apis.data.go.kr/1471000/FoodHistTrckMngPrdlstRegInfo"
def get_food_hist_info(barcode: str, start_idx=1, end_idx=5):
    key = get_api_key("FOOD_API_KEY")
    if not key:
        return None
    url = f"{BASE_HIST_URL}/getFoodHistTrckMngPrdlstRegInfo"
    params = {
        "serviceKey": key,
        "pdtBarcd": barcode,
        "pageNo": start_idx,
        "numOfRows": end_idx
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        header = data.get("header", {})
        if header.get("resultCode") == "00":
            return data.get("body", {}).get("items", [])
        else:
            st.error(f"식품이력추적 API 오류: {header.get('resultMsg', '알 수 없는 오류')}")
            return None
    except Exception as e:
        st.error(f"식품이력추적 API 호출 오류: {e}")
        return None

# 유통바코드 조회
BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"
def get_distribution_barcode_info(barcode: str, start_idx=1, end_idx=5):
    key = get_api_key("FOOD_API_KEY")
    if not key:
        return None
    service_id = "I2570"
    data_type = "json"
    url = f"{BASE_URL}/{quote(key)}/{service_id}/{data_type}/{start_idx}/{end_idx}?BRCD_NO={barcode}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if service_id in data:
            meta = data[service_id]
            result = meta.get("RESULT", {})
            if result.get("CODE") == "INFO-000":
                return meta.get("row", [])
            elif result.get("CODE") == "INFO-200":
                st.info("해당 바코드 정보가 없습니다.")
            else:
                st.error(f"유통바코드 API 오류: {result.get('MSG', '알 수 없는 오류')}")
        else:
            st.error("유통바코드 API 응답 구조가 예상과 다릅니다.")
        return None
    except Exception as e:
        st.error(f"유통바코드 API 호출 오류: {e}")
        return None

def fetch_all_product_info(barcode: str):
    """바코드로 식품이력 및 유통바코드 정보를 모두 조회하여 반환합니다."""
    return {
        "food_hist_info": get_food_hist_info(barcode),
        "distribution_info": get_distribution_barcode_info(barcode)
    }

# 이미지 처리 및 텍스트 추출
def process_image(image_bytes):
    """이미지에서 바코드, 객체, 텍스트를 추출합니다."""
    results = {
        "barcodes": [],
        "objects": [],
        "text": None
    }
    
    # 바코드 추출
    try:
        from pyzbar.pyzbar import decode as pyzbar_decode
        image = Image.open(io.BytesIO(image_bytes))
        barcodes = pyzbar_decode(image)
        results["barcodes"] = [b.data.decode("utf-8") for b in barcodes]
    except ImportError:
        st.warning("pyzbar 모듈이 설치되어 있지 않아 바코드 인식을 수행할 수 없습니다.")
    except Exception as e:
        st.error(f"바코드 인식 중 오류 발생: {e}")

    # Google Cloud Vision API를 사용한 텍스트 추출
    if gcv_client:
        try:
            image = vision.Image(content=image_bytes)
            response = gcv_client.text_detection(image=image)
            if response.error.message:
                st.error(f"Vision API 오류: {response.error.message}")
            else:
                texts = response.text_annotations
                if texts:
                    results["text"] = texts[0].description
        except Exception as e:
            st.error(f"텍스트 추출 중 오류 발생: {e}")

    return results

def extract_product_names(text, stopwords=None):
    """OCR로 추출된 텍스트에서 상품명을 추출합니다."""
    if not text:
        return []
    if stopwords is None:
        stopwords = []
    lines = text.split('\n')
    return [line.strip() for line in lines if line.strip() and not any(sw in line for sw in stopwords)]

# Streamlit 앱에서 사용할 함수들
def upload_and_process_image():
    uploaded_file = st.file_uploader("이미지 파일을 업로드하세요", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="업로드된 이미지", use_column_width=True)
        results = process_image(image_bytes)
        
        if results["barcodes"]:
            st.subheader("인식된 바코드")
            for barcode in results["barcodes"]:
                st.write(barcode)
                product_info = fetch_all_product_info(barcode)
                if product_info["food_hist_info"] or product_info["distribution_info"]:
                    st.json(product_info)
                else:
                    st.warning("해당 바코드에 대한 제품 정보를 찾을 수 없습니다.")
        
        if results["text"]:
            st.subheader("추출된 텍스트")
            st.text(results["text"])
            
            product_names = extract_product_names(results["text"])
            if product_names:
                st.subheader("추출된 상품명")
                for name in product_names:
                    st.write(name)
