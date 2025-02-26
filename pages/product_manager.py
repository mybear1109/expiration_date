# pages/product_manager.py

import streamlit as st
from modules.external_apis import fetch_all_product_info

def show():
    st.title("제품 관리 페이지")
    
    # 바코드 입력
    barcode = st.text_input("조회할 바코드:")
    
    if st.button("조회"):
        if not barcode:
            st.warning("바코드를 입력하세요.")
        else:
            # API 호출하여 제품 정보를 조회
            result = fetch_all_product_info(barcode)
            st.write("조회 결과:")
            st.json(result)
