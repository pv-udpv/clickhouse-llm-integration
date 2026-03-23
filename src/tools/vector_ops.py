"""
Vector Operations Utility
"""

import numpy as np
from typing import List

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
    """Calculate Euclidean distance"""
    return np.linalg.norm(np.array(vec1) - np.array(vec2))

def normalize_vector(vec: List[float]) -> List[float]:
    """L2 normalize vector"""
    norm = np.linalg.norm(vec)
    return (np.array(vec) / norm).tolist() if norm > 0 else vec
