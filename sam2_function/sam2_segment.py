import torch
from transformers import CLIPProcessor, CLIPModel
from sam2.sam2_image_predictor import SAM2ImagePredictor
from sam2.sam2_video_predictor import SAM2VideoPredictor
from PIL import Image
import numpy as np
import torch.nn.functional as F
import os


class CLIPGuidedSAM2:
    def __init__(self, force_cpu=False):
        self.device = torch.device("cpu") if force_cpu else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        try:
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", attn_implementation="eager")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = self.clip_model.to(self.device)
        except Exception as e:
            print(f"Error loading CLIP model: {e}")
            raise

        try:
            self.image_predictor = SAM2ImagePredictor.from_pretrained("facebook/sam2-hiera-large", device=self.device)
        except Exception as e:
            print(f"Error loading SAM2 model: {e}")
            raise

        # Add a projection layer for image features
        self.image_projection = torch.nn.Linear(768, 512).to(self.device)

    def get_clip_feature_map(self, image, keyword):
        """Generate feature attention map using CLIP's cross-attention with text features."""
        try:
            # Process inputs
            image_inputs = self.clip_processor(images=image, return_tensors="pt")
            text_inputs = self.clip_processor(text=[f"a {keyword}", "background"], return_tensors="pt", padding=True)

            # Move to device
            image_inputs = {k: v.to(self.device) for k, v in image_inputs.items()}
            text_inputs = {k: v.to(self.device) for k, v in text_inputs.items()}

            with torch.no_grad():
                # Get vision model outputs with attention
                vision_outputs = self.clip_model.vision_model(
                    pixel_values=image_inputs['pixel_values'], output_attentions=True, output_hidden_states=True
                )

                # Get text features
                text_outputs = self.clip_model.text_model(**text_inputs)
                text_features = text_outputs[1]  # Text embeddings (last hidden state)

                # Project text features
                text_features = self.clip_model.text_projection(text_features)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)

                # Get image features from intermediate layers
                image_features = vision_outputs.hidden_states[-1].mean(dim=1)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)

                # Project image features to match text feature dimensions
                image_features = self.image_projection(image_features)

                # Compute similarity between image and text features
                similarity = torch.matmul(image_features, text_features.transpose(-1, -2))

                # Get attention for target vs background
                target_attention = similarity[:, 0].reshape(-1)
                background_attention = similarity[:, 1].reshape(-1)

                # Compute relative attention
                relative_attention = torch.sigmoid(target_attention - background_attention)

                # Reshape to square feature map
                size = int(np.sqrt(relative_attention.shape[0]))
                attention_map = relative_attention.reshape(size, size)

                # Upscale to image size
                attention_map = F.interpolate(
                    attention_map.unsqueeze(0).unsqueeze(0), size=image.size[::-1], mode='bicubic', align_corners=False
                ).squeeze()

                return attention_map.cpu().numpy()

        except Exception as e:
            print(f"Error generating feature map: {e}")
            raise


    def get_prompt_points(self, attention_map, threshold=0.5, min_points=3, max_points=5):
        """Convert attention map to prompt points with adaptive thresholding."""
        try:
            # Normalize attention map
            attention_map = (attention_map - attention_map.min()) / (attention_map.max() - attention_map.min())

            # Adaptive thresholding to ensure we get enough points
            while threshold > 0.2:  # Don't go too low
                high_attention = attention_map > threshold
                coords = np.column_stack(np.where(high_attention))

                if len(coords) >= min_points:
                    break

                threshold -= 0.1

            # If we still don't have enough points, take the top N highest attention points
            if len(coords) < min_points:
                flat_indices = np.argsort(attention_map.ravel())[-max_points:]
                coords = np.array(np.unravel_index(flat_indices, attention_map.shape)).T

            # If we have too many points, select a diverse subset
            if len(coords) > max_points:
                selected_coords = []
                remaining_coords = coords.copy()

                # Always include the highest attention point
                highest_idx = np.argmax([attention_map[tuple(coord)] for coord in coords])
                selected_coords.append(coords[highest_idx])
                remaining_coords = np.delete(remaining_coords, highest_idx, axis=0)

                # Add points that are furthest from already selected points
                while len(selected_coords) < max_points and len(remaining_coords) > 0:
                    distances = []
                    for coord in remaining_coords:
                        min_dist = min(np.linalg.norm(coord - sel_coord) for sel_coord in selected_coords)
                        distances.append(min_dist)

                    furthest_idx = np.argmax(distances)
                    selected_coords.append(remaining_coords[furthest_idx])
                    remaining_coords = np.delete(remaining_coords, furthest_idx, axis=0)

                coords = np.array(selected_coords)

            return coords

        except Exception as e:
            print(f"Error generating prompt points: {e}")
            raise

    def process_image(self, image_path, keyword, output_path):
        try:
            image = Image.open(image_path).convert("RGB")
            print(f"Loaded image from {image_path}")

            attention_map = self.get_clip_feature_map(image, keyword)
            print("Generated attention map")

            prompt_points = self.get_prompt_points(attention_map)
            print(f"Generated {len(prompt_points)} prompt points")

            self.image_predictor.set_image(np.array(image))

            # Updated predict method call
            masks, _, _ = self.image_predictor.predict(
                point_coords=prompt_points,
                point_labels=np.ones(len(prompt_points)),
                multimask_output=True  # Retain only supported arguments
            )
            print("Generated masks")

            # Apply a threshold manually if needed
            mask_threshold = 0.5
            masks = (masks > mask_threshold).astype(np.uint8)

            # Select best mask based on correlation with attention map
            best_mask_idx = 0
            best_correlation = -1
            for i, mask in enumerate(masks):
                correlation = np.corrcoef(attention_map.flatten(), mask.flatten())[0, 1]
                if correlation > best_correlation:
                    best_correlation = correlation
                    best_mask_idx = i

            result = np.array(image) * masks[best_mask_idx][..., None]

            output_file = f"{output_path}_segmented.png"
            Image.fromarray(result.astype(np.uint8)).save(output_file)
            print(f"Saved segmented image to {output_file}")

            return result

        except Exception as e:
            print(f"Error processing image: {e}")
            raise

        except Exception as e:
            print(f"Error processing image: {e}")
            raise


def segment_based_on_keyword(input_path, keyword, output_path="output", force_cpu=False):
    try:
        print(f"Initializing segmentation for {input_path} with keyword '{keyword}'")
        segmenter = CLIPGuidedSAM2(force_cpu=force_cpu)

        if input_path.endswith(('.png', '.jpg', '.jpeg')):
            segmenter.process_image(input_path, keyword, output_path)
        else:
            raise ValueError("Unsupported file format. Please provide an image file.")

    except Exception as e:
        print(f"Error during segmentation: {e}")
        raise


if __name__ == "__main__":
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "demo_photo.jpeg")

        segment_based_on_keyword(image_path, "shirt", force_cpu=True)

    except Exception as e:
        print(f"Main execution failed: {e}")