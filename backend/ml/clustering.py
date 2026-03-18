from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class TemplateClustering:
    def __init__(self, distance_threshold=0.3):
        # Using AGNES (AgglomerativeClustering)
        self.clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=distance_threshold,
            metric='cosine', # Ensure metric corresponds to the similarity you want
            linkage='average'
        )
        self.known_templates = []
        
    def add_template(self, feature_vector: np.ndarray):
        """Adds a known phishing template feature vector."""
        self.known_templates.append(feature_vector)
        
    def get_similarity(self, feature_vector: np.ndarray) -> float:
        """Returns the maximum cosine similarity to any known phishing template."""
        if not self.known_templates:
            return 0.0
            
        templates_matrix = np.vstack(self.known_templates)
        # Ensure 2D
        if len(feature_vector.shape) == 1:
            feature_vector = feature_vector.reshape(1, -1)
            
        similarities = cosine_similarity(feature_vector, templates_matrix)
        return float(np.max(similarities))
        
    def attempt_cluster(self, new_vectors: np.ndarray):
        """Re-clusters all known templates + new ones. Useful for grouping similar campaigns."""
        return self.clustering.fit_predict(new_vectors)
