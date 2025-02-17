from BLIP import generate_detailed_caption
from serp_api import search_product
from flask import jsonify, request
import types

def ping():
    """
    A simple endpoint to verify that the server is running.
    """
    return jsonify({"message": "Clothing Search API is up!"})

def search_text():
    """
    Accepts a JSON body with a 'query' field to perform a text-based search.
    Returns JSON with product details from SerpApi.
    Example input JSON:
    {
      "query": "red dress"
    }
    """
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    query = data["query"].strip()
    if not query:
        return jsonify({"error": "Query string is empty"}), 400

    results = search_product(query, limit=5)
    return jsonify({"results": results})

def caption_image():
    """
    Accepts a JSON body with an 'image_path' (for local testing) and generates
    a clothing-focused caption using the BLIP model.
    Example input JSON:
    {
      "image_path": "./demo_photo_4.jpg"
    }
    """
    data = request.get_json()
    if not data or "image_path" not in data:
        return jsonify({"error": "Missing 'image_path' in request body"}), 400

    image_path = data["image_path"]
    try:
        caption = generate_detailed_caption(image_path)
        return jsonify({"caption": caption})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def search_image(image_path):

    data = request.get_json()
    if not data or "image_path" not in data:
        return jsonify({"error": "Missing 'image_path' in request body"}), 400

    # image_path = data["image_path"]

    try:
        # Step 1: Generate caption using BLIP
        caption = generate_detailed_caption(image_path)

        # Step 2: Use caption as query for SerpApi
        search_results = search_product(caption, limit=5)

        # Step 3: Return both the caption and the shopping results
        return jsonify({"caption": caption, "results": search_results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

