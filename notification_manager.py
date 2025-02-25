import streamlit as st

def show():
    st.title("🔔 유통기한 알림")
    st.write("📢 유통기한이 임박한 제품을 확인하세요.")

    notifications = [
        {"제품명": "우유", "유통기한": "2024-02-20"},
        {"제품명": "냉동 만두", "유통기한": "2024-02-25"},
        {"제품명": "생선", "유통기한": "2024-02-22"}
    ]

    for item in notifications:
        st.warning(f"⚠️ {item['제품명']} - 유통기한: {item['유통기한']}")
