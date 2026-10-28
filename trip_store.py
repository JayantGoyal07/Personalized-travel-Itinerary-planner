# ============================================================
# trip_store.py  –  In-memory + session-state trip persistence
# Zero external database dependencies
# ============================================================
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

import streamlit as st


# ──────────────────────────────────────────────────────────────
def _init_store() -> None:
    """Ensure session_state has the trips store."""
    if "trips_db" not in st.session_state:
        st.session_state.trips_db = {}


# ──────────────────────────────────────────────────────────────
def save_trip(
    name: str,
    preferences: dict,
    itinerary: dict,
    destinations: list | None = None,
) -> str:
    """Persist a trip and return its ID."""
    _init_store()
    trip_id = str(uuid.uuid4())[:8].upper()
    st.session_state.trips_db[trip_id] = {
        "id":           trip_id,
        "name":         name,
        "created_at":   datetime.now().isoformat(timespec="seconds"),
        "preferences":  preferences,
        "itinerary":    itinerary,
        "destinations": destinations or [],
    }
    return trip_id


# ──────────────────────────────────────────────────────────────
def list_trips() -> list[dict]:
    """Return all saved trips sorted newest-first."""
    _init_store()
    trips = list(st.session_state.trips_db.values())
    trips.sort(key=lambda t: t["created_at"], reverse=True)
    return trips


# ──────────────────────────────────────────────────────────────
def load_trip(trip_id: str) -> dict | None:
    """Load a trip by ID or return None."""
    _init_store()
    return st.session_state.trips_db.get(trip_id)


# ──────────────────────────────────────────────────────────────
def delete_trip(trip_id: str) -> bool:
    """Delete a trip; return True if found and deleted."""
    _init_store()
    if trip_id in st.session_state.trips_db:
        del st.session_state.trips_db[trip_id]
        return True
    return False


# ──────────────────────────────────────────────────────────────
def export_trips_json() -> str:
    """Serialise all trips to JSON string for download."""
    _init_store()
    return json.dumps(list(st.session_state.trips_db.values()), indent=2, default=str)

