# 레시피 추천 기능을 제공합니다. (기본 구조만 제공)
def recommend_recipes(product_name, ingredients=None):
    """
    제품 이름과 재료를 기반으로 레시피를 추천합니다.
    (실제 레시피 추천 기능은 레시피 데이터베이스 또는 API 연동이 필요합니다.)
    """
    print(f"{product_name}을(를) 이용한 레시피를 추천합니다.")
    if ingredients:
        print(f"함께 사용할 수 있는 재료: {ingredients}")
    return ["김치찌개", "김치볶음밥"]  # 예시 레시피 목록
