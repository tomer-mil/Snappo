import re

from APIs.serp_api import search_product


def replace_product_with_serp(product):
    if not is_url_valid(product.image_url):
        product = search_product(product.title, limit=1)[0]
    return product


# check if product image is valid
def is_url_valid(url):
    image_extensions = re.compile(r"\.(jpeg|jpg|png|gif|bmp|tiff|webp)$", re.IGNORECASE)
    return bool(image_extensions.search(url))
