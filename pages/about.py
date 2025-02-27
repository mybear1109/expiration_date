import streamlit as st

def show():
    st.title("앱 정보")
    st.markdown("""
    **냉장고 관리 앱**
    
    이 앱은 영수증, 바코드, 이미지 인식을 통해 식재료 등록 및 관리, 유통기한 알림, 맞춤 레시피 추천 기능을 제공합니다.
    
    - **주요 기능**: 
      - 영수증 텍스트 인식 및 OCR
      - 바코드/QR 코드 스캔 및 제품 정보 조회
      - 객체 검출 및 이미지 분석
      - 맞춤 레시피 추천
    - **기술 스택**: Streamlit, OpenCV, Google Cloud Vision, Transformers, pyzbar, SQLite, Elasticsearch 등
    """)
