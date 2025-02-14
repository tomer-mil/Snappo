"""
main.py
---------
Entry point for the Flask application using BLIP for image captioning.
"""

from flask import Flask, request, jsonify
from BLIP import generate_detailed_caption
from serp_api import search_product

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    """
    A simple endpoint to verify that the server is running.
    """
    return jsonify({"message": "Clothing Search API is up!"})


@app.route("/search-text", methods=["POST"])
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


@app.route("/caption-image", methods=["POST"])
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

@app.route("/search-image", methods=["POST"])
def search_image():
    """
    Accepts a JSON body with an 'image_path' and:
    1. Generates a caption using BLIP
    2. Uses the generated caption as a search query in SerpApi
    3. Returns both the generated caption and the shopping results

    Example input JSON:
    {
      "image_path": "./demo_photo_4.jpg"
    }

    Example response JSON:
    {
      "caption": "A red dress with floral patterns",
      "results": [
        {"title": "Red Floral Dress", "price": "$49.99", "source": "Amazon", "product_link": "..."},
        {"title": "Elegant Red Dress", "price": "$59.99", "source": "Zara", "product_link": "..."}
      ]
    }
    """
    data = request.get_json()
    if not data or "image_path" not in data:
        return jsonify({"error": "Missing 'image_path' in request body"}), 400

    image_path = data["image_path"]

    try:
        # Step 1: Generate caption using BLIP
        caption = generate_detailed_caption(image_path)
        
        # Step 2: Use caption as query for SerpApi
        search_results = search_product(caption, limit=5)

        # Step 3: Return both the caption and the shopping results
        return jsonify({"caption": caption, "results": search_results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
