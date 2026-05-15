"""
Hybrid Recommendation Engine
===============================
Combines content-based, collaborative, and popularity signals.
"""

import numpy as np
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.content_based import ContentBasedEngine
from engine.collaborative import CollaborativeEngine
import database as db


class HybridEngine:
    """
    Hybrid recommendation combining:
    - Content-Based (item features)
    - Collaborative (user behavior)
    - Popularity (trending items)

    Weights adapt based on user history depth.
    """

    def __init__(self):
        self.content_engine = ContentBasedEngine()
        self.collab_engine = CollaborativeEngine()
        self.products_df = None
        self.is_fitted = False

    def fit(self):
        """Fit all sub-engines from database data."""
        products = db.get_all_products()
        if not products:
            return
        self.products_df = pd.DataFrame(products)

        # Fit content-based
        self.content_engine.fit(products)

        # Fit collaborative
        interactions = db.get_all_interactions()
        if interactions:
            inter_df = pd.DataFrame(interactions)
            inter_df = inter_df.rename(columns={"product_id": "product_id"})
            if "product_id" in inter_df.columns and "user_id" in inter_df.columns:
                self.collab_engine.fit(inter_df, self.products_df)

        self.is_fitted = True

    def get_recommendations(self, user_id, top_n=20):
        """
        Generate hybrid recommendations for a user.

        Strategy:
        - New users (< 5 interactions) -> popularity + content
        - Active users -> weighted hybrid of all three
        """
        if not self.is_fitted:
            self.fit()

        user_interactions = db.get_user_interactions(user_id, limit=200)
        interacted_ids = {i["product_id"] for i in user_interactions}
        n_interactions = len(user_interactions)

        # Adaptive weights based on history
        if n_interactions < 5:
            # Cold start: more popularity, some content
            w_content, w_collab, w_pop = 0.3, 0.0, 0.7
        elif n_interactions < 20:
            w_content, w_collab, w_pop = 0.4, 0.3, 0.3
        else:
            w_content, w_collab, w_pop = 0.35, 0.45, 0.2

        scores = {}  # product_id -> {score, name, ...}

        # 1. Content-based recommendations
        if w_content > 0 and user_interactions:
            content_recs = self.content_engine.get_user_recommendations(
                user_interactions, top_n=top_n * 3, exclude_ids=interacted_ids
            )
            for rec in content_recs:
                pid = rec["product_id"]
                if pid not in scores:
                    scores[pid] = {**rec, "content_score": 0, "collab_score": 0, "pop_score": 0}
                scores[pid]["content_score"] = rec["score"]

        # 2. Collaborative recommendations
        if w_collab > 0 and self.collab_engine.is_fitted:
            collab_recs = self.collab_engine.get_user_recommendations(
                user_id, top_n=top_n * 3, exclude_ids=interacted_ids
            )
            for rec in collab_recs:
                pid = rec["product_id"]
                if pid not in scores:
                    scores[pid] = {**rec, "content_score": 0, "collab_score": 0, "pop_score": 0}
                scores[pid]["collab_score"] = rec["score"]

        # 3. Popularity-based
        if w_pop > 0:
            trending = db.get_trending_products(limit=top_n * 2)
            max_trend = max((t.get("trend_score", 0) or 0) for t in trending) if trending else 1
            max_trend = max(max_trend, 1)
            for t in trending:
                pid = t["id"]
                if pid in interacted_ids:
                    continue
                norm_pop = (t.get("trend_score", 0) or 0) / max_trend
                if pid not in scores:
                    scores[pid] = {
                        "product_id": pid, "name": t["name"],
                        "category": t["category"], "price": t["price"],
                        "rating": t["rating"], "image_emoji": t["image_emoji"],
                        "content_score": 0, "collab_score": 0, "pop_score": 0,
                    }
                scores[pid]["pop_score"] = norm_pop

        # 4. Compute hybrid score
        for pid in scores:
            s = scores[pid]
            s["score"] = (
                w_content * s["content_score"] +
                w_collab * s["collab_score"] +
                w_pop * s["pop_score"]
            )
            s["method"] = "hybrid"

        # Sort by hybrid score
        ranked = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return ranked[:top_n]

    def get_similar_products(self, product_id, top_n=10):
        """Get similar products combining content + collaborative."""
        if not self.is_fitted:
            self.fit()

        content_sim = self.content_engine.get_similar(product_id, top_n=top_n)
        collab_sim = self.collab_engine.get_similar_items(product_id, top_n=top_n)

        # Merge scores
        merged = {}
        for r in content_sim:
            merged[r["product_id"]] = {**r, "score": r["score"] * 0.6}
        for r in collab_sim:
            pid = r["product_id"]
            if pid in merged:
                merged[pid]["score"] += r["score"] * 0.4
            else:
                merged[pid] = {**r, "score": r["score"] * 0.4}

        ranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
        return ranked[:top_n]

    def get_category_recommendations(self, user_id, top_n=10):
        """Recommend products from user's preferred categories."""
        affinities = db.get_user_category_affinity(user_id)
        if not affinities:
            return []
        top_cat = affinities[0]["category"]
        cat_products = db.get_products_by_category(top_cat)
        interacted = {i["product_id"] for i in db.get_user_interactions(user_id, limit=200)}
        results = []
        for p in cat_products:
            if p["id"] not in interacted:
                results.append({
                    "product_id": p["id"], "name": p["name"],
                    "category": p["category"], "price": p["price"],
                    "rating": p["rating"], "image_emoji": p["image_emoji"],
                    "score": p.get("popularity_score", 0),
                    "method": "category",
                })
            if len(results) >= top_n:
                break
        return results
