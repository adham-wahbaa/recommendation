"""
Synthetic E-Commerce Dataset Generator
========================================
Generates realistic products, users, and interactions for the recommendation system.
"""

import random
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import init_db, get_db, hash_password

# ─── Product Catalog Definition ──────────────────────────────────

CATALOG = {
    "Gaming": {
        "emoji": "🎮",
        "subcategories": {
            "Keyboards": {
                "brands": ["Razer", "Corsair", "Logitech", "SteelSeries", "HyperX"],
                "items": ["Mechanical Gaming Keyboard", "RGB Keyboard", "Wireless Gaming Keyboard",
                          "60% Compact Keyboard", "Full-Size Gaming Keyboard", "TKL Keyboard"],
                "tags": "gaming,keyboard,rgb,mechanical,esports",
                "price_range": (49, 199),
            },
            "Mice": {
                "brands": ["Razer", "Logitech", "Corsair", "Glorious", "Zowie"],
                "items": ["Gaming Mouse", "Wireless Gaming Mouse", "Ultralight Mouse",
                          "MMO Mouse", "FPS Gaming Mouse", "Ergonomic Gaming Mouse"],
                "tags": "gaming,mouse,rgb,wireless,sensor",
                "price_range": (29, 149),
            },
            "Headsets": {
                "brands": ["SteelSeries", "HyperX", "Razer", "Corsair", "Astro"],
                "items": ["Gaming Headset", "Wireless Gaming Headset", "7.1 Surround Headset",
                          "RGB Headset", "Noise-Canceling Gaming Headset"],
                "tags": "gaming,headset,audio,surround,microphone",
                "price_range": (39, 299),
            },
            "Controllers": {
                "brands": ["Xbox", "PlayStation", "Scuf", "8BitDo", "Razer"],
                "items": ["Wireless Controller", "Pro Controller", "Custom Controller",
                          "Retro Controller", "Racing Wheel"],
                "tags": "gaming,controller,wireless,console",
                "price_range": (29, 199),
            },
            "Monitors": {
                "brands": ["ASUS", "BenQ", "Samsung", "LG", "Alienware"],
                "items": ["144Hz Gaming Monitor", "4K Gaming Monitor", "Curved Gaming Monitor",
                          "Ultrawide Monitor", "240Hz Esports Monitor", "27-inch Gaming Monitor"],
                "tags": "gaming,monitor,display,144hz,4k,curved",
                "price_range": (199, 899),
            },
            "Chairs": {
                "brands": ["Secretlab", "DXRacer", "Herman Miller", "Corsair", "Razer"],
                "items": ["Gaming Chair", "Ergonomic Gaming Chair", "Racing Style Chair",
                          "Premium Gaming Chair"],
                "tags": "gaming,chair,ergonomic,comfort",
                "price_range": (199, 599),
            },
        },
    },
    "Electronics": {
        "emoji": "🖥️",
        "subcategories": {
            "Laptops": {
                "brands": ["Apple", "Dell", "HP", "Lenovo", "ASUS"],
                "items": ["Ultrabook Laptop", "Business Laptop", "Chromebook",
                          "2-in-1 Laptop", "Budget Laptop", "Student Laptop"],
                "tags": "laptop,computer,portable,productivity",
                "price_range": (399, 1999),
            },
            "Tablets": {
                "brands": ["Apple", "Samsung", "Microsoft", "Lenovo", "Amazon"],
                "items": ["Pro Tablet", "Budget Tablet", "Drawing Tablet",
                          "E-Reader Tablet", "Kids Tablet"],
                "tags": "tablet,portable,touchscreen,digital",
                "price_range": (99, 1299),
            },
            "Smartphones": {
                "brands": ["Apple", "Samsung", "Google", "OnePlus", "Xiaomi"],
                "items": ["Flagship Phone", "Budget Smartphone", "Camera Phone",
                          "5G Smartphone", "Foldable Phone"],
                "tags": "phone,smartphone,mobile,5g,camera",
                "price_range": (199, 1499),
            },
            "Cameras": {
                "brands": ["Canon", "Sony", "Nikon", "Fujifilm", "GoPro"],
                "items": ["Mirrorless Camera", "DSLR Camera", "Action Camera",
                          "Compact Camera", "Vlog Camera"],
                "tags": "camera,photography,video,lens,4k",
                "price_range": (299, 2499),
            },
            "Audio": {
                "brands": ["Sony", "Bose", "Sennheiser", "Apple", "JBL"],
                "items": ["Wireless Earbuds", "Over-Ear Headphones", "Bluetooth Speaker",
                          "Soundbar", "Portable Speaker", "Studio Headphones"],
                "tags": "audio,headphones,speaker,bluetooth,wireless",
                "price_range": (29, 399),
            },
        },
    },
    "Fashion": {
        "emoji": "👕",
        "subcategories": {
            "Men's Clothing": {
                "brands": ["Nike", "Adidas", "Uniqlo", "Zara", "H&M"],
                "items": ["T-Shirt", "Hoodie", "Jacket", "Jeans", "Polo Shirt", "Shorts"],
                "tags": "men,clothing,casual,fashion,style",
                "price_range": (19, 149),
            },
            "Women's Clothing": {
                "brands": ["Zara", "H&M", "Nike", "Lululemon", "Mango"],
                "items": ["Dress", "Blouse", "Leggings", "Cardigan", "Skirt", "Crop Top"],
                "tags": "women,clothing,fashion,style,casual",
                "price_range": (19, 199),
            },
            "Shoes": {
                "brands": ["Nike", "Adidas", "New Balance", "Converse", "Vans"],
                "items": ["Running Shoes", "Sneakers", "Casual Shoes", "Boots", "Sandals"],
                "tags": "shoes,footwear,sneakers,running,casual",
                "price_range": (39, 249),
            },
            "Accessories": {
                "brands": ["Ray-Ban", "Fossil", "Coach", "Michael Kors", "Casio"],
                "items": ["Sunglasses", "Watch", "Belt", "Wallet", "Backpack", "Hat"],
                "tags": "accessories,fashion,style,everyday",
                "price_range": (15, 299),
            },
        },
    },
    "Home & Kitchen": {
        "emoji": "🏠",
        "subcategories": {
            "Kitchen Appliances": {
                "brands": ["KitchenAid", "Ninja", "Cuisinart", "Instant Pot", "Breville"],
                "items": ["Blender", "Air Fryer", "Coffee Maker", "Toaster", "Stand Mixer",
                          "Electric Kettle"],
                "tags": "kitchen,appliance,cooking,home",
                "price_range": (29, 399),
            },
            "Furniture": {
                "brands": ["IKEA", "Wayfair", "West Elm", "CB2", "Article"],
                "items": ["Desk", "Bookshelf", "Office Chair", "Standing Desk",
                          "TV Stand", "Side Table"],
                "tags": "furniture,home,office,desk,decor",
                "price_range": (79, 599),
            },
            "Smart Home": {
                "brands": ["Amazon", "Google", "Ring", "Philips", "TP-Link"],
                "items": ["Smart Speaker", "Smart Light Bulb", "Smart Plug", "Security Camera",
                          "Smart Thermostat", "Smart Display"],
                "tags": "smart,home,iot,automation,alexa,google",
                "price_range": (19, 299),
            },
        },
    },
    "Sports & Fitness": {
        "emoji": "⚽",
        "subcategories": {
            "Fitness Equipment": {
                "brands": ["Bowflex", "NordicTrack", "Peloton", "Rogue", "TRX"],
                "items": ["Dumbbells", "Yoga Mat", "Resistance Bands", "Exercise Bike",
                          "Pull-Up Bar", "Kettlebell", "Foam Roller"],
                "tags": "fitness,gym,workout,exercise,training",
                "price_range": (15, 499),
            },
            "Sportswear": {
                "brands": ["Nike", "Under Armour", "Adidas", "Lululemon", "Puma"],
                "items": ["Athletic Shorts", "Sport Leggings", "Running Jacket",
                          "Compression Shirt", "Sports Bra", "Training Shoes"],
                "tags": "sportswear,athletic,running,training,gym",
                "price_range": (25, 149),
            },
            "Outdoor Gear": {
                "brands": ["The North Face", "Patagonia", "Columbia", "REI", "Osprey"],
                "items": ["Hiking Backpack", "Camping Tent", "Sleeping Bag",
                          "Trekking Poles", "Water Bottle", "Flashlight"],
                "tags": "outdoor,hiking,camping,adventure,nature",
                "price_range": (19, 399),
            },
        },
    },
    "Books & Education": {
        "emoji": "📚",
        "subcategories": {
            "Programming": {
                "brands": ["O'Reilly", "Manning", "Packt", "Addison-Wesley", "No Starch"],
                "items": ["Python Programming Book", "Machine Learning Guide", "Web Dev Handbook",
                          "Data Science Textbook", "AI Fundamentals", "Algorithms Book"],
                "tags": "book,programming,coding,tech,education",
                "price_range": (19, 69),
            },
            "Business": {
                "brands": ["HBR", "Penguin", "Portfolio", "Crown", "Random House"],
                "items": ["Leadership Book", "Marketing Guide", "Startup Handbook",
                          "Finance Textbook", "Management Book"],
                "tags": "book,business,leadership,finance,management",
                "price_range": (12, 45),
            },
            "Online Courses": {
                "brands": ["Udemy", "Coursera", "edX", "Skillshare", "LinkedIn Learning"],
                "items": ["Python Course", "Data Science Bootcamp", "Web Development Course",
                          "ML & AI Masterclass", "Cloud Computing Course"],
                "tags": "course,online,learning,education,certificate",
                "price_range": (9, 199),
            },
        },
    },
    "Beauty & Health": {
        "emoji": "💄",
        "subcategories": {
            "Skincare": {
                "brands": ["CeraVe", "The Ordinary", "Neutrogena", "La Roche-Posay", "Olay"],
                "items": ["Moisturizer", "Sunscreen", "Face Wash", "Serum", "Toner", "Eye Cream"],
                "tags": "skincare,beauty,face,moisturizer,spf",
                "price_range": (8, 65),
            },
            "Hair Care": {
                "brands": ["Olaplex", "Moroccanoil", "Dyson", "CHI", "Redken"],
                "items": ["Shampoo", "Conditioner", "Hair Dryer", "Styling Cream",
                          "Hair Serum", "Curling Iron"],
                "tags": "hair,beauty,styling,shampoo,care",
                "price_range": (10, 399),
            },
            "Supplements": {
                "brands": ["Nature Made", "Optimum Nutrition", "Garden of Life", "NOW", "Vital"],
                "items": ["Multivitamin", "Protein Powder", "Omega-3", "Pre-Workout",
                          "Creatine", "BCAA"],
                "tags": "supplements,health,vitamins,protein,nutrition",
                "price_range": (12, 59),
            },
        },
    },
    "Toys & Hobbies": {
        "emoji": "🧸",
        "subcategories": {
            "Board Games": {
                "brands": ["Hasbro", "Ravensburger", "Fantasy Flight", "Asmodee", "Mattel"],
                "items": ["Strategy Board Game", "Family Board Game", "Card Game",
                          "Party Game", "Puzzle 1000pc", "Cooperative Game"],
                "tags": "boardgame,family,game,puzzle,fun",
                "price_range": (15, 79),
            },
            "Collectibles": {
                "brands": ["LEGO", "Funko", "Bandai", "Hot Toys", "McFarlane"],
                "items": ["LEGO Set", "Action Figure", "Funko Pop", "Model Kit",
                          "Trading Cards Pack"],
                "tags": "collectible,figure,lego,funko,hobby",
                "price_range": (10, 299),
            },
            "RC & Drones": {
                "brands": ["DJI", "Holy Stone", "Traxxas", "Hubsan", "Potensic"],
                "items": ["Camera Drone", "Mini Drone", "RC Car", "FPV Drone",
                          "Racing Drone"],
                "tags": "drone,rc,flying,camera,remote",
                "price_range": (29, 999),
            },
        },
    },
}

