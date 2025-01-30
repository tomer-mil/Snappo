import os
import torch
from PIL.ImageFile import ImageFile
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, Dict
from ClotheObject import ClotheObject


CATEGORY_MAP = {
        0: "Background",
        1: "Hat",
        2: "Hair",
        3: "Sunglasses",
        4: "Upper-clothes",
        5: "Skirt",
        6: "Pants",
        7: "Dress",
        8: "Belt",
        9: "Left-shoe",
        10: "Right-shoe",
        11: "Face",
        12: "Left-leg",
        13: "Right-leg",
        14: "Left-arm",
        15: "Right-arm",
        16: "Bag",
        17: "Scarf"
}

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
    9: [0, 0, 128],      # Left-shoe
    10: [128, 128, 0],   # Right-shoe
    11: [128, 0, 128],   # Face
    12: [0, 128, 128],   # Left-leg
    13: [64, 0, 0],      # Right-leg
    14: [128, 128, 128], # Left-arm
    15: [64, 64, 64],    # Right-arm
    16: [192, 192, 192], # Bag
    17: [64, 0, 128]     # Scarf
}

COLOR_NAME_MAP = {
    0: "Black",        # Background
    1: "Red",          # Hat
    2: "Green",        # Hair
    3: "Blue",         # Sunglasses
    4: "Yellow",       # Upper-clothes
    5: "Magenta",      # Skirt
    6: "Cyan",         # Pants
    7: "Maroon",       # Dress
    8: "Dark Green",   # Belt
    9: "Navy",         # Left-shoe
    10: "Olive",       # Right-shoe
    11: "Purple",      # Face
    12: "Teal",        # Left-leg
    13: "Brown",       # Right-leg
    14: "Gray",        # Left-arm
    15: "Dark Gray",   # Right-arm
    16: "Silver",      # Bag
    17: "Indigo"       # Scarf
}

def load_model_and_processor() -> Tuple[SegformerImageProcessor, SegformerForSemanticSegmentation]:
    processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
    model = SegformerForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
    model.eval()
    return processor, model

def process_image(image_path: str, processor: SegformerImageProcessor) -> Tuple[ImageFile, Dict[str, torch.Tensor]]:
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    return image, inputs

def run_inference(model: SegformerForSemanticSegmentation, inputs: Dict[str, torch.Tensor]) -> torch.Tensor:
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.logits  # shape (batch_size, num_labels, height/4, width/4)

def get_segmentation_map(logits: torch.Tensor, image_size: Tuple[int, int]) -> np.ndarray:
    upsampled_logits = torch.nn.functional.interpolate(
        input=logits,
        size=image_size[::-1],  # (height, width)
        mode="bilinear",
        align_corners=False,
    )
    pred_seg = upsampled_logits.argmax(dim=1)[0]
    return pred_seg.cpu().numpy()

def create_colored_mask(seg_map: np.ndarray, color_map: Dict[int, list]) -> np.ndarray:
    colored_mask = np.zeros((seg_map.shape[0], seg_map.shape[1], 3), dtype=np.uint8)
    for label, color in color_map.items():
        mask = seg_map == label
        colored_mask[mask] = color
    return colored_mask

def display_results(image: Image.Image, colored_mask: np.ndarray) -> None:
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    ax1.imshow(image)
    ax1.set_title('Original Image')
    ax1.axis('off')

    ax2.imshow(colored_mask)
    ax2.set_title('Segmentation Mask')
    ax2.axis('off')

    img_array = np.array(image)
    blended = cv2.addWeighted(img_array, 0.7, colored_mask, 0.3, 0)
    ax3.imshow(blended)
    ax3.set_title('Blended Result')
    ax3.axis('off')

    plt.show()

def print_detected_items(seg_map: np.ndarray, color_map: Dict[int, list]) -> None:
    unique_labels = np.unique(seg_map)
    print("\nDetected items:")
    for label in unique_labels:
        if label in color_map:
            percentage = (seg_map == label).sum() / (seg_map.shape[0] * seg_map.shape[1]) * 100
            print(f"{CATEGORY_MAP[label]} ({COLOR_NAME_MAP[label]}): {percentage:.1f}% of image")

def extract_clothes(seg_map: np.ndarray, image: Image.Image, save_dir: str = "extracted_clothes") -> list[ClotheObject]:
    os.makedirs(save_dir, exist_ok=True)
    clothes_objects = []

    detected_labels = [CATEGORY_MAP[x] for x in np.unique(seg_map)]
    print("\nDetected clothes labels:", detected_labels)
    
    for label in CATEGORY_MAP.keys():
        if label in detected_labels:
            mask = (seg_map == label)
            if not np.any(mask):
                continue
                
            item_image = np.array(image.copy())
            item_image[~mask] = [255, 255, 255]
            
            image_path = os.path.join(save_dir, f"{CATEGORY_MAP[label]}.png")
            cv2.imwrite(image_path, cv2.cvtColor(item_image, cv2.COLOR_RGB2BGR))
            
            clothe_obj = ClotheObject(
                clothe_id=str(label),
                category=CATEGORY_MAP[label],
                color="unknown",
                size="unknown",
                image_path=image_path
            )
            clothes_objects.append(clothe_obj)
    
    return clothes_objects

def main(image_path: str):

    processor, model = load_model_and_processor()
    image, inputs = process_image(image_path, processor)
    logits = run_inference(model, inputs)
    seg_map = get_segmentation_map(logits, image.size)
    colored_mask = create_colored_mask(seg_map, COLOR_MAP)
    display_results(image, colored_mask)
    print_detected_items(seg_map, COLOR_MAP)

    clothes = extract_clothes(seg_map, image)
    return clothes

if __name__ == "__main__":
    detected_clothes = main("./demo_photo.jpeg")
    for clothe in detected_clothes:
        print(f"\nDetected: {clothe}")