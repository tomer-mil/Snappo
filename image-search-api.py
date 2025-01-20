import os
import requests

def search_pexels_images(query, per_page=15, page=1):
    # Load the API key from an environment variable
    api_key = "78NaawF3Qa9OYKvMDpWSHTYvMIBUIEfoVFR7ogidDo2NkoylPn1xmY5l"
    if not api_key:
        print("Error: API key not found. Set the 'PEXELS_API_KEY' environment variable.")
        return

    url = "https://api.pexels.com/v1/search"
    
    # Define the headers with the API key
    headers = {
        "Authorization": api_key
    }
    
    # Define the query parameters
    params = {
        "query": query,
        "per_page": per_page,
        "page": page
    }
    
    # Make the GET request
    response = requests.get(url, headers=headers, params=params)
    
    # Handle the response
    if response.status_code == 200:
        data = response.json()
        for photo in data.get("photos", []):
            print(f"Photographer: {photo['photographer']}")
            print(f"URL: {photo['url']}")
            print(f"Image: {photo['src']['original']}\n")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

# Example usage
# search_pexels_images("blakc leather jacket", per_page=5, page=1)

def fake_store_api():

    response = requests.get('https://fakestoreapi.com/products')
    products = response.json()
    for product in products:
        print(f"Title: {product['title']}")
        print(f"Price: ${product['price']}")
        print(f"Description: {product['description']}")
        print(f"Image URL: {product['image']}")
        # print(f"Product URL: {product['url']}\n")

# fake_store_api()

def dummyjson():
    import requests

    response = requests.get('https://dummyjson.com/products/search?q=watch')
    products = response.json().get('products', [])
    if not products:
        print("No products found.")
        return
    for product in products:
        print(f"Title: {product['title']}")
        print(f"Price: ${product['price']}")
        print(f"Description: {product['description']}")
        print(f"Image URL: {product['thumbnail']}")

# dummyjson()

def serpapi():
    import requests

def search_google_images(query, api_key, num_results=10):
    # SerpApi endpoint for Google Images
    endpoint = "https://serpapi.com/search"
    
    # Define the parameters for the API request
    params = {
        "engine": "google",            # Search engine
        "q": query,                   # Search query
        "tbm": "isch",                # Image search mode
        "num": num_results,           # Number of results to retrieve
        "api_key": api_key            # Your SerpApi API key
    }
    
    # Make the GET request
    response = requests.get(endpoint, params=params)
    
    # Check for a successful response
    if response.status_code == 200:
        data = response.json()
        images = data.get("images_results", [])
        for idx, image in enumerate(images, 1):
            print(f"{idx}. Title: {image.get('title')}")
            print(f"Image URL: {image.get('original')}")
            print(f"Source Page URL: {image.get('link')}\n")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

# Replace 'your_serpapi_key' with your actual SerpApi API key
api_key = "970948c83db54825b85fb7365133297cd23184abd6d8e7d25693c816160a2db4"

# Perform a Google Image search
search_google_images("blue dress with fluffy skirt", api_key, num_results=1)


serpapi()


