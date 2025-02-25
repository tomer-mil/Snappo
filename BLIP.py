from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from PIL import Image

# Load BLIP model & processor
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


# Function to generate a clothing-focused caption
def generate_detailed_caption(photo_bytes, is_pil_image=False):
    if not is_pil_image:
        image = Image.open(photo_bytes).convert("RGB")
    else:
        image = photo_bytes

    # Run BLIP in captioning mode (no user prompt)
    inputs = processor(images=image, return_tensors="pt").to(device)

    with torch.no_grad():
        output = model.generate(**inputs, min_length=20, max_length=100, num_beams=5)

    caption = processor.tokenizer.decode(output[0], skip_special_tokens=True)

    return caption

# Example Usage
# image_path = "media/demo_photo_4.jpg"  # Replace with your actual image path
# caption = generate_detailed_caption(image_path)
# print(f"Generated Caption: {caption}")
