"""
AI-Powered E-Commerce Recommendation System
=============================================
Main Streamlit application entry point.
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, authenticate_user, create_user, get_user
from generate_dataset import populate_database


def setup():
    """Initialize database and populate if needed."""
    init_db()
    populate_database()


def login_page():
    """Render login/signup page."""
    st.markdown("""
    <div style="text-align:center; padding:2rem 0;">
        <h1 style="font-size:3rem;">🛒 SmartShop AI</h1>
        <p style="font-size:1.2rem; color:#888;">
            AI-Powered Product Recommendations
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
            if submitted:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state["user"] = user
                        st.session_state["logged_in"] = True
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.warning("Please fill in all fields.")

        st.info("**Demo account:** username `demo` / password `demo`")

    with tab2:
        with st.form("signup_form"):
            new_user = st.text_input("Username", placeholder="Choose a username", key="su_user")
            new_email = st.text_input("Email", placeholder="your@email.com", key="su_email")
            new_pass = st.text_input("Password", type="password", placeholder="Choose password", key="su_pass")
            new_name = st.text_input("Display Name", placeholder="Your name", key="su_name")
            signed = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            if signed:
                if new_user and new_email and new_pass:
                    uid = create_user(new_user, new_email, new_pass, new_name or new_user)
                    if uid:
                        st.success("Account created! Please login.")
                    else:
                        st.error("Username or email already exists.")
                else:
                    st.warning("Please fill in all fields.")


def main():
    st.set_page_config(
        page_title="SmartShop AI - Recommendation System",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS
    st.markdown("""
    <style>
    .stApp { }
    .product-card {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border-radius: 12px; padding: 1rem;
        border: 1px solid #333; transition: transform 0.2s;
        height: 100%;
    }
    .product-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }
    .price-tag { color: #4CAF50; font-size: 1.3rem; font-weight: bold; }
    .rating-stars { color: #FFC107; }
    .section-title {
        font-size: 1.4rem; font-weight: 600;
        border-left: 4px solid #4CAF50; padding-left: 12px;
        margin: 1.5rem 0 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 10px; padding: 1.2rem; text-align: center;
        border: 1px solid #333;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #4CAF50; }
    .metric-label { color: #888; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

    # Init
    setup()

    # Auth check
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        login_page()
        return

    # Handle programmatic navigation
    if "change_page_to" in st.session_state:
        st.session_state["nav_radio"] = st.session_state["change_page_to"]
        del st.session_state["change_page_to"]

    # Sidebar
    user = st.session_state["user"]
    with st.sidebar:
        st.markdown(f"### 👋 Hello, {user['display_name']}!")
        st.caption(f"@{user['username']}")
        st.divider()

        page = st.radio(
            "Navigation",
            ["🏠 Home", "🛍️ Browse", "📦 Product", "👤 Profile",
             "📊 Analytics", "🧪 Evaluation"],
            label_visibility="collapsed",
            key="nav_radio",
        )

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Route to pages
    if page == "🏠 Home":
        from pages import home
        home.render(user)
    elif page == "🛍️ Browse":
        from pages import browse
        browse.render(user)
    elif page == "📦 Product":
        from pages import product
        product.render(user)
    elif page == "👤 Profile":
        from pages import profile
        profile.render(user)
    elif page == "📊 Analytics":
        from pages import analytics
        analytics.render(user)
    elif page == "🧪 Evaluation":
        from pages import evaluation
        evaluation.render(user)


if __name__ == "__main__":
    main()
