import streamlit as st
import cv2
import numpy as np
import re
from modules.external_apis import (
    extract_text_from_image,
    fetch_all_product_info,
    object_detection
)

def extract_distribution_barcode(recognized_text):
    """
    OCR로 인식된 텍스트에서 13자리 숫자를 추출합니다.
    이 13자리 숫자가 제품 유통바코드라고 가정합니다.
    """
    pattern = r'\b\d{13}\b'
    matches = re.findall(pattern, recognized_text)
    if matches:
        return matches[0]
    return None

def show():
    st.title("영수증 텍스트 기반 분석 및 제품 검색")
    
    # 이미지 업로드
    uploaded_file = st.file_uploader("이미지 파일을 업로드하세요.", type=["jpg", "jpeg", "png", "bmp"])
    
    if uploaded_file:
        # 업로드된 이미지 표시 (use_column_width 사용)
        file_bytes = uploaded_file.read()
        st.image(file_bytes, caption="업로드된 이미지", use_column_width=True)
        
        # 업로드된 파일 포인터 재설정 후 임시 파일로 저장
        uploaded_file.seek(0)
        temp_path = "temp_uploaded.jpg"
        with open(temp_path, "wb") as f:
            f.write(file_bytes)
        
        # OCR (텍스트 인식)
        st.subheader("OCR (텍스트 인식) 결과")
        recognized_text = extract_text_from_image(temp_path)
        if recognized_text:
            st.text(recognized_text)
            
            # 13자리 유통바코드 추출
            distribution_barcode = extract_distribution_barcode(recognized_text)
            if distribution_barcode:
                st.success(f"추출된 유통바코드: {distribution_barcode}")
                # 제품 정보 조회 (식품이력 및 유통바코드 정보)
                product_info = fetch_all_product_info(distribution_barcode)
                if product_info:
                    st.subheader("제품 정보")
                    st.json(product_info)
                else:
                    st.error("제품 정보를 찾을 수 없습니다.")
            else:
                st.error("인식된 텍스트에서 13자리 유통바코드를 추출하지 못했습니다.")
        else:
            st.info("텍스트 인식에 실패했습니다.")
        
        # 객체 검출 (이미지 내 객체를 시각화)
        st.subheader("객체 검출 결과")
        try:
            object_detection(temp_path)
        except Exception as e:
            st.error(f"객체 검출 중 오류 발생: {e}")
    else:
        st.info("분석할 이미지를 업로드 해주세요.")

