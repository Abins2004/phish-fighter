import torch
import torch.nn as nn
import os

class MultiModalFusionModel(nn.Module):
    def __init__(self, visual_dim=1280, semantic_dim=384, structured_dim=15, hidden_dim=256):
        super(MultiModalFusionModel, self).__init__()
        
        # Total concatenated input simply adds the dimensions
        input_dim = visual_dim + semantic_dim + structured_dim
        
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_dim, 64)
        self.fc3 = nn.Linear(64, 1) # Single output for phishing probability
        self.sigmoid = nn.Sigmoid()

    def forward(self, visual_feat, semantic_feat, structured_feat):
        # Concatenate features along the feature dimension
        combined = torch.cat((visual_feat, semantic_feat, structured_feat), dim=1)
        
        x = self.fc1(combined)
        x = self.relu(x)
        x = self.dropout(x)
        
        x = self.fc2(x)
        x = self.relu(x)
        
        x = self.fc3(x)
        out = self.sigmoid(x)
        
        return out

class FusionPipeline:
    def __init__(self, model_dir="backend/data/models"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = MultiModalFusionModel().to(self.device)
        self.model_dir = model_dir
        
    def save_model(self):
        os.makedirs(self.model_dir, exist_ok=True)
        torch.save(self.model.state_dict(), os.path.join(self.model_dir, 'fusion_model.pth'))
        
    def load_model(self):
        model_path = os.path.join(self.model_dir, 'fusion_model.pth')
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            
    def predict(self, visual: torch.Tensor, semantic: torch.Tensor, structured: torch.Tensor) -> float:
        self.model.eval()
        with torch.no_grad():
            # Ensure tensors have batch dimension
            if visual.dim() == 1: visual = visual.unsqueeze(0)
            if semantic.dim() == 1: semantic = semantic.unsqueeze(0)
            if structured.dim() == 1: structured = structured.unsqueeze(0)
            
            output = self.model(visual, semantic, structured)
            return output.item()
