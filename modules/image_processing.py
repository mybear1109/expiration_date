import cv2
import numpy as np
from pyzbar.pyzbar import decode
import streamlit as st
import re
import os
from google.cloud import vision

def process_image(uploaded_file):
    """
    업로드된 이미지 파일에서 바코드 또는 이스터에그 식별코드를 추출하는 함수.
    지원 포맷: JPG, JPEG, PNG, BMP 등
    """
    # 파일 확장자 확인 (업로드한 파일에 name 속성이 있는 경우)
    allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
    file_name = getattr(uploaded_file, "name", "")
    ext = file_name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        st.error(f"지원되지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}")
        return None

    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if image is None:
        st.error("이미지 디코딩에 실패했습니다.")
        return None

    # 바코드 또는 이스터에그 코드 디코딩
    codes = decode(image)
    results = [code.data.decode("utf-8") for code in codes]
    return results

# -------------------------------------------
# 1. 이미지 전처리 함수 (OpenCV 사용)
# -------------------------------------------
def preprocess_image(image_path):
    """
    주어진 이미지 파일 경로의 이미지를 읽어와 그레이스케일 변환과 히스토그램 균일화를 적용한 후 반환.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("이미지를 읽어오지 못했습니다.")
    
    # 그레이스케일 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 명암대비 스트레칭 (히스토그램 균일화)
    processed = cv2.equalizeHist(gray)
    
    # 추가 전처리 (예: 노이즈 제거) 필요 시 추가
    return processed

# -------------------------------------------
# 2. Google Cloud Vision API를 이용한 텍스트 인식 함수
# -------------------------------------------
def extract_text_from_image(image_path):
    """
    전처리된 이미지 파일을 Google Cloud Vision API를 이용해 텍스트를 추출하는 함수.
    """
    # 전처리된 이미지 저장 (임시 파일로 저장하여 사용)
    processed_image = preprocess_image(image_path)
    temp_image_path = "temp_processed.jpg"
    cv2.imwrite(temp_image_path, processed_image)
    
    # Vision API 클라이언트 생성
    client = vision.ImageAnnotatorClient()
    
    # 이미지 파일 읽기
    with open(temp_image_path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    
    # 텍스트 인식 요청
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        # 전체 인식된 텍스트 반환 (첫 번째 요소는 전체 텍스트)
        return texts[0].description
    else:
        return ""

# -------------------------------------------
# 3. 상품명 추출 함수 (불용어 제거 포함)
# -------------------------------------------
def extract_product_names(recognized_text, stopwords=None):
    """
    인식된 텍스트에서 '상품명'과 '합계' 사이의 영역을 파싱하여 상품명을 추출하는 함수.
    불용어(stopwords)가 포함된 라인은 제외.
    """
    if stopwords is None:
        stopwords = ['과세물품', '행사']  # 예시 불용어 목록
    
    # "상품명"과 "합계" 사이의 텍스트 추출 (줄바꿈 포함)
    match = re.search(r'상품명.*?합계', recognized_text, re.DOTALL)
    if not match:
        print("영수증 내 상품명 영역을 찾지 못했습니다.")
        return []
    
    product_section = match.group(0)
    lines = product_section.splitlines()
    
    # 첫 번째 줄은 보통 헤더("상품명 (단가) 수량 금액")이므로 제거
    product_lines = lines[1:]
    product_names = []
    for line in product_lines:
        # 불용어가 포함된 줄은 건너뜁니다.
        if any(stopword in line for stopword in stopwords):
            continue
        # 예시: 공백으로 분리하여 첫 번째 토큰을 상품명으로 가정
        tokens = line.split()
        if tokens:
            product_names.append(tokens[0])
    
    return product_names

# -------------------------------------------
# 4. 메인 실행 코드 (테스트용)
# -------------------------------------------
if __name__ == '__main__':
    # Google Cloud Vision API 자격증명 JSON 파일 경로 설정
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/credentials.json'
    
    # 처리할 영수증 이미지 파일 경로 (예: receipt.jpg)
    image_path = 'receipt.jpg'
    
    # 1단계: 텍스트 인식
    recognized_text = extract_text_from_image(image_path)
    print("인식된 텍스트:")
    print(recognized_text)
    
    # 2단계: 상품명 추출 (불용어 제거 포함)
    stopwords = ['과세물품', '행사']
    products = extract_product_names(recognized_text, stopwords)
    print("추출된 상품명:")
    for product in products:
        print("-", product)
