import pandas as pd
import streamlit as st

from utils.data_manager import DataManager
from utils.login_manager import LoginManager

# ---------------------------------------------------------
# Seiten-Konfiguration
# ---------------------------------------------------------
st.set_page_config(page_title="MediTrack", page_icon="💊")

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
# MediTrack-Daten pro User laden
# ---------------------------------------------------------
if "medications_df" not in st.session_state:
    st.session_state["medications_df"] = data_manager.load_user_data(
        "medications.csv",
        initial_value=pd.DataFrame(
            columns=["id", "name", "time", "days", "note", "created_at"]
        ),
        parse_dates=["created_at"]
    )

if "intakes_df" not in st.session_state:
    st.session_state["intakes_df"] = data_manager.load_user_data(
        "intakes.csv",
        initial_value=pd.DataFrame(
            columns=[
                "id",
                "medication_id",
                "medication_name",
                "date",
                "time",
                "confirmed",
                "note",
                "created_at",
            ]
        ),
        parse_dates=["created_at"]
    )

# Falls nichts geladen wurde
if st.session_state["medications_df"] is None:
    st.session_state["medications_df"] = pd.DataFrame(
        columns=["id", "name", "time", "days", "note", "created_at"]
    )

if st.session_state["intakes_df"] is None:
    st.session_state["intakes_df"] = pd.DataFrame(
        columns=[
            "id",
            "medication_id",
            "medication_name",
            "date",
            "time",
            "confirmed",
            "note",
            "created_at",
        ]
    )

# Zusätzliche UI-States
if "last_success_message" not in st.session_state:
    st.session_state["last_success_message"] = "Super!"

if "editing_medication_id" not in st.session_state:
    st.session_state["editing_medication_id"] = None

if "editing_intake_id" not in st.session_state:
    st.session_state["editing_intake_id"] = None

# Optional: DataManager global verfügbar machen
st.session_state["data_manager"] = data_manager

# ---------------------------------------------------------
# Navigation
# ---------------------------------------------------------
pg_main = st.Page(
    "views/MediTrack.py",
    title="MediTrack",
    icon="💊",
    default=True
)

pg = st.navigation([pg_main])
pg.run()
