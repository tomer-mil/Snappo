class SerpAPI:
	SERPAPI_SEARCH_ENDPOINT = "https://serpapi.com/search"

	IMAGE_EXTRACTION_ERROR_MESSAGE = "Error extracting text from image:"
	SHOPPING_RESULTS_PARSING_ERROR_MESSAGE = "Error parsing shopping results:"
	SEARCH_ERROR_MESSAGE = "Error during SerpAPI search:"

class LykdatAPI:
	LYKDAT_GLOBAL_SEARCH_URL = "https://cloudapi.lykdat.com/v1/global/search"
	API_REQUEST_ERROR_MESSAGE = "API request error:"
	GLOBAL_SEARCH_MOCK_RESPONSE_PATH = "APIs/mock_responses/lykdat_global_search_response_mock.json"

class ClothesSegmorfer:
	B2_CLOTHES_MODEL_NAME = "mattmdjaga/segformer_b2_clothes"
	COLOR_MAP = {
		0: [0, 0, 0],        # Background
		1: [255, 0, 0],      # Hat
		2: [0, 255, 0],      # Hair
		3: [0, 0, 255],      # Sunglasses
		4: [255, 255, 0],    # Upper-clothes
		5: [255, 0, 255],    # Skirt
		6: [0, 255, 255],    # Pants
		7: [128, 0, 0],      # Dress
		8: [0, 128, 0],      # Belt
		9: [0, 0, 128],      # Left-Shoe
		10: [128, 128, 0],   # Right-shoe
		11: [128, 0, 128],   # Face
		12: [0, 128, 128],   # Left-leg
		13: [64, 0, 0],      # Right-leg
		14: [0, 64, 0],      # Left-arm
		15: [0, 0, 64],      # Right-arm
		16: [64, 64, 0],     # Bag
		17: [64, 0, 64]      # Scarf
	}
	LABEL_TO_NAME = {
		1: "hat",
		3: "sunglasses",
		4: "upper-clothes",
		5: "skirt",
		6: "pants",
		7: "dress",
		8: "belt",
		9: "l_shoe",
		10: "r_shoe",
		16: "bag",
		17: "scarf"
	}
