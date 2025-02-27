import os
import re
import io
import json
import base64
import requests
import streamlit as st
from urllib.parse import quote
from PIL import Image
from google.cloud import vision

#############################################
# 1) API 키 및 환경 변수 설정
#############################################
def get_api_key(key_name):
    """
    환경 변수 또는 Streamlit secrets에서 API 키를 가져옵니다.
    """
    key = os.getenv(key_name) or (st.secrets.get(key_name) if hasattr(st, "secrets") else None)
    if not key:
        st.warning(f"{key_name}가 설정되어 있지 않습니다.")
    return key

# Google Cloud Vision 클라이언트 초기화  
# 실제 서비스 계정 JSON 파일의 경로로 수정하세요.
try:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./secrets/your-vision-service-account.json"
    gcv_client = vision.ImageAnnotatorClient()
except Exception as e:
    st.warning(f"Google Cloud Vision 클라이언트 초기화 실패: {e}")
    gcv_client = None

#############################################
# 2) 식품이력추적 관리품목 등록정보 조회 (FoodHistTrckMngPrdlstRegInfo)
#############################################
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

#############################################
# 3) 유통바코드 조회 (I2570)
#############################################
BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"
def get_distribution_barcode_info(barcode: str, start_idx=1, end_idx=5):
    key = get_api_key("BARCODE_API_KEY")
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
    """
    바코드로 식품이력 및 유통바코드 정보를 모두 조회하여 반환합니다.
    """
    return {
        "food_hist_info": get_food_hist_info(barcode),
        "distribution_info": get_distribution_barcode_info(barcode)
    }

#############################################
# 4) 이미지 처리 및 텍스트/바코드/객체 인식 기능
#############################################
# pyzbar 사용 (바코드/QR 코드 인식)
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    _has_pyzbar = True
except ImportError:
    _has_pyzbar = False

# Transformers Object Detection (옵션)
try:
    from transformers import pipeline as transformers_pipeline
    _object_detection_pipeline = transformers_pipeline(
        "object-detection", 
        model="facebook/detr-resnet-50", 
        revision="1d5f47b", 
        use_fast=True
    )
except Exception as e:
    st.warning(f"Transformers object-detection 파이프라인 초기화 실패: {e}")
    _object_detection_pipeline = None

# Google Cloud Vision OCR (이미지 텍스트 인식) - images:annotate 사용
try:
    from google.cloud import vision
    _has_gcv = True
    _gcv_client = vision.ImageAnnotatorClient()
except Exception as e:
    st.warning(f"Google Cloud Vision 클라이언트 초기화 실패: {e}")
    _has_gcv = False
    _gcv_client = None

def process_barcode(file_bytes):
    """
    업로드된 이미지의 바이트 데이터를 기반으로 pyzbar를 이용해 바코드/QR 코드를 인식합니다.
    """
    if not _has_pyzbar:
        st.error("pyzbar 모듈이 설치되어 있지 않습니다.")
        return []
    try:
        image = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        st.error(f"이미지 열기 오류: {e}")
        return []
    results = pyzbar_decode(image)
    codes = []
    for r in results:
        try:
            code_str = r.data.decode("utf-8")
        except Exception:
            code_str = str(r.data)
        codes.append(code_str)
    return codes

def extract_barcode_from_text(file_bytes):
    return process_barcode(file_bytes)

def object_detection(image_path):
    """
    입력된 이미지 경로를 기반으로 Transformers의 object-detection 파이프라인을 사용해 객체를 검출합니다.
    """
    if _object_detection_pipeline is None:
        st.warning("Transformers object-detection 파이프라인을 사용할 수 없습니다.")
        return
    try:
        results = _object_detection_pipeline(image_path)
    except Exception as e:
        st.error(f"객체 검출 오류: {e}")
        return
    if not results:
        st.info("검출된 객체가 없습니다.")
        return
    st.write("검출된 객체:")
    for i, obj in enumerate(results, start=1):
        label = obj.get("label", "Unknown")
        score = obj.get("score", 0)
        bbox = obj.get("box", {})
        st.write(f"{i}. {label} (score={score:.2f}), bbox={bbox}")

def extract_text_from_image(image_path):
    """
    Google Cloud Vision API의 images:annotate 메소드를 이용해 
    입력된 이미지 경로의 텍스트를 추출합니다.
    parent 파라미터를 지정할 수 있도록 구성되어 있습니다.
    """
    if not _has_gcv or _gcv_client is None:
        st.warning("Google Cloud Vision을 사용할 수 없습니다.")
        return None
    try:
        with open(image_path, "rb") as f:
            content = f.read()
        # 이미지 콘텐츠를 Base64로 인코딩
        encoded_content = base64.b64encode(content).decode("UTF-8")
        # 요청 본문 구성
        request_body = {
            "requests": [
                {
                    "image": {
                        "content": encoded_content
                    },
                    "features": [
                        {"type": "TEXT_DETECTION"}
                    ]
                }
            ]
        }
        # parent 파라미터 (선택 사항)
        project_id = st.secrets.get("PROJECT_ID") if hasattr(st, "secrets") else None
        if project_id:
            request_body["parent"] = f"projects/{project_id}/locations/us"
        response = _gcv_client.batch_annotate_images(requests=request_body)
        if response.error.message:
            st.error(f"Vision API 오류: {response.error.message}")
            return None
        responses = response.responses
        if responses and len(responses) > 0:
            text_annotations = responses[0].text_annotations
            if text_annotations:
                return text_annotations[0].description
        return None
    except Exception as e:
        st.error(f"OCR 오류: {e}")
        return None

def extract_product_names(text, stopwords=None):
    """
    OCR로 추출된 텍스트에서 각 줄을 분리하고, 
    불용어(stopwords)가 포함되지 않은 줄들을 상품명으로 간주하여 리스트로 반환합니다.
    """
    if not text:
        return []
    if stopwords is None:
        stopwords = []
    lines = text.split('\n')
    product_list = []
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        if any(sw in clean_line for sw in stopwords):
            continue
        product_list.append(clean_line)
    return product_list

def detect_text_gcv(image_path):
    return extract_text_from_image(image_path)
