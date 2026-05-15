"""
Product Detail Page — View, Like, Purchase, Reviews, Similar Items
"""

import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db
from pages.home import render_product_row, get_engine


def render(user):
    """Render product detail page."""
    st.markdown("## 📦 Product Details")

    user_id = user["id"]

    # Handle programmatic product change
    if "change_product_to" in st.session_state:
        st.session_state["product_selectbox"] = st.session_state["change_product_to"]
        st.session_state["selected_product"] = st.session_state["change_product_to"]
        pid = st.session_state["change_product_to"]
        del st.session_state["change_product_to"]
    else:
        pid = st.session_state.get("selected_product", None)

    all_products = db.get_all_products()
    product_names = {p["id"]: f"{p['image_emoji']} {p['name']}" for p in all_products}

    # Initialize selectbox state if needed
    if "product_selectbox" not in st.session_state and pid and pid in product_names:
        st.session_state["product_selectbox"] = pid

    selected = st.selectbox(
        "Select a product to view",
        options=list(product_names.keys()),
        format_func=lambda x: product_names.get(x, str(x)),
        key="product_selectbox",
    )

    if selected:
        st.session_state["selected_product"] = selected
        product = db.get_product(selected)

        if not product:
            st.error("Product not found.")
            return

        # Record view
        db.record_interaction(user_id, selected, "view", 60)

        # ─── Product Header ──────────────────────────────
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f"""
            <div style="text-align:center; background:linear-gradient(135deg,#1e1e2e,#2a2a3e);
                        border-radius:16px; padding:2rem; border:1px solid #333;">
                <div style="font-size:6rem;">{product['image_emoji']}</div>
                <p style="color:#888; margin-top:0.5rem;">{product['brand']}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"### {product['name']}")
            st.markdown(f"**Category:** {product['category']} > {product['subcategory']}")
            st.markdown(f"**Brand:** {product['brand']}")
            st.markdown(f"<span class='price-tag'>${product['price']:.2f}</span>",
                        unsafe_allow_html=True)
            st.markdown(f"<span class='rating-stars'>{'⭐' * int(product['rating'])} "
                        f"{product['rating']:.1f}</span> ({product['review_count']} reviews)",
                        unsafe_allow_html=True)
            st.markdown(f"_{product['description']}_")

            # Tags
            tags = product.get("tags", "").split(",")
            tag_html = " ".join(
                f'<span style="background:#333;padding:2px 8px;border-radius:12px;'
                f'font-size:0.75rem;margin:2px;">{t.strip()}</span>'
                for t in tags if t.strip()
            )
            st.markdown(tag_html, unsafe_allow_html=True)

        # ─── Action Buttons ──────────────────────────────
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("❤️ Like", use_container_width=True, type="primary"):
                db.record_interaction(user_id, selected, "like")
                st.toast("Added to liked items!")
        with c2:
            if st.button("📌 Wishlist", use_container_width=True):
                db.record_interaction(user_id, selected, "wishlist")
                st.toast("Added to wishlist!")
        with c3:
            if st.button("🛒 Purchase", use_container_width=True, type="primary"):
                db.record_interaction(user_id, selected, "purchase")
                st.toast("Purchase recorded!")
                st.balloons()
        with c4:
            if st.button("🔄 Refresh Recs", use_container_width=True):
                st.cache_resource.clear()
                st.rerun()

        st.divider()

        # ─── Reviews Section ─────────────────────────────
        st.markdown('<div class="section-title">📝 Reviews</div>', unsafe_allow_html=True)

        with st.expander("Write a Review"):
            rating = st.slider("Your Rating", 1.0, 5.0, 4.0, 0.5, key="review_rating")
            comment = st.text_area("Comment", placeholder="Share your experience...", key="review_comment")
            if st.button("Submit Review"):
                db.add_review(user_id, selected, rating, comment)
                db.record_interaction(user_id, selected, "review")
                st.success("Review submitted!")
                st.rerun()

        reviews = db.get_product_reviews(selected)
        if reviews:
            for rev in reviews[:5]:
                st.markdown(f"""
                **{rev['display_name']}** — {'⭐' * int(rev['rating'])} {rev['rating']}  
                _{rev['comment']}_
                """)
        else:
            st.caption("No reviews yet. Be the first!")

        st.divider()

        # ─── Similar Products ────────────────────────────
        engine = get_engine()
        similar = engine.get_similar_products(selected, top_n=5)
        render_product_row("🔗 Similar Products", similar, user_id)

        st.divider()

        # ─── Frequently Bought Together ──────────────────
        fbt = engine.collab_engine.get_frequently_bought_together(selected, top_n=5)
        if fbt:
            render_product_row("🛒 Frequently Bought Together", fbt, user_id)
