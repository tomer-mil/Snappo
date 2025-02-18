import torch
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def load_model():
    processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
    model = SegformerForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
    model.eval()
    return processor, model

def process_image(image_bytes, processor):
    image = Image.open(image_bytes)
    inputs = processor(images=image, return_tensors="pt")
    return image, inputs

def get_segmentation_map(model, inputs, image_size):
    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    upsampled_logits = torch.nn.functional.interpolate(
        logits,
        size=image_size[::-1],  # (height, width)
        mode="bilinear",
        align_corners=False,
    )
    return upsampled_logits.argmax(dim=1)[0]

def get_color_map():
    return {
        0: [0, 0, 0],        # Background
        1: [255, 0, 0],      # Upper-clothes
        2: [0, 255, 0],      # Pants
        3: [0, 0, 255],      # Dress
        4: [255, 255, 0],    # Skirt
        5: [255, 0, 255],    # Face
        6: [0, 255, 255],    # Arms
        7: [128, 0, 0],      # Legs
        8: [0, 128, 0],      # Hat
        9: [0, 0, 128],      # Gloves
        10: [128, 128, 0],   # Socks
        11: [128, 0, 128],   # Sunglasses
        12: [0, 128, 128],   # Shoes
        13: [64, 0, 0]       # Hair
    }

def create_colored_mask(seg_map, color_map):
    colored_mask = np.zeros((seg_map.shape[0], seg_map.shape[1], 3), dtype=np.uint8)
    for label, color in color_map.items():
        mask = seg_map == label
        colored_mask[mask] = color
    return colored_mask

def display_results(image, colored_mask):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

    # Original image
    ax1.imshow(image)
    ax1.set_title('Original Image')
    ax1.axis('off')

    # Segmentation mask
    ax2.imshow(colored_mask)
    ax2.set_title('Segmentation Mask')
    ax2.axis('off')

    # Blended result
    img_array = np.array(image)
    blended = cv2.addWeighted(img_array, 0.7, colored_mask, 0.3, 0)
    ax3.imshow(blended)
    ax3.set_title('Blended Result')
    ax3.axis('off')

    plt.show()

def extract_clothes(image, seg_map):
    detected_items = []
    img_array = np.array(image)
    unique_labels = np.unique(seg_map)

    # Map label numbers to meaningful clothing names (based on your color_map)
    label_to_name = {
        1: "upper_clothes",
        2: "pants",
        3: "dress",
        4: "skirt",
        8: "hat",
        9: "gloves",
        10: "socks",
        12: "shoes"
    }

    for label in unique_labels:
        if label in label_to_name:
            # Create binary mask for this clothing item
            mask = (seg_map == label)
            if not np.any(mask):  # Skip if no pixels found for this label
                continue

            # Find contiguous regions
            y_indices, x_indices = np.where(mask)
            if len(y_indices) == 0 or len(x_indices) == 0:
                continue

            # Add padding to bounding box
            padding = 5
            y_min, y_max = max(0, np.min(y_indices) - padding), min(seg_map.shape[0], np.max(y_indices) + padding)
            x_min, x_max = max(0, np.min(x_indices) - padding), min(seg_map.shape[1], np.max(x_indices) + padding)

            # Crop the image and mask
            cropped_img = img_array[y_min:y_max+1, x_min:x_max+1].copy()
            cropped_mask = mask[y_min:y_max+1, x_min:x_max+1]

            # Create transparent background
            rgba = np.zeros((cropped_img.shape[0], cropped_img.shape[1], 4), dtype=np.uint8)
            rgba[..., :3] = cropped_img
            rgba[..., 3] = cropped_mask * 255  # Alpha channel

            # Create white background and paste RGBA image on it
            background = Image.new('RGB', (rgba.shape[1], rgba.shape[0]), (255, 255, 255))
            pil_image = Image.fromarray(rgba)
            background.paste(pil_image, (0, 0), pil_image)
            pil_image = background

            detected_items.append({
                "clothe_type": label_to_name[label],
                "image": pil_image
            })

    return detected_items

def print_detected_items(seg_map, color_map):
    unique_labels = np.unique(seg_map)
    print("\nDetected items:")
    for label in unique_labels:
        if label in color_map:
            percentage = (seg_map == label).sum() / (seg_map.shape[0] * seg_map.shape[1]) * 100
            print(f"Class {label}: {percentage:.1f}% of image")

def get_clothes_from_image(image_bytes):
    # Initialize model and processor
    processor, model = load_model()

    # Load and process image
    # image_path = "sam2_function/demo_photo.jpeg"
    image, inputs = process_image(image_bytes, processor)

    # Get segmentation map
    seg_map = get_segmentation_map(model, inputs, image.size)
    detected_items = extract_clothes(image, seg_map.cpu().numpy())
    return detected_items

    # Print statistics
    # print_detected_items(seg_map.cpu().numpy(), color_map)