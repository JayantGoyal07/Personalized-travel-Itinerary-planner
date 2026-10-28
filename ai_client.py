# ============================================================
# ai_client.py  –  Unified AI provider wrapper
# Supports Google Gemini, Groq, and Demo-mode fallback
# ============================================================
from __future__ import annotations

import json
import re
import time
from typing import Any


# ── Attempt imports (optional deps) ──────────────────────────
try:
    import google.generativeai as genai  # type: ignore
    GEMINI_OK = True
except ImportError:
    GEMINI_OK = False

try:
    from groq import Groq  # type: ignore
    GROQ_OK = True
except ImportError:
    GROQ_OK = False


# ──────────────────────────────────────────────────────────────
class AIClient:
    """Single interface for Gemini / Groq / Demo-mode."""

    def __init__(self, provider: str, api_key: str | None = None):
        self.provider = provider.lower()
        self.api_key  = api_key
        self._client  = None

        if self.provider == "gemini" and api_key and GEMINI_OK:
            genai.configure(api_key=api_key)
            self._client = genai.GenerativeModel("gemini-1.5-flash")

        elif self.provider == "groq" and api_key and GROQ_OK:
            self._client = Groq(api_key=api_key)

    # ── core call ─────────────────────────────────────────────
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Return raw text from the model (or demo fallback)."""
        if self.provider == "demo" or self._client is None:
            return self._demo_response(prompt)

        try:
            if self.provider == "gemini":
                resp = self._client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=4096,
                    ),
                )
                return resp.text

            elif self.provider == "groq":
                resp = self._client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=4096,
                )
                return resp.choices[0].message.content

        except Exception as exc:
            raise RuntimeError(f"AI call failed ({self.provider}): {exc}") from exc

        return ""

    # ── JSON helper ───────────────────────────────────────────
    def generate_json(self, prompt: str, temperature: float = 0.6) -> Any:
        """Return parsed JSON dict/list or raise ValueError."""
        raw = self.generate(prompt + "\n\nRespond ONLY with valid JSON.", temperature)
        # Strip markdown fences if present
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Could not parse AI JSON response: {exc}\nRaw: {raw[:400]}") from exc

    # ── Demo / offline responses ──────────────────────────────
    @staticmethod
    def _demo_response(prompt: str) -> str:
        """Return deterministic demo data so the app is useful without keys."""
        p = prompt.lower()

        if "destination" in p and "recommend" in p:
            return json.dumps(_DEMO_DESTINATIONS)

        if "itinerary" in p or "day-by-day" in p or "day 1" in p:
            return json.dumps(_DEMO_ITINERARY)

        if "swap" in p or "replace" in p or "alternative" in p:
            return json.dumps(_DEMO_SWAP)

        return json.dumps({"message": "Demo mode active. Connect an API key for AI-powered content."})


# ══════════════════════════════════════════════════════════════
#  DEMO DATA FIXTURES
# ══════════════════════════════════════════════════════════════

_DEMO_DESTINATIONS = [
    {
        "rank": 1,
        "city": "Bali, Indonesia",
        "country": "Indonesia",
        "tagline": "Island of the Gods — temples, rice terraces & surf",
        "match_score": 97,
        "best_months": "Apr–Oct",
        "avg_daily_usd": 55,
        "avg_daily_inr": 4600,
        "tags": ["Beach", "Cultural", "Food", "Budget-Friendly"],
        "highlights": ["Ubud Monkey Forest", "Tanah Lot Temple", "Seminyak Beach", "Tegallalang Rice Terraces"],
        "weather": "Sunny & warm 28–32°C",
        "emoji": "🌴",
    },
    {
        "rank": 2,
        "city": "Kyoto, Japan",
        "country": "Japan",
        "tagline": "Ancient capital — geisha districts, bamboo & zen gardens",
        "match_score": 91,
        "best_months": "Mar–May, Sep–Nov",
        "avg_daily_usd": 120,
        "avg_daily_inr": 10000,
        "tags": ["Cultural", "History", "Food", "Scenic"],
        "highlights": ["Fushimi Inari", "Arashiyama Bamboo", "Nishiki Market", "Kinkaku-ji"],
        "weather": "Pleasant 18–25°C",
        "emoji": "⛩️",
    },
    {
        "rank": 3,
        "city": "Queenstown, New Zealand",
        "country": "New Zealand",
        "tagline": "Adventure capital of the world — fjords, skiing & bungee",
        "match_score": 84,
        "best_months": "Dec–Feb (summer)",
        "avg_daily_usd": 180,
        "avg_daily_inr": 15000,
        "tags": ["Adventure", "Mountains", "Nature", "Luxury"],
        "highlights": ["Bungee Jumping", "Milford Sound", "Remarkables Ski", "Lake Wakatipu"],
        "weather": "Cool & crisp 14–22°C",
        "emoji": "🏔️",
    },
]

_DEMO_ITINERARY = {
    "destination": "Bali, Indonesia",
    "trip_summary": "A perfectly balanced 5-day Bali adventure mixing culture, cuisine & coastal relaxation.",
    "total_estimated_usd": 285,
    "total_estimated_inr": 23940,
    "currency_note": "1 USD ≈ 84 INR | 1 USD ≈ 15,600 IDR",
    "days": [
        {
            "day": 1,
            "theme": "Arrival & Seminyak Vibes",
            "cluster_area": "South Bali — Seminyak & Kuta",
            "slots": [
                {
                    "time": "Morning",
                    "icon": "🌅",
                    "title": "Airport → Seminyak Hotel Check-in",
                    "description": "Settle in, freshen up. Grab a nasi goreng breakfast at a local warung.",
                    "cost_usd": 8,
                    "cost_inr": 672,
                    "type": "Travel",
                },
                {
                    "time": "Afternoon",
                    "icon": "🏖️",
                    "title": "Seminyak Beach & Sunset Strip",
                    "description": "Stroll the iconic beach strip, rent a sunbed, enjoy the Indian Ocean waves.",
                    "cost_usd": 12,
                    "cost_inr": 1008,
                    "type": "Leisure",
                },
                {
                    "time": "Evening",
                    "icon": "🍷",
                    "title": "Ku De Ta Sunset Cocktails & Dinner",
                    "description": "World-famous sunset view restaurant. Try the grilled barramundi.",
                    "cost_usd": 35,
                    "cost_inr": 2940,
                    "type": "Dining",
                },
            ],
            "day_total_usd": 55,
            "day_total_inr": 4620,
        },
        {
            "day": 2,
            "theme": "Temples & Rice Terraces",
            "cluster_area": "Central Bali — Ubud Corridor",
            "slots": [
                {
                    "time": "Morning",
                    "icon": "🌄",
                    "title": "Tegallalang Rice Terraces",
                    "description": "UNESCO-listed cascading rice paddies. Best light at 8–10 AM. Instagram gold.",
                    "cost_usd": 5,
                    "cost_inr": 420,
                    "type": "Sightseeing",
                },
                {
                    "time": "Lunch",
                    "icon": "🍽️",
                    "title": "Warung Babi Guling Ibu Oka",
                    "description": "Legendary suckling pig (babi guling) — Ubud's most famous local lunch spot.",
                    "cost_usd": 8,
                    "cost_inr": 672,
                    "type": "Dining",
                },
                {
                    "time": "Afternoon",
                    "icon": "🐒",
                    "title": "Ubud Monkey Forest & Palace",
                    "description": "Sacred monkey sanctuary in dense jungle. Then visit the ornate Ubud Palace.",
                    "cost_usd": 5,
                    "cost_inr": 420,
                    "type": "Sightseeing",
                },
                {
                    "time": "Evening",
                    "icon": "🎭",
                    "title": "Kecak Fire Dance Performance",
                    "description": "Traditional Balinese dance at Uluwatu Temple during sunset. Breathtaking.",
                    "cost_usd": 15,
                    "cost_inr": 1260,
                    "type": "Entertainment",
                },
            ],
            "day_total_usd": 58,
            "day_total_inr": 4872,
        },
        {
            "day": 3,
            "theme": "Adventure & Water Sports",
            "cluster_area": "East Bali — Amed & Candidasa",
            "slots": [
                {
                    "time": "Morning",
                    "icon": "🤿",
                    "title": "Snorkelling at Amed Beach",
                    "description": "Crystal-clear waters with WWII shipwreck USS Liberty. Vibrant coral reefs.",
                    "cost_usd": 20,
                    "cost_inr": 1680,
                    "type": "Adventure",
                },
                {
                    "time": "Lunch",
                    "icon": "🦞",
                    "title": "Fresh Seafood at Amed Fish Market",
                    "description": "Choose your catch, they grill it on the spot. Local Balinese sambal included.",
                    "cost_usd": 12,
                    "cost_inr": 1008,
                    "type": "Dining",
                },
                {
                    "time": "Afternoon",
                    "icon": "🌊",
                    "title": "White-Water Rafting — Ayung River",
                    "description": "Grade II–III rapids through jungle gorge. Safe for beginners. Thrilling!",
                    "cost_usd": 30,
                    "cost_inr": 2520,
                    "type": "Adventure",
                },
                {
                    "time": "Evening",
                    "icon": "💆",
                    "title": "Traditional Balinese Massage",
                    "description": "1-hour full-body massage at a reputable spa. Well-deserved after adventure day.",
                    "cost_usd": 15,
                    "cost_inr": 1260,
                    "type": "Wellness",
                },
            ],
            "day_total_usd": 77,
            "day_total_inr": 6468,
        },
        {
            "day": 4,
            "theme": "Spiritual North & Volcano Views",
            "cluster_area": "North & Central Bali — Bedugul & Kintamani",
            "slots": [
                {
                    "time": "Morning",
                    "icon": "🌋",
                    "title": "Mount Batur Sunrise Hike",
                    "description": "2-hour guided hike to active volcano summit. Watch sunrise above the clouds.",
                    "cost_usd": 35,
                    "cost_inr": 2940,
                    "type": "Adventure",
                },
                {
                    "time": "Lunch",
                    "icon": "🍳",
                    "title": "Eggs cooked in volcanic steam",
                    "description": "Unique experience — eggs & corn steamed using natural geothermal vents at the summit.",
                    "cost_usd": 5,
                    "cost_inr": 420,
                    "type": "Dining",
                },
                {
                    "time": "Afternoon",
                    "icon": "🛕",
                    "title": "Pura Ulun Danu Bratan Water Temple",
                    "description": "Iconic temple on Lake Bratan — appears to float on water. Sacred Hindu site.",
                    "cost_usd": 5,
                    "cost_inr": 420,
                    "type": "Sightseeing",
                },
                {
                    "time": "Evening",
                    "icon": "🌃",
                    "title": "Night Market at Singaraja",
                    "description": "Local night market with grilled satay, martabak, and tropical fruit juices.",
                    "cost_usd": 10,
                    "cost_inr": 840,
                    "type": "Food & Nightlife",
                },
            ],
            "day_total_usd": 55,
            "day_total_inr": 4620,
        },
        {
            "day": 5,
            "theme": "Tanah Lot & Farewell Shopping",
            "cluster_area": "West Bali — Tanah Lot & Canggu",
            "slots": [
                {
                    "time": "Morning",
                    "icon": "⛩️",
                    "title": "Tanah Lot Temple at Low Tide",
                    "description": "Most photographed temple in Bali — perched on a sea rock. Visit early to beat crowds.",
                    "cost_usd": 6,
                    "cost_inr": 504,
                    "type": "Sightseeing",
                },
                {
                    "time": "Lunch",
                    "icon": "☕",
                    "title": "Canggu Café Crawl",
                    "description": "Canggu is Bali's hipster hub. Try Revolver Espresso or Nude café for brunch.",
                    "cost_usd": 14,
                    "cost_inr": 1176,
                    "type": "Dining",
                },
                {
                    "time": "Afternoon",
                    "icon": "🛍️",
                    "title": "Souvenirs & Artisan Shopping",
                    "description": "Seminyak Square & Kuta Art Market. Batik, silver jewellery, wooden carvings.",
                    "cost_usd": 25,
                    "cost_inr": 2100,
                    "type": "Shopping",
                },
                {
                    "time": "Evening",
                    "icon": "✈️",
                    "title": "Airport Transfer & Departure",
                    "description": "Private car transfer to Ngurah Rai International Airport. Safe travels!",
                    "cost_usd": 15,
                    "cost_inr": 1260,
                    "type": "Travel",
                },
            ],
            "day_total_usd": 60,
            "day_total_inr": 5040,
        },
    ],
}

_DEMO_SWAP = {
    "original_slot": "Museum Visit",
    "new_slot": {
        "time": "Afternoon",
        "icon": "🛒",
        "title": "Badung Traditional Market",
        "description": "Vibrant 2-storey market bursting with spices, textiles, and local crafts. Bargain hard!",
        "cost_usd": 10,
        "cost_inr": 840,
        "type": "Shopping",
    },
    "swap_reason": "Replaced indoor museum with an authentic local market experience for cultural immersion.",
}

