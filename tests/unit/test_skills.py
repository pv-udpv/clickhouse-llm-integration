"""
Unit tests for Skills
"""

import pytest
import numpy as np
from src.skills.similarity_skill import SimilaritySkill

class TestSimilaritySkill:
    """Test similarity skill"""
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        skill = SimilaritySkill(metric='cosine')
        
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        similarity = skill.calculate(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001
    
    def test_orthogonal_vectors(self):
        """Test orthogonal vectors"""
        skill = SimilaritySkill(metric='cosine')
        
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        
        similarity = skill.calculate(vec1, vec2)
        assert abs(similarity) < 0.001
    
    def test_find_most_similar(self):
        """Test finding most similar vectors"""
        skill = SimilaritySkill(metric='cosine')
        
        query = [1.0, 0.0, 0.0]
        candidates = [
            [0.9, 0.1, 0.0],  # Most similar
            [0.0, 1.0, 0.0],  # Orthogonal
            [0.8, 0.2, 0.0],  # Similar
        ]
        
        results = skill.find_most_similar(query, candidates, top_k=2)
        
        assert len(results) == 2
        assert results[0][0] == 0  # Index of most similar
        assert results[0][1] > results[1][1]  # Scores in descending order
    
    def test_batch_calculate(self):
        """Test batch calculation"""
        skill = SimilaritySkill(metric='cosine')
        
        query = [1.0, 0.0]
        vecs = [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.5, 0.5],
        ]
        
        similarities = skill.batch_calculate(query, vecs)
        
        assert len(similarities) == 3
        assert similarities[0] > similarities[2] > similarities[1]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
