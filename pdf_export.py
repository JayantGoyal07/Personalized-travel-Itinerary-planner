# ============================================================
# pdf_export.py  –  ReportLab PDF generator
# Produces a beautiful, formatted offline travel guide
# ============================================================
from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.colors import HexColor

# ── Brand colours ─────────────────────────────────────────────
C_PRIMARY   = HexColor("#FF6B35")
C_SECONDARY = HexColor("#004E89")
C_ACCENT    = HexColor("#1A936F")
C_DARK      = HexColor("#0D1B2A")
C_MUTED     = HexColor("#8FA3B1")
C_WHITE     = colors.white
C_LIGHT     = HexColor("#E8F4F8")
C_WARN      = HexColor("#F4A261")


# ──────────────────────────────────────────────────────────────
def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=26,
            textColor=C_WHITE,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Helvetica",
            fontSize=11,
            textColor=HexColor("#ccddee"),
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Helvetica-Bold",
            fontSize=15,
            textColor=C_PRIMARY,
            spaceBefore=14,
            spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "h3",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=HexColor("#1B2A3B"),
            spaceBefore=6,
            spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=HexColor("#2c3e50"),
            spaceAfter=3,
            leading=14,
        ),
        "muted": ParagraphStyle(
            "muted",
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            textColor=C_MUTED,
            spaceAfter=2,
        ),
        "cost": ParagraphStyle(
            "cost",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=C_ACCENT,
            alignment=TA_RIGHT,
        ),
        "checklist": ParagraphStyle(
            "checklist",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=HexColor("#2c3e50"),
            spaceAfter=5,
            leftIndent=12,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=C_MUTED,
            alignment=TA_CENTER,
        ),
    }


