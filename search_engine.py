from typing import List
import re
from PIL import Image
from APIs.lykdat_api import search_lykdat
from APIs.serp_api import search_product as search_serp
from Product import Product

class SearchEngine:
    IMAGE_SUFFIXES = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')

    @staticmethod
    def is_valid_image_url(url: str) -> bool:
        """Check if URL points to an image based on file extension."""
        return any(url.lower().endswith(suffix) for suffix in SearchEngine.IMAGE_SUFFIXES)

    def search_product(self, clothe_image: Image) -> List[Product]:
        """Search for similar products using the extracted clothing image."""
        # First attempt with Lykdat API
        lykdat_results = search_lykdat(clothe_image)

        processed_results = []
        for product in lykdat_results:
            # Check if image URL is valid
            if self.is_valid_image_url(product.image_url):
                processed_results.append(product)
                continue

            # Fallback to SerpAPI using product name
            serp_results = search_serp(product.name)
            if serp_results:
                # Take the first result from SerpAPI
                processed_results.append(serp_results[0])

        return processed_results
