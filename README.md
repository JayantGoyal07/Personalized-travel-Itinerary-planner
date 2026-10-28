# ✈️ Personalized Travel Itinerary Planner

> **Skill Wallet Capstone Project 4** — AI-powered travel planning SaaS built with Streamlit

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/cloud)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

## 🌍 Features

| Module | Description |
|--------|-------------|
| 🔑 **Configuration** | Secure API key input for Gemini / Groq with full Demo Mode |
| 🌍 **Destination Finder** | AI recommends top 3 cities by vibe, budget & season |
| 🗓️ **Itinerary Generator** | Day-by-day plans with geographic clustering & budget tracking |
| 🎨 **Vibe & Swap** | Swap individual slots without wiping the full plan |
| 📁 **Manage & Export** | Trip history, 1-click PDF download, JSON export |

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Open your browser
Navigate to `http://localhost:8501`

## 🔑 API Keys (Optional)

The app runs fully in **Demo Mode** without any API key — rich offline data is used.

To unlock AI-powered planning:
- **Google Gemini**: Get a free key at [aistudio.google.com](https://aistudio.google.com/apikey)
- **Groq**: Get a free key at [console.groq.com](https://console.groq.com/)

Paste your key in the sidebar → **Connect**.

## 📁 Project Structure

```
my new project/
├── app.py              # Main Streamlit application
├── config.py           # Constants & configuration
├── styles.py           # Wanderlust CSS theme
├── ai_client.py        # Gemini / Groq / Demo AI wrapper
├── prompts.py          # AI prompt templates
├── trip_store.py       # Session-state trip persistence
├── pdf_export.py       # ReportLab PDF generator
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── config.toml     # Streamlit theme config
└── README.md
```

## ☁️ Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set `app.py` as entry point → Deploy
4. Add API keys as **Secrets** in the cloud dashboard (optional)

## 🎒 Epics Coverage

- **Epic 3**: Configuration, User Preferences, Destination Recommender ✅
- **Epic 4**: Itinerary Generator (geo-clustering, budget tracker), Vibe & Swap ✅  
- **Epic 5**: Trip Management, PDF Export, Emergency Checklist ✅

