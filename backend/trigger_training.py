import sys
import os
import shutil

# Ensure backend directory is in path
sys.path.append('c:/honours/phish-fighter/backend')

from ml.dataset import DatasetManager
from ml.models import ClassificationModels

# 1. First delete the old 5-feature models so they don't corrupt the training run
model_dir = "c:/honours/phish-fighter/backend/data/models"
if os.path.exists(model_dir):
    shutil.rmtree(model_dir)

# 2. Instantiate systems
dm = DatasetManager()
ml = ClassificationModels()

# 3. Get the new massive 30-feature vector dataset
X, y = dm.get_training_data()

# 4. Train!
print(f"Beginning training across {len(X)} records and {len(X[0]) if len(X) > 0 else 0} dimensions...")
ml.train(X, y)
print("Finished compiling AI Models.")
