import json
from currency_symbols import CurrencySymbols

from response_parser import ResponseParser
from response_enum import ProductResponseKeys as PRK

class Product:

	name: str
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

	def to_dict(self):
		return {
			"name": self.name,
			"price": self.price,
			"currency": self.currency,
			"url": self.url,
			"image_url": self.image_url,
			"brand": self.brand,
			"source_api": self.source_api
		}

	def to_json(self):
		return json.dumps(self.to_dict())

