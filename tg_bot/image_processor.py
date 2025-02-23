from BLIP import generate_detailed_caption
from APIs.serp_api import search_product
import json


def ping():
    """
    A simple endpoint to verify that the server is running.
    """
    return json.dumps({"message": "Clothing Search API is up!"})

def search_text(query_data):
    """
    Accepts a dictionary with a 'query' field to perform a text-based search.
    Returns JSON string with product details from SerpApi.
    Example input:
    {
      "query": "red dress"
    }
    """
    if not query_data or "query" not in query_data:
        return json.dumps({"error": "Missing 'query' in request"})

    query = query_data["query"].strip()
    if not query:
        return json.dumps({"error": "Query string is empty"})

    results = search_product(query, limit=5)
    return json.dumps({"results": results})

def caption_image(image_data):
    """
    Accepts a dictionary with an 'image_path' (for local testing) and generates
    a clothing-focused caption using the BLIP model.
    Example input:
    {
      "image_path": "./demo_photo_4.jpg"
    }
    """
    if not image_data or "image_path" not in image_data:
        return json.dumps({"error": "Missing 'image_path' in request"})

    image_path = image_data["image_path"]
    try:
        caption = generate_detailed_caption(image_path)
        return json.dumps({"caption": caption})
    except Exception as e:
        return json.dumps({"error": str(e)})

# def set_image_results_json(search_results: str, is_):


def search_image(image_path, is_pil_image=False):
    """
    Search for products based on an image using BLIP for caption generation
    and SerpApi for product search.
    """
    try:
        # Step 1: Generate caption using BLIP
        caption = generate_detailed_caption(image_path, is_pil_image)

        # Step 2: Use caption as query for SerpApi
        search_results = search_product(query=caption, limit=5)

        # Step 3: Return both the caption and the shopping results
        return json.dumps({
            "caption": caption,
            "results": search_results
        })

    except Exception as e:
        return json.dumps({"error": str(e)})