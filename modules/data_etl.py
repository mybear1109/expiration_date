import pandas as pd
import os
import json
import api_client  # 위에서 작성한 api_client 모듈 사용
import streamlit as st

def collect_and_transform_data(barcode_list):
    """
    주어진 바코드 리스트에 대해 API에서 데이터를 수집한 후, 원하는 필드만 추출하여 DataFrame으로 반환.
    """
    records = []
    for barcode in barcode_list:
        product_info = api_client.get_product_info(barcode)
        hist_info = api_client.get_food_hist_info(barcode)
        if product_info:
            record = {
                "barcode": barcode,
                "product_name": product_info.get("PRDLST_NM"),
                "expiration_date": product_info.get("POG_DAYCNT"),  # 예시: 소비기한
                "limit_day": product_info.get("LIMIT_DAY"),
                "manufacturer": product_info.get("BSSH_NM")
            }
            # 필요에 따라 hist_info의 데이터 병합
            if hist_info:
                record["history_info"] = hist_info
            records.append(record)
    df = pd.DataFrame(records)
    return df

def save_data_to_csv(df, filename="data/expiration_data.csv"):
    """
    DataFrame 데이터를 CSV 파일로 저장.
    """
    os.makedirs("data", exist_ok=True)
    df.to_csv(filename, index=False)
    st.success(f"데이터가 {filename}에 저장되었습니다.")
