"""
utils/pdf_export.py
PDF-Export für MediTrack: Einnahmen, Blutdruck, Blutzucker, Stimmung.
Verwendet fpdf2 (pip install fpdf2).
"""

from datetime import datetime


def _header(pdf, title: str, profile: dict):
    """Zeichnet den Seitenkopf mit Logo, Titel und Profilinfos."""
    # Farbiger Balken oben
    pdf.set_fill_color(37, 99, 235)
    pdf.rect(0, 0, 210, 18, 'F')
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, 4)
    pdf.cell(0, 10, "💊 MediTrack", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(22)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(17, 24, 39)
    pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 5, f"Erstellt am: {datetime.now().strftime('%d.%m.%Y, %H:%M Uhr')}", new_x="LMARGIN", new_y="NEXT")

    # Profilzeile
    firstname = profile.get("firstname", "")
    lastname  = profile.get("lastname", "")
    fullname  = f"{firstname} {lastname}".strip()
    parts = []
    if fullname: parts.append(f"Patient/in: {fullname}")
    if profile.get("birthdate"): parts.append(f"Geb.: {profile['birthdate']}")
    if profile.get("doctor"): parts.append(f"Arzt: {profile['doctor']}")
    if profile.get("blood_type") and profile["blood_type"] != "—":
        parts.append(f"Blutgruppe: {profile['blood_type']}")
    if parts:
        pdf.cell(0, 5, "  |  ".join(parts), new_x="LMARGIN", new_y="NEXT")
    if profile.get("emergency"):
        pdf.cell(0, 5, f"Notfall: {profile['emergency']}  {profile.get('emergency_phone','')}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.set_draw_color(229, 231, 235)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)


def _section_title(pdf, title: str, color=(37, 99, 235)):
    """Zeichnet einen farbigen Abschnittstitel."""
    pdf.set_fill_color(*color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, f"  {title}", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.set_text_color(17, 24, 39)
    pdf.ln(2)


def _table_header(pdf, headers: list, widths: list, color=(239, 246, 255)):
    """Zeichnet einen Tabellenkopf."""
    pdf.set_fill_color(*color)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(37, 99, 235)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    pdf.set_text_color(17, 24, 39)


def _table_row(pdf, values: list, widths: list, idx: int):
    """Zeichnet eine Tabellenzeile mit alternierenden Farben."""
    if idx % 2 == 0:
        pdf.set_fill_color(249, 250, 251)
    else:
        pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Helvetica", "", 9)
    for val, w in zip(values, widths):
        pdf.cell(w, 6, str(val)[:40], border=1, fill=True)
    pdf.ln()


def generate_pdf(
    profile: dict,
    include_intakes: bool = False,
    include_bp: bool = False,
    include_bs: bool = False,
    include_mood: bool = False,
    intakes_df=None,
    bp_df=None,
    bs_df=None,
    mood_df=None,
) -> bytes:
    """
    Erstellt ein PDF mit den gewählten Gesundheitsdaten.
    Gibt die PDF-Bytes zurück.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("fpdf2 ist nicht installiert. Bitte 'pip install fpdf2' ausführen.")

    import pandas as pd

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Titel bestimmen
    sections = []
    if include_intakes: sections.append("Einnahmen")
    if include_bp:      sections.append("Blutdruck")
    if include_bs:      sections.append("Blutzucker")
    if include_mood:    sections.append("Stimmung")
    title = "Gesundheitsbericht" if len(sections) > 1 else (sections[0] if sections else "Bericht")

    _header(pdf, title, profile)

    # ── 1. Medikamenten-Einnahmen ─────────────────────────────────────────────
    if include_intakes and intakes_df is not None and not intakes_df.empty:
        _section_title(pdf, "Medikamenten-Einnahmen", color=(37, 99, 235))
        df = intakes_df.copy().sort_values(["date","time"], ascending=False)

        headers = ["Datum", "Medikament", "Uhrzeit", "Status", "Bemerkung"]
        widths  = [28, 55, 20, 28, 59]
        _table_header(pdf, headers, widths)

        for i, (_, row) in enumerate(df.iterrows()):
            confirmed = str(row.get("confirmed","")).lower() in ["true","1","yes"]
            status    = "✓ Bestätigt" if confirmed else "✗ Ausstehend"
            note      = str(row.get("note",""))[:30] if row.get("note") and str(row.get("note","")).strip() else "—"
            _table_row(pdf, [
                str(row.get("date",""))[:10],
                str(row.get("medication_name",""))[:28],
                str(row.get("time",""))[:5],
                status,
                note,
            ], widths, i)
        pdf.ln(4)

    # ── 2. Blutdruck ──────────────────────────────────────────────────────────
    if include_bp and bp_df is not None and not bp_df.empty:
        if pdf.get_y() > 220:
            pdf.add_page()
            _header(pdf, title, profile)

        _section_title(pdf, "Blutdruck-Tagebuch", color=(239, 68, 68))

        def bp_status(sys, dia):
            if sys >= 180 or dia >= 110: return "Hypertonie Grad 3"
            if sys >= 160 or dia >= 100: return "Hypertonie Grad 2"
            if sys >= 140 or dia >= 90:  return "Hypertonie Grad 1"
            if sys >= 130 or dia >= 85:  return "Hoch-normal"
            if sys >= 120 or dia >= 80:  return "Normal"
            if sys < 100 or dia < 60:    return "Hypotonie"
            return "Optimal"

        df = bp_df.copy().sort_values("date", ascending=False)
        headers = ["Datum", "Systolisch", "Diastolisch", "Status"]
        widths  = [35, 42, 42, 71]
        _table_header(pdf, headers, widths, color=(254, 242, 242))

        for i, (_, row) in enumerate(df.iterrows()):
            sv  = int(row.get("systolic", 0))
            dv  = int(row.get("diastolic", 0))
            _table_row(pdf, [
                str(row.get("date",""))[:10],
                f"{sv} mmHg",
                f"{dv} mmHg",
                bp_status(sv, dv),
            ], widths, i)
        pdf.ln(4)

    # ── 3. Blutzucker ─────────────────────────────────────────────────────────
    if include_bs and bs_df is not None and not bs_df.empty:
        if pdf.get_y() > 220:
            pdf.add_page()
            _header(pdf, title, profile)

        _section_title(pdf, "Blutzucker-Tagebuch (Nüchternwerte)", color=(139, 92, 246))

        def bs_status(val):
            if val < 3.0:   return "Kritisch tief"
            if val < 3.9:   return "Auffällig tief"
            if val <= 5.5:  return "Normal"
            if val < 7.0:   return "Auffällig hoch"
            return "Kritisch hoch"

        df = bs_df.copy().sort_values("date", ascending=False)
        headers = ["Datum", "Blutzucker (mmol/l)", "Status"]
        widths  = [35, 60, 95]
        _table_header(pdf, headers, widths, color=(245, 243, 255))

        for i, (_, row) in enumerate(df.iterrows()):
            val = float(row.get("value", 0))
            _table_row(pdf, [
                str(row.get("date",""))[:10],
                f"{val:.1f} mmol/l",
                bs_status(val),
            ], widths, i)
        pdf.ln(4)

    # ── 4. Stimmung ───────────────────────────────────────────────────────────
    if include_mood and mood_df is not None and not mood_df.empty:
        if pdf.get_y() > 220:
            pdf.add_page()
            _header(pdf, title, profile)

        _section_title(pdf, "Stimmungsverlauf", color=(16, 185, 129))

        MOOD_LABELS = {
            "great": "😄 Sehr gut", "good": "🙂 Gut", "okay": "😐 Okay",
            "bad": "😕 Schlecht", "terrible": "😞 Sehr schlecht",
        }

        df = mood_df.copy().sort_values("date", ascending=False)
        headers = ["Datum", "Stimmung", "Kommentar"]
        widths  = [35, 45, 110]
        _table_header(pdf, headers, widths, color=(236, 253, 245))

        for i, (_, row) in enumerate(df.iterrows()):
            mood_key   = str(row.get("mood_key","okay"))
            mood_label = MOOD_LABELS.get(mood_key, str(row.get("mood_label","")))
            note       = str(row.get("note",""))[:50] if row.get("note") and str(row.get("note","")).strip() else "—"
            # Emojis aus FPDF entfernen (nicht unterstützt)
            mood_label_clean = mood_label.replace("😄","").replace("🙂","").replace("😐","").replace("😕","").replace("😞","").strip()
            _table_row(pdf, [
                str(row.get("date",""))[:10],
                mood_label_clean,
                note,
            ], widths, i)
        pdf.ln(4)

    # ── Footer ────────────────────────────────────────────────────────────────
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(156, 163, 175)
    pdf.cell(0, 5, f"MediTrack – Gesundheitsbericht  |  Seite {pdf.page_no()}  |  {datetime.now().strftime('%d.%m.%Y')}", align="C")

    return bytes(pdf.output())