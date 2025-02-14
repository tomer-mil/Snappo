"""
improved_clothes_segmentation_only_clothes.py
---------------------------------------------
An improved script that ensures the segmentation detects only clothing items 
and not body parts (face, arms, legs, etc.).
"""

import torch
import numpy as np
import cv2
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation

# Model to use
MODEL_NAME = "mattmdjaga/segformer_b2_clothes"

# Filter out body parts, keeping only clothes
CLOTHING_LABELS = {
    1: "upper-clothes",
    2: "pants",
    3: "dress",
    4: "skirt",
    10: "socks",
    12: "shoes",
}

# Colors for clothing items (non-body)
COLOR_MAP = {
    1: [255, 0, 0],      # Upper-clothes (red)
    2: [0, 255, 0],      # Pants (green)
    3: [0, 0, 255],      # Dress (blue)
    4: [255, 255, 0],    # Skirt (yellow)
    10: [128, 0, 128],   # Socks (purple)
    12: [0, 128, 128],   # Shoes (teal)
}

def load_segmentation_model():
    """
    Loads the SegFormer model and processor.
    """
    processor = SegformerImageProcessor.from_pretrained(MODEL_NAME)
    model = SegformerForSemanticSegmentation.from_pretrained(MODEL_NAME)
    model.eval()
    return model, processor

def segment_clothes(model, processor, image_path, resize_dim=512, contrast_factor=1.5, sharpness_factor=2.0):
    """
    Performs segmentation but filters out non-clothing items like face, arms, and legs.
    Displays original, segmentation mask, and blended overlay.
    """
    # Load and enhance image
    image = Image.open(image_path).convert("RGB")
    image = image.resize((resize_dim, resize_dim))

    # Apply contrast enhancement
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast_factor)

    # Apply sharpness enhancement (helps detect textures better)
    sharpness_enhancer = ImageEnhance.Sharpness(image)
    image = sharpness_enhancer.enhance(sharpness_factor)

    # Process image with model
    inputs = processor(images=image, return_tensors="pt")
    
    # Run inference
    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    upsampled_logits = torch.nn.functional.interpolate(
        logits,
        size=image.size[::-1],  # Resize back to original dimensions
        mode="bilinear",
        align_corners=False,
    )
    
    seg_map = upsampled_logits.argmax(dim=1)[0].cpu().numpy()  # Get segmentation mask

    # Identify detected clothing items (ignore body parts)
    detected_items = []
    total_pixels = seg_map.shape[0] * seg_map.shape[1]
    for label in np.unique(seg_map):
        if label not in CLOTHING_LABELS:
            continue  # Skip body parts

        label_name = CLOTHING_LABELS[label]
        coverage_pct = (seg_map == label).sum() / total_pixels * 100

        # Only report items that cover a significant part of the image
        if coverage_pct > 1:
            detected_items.append({"label_name": label_name, "coverage": round(coverage_pct, 2)})

    # Create visualization (color clothing, ignore body)
    seg_map_colored = np.zeros((seg_map.shape[0], seg_map.shape[1], 3), dtype=np.uint8)
    
    for label, color in COLOR_MAP.items():
        mask = seg_map == label
        seg_map_colored[mask] = color  # Assign color to detected clothing labels

    # Convert PIL image to NumPy for blending
    img_np = np.array(image)
    blended = cv2.addWeighted(img_np, 0.7, seg_map_colored, 0.3, 0)  # Blend with segmentation mask

    # Show images
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    axes[0].imshow(image)
    axes[0].set_title("Original Image")
    axes[0].axis("off")

    axes[1].imshow(seg_map_colored)
    axes[1].set_title("Segmentation Mask (Clothes Only)")
    axes[1].axis("off")

    axes[2].imshow(blended)
    axes[2].set_title("Blended Segmentation")
    axes[2].axis("off")

    plt.show()

    return detected_items

def demo():
    """
    Run a demo with a sample image.
    """
    test_image = "demo_photo.jpeg"  # Replace with your own image path
    model, processor = load_segmentation_model()
    results = segment_clothes(model, processor, test_image)

    if not results:
        print("No clothing items detected.")
    else:
        print("Detected clothing items:")
        for item in results:
            print(f"- {item['label_name']} ({item['coverage']}% coverage)")

if __name__ == "__main__":
    demo()
