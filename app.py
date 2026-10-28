# ============================================================
# app.py  –  Main Streamlit entry point
# Personalized Travel Itinerary Planner | Capstone Project 4
# ============================================================
from __future__ import annotations

import copy
import traceback
from datetime import date, timedelta

import streamlit as st

# ── Local modules ─────────────────────────────────────────────
from config import (
    APP_SUBTITLE, APP_TITLE, BUDGET_TIERS, DEMO_DESTINATIONS,
    INTEREST_OPTIONS, PACE_OPTIONS, TRAVEL_PARTY_OPTIONS, VIBE_OPTIONS,
)
from styles import GLOBAL_CSS
from ai_client import AIClient
from prompts import (
    destination_recommend_prompt,
    itinerary_prompt,
    swap_activity_prompt,
)
from trip_store import delete_trip, export_trips_json, list_trips, load_trip, save_trip

# ── PDF export (optional – graceful fallback) ─────────────────
try:
    from pdf_export import generate_pdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Travel Itinerary Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SESSION STATE INITIALISATION
# ══════════════════════════════════════════════════════════════
def _init_state() -> None:
    defaults = {
        "ai_client":       None,
        "provider":        "demo",
        "api_key":         "",
        "preferences":     {},
        "destinations":    [],
        "itinerary":       {},
        "active_trip_id":  None,
        "swap_results":    {},   # {(day_idx, slot_idx): new_slot}
        "gen_status":      "",
        "dest_status":     "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()


# ══════════════════════════════════════════════════════════════
#  SIDEBAR – CONFIG & PREFERENCES
# ══════════════════════════════════════════════════════════════
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            "<div style='text-align:center;padding:1rem 0 .5rem;'>"
            "<span style='font-size:2.8rem;'>✈️</span>"
            f"<p style='color:#FF6B35;font-weight:700;font-size:1.1rem;margin:.3rem 0 0;'>{APP_TITLE}</p>"
            f"<p style='color:#8FA3B1;font-size:.75rem;margin:0;'>{APP_SUBTITLE}</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.divider()

        # ── API Configuration ─────────────────────────────────
        st.markdown("### 🔑 API Configuration")
        provider = st.selectbox(
            "AI Provider",
            ["Demo Mode (No Key)", "Google Gemini", "Groq"],
            help="Demo mode uses rich offline data. Connect an API key for AI-powered planning.",
        )

        api_key = ""
        if provider != "Demo Mode (No Key)":
            api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="Paste your key here…",
                help="Your key is never stored beyond this session.",
            )

        if st.button("🔌 Connect", use_container_width=True):
            _connect_ai(provider, api_key)

        # Status indicator
        status_color = "#1A936F" if st.session_state.ai_client is not None or st.session_state.provider == "demo" else "#FF6B35"
        status_text  = "✅ Connected" if st.session_state.ai_client is not None or st.session_state.provider == "demo" else "⚠️ Not connected"
        st.markdown(
            f"<div style='color:{status_color};font-size:.85rem;margin:.3rem 0;'>{status_text}  "
            f"<span style='color:#8FA3B1'>({st.session_state.provider.title()})</span></div>",
            unsafe_allow_html=True,
        )
        st.divider()

        # ── Trip Preferences Form ─────────────────────────────
        st.markdown("### 🗺️ Trip Preferences")
        with st.form("prefs_form"):
            destination = st.text_input(
                "📍 Destination (optional)",
                placeholder="e.g. Tokyo, Bali, Paris  — or leave blank for AI picks",
            )
            vibe = st.selectbox("🌈 Travel Vibe", VIBE_OPTIONS)
            duration = st.slider("📅 Trip Duration (days)", 2, 21, 5)

            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("🗓️ Start Date", value=date.today() + timedelta(days=30))
            with col2:
                end_date = st.date_input("🗓️ End Date", value=date.today() + timedelta(days=30 + duration))

            budget = st.select_slider(
                "💰 Budget Level",
                options=["Budget", "Moderate", "Luxury"],
                value="Moderate",
            )
            party = st.selectbox("👥 Travel Party", TRAVEL_PARTY_OPTIONS)
            pace  = st.selectbox("⚡ Pace", list(PACE_OPTIONS.keys()))
            interests = st.multiselect(
                "🎯 Interests",
                INTEREST_OPTIONS,
                default=INTEREST_OPTIONS[:2],
                max_selections=5,
            )
            climate = st.select_slider(
                "🌡️ Preferred Climate",
                options=["Cool", "Mild", "Warm", "Hot & Humid", "Any"],
                value="Warm",
            )

            submitted = st.form_submit_button("💾 Save Preferences", use_container_width=True)

        if submitted:
            _save_preferences(
                destination, vibe, duration, start_date, end_date,
                budget, party, pace, interests, climate,
            )
            st.success("✅ Preferences saved!")

        # Quick-read preference summary
        prefs = st.session_state.preferences
        if prefs:
            st.markdown("**Current preferences:**")
            dest_label = prefs.get("destination") or f"{prefs.get('vibe')} vibe"
            st.caption(
                f"📍 {dest_label}  |  📅 {prefs.get('duration')}d  |  "
                f"💰 {prefs.get('budget')}  |  👥 {prefs.get('party')}"
            )


