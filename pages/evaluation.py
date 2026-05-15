"""
Evaluation Page — Model Performance, EDA, and ML Metrics
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db
from pages.home import get_engine


def precision_at_k(recommended_ids, relevant_ids, k):
    rec = recommended_ids[:k]
    hits = len(set(rec) & set(relevant_ids))
    return hits / k if k > 0 else 0


def recall_at_k(recommended_ids, relevant_ids, k):
    rec = recommended_ids[:k]
    hits = len(set(rec) & set(relevant_ids))
    return hits / len(relevant_ids) if relevant_ids else 0


def ndcg_at_k(recommended_ids, relevant_ids, k):
    rec = recommended_ids[:k]
    dcg = sum(1.0 / np.log2(i + 2) for i, r in enumerate(rec) if r in relevant_ids)
    ideal = min(len(relevant_ids), k)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(ideal))
    return dcg / idcg if idcg > 0 else 0


def render(user):
    """Render evaluation page."""
    st.markdown("## 🧪 Model Evaluation & EDA")
    st.caption("Machine Learning model performance and data analysis")

    engine = get_engine()

    tab1, tab2, tab3 = st.tabs(["📏 Model Evaluation", "🔬 EDA", "📊 Similarity Analysis"])

    # ─── Tab 1: Model Evaluation ─────────────────────────
    with tab1:
        st.markdown("### Recommendation Model Comparison")
        st.markdown("""
        We evaluate three approaches using standard IR metrics:
        - **Content-Based**: TF-IDF + Cosine Similarity
        - **Collaborative**: KNN + SVD Matrix Factorization
        - **Hybrid**: Weighted combination of both + popularity
        """)

        if st.button("▶️ Run Evaluation", type="primary"):
            with st.spinner("Evaluating models on test users..."):
                results = evaluate_models(engine)

            if results:
                df_results = pd.DataFrame(results)
                st.dataframe(df_results.style.format({
                    "Precision@5": "{:.4f}", "Precision@10": "{:.4f}",
                    "Recall@5": "{:.4f}", "Recall@10": "{:.4f}",
                    "NDCG@5": "{:.4f}", "NDCG@10": "{:.4f}",
                    "Coverage": "{:.2%}",
                }), use_container_width=True)

                # Bar chart comparison
                metrics = ["Precision@5", "Precision@10", "Recall@5", "Recall@10", "NDCG@5", "NDCG@10"]
                fig = go.Figure()
                colors = ["#2196F3", "#E91E63", "#4CAF50"]
                for i, (_, row) in enumerate(df_results.iterrows()):
                    fig.add_trace(go.Bar(
                        name=row["Model"],
                        x=metrics,
                        y=[row[m] for m in metrics],
                        marker_color=colors[i % len(colors)],
                    ))
                fig.update_layout(
                    barmode="group", template="plotly_dark", height=400,
                    title="Model Comparison", yaxis_title="Score",
                    margin=dict(l=20, r=20, t=50, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Click 'Run Evaluation' to compare recommendation models.")

    # ─── Tab 2: EDA ──────────────────────────────────────
    with tab2:
        st.markdown("### Exploratory Data Analysis")

        products_df = pd.DataFrame(db.get_all_products())

        # Dataset overview
        st.markdown("#### Dataset Overview")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Products", len(products_df))
            st.metric("Categories", products_df["category"].nunique())
            st.metric("Brands", products_df["brand"].nunique())
        with col2:
            st.metric("Avg Price", f"${products_df['price'].mean():.2f}")
            st.metric("Avg Rating", f"{products_df['rating'].mean():.2f}")
            stats = db.get_interaction_stats()
            st.metric("Interactions", f"{stats['total_interactions']:,}")

        st.divider()

        # Products per category
        st.markdown("#### Products per Category")
        cat_counts = products_df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig = px.bar(cat_counts, x="Category", y="Count",
                     color="Count", color_continuous_scale="Viridis")
        fig.update_layout(template="plotly_dark", height=350,
                          coloraxis_showscale=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

        # Price by category
        st.markdown("#### Price Distribution by Category")
        fig = px.violin(products_df, x="category", y="price", color="category",
                        color_discrete_sequence=px.colors.qualitative.Set2, box=True)
        fig.update_layout(template="plotly_dark", height=400, showlegend=False,
                          xaxis_tickangle=-30, xaxis_title="", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)

        # Rating distribution
        st.markdown("#### Rating Distribution")
        fig = px.histogram(products_df, x="rating", nbins=30,
                           color_discrete_sequence=["#FFC107"], marginal="box")
        fig.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)

        # Correlation heatmap
        st.markdown("#### Feature Correlations")
        num_cols = ["price", "rating", "review_count", "popularity_score"]
        existing = [c for c in num_cols if c in products_df.columns]
        if existing:
            corr = products_df[existing].corr()
            fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                            aspect="auto")
            fig.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig, use_container_width=True)

    # ─── Tab 3: Similarity Analysis ──────────────────────
    with tab3:
        st.markdown("### Similarity Quality Assessment")
        st.markdown("Evaluate how well the content-based model finds genuinely similar products.")

        if st.button("▶️ Run Similarity Test", type="primary"):
            with st.spinner("Testing similarity quality..."):
                results = test_similarity(engine)

            if results:
                st.metric("Average Genre Overlap", f"{results['avg_overlap']:.1%}")
                st.markdown("Higher genre overlap = better content similarity")

                df_sim = pd.DataFrame(results["details"])
                fig = px.bar(df_sim, x="product", y="genre_overlap",
                             color="genre_overlap", color_continuous_scale="Viridis")
                fig.update_layout(template="plotly_dark", height=400,
                                  xaxis_tickangle=-45, coloraxis_showscale=False,
                                  yaxis_title="Genre Overlap Score")
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(df_sim, use_container_width=True)


def evaluate_models(engine):
    """Evaluate recommendation models."""
    all_users = db.get_all_users()
    products = db.get_all_products()
    all_pids = set(p["id"] for p in products)

    results = []
    for model_name, model_type in [
        ("Content-Based", "content"),
        ("Collaborative", "collab"),
        ("Hybrid", "hybrid"),
    ]:
        precisions_5, precisions_10 = [], []
        recalls_5, recalls_10 = [], []
        ndcgs_5, ndcgs_10 = [], []
        all_recommended = set()

        for u in all_users[:20]:
            uid = u["id"]
            interactions = db.get_user_interactions(uid, limit=500)
            if len(interactions) < 10:
                continue

            # Split 80/20
            np.random.seed(42)
            np.random.shuffle(interactions)
            split = int(len(interactions) * 0.8)
            test = interactions[split:]
            relevant = {i["product_id"] for i in test
                        if i["interaction_type"] in ("purchase", "like")}
            if not relevant:
                continue

            # Get recommendations
            try:
                if model_type == "content":
                    recs = engine.content_engine.get_user_recommendations(
                        interactions[:split], top_n=20,
                        exclude_ids={i["product_id"] for i in interactions[:split]}
                    )
                elif model_type == "collab":
                    recs = engine.collab_engine.get_user_recommendations(
                        uid, top_n=20,
                        exclude_ids={i["product_id"] for i in interactions[:split]}
                    )
                else:
                    recs = engine.get_recommendations(uid, top_n=20)

                rec_ids = [r["product_id"] for r in recs]
                all_recommended.update(rec_ids)

                precisions_5.append(precision_at_k(rec_ids, relevant, 5))
                precisions_10.append(precision_at_k(rec_ids, relevant, 10))
                recalls_5.append(recall_at_k(rec_ids, relevant, 5))
                recalls_10.append(recall_at_k(rec_ids, relevant, 10))
                ndcgs_5.append(ndcg_at_k(rec_ids, relevant, 5))
                ndcgs_10.append(ndcg_at_k(rec_ids, relevant, 10))
            except Exception:
                continue

        coverage = len(all_recommended) / len(all_pids) if all_pids else 0

        results.append({
            "Model": model_name,
            "Precision@5": np.mean(precisions_5) if precisions_5 else 0,
            "Precision@10": np.mean(precisions_10) if precisions_10 else 0,
            "Recall@5": np.mean(recalls_5) if recalls_5 else 0,
            "Recall@10": np.mean(recalls_10) if recalls_10 else 0,
            "NDCG@5": np.mean(ndcgs_5) if ndcgs_5 else 0,
            "NDCG@10": np.mean(ndcgs_10) if ndcgs_10 else 0,
            "Coverage": coverage,
        })

    return results


def test_similarity(engine):
    """Test content-based similarity quality via genre overlap."""
    products = db.get_all_products()
    products_df = pd.DataFrame(products)

    # Top 15 popular products
    test_products = products_df.nlargest(15, "popularity_score")
    details = []
    overlaps = []

    for _, row in test_products.iterrows():
        pid = row["id"]
        try:
            similar = engine.content_engine.get_similar(pid, top_n=10)
            if not similar:
                continue
            source_cat = row["category"]
            cat_matches = sum(1 for s in similar if s["category"] == source_cat)
            overlap = cat_matches / len(similar)
            overlaps.append(overlap)
            details.append({
                "product": row["name"][:35],
                "category": source_cat,
                "genre_overlap": overlap,
            })
        except Exception:
            continue

    return {
        "avg_overlap": np.mean(overlaps) if overlaps else 0,
        "details": details,
    }
