import json
from io import BytesIO
import requests
from PIL import Image
from currency_symbols import CurrencySymbols

from utils.response_parser import ResponseParser

class Product:
    name: str
    price: float
    currency: str
    url: str
    image_url: str
    image_data: BytesIO
    brand: str
    source_api: str

    def __init__(self, response, source: str):
        self.source_api = source
        parsed_response = ResponseParser.parse_lykdat_product(
            response) if source == "lykdat" else ResponseParser.parse_serpapi_product(response)
        self.price = parsed_response.get("price", -1)
        self.url = parsed_response.get("url", "")

        image_url = parsed_response.get("image_url", "")
        self.image_url = image_url
        self.image_data = self.get_image_data_from_url(url=image_url)

        self.brand = parsed_response.get("brand", "")
        self.name = parsed_response.get("name", "")

        if source == "lykdat":
            try:
                self.currency = CurrencySymbols.get_symbol(currency=parsed_response.get("currency", ""))
            except KeyError:
                self.currency = "$"
        else:
            self.currency = parsed_response.get("currency", "")

    def __repr__(self):
        return str(self.to_dict())

    @staticmethod
    def get_image_data_from_url(url: str):
        """
        Returns the image content as a BytesIO object.
        """
        try:
            response = requests.get(url, timeout=8)
            if response.status_code != 200:
                print(f"Failed to download image. Status code:\n\t{response.status_code}")
                return None

            image_data = BytesIO(response.content)
            try:
                img = Image.open(image_data)
                img.verify()
                image_data.seek(0)
                return image_data
            except Exception as e:
                print(f"Downloaded content is not an image file: {str(e)}")
                return None
        except Exception as e:
            print(f"Failed to get image from url when initializing Product object: {str(e)}")
            return None

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "url": self.url,
            "image_url": self.image_url,
            "image_data": self.image_data,
            "brand": self.brand,
            "source_api": self.source_api
        }

    def to_json(self):
        return json.dumps(self.to_dict())
