"""
User Profile Page — Activity, Preferences, Wishlist
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db


def render(user):
    """Render user profile page."""
    st.markdown("## 👤 Your Profile")

    user_id = user["id"]

    # ─── Profile Info ────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    interactions = db.get_user_interactions(user_id, limit=1000)
    views = [i for i in interactions if i["interaction_type"] == "view"]
    likes = [i for i in interactions if i["interaction_type"] == "like"]
    purchases = [i for i in interactions if i["interaction_type"] == "purchase"]
    wishlists = [i for i in interactions if i["interaction_type"] == "wishlist"]

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(views)}</div>
            <div class="metric-label">👁️ Views</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(likes)}</div>
            <div class="metric-label">❤️ Likes</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(purchases)}</div>
            <div class="metric-label">🛒 Purchases</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(wishlists)}</div>
            <div class="metric-label">📌 Wishlist</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ─── Category Preferences (Radar Chart) ──────────────
    st.markdown('<div class="section-title">🎯 Your Category Preferences</div>',
                unsafe_allow_html=True)

    affinities = db.get_user_category_affinity(user_id)
    if affinities:
        df_aff = pd.DataFrame(affinities)
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=df_aff["affinity_score"].values,
            theta=df_aff["category"].values,
            fill="toself",
            name="Affinity",
            line=dict(color="#4CAF50"),
            fillcolor="rgba(76,175,80,0.2)",
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, df_aff["affinity_score"].max() * 1.2])),
            showlegend=False, height=400,
            template="plotly_dark",
            margin=dict(l=80, r=80, t=30, b=30),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start browsing to see your preferences!")

    st.divider()

    # ─── Interaction History ─────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["❤️ Liked", "🛒 Purchases", "📌 Wishlist", "👁️ Recent Views"])

    def show_history(items, itype):
        if not items:
            st.caption(f"No {itype} yet.")
            return
        for item in items[:20]:
            c1, c2, c3 = st.columns([1, 4, 1])
            with c1:
                st.markdown(f"<span style='font-size:2rem;'>{item.get('image_emoji','📦')}</span>",
                            unsafe_allow_html=True)
            with c2:
                st.markdown(f"**{item['name']}**")
                st.caption(f"{item['category']} · ${item['price']:.2f}")
            with c3:
                if st.button("View", key=f"hist_{itype}_{item['id']}"):
                    st.session_state["selected_product"] = item["product_id"]
                    st.session_state["change_product_to"] = item["product_id"]
                    st.session_state["change_page_to"] = "📦 Product"
                    st.rerun()

    with tab1:
        show_history(likes, "likes")
    with tab2:
        show_history(purchases, "purchases")
    with tab3:
        show_history(wishlists, "wishlist items")
    with tab4:
        show_history(views[:10], "views")
