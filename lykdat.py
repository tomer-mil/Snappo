from io import BytesIO
import requests

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


def parse_lykdat_response(response_json):
    # Parse the response from LykDat API
    lykdat_result_products = response_json["data"]["result_groups"][0]["similar_products"]

    return parse_response_product(products=lykdat_result_products)


def parse_response_product(products):
    parsed_results = []

    for product in products:
        parsed_result = {
            "brand": product["brand_name"],
            "currency": product["currency"],
            "image": product["matching_image"],
            "price": product["price"],
            "url": product["url"]
        }
        parsed_results.append(parsed_result)

    return parsed_results


def search_lykdat(pil_image):
    img_byte_arr = convert_pil_to_bytes(pil_image)
    lykdat_response = call_lykdat_global_search(image=img_byte_arr)

    return parse_lykdat_response(lykdat_response)


def search_images_list(images_list):
    results = []

    for img in images_list:
        results.append(search_lykdat(img["image"]))

    return results