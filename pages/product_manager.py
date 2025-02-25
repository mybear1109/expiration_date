import streamlit as st
from modules.database import create_tables, insert_product
from modules.api_client import get_product_info

def show():
    st.title("제품 관리")
    create_tables()  # 테이블 생성

    barcode = st.text_input("제품 바코드를 입력하세요:")
    if st.button("제품 정보 조회"):
        product = get_product_info(barcode)
        if product:
            st.write("제품 정보:", product)
            # DB에 저장 (예시)
            record = {
                "barcode": barcode,
                "product_name": product.get("PRDLST_NM", ""),
                "expiration_date": product.get("POG_DAYCNT", ""),
                "limit_day": product.get("LIMIT_DAY", ""),
                "manufacturer": product.get("BSSH_NM", "")
            }
            insert_product(record)
            st.success("제품 정보가 데이터베이스에 저장되었습니다.")
        else:
            st.error("제품 정보를 찾을 수 없습니다.")
