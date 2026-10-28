# ============================================================
# prompts.py  –  All AI prompt templates
# ============================================================
from __future__ import annotations
from typing import Any


def destination_recommend_prompt(prefs: dict) -> str:
    return f"""
You are an expert travel consultant with 20 years of experience.
A traveller has the following preferences:
- Vibe: {prefs.get('vibe', 'Mixed')}
- Budget level: {prefs.get('budget', 'Moderate')}
- Duration: {prefs.get('duration', 7)} days
- Travel dates: {prefs.get('dates', 'Flexible')}
- Travel party: {prefs.get('party', 'Solo')}
- Interests: {', '.join(prefs.get('interests', ['Food', 'Culture']))}
- Preferred climate: {prefs.get('climate', 'Warm')}

Recommend exactly 3 destinations that best match these preferences.
Return a JSON array of 3 objects, each with these EXACT fields:
{{
  "rank": <1|2|3>,
  "city": "<City, Country>",
  "country": "<Country>",
  "tagline": "<one-sentence evocative description>",
  "match_score": <integer 60-99>,
  "best_months": "<e.g. Mar-May>",
  "avg_daily_usd": <integer>,
  "avg_daily_inr": <integer>,
  "tags": ["<tag1>", "<tag2>", ...],
  "highlights": ["<attraction1>", "<attraction2>", "<attraction3>", "<attraction4>"],
  "weather": "<description with temperature>",
  "emoji": "<single emoji>"
}}
Ensure destinations are geographically diverse. Prioritise value-for-money.
"""


def itinerary_prompt(prefs: dict) -> str:
    return f"""
You are a world-class travel itinerary architect specialising in personalised travel experiences.
Create a detailed, optimised {prefs.get('duration', 5)}-day itinerary for:

Destination: {prefs.get('destination', 'Bali, Indonesia')}
Travel party: {prefs.get('party', 'Solo')}
Budget: {prefs.get('budget', 'Moderate')} (approx USD {prefs.get('budget_daily_usd', '80-200')}/day)
Pace: {prefs.get('pace', 'Moderate')}
Interests: {', '.join(prefs.get('interests', ['Food', 'Culture']))}
Travel dates: {prefs.get('dates', 'Flexible')}

CLUSTERING RULES (critical):
- Group attractions in the same geographic zone per day to minimise transit time.
- Never schedule attractions at opposite ends of the city on the same day.
- Label each day's "cluster_area" (e.g. "South Bali — Seminyak & Kuta").

Return a JSON object with EXACTLY this structure:
{{
  "destination": "<destination>",
  "trip_summary": "<2-sentence overview>",
  "total_estimated_usd": <number>,
  "total_estimated_inr": <number>,
  "currency_note": "<exchange rate note>",
  "days": [
    {{
      "day": <1..N>,
      "theme": "<catchy day theme>",
      "cluster_area": "<geographic zone>",
      "slots": [
        {{
          "time": "<Morning|Lunch|Afternoon|Evening|Night>",
          "icon": "<relevant emoji>",
          "title": "<activity name>",
          "description": "<2-sentence vivid description>",
          "cost_usd": <number>,
          "cost_inr": <number>,
          "type": "<Sightseeing|Dining|Leisure|Adventure|Entertainment|Travel|Shopping|Wellness>"
        }}
      ],
      "day_total_usd": <number>,
      "day_total_inr": <number>
    }}
  ]
}}
Include 3-5 slots per day. Costs must be realistic. Do NOT use markdown, return pure JSON only.
"""


def swap_activity_prompt(
    destination: str,
    day_num: int,
    day_theme: str,
    original_slot: dict,
    swap_request: str,
    budget: str,
    interests: list[str],
) -> str:
    return f"""
You are a travel concierge. A traveller wants to swap one activity in their itinerary.

Destination: {destination}
Day {day_num} theme: {day_theme}
Current slot: {original_slot.get('title')} at {original_slot.get('time')} ({original_slot.get('type')})
Current cost: USD {original_slot.get('cost_usd', 0)}
Traveller's swap request: "{swap_request}"
Budget level: {budget}
Interests: {', '.join(interests)}

Find the best alternative that:
1. Fits the same time slot ({original_slot.get('time')})
2. Is in the same geographic area
3. Matches the swap request
4. Stays within a similar budget

Return JSON with EXACTLY this structure:
{{
  "original_slot": "{original_slot.get('title')}",
  "new_slot": {{
    "time": "{original_slot.get('time')}",
    "icon": "<emoji>",
    "title": "<activity name>",
    "description": "<2-sentence description>",
    "cost_usd": <number>,
    "cost_inr": <number>,
    "type": "<type>"
  }},
  "swap_reason": "<1-sentence explanation of why this is a great swap>"
}}
"""

