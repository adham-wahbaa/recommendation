"""
Home Page — Personalized Recommendation Feed
"""

import streamlit as st
import uuid
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db
from engine.hybrid import HybridEngine


def product_card(product, col, user_id, section="sec"):
    """Render a product card with interaction buttons."""
    with col:
        pid = product.get("product_id", product.get("id"))
        emoji = product.get("image_emoji", "📦")
        name = product.get("name", "Product")
        price = product.get("price", 0)
        rating = product.get("rating", 0)
        category = product.get("category", "")
        score = product.get("score", None)

        st.markdown(f"""
        <div class="product-card">
            <div style="font-size:3rem; text-align:center; padding:0.5rem 0;">{emoji}</div>
            <p style="font-weight:600; font-size:0.95rem; margin:0.3rem 0; min-height:2.5rem;">
                {name[:45]}
            </p>
            <p style="color:#888; font-size:0.8rem; margin:0;">{category}</p>
            <p class="price-tag">${price:.2f}</p>
            <p class="rating-stars">{"⭐" * int(rating)} {rating:.1f}</p>
            {f'<p style="color:#4CAF50; font-size:0.75rem;">Match: {score:.0%}</p>' if score and score > 0 else ''}
        </div>
        """, unsafe_allow_html=True)

        uk = f"{section}_{pid}"
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("👁️", key=f"view_{uk}", help="View"):
                db.record_interaction(user_id, pid, "view", 30)
                st.session_state["selected_product"] = pid
                st.session_state["change_product_to"] = pid
                st.session_state["change_page_to"] = "📦 Product"
                st.toast(f"Viewing {name[:20]}...")
                st.rerun()
        with c2:
            if st.button("❤️", key=f"like_{uk}", help="Like"):
                db.record_interaction(user_id, pid, "like")
                st.toast(f"Liked {name[:20]}!")
        with c3:
            if st.button("🛒", key=f"buy_{uk}", help="Buy"):
                db.record_interaction(user_id, pid, "purchase")
                st.toast(f"Purchased {name[:20]}!")


def render_product_row(title, products, user_id, num_cols=5, section=None):
    """Render a horizontal row of product cards."""
    if not products:
        return
    if section is None:
        section = title.replace(" ", "_")[:20]
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    cols = st.columns(min(num_cols, len(products)))
    for i, prod in enumerate(products[:num_cols]):
        product_card(prod, cols[i % len(cols)], user_id, section=f"{section}_{i}")


@st.cache_resource
def get_engine():
    """Cached recommendation engine."""
    engine = HybridEngine()
    engine.fit()
    return engine


def render(user):
    """Render the home page."""
    st.markdown("## 🏠 Your Personalized Feed")
    st.caption("Recommendations powered by AI — they improve as you interact!")

    user_id = user["id"]

    # Get engine
    engine = get_engine()

    # ─── Recommended For You ─────────────────────────────
    recs = engine.get_recommendations(user_id, top_n=10)
    render_product_row("🎯 Recommended For You", recs, user_id)

    st.divider()

    # ─── Trending Products ───────────────────────────────
    trending = db.get_trending_products(limit=10)
    trending_formatted = [{
        "product_id": t["id"], "name": t["name"], "category": t["category"],
        "price": t["price"], "rating": t["rating"], "image_emoji": t["image_emoji"],
    } for t in trending]
    render_product_row("🔥 Trending Now", trending_formatted, user_id)

    st.divider()

    # ─── Based on Your Interests ─────────────────────────
    cat_recs = engine.get_category_recommendations(user_id, top_n=5)
    if cat_recs:
        cat_name = cat_recs[0]["category"] if cat_recs else ""
        render_product_row(f"💡 Because You Like {cat_name}", cat_recs, user_id)
        st.divider()

    # ─── Recently Viewed ─────────────────────────────────
    recent = db.get_recently_viewed(user_id, limit=5)
    if recent:
        recent_formatted = [{
            "product_id": r["id"], "name": r["name"], "category": r["category"],
            "price": r["price"], "rating": r["rating"], "image_emoji": r["image_emoji"],
        } for r in recent]
        render_product_row("🕐 Recently Viewed", recent_formatted, user_id)
