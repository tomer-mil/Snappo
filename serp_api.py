import requests
import os
from PIL import Image
import pytesseract

# Replace with your SerpApi key
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
        print(f"Error extracting text from image: {e}")
        return ""

def parse_shopping_results(data):
    try:
        # Access the shopping results section
        shopping_results = data.get("shopping_results", [])

        # Parse relevant information
        parsed_results = []
        for result in shopping_results:
            parsed_results.append({
                "title": result.get("title"),
                "price": result.get("price"),
                "source": result.get("source"),
                "product_link": result.get("product_link"),
                "rating": result.get("rating"),
                "reviews": result.get("reviews"),
                "thumbnail": result.get("thumbnail"),
            })

        return parsed_results
    except Exception as e:
        print(f"Error parsing shopping results: {e}")
        return []
    
def search_product(query, limit=5):
    """
    Search for a product using SerpApi and return product URLs.
    """
    endpoint = "https://serpapi.com/search"
    params = {
        "engine": "google",          # Use Google search
        "q": query,                 # Search query
        "tbm": "shop",              # Google Shopping
        "num": limit,               # Limit to a specific number of results
        "api_key": SERPAPI_KEY      # Your SerpApi key
    }
    
    try:
        # Perform the API request
        response = requests.get(endpoint, params=params)
        # print(response)

        response.raise_for_status()
        results = response.json()
        # print(results)

        
        # Extract shopping results and limit to the desired count
        product_data = []
        shopping_results = results.get("shopping_results", [])
        for item in shopping_results[:limit]:
            title = item.get("title")
            product_link = item.get("product_link")
            
            product_data.append({"title": title, "product_link": product_link})
        return product_data
    except Exception as e:
        print(f"Error during search: {e}")
        return []

def main():
    input_type = input("Enter input type (text/photo): ").strip().lower()
    query = ""

    if input_type == "text":
        # Get product description as input
        query = input("Enter product description: ").strip()
    elif input_type == "photo":
        # Get photo path as input
        image_path = input("Enter image file path: ").strip()
        if os.path.exists(image_path):
            print("Extracting text from image...")
            query = extract_text_from_image(image_path)
            print(f"Extracted text: {query}")
        else:
            print("Invalid image file path.")
            return
    else:
        print("Invalid input type. Please enter 'text' or 'photo'.")
        return

    if query:
        print("Searching for products...")
        product_data = search_product(query, limit=5)
        if product_data:
            print("\nTop 5 Product URLs:")
            for idx, data in enumerate(product_data, 1):
                print(f"{idx}. {data}")
        else:
            print("No products found.")
    else:
        print("No valid query to search.")

if __name__ == "__main__":
    main()
