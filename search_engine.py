import re
from PIL import Image
from APIs.lykdat_api import search_lykdat
from APIs.serp_api import search_product as search_serp
from Product import Product
from segmorfer_b2_clothes import ClothesSegmorfer

class SearchEngine:

    segmorfer: ClothesSegmorfer
    clothe_types: list[str]
    detected_clothes: list[dict]

    def __init__(self):
        self.segmorfer = ClothesSegmorfer()

    @staticmethod
    def is_valid_image_url(url: str):
        image_extensions = re.compile(r"\.(jpeg|jpg|png|gif|bmp|tiff|webp)$", re.IGNORECASE)
        return bool(image_extensions.search(url))

    @staticmethod
    def extract_clothe_types(detected_clothes: list[dict]) -> list[str]:
        """Extract the types of clothes detected in the image by the segmorfer."""
        clothe_types = []
        for clothe in detected_clothes:
            clothe_type = clothe.get("clothe_type", "")
            clothe_types.append(clothe_type)
        return clothe_types

    def search_product(self, clothe_image: Image) -> list[Product]:
        """Search for similar products using the extracted clothing image."""
        processed_results = []

        # First attempt with Lykdat API
        lykdat_results = search_lykdat(image=clothe_image)

        for product in lykdat_results:
            # Check if image URL is valid
            if not self.is_valid_image_url(product.image_url):
                # Fallback to SerpAPI using product name
                serp_results = search_serp(query=product.name)
                if not serp_results:
                    # Skip if no results from SerpAPI
                    continue
                # Take the first result from SerpAPI
                product = serp_results[0]
            processed_results.append(product)

        return processed_results

    def extract_clothes_from_image(self, image: Image):
        self.detected_clothes = self.segmorfer.get_clothes_from_image(image=image)
        self.clothe_types = self.extract_clothe_types(self.detected_clothes)


