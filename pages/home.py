import streamlit as st

def show():
    st.title("냉장고 관리 애플리케이션")
    st.markdown("""
    이 애플리케이션은 영수증과 바코드 스캔을 통해 식재료를 등록하고,
    유통기한 관리 및 맞춤 레시피 추천 기능을 제공합니다.
    """)
