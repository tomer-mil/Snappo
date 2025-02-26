import json

import requests
from PIL import Image
import pytesseract

from utils.constants import SerpAPI as Constants
from core.models.product import Product

SERPAPI_KEY = "970948c83db54825b85fb7365133297cd23184abd6d8e7d25693c816160a2db4"

def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"{Constants.IMAGE_EXTRACTION_ERROR_MESSAGE} {e}")
        return ""

def parse_shopping_results(data):
    """
    Given a JSON response from SerpApi, extract relevant shopping information.
    """
    try:
        shopping_results = data.get("shopping_results", [])
        parsed_results = []
        for result in shopping_results:
            parsed_results.append(Product(response=result, source="serpapi"))
        return parsed_results
    except Exception as e:
        print(f"{Constants.SHOPPING_RESULTS_PARSING_ERROR_MESSAGE} {e}")
        return []

def build_serpapi_params(query, limit):
    """
    Build the parameters for the SerpApi request.
    """
    return {
        "engine": "google",
        "q": query,
        "tbm": "shop",
        "num": limit,
        "api_key": SERPAPI_KEY
    }

def search_product(query, limit=3):
    """
    Search for a product using SerpApi and return product details.
    """
    with open(Constants.SEARCH_MOCK_RESPONSE_PATH, 'r', encoding="utf-8") as f:
        mock_results = json.load(f)
        mock_all_parsed = parse_shopping_results(data=mock_results)
        return mock_all_parsed[:limit]

    params = build_serpapi_params(query=query, limit=limit)
    try:
        response = requests.get(Constants.SERPAPI_SEARCH_ENDPOINT, params=params)
        response.raise_for_status()
        results = response.json()

        # Parse the shopping results
        all_parsed = parse_shopping_results(results)

        return all_parsed[:limit]

    except Exception as e:
        print(f"{Constants.SEARCH_ERROR_MESSAGE} {e}")
        return []
