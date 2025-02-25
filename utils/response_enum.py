from enum import Enum
from typing import NamedTuple


class ResponseMapping(NamedTuple):
    lykdat_key: str
    serpapi_key: str


class ProductResponseKeys(Enum):
    BRAND = ResponseMapping(
        lykdat_key="brand_name",
        serpapi_key="source"
    )
    PRICE = ResponseMapping(
        lykdat_key="price",
        serpapi_key="price"
    )
    CURRENCY = ResponseMapping(
        lykdat_key="currency",
        serpapi_key="alternative_price.currency"
    )
    PRODUCT_URL = ResponseMapping(
        lykdat_key="url",
        serpapi_key="product_link"
    )
    IMAGE_URL = ResponseMapping(
        lykdat_key="matching_image",
        serpapi_key="thumbnail"
    )
    NAME = ResponseMapping(
        lykdat_key="name",
        serpapi_key="title"
    )
