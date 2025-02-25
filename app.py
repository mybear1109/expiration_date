import streamlit as st
from pages import home, barcode_scanner, product_manager, notifications, about
from modules import recipe_recommender

# 세션 상태 초기화 (기본값: 홈)
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# 페이지 전환 함수
def switch_page(page):
    st.session_state.current_page = page

# 네비게이션 버튼 UI (간단한 CSS 포함)
st.markdown("""
    <style>
        .nav-buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        .stButton > button {
            font-size: 16px;
            padding: 10px 20px;
        }
    </style>
    <div class="nav-buttons">
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    if st.button("🏠 홈", key="home_button"):
        switch_page("Home")
with col2:
    if st.button("📸 바코드 스캔", key="barcode_button"):
        switch_page("Barcode Scanner")
with col3:
    if st.button("📦 제품 관리", key="product_button"):
        switch_page("Product Manager")
with col4:
    if st.button("🔔 알림", key="notifications_button"):
        switch_page("Notifications")
with col5:
    if st.button("🍳 레시피 추천", key="recipe_button"):
        switch_page("Recipe Recommender")
with col6:
    if st.button("ℹ️ 정보", key="about_button"):
        switch_page("About")

# 선택된 페이지 표시
if st.session_state.current_page == "Home":
    home.show()
elif st.session_state.current_page == "Barcode Scanner":
    barcode_scanner.show()
elif st.session_state.current_page == "Product Manager":
    product_manager.show()
elif st.session_state.current_page == "Notifications":
    notifications.show()
elif st.session_state.current_page == "Recipe Recommender":
    recipe_recommender.show()
elif st.session_state.current_page == "About":
    about.show()

