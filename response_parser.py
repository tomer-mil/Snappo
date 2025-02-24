from typing import Dict, Any
from response_enum import ProductResponseKeys

class ResponseParser:
    @staticmethod
    def parse_lykdat_product(response: Dict[str, Any]) -> Dict[str, Any]:

        parsed_product = {
            "name": response[ProductResponseKeys.NAME.value.lykdat_key],
            "brand": response[ProductResponseKeys.BRAND.value.lykdat_key],
            "price": response[ProductResponseKeys.PRICE.value.lykdat_key],
            "currency": response[ProductResponseKeys.CURRENCY.value.lykdat_key],
            "url": response[ProductResponseKeys.PRODUCT_URL.value.lykdat_key],
            "image_url": response[ProductResponseKeys.IMAGE_URL.value.lykdat_key]
        }

        return parsed_product

    @staticmethod
    def parse_serpapi_product(response: Dict[str, Any]) -> Dict[str, Any]:

        parsed_product = {
            "name": response[ProductResponseKeys.NAME.value.serpapi_key],
            "brand": response[ProductResponseKeys.BRAND.value.serpapi_key],
            "price": response[ProductResponseKeys.PRICE.value.serpapi_key],
            "currency": response.get("alternative_price", {}).get("currency"),  # Nested path
            "url": response[ProductResponseKeys.PRODUCT_URL.value.serpapi_key],
            "image_url": response[ProductResponseKeys.IMAGE_URL.value.serpapi_key]
        }

        return parsed_product
