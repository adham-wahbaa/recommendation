"""
Collaborative Filtering Engine
=================================
User-user and item-item collaborative filtering using KNN and SVD.
"""

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix


class CollaborativeEngine:
    """Collaborative filtering using interaction matrices."""

    def __init__(self, n_neighbors=20, n_factors=50):
        self.n_neighbors = n_neighbors
        self.n_factors = n_factors
        self.user_item_matrix = None
        self.item_knn = None
        self.svd = None
        self.svd_matrix = None
        self.user_idx = None
        self.idx_user = None
        self.item_idx = None
        self.idx_item = None
        self.products_df = None
        self.is_fitted = False

    def fit(self, interactions_df, products_df):
        """
        Build user-item matrix and fit models.

        Args:
            interactions_df: DataFrame with user_id, product_id, interaction_type
            products_df: DataFrame with product info
        """
        self.products_df = products_df.copy()

        # Weight interactions
        type_weights = {"purchase": 5, "like": 3, "wishlist": 2, "view": 1, "search": 0.5}
        interactions_df = interactions_df.copy()
        interactions_df["weight"] = interactions_df["interaction_type"].map(type_weights).fillna(1)

        # Aggregate: sum weights per user-item pair
        agg = interactions_df.groupby(["user_id", "product_id"])["weight"].sum().reset_index()

        # Build index mappings
        users = agg["user_id"].unique()
        items = agg["product_id"].unique()
        self.user_idx = {u: i for i, u in enumerate(users)}
        self.idx_user = {i: u for u, i in self.user_idx.items()}
        self.item_idx = {it: i for i, it in enumerate(items)}
        self.idx_item = {i: it for it, i in self.item_idx.items()}

        # Create sparse matrix
        n_users = len(users)
        n_items = len(items)
        rows = agg["user_id"].map(self.user_idx).values
        cols = agg["product_id"].map(self.item_idx).values
        vals = agg["weight"].values
        self.user_item_matrix = csr_matrix(
            (vals, (rows, cols)), shape=(n_users, n_items)
        )

        # Item-based KNN
        item_matrix = self.user_item_matrix.T  # items x users
        self.item_knn = NearestNeighbors(
            n_neighbors=min(self.n_neighbors + 1, item_matrix.shape[0]),
            metric="cosine", algorithm="brute", n_jobs=-1
        )
        self.item_knn.fit(item_matrix)

        # SVD for latent factors
        n_comp = min(self.n_factors, min(n_users, n_items) - 1)
        if n_comp > 1:
            self.svd = TruncatedSVD(n_components=n_comp, random_state=42)
            self.svd_matrix = self.svd.fit_transform(self.user_item_matrix)

        self.is_fitted = True

    def get_similar_items(self, product_id, top_n=10):
        """Find similar items using KNN on interaction patterns."""
        if not self.is_fitted or product_id not in self.item_idx:
            return []
        idx = self.item_idx[product_id]
        item_vec = self.user_item_matrix.T[idx].toarray().reshape(1, -1)
        distances, indices = self.item_knn.kneighbors(item_vec)

        results = []
        for i in range(1, len(indices[0])):
            n_idx = indices[0][i]
            n_pid = self.idx_item.get(n_idx)
            if n_pid is None:
                continue
            sim = max(1 - distances[0][i], 0)
            prod = self.products_df[self.products_df["id"] == n_pid]
            if len(prod) == 0:
                continue
            row = prod.iloc[0]
            results.append({
                "product_id": int(n_pid),
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "rating": row["rating"],
                "image_emoji": row["image_emoji"],
                "score": float(sim),
                "method": "collaborative",
            })
            if len(results) >= top_n:
                break
        return results

    def get_user_recommendations(self, user_id, top_n=10, exclude_ids=None):
        """Recommend items for a user using SVD latent factors."""
        if not self.is_fitted or self.svd_matrix is None:
            return []
        if user_id not in self.user_idx:
            return []

        exclude = set(exclude_ids or [])
        u_idx = self.user_idx[user_id]
        user_vec = self.svd_matrix[u_idx].reshape(1, -1)

        # Project items into latent space and compute scores
        item_vecs = self.svd.transform(self.user_item_matrix.T.T)
        # Reconstruct predicted preferences
        pred = self.svd.inverse_transform(self.svd_matrix)
        scores = pred[u_idx]

        # Exclude already interacted
        for pid in exclude:
            if pid in self.item_idx:
                scores[self.item_idx[pid]] = -1

        top_indices = scores.argsort()[::-1][:top_n * 2]
        results = []
        for i in top_indices:
            pid = self.idx_item.get(i)
            if pid is None or pid in exclude or scores[i] <= 0:
                continue
            prod = self.products_df[self.products_df["id"] == pid]
            if len(prod) == 0:
                continue
            row = prod.iloc[0]
            # Normalize score to 0-1
            max_s = max(scores.max(), 1)
            results.append({
                "product_id": int(pid),
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "rating": row["rating"],
                "image_emoji": row["image_emoji"],
                "score": float(scores[i] / max_s),
                "method": "collaborative",
            })
            if len(results) >= top_n:
                break
        return results

    def get_frequently_bought_together(self, product_id, top_n=5):
        """Products frequently interacted together (purchased by same users)."""
        return self.get_similar_items(product_id, top_n)
