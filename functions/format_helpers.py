"""
functions/format_helpers.py
Hilfsfunktionen für HTML-Escaping, ID-Generierung und Formatierung.
"""

import html
import pandas as pd
from utils.translations import t


def e(text):
    """HTML-Escape für sichere Anzeige in st.markdown."""
    return html.escape(str(text))


def next_id(df):
    """Nächste freie ID in einem DataFrame."""
    if df.empty or "id" not in df.columns:
        return 1
    return int(df["id"].max()) + 1


def is_confirmed(val):
    """Prüft ob ein Wert als 'bestätigt' gilt."""
    return str(val).strip().lower() in ["true", "1", "yes"]


def format_days(days_str):
    """
    Formatiert den days-String (intern immer DE-Kürzel) in die aktuelle Sprache.
    Beispiel: 'Mo,Di,Mi,Do,Fr,Sa,So' → 'Täglich' / 'Daily' / 'Tutti i giorni'
    """
    if not days_str or pd.isna(days_str):
        return "—"
    days = [d.strip() for d in str(days_str).split(",")]
    DAYS_ALL = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    if days == DAYS_ALL:
        return t("daily")
    if days == ["Mo", "Di", "Mi", "Do", "Fr"]:
        return t("mo_fr")
    shorts_de         = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    shorts_translated = t("weekdays_short").split(",")
    mapped = [
        shorts_translated[shorts_de.index(d)] if d in shorts_de else d
        for d in days
    ]
    return ", ".join(mapped)


def get_weekday_name(weekday_int):
    """Gibt den übersetzten Wochentagnamen zurück (0=Mo, 6=So)."""
    return t("weekdays_long").split(",")[weekday_int]


def get_month_name(month_int):
    """Gibt den übersetzten Monatsnamen zurück (1=Januar, 12=Dezember)."""
    return t("months").split(",")[month_int - 1]


# Globale Konstante: Wochentag-Kürzel (intern immer DE für Datenspeicherung)
WEEKDAYS_DE_SHORT = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def translate_weekday_short(day_short):
    """
    Übersetzt ein DE-Wochentag-Kürzel (Mo/Di/Mi/...) in die aktuelle Sprache.
    Beispiel: 'Mi' → 'We' (en) / 'Me' (fr)
    """
    if day_short not in WEEKDAYS_DE_SHORT:
        return day_short
    shorts_translated = t("weekdays_short").split(",")
    return shorts_translated[WEEKDAYS_DE_SHORT.index(day_short)]


def get_today_day_short():
    """Gibt das DE-Kürzel des heutigen Wochentags zurück."""
    from datetime import date
    return WEEKDAYS_DE_SHORT[date.today().weekday()]



def get_day_label_map():
    """
    Gibt ein Dictionary {DE-Kürzel: übersetztes Kürzel} zurück.
    Beispiel: {"Mo": "Mon", "Di": "Tue", ...}
    """
    shorts_translated = t("weekdays_short").split(",")
    return dict(zip(WEEKDAYS_DE_SHORT, shorts_translated))