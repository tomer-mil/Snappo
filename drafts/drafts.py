import requests

# Replace with your API Key
CLARIFAI_API_KEY = "YOUR_API_KEY"

def describe_clothing_clarifai(image_url):
    url = "https://api.clarifai.com/v2/models/clothing-detection-recognition/outputs"
    headers = {"Authorization": f"Key {CLARIFAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "inputs": [
            {
                "data": {
                    "image": {"url": image_url}
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    # Extract clothing descriptions
    clothing_items = [concept["name"] for concept in result["outputs"][0]["data"]["concepts"]]

    return clothing_items

# Example usage
clothing_detected = describe_clothing_clarifai("https://example.com/image.jpg")
print("Detected Clothing Items:", clothing_detected)
