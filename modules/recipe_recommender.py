import json
import os
import streamlit as st
from huggingface_hub import InferenceClient
from typing import List, Dict

# 올바른 모듈에서 유통기한 임박 재료 정보를 받아옵니다.
# 임시로 유통기한 임박 재료 정보를 반환하는 함수 정의 (추후 다른 모듈에서 정보를 받아오도록 수정 가능)
def get_expiring_ingredients() -> List[str]:
    # 실제 구현 시, DB 또는 다른 모듈에서 데이터를 가져오도록 구현할 수 있습니다.
    return ["우유", "계란", "채소"]


def get_huggingface_token():
    """환경 변수 또는 Streamlit secrets에서 Hugging Face API 토큰을 가져옵니다."""
    return st.secrets.get("HUGGINGFACE_API_TOKEN")

def generate_text_via_api(prompt: str, model_name: str = "google/gemma-2-9b-it"):
    """Hugging Face API를 사용하여 텍스트를 생성합니다."""
    token = get_huggingface_token()
    client = InferenceClient(model=model_name, api_key=token)
    response = client.text_generation(prompt=prompt)
    return response

def get_expiration_recipe_recommendation(expiring_ingredients: List[str], additional_info: Dict[str, str] = {}) -> str:
    """
    냉장고에 있는 유통기한 임박 재료들을 활용하여 7일 분량의 음식 레시피를 추천합니다.
    - expiring_ingredients: 유통기한이 임박한 재료들의 목록
    - additional_info: 추가적인 정보 (예: "식이 제한": "저탄수화물", "선호 음식": "한식")
    프롬프트를 구성하여 한국어로 된 레시피 추천을 생성합니다.
    """
    ingredients_text = ", ".join(expiring_ingredients)
    prompt = (
        f"냉장고에 있는 재료 중 유통기한이 임박한 재료가 있습니다: {ingredients_text}.\n"
        "이 재료들을 활용하여 빠르게 만들 수 있는 음식 레시피를 7일 분량 추천해 주세요.\n"
        "각 요일별로 아침, 점심, 저녁 메뉴를 구성하고, 각 식단에는 사용 재료, 조리 방법, 예상 칼로리, 조리 시간, 난이도, 영양 정보 등을 포함하세요.\n"
        "레시피는 한국어로 작성되어야 하며, 유통기한 임박 재료의 낭비를 최소화할 수 있도록 효율적인 메뉴를 제안해 주세요.\n"
    )
    
    if additional_info:
        for key, value in additional_info.items():
            prompt += f"- {key}: {value}\n"
    
    return generate_text_via_api(prompt)

def show():
    st.title("유통기한 임박 재료를 활용한 레시피 추천")
    
    # 다른 모듈에서 유통기한 임박 재료 정보를 가져옵니다.
    expiring_ingredients = get_expiring_ingredients()
    if not expiring_ingredients:
        st.error("현재 유통기한 임박 재료 정보가 없습니다.")
    else:
        st.subheader("현재 유통기한 임박 재료")
        st.write(", ".join(expiring_ingredients))
    
    additional_info_json = st.text_area(
        "추가 정보 (JSON 형식, 예: {\"식이 제한\": \"저탄수화물\", \"선호 음식\": \"한식\"}):",
        value="{}"
    )
    
    try:
        additional_info = json.loads(additional_info_json)
    except json.JSONDecodeError:
        st.error("추가 정보는 올바른 JSON 형식이어야 합니다.")
        additional_info = {}
    
    if st.button("레시피 추천 받기"):
        if expiring_ingredients:
            recommendation = get_expiration_recipe_recommendation(expiring_ingredients, additional_info)
            st.subheader("레시피 추천 결과")
            st.write(recommendation)
        else:
            st.error("유통기한 임박 재료 정보를 확인할 수 없습니다.")
