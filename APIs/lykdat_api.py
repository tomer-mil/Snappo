import json
import os
from datetime import datetime
from io import BytesIO
import requests
from Product import Product

LYKDAT_URL = "https://cloudapi.lykdat.com/v1/global/search"
API_KEY = "58c2f99e908650cf4b6c35f4cdd7131e52ae6e6ab151fc8459a16a5fa9c3b33b"


def convert_pil_to_bytes(pil_image):
    img_byte_arr = BytesIO()
    pil_image.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()


def call_lykdat_global_search(image):
    payload = {
        "api_key": API_KEY
    }

    files = [
        ('image', ('image.jpg', image, 'image/jpeg'))
    ]

    response = None

    try:
        response = requests.post(LYKDAT_URL, data=payload, files=files)
        response.raise_for_status()  # Raise exception for bad status codes

    except requests.exceptions.RequestException as e:
        print(f"API request error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

    return response.json()


def call_lykdat_global_search_mock(image):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(ROOT_DIR, 'mock_responses\\lykdat_results_raw_20250223_155426.json'), 'r') as f:
        return json.load(f)


def parse_lykdat_response(response_json):
    # Parse the response from LykDat API
    lykdat_result_products = response_json["data"]["result_groups"][0]["similar_products"]
    return parse_response_product(products=lykdat_result_products)


def parse_response_product(products):
    parsed_results = []

    for product in products:
        parsed_result = Product(response=product, source="lykdat")
        # parsed_result = {
        #     "brand": product["brand_name"],
        #     "currency": product["currency"],
        #     "image": product["matching_image"],
        #     "price": product["price"],
        #     "url": product["url"]
        # }
        parsed_results.append(parsed_result)

    return parsed_results


def search_lykdat(pil_image):
    img_byte_arr = convert_pil_to_bytes(pil_image)

    # TODO: Don't forget to change back to original call! lykdat_response = call_lykdat_global_search(image=img_byte_arr)

    lykdat_response = call_lykdat_global_search_mock(image=img_byte_arr)
    parsed_response = parse_lykdat_response(lykdat_response)

    json_response = [product.to_json() for product in parsed_response]

    return parsed_response


def search_images_list(images_list):
    results = []

    for img in images_list:
        results.append(search_lykdat(img["image"]))

    return results
