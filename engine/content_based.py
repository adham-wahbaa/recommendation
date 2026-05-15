"""
Content-Based Filtering Engine
================================
Recommends products based on item features using TF-IDF and Cosine Similarity.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedEngine:
    """Content-based recommendation using TF-IDF on product features."""

    def __init__(self):
        self.tfidf = TfidfVectorizer(
            max_features=5000, stop_words="english",
            ngram_range=(1, 2), min_df=1, max_df=0.95
        )
        self.tfidf_matrix = None
        self.products_df = None
        self.id_to_idx = None
        self.idx_to_id = None
        self.is_fitted = False

    def fit(self, products):
        """Fit on product list (list of dicts)."""
        self.products_df = pd.DataFrame(products)
        self.products_df["content"] = (
            (self.products_df["category"] + " ") * 3 +
            (self.products_df["subcategory"] + " ") * 2 +
            self.products_df["tags"].fillna("") + " " +
            self.products_df["brand"].fillna("") + " " +
            self.products_df["description"].fillna("")
        )
        self.id_to_idx = {pid: i for i, pid in enumerate(self.products_df["id"])}
        self.idx_to_id = {i: pid for pid, i in self.id_to_idx.items()}
        self.tfidf_matrix = self.tfidf.fit_transform(self.products_df["content"])
        self.is_fitted = True

    def get_similar(self, product_id, top_n=10):
        """Get products similar to a given product."""
        if not self.is_fitted or product_id not in self.id_to_idx:
            return []
        idx = self.id_to_idx[product_id]
        sim_scores = cosine_similarity(
            self.tfidf_matrix[idx], self.tfidf_matrix
        ).flatten()
        top_indices = sim_scores.argsort()[::-1][1:top_n + 1]
        results = []
        for i in top_indices:
            row = self.products_df.iloc[i]
            results.append({
                "product_id": int(row["id"]),
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "rating": row["rating"],
                "image_emoji": row["image_emoji"],
                "score": float(sim_scores[i]),
                "method": "content",
            })
        return results

    def get_user_recommendations(self, user_interactions, top_n=10, exclude_ids=None):
        """
        Recommend products for a user based on their interaction history.
        Builds a user profile from interacted items' TF-IDF vectors.
        """
        if not self.is_fitted:
            return []
        exclude = set(exclude_ids or [])
        # Weight interactions by type
        type_weights = {"purchase": 5, "like": 3, "wishlist": 2, "view": 1, "search": 0.5}
        user_vector = np.zeros(self.tfidf_matrix.shape[1])
        total_weight = 0
        for inter in user_interactions:
            pid = inter["product_id"]
            if pid not in self.id_to_idx:
                continue
            idx = self.id_to_idx[pid]
            w = type_weights.get(inter["interaction_type"], 1)
            user_vector += w * self.tfidf_matrix[idx].toarray().flatten()
            total_weight += w
        if total_weight == 0:
            return []
        user_vector /= total_weight
        sim_scores = cosine_similarity(
            user_vector.reshape(1, -1), self.tfidf_matrix
        ).flatten()
        # Exclude already interacted
        for pid in exclude:
            if pid in self.id_to_idx:
                sim_scores[self.id_to_idx[pid]] = -1
        top_indices = sim_scores.argsort()[::-1][:top_n]
        results = []
        for i in top_indices:
            if sim_scores[i] <= 0:
                continue
            row = self.products_df.iloc[i]
            results.append({
                "product_id": int(row["id"]),
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "rating": row["rating"],
                "image_emoji": row["image_emoji"],
                "score": float(sim_scores[i]),
                "method": "content",
            })
        return results
