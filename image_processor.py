import cv2
import numpy as np
from pyzbar.pyzbar import decode

def process_image(uploaded_file):
    """
    업로드된 이미지 파일에서 바코드를 인식하여 반환하는 함수
    지원 포맷: JPG, JPEG, PNG, BMP 등
    """
    # 파일 확장자 검사 (업로드한 파일에 name 속성이 있을 경우)
    allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
    file_name = getattr(uploaded_file, "name", None)
    if file_name:
        ext = file_name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise ValueError(
                f"지원되지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}"
            )
    
    # 업로드된 파일을 바이트 배열로 변환 후 이미지 디코딩
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("이미지 디코딩에 실패했습니다. 파일이 손상되었거나 지원되지 않는 포맷일 수 있습니다.")
    
    # 바코드 감지
    detected_barcodes = decode(image)
    
    # 첫 번째 감지된 바코드 데이터 반환
    if detected_barcodes:
        for barcode in detected_barcodes:
            barcode_data = barcode.data.decode("utf-8")
            return barcode_data
    
    # 바코드 인식 실패 시 None 반환
    return None
