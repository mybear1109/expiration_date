import cv2
import numpy as np
from pyzbar.pyzbar import decode
import streamlit as st

def process_image(uploaded_file):
    """
    업로드된 이미지 파일에서 바코드 또는 이스터에그 식별코드를 추출하는 함수.
    지원 포맷: JPG, JPEG, PNG, BMP 등
    """
    allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
    file_name = getattr(uploaded_file, "name", "")
    ext = file_name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        st.error(f"지원되지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}")
        return None

    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if image is None:
        st.error("이미지 디코딩에 실패했습니다.")
        return None

    codes = decode(image)
    results = [code.data.decode("utf-8") for code in codes]
    return results
