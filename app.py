import streamlit as st
import barcode_scanner
import product_manager
import notification_manager
import recipe_recommender
from home import show as home_show 
from about import show as about_show 

# 📌 세션 상태 초기화 (기본값: 홈)
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# 📌 페이지 변경 함수
def switch_page(page):
    st.session_state.current_page = page

# 📌 네비게이션 버튼 UI
st.markdown("""
    <style>
        .nav-buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        .stButton>button {
            font-size: 16px;
            padding: 10px 20px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    if st.button("🏠 홈"):
        switch_page("Home")
with col2:
    if st.button("📸 바코드 스캔"):
        switch_page("Barcode Scanner")
with col3:
    if st.button("📦 제품 관리"):
        switch_page("Product Manager")
with col4:
    if st.button("🔔 알림"):
        switch_page("Notifications")
with col5:
    if st.button("레시피 추천"):
        switch_page("Recipe Recommender")       
with col6:
    if st.button("ℹ️ 정보"):
        switch_page("About")

st.markdown('</div>', unsafe_allow_html=True)

# 📌 현재 선택된 페이지 실행
if st.session_state.current_page == "Home":
    home_show()  # 홈 페이지 함수 호출
elif st.session_state.current_page == "Barcode Scanner":
    barcode_scanner.show()  # 바코드 스캔 페이지 함수 호출
elif st.session_state.current_page == "Product Manager":
    product_manager.show()  # 제품 관리 페이지 함수 호출
elif st.session_state.current_page == "Notifications":
    notification_manager.show()  # 알림 페이지 함수 호출
elif st.session_state.current_page == "Recipe Recommender":
    # recipe_recommender 모듈에 show() 또는 show_page() 함수가 있는지 확인 후 호출
    if hasattr(recipe_recommender, "show"):
        recipe_recommender.show()
    elif hasattr(recipe_recommender, "show_page"):
        recipe_recommender.show_page()
    else:
        st.error("recipe_recommender 모듈에 표시할 함수가 없습니다. 해당 모듈에 show() 함수를 추가해주세요.")
elif st.session_state.current_page == "About":
    about_show()  # 정보 페이지 함수 호출
