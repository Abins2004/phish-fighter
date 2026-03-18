import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

class VisualFeatureExtractor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Load pre-trained EfficientNet-B0
        self.model = models.efficientnet_b0(pretrained=True).to(self.device)
        # Remove the final classification layer to get the 1280-dim embedding
        self.model.classifier = nn.Identity()
        self.model.eval()
        
        # Standard ImageNet normalization
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def extract_features(self, image_path: str) -> torch.Tensor:
        try:
            image = Image.open(image_path).convert("RGB")
            input_tensor = self.preprocess(image)
            input_batch = input_tensor.unsqueeze(0).to(self.device)

            with torch.no_grad():
                features = self.model(input_batch)
                
            return features.squeeze(0)
        except Exception as e:
            print(f"Error extracting visual features from {image_path}: {e}")
            return torch.zeros(1280).to(self.device) # EfficientNet-B0 embedding size
