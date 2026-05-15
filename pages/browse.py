"""
Browse Page — Product Catalog with Search & Filters
"""

import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db
from pages.home import product_card


def render(user):
    """Render the browse page."""
    st.markdown("## 🛍️ Browse Products")

    user_id = user["id"]

    # ─── Search & Filters ──────────────────────────────────
    col_search, col_cat, col_sort = st.columns([3, 2, 2])

    with col_search:
        query = st.text_input("🔍 Search products", placeholder="Search by name, category, or brand...")

    with col_cat:
        categories = ["All Categories"] + db.get_categories()
        selected_cat = st.selectbox("📂 Category", categories)

    with col_sort:
        sort_by = st.selectbox("📊 Sort by", [
            "Popularity", "Price: Low to High", "Price: High to Low",
            "Rating: High to Low", "Name A-Z"
        ])

    # ─── Price Filter ──────────────────────────────────────
    price_range = st.slider("💰 Price Range", 0, 2500, (0, 2500), step=10)

    # ─── Get Products ──────────────────────────────────────
    if query:
        products = db.search_products(query)
        # Track search
        db.record_interaction(user_id, 0, "search")
        st.caption(f"Found {len(products)} results for '{query}'")
    elif selected_cat != "All Categories":
        products = db.get_products_by_category(selected_cat)
    else:
        products = db.get_all_products()

    # Filter by price
    products = [p for p in products if price_range[0] <= p["price"] <= price_range[1]]

    # Sort
    if sort_by == "Price: Low to High":
        products.sort(key=lambda x: x["price"])
    elif sort_by == "Price: High to Low":
        products.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "Rating: High to Low":
        products.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "Name A-Z":
        products.sort(key=lambda x: x["name"])
    # Default: popularity (already sorted)

    st.caption(f"Showing {min(len(products), 50)} of {len(products)} products")
    st.divider()

    # ─── Product Grid ──────────────────────────────────────
    if not products:
        st.info("No products found. Try adjusting your filters.")
        return

    # Display in grid (5 columns)
    display_products = products[:50]
    for row_start in range(0, len(display_products), 5):
        row_items = display_products[row_start:row_start + 5]
        cols = st.columns(5)
        for i, prod in enumerate(row_items):
            formatted = {
                "product_id": prod["id"], "name": prod["name"],
                "category": prod["category"], "price": prod["price"],
                "rating": prod["rating"], "image_emoji": prod["image_emoji"],
            }
            product_card(formatted, cols[i], user_id, section=f"browse_{row_start}_{i}")
