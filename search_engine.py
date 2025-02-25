import re
from PIL import Image
from APIs.lykdat_api import search_lykdat
from APIs.serp_api import search_product as search_serp
from Product import Product
from segmorfer_b2_clothes import ClothesSegmorfer


class SearchEngine:
    """
    A class to handle clothing image segmentation and product search.

    Attributes:
        segmorfer (ClothesSegmorfer): An instance of the ClothesSegmorfer class for detecting clothing items.
        clothe_types (list[str]): A list of detected clothing types from an image.
        detected_clothes (dict): A dictionary mapping clothing types to their respective images.
    """
    segmorfer: ClothesSegmorfer
    clothe_types: list[str]
    detected_clothes: dict

    def __init__(self):
        """
        Initializes the SearchEngine with an instance of ClothesSegmorfer,
        an empty list for clothing types, and an empty dictionary for detected clothes.
        """
        self.segmorfer = ClothesSegmorfer()
        self.clothe_types = []
        self.detected_clothes = {}

    @staticmethod
    def is_valid_image_url(url: str):
        """
        Checks if a given URL is a valid image URL.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL points to a valid image file, False otherwise.
        """
        image_extensions = re.compile(r"\.(jpeg|jpg|png|gif|bmp|tiff|webp)$", re.IGNORECASE)
        return bool(image_extensions.search(url))

    @staticmethod
    def extract_clothe_types(detected_clothes: list[dict]) -> list[str]:
        """
        Extracts the types of clothes detected in an image.

        Args:
            detected_clothes (list[dict]): A list of detected clothing items, each represented as a dictionary.

        Returns:
            list[str]: A list of clothing types detected in the image.
        """
        clothe_types = []
        for clothe in detected_clothes:
            clothe_type = clothe.get("clothe_type", "")
            clothe_types.append(clothe_type)
        return clothe_types

    def search_product_by_type(self, clothe_type: str) -> list[Product]:
        """
        Searches for similar products based on a given clothing type.

        Args:
            clothe_type (str): The type of clothing to search for.

        Returns:
            list[Product]: A list of Product objects containing search results.
        """
        processed_results = []
        clothe_image = self.detected_clothes[clothe_type]

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
        """
        Extracts clothing items from a given image using ClothesSegmorfer.

        Args:
            image (Image): The image to analyze.
        """
        self.detected_clothes = self.segmorfer.get_clothes_from_image(image=image)
        self.clothe_types = list(self.detected_clothes.keys())
