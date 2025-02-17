import torch
from sam2.sam2_image_predictor import SAM2ImagePredictor
from sam2.sam2_video_predictor import SAM2VideoPredictor
from PIL import Image
import numpy as np
import os
import cv2

class SimpleSAM2:
    def __init__(self, force_cpu=False):
        self.device = torch.device("cpu") if force_cpu else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        try:
           # Load the SAM2 model directly using SAM2ImagePredictor.from_pretrained
            self.image_predictor = SAM2ImagePredictor.from_pretrained("facebook/sam2-hiera-large", device=self.device)

        except Exception as e:
            print(f"Error loading SAM2 model: {e}")
            raise

    def get_prompt_box(self, image, box_coords):
        """Convert bounding box coords to prompt box for SAM2."""
        x1, y1, x2, y2 = box_coords
        bbox = [x1, y1, x2, y2]
        return bbox

    def process_image(self, image_path, box_coords, output_path):
        try:
            image = Image.open(image_path).convert("RGB")
            print(f"Loaded image from {image_path}")

            prompt_box = self.get_prompt_box(image, box_coords)
            print("Generated bounding box")

            self.image_predictor.set_image(np.array(image))

            # Updated predict method call
            # Generate masks
            masks, _, _ = self.image_predictor.predict(
                box=prompt_box,
                multimask_output=True
            )

            # Apply the mask
            final_mask = masks[0]  # select the first mask
            segmented_result = np.array(image) * final_mask[..., None]

            output_file = f"{output_path}_segmented.png"
            Image.fromarray(segmented_result.astype(np.uint8)).save(output_file)
            print(f"Saved segmented image to {output_file}")

            return segmented_result

        except Exception as e:
            print(f"Error processing image: {e}")
            raise


def segment_based_on_box(input_path, box_coords, output_path="output", force_cpu=False):
    try:
        print(f"Initializing segmentation for {input_path} with bounding box '{box_coords}'")
        segmenter = SimpleSAM2(force_cpu=force_cpu)

        if input_path.endswith(('.png', '.jpg', '.jpeg')):
            segmenter.process_image(input_path, box_coords, output_path)
        else:
            raise ValueError("Unsupported file format. Please provide an image file.")

    except Exception as e:
        print(f"Error during segmentation: {e}")
        raise


if __name__ == "__main__":
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "demo_photo.jpeg")

        # Example bounding box (x1, y1, x2, y2) - Adjust this as needed for your specific image
        bounding_box = [100, 100, 400, 400]

        segment_based_on_box(image_path, bounding_box, force_cpu=True)

    except Exception as e:
        print(f"Main execution failed: {e}")