import json
from io import BytesIO
import requests
from PIL import Image

from core.models.product import Product
from utils.constants import LykdatAPI as Constants
from utils.env_manager import get_api_key, LYKDAT_API_KEY_ENV


# Get API key from environment variables
def get_lykdat_api_key():
    return get_api_key(LYKDAT_API_KEY_ENV)

def convert_pil_to_bytes(pil_image):
    """
    Converts a PIL image to a byte array in JPEG format.
    """
    img_byte_arr = BytesIO()
    pil_image.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()


def build_lykdat_params(image):
    """
    Builds the parameters required for the Lykdat API request.
    """
    payload = {
        "api_key": get_lykdat_api_key()
    }
    files = [
        ('image', ('image.jpg', image, 'image/jpeg'))
    ]
    return payload, files


def call_lykdat_global_search(image):
    """
    Sends an image to the Lykdat global search API and returns the JSON response.
    """
    payload, files = build_lykdat_params(image=image)
    response = None

    try:
        response = requests.post(Constants.LYKDAT_GLOBAL_SEARCH_URL, data=payload, files=files)
        response.raise_for_status()  # Raise exception for bad status codes

    except requests.exceptions.RequestException as e:
        print(f"{Constants.API_REQUEST_ERROR_MESSAGE} {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

    return response.json()


def call_lykdat_global_search_mock(image):
    with open(Constants.GLOBAL_SEARCH_MOCK_RESPONSE_PATH, 'r') as f:
        return json.load(f)


def parse_lykdat_response(response_json, limit=5) -> list[Product]:
    """
    Parses the response from Lykdat API and extracts product information.
    """
    lykdat_result_products = response_json["data"]["result_groups"][0]["similar_products"][:limit]
    return convert_to_product_objects_list(products=lykdat_result_products)


def convert_to_product_objects_list(products: dict) -> list[Product]:
    """
    Converts raw product data from the Lykdat API response into a list of Product objects.
    """
    parsed_results = []

    for product in products:
        parsed_result = Product(response=product, source="lykdat")
        parsed_results.append(parsed_result)

    return parsed_results


def search_lykdat(image: Image, limit=5):
    """
    Conducts a Lykdat API search using a given image and returns parsed product results.
    """
    img_byte_arr = convert_pil_to_bytes(image)

    lykdat_response = call_lykdat_global_search(image=img_byte_arr)
    parsed_response = parse_lykdat_response(lykdat_response, limit=limit)

    return parsed_response


def search_images_list(images_list):
    """
    Searches multiple images using the Lykdat API and returns results for each.
    """
    results = []

    for img in images_list:
        results.append(search_lykdat(img["image"]))

    return results
