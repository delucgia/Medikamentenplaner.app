"""
views/achievements.py
Abzeichen-System: Freigeschaltete und gesperrte Achievements.
Vollständig übersetzt via utils/translations.py
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.translations import t
from utils.themes import inject_theme, get_theme
from utils.vita import mascot_svg

inject_theme()
theme = get_theme()


def is_confirmed(val):
    return str(val).strip().lower() in ["true", "1", "yes"]


def check_achievements(intakes_df, bp_df, bs_df, mood_df, meds_df, streak):
    """
    Prüft welche Achievements freigeschaltet sind.
    Gibt ein Dict {key: bool} zurück.
    """
    results = {}

    # Erster Schritt – erste bestätigte Einnahme
    results["first_intake"] = (
        not intakes_df.empty and
        intakes_df["confirmed"].apply(is_confirmed).any()
    )

    # On Fire – 7 Tage Streak
    results["streak_7"] = streak >= 7

    # Eiserner Wille – 30 Tage Streak
    results["streak_30"] = streak >= 30

    # Legende – 100 Tage Streak
    results["streak_100"] = streak >= 100

    # Grüne Zone – Blutdruck 7x optimal/normal
    if not bp_df.empty:
        bp_copy = bp_df.copy()
        bp_copy["systolic"]  = pd.to_numeric(bp_copy["systolic"],  errors="coerce")
        bp_copy["diastolic"] = pd.to_numeric(bp_copy["diastolic"], errors="coerce")
        good_bp = bp_copy[
            (bp_copy["systolic"]  < 130) &
            (bp_copy["diastolic"] < 85)
        ]
        results["bp_green"] = len(good_bp) >= 7
    else:
        results["bp_green"] = False

    # Blutzucker im Griff – 5x normaler Nüchternwert
    if not bs_df.empty:
        bs_copy = bs_df.copy()
        bs_copy["value"] = pd.to_numeric(bs_copy["value"], errors="coerce")
        good_bs = bs_copy[
            (bs_copy["value"] >= 3.9) &
            (bs_copy["value"] <= 5.5)
        ]
        results["bs_normal"] = len(good_bs) >= 5
    else:
        results["bs_normal"] = False

    # Daten-Fan – 20 Gesundheitswerte erfasst
    total_values = len(bp_df) + len(bs_df)
    results["data_fan"] = total_values >= 20

    # Ausgeglichen – 7x Stimmung "Sehr gut"
    if not mood_df.empty:
        great_moods = mood_df[mood_df["mood_key"] == "great"]
        results["mood_great"] = len(great_moods) >= 7
    else:
        results["mood_great"] = False

    # Arztprofi – PDF mindestens einmal erstellt (wir tracken es im Session State)
    results["pdf_export"] = st.session_state.get("pdf_exported_once", False)

    # Treuer Begleiter – 50 Einnahmen bestätigt
    if not intakes_df.empty:
        confirmed_count = intakes_df["confirmed"].apply(is_confirmed).sum()
        results["confirmed_50"] = confirmed_count >= 50
    else:
        results["confirmed_50"] = False

    # Vollständig – Profil komplett ausgefüllt
    profile = st.session_state.get("profile", {})
    required_fields = ["firstname", "lastname", "birthdate", "doctor", "emergency"]
    results["profile_complete"] = all(profile.get(f, "").strip() for f in required_fields)

    return results


# ── Daten ─────────────────────────────────────────────────────────────────────
intakes_df = st.session_state.get("intakes_df", pd.DataFrame())
bp_df      = st.session_state.get("blood_pressure_df", pd.DataFrame())
bs_df      = st.session_state.get("blood_sugar_df", pd.DataFrame())
mood_df    = st.session_state.get("mood_df", pd.DataFrame())
meds_df    = st.session_state.get("medications_df", pd.DataFrame())

# Streak berechnen
streak = 0
if not intakes_df.empty and not meds_df.empty:
    shorts_de = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    check_date = date.today()
    for _ in range(365):
        day_name = shorts_de[check_date.weekday()]
        due = meds_df[meds_df["days"].apply(
            lambda d: day_name in [x.strip() for x in str(d).split(",")]
            if pd.notna(d) else False
        )]
        if due.empty:
            check_date -= timedelta(days=1)
            continue
        day_i = intakes_df[intakes_df["date"].astype(str) == check_date.isoformat()]
        if all(
            not day_i[(day_i["medication_id"] == mid) &
                      (day_i["confirmed"].apply(is_confirmed))].empty
            for mid in due["id"]
        ):
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

achieved = check_achievements(intakes_df, bp_df, bs_df, mood_df, meds_df, streak)

# Alle Achievements definieren
ACHIEVEMENTS = [
    {
        "key":   "first_intake",
        "icon":  "🌱",
        "name":  {"de":"Erster Schritt",  "fr":"Premier pas",      "it":"Primo passo",     "en":"First step"},
        "desc":  {"de":"Erste Einnahme bestätigt", "fr":"Première prise confirmée", "it":"Prima assunzione confermata", "en":"First intake confirmed"},
    },
    {
        "key":   "streak_7",
        "icon":  "🔥",
        "name":  {"de":"On Fire",         "fr":"En feu",           "it":"On Fire",          "en":"On Fire"},
        "desc":  {"de":"7 Tage Streak",   "fr":"7 jours de suite", "it":"7 giorni di fila", "en":"7-day streak"},
    },
    {
        "key":   "streak_30",
        "icon":  "💪",
        "name":  {"de":"Eiserner Wille",  "fr":"Volonté de fer",   "it":"Volontà di ferro", "en":"Iron will"},
        "desc":  {"de":"30 Tage Streak",  "fr":"30 jours de suite","it":"30 giorni di fila","en":"30-day streak"},
    },
    {
        "key":   "streak_100",
        "icon":  "👑",
        "name":  {"de":"Legende",         "fr":"Légende",          "it":"Leggenda",         "en":"Legend"},
        "desc":  {"de":"100 Tage Streak", "fr":"100 jours de suite","it":"100 giorni di fila","en":"100-day streak"},
    },
    {
        "key":   "bp_green",
        "icon":  "💚",
        "name":  {"de":"Grüne Zone",      "fr":"Zone verte",       "it":"Zona verde",       "en":"Green zone"},
        "desc":  {"de":"Blutdruck 7× optimal", "fr":"Tension 7× optimale", "it":"Pressione 7× ottimale", "en":"Blood pressure 7× optimal"},
    },
    {
        "key":   "bs_normal",
        "icon":  "🩸",
        "name":  {"de":"Zuckerfrei",      "fr":"Sans sucre",       "it":"Senza zucchero",   "en":"Sugar control"},
        "desc":  {"de":"Blutzucker 5× normal", "fr":"Glycémie 5× normale", "it":"Glicemia 5× normale", "en":"Blood sugar 5× normal"},
    },
    {
        "key":   "data_fan",
        "icon":  "📊",
        "name":  {"de":"Daten-Fan",       "fr":"Fan de données",   "it":"Fan dei dati",     "en":"Data fan"},
        "desc":  {"de":"20 Werte erfasst","fr":"20 valeurs saisies","it":"20 valori registrati","en":"20 values recorded"},
    },
    {
        "key":   "mood_great",
        "icon":  "🧘",
        "name":  {"de":"Ausgeglichen",    "fr":"Équilibré",        "it":"Equilibrato",      "en":"Balanced"},
        "desc":  {"de":"7× Stimmung sehr gut","fr":"7× humeur très bonne","it":"7× umore molto buono","en":"7× mood very good"},
    },
    {
        "key":   "pdf_export",
        "icon":  "📄",
        "name":  {"de":"Arztprofi",       "fr":"Pro médecin",      "it":"Pro medico",       "en":"Doctor pro"},
        "desc":  {"de":"Ersten PDF exportiert","fr":"Premier PDF exporté","it":"Primo PDF esportato","en":"First PDF exported"},
    },
    {
        "key":   "confirmed_50",
        "icon":  "🏅",
        "name":  {"de":"Treuer Begleiter","fr":"Compagnon fidèle", "it":"Compagno fedele",  "en":"Loyal companion"},
        "desc":  {"de":"50 Einnahmen bestätigt","fr":"50 prises confirmées","it":"50 assunzioni confermate","en":"50 intakes confirmed"},
    },
    {
        "key":   "profile_complete",
        "icon":  "✨",
        "name":  {"de":"Vollständig",     "fr":"Complet",          "it":"Completo",         "en":"Complete"},
        "desc":  {"de":"Profil vollständig ausgefüllt","fr":"Profil entièrement rempli","it":"Profilo completamente compilato","en":"Profile fully completed"},
    },
]

lang = st.session_state.get("language", "de")

unlocked = [a for a in ACHIEVEMENTS if achieved.get(a["key"], False)]
locked    = [a for a in ACHIEVEMENTS if not achieved.get(a["key"], False)]

# ── Seite ─────────────────────────────────────────────────────────────────────
st.markdown(f"## 🏆 {t('nav_achievements')}")

# Vita mit Nachricht
vita_col, text_col = st.columns([1, 3])
with vita_col:
    if len(unlocked) >= len(ACHIEVEMENTS):
        st.markdown(mascot_svg("excited", size=80), unsafe_allow_html=True)
    elif len(unlocked) > 0:
        st.markdown(mascot_svg("happy", size=80), unsafe_allow_html=True)
    else:
        st.markdown(mascot_svg("happy", size=80), unsafe_allow_html=True)

with text_col:
    total  = len(ACHIEVEMENTS)
    done   = len(unlocked)
    pct    = int(done / total * 100)
    bar_color = "#22c55e" if pct >= 80 else ("#f59e0b" if pct >= 40 else "#f472b6")
    st.markdown(
        f'<div style="font-size:14px;font-weight:500;color:#111827;margin-bottom:6px">'
        f'{done} / {total} {t("nav_achievements")}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="height:8px;background:{theme["border"]};border-radius:99px;overflow:hidden;margin-bottom:10px">'
        f'<div style="height:100%;width:{pct}%;background:{bar_color};border-radius:99px"></div></div>',
        unsafe_allow_html=True
    )
    if done == total:
        st.markdown(
            f'<p style="color:#15803d;font-size:13px">{t("vita_achievement")}</p>',
            unsafe_allow_html=True
        )
    elif done == 0:
        st.markdown(
            f'<p style="color:#6b7280;font-size:13px">{t("vita_morning")}</p>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<p style="color:#6b7280;font-size:13px">{t("vita_streak_small").format(streak=streak) if streak > 0 else t("vita_noon")}</p>',
            unsafe_allow_html=True
        )

st.divider()

# ── Freigeschaltet ────────────────────────────────────────────────────────────
if unlocked:
    st.markdown(f"#### ✅ Freigeschaltet ({len(unlocked)})")
    cols = st.columns(3)
    for i, a in enumerate(unlocked):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:{theme['card']};border:1.5px solid #22c55e;
                        border-radius:14px;padding:1rem;text-align:center;margin-bottom:0.75rem">
                <div style="font-size:2.2rem;margin-bottom:6px">{a['icon']}</div>
                <div style="font-size:13px;font-weight:600;color:#111827;margin-bottom:2px">
                    {a['name'].get(lang, a['name']['de'])}
                </div>
                <div style="font-size:11px;color:#6b7280">
                    {a['desc'].get(lang, a['desc']['de'])}
                </div>
                <div style="margin-top:6px;font-size:11px;font-weight:600;color:#15803d">✓</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ── Noch gesperrt ─────────────────────────────────────────────────────────────
if locked:
    st.markdown(f"#### 🔒 Noch nicht freigeschaltet ({len(locked)})")
    cols = st.columns(3)
    for i, a in enumerate(locked):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:{theme['metric_bg']};border:0.5px solid {theme['border']};
                        border-radius:14px;padding:1rem;text-align:center;
                        margin-bottom:0.75rem;opacity:0.55;filter:grayscale(0.6)">
                <div style="font-size:2.2rem;margin-bottom:6px">{a['icon']}</div>
                <div style="font-size:13px;font-weight:600;color:#111827;margin-bottom:2px">
                    {a['name'].get(lang, a['name']['de'])}
                </div>
                <div style="font-size:11px;color:#6b7280">
                    {a['desc'].get(lang, a['desc']['de'])}
                </div>
                <div style="margin-top:6px;font-size:11px;color:#9ca3af">🔒</div>
            </div>
            """, unsafe_allow_html=True)