"""
google_vision_ocr.py
-------------------------
Uses Tesseract OCR to extract text from an image and detect clothing items.
This replaces the previous segmentation-based approach.
"""

import pytesseract
from PIL import Image

# Define keywords that indicate clothing items
CLOTHING_KEYWORDS = ["shirt", "jeans", "jacket", "dress", "skirt", "hat", "shoes", "coat", "pants", "sweater", "scarf"]

def extract_text_from_image(image_path):
    """
    Extracts text from an image using Tesseract OCR.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

def detect_clothing_from_text(image_path):
    """
    Uses OCR to extract text and detect clothing items.
    """
    print("Extracting text from image...")
    extracted_text = extract_text_from_image(image_path)

    if not extracted_text:
        print("No text detected in image.")
        return []

    print(f"Extracted Text: {extracted_text}")

    # Search for clothing-related words in the extracted text
    detected_clothing = [word for word in CLOTHING_KEYWORDS if word in extracted_text.lower()]

    return detected_clothing

def demo():
    """
    Runs a test with a sample image.
    """
    test_image = "demo_photo.jpg"  # Replace with your image file
    detected_clothing = detect_clothing_from_text(test_image)

    if detected_clothing:
        print("\nDetected clothing items:")
        for item in detected_clothing:
            print(f"- {item}")
    else:
        print("No clothing items detected.")

if __name__ == "__main__":
    demo()
