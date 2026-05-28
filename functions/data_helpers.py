"""
functions/data_helpers.py
Funktionen zum Speichern von Daten und prüfen von Einnahmen.
"""

import streamlit as st
import pandas as pd
from utils.translations import t
from datetime import date, timedelta
from functions.format_helpers import is_confirmed


def save_medications():
    """Speichert medications_df auf SwitchDrive."""
    st.session_state["data_manager"].save_user_data(
        st.session_state["medications_df"], "medications.csv"
    )


def save_intakes():
    """Speichert intakes_df auf SwitchDrive."""
    st.session_state["data_manager"].save_user_data(
        st.session_state["intakes_df"], "intakes.csv"
    )


def save_bp():
    """Speichert blood_pressure_df auf SwitchDrive."""
    st.session_state["data_manager"].save_user_data(
        st.session_state["blood_pressure_df"], "blood_pressure.csv"
    )


def save_bs():
    """Speichert blood_sugar_df auf SwitchDrive."""
    st.session_state["data_manager"].save_user_data(
        st.session_state["blood_sugar_df"], "blood_sugar.csv"
    )


def save_mood():
    """Speichert mood_df auf SwitchDrive."""
    st.session_state["data_manager"].save_user_data(
        st.session_state["mood_df"], "mood.csv"
    )


def med_due_today(days_str):
    """Prüft ob ein Medikament heute fällig ist (basierend auf days-String)."""
    if not days_str or pd.isna(days_str):
        return False
    shorts_de = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    today_short = shorts_de[date.today().weekday()]
    days = [d.strip() for d in str(days_str).split(",")]
    return today_short in days


def intake_exists_today(medication_id):
    """Prüft ob eine bestätigte Einnahme für ein Medikament heute existiert."""
    intakes = st.session_state.get("intakes_df", pd.DataFrame())
    if intakes.empty:
        return False
    today_str = date.today().isoformat()
    today_intakes = intakes[
        (intakes["medication_id"] == medication_id) &
        (intakes["date"].astype(str) == today_str)
    ]
    if today_intakes.empty:
        return False
    return today_intakes["confirmed"].apply(is_confirmed).any()


def compute_streak():
    """
    Berechnet die Streak: wie viele Tage in Folge wurden alle fälligen
    Medikamente bestätigt? Rückwärts ab heute, Tage ohne fällige Medikamente
    werden übersprungen.
    """
    meds_df    = st.session_state.get("medications_df", pd.DataFrame())
    intakes_df = st.session_state.get("intakes_df",     pd.DataFrame())

    if meds_df.empty or intakes_df.empty:
        return 0

    shorts_de = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    streak = 0
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
        all_confirmed = all(
            not day_i[
                (day_i["medication_id"] == mid) &
                (day_i["confirmed"].apply(is_confirmed))
            ].empty
            for mid in due["id"]
        )
        if all_confirmed:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak


def compute_trend(df, value_col, days=7):
    """
    Berechnet einen einfachen Trend für eine Wertespalte über die letzten X Tage.
    Gibt zurück: 'up', 'down', 'stable' oder None
    """
    if df.empty or len(df) < 4:
        return None

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"], errors="coerce")
    df_copy[value_col] = pd.to_numeric(df_copy[value_col], errors="coerce")
    df_copy = df_copy.dropna(subset=["date", value_col]).sort_values("date").tail(days)

    if len(df_copy) < 4:
        return None

    half = len(df_copy) // 2
    avg_first  = df_copy[value_col].iloc[:half].mean()
    avg_second = df_copy[value_col].iloc[half:].mean()
    std        = df_copy[value_col].std()

    if std == 0 or pd.isna(std):
        return "stable"

    diff = avg_second - avg_first
    threshold = std * 0.3

    if abs(diff) < threshold:
        return "stable"
    return "up" if diff > 0 else "down"



def save_intake(medication_id, med_name, intake_date, intake_time, confirmed=True, note=""):
    """
    Speichert eine einzelne Einnahme. Fügt sie zum intakes_df hinzu wenn sie
    noch nicht existiert, sonst aktualisiert sie den bestehenden Eintrag.
    """
    import streamlit as st
    from functions.format_helpers import next_id

    intakes = st.session_state.get("intakes_df", pd.DataFrame())
    date_str = intake_date.isoformat() if hasattr(intake_date, "isoformat") else str(intake_date)
    time_str = intake_time.strftime("%H:%M") if hasattr(intake_time, "strftime") else str(intake_time)

    # Prüfen ob bereits ein Eintrag heute existiert
    if not intakes.empty:
        mask = (
            (intakes["medication_id"] == medication_id) &
            (intakes["date"].astype(str) == date_str)
        )
        if mask.any():
            idx = intakes[mask].index[0]
            intakes.at[idx, "time"]      = time_str
            intakes.at[idx, "confirmed"] = confirmed
            intakes.at[idx, "note"]      = note
            st.session_state["intakes_df"] = intakes
            save_intakes()
            return

    new_row = pd.DataFrame([{
        "id":              next_id(intakes),
        "medication_id":   medication_id,
        "medication_name": med_name,
        "date":            date_str,
        "time":            time_str,
        "confirmed":       confirmed,
        "note":            note,
        "created_at":      pd.Timestamp.now(),
    }])
    st.session_state["intakes_df"] = pd.concat([intakes, new_row], ignore_index=True)
    save_intakes()



def add_or_replace_entry(df, date_str, new_entry_dict):
    """
    Fügt einen neuen Eintrag zu einem Gesundheits-DataFrame hinzu oder ersetzt
    den bestehenden Eintrag am gleichen Datum.
    Wird für Blutdruck, Blutzucker, Stimmung verwendet.
    """
    if not df.empty and date_str in df["date"].astype(str).values:
        df = df[df["date"].astype(str) != date_str]
    new_row = pd.DataFrame([new_entry_dict])
    df = pd.concat([df, new_row], ignore_index=True)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def get_profile_name(profile):
    """Gibt den vollen Namen aus dem Profil zurück (firstname + lastname)."""
    firstname = profile.get("firstname", "") if profile else ""
    lastname  = profile.get("lastname", "")  if profile else ""
    return f"{firstname} {lastname}".strip()


def get_profile_initials(profile):
    """Gibt die Initialen aus dem Profil zurück (z.B. 'MB' für Maria Bianchi)."""
    firstname = profile.get("firstname", "") if profile else ""
    lastname  = profile.get("lastname", "")  if profile else ""
    return f"{firstname[:1]}{lastname[:1]}".upper() if (firstname or lastname) else "?"



def load_all_health_data():
    """
    Lädt alle Gesundheits-DataFrames aus dem Session State.
    Gibt (intakes_df, bp_df, bs_df, mood_df, meds_df, profile) zurück.
    """
    import streamlit as st
    return (
        st.session_state.get("intakes_df",        pd.DataFrame()),
        st.session_state.get("blood_pressure_df", pd.DataFrame()),
        st.session_state.get("blood_sugar_df",    pd.DataFrame()),
        st.session_state.get("mood_df",           pd.DataFrame()),
        st.session_state.get("medications_df",    pd.DataFrame()),
        st.session_state.get("profile",           {}),
    )


def show_health_disclaimer_if_needed():
    """
    Zeigt einen Disclaimer wenn die Sprache nicht Deutsch ist.
    (Medizinische Erklärtexte sind nur auf Deutsch verfügbar.)
    Gibt True zurück wenn ein Disclaimer angezeigt wurde.
    """
    import streamlit as st
    lang = st.session_state.get("language", "de")
    if lang != "de":
        st.info(t("health_notes_disclaimer"))
        return True
    return False