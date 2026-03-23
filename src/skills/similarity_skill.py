"""
Similarity Skill - Calculate vector similarities
"""

import numpy as np
from typing import List, Tuple
from src.tools.vector_ops import (
    cosine_similarity,
    euclidean_distance,
    normalize_vector
)

class SimilaritySkill:
    """Calculate similarities between vectors"""
    
    def __init__(self, metric: str = 'cosine'):
        """
        Initialize similarity skill
        
        Args:
            metric: Distance metric ('cosine', 'euclidean', 'dot')
        """
        self.metric = metric
    
    def calculate(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score
        """
        if self.metric == 'cosine':
            return cosine_similarity(vec1, vec2)
        elif self.metric == 'euclidean':
            return 1.0 / (1.0 + euclidean_distance(vec1, vec2))
        elif self.metric == 'dot':
            return float(np.dot(vec1, vec2))
        else:
            raise ValueError(f"Unknown metric: {self.metric}")
    
    def find_most_similar(self, query_vec: List[float], 
                         candidate_vecs: List[List[float]], 
                         top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Find most similar vectors from candidates
        
        Args:
            query_vec: Query vector
            candidate_vecs: List of candidate vectors
            top_k: Number of results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        similarities = []
        
        for idx, candidate in enumerate(candidate_vecs):
            score = self.calculate(query_vec, candidate)
            similarities.append((idx, score))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def batch_calculate(self, vec1: List[float], 
                       vecs: List[List[float]]) -> List[float]:
        """
        Calculate similarities between one vector and many
        
        Args:
            vec1: Query vector
            vecs: List of vectors to compare
            
        Returns:
            List of similarity scores
        """
        return [self.calculate(vec1, vec2) for vec2 in vecs]
    
    def rerank(self, query_vec: List[float],
              candidates: List[Tuple[any, List[float]]],
              top_k: int = 10) -> List[Tuple[any, float]]:
        """
        Rerank candidates by similarity to query
        
        Args:
            query_vec: Query vector
            candidates: List of (item, vector) tuples
            top_k: Number of results
            
        Returns:
            List of (item, similarity_score) tuples
        """
        scored = []
        for item, vec in candidates:
            score = self.calculate(query_vec, vec)
            scored.append((item, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
