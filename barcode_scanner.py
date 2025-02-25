import streamlit as st
from api_connector import get_product_info, is_refrigerated_or_frozen
from image_processor import process_image

def show():
    st.title("📸 바코드 스캔")

    # 바코드 입력 방식 선택
    option = st.radio("바코드 입력 방법을 선택하세요:", ["📷 이미지 업로드", "⌨️ 바코드 직접 입력"])

    barcode = None  # 초기 바코드 값 설정

    if option == "📷 이미지 업로드":
        uploaded_file = st.file_uploader("바코드가 포함된 이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            barcode = process_image(uploaded_file)
            if barcode:
                st.success(f"✅ 바코드 인식 성공: `{barcode}`")
            else:
                st.error("❌ 바코드를 인식하지 못했습니다. 다시 시도해주세요.")

    elif option == "⌨️ 바코드 직접 입력":
        barcode = st.text_input("바코드를 입력하세요:")

    if st.button("🔍 검색"):
        if barcode:
            product_info = get_product_info(barcode)
            if product_info:
                st.write("✅ 제품 정보:")
                st.json(product_info)
                if is_refrigerated_or_frozen(product_info):
                    st.warning("🚨 냉장/냉동 보관이 필요한 제품입니다.")
                else:
                    st.success("✅ 일반 제품입니다.")
            else:
                st.error("❌ 제품 정보를 찾을 수 없습니다.")
        else:
            st.warning("⚠️ 바코드를 입력하세요.")
