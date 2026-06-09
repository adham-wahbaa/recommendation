# 🛒 SmartShop AI — AI-Powered Recommendation System

## Machine Learning | Recommendation Systems | Big Data | Full Stack Python

A complete full-stack AI-powered e-commerce recommendation platform that tracks real user behavior and generates personalized product recommendations — similar to Amazon, Netflix, and YouTube.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/adham-wahbaa/recommendation.git
cd recommendation
```

### 2. Create & activate virtual environment
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1       # PowerShell (Windows)
# or
.venv\Scripts\activate.bat       # CMD (Windows)
# or
source .venv/bin/activate        # macOS / Linux
```

> **Note:** If you get an execution policy error on PowerShell, run:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

**Demo Login:** username `demo` / password `demo`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Streamlit Frontend                 │
│  Home │ Browse │ Product │ Profile │ Analytics  │
├─────────────────────────────────────────────────┤
│              Authentication Layer               │
├─────────────────────────────────────────────────┤
│           Hybrid Recommendation Engine          │
│  Content-Based │ Collaborative │ Popularity     │
├─────────────────────────────────────────────────┤
│          Interaction Tracking System            │
├─────────────────────────────────────────────────┤
│              SQLite Database                    │
│  Users │ Products │ Interactions │ Reviews      │
└─────────────────────────────────────────────────┘
```

---

## 📋 Features

### Authentication
- User signup & login
- Session management
- User profiles

### Product Browsing
- Product catalog with 1,500+ products
- 8 categories, 30+ subcategories
- Search, filter, sort
- Product detail pages

### User Interaction Tracking
- 👁️ Views
- ❤️ Likes
- 📌 Wishlist
- 🛒 Purchases
- 🔍 Searches

### AI Recommendations
- 🎯 **Recommended For You** — personalized hybrid recommendations
- 🔗 **Similar Products** — content-based item similarity
- 🔥 **Trending Now** — popularity-based
- 💡 **Based on Your Interests** — category affinity
- 🕐 **Recently Viewed** — browsing history
- 🛒 **Frequently Bought Together** — collaborative patterns

### Analytics Dashboard
- Interaction type distribution (pie chart)
- Category popularity (bar chart)
- Top products by interaction volume (stacked bar)
- User activity distribution
- Price distribution by category (box plot)
- Conversion funnel visualization
- Rating distribution

### ML Evaluation
- Precision@K, Recall@K, NDCG@K metrics
- Model comparison (Content vs Collaborative vs Hybrid)
- Similarity quality assessment
- EDA with interactive Plotly charts

---

## 🧠 Recommendation Engine

### Content-Based Filtering
- TF-IDF vectorization on product features (category, tags, description, brand)
- Cosine Similarity for item-to-item matching
- User profile built from weighted interaction history

### Collaborative Filtering
- Item-item KNN on user-interaction matrix
- SVD (Truncated) for latent factor discovery
- Weighted interactions (purchase=5, like=3, wishlist=2, view=1)

### Hybrid System
- Adaptive weighting based on user history depth:
  - New users (<5 interactions): 70% popularity + 30% content
  - Medium users (5-20): 40% content + 30% collaborative + 30% popularity
  - Active users (20+): 35% content + 45% collaborative + 20% popularity

---

## 📊 Dataset

Synthetic e-commerce dataset:
- **1,500+ products** across 8 categories
- **16 users** with diverse preference profiles
- **50,000 interactions** (views, likes, purchases, wishlists)
- **5,000 reviews** with ratings and comments

---

## 📁 Project Structure

```
recommendation/
├── app.py                 ← Streamlit entry point
├── database.py            ← SQLite operations
├── generate_dataset.py    ← Dataset generator
├── requirements.txt
├── README.md
├── engine/
│   ├── content_based.py   ← TF-IDF + Cosine Similarity
│   ├── collaborative.py   ← KNN + SVD
│   └── hybrid.py          ← Weighted hybrid system
└── pages/
    ├── home.py            ← Personalized feed
    ├── browse.py          ← Product catalog
    ├── product.py         ← Product details
    ├── profile.py         ← User profile
    ├── analytics.py       ← Analytics dashboard
    └── evaluation.py      ← ML evaluation
```

---

## 🛠️ Technologies

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Database | SQLite |
| ML | Scikit-learn (TF-IDF, KNN, SVD) |
| Visualization | Plotly |
| Language | Python |

---

## 👤 Author

domix — Machine Learning, Recommendation Systems, Big Data, Full Stack Python
