# main.py
from api_connector import get_product_info, is_refrigerated_or_frozen
from product_manager import ProductManager, Product
from notification_manager import send_notification
from recipe_recommender import recommend_recipes

def main():
    product_manager = ProductManager()

    while True:
        barcode = input("바코드를 입력하세요 (종료하려면 '종료' 입력): ")
        if barcode == "종료":
            break

        product_info = get_product_info(barcode)

        if product_info:
            if is_refrigerated_or_frozen(product_info):
                name = product_info['PRDLST_NM']
                product_type = product_info['PRDLST_DCNM']
                expiration_date = product_info['POG_DAYCNT']

                product = Product(barcode, name, product_type, expiration_date)
                product_manager.add_product(product)

                print("제품이 추가되었습니다.")
                print(product)


            else:
                print("냉장/냉동 제품이 아닙니다.")
        else:
            print("제품 정보를 가져오지 못했습니다.")

        expiring_products = product_manager.get_expiring_products()
        if expiring_products:
            for product in expiring_products:
                message = f"{product.name}의 유통기한이 {product.remaining_days()}일 남았습니다."
                send_notification(message)
                recipes = recommend_recipes(product.name)
                print("추천 레시피:", recipes)
        else:
            print("유통기한 임박 제품이 없습니다.")

if __name__ == "__main__":
    main()