# ─── User Persona Templates ──────────────────────────────────────

USER_PERSONAS = [
    {"name": "gamer_alex",    "display": "Alex",    "bias": ["Gaming", "Electronics"]},
    {"name": "techie_sam",    "display": "Sam",     "bias": ["Electronics", "Gaming"]},
    {"name": "fashionista_mia","display": "Mia",    "bias": ["Fashion", "Beauty & Health"]},
    {"name": "fitness_jake",  "display": "Jake",    "bias": ["Sports & Fitness", "Beauty & Health"]},
    {"name": "homechef_emma", "display": "Emma",    "bias": ["Home & Kitchen", "Books & Education"]},
    {"name": "bookworm_liam", "display": "Liam",    "bias": ["Books & Education", "Electronics"]},
    {"name": "outdoor_noah",  "display": "Noah",    "bias": ["Sports & Fitness", "Toys & Hobbies"]},
    {"name": "creative_sophia","display":"Sophia",   "bias": ["Toys & Hobbies", "Fashion"]},
    {"name": "parent_olivia", "display": "Olivia",  "bias": ["Toys & Hobbies", "Home & Kitchen"]},
    {"name": "student_ethan", "display": "Ethan",   "bias": ["Books & Education", "Electronics"]},
    {"name": "minimalist_ava","display": "Ava",     "bias": ["Home & Kitchen", "Beauty & Health"]},
    {"name": "gadget_ryan",   "display": "Ryan",    "bias": ["Electronics", "Gaming"]},
    {"name": "wellness_zoe",  "display": "Zoe",     "bias": ["Beauty & Health", "Sports & Fitness"]},
    {"name": "explorer_mason","display": "Mason",   "bias": ["Sports & Fitness", "Electronics"]},
    {"name": "hobbyist_lily", "display": "Lily",    "bias": ["Toys & Hobbies", "Books & Education"]},
]


