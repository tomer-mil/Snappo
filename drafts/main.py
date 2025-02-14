"""
main.py
---------
Entry point for the Flask application.
"""

from flask import Flask, request, jsonify
from drafts.clothes_segmentation import load_segmentation_model, segment_clothes
from serp_api import search_product

app = Flask(__name__)

# 1. Load segmentation model once at startup.
seg_model, seg_processor = load_segmentation_model()

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


@app.route("/segment", methods=["POST"])
def segment():
    """
    Accepts a JSON body with an 'image_path' (for local testing) or will be adapted
    for actual file upload in the future.
    Returns the list of detected items (labels).
    Example input JSON:
    {
      "image_path": "./demo_photo.jpg"
    }
    """
    data = request.get_json()
    if not data or "image_path" not in data:
        return jsonify({"error": "Missing 'image_path' in request body"}), 400

    image_path = data["image_path"]
    try:
        detected_items = segment_clothes(seg_model, seg_processor, image_path)
        return jsonify({"detected_items": detected_items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
