"""
views/medikamente.py
Medikamentenverwaltung: Übersicht, Hinzufügen, Bearbeiten, Löschen.
"""

import html
import streamlit as st
import pandas as pd
from datetime import datetime, time as dtime
from utils.translations import t
from utils.themes import get_theme

theme = get_theme()

def e(x): return html.escape(str(x))

DAYS = ["Mo","Di","Mi","Do","Fr","Sa","So"]

def format_days(days_str):
    if not days_str or pd.isna(days_str): return "—"
    days = [d.strip() for d in str(days_str).split(",")]
    if days == DAYS: return t("daily")
    if days == ["Mo","Di","Mi","Do","Fr"]: return t("mo_fr")
    return ", ".join(days)

def next_id(df):
    if df.empty or "id" not in df.columns: return 1
    return int(df["id"].max()) + 1

def save_medications():
    st.session_state["data_manager"].save_user_data(
        st.session_state["medications_df"], "medications.csv"
    )

# ── Seite ─────────────────────────────────────────────────────────────────────
st.markdown(f"## 💊 {t('med_title')}")
st.markdown('<p style="color:#6b7280">Verwalte deine Medikamente und Einnahmezeiten.</p>', unsafe_allow_html=True)
st.write("")

meds_df = st.session_state["medications_df"]

tab_list, tab_form = st.tabs([
    f"📋 {t('med_overview')}",
    f"➕ {t('med_add')}"
])

# ── Tab 1: Übersicht ──────────────────────────────────────────────────────────
with tab_list:
    if meds_df.empty:
        st.info(t("med_none"))
    else:
        sorted_meds = meds_df.sort_values("time")
        for _, med in sorted_meds.iterrows():
            note_text = str(med["note"]).strip() if pd.notna(med.get("note")) and str(med.get("note","")).strip() else "—"
            st.markdown(f"""
            <div style="background:{theme['card']};border:1px solid {theme['border']};
                        border-radius:14px;padding:1rem 1.1rem;margin-bottom:0.5rem">
                <div style="display:flex;align-items:center;gap:12px">
                    <div style="width:38px;height:38px;border-radius:10px;
                                background:{theme['pill_icon_bg']};
                                display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0">💊</div>
                    <div style="flex:1">
                        <div style="font-size:14px;font-weight:600;color:#111827">{e(str(med['name']))}</div>
                        <div style="font-size:12px;color:#6b7280;margin-top:1px">{e(format_days(med['days']))} · Bemerkung: {e(note_text)}</div>
                    </div>
                    <div style="font-size:11px;font-weight:600;background:{theme['metric_bg']};
                                color:#6b7280;padding:2px 8px;border-radius:7px;font-family:monospace;flex-shrink:0">
                        {e(str(med['time']))}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✏️ Bearbeiten", key=f"edit_{med['id']}", use_container_width=True):
                    st.session_state["editing_medication_id"] = int(med["id"])
                    st.rerun()
            with c2:
                if st.button("🗑️ Löschen", key=f"del_{med['id']}", use_container_width=True):
                    st.session_state["medications_df"] = meds_df[meds_df["id"] != med["id"]].reset_index(drop=True)
                    intakes = st.session_state["intakes_df"]
                    if not intakes.empty:
                        st.session_state["intakes_df"] = intakes[intakes["medication_id"] != med["id"]].reset_index(drop=True)
                        st.session_state["data_manager"].save_user_data(st.session_state["intakes_df"], "intakes.csv")
                    save_medications()
                    st.success(t("med_deleted"))
                    st.rerun()

# ── Tab 2: Formular ───────────────────────────────────────────────────────────
with tab_form:
    editing_id  = st.session_state.get("editing_medication_id")
    editing_row = None
    if editing_id is not None and not meds_df.empty:
        matches = meds_df[meds_df["id"] == editing_id]
        if not matches.empty:
            editing_row = matches.iloc[0]

    if editing_row is not None:
        st.markdown(f"**{t('edit_label')}:** {editing_row['name']}")
        if st.button("↩️ Abbrechen"):
            st.session_state["editing_medication_id"] = None
            st.rerun()

    default_name = str(editing_row["name"]) if editing_row is not None else ""
    default_time = (
        datetime.strptime(str(editing_row["time"]), "%H:%M").time()
        if editing_row is not None else dtime(8, 0)
    )
    default_days = (
        [d.strip() for d in str(editing_row["days"]).split(",")]
        if editing_row is not None and pd.notna(editing_row.get("days")) else []
    )
    default_note = str(editing_row["note"]) if editing_row is not None and pd.notna(editing_row.get("note")) else ""

    with st.form("medication_form", clear_on_submit=True):
        name     = st.text_input(f"{t('med_name')} *", value=default_name, placeholder="z.B. Aspirin 100mg")
        med_time = st.time_input(t("med_time"), value=default_time, step=1800)
        days     = st.multiselect(f"{t('med_days')} *", options=DAYS, default=default_days)
        note     = st.text_area(t("med_note"), value=default_note, placeholder="z.B. zum Essen einnehmen")

        submitted = st.form_submit_button(t("save"), use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Bitte gib einen Medikamentennamen ein.")
            elif not days:
                st.error("Bitte wähle mindestens einen Wochentag aus.")
            else:
                days_str = ",".join(days)
                time_str = med_time.strftime("%H:%M")

                if editing_row is not None:
                    idx = st.session_state["medications_df"].index[
                        st.session_state["medications_df"]["id"] == editing_id
                    ].tolist()
                    if idx:
                        st.session_state["medications_df"].at[idx[0], "name"]  = name.strip()
                        st.session_state["medications_df"].at[idx[0], "time"]  = time_str
                        st.session_state["medications_df"].at[idx[0], "days"]  = days_str
                        st.session_state["medications_df"].at[idx[0], "note"]  = note.strip()
                    intakes = st.session_state["intakes_df"]
                    if not intakes.empty:
                        mask = intakes["medication_id"] == editing_id
                        st.session_state["intakes_df"].loc[mask, "medication_name"] = name.strip()
                        st.session_state["data_manager"].save_user_data(st.session_state["intakes_df"], "intakes.csv")
                    st.session_state["editing_medication_id"] = None
                    st.success(f"✅ '{name.strip()}' wurde aktualisiert.")
                else:
                    new_row = pd.DataFrame([{
                        "id":         next_id(st.session_state["medications_df"]),
                        "name":       name.strip(),
                        "time":       time_str,
                        "days":       days_str,
                        "note":       note.strip(),
                        "created_at": pd.Timestamp.now(),
                    }])
                    st.session_state["medications_df"] = pd.concat(
                        [st.session_state["medications_df"], new_row], ignore_index=True
                    )
                    st.success(f"✅ '{name.strip()}' wurde gespeichert.")

                save_medications()
                st.rerun()