def generate_products():
    """Generate all products from the catalog."""
    products = []
    pid = 0
    for category, cat_data in CATALOG.items():
        emoji = cat_data["emoji"]
        for subcat, sub_data in cat_data["subcategories"].items():
            for item_name in sub_data["items"]:
                for brand in sub_data["brands"]:
                    pid += 1
                    price = round(random.uniform(*sub_data["price_range"]), 2)
                    name = f"{brand} {item_name}"
                    desc = (f"Premium {item_name.lower()} by {brand}. "
                            f"Perfect for {category.lower()} enthusiasts. "
                            f"Features top-quality materials and modern design. "
                            f"Category: {subcat}.")
                    rating = round(random.uniform(3.0, 5.0), 1)
                    review_count = random.randint(5, 500)
                    tags = f"{sub_data['tags']},{brand.lower()},{subcat.lower()}"
                    products.append((
                        name, category, subcat, desc, price, brand,
                        rating, review_count, tags, emoji, rating * review_count / 100
                    ))
    return products


def generate_interactions(user_ids, product_map, num_interactions=50000):
    """Generate realistic user interactions based on persona biases."""
    interactions = []
    types_weights = {
        "view": 50,
        "like": 20,
        "wishlist": 10,
        "purchase": 8,
        "search": 12,
    }
    types = list(types_weights.keys())
    weights = list(types_weights.values())

    # Group products by category
    cat_products = {}
    for pid, cat in product_map.items():
        cat_products.setdefault(cat, []).append(pid)

    all_categories = list(cat_products.keys())
    now = time.time()

    for _ in range(num_interactions):
        # Pick a user
        user_idx = random.randint(0, len(user_ids) - 1)
        user_id = user_ids[user_idx]
        persona = USER_PERSONAS[user_idx % len(USER_PERSONAS)]
        biased_cats = persona["bias"]

        # 70% chance to interact with preferred categories
        if random.random() < 0.7 and biased_cats:
            cat = random.choice(biased_cats)
        else:
            cat = random.choice(all_categories)

        if cat not in cat_products or not cat_products[cat]:
            cat = random.choice(all_categories)

        product_id = random.choice(cat_products[cat])
        itype = random.choices(types, weights=weights, k=1)[0]
        ts = now - random.uniform(0, 90 * 86400)  # Last 90 days
        duration = random.uniform(5, 300) if itype == "view" else 0

        interactions.append((user_id, product_id, itype, ts, duration))

    return interactions


