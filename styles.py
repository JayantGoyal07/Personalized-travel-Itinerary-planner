# ============================================================
# styles.py  –  Wanderlust-inspired CSS
# ============================================================

GLOBAL_CSS = """
<style>
/* ── Google Fonts ──────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

/* ── Root variables ────────────────────────────────────── */
:root {
    --primary:   #FF6B35;
    --secondary: #004E89;
    --accent:    #1A936F;
    --warn:      #F4A261;
    --bg-dark:   #0D1B2A;
    --bg-card:   #1B2A3B;
    --text:      #E8F4F8;
    --muted:     #8FA3B1;
    --radius:    14px;
    --shadow:    0 8px 32px rgba(0,0,0,.45);
}

/* ── App background ────────────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0D1B2A 0%, #1a2d42 50%, #0f2337 100%);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

/* ── Hide default Streamlit chrome ─────────────────────── */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1.5rem; padding-bottom: 3rem;}

/* ── Hero banner ────────────────────────────────────────── */
.hero-banner {
    background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 40%, #004E89 100%);
    border-radius: var(--radius);
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute; inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #fff;
    margin: 0;
    text-shadow: 0 2px 8px rgba(0,0,0,.4);
    position: relative;
}
.hero-sub {
    color: rgba(255,255,255,.85);
    font-size: 1rem;
    margin-top: .5rem;
    letter-spacing: .05em;
    position: relative;
}

/* ── Section cards ──────────────────────────────────────── */
.travel-card {
    background: var(--bg-card);
    border: 1px solid rgba(255,107,53,.25);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: var(--shadow);
    transition: border-color .25s;
}
.travel-card:hover {border-color: var(--primary);}

/* ── Tag / badge pills ──────────────────────────────────── */
.tag-pill {
    display: inline-block;
    background: rgba(255,107,53,.18);
    color: var(--primary);
    border: 1px solid rgba(255,107,53,.4);
    border-radius: 999px;
    padding: .18rem .75rem;
    font-size: .78rem;
    font-weight: 600;
    margin: .15rem .1rem;
    letter-spacing: .03em;
}
.tag-green  {background:rgba(26,147,111,.18);color:#1A936F;border-color:rgba(26,147,111,.4);}
.tag-blue   {background:rgba(0,78,137,.28);color:#5DB8E8;border-color:rgba(93,184,232,.35);}
.tag-yellow {background:rgba(244,162,97,.18);color:#F4A261;border-color:rgba(244,162,97,.4);}

/* ── Day itinerary block ────────────────────────────────── */
.day-block {
    background: linear-gradient(135deg, #1B2A3B 0%, #1e3048 100%);
    border-left: 4px solid var(--primary);
    border-radius: 0 var(--radius) var(--radius) 0;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(0,0,0,.3);
}
.day-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    color: var(--primary);
    margin-bottom: .6rem;
}
.time-slot {
    display: flex;
    align-items: flex-start;
    gap: .75rem;
    padding: .5rem 0;
    border-bottom: 1px solid rgba(255,255,255,.06);
}
.time-slot:last-child {border-bottom: none;}
.slot-icon {font-size: 1.3rem; min-width: 2rem; text-align: center;}
.slot-body {flex: 1;}
.slot-title {font-weight: 600; color: var(--text);}
.slot-desc  {font-size: .85rem; color: var(--muted); margin-top: .15rem;}
.slot-cost  {font-size: .82rem; color: var(--accent); font-weight: 600; white-space: nowrap;}

/* ── Budget tracker bar ─────────────────────────────────── */
.budget-bar-container {
    background: rgba(255,255,255,.08);
    border-radius: 999px;
    height: 10px;
    margin: .5rem 0;
    overflow: hidden;
}
.budget-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #1A936F, #F4A261, #FF6B35);
    transition: width .5s ease;
}

/* ── Destination recommendation card ───────────────────── */
.dest-card {
    background: linear-gradient(135deg, #1B2A3B, #22344a);
    border: 2px solid rgba(255,107,53,.2);
    border-radius: var(--radius);
    padding: 1.4rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: all .3s ease;
}
.dest-card:hover {
    border-color: var(--primary);
    transform: translateY(-2px);
    box-shadow: 0 12px 36px rgba(255,107,53,.2);
}
.dest-rank {
    position: absolute; top: 1rem; right: 1rem;
    background: var(--primary);
    color: #fff; font-weight: 700; font-size: .85rem;
    width: 2rem; height: 2rem;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
}
.dest-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem; color: #fff; margin-bottom: .4rem;
}
.dest-tagline {color: var(--muted); font-size: .9rem; margin-bottom: .8rem;}

/* ── Emergency checklist ────────────────────────────────── */
.checklist-item {
    display: flex; align-items: center; gap: .6rem;
    padding: .4rem 0;
    border-bottom: 1px solid rgba(255,255,255,.05);
    color: var(--text); font-size: .9rem;
}
.checklist-item:last-child {border-bottom: none;}

/* ── Trip history card ──────────────────────────────────── */
.trip-hist {
    background: var(--bg-card);
    border: 1px solid rgba(93,184,232,.2);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin-bottom: .8rem;
    display: flex; align-items: center; gap: 1rem;
}
.trip-hist-icon {font-size: 2rem;}
.trip-hist-meta {flex:1;}
.trip-hist-title {font-weight: 600; color: var(--text);}
.trip-hist-sub   {font-size: .82rem; color: var(--muted);}

/* ── Streamlit widget overrides ─────────────────────────── */
div[data-testid="stTabs"] button {
    color: var(--muted) !important;
    font-weight: 500;
    border-radius: 8px 8px 0 0;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 3px solid var(--primary);
    background: rgba(255,107,53,.08) !important;
}
div[data-testid="stSidebar"] {
    background: #0a1520 !important;
    border-right: 1px solid rgba(255,107,53,.15);
}
.stButton > button {
    background: linear-gradient(135deg, var(--primary), #e85d2a) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: .5rem 1.4rem !important;
    transition: all .25s !important;
    box-shadow: 0 4px 14px rgba(255,107,53,.4) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(255,107,53,.55) !important;
}
div[data-testid="stMetricValue"] {
    color: var(--primary) !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}

/* ── Section header ─────────────────────────────────────── */
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    color: #fff;
    margin: 1.2rem 0 .8rem;
    padding-bottom: .4rem;
    border-bottom: 2px solid rgba(255,107,53,.35);
}

/* ── Info banner ────────────────────────────────────────── */
.info-banner {
    background: rgba(0,78,137,.25);
    border: 1px solid rgba(93,184,232,.3);
    border-radius: 10px;
    padding: .9rem 1.1rem;
    margin-bottom: 1rem;
    font-size: .9rem;
    color: #a8d8f0;
}

/* ── Success banner ─────────────────────────────────────── */
.success-banner {
    background: rgba(26,147,111,.2);
    border: 1px solid rgba(26,147,111,.4);
    border-radius: 10px;
    padding: .9rem 1.1rem;
    margin-bottom: 1rem;
    color: #6dd9b5;
    font-size: .9rem;
}

/* ── Scrollable itinerary area ──────────────────────────── */
.itinerary-scroll {max-height: 70vh; overflow-y: auto; padding-right: .4rem;}

/* ── Scrollbar styling ──────────────────────────────────── */
::-webkit-scrollbar {width: 6px;}
::-webkit-scrollbar-track {background: transparent;}
::-webkit-scrollbar-thumb {background: rgba(255,107,53,.4); border-radius: 3px;}
</style>
"""