# ──────────────────────────────────────────────────────────────
def _connect_ai(provider_label: str, api_key: str) -> None:
    prov_map = {
        "Demo Mode (No Key)": "demo",
        "Google Gemini":       "gemini",
        "Groq":                "groq",
    }
    prov = prov_map.get(provider_label, "demo")
    try:
        client = AIClient(provider=prov, api_key=api_key or None)
        st.session_state.ai_client = client
        st.session_state.provider  = prov
        st.success(f"Connected to {provider_label}!")
    except Exception as exc:
        st.error(f"Connection failed: {exc}")


def _save_preferences(
    destination, vibe, duration, start_date, end_date,
    budget, party, pace, interests, climate,
) -> None:
    budget_info = BUDGET_TIERS[budget]
    lo, hi = budget_info["daily_usd"]
    st.session_state.preferences = {
        "destination":      destination.strip() if destination else "",
        "vibe":             vibe.split()[1] if " " in vibe else vibe,   # strip emoji
        "duration":         duration,
        "dates":            f"{start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')}",
        "start_date":       str(start_date),
        "budget":           budget,
        "budget_daily_usd": f"{lo}-{hi}",
        "party":            party.split()[-1] if " " in party else party,
        "pace":             pace,
        "interests":        [i.split(" ", 1)[1] if " " in i else i for i in interests],
        "climate":          climate,
    }


# ══════════════════════════════════════════════════════════════
#  TAB 1 – SMART DESTINATION RECOMMENDER
# ══════════════════════════════════════════════════════════════
def render_tab_destinations() -> None:
    st.markdown('<p class="section-header">🌍 Smart Destination Recommender</p>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-banner">✨ No destination in mind? Let AI suggest your perfect match based on '
        'your vibe, budget, season & interests.</div>',
        unsafe_allow_html=True,
    )

    prefs = st.session_state.preferences
    if not prefs:
        st.warning("⚠️ Please fill in your **Trip Preferences** in the sidebar first.")
        return

    col_btn, col_status = st.columns([1, 3])
    with col_btn:
        gen_dest = st.button("🔍 Find My Destinations", use_container_width=True)

    if gen_dest:
        with st.spinner("🌐 Scouting the globe for you…"):
            try:
                client = _get_client()
                prompt = destination_recommend_prompt(prefs)
                data   = client.generate_json(prompt)
                if isinstance(data, list):
                    st.session_state.destinations = data
                else:
                    st.error("Unexpected AI response format.")
            except Exception as exc:
                st.error(f"Error: {exc}")
                st.session_state.destinations = []

    dests = st.session_state.destinations
    if not dests:
        # Show placeholder cards
        st.markdown('<div class="info-banner">👆 Click above to discover AI-recommended destinations.</div>', unsafe_allow_html=True)
        return

    st.markdown(f"### Top {len(dests)} Destinations for You")
    for d in dests:
        _render_destination_card(d)

    # Option to lock a destination and proceed
    st.divider()
    city_options = [d["city"] for d in dests]
    chosen = st.selectbox("📌 Select a destination to use for your itinerary:", city_options)
    if st.button("✅ Lock This Destination & Go to Itinerary"):
        st.session_state.preferences["destination"] = chosen
        st.success(f"✅ Locked: **{chosen}**  — head to the Itinerary tab!")


