import requests
import base64
import os

# Replace with your Ximilar API Key
XIMILAR_API_KEY = "b7f8d2b1d5b1a3cb5a3735f91d8c60a416f6ac71"

# Primary and alternative endpoints
ENDPOINTS = [
    "https://api.ximilar.com/tagging/v2/tagging",  # Default endpoint
    "https://api.ximilar.com/fashion/v2/detect"   # Alternative if 404 occurs
]

def describe_clothing_ximilar(image_path):
    """
    Uses Ximilar Fashion API to analyze clothing attributes from a local image file.
    :param image_path: Path to the local image file
    :return: List of detected clothing attributes or error message
    """
    headers = {"Authorization": f"Token {XIMILAR_API_KEY}"}

    # Check if file exists
    if not os.path.exists(image_path):
        return f"Error: Image file '{image_path}' not found."

    # Convert local image to Base64 (Ximilar requires image URLs or Base64)
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Try multiple endpoints in case of 404 error
    for url in ENDPOINTS:
        print(f"Trying Ximilar API: {url}")
        payload = {"records": [{"_base64": encoded_image}]}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()

            # Extract clothing details
            if "records" in result and len(result["records"]) > 0:
                clothing_tags = result["records"][0]["_tags"]
                formatted_results = [f"{item['name']} ({item['score']*100:.1f}%)" for item in clothing_tags]
                return formatted_results
            else:
                return ["No clothing detected"]
        
        elif response.status_code == 404:
            print(f"Error: Endpoint {url} returned 404. Trying next endpoint...")

        else:
            return f"Error: {response.status_code} - {response.text}"

    return "Error: All Ximilar API endpoints failed."

# Example usage with a local image
image_path = "demo_photo_2.jpg"  # Replace with your local image path
clothing_tags = describe_clothing_ximilar(image_path)

# Print detected clothing attributes
print("Detected Clothing Attributes:")
for tag in clothing_tags:
    print("-", tag)