def generate_reviews(user_ids, product_map, num_reviews=5000):
    """Generate product reviews."""
    reviews = []
    pids = list(product_map.keys())
    comments = [
        "Great product, highly recommend!",
        "Good quality for the price.",
        "Exactly what I was looking for.",
        "Works perfectly, fast shipping.",
        "Decent product, nothing special.",
        "Amazing quality, exceeded expectations!",
        "Not bad, but could be better.",
        "Excellent value for money.",
        "Very happy with this purchase!",
        "Solid build quality.",
        "Perfect gift idea!",
        "Would buy again.",
        "Pretty good overall.",
        "Love it! Five stars!",
        "Meets expectations.",
    ]
    seen = set()
    for _ in range(num_reviews):
        uid = random.choice(user_ids)
        pid = random.choice(pids)
        key = (uid, pid)
        if key in seen:
            continue
        seen.add(key)
        rating = round(random.uniform(2.5, 5.0), 1)
        comment = random.choice(comments)
        ts = time.time() - random.uniform(0, 180 * 86400)
        reviews.append((uid, pid, rating, comment, ts))
    return reviews


def populate_database():
    """Generate and insert all data into the database."""
    print("=" * 60)
    print("  GENERATING E-COMMERCE DATASET")
    print("=" * 60)

    init_db()

    with get_db() as conn:
        # Check if already populated
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count > 0:
            print(f"  Database already populated ({count} products). Skipping.")
            return

        # 1. Generate Products
        print("\n  [1/4] Generating products...")
        products = generate_products()
        conn.executemany(
            """INSERT INTO products (name, category, subcategory, description, price,
               brand, rating, review_count, tags, image_emoji, popularity_score)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            products
        )
        print(f"    -> {len(products)} products created")

        # 2. Create Users
        print("  [2/4] Creating users...")
        user_ids = []
        for persona in USER_PERSONAS:
            pw = hash_password("password123")
            cur = conn.execute(
                "INSERT INTO users (username, email, password_hash, display_name) VALUES (?, ?, ?, ?)",
                (persona["name"], f"{persona['name']}@demo.com", pw, persona["display"])
            )
            user_ids.append(cur.lastrowid)
        # Add a demo user
        pw = hash_password("demo")
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash, display_name) VALUES (?, ?, ?, ?)",
            ("demo", "demo@demo.com", pw, "Demo User")
        )
        user_ids.append(cur.lastrowid)
        print(f"    -> {len(user_ids)} users created")

        # Build product map
        rows = conn.execute("SELECT id, category FROM products").fetchall()
        product_map = {r["id"]: r["category"] for r in rows}

        # 3. Generate Interactions
        print("  [3/4] Generating interactions...")
        interactions = generate_interactions(user_ids, product_map, 50000)
        conn.executemany(
            "INSERT INTO interactions (user_id, product_id, interaction_type, timestamp, duration) VALUES (?, ?, ?, ?, ?)",
            interactions
        )
        print(f"    -> {len(interactions)} interactions created")

        # 4. Generate Reviews
        print("  [4/4] Generating reviews...")
        reviews = generate_reviews(user_ids, product_map, 5000)
        conn.executemany(
            "INSERT INTO reviews (user_id, product_id, rating, comment, timestamp) VALUES (?, ?, ?, ?, ?)",
            reviews
        )
        print(f"    -> {len(reviews)} reviews created")

    print("\n  Database populated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    populate_database()
