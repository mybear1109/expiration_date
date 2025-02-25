# 제품 정보를 관리하고 유통기한을 처리하는 기능을 제공합니다.
import datetime

class Product:
    def __init__(self, barcode, name, product_type, expiration_date):
        self.barcode = barcode
        self.name = name
        self.product_type = product_type
        self.expiration_date = expiration_date #YYYYMMDD
        self.used = False

    def __str__(self):
         return f"바코드: {self.barcode}, 제품명: {self.name}, 유형: {self.product_type}, 유통기한: {self.expiration_date}, 사용여부: {self.used}"

    def remaining_days(self):
        today = datetime.date.today()
        expiration_date = datetime.datetime.strptime(self.expiration_date, '%Y%m%d').date()

        time_difference = expiration_date - today
        return time_difference.days


class ProductManager:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def remove_product(self, barcode):
        self.products = [product for product in self.products if product.barcode != barcode]

    def mark_as_used(self, barcode):
        for product in self.products:
            if product.barcode == barcode:
                product.used = True
                break

    def get_expiring_products(self, days=7):
        expiring_products = [product for product in self.products if product.remaining_days() <= days and not product.used]
        return expiring_products

    def get_product_by_barcode(self, barcode):
        for product in self.products:
            if product.barcode == barcode:
                return product
        return None
