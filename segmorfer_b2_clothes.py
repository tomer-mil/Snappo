import torch
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# Load model and processor
processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
model = SegformerForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")

# Set model to evaluation mode
model.eval()

# Load and process image
image = Image.open("./demo_photo.jpeg")  # Replace with your image path
inputs = processor(images=image, return_tensors="pt")

# Run inference
with torch.no_grad():
    outputs = model(**inputs)

# Get predictions
logits = outputs.logits
upsampled_logits = torch.nn.functional.interpolate(
    logits,
    size=image.size[::-1],  # (height, width)
    mode="bilinear",
    align_corners=False,
)
pred_seg = upsampled_logits.argmax(dim=1)[0]

# Color mapping for different clothing items
color_map = {
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

# Create colored segmentation map
seg_map = pred_seg.cpu().numpy()
colored_mask = np.zeros((seg_map.shape[0], seg_map.shape[1], 3), dtype=np.uint8)
for label, color in color_map.items():
    mask = seg_map == label
    colored_mask[mask] = color

# Display results
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
ax1.imshow(image)
ax1.set_title('Original Image')
ax1.axis('off')

ax2.imshow(colored_mask)
ax2.set_title('Segmentation Mask')
ax2.axis('off')

# Create blended image
img_array = np.array(image)
blended = cv2.addWeighted(img_array, 0.7, colored_mask, 0.3, 0)
ax3.imshow(blended)
ax3.set_title('Blended Result')
ax3.axis('off')

plt.show()

# Print detected items
unique_labels = np.unique(seg_map)
print("\nDetected items:")
for label in unique_labels:
    if label in color_map:
        percentage = (seg_map == label).sum() / (seg_map.shape[0] * seg_map.shape[1]) * 100
        print(f"Class {label}: {percentage:.1f}% of image")