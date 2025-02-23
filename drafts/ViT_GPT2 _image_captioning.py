from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image

# Load the model, processor, and tokenizer
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Enhanced parameters for longer, more descriptive captions
max_length = 50   # Allow longer captions
num_beams = 8     # Increase beam search depth
temperature = 0.8  # Encourage diversity in text
top_p = 0.95      # Enable more natural responses
do_sample = True  # Allow diversity in word choices
repetition_penalty = 1.2  # Avoid generic phrases

# Function to generate a detailed clothing description
def generate_caption(image_path):
    # Load and process the image
    image = Image.open(image_path).convert("RGB")
    pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    # Inject a guiding prompt to encourage fashion descriptions
    prompt = "Describe the person's clothing in great detail:"

    # Tokenize the prompt and prepare the input
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    input_ids = input_ids.to(device)

    # Generate caption with improved settings
    output_ids = model.generate(
        pixel_values, 
        max_length=max_length, 
        num_beams=num_beams, 
        temperature=temperature, 
        top_p=top_p, 
        do_sample=do_sample,
        repetition_penalty=repetition_penalty
    )

    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return caption

# Example Usage
image_path = "demo_photo_2.jpg"  # Replace with the actual image path
caption = generate_caption(image_path)
print(f"Generated Caption: {caption}")
