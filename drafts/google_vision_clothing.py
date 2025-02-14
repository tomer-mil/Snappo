"""
google_vision_clothing.py
-------------------------
Corrected script for Google Reverse Image Search using SerpApi.

Steps:
1. Upload the image to PostImages API (temporary hosting).
2. Perform Google Reverse Image Search using SerpApi.
3. Extract clothing descriptions from search results.
"""

import requests
import json

# 🔹 SerpApi Key (Replace with your own key)
SERPAPI_KEY = "970948c83db54825b85fb7365133297cd23184abd6d8e7d25693c816160a2db4"

# 🔹 PostImages API for temporary image hosting (Free & No API Key Required)
UPLOAD_URL = "https://api.imgbb.com/1/upload"
IMGBB_API_KEY = "b6f53ba76b76f4c65a8e013410753125"  # Replace with your own Imgbb API key (Free sign-up)

def upload_image(image_path):
    """
    Uploads an image to ImgBB (or PostImages) to obtain a temporary public URL.
    """
    with open(image_path, "rb") as file:
        response = requests.post(UPLOAD_URL, data={"key": IMGBB_API_KEY}, files={"image": file})
    
    if response.status_code != 200:
        print(f"Error uploading image: {response.text}")
        return None
    
    response_data = response.json()
    return response_data["data"]["url"]

def search_image_description(image_url):
    """
    Uses Google Reverse Image Search via SerpApi to retrieve clothing descriptions.
    """
    endpoint = "https://serpapi.com/search"
    params = {
        "engine": "google_reverse_image",
        "image_url": image_url,
        "api_key": SERPAPI_KEY
    }

    response = requests.get(endpoint, params=params)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        return []

    results = response.json()

    # Extract clothing-related descriptions
    clothing_descriptions = []
    for item in results.get("visual_matches", []):
        title = item.get("title", "").lower()
        if any(keyword in title for keyword in ["shirt", "jeans", "jacket", "dress", "skirt", "hat", "shoes", "coat", "pants"]):
            clothing_descriptions.append(title)

    return clothing_descriptions

def detect_clothing(image_path):
    """
    Full pipeline:
    1. Uploads image to hosting service.
    2. Performs Google Reverse Image Search via SerpApi.
    3. Extracts and returns clothing descriptions.
    """
    print("Uploading image...")
    image_url = upload_image(image_path)
    
    if not image_url:
        print("Image upload failed. Cannot proceed with search.")
        return []
    
    print(f"Image uploaded successfully: {image_url}")
    
    print("Searching for clothing items...")
    clothing_items = search_image_description(image_url)

    return clothing_items

def demo():
    """
    Runs a test with a sample image.
    """
    test_image = "demo_photo_2.jpg"  # Replace with your actual image path
    detected_clothing = detect_clothing(test_image)

    if detected_clothing:
        print("\nDetected clothing items:")
        for item in detected_clothing:
            print(f"- {item}")
    else:
        print("No clothing items detected.")

if __name__ == "__main__":
    demo()
