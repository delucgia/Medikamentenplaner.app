import pandas as pd
import streamlit as st
from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# ---------------------------------------------------------
# Seiten-Konfiguration
# ---------------------------------------------------------
st.set_page_config(page_title="MediTrack", page_icon="💊", layout="wide")

# ---------------------------------------------------------
# Data Manager + Login
# ---------------------------------------------------------
data_manager = DataManager(
    fs_protocol="webdav",
    fs_root_folder="MediTrack"
)
login_manager = LoginManager(data_manager)
login_manager.login_register()

# ---------------------------------------------------------
# Einstellungen laden (Sprache, Theme)
# ---------------------------------------------------------
if "settings_loaded" not in st.session_state:
    try:
        saved = data_manager.load_user_data("settings.json", initial_value={}) or {}
        if saved.get("language"):
            st.session_state["language"] = saved["language"]
        if saved.get("theme"):
            st.session_state["theme"] = saved["theme"]
    except Exception:
        pass
    st.session_state["settings_loaded"] = True

if "language" not in st.session_state:
    st.session_state["language"] = "de"
if "theme" not in st.session_state:
    st.session_state["theme"] = "blue"

# ---------------------------------------------------------
# Profil laden
# ---------------------------------------------------------
if "profile" not in st.session_state:
    try:
        st.session_state["profile"] = data_manager.load_user_data(
            "profile.json", initial_value={}
        ) or {}
    except Exception:
        st.session_state["profile"] = {}

# ---------------------------------------------------------
# MediTrack-Daten pro User laden (CSV → DataFrame)
# ---------------------------------------------------------
if "medications_df" not in st.session_state:
    st.session_state["medications_df"] = data_manager.load_user_data(
        "medications.csv",
        initial_value=pd.DataFrame(
            columns=["id", "name", "time", "days", "note", "created_at"]
        ),
        parse_dates=["created_at"],
    )

if "intakes_df" not in st.session_state:
    st.session_state["intakes_df"] = data_manager.load_user_data(
        "intakes.csv",
        initial_value=pd.DataFrame(
            columns=["id", "medication_id", "medication_name",
                     "date", "time", "confirmed", "note", "created_at"]
        ),
        parse_dates=["created_at"],
    )

if "blood_pressure_df" not in st.session_state:
    st.session_state["blood_pressure_df"] = data_manager.load_user_data(
        "blood_pressure.csv",
        initial_value=pd.DataFrame(columns=["date", "systolic", "diastolic"]),
    )

if "blood_sugar_df" not in st.session_state:
    st.session_state["blood_sugar_df"] = data_manager.load_user_data(
        "blood_sugar.csv",
        initial_value=pd.DataFrame(columns=["date", "value"]),
    )

# mood_df immer frisch laden (nicht cachen) damit neue Einträge nach Neustart sichtbar sind
try:
    loaded_mood = data_manager.load_user_data(
        "mood.csv",
        initial_value=pd.DataFrame(
            columns=["date", "mood_key", "mood_value", "mood_label", "note"]
        ),
    )
    st.session_state["mood_df"] = loaded_mood if loaded_mood is not None else pd.DataFrame(
        columns=["date", "mood_key", "mood_value", "mood_label", "note"]
    )
except Exception as ex:
    if "mood_df" not in st.session_state:
        st.session_state["mood_df"] = pd.DataFrame(
            columns=["date", "mood_key", "mood_value", "mood_label", "note"]
        )

# Fehlende DataFrames abfangen
for key, cols in [
    ("medications_df",    ["id", "name", "time", "days", "note", "created_at"]),
    ("intakes_df",        ["id", "medication_id", "medication_name", "date", "time", "confirmed", "note", "created_at"]),
    ("blood_pressure_df", ["date", "systolic", "diastolic"]),
    ("blood_sugar_df",    ["date", "value"]),
    ("mood_df",           ["date", "mood_key", "mood_value", "mood_label", "note"]),
]:
    if st.session_state[key] is None:
        st.session_state[key] = pd.DataFrame(columns=cols)

# ---------------------------------------------------------
# Zusätzliche UI-States
# ---------------------------------------------------------
if "last_success_message" not in st.session_state:
    st.session_state["last_success_message"] = ""
if "editing_medication_id" not in st.session_state:
    st.session_state["editing_medication_id"] = None
if "editing_intake_id" not in st.session_state:
    st.session_state["editing_intake_id"] = None

# DataManager global verfügbar machen
st.session_state["data_manager"] = data_manager

# ---------------------------------------------------------
# Theme + Übersetzung global laden — VOR pg.run()
# damit Sidebar-Farbe auf allen Seiten gilt
# ---------------------------------------------------------
from utils.themes import inject_theme
from utils.translations import t
inject_theme()

# ---------------------------------------------------------
# Navigation
# ---------------------------------------------------------
pg_dashboard   = st.Page("views/dashboard.py",    title=t("nav_dashboard"),      icon="🏠", default=True)
pg_medikamente = st.Page("views/medikamente.py",  title=t("nav_medications"),    icon="💊")
pg_verlauf     = st.Page("views/verlauf.py",       title=t("nav_history"),        icon="📋")
pg_blutdruck   = st.Page("views/blutdruck.py",    title=t("nav_blood_pressure"), icon="❤️")
pg_blutzucker  = st.Page("views/blutzucker.py",   title=t("nav_blood_sugar"),    icon="🩸")
pg_stimmung    = st.Page("views/stimmung.py",     title=t("nav_mood"),           icon="😊")
pg_profil      = st.Page("views/profil.py",       title=t("nav_profile"),        icon="👤")
pg_settings    = st.Page("views/einstellungen.py",title=t("nav_settings"),       icon="⚙️")
pg_pdf         = st.Page("views/pdf_export.py",    title="PDF-Export",            icon="📄")

pg = st.navigation([
    pg_dashboard,
    pg_medikamente,
    pg_verlauf,
    pg_blutdruck,
    pg_blutzucker,
    pg_stimmung,
    pg_profil,
    pg_settings,
    pg_pdf,
])
pg.run()