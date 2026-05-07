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
        initial_value=pd.DataFrame(
            columns=["date", "systolic", "diastolic"]
        ),
    )

if "blood_sugar_df" not in st.session_state:
    st.session_state["blood_sugar_df"] = data_manager.load_user_data(
        "blood_sugar.csv",
        initial_value=pd.DataFrame(
            columns=["date", "value"]
        ),
    )

# Fehlende DataFrames abfangen
for key, cols in [
    ("medications_df",    ["id", "name", "time", "days", "note", "created_at"]),
    ("intakes_df",        ["id", "medication_id", "medication_name", "date", "time", "confirmed", "note", "created_at"]),
    ("blood_pressure_df", ["date", "systolic", "diastolic"]),
    ("blood_sugar_df",    ["date", "value"]),
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
# Navigation
# ---------------------------------------------------------
pg_dashboard   = st.Page("views/dashboard.py",    title="Dashboard",   icon="🏠", default=True)
pg_medikamente = st.Page("views/medikamente.py",  title="Medikamente", icon="💊")
pg_verlauf     = st.Page("views/verlauf.py",       title="Verlauf",     icon="📋")
pg_blutdruck   = st.Page("views/blutdruck.py",    title="Blutdruck",   icon="❤️")
pg_blutzucker  = st.Page("views/blutzucker.py",   title="Blutzucker",  icon="🩸")

pg = st.navigation([pg_dashboard, pg_medikamente, pg_verlauf, pg_blutdruck, pg_blutzucker])
pg.run()