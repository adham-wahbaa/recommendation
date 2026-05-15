"""
Analytics Dashboard — Platform-wide analytics and visualizations
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db


def render(user):
    """Render analytics dashboard."""
    st.markdown("## 📊 Analytics Dashboard")
    st.caption("Platform-wide insights and data visualizations")

    stats = db.get_interaction_stats()

    # ─── Key Metrics ─────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("👥 Total Users", f"{stats['total_users']:,}")
    with c2:
        st.metric("📦 Total Products", f"{stats['total_products']:,}")
    with c3:
        st.metric("🔄 Total Interactions", f"{stats['total_interactions']:,}")
    with c4:
        st.metric("⭐ Total Reviews", f"{stats['total_reviews']:,}")

    st.divider()

    # ─── Interaction Type Distribution ────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">📊 Interaction Types</div>', unsafe_allow_html=True)
        if stats["by_type"]:
            df_types = pd.DataFrame(
                list(stats["by_type"].items()),
                columns=["Type", "Count"]
            )
            fig = px.pie(df_types, values="Count", names="Type",
                         color_discrete_sequence=px.colors.qualitative.Set2,
                         hole=0.4)
            fig.update_layout(template="plotly_dark", height=350,
                              margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">🏷️ Category Popularity</div>', unsafe_allow_html=True)
        if stats["by_category"]:
            df_cats = pd.DataFrame(
                list(stats["by_category"].items()),
                columns=["Category", "Interactions"]
            ).sort_values("Interactions", ascending=True)
            fig = px.bar(df_cats, x="Interactions", y="Category", orientation="h",
                         color="Interactions", color_continuous_scale="Viridis")
            fig.update_layout(template="plotly_dark", height=350,
                              margin=dict(l=20, r=20, t=30, b=20),
                              showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ─── Top Products ────────────────────────────────────
    st.markdown('<div class="section-title">🏆 Top 15 Products by Interaction Volume</div>',
                unsafe_allow_html=True)

    with db.get_db() as conn:
        rows = conn.execute("""
            SELECT p.name, p.category, p.image_emoji, COUNT(i.id) as interactions,
                   SUM(CASE WHEN i.interaction_type='purchase' THEN 1 ELSE 0 END) as purchases,
                   SUM(CASE WHEN i.interaction_type='like' THEN 1 ELSE 0 END) as likes,
                   SUM(CASE WHEN i.interaction_type='view' THEN 1 ELSE 0 END) as views
            FROM products p
            LEFT JOIN interactions i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY interactions DESC LIMIT 15
        """).fetchall()
        df_top = pd.DataFrame([dict(r) for r in rows])

    if not df_top.empty:
        fig = px.bar(df_top, x="name", y=["views", "likes", "purchases"],
                     title="",
                     color_discrete_sequence=["#2196F3", "#E91E63", "#4CAF50"],
                     barmode="stack")
        fig.update_layout(template="plotly_dark", height=400, xaxis_tickangle=-45,
                          margin=dict(l=20, r=20, t=30, b=100),
                          legend_title="Type", xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ─── User Activity Distribution ──────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">👥 User Activity Distribution</div>',
                    unsafe_allow_html=True)
        with db.get_db() as conn:
            rows = conn.execute("""
                SELECT u.username, u.display_name, COUNT(i.id) as interactions
                FROM users u LEFT JOIN interactions i ON u.id = i.user_id
                GROUP BY u.id ORDER BY interactions DESC
            """).fetchall()
            df_users = pd.DataFrame([dict(r) for r in rows])

        if not df_users.empty:
            fig = px.bar(df_users, x="display_name", y="interactions",
                         color="interactions", color_continuous_scale="Viridis")
            fig.update_layout(template="plotly_dark", height=350,
                              margin=dict(l=20, r=20, t=30, b=60),
                              coloraxis_showscale=False, xaxis_title="", yaxis_title="Interactions")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">💰 Price Distribution by Category</div>',
                    unsafe_allow_html=True)
        with db.get_db() as conn:
            rows = conn.execute(
                "SELECT category, price FROM products"
            ).fetchall()
            df_prices = pd.DataFrame([dict(r) for r in rows])

        if not df_prices.empty:
            fig = px.box(df_prices, x="category", y="price",
                         color="category", color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(template="plotly_dark", height=350,
                              margin=dict(l=20, r=20, t=30, b=100),
                              showlegend=False, xaxis_tickangle=-45,
                              xaxis_title="", yaxis_title="Price ($)")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ─── Rating Distribution ─────────────────────────────
    st.markdown('<div class="section-title">⭐ Product Rating Distribution</div>',
                unsafe_allow_html=True)
    with db.get_db() as conn:
        rows = conn.execute("SELECT rating FROM products WHERE rating > 0").fetchall()
        ratings = [r["rating"] for r in rows]

    if ratings:
        fig = px.histogram(pd.DataFrame({"Rating": ratings}), x="Rating", nbins=20,
                           color_discrete_sequence=["#FFC107"])
        fig.update_layout(template="plotly_dark", height=300,
                          margin=dict(l=20, r=20, t=30, b=20),
                          xaxis_title="Rating", yaxis_title="Number of Products")
        st.plotly_chart(fig, use_container_width=True)

    # ─── Conversion Analysis ─────────────────────────────
    st.markdown('<div class="section-title">📈 Conversion Funnel</div>', unsafe_allow_html=True)
    by_type = stats.get("by_type", {})
    funnel_data = pd.DataFrame({
        "Stage": ["Views", "Likes", "Wishlist", "Purchases"],
        "Count": [
            by_type.get("view", 0),
            by_type.get("like", 0),
            by_type.get("wishlist", 0),
            by_type.get("purchase", 0),
        ]
    })
    fig = go.Figure(go.Funnel(
        y=funnel_data["Stage"],
        x=funnel_data["Count"],
        textinfo="value+percent initial",
        marker=dict(color=["#2196F3", "#E91E63", "#FF9800", "#4CAF50"]),
    ))
    fig.update_layout(template="plotly_dark", height=300,
                      margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)
