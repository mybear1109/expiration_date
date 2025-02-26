# app.py
import streamlit as st

st.set_page_config(page_title="냉장고 관리 앱", page_icon="🥦", layout="wide")

import pages.home as home
import pages.barcode_scanner as barcode_scanner
import pages.product_manager as product_manager
import pages.notifications as notifications
import pages.recipe_recommender as recipe_recommender
import pages.about as about
import pages.product_manager as product_manager


if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

def switch_page(page_name):
    st.session_state.current_page = page_name

cols = st.columns(6)
with cols[0]:
    if st.button("🏠 홈"):
        switch_page("Home")
with cols[1]:
    if st.button("📸 스캐너"):
        switch_page("Scanner")
with cols[2]:
    if st.button("📦 제품관리"):
        switch_page("Manager")
with cols[3]:
    if st.button("🔔 알림"):
        switch_page("Notifications")
with cols[4]:
    if st.button("🍳 레시피"):
        switch_page("Recipe")
with cols[5]:
    if st.button("ℹ️ 정보"):
        switch_page("About")

if st.session_state.current_page == "Home":
    home.show()
elif st.session_state.current_page == "Scanner":
    barcode_scanner.show()
elif st.session_state.current_page == "Manager":
    product_manager.show()
elif st.session_state.current_page == "Notifications":
    notifications.show()
elif st.session_state.current_page == "Recipe":
    recipe_recommender.show()
elif st.session_state.current_page == "About":
    about.show()