def _render_destination_card(d: dict) -> None:
    rank     = d.get("rank", "")
    city     = d.get("city", "")
    emoji    = d.get("emoji", "🌍")
    tagline  = d.get("tagline", "")
    score    = d.get("match_score", 0)
    months   = d.get("best_months", "")
    weather  = d.get("weather", "")
    usd      = d.get("avg_daily_usd", 0)
    inr      = d.get("avg_daily_inr", 0)
    tags     = d.get("tags", [])
    hl       = d.get("highlights", [])

    tags_html = " ".join(f'<span class="tag-pill">{t}</span>' for t in tags)
    hl_html   = " ".join(f'<span class="tag-pill tag-green">📍 {h}</span>' for h in hl)
    bar_w     = min(score, 100)
    score_color = "#1A936F" if score >= 90 else "#F4A261" if score >= 75 else "#FF6B35"

    st.markdown(
        f"""
        <div class="dest-card">
          <div class="dest-rank">#{rank}</div>
          <div class="dest-name">{emoji} {city}</div>
          <div class="dest-tagline">{tagline}</div>
          <div style="margin:.5rem 0;">{tags_html}</div>
          <div style="display:flex;gap:2rem;font-size:.85rem;color:#8FA3B1;margin:.5rem 0;">
            <span>📅 Best: <b style="color:#E8F4F8;">{months}</b></span>
            <span>🌡️ <b style="color:#E8F4F8;">{weather}</b></span>
            <span>💵 <b style="color:#1A936F;">~USD {usd}/day</b> &nbsp;/&nbsp; <b style="color:#1A936F;">₹{inr:,}/day</b></span>
          </div>
          <div style="display:flex;align-items:center;gap:.8rem;margin:.4rem 0;">
            <span style="font-size:.8rem;color:#8FA3B1;">Match</span>
            <div class="budget-bar-container" style="flex:1">
              <div class="budget-bar-fill" style="width:{bar_w}%;"></div>
            </div>
            <span style="font-size:.85rem;font-weight:700;color:{score_color};">{score}%</span>
          </div>
          <div style="margin-top:.6rem;">{hl_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════
#  TAB 2 – ITINERARY GENERATOR
# ══════════════════════════════════════════════════════════════
def render_tab_itinerary() -> None:
    st.markdown('<p class="section-header">🗓️ Day-by-Day Optimised Itinerary</p>', unsafe_allow_html=True)

    prefs = st.session_state.preferences
    if not prefs:
        st.warning("⚠️ Please fill in your **Trip Preferences** in the sidebar first.")
        return

    if not prefs.get("destination"):
        st.info("💡 No destination set — visit the **Destination Recommender** tab first, or type one in the sidebar.")

    # ── Generate button row ───────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        gen_btn = st.button("🚀 Generate Itinerary", use_container_width=True)
    with col2:
        dest_display = prefs.get("destination") or f"Best for {prefs.get('vibe', 'your vibe')}"
        st.markdown(
            f"<div style='padding:.5rem;background:rgba(255,107,53,.1);border-radius:8px;"
            f"font-size:.85rem;color:#E8F4F8;'>📍 <b>{dest_display}</b>  ·  "
            f"📅 {prefs.get('duration', '?')} days  ·  💰 {prefs.get('budget','')}</div>",
            unsafe_allow_html=True,
        )

    if gen_btn:
        _generate_itinerary(prefs)

    itin = st.session_state.itinerary
    if not itin:
        st.markdown(
            '<div class="info-banner">👆 Click "Generate Itinerary" to build your personalised trip plan.</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Budget overview metrics ───────────────────────────────
    total_usd = itin.get("total_estimated_usd", 0)
    total_inr = itin.get("total_estimated_inr", 0)
    duration  = prefs.get("duration", 1)
    daily_avg_usd = round(total_usd / max(duration, 1), 1)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💵 Total (USD)", f"${total_usd:,}")
    m2.metric("₹ Total (INR)", f"₹{total_inr:,}")
    m3.metric("📊 Avg/Day (USD)", f"${daily_avg_usd}")
    m4.metric("📅 Days Planned", str(len(itin.get("days", []))))

    # Currency note
    currency_note = itin.get("currency_note", "")
    if currency_note:
        st.caption(f"💱 {currency_note}")

    # Trip summary
    if itin.get("trip_summary"):
        st.markdown(
            f'<div class="success-banner">🗺️ {itin["trip_summary"]}</div>',
            unsafe_allow_html=True,
        )

    # ── Running budget tracker ────────────────────────────────
    st.markdown("#### 💰 Running Budget Tracker")
    days_data = itin.get("days", [])
    running = 0
    cols = st.columns(len(days_data)) if days_data else []
    for i, day in enumerate(days_data):
        running += day.get("day_total_usd", 0)
        pct = min(int(running / max(total_usd, 1) * 100), 100)
        if i < len(cols):
            with cols[i]:
                st.markdown(
                    f"<div style='text-align:center;font-size:.75rem;color:#8FA3B1;'>Day {day['day']}</div>"
                    f"<div style='text-align:center;font-size:.9rem;font-weight:700;color:#FF6B35;'>${running}</div>"
                    f"<div class='budget-bar-container'><div class='budget-bar-fill' style='width:{pct}%;'></div></div>"
                    f"<div style='text-align:center;font-size:.7rem;color:#8FA3B1;'>{pct}%</div>",
                    unsafe_allow_html=True,
                )

    st.divider()

    # ── Day cards ─────────────────────────────────────────────
    st.markdown("#### 🗺️ Your Day-by-Day Plan")
    for day in days_data:
        _render_day_card(day, prefs)

    st.divider()

    # ── Save trip ─────────────────────────────────────────────
    col_save, col_name = st.columns([1, 3])
    with col_name:
        trip_name = st.text_input(
            "Trip name",
            value=f"{itin.get('destination','My Trip')} — {prefs.get('dates','')}",
            label_visibility="collapsed",
        )
    with col_save:
        if st.button("💾 Save Trip", use_container_width=True):
            trip_id = save_trip(
                name=trip_name,
                preferences=prefs,
                itinerary=itin,
                destinations=st.session_state.destinations,
            )
            st.session_state.active_trip_id = trip_id
            st.success(f"✅ Saved! Trip ID: **{trip_id}**")


def _generate_itinerary(prefs: dict) -> None:
    with st.spinner("🗺️ Architecting your perfect trip…"):
        try:
            client = _get_client()
            prompt = itinerary_prompt(prefs)
            data   = client.generate_json(prompt)
            if isinstance(data, dict) and "days" in data:
                st.session_state.itinerary = data
                st.session_state.swap_results = {}
                st.success("✅ Itinerary generated!")
            else:
                st.error("Unexpected response format from AI. Please try again.")
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
            with st.expander("Debug info"):
                st.code(traceback.format_exc())


def _render_day_card(day: dict, prefs: dict) -> None:
    day_num = day.get("day", "?")
    theme   = day.get("theme", "")
    cluster = day.get("cluster_area", "")
    d_usd   = day.get("day_total_usd", 0)
    d_inr   = day.get("day_total_inr", 0)

    with st.expander(f"📅 Day {day_num}  —  {theme}  |  💵 ${d_usd}  /  ₹{d_inr:,}", expanded=(day_num == 1)):
        if cluster:
            st.markdown(
                f'<span class="tag-pill tag-blue">📍 {cluster}</span>',
                unsafe_allow_html=True,
            )

        slots = day.get("slots", [])
        # Apply any swapped slots
        swap_results = st.session_state.swap_results
        effective_slots = []
        for slot_idx, slot in enumerate(slots):
            key = (day_num, slot_idx)
            effective_slots.append(swap_results.get(key, slot))

        # Build slot HTML
        slots_html = ""
        for slot in effective_slots:
            icon  = slot.get("icon", "•")
            title = slot.get("title", "")
            desc  = slot.get("description", "")
            time  = slot.get("time", "")
            c_usd = slot.get("cost_usd", 0)
            c_inr = slot.get("cost_inr", 0)
            stype = slot.get("type", "")
            slots_html += f"""
            <div class="time-slot">
              <div class="slot-icon">{icon}</div>
              <div class="slot-body">
                <div class="slot-title">{time} — {title}
                  <span class="tag-pill tag-yellow" style="margin-left:.4rem;font-size:.7rem;">{stype}</span>
                </div>
                <div class="slot-desc">{desc}</div>
              </div>
              <div class="slot-cost">USD {c_usd}<br/><span style="font-size:.75rem;">₹{c_inr:,}</span></div>
            </div>
            """

        st.markdown(f'<div class="day-block">{slots_html}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  TAB 3 – VIBE CUSTOMISATION & ACTIVITY SWAP
# ══════════════════════════════════════════════════════════════
def render_tab_swap() -> None:
    st.markdown('<p class="section-header">🎨 Vibe Customisation & Activity Swap</p>', unsafe_allow_html=True)

    itin = st.session_state.itinerary
    if not itin or not itin.get("days"):
        st.info("ℹ️ Generate an itinerary first (Tab 2) to customise it here.")
        return

    st.markdown(
        '<div class="info-banner">💡 Swap individual activity slots without regenerating your entire plan. '
        'Changes are applied instantly and preserved when you export.</div>',
        unsafe_allow_html=True,
    )

    prefs = st.session_state.preferences
    days  = itin.get("days", [])

    # ── Swap controls ─────────────────────────────────────────
    st.markdown("#### 🔄 Swap an Activity")

    col1, col2 = st.columns(2)
    with col1:
        day_labels = [f"Day {d['day']} — {d['theme']}" for d in days]
        day_choice = st.selectbox("Select Day", day_labels)
        day_idx    = day_labels.index(day_choice)
        selected_day = days[day_idx]

    slots = selected_day.get("slots", [])
    # Include swap history
    swap_results = st.session_state.swap_results
    effective_slots = [
        swap_results.get((selected_day["day"], i), s)
        for i, s in enumerate(slots)
    ]
    slot_labels = [f"{s.get('time')} — {s.get('title')}" for s in effective_slots]

    with col2:
        slot_choice = st.selectbox("Select Slot to Swap", slot_labels)
        slot_idx    = slot_labels.index(slot_choice)
        original_slot = effective_slots[slot_idx]

    # Swap request text
    swap_request = st.text_input(
        "🎯 What do you want instead?",
        placeholder="e.g. 'Swap museum for outdoor market', 'Find vegetarian lunch spot', 'Something adventurous'",
    )

    col_swap, col_reset = st.columns([1, 1])
    with col_swap:
        do_swap = st.button("✨ Generate Swap", use_container_width=True, disabled=not swap_request.strip())
    with col_reset:
        do_reset = st.button("↩️ Reset This Slot", use_container_width=True)

    if do_reset:
        key = (selected_day["day"], slot_idx)
        if key in st.session_state.swap_results:
            del st.session_state.swap_results[key]
            st.success("✅ Slot reset to original.")
            st.rerun()

    if do_swap and swap_request.strip():
        with st.spinner("🔍 Finding the perfect alternative…"):
            try:
                client  = _get_client()
                prompt  = swap_activity_prompt(
                    destination   = itin.get("destination", ""),
                    day_num       = selected_day["day"],
                    day_theme     = selected_day.get("theme", ""),
                    original_slot = original_slot,
                    swap_request  = swap_request,
                    budget        = prefs.get("budget", "Moderate"),
                    interests     = prefs.get("interests", []),
                )
                result = client.generate_json(prompt)
                new_slot = result.get("new_slot", {})
                reason   = result.get("swap_reason", "")

                if new_slot:
                    key = (selected_day["day"], slot_idx)
                    st.session_state.swap_results[key] = new_slot
                    st.markdown(
                        f'<div class="success-banner">✅ Swapped! <em>{reason}</em></div>',
                        unsafe_allow_html=True,
                    )
                    st.rerun()
                else:
                    st.error("No valid alternative found. Try rephrasing your request.")
            except Exception as exc:
                st.error(f"Swap failed: {exc}")

    # ── Current day preview after swaps ──────────────────────
    st.divider()
    st.markdown(f"#### 📋 Preview: {day_choice}")

    for i, slot in enumerate(effective_slots):
        is_swapped = (selected_day["day"], i) in swap_results
        icon  = slot.get("icon", "•")
        title = slot.get("title", "")
        time  = slot.get("time", "")
        desc  = slot.get("description", "")
        c_usd = slot.get("cost_usd", 0)
        c_inr = slot.get("cost_inr", 0)
        badge = '<span class="tag-pill" style="background:rgba(26,147,111,.25);color:#6dd9b5;border-color:#1A936F;">🔄 SWAPPED</span>' if is_swapped else ""

        st.markdown(
            f"""
            <div class="time-slot" style="{'border-left:2px solid #1A936F;padding-left:.6rem;' if is_swapped else ''}">
              <div class="slot-icon">{icon}</div>
              <div class="slot-body">
                <div class="slot-title">{time} — {title} {badge}</div>
                <div class="slot-desc">{desc}</div>
              </div>
              <div class="slot-cost">USD {c_usd}<br/><span style="font-size:.75rem;">₹{c_inr:,}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Global vibe presets ───────────────────────────────────
    st.divider()
    st.markdown("#### 🌈 Quick Vibe Boost")
    st.caption("Apply a global preference shift — regenerates itinerary with a new lens:")

    vibe_cols = st.columns(4)
    vibe_presets = {
        "🍜 Foodie Mode":     "Focus heavily on food, restaurants, markets and cooking experiences",
        "🧘 Slow Travel":     "Replace rushed sightseeing with immersive local experiences and rest",
        "💸 Budget Crunch":   "Swap paid attractions for free alternatives, street food and public transport",
        "🎉 Party Mode":      "Add evening nightlife, rooftop bars, music venues and late-night experiences",
    }
    for col, (label, hint) in zip(vibe_cols, vibe_presets.items()):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.preferences["vibe_boost"] = hint
                st.info(f"💡 '{label}' applied — re-generate the itinerary to see changes!")


# ══════════════════════════════════════════════════════════════
#  TAB 4 – TRIP MANAGEMENT & EXPORT
# ══════════════════════════════════════════════════════════════
def render_tab_management() -> None:
    st.markdown('<p class="section-header">📁 Trip Management & Export</p>', unsafe_allow_html=True)

    # ── Current trip export ───────────────────────────────────
    itin  = st.session_state.itinerary
    prefs = st.session_state.preferences

    if itin and prefs:
        st.markdown("#### 📤 Export Current Trip")
        col1, col2, col3 = st.columns(3)

        with col1:
            if PDF_AVAILABLE:
                if st.button("📄 Download PDF Guide", use_container_width=True):
                    with st.spinner("📝 Generating PDF…"):
                        try:
                            # Apply swap overrides into itinerary copy
                            itin_copy = copy.deepcopy(itin)
                            for (day_num, slot_idx), new_slot in st.session_state.swap_results.items():
                                for day in itin_copy.get("days", []):
                                    if day["day"] == day_num:
                                        if slot_idx < len(day["slots"]):
                                            day["slots"][slot_idx] = new_slot
                            pdf_bytes = generate_pdf(
                                preferences  = prefs,
                                itinerary    = itin_copy,
                                destinations = st.session_state.destinations,
                            )
                            dest_name = itin.get("destination", "trip").replace(", ", "_").replace(" ", "_")
                            st.download_button(
                                label    = "⬇️ Click to Download PDF",
                                data     = pdf_bytes,
                                file_name= f"itinerary_{dest_name}.pdf",
                                mime     = "application/pdf",
                                use_container_width=True,
                            )
                        except Exception as exc:
                            st.error(f"PDF generation failed: {exc}")
                            with st.expander("Debug"):
                                st.code(traceback.format_exc())
            else:
                st.warning("⚠️ ReportLab not installed. Run `pip install reportlab` to enable PDF export.")

        with col2:
            # JSON export
            json_data = export_trips_json()
            st.download_button(
                label     = "📦 Export All Trips (JSON)",
                data      = json_data,
                file_name = "travel_trips.json",
                mime      = "application/json",
                use_container_width=True,
            )

        with col3:
            # Save current
            if st.button("💾 Save to History", use_container_width=True):
                dest_name = itin.get("destination", "My Trip")
                trip_id = save_trip(
                    name         = f"{dest_name} — {prefs.get('dates', '')}",
                    preferences  = prefs,
                    itinerary    = itin,
                    destinations = st.session_state.destinations,
                )
                st.success(f"✅ Saved! ID: **{trip_id}**")

    st.divider()

    # ── Trip history ──────────────────────────────────────────
    st.markdown("#### 🗂️ Trip History")
    trips = list_trips()

    if not trips:
        st.markdown(
            '<div class="info-banner">📭 No saved trips yet. Generate and save a trip to see it here.</div>',
            unsafe_allow_html=True,
        )
        return

    st.caption(f"📚 {len(trips)} saved trip(s)")

    for trip in trips:
        _render_trip_history_card(trip)


def _render_trip_history_card(trip: dict) -> None:
    tid   = trip.get("id", "???")
    name  = trip.get("name", "Unnamed Trip")
    prefs = trip.get("preferences", {})
    itin  = trip.get("itinerary", {})
    ts    = trip.get("created_at", "")
    dest  = itin.get("destination", prefs.get("destination", "Unknown"))
    days  = len(itin.get("days", []))
    total = itin.get("total_estimated_usd", 0)

    with st.container():
        st.markdown(
            f"""
            <div class="trip-hist">
              <div class="trip-hist-icon">✈️</div>
              <div class="trip-hist-meta">
                <div class="trip-hist-title">{name}</div>
                <div class="trip-hist-sub">
                  📍 {dest}  ·  📅 {days} days  ·  💵 ~${total:,}  ·  🆔 {tid}  ·  ⏰ {ts[:10]}
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button(f"📂 Load", key=f"load_{tid}", use_container_width=True):
                loaded = load_trip(tid)
                if loaded:
                    st.session_state.preferences  = loaded["preferences"]
                    st.session_state.itinerary    = loaded["itinerary"]
                    st.session_state.destinations = loaded.get("destinations", [])
                    st.session_state.swap_results = {}
                    st.success(f"✅ Trip **{name}** loaded!")
                    st.rerun()
        with col2:
            if st.button(f"🗑️ Delete", key=f"del_{tid}", use_container_width=True):
                delete_trip(tid)
                st.success("Deleted.")
                st.rerun()
        with col3:
            if PDF_AVAILABLE:
                if st.button(f"📄 PDF Export", key=f"pdf_{tid}", use_container_width=True):
                    loaded = load_trip(tid)
                    if loaded:
                        try:
                            pdf_bytes = generate_pdf(loaded["preferences"], loaded["itinerary"], loaded.get("destinations", []))
                            safe_name = dest.replace(", ", "_").replace(" ", "_")
                            st.download_button(
                                label=f"⬇️ Download {safe_name}.pdf",
                                data=pdf_bytes,
                                file_name=f"itinerary_{safe_name}.pdf",
                                mime="application/pdf",
                                key=f"dl_{tid}",
                                use_container_width=True,
                            )
                        except Exception as exc:
                            st.error(f"PDF failed: {exc}")


# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def _get_client() -> AIClient:
    """Return existing client or auto-create a demo client."""
    if st.session_state.ai_client is None:
        client = AIClient(provider="demo")
        st.session_state.ai_client = client
        st.session_state.provider  = "demo"
    return st.session_state.ai_client


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main() -> None:
    # ── Hero banner ───────────────────────────────────────────
    st.markdown(
        f"""
        <div class="hero-banner">
          <p class="hero-title">{APP_TITLE}</p>
          <p class="hero-sub">🌐 AI-Powered · 🗺️ Day-by-Day Plans · 💰 Budget Tracker · 📄 PDF Export</p>
          <p style="color:rgba(255,255,255,.6);font-size:.78rem;margin-top:.3rem;position:relative;">{APP_SUBTITLE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar
    render_sidebar()

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌍 Destination Finder",
        "🗓️ Itinerary Generator",
        "🎨 Vibe & Swap",
        "📁 Manage & Export",
    ])

    with tab1:
        render_tab_destinations()
    with tab2:
        render_tab_itinerary()
    with tab3:
        render_tab_swap()
    with tab4:
        render_tab_management()


if __name__ == "__main__":
    main()

