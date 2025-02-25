from typing import Dict, Any
from response_enum import ProductResponseKeys


class ResponseParser:
    """
    A utility class for parsing product response data from different sources.
    This class provides methods to extract relevant product details from responses
    obtained from Lykdat and SerpApi.
    """
    @staticmethod
    def parse_lykdat_product(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses a product response from Lykdat and extracts relevant product details.

        Args:
            response (Dict[str, Any]): The JSON response from Lykdat containing product details.

        Returns:
            Dict[str, Any]: A dictionary containing parsed product details including
            name, brand, price, currency, URL, and image URL.
        """
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
        """
        Parses a product response from SerpApi and extracts relevant product details.
        Additionally, it separates the currency symbol from the price.

        Args:
            response (Dict[str, Any]): The JSON response from SerpApi containing product details.

        Returns:
            Dict[str, Any]: A dictionary containing parsed product details including
            name, brand, price, currency, URL, and image URL.
        """
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
        Extracts the currency symbol and numeric price value from a price string.

        Args:
            price_with_symbol (str): The price string containing both the currency symbol and price value.

        Returns:
            tuple: A tuple containing the extracted currency symbol (str) and the numerical price (float).
                    If conversion fails, returns (-1.0) as the price.
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
