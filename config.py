# ============================================================
# config.py  –  App-wide constants & styling
# Personalized Travel Itinerary Planner  |  Capstone Project 4
# ============================================================

APP_TITLE = "✈️ Personalized Travel Itinerary Planner"
APP_SUBTITLE = "Skill Wallet Capstone Project 4"
APP_VERSION = "1.0.0"

# ── Budget tiers ──────────────────────────────────────────────
BUDGET_TIERS = {
    "Budget":   {"daily_usd": (30, 80),   "daily_inr": (2500, 6500),   "emoji": "💰"},
    "Moderate": {"daily_usd": (80, 200),  "daily_inr": (6500, 16000),  "emoji": "💳"},
    "Luxury":   {"daily_usd": (200, 600), "daily_inr": (16000, 50000), "emoji": "💎"},
}

# ── Interest tags ─────────────────────────────────────────────
INTEREST_OPTIONS = [
    "🍜 Food & Cuisine",
    "🧗 Adventure & Sports",
    "🏛️ History & Culture",
    "🌙 Nightlife & Entertainment",
    "🛍️ Shopping",
    "🌿 Nature & Wildlife",
    "🎨 Art & Museums",
    "🧘 Wellness & Spa",
]

# ── Vibe presets ──────────────────────────────────────────────
VIBE_OPTIONS = ["🏖️ Beach", "⛰️ Mountains", "🏙️ Urban", "🎭 Cultural", "🌿 Nature", "🎲 Mixed"]

TRAVEL_PARTY_OPTIONS = ["🧍 Solo", "💑 Couple", "👨‍👩‍👧‍👦 Family", "👫 Friends Group"]

PACE_OPTIONS = {
    "Relaxed":     "2-3 activities/day, long breaks",
    "Moderate":    "4-5 activities/day, balanced",
    "Fast-Paced":  "6+ activities/day, maximise sights",
}

# ── Demo destination seeds (used in demo mode) ───────────────
DEMO_DESTINATIONS = {
    "Beach":    ["Bali, Indonesia", "Phuket, Thailand", "Santorini, Greece"],
    "Mountains":["Manali, India", "Zermatt, Switzerland", "Queenstown, New Zealand"],
    "Urban":    ["Tokyo, Japan", "New York, USA", "Dubai, UAE"],
    "Cultural": ["Kyoto, Japan", "Rome, Italy", "Varanasi, India"],
    "Nature":   ["Costa Rica", "Patagonia, Argentina", "Kerala, India"],
    "Mixed":    ["Singapore", "Cape Town, South Africa", "Barcelona, Spain"],
}

# ── CSS colour palette ────────────────────────────────────────
PRIMARY   = "#FF6B35"
SECONDARY = "#004E89"
ACCENT    = "#1A936F"
WARN      = "#F4A261"
BG_DARK   = "#0D1B2A"
BG_CARD   = "#1B2A3B"
TEXT_LIGHT = "#E8F4F8"

