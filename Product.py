import json

from response_parser import ResponseParser
from response_enum import ProductResponseKeys as PRK

class Product:

	price: float
	currency: str
	url: str
	image_url: str
	brand: str
	source_api: str


	def __init__(self, response, source: str):
		self.source_api = source
		parsed_response = ResponseParser.parse_lykdat_product(response) if source == "lykdat" else ResponseParser.parse_serpapi_product(response)
		self.price = parsed_response.get("price", -1)
		self.url = parsed_response.get("url", "")
		self.image_url = parsed_response.get("image_url", "")
		self.currency = parsed_response.get("currency", "")
		self.brand = parsed_response.get("brand", "")

		# match source:
		# 	# TODO: Change attribute `set` to match the structure in `response_parser`
		# 	case "lykdat":
		# 		parsed_response = ResponseParser.parse_lykdat_product(response)
		# 		self.price = parsed_response.get(PRK.PRICE.value.lykdat_key)
		# 		self.url = parsed_response.get(PRK.PRODUCT_URL.value.lykdat_key)
		# 		self.image_url = parsed_response.get(PRK.IMAGE_URL.value.lykdat_key)
		# 		self.currency = parsed_response.get(PRK.CURRENCY.value.lykdat_key)
		# 		self.brand = parsed_response.get(PRK.BRAND.value.lykdat_key)
		# 	case "serpapi":
		# 		parsed_response = ResponseParser.parse_serpapi_product(response)
		# 		self.price = parsed_response.get(PRK.PRICE.value.serpapi_key)
		# 		self.url = parsed_response.get(PRK.PRODUCT_URL.value.serpapi_key)
		# 		self.image_url = parsed_response.get(PRK.IMAGE_URL.value.serpapi_key)
		# 		self.currency = parsed_response.get("alternative_price", {}).get("currency")
		# 		self.brand = parsed_response.get(PRK.BRAND.value.serpapi_key)
		# 	case _:
		# 		raise ValueError("Invalid source API")


	def __repr__(self):
		return str(self.to_dict())

	def to_dict(self):
		return {
			"price": self.price,
			"currency": self.currency,
			"url": self.url,
			"image_url": self.image_url,
			"brand": self.brand,
			"source_api": self.source_api
		}

	def to_json(self):
		return json.dumps(self.to_dict())

