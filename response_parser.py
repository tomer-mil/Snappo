from typing import Dict, Any, List
from response_enum import ProductResponseKeys

class ResponseParser:
    @staticmethod
    def parse_lykdat_product(response: Dict[str, Any]) -> Dict[str, Any]:
        # product = response["data"]["result_groups"][0]["similar_products"][index]

        parsed_product = {
            "brand": response[ProductResponseKeys.BRAND.value.lykdat_key],
            "price": response[ProductResponseKeys.PRICE.value.lykdat_key],
            "currency": response[ProductResponseKeys.CURRENCY.value.lykdat_key],
            "url": response[ProductResponseKeys.PRODUCT_URL.value.lykdat_key],
            "image_url": response[ProductResponseKeys.IMAGE_URL.value.lykdat_key],
            "name": response[ProductResponseKeys.NAME.value.lykdat_key]
        }

        return parsed_product

    @staticmethod
    def parse_serpapi_product(response: Dict[str, Any]) -> Dict[str, Any]:
        # products = response.get("shopping_results", [])
        # product = products[index]

        parsed_product = {
            "brand": response[ProductResponseKeys.BRAND.value.serpapi_key],
            "price": response[ProductResponseKeys.PRICE.value.serpapi_key],
            "currency": response.get("alternative_price", {}).get("currency"),  # Nested path
            "url": response[ProductResponseKeys.PRODUCT_URL.value.serpapi_key],
            "image_url": response[ProductResponseKeys.IMAGE_URL.value.serpapi_key]
        }

        return parsed_product
