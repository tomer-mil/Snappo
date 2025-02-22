import torch
from PIL.ImageFile import ImageFile
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from transformers.image_processing_base import BatchFeature


class ClothesSegmorfer:

    model: SegformerForSemanticSegmentation
    processor: SegformerImageProcessor

    image: ImageFile
    inputs = None


    seg_map: torch.Tensor
    colored_mask: np.ndarray

    label_to_name = {
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
    color_map = {
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


    def __init__(self, image_bytes):
        self.processor, self.model = self.load_model()
        self.image = Image.open(image_bytes)

    ##################################
    ### Clothes Extraction Methods ###
    ##################################
    @staticmethod
    def load_model():
        processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
        model = SegformerForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
        model.eval()
        return processor, model


    def process_image_inputs(self):
        self.inputs = self.processor(images=self.image, return_tensors="pt")


    def get_segmentation_map(self):
        self.process_image_inputs()

        with torch.no_grad():
            outputs = self.model(**self.inputs)

        logits = outputs.logits
        upsampled_logits = torch.nn.functional.interpolate(
            logits,
            size=self.image.size[::-1],  # (height, width)
            mode="bilinear",
            align_corners=False,
        )
        return upsampled_logits.argmax(dim=1)[0]


    def extract_clothes(self) -> list[dict]:
        """Extract individual clothing items from the segmented image."""
        detected_items = []
        img_array = np.array(self.image)
        unique_labels = np.unique(self.seg_map.cpu().numpy())

        for label in unique_labels:
            if label not in self.label_to_name:
                continue

            # Get masked crop
            cropped_img, cropped_mask = self.create_masked_crop(label, img_array)
            if cropped_img is None:
                continue

            # Create transparent image
            rgba = self.create_transparent_crop(cropped_img, cropped_mask)

            # Create final image with white background
            background = Image.new('RGB', (rgba.shape[1], rgba.shape[0]), (255, 255, 255))
            pil_image = Image.fromarray(rgba)
            background.paste(pil_image, (0, 0), pil_image)

            detected_items.append({
                "clothe_type": self.label_to_name[label],
                "image": background
            })

        return detected_items


    def get_clothes_from_image(self) -> list[dict]:
        # Get segmentation map
        self.seg_map = self.get_segmentation_map()

        # Extract clothes using segmentation map
        detected_items = self.extract_clothes()
        return detected_items

        # Print statistics
        # print_detected_items(seg_map.cpu().numpy(), color_map)


    ##################################################
    ### Extracted Clothes Image Processing Methods ###
    ##################################################
    @staticmethod
    def create_transparent_crop(cropped_img, cropped_mask):
        """Create transparent RGBA image from cropped image and mask."""
        rgba = np.zeros((cropped_img.shape[0], cropped_img.shape[1], 4), dtype=np.uint8)
        rgba[..., :3] = cropped_img
        rgba[..., 3] = cropped_mask * 255
        return rgba


    def create_mask_and_indices(self, label):
        """Create binary mask and get indices for a clothing item."""
        mask = (self.seg_map == label).cpu().numpy()
        if not np.any(mask):
            return None, None, None

        y_indices, x_indices = np.where(mask)
        if len(y_indices) == 0 or len(x_indices) == 0:
            return None, None, None

        return mask, y_indices, x_indices


    def get_bounding_box(self, indices, padding=5):
        """Calculate padded bounding box coordinates."""
        y_indices, x_indices = indices
        y_min = max(0, np.min(y_indices) - padding)
        y_max = min(self.seg_map.shape[0], np.max(y_indices) + padding)
        x_min = max(0, np.min(x_indices) - padding)
        x_max = min(self.seg_map.shape[1], np.max(x_indices) + padding)
        return y_min, y_max, x_min, x_max


    def create_masked_crop(self, label, img_array):
        """Create masked crop of an image for a given label.

        Args:
            label: Label ID to create mask for
            img_array: Source image array

        Returns:
            tuple: (cropped_img, cropped_mask) or (None, None) if no mask found
        """
        # Get mask and indices
        mask, y_indices, x_indices = self.create_mask_and_indices(label)
        if mask is None:
            return None, None

        # Get bounding box
        y_min, y_max, x_min, x_max = self.get_bounding_box((y_indices, x_indices))

        # Crop image and mask
        cropped_img = img_array[y_min:y_max + 1, x_min:x_max + 1].copy()
        cropped_mask = mask[y_min:y_max + 1, x_min:x_max + 1]

        return cropped_img, cropped_mask


    ##########################################
    ### Presenting Model's Results Methods ###
    ##########################################
    @staticmethod
    def display_extracted_clothes_plot(clothes_list: list[dict]):
        """Plot each extracted clothing item with its type label."""
        num_items = len(clothes_list)
        if num_items == 0:
            print("No clothes detected in the image.")
            return

        # Calculate grid dimensions
        cols = min(4, num_items)  # Maximum 4 items per row
        rows = (num_items + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
        if rows == 1 and cols == 1:
            axes = np.array([axes])
        axes = axes.flatten()

        # Plot each clothing item
        for idx, item in enumerate(clothes_list):
            axes[idx].imshow(item["image"])
            axes[idx].set_title(item["clothe_type"].replace('_', ' ').title())
            axes[idx].axis('off')

        # Turn off any remaining empty subplots
        for idx in range(num_items, len(axes)):
            axes[idx].axis('off')

        plt.tight_layout()
        plt.show()


    def display_segmentation_plot(self):
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
        colored_mask = self.create_colored_mask()

        # Original image
        ax1.imshow(self.image)
        ax1.set_title('Original Image')
        ax1.axis('off')

        # Segmentation mask
        ax2.imshow(colored_mask)
        ax2.set_title('Segmentation Mask')
        ax2.axis('off')

        # Blended result
        img_array = np.array(self.image)
        blended = cv2.addWeighted(img_array, 0.7, colored_mask, 0.3, 0)
        ax3.imshow(blended)
        ax3.set_title('Blended Result')
        ax3.axis('off')

        plt.show()


    def create_colored_mask(self):
        colored_mask = np.zeros((self.seg_map.shape[0], self.seg_map.shape[1], 3), dtype=np.uint8)
        for label, color in self.color_map.items():
            mask = self.seg_map == label
            colored_mask[mask] = color
        return colored_mask


    def print_detected_items(self):
        unique_labels = np.unique(self.seg_map)
        print("\nDetected items:")
        for label in unique_labels:
            if label in self.color_map:
                percentage = (self.seg_map == label).sum() / (self.seg_map.shape[0] * self.seg_map.shape[1]) * 100
                print(f"Class {label}: {percentage:.1f}% of image")

    @staticmethod
    def test_clothes_extraction(image_url="media/demo_photo_0.jpeg"):
        segmorfer = ClothesSegmorfer(image_url)
        clothes = segmorfer.get_clothes_from_image()
        segmorfer.display_segmentation_plot()
        segmorfer.display_extracted_clothes_plot(clothes_list=clothes)