# ──────────────────────────────────────────────────────────────
def _header_canvas(canvas, doc):
    """Draw page header & footer on every page."""
    canvas.saveState()
    w, h = A4
    # footer line
    canvas.setStrokeColor(C_PRIMARY)
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.5 * cm, w - 2 * cm, 1.5 * cm)
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(C_MUTED)
    canvas.drawCentredString(w / 2, 1.0 * cm, f"✈ Personalized Travel Itinerary Planner  |  Generated {datetime.now().strftime('%d %b %Y')}")
    canvas.drawRightString(w - 2 * cm, 1.0 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ──────────────────────────────────────────────────────────────
def generate_pdf(preferences: dict, itinerary: dict, destinations: list | None = None) -> bytes:
    """
    Generate a complete travel itinerary PDF and return bytes.

    Parameters
    ----------
    preferences : dict  – user trip preferences
    itinerary   : dict  – structured day-by-day itinerary
    destinations: list  – optional destination recommendations

    Returns
    -------
    bytes – the raw PDF binary
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.5 * cm,
    )
    S = _styles()
    story = []
    w, _ = A4

    # ── COVER PAGE ────────────────────────────────────────────
    # Dark banner background via table
    dest = itinerary.get("destination", preferences.get("destination", "Your Destination"))
    duration = preferences.get("duration", "?")
    party = preferences.get("party", "")
    budget = preferences.get("budget", "")

    cover_data = [[
        Paragraph("✈ TRAVEL ITINERARY GUIDE", S["title"]),
    ]]
    cover_table = Table(cover_data, colWidths=[w - 4 * cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 8))

    # Destination & meta row
    meta_rows = [[
        Paragraph(f"<b>{dest}</b>", ParagraphStyle("dm", fontName="Helvetica-Bold", fontSize=20, textColor=C_PRIMARY)),
        "",
    ]]
    meta_table = Table(meta_rows, colWidths=[(w - 4 * cm) * 0.6, (w - 4 * cm) * 0.4])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#1B2A3B")),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # Summary metrics table
    metrics = [
        ["📅 Duration", f"{duration} Days"],
        ["👥 Travel Party", party],
        ["💰 Budget", budget],
        ["📌 Pace", preferences.get("pace", "Moderate")],
        ["🗓️ Dates", preferences.get("dates", "Flexible")],
    ]
    met_table = Table(metrics, colWidths=[(w - 4 * cm) * 0.35, (w - 4 * cm) * 0.65])
    met_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (0, -1), HexColor("#e8f0f7")),
        ("BACKGROUND",  (1, 0), (1, -1), C_WHITE),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR",   (0, 0), (0, -1), C_SECONDARY),
        ("TEXTCOLOR",   (1, 0), (1, -1), HexColor("#2c3e50")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#cccccc")),
    ]))
    story.append(met_table)
    story.append(Spacer(1, 8))

    # Trip summary
    if itinerary.get("trip_summary"):
        story.append(Paragraph(itinerary["trip_summary"], S["body"]))
    story.append(Spacer(1, 6))

    # Budget overview
    total_usd = itinerary.get("total_estimated_usd", 0)
    total_inr = itinerary.get("total_estimated_inr", 0)
    currency_note = itinerary.get("currency_note", "")
    budget_data = [
        [Paragraph("Total Estimated Cost", S["h3"]),
         Paragraph(f"USD {total_usd:,.0f}  /  ₹ {total_inr:,.0f}", ParagraphStyle("bc", fontName="Helvetica-Bold", fontSize=13, textColor=C_ACCENT))],
        [Paragraph(currency_note, S["muted"]), ""],
    ]
    b_table = Table(budget_data, colWidths=[(w - 4 * cm) * 0.5, (w - 4 * cm) * 0.5])
    b_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), HexColor("#f0fff8")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("BOX", (0, 0), (-1, -1), 1, C_ACCENT),
        ("ROUNDEDCORNERS", [6]),
        ("SPAN", (0, 1), (-1, 1)),
    ]))
    story.append(b_table)
    story.append(PageBreak())

    # ── DAY-BY-DAY ITINERARY ──────────────────────────────────
    story.append(Paragraph("🗺️ Day-by-Day Itinerary", S["h2"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_PRIMARY, spaceAfter=8))

    days = itinerary.get("days", [])
    running_usd = 0
    running_inr = 0

    for day in days:
        day_num  = day.get("day", "?")
        theme    = day.get("theme", "")
        cluster  = day.get("cluster_area", "")
        day_usd  = day.get("day_total_usd", 0)
        day_inr  = day.get("day_total_inr", 0)
        running_usd += day_usd
        running_inr += day_inr

        # Day header band
        day_header = [[
            Paragraph(f"Day {day_num}  —  {theme}", ParagraphStyle(
                "dh", fontName="Helvetica-Bold", fontSize=13, textColor=C_WHITE)),
            Paragraph(f"USD {day_usd}  /  ₹{day_inr:,}", ParagraphStyle(
                "dc", fontName="Helvetica-Bold", fontSize=10, textColor=HexColor("#ffcc99"), alignment=TA_RIGHT)),
        ]]
        dh_table = Table(day_header, colWidths=[(w - 4 * cm) * 0.7, (w - 4 * cm) * 0.3])
        dh_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_SECONDARY),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ]))
        story.append(dh_table)

        # Cluster area note
        if cluster:
            story.append(Paragraph(f"📍 Area: {cluster}", S["muted"]))

        # Slots table
        slot_rows = [["Time", "Activity", "Description", "Cost (USD)"]]
        for slot in day.get("slots", []):
            icon  = slot.get("icon", "•")
            title = slot.get("title", "")
            desc  = slot.get("description", "")
            cost  = slot.get("cost_usd", 0)
            time  = slot.get("time", "")
            slot_rows.append([
                Paragraph(f"{time}", ParagraphStyle("st", fontName="Helvetica-Bold", fontSize=8.5, textColor=C_SECONDARY)),
                Paragraph(f"{icon} {title}", ParagraphStyle("sat", fontName="Helvetica-Bold", fontSize=9)),
                Paragraph(desc, ParagraphStyle("sd", fontName="Helvetica", fontSize=8.5, textColor=HexColor("#444444"), leading=12)),
                Paragraph(f"${cost}", S["cost"]),
            ])

        col_w = w - 4 * cm
        slot_table = Table(
            slot_rows,
            colWidths=[col_w * 0.12, col_w * 0.23, col_w * 0.52, col_w * 0.13],
        )
        slot_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), HexColor("#e8f0f7")),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0), 8.5),
            ("TEXTCOLOR",     (0, 0), (-1, 0), C_SECONDARY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, HexColor("#f7fafc")]),
            ("GRID",          (0, 0), (-1, -1), 0.25, HexColor("#dde4ec")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(slot_table)

        # Running total
        story.append(Paragraph(
            f"<b>Cumulative spend after Day {day_num}:</b>  USD {running_usd:,}  /  ₹{running_inr:,}",
            ParagraphStyle("rt", fontName="Helvetica-Oblique", fontSize=8.5, textColor=C_ACCENT, spaceAfter=8),
        ))
        story.append(Spacer(1, 6))

    # ── DESTINATION RECOMMENDATIONS (optional) ─────────────────
    if destinations:
        story.append(PageBreak())
        story.append(Paragraph("🌍 Destination Highlights", S["h2"]))
        story.append(HRFlowable(width="100%", thickness=1.5, color=C_PRIMARY, spaceAfter=8))
        for d in destinations:
            story.append(Paragraph(f"{d.get('emoji','')} #{d.get('rank','')}  {d.get('city','')}", S["h3"]))
            story.append(Paragraph(d.get("tagline", ""), S["body"]))
            tags = "  ".join(f"[{t}]" for t in d.get("tags", []))
            story.append(Paragraph(tags, ParagraphStyle("tags", fontName="Helvetica-Oblique", fontSize=8.5, textColor=C_SECONDARY)))
            story.append(Paragraph(
                f"Best time: {d.get('best_months','')}  |  Avg/day: USD {d.get('avg_daily_usd','')} / ₹{d.get('avg_daily_inr','')}",
                S["muted"],
            ))
            story.append(Spacer(1, 5))

    # ── EMERGENCY CONTACT CHECKLIST ───────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("🆘 Emergency Contact Checklist", S["h2"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_WARN, spaceAfter=8))

    checklist_sections = {
        "🏥 Medical & Health": [
            "Local emergency number (police/ambulance): ___________________________",
            "Nearest hospital / clinic address: ___________________________________",
            "Travel insurance policy number: ______________________________________",
            "Insurance 24-hr helpline: ____________________________________________",
            "Personal doctor contact (home): ______________________________________",
            "Known allergies / medications: _______________________________________",
        ],
        "🛂 Travel Documents": [
            "Passport number & expiry: ____________________________________________",
            "Visa reference number: _______________________________________________",
            "Return flight booking reference: _____________________________________",
            "Hotel confirmation number: ___________________________________________",
            "Photocopy stored separately: ☐ Yes  ☐ No",
            "Digital copies in cloud/email: ☐ Yes  ☐ No",
        ],
        "🏦 Financial": [
            "Bank 24-hr card block number: ________________________________________",
            "Emergency cash (USD / local currency) amount: ________________________",
            "Travel card / forex card number (last 4): ____________________________",
            "Emergency contact who can wire money: ________________________________",
        ],
        "🏠 Home & Local Contacts": [
            "Emergency contact name & phone: ______________________________________",
            "Home country embassy address & phone: ________________________________",
            "Hotel front desk number: _____________________________________________",
            "Local tour operator / guide contact: __________________________________",
            "Trusted local taxi / driver: __________________________________________",
        ],
    }

    for section_title, items in checklist_sections.items():
        story.append(Paragraph(section_title, S["h3"]))
        for item in items:
            story.append(Paragraph(f"☐  {item}", S["checklist"]))
        story.append(Spacer(1, 4))

    # ── PACKING ESSENTIALS ────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("🎒 Packing Essentials Checklist", S["h2"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_ACCENT, spaceAfter=8))

    packing = {
        "👔 Clothing": [
            "Lightweight, breathable clothing (x{} days)".format(duration),
            "Rain jacket / travel umbrella",
            "Comfortable walking shoes",
            "Swimwear / beach attire",
            "Formal outfit (if needed)",
        ],
        "💊 Health & Safety": [
            "Prescription medications (extra supply)",
            "First aid kit (plasters, antiseptic, pain relief)",
            "Sunscreen SPF 50+ & insect repellent",
            "Hand sanitizer & wet wipes",
            "Rehydration sachets",
        ],
        "🔌 Tech & Gadgets": [
            "Universal travel adapter",
            "Power bank (20,000 mAh recommended)",
            "Phone & camera chargers",
            "Noise-cancelling headphones",
            "Portable Wi-Fi / SIM card (local)",
        ],
        "📄 Documents": [
            "Passport (+ 2 photocopies)",
            "Travel insurance documents",
            "Visa & booking confirmations (printed)",
            "This PDF itinerary guide ✈",
            "Emergency contact card (wallet-sized)",
        ],
    }

    for section_title, items in packing.items():
        story.append(Paragraph(section_title, S["h3"]))
        for item in items:
            story.append(Paragraph(f"☐  {item}", S["checklist"]))
        story.append(Spacer(1, 4))

    # ── BUILD ─────────────────────────────────────────────────
    doc.build(story, onFirstPage=_header_canvas, onLaterPages=_header_canvas)
    return buf.getvalue()

