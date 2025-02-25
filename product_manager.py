import streamlit as st

def show():
    st.title("📦 제품 관리")
    st.write("📋 현재 보관 중인 제품 목록:")

    products = [
        {"이름": "우유", "유통기한": "2024-02-20"},
        {"이름": "냉동 만두", "유통기한": "2024-02-25"},
        {"이름": "생선", "유통기한": "2024-02-22"}
    ]

    for product in products:
        st.write(f"📌 {product['이름']} - 유통기한: {product['유통기한']}")
