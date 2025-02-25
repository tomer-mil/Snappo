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
        price_with_symbol = response[ProductResponseKeys.PRICE.value.serpapi_key]
        currency, price = ResponseParser.separate_currency_symbol_and_price(price_with_symbol=price_with_symbol)
        parsed_product = {
            "name": response[ProductResponseKeys.NAME.value.serpapi_key],
            "brand": response[ProductResponseKeys.BRAND.value.serpapi_key],
            "price": price,
            "currency": currency,
            "url": response[ProductResponseKeys.PRODUCT_URL.value.serpapi_key],
            "image_url": response[ProductResponseKeys.IMAGE_URL.value.serpapi_key]
        }

        return parsed_product

    @staticmethod
    def separate_currency_symbol_and_price(price_with_symbol: str) -> (str, float):
        """
        Extract the currency symbol from the price string.
        """
        currency_symbol = ""
        clean_price = ""
        for char in price_with_symbol:
            if not char.isdigit() and char != ".":
                currency_symbol = char
            else:
                clean_price += char
        try:
            clean_price = float(clean_price)
        except ValueError:
            print(f"Error casting price to float: {price_with_symbol}")
            clean_price = -1.0
        return currency_symbol, clean_price
