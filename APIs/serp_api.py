"""
serp_api.py
-----------
Handles communication with SerpApi to perform Google Shopping queries.
"""

import requests
from PIL import Image
import pytesseract

import Constants
from Product import Product

# Replace with your actual SerpApi key
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
        print(f"{Constants.SerpAPI.IMAGE_EXTRACTION_ERROR_MESSAGE} {e}")
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
            # parsed_results.append({
            #     "title": result.get("title"),
            #     "price": result.get("price"),
            #     "source": result.get("source"),    # store name
            #     "product_link": result.get("product_link"),
            #     "rating": result.get("rating"),
            #     "reviews": result.get("reviews"),
            #     "thumbnail": result.get("thumbnail"),
            # })
        return parsed_results
    except Exception as e:
        print(f"{Constants.SerpAPI.SHOPPING_RESULTS_PARSING_ERROR_MESSAGE} {e}")
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
    params = build_serpapi_params(query=query, limit=limit)
    
    try:
        response = requests.get(Constants.SerpAPI.SERPAPI_SEARCH_ENDPOINT, params=params)
        response.raise_for_status()
        results = response.json()

        # Parse the shopping results
        all_parsed = parse_shopping_results(results)

        # Save results to a JSON file
        # try:
        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     filename = f'shopping_results_{timestamp}.json'
        #     with open(filename, 'w', encoding='utf-8') as f:
        #         json.dump(all_parsed, f, ensure_ascii=False, indent=2)
        # except Exception as e:
        #     print(f"Error saving results to file: {e}")

        # Return only the first `limit` results
        return all_parsed[:limit]
    except Exception as e:
        print(f"{Constants.SerpAPI.SEARCH_ERROR_MESSAGE} {e}")
        return []
