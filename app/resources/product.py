from app.models import Product
from flask_restful import Resourece


class ProductList(Resource):
    def get(self):
        products = Product.query.all()  # SELECT * FROM product
