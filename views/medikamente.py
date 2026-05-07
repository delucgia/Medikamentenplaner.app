"""
views/medikamente.py
Medikamentenverwaltung: Übersicht, Hinzufügen, Bearbeiten, Löschen.
Arbeitet mit st.session_state["medications_df"].
"""

import html
import streamlit as st
import pandas as pd
from datetime import datetime, time as dtime

# ── Styling ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.pill-card { background:#fafafa; border:1px solid #e5e7eb; border-radius:14px; padding:1rem 1.1rem; margin-bottom:0.75rem; }
.time-badge { float:right; background:#f3f4f6; color:#374151; padding:0.18rem 0.55rem; border-radius:8px; font-size:0.78rem; font-weight:600; }
.muted { color:#6b7280; font-size:0.9rem; }
div.stButton > button { border-radius:12px; font-weight:600; min-height:40px; }
</style>""", unsafe_allow_html=True)

# ── Konstanten ───────────────────────────────────────────────────────────────────
DAYS = ["Mo","Di","Mi","Do","Fr","Sa","So"]

def e(t): return html.escape(str(t))

def format_days(days_str):
    if not days_str or pd.isna(days_str):
        return "—"
    days = [d.strip() for d in str(days_str).split(",")]
    if days == DAYS:
        return "Täglich"
    if days == ["Mo","Di","Mi","Do","Fr"]:
        return "Mo–Fr"
    return ", ".join(days)

def next_id(df):
    if df.empty or "id" not in df.columns:
        return 1
    return int(df["id"].max()) + 1

def save_medications():
    """Speichert den aktuellen medications_df in die Cloud."""
    dm = st.session_state["data_manager"]
    dm.save_user_data(st.session_state["medications_df"], "medications.csv")

# ── Seiteninhalt ─────────────────────────────────────────────────────────────────
st.markdown("## 💊 Medikamente")
st.markdown('<p style="color:#6b7280">Verwalte deine Medikamente und Einnahmezeiten.</p>', unsafe_allow_html=True)
st.write("")

meds_df = st.session_state["medications_df"]
tab_list, tab_form = st.tabs(["📋 Übersicht", "➕ Hinzufügen / Bearbeiten"])

# ── Tab 1: Übersicht ─────────────────────────────────────────────────────────────
with tab_list:
    if meds_df.empty:
        st.info("Noch keine Medikamente vorhanden. Füge dein erstes Medikament im Tab rechts hinzu.")
    else:
        sorted_meds = meds_df.sort_values("time")
        for _, med in sorted_meds.iterrows():
            note_text = med["note"] if pd.notna(med.get("note")) and str(med.get("note","")).strip() else "—"
            st.markdown(f"""
            <div class="pill-card">
                <strong>{e(med['name'])}</strong>
                <span class="time-badge">{e(med['time'])}</span><br>
                <span class="muted">Tage: {e(format_days(med['days']))}</span><br>
                <span class="muted">Bemerkung: {e(note_text)}</span>
            </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✏️ Bearbeiten", key=f"edit_{med['id']}", use_container_width=True):
                    st.session_state["editing_medication_id"] = int(med["id"])
                    st.rerun()
            with c2:
                if st.button("🗑️ Löschen", key=f"del_{med['id']}", use_container_width=True):
                    # Medikament löschen
                    st.session_state["medications_df"] = meds_df[meds_df["id"] != med["id"]].reset_index(drop=True)
                    # Zugehörige Einnahmen löschen
                    intakes = st.session_state["intakes_df"]
                    if not intakes.empty:
                        st.session_state["intakes_df"] = intakes[intakes["medication_id"] != med["id"]].reset_index(drop=True)
                        st.session_state["data_manager"].save_user_data(st.session_state["intakes_df"], "intakes.csv")
                    save_medications()
                    st.success(f"'{med['name']}' wurde gelöscht.")
                    st.rerun()

# ── Tab 2: Formular ───────────────────────────────────────────────────────────────
with tab_form:
    editing_id = st.session_state.get("editing_medication_id")
    editing_row = None
    if editing_id is not None and not meds_df.empty:
        matches = meds_df[meds_df["id"] == editing_id]
        if not matches.empty:
            editing_row = matches.iloc[0]

    if editing_row is not None:
        st.markdown(f"**Bearbeite:** {editing_row['name']}")
        if st.button("↩️ Abbrechen"):
            st.session_state["editing_medication_id"] = None
            st.rerun()

    # Standardwerte
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
        name     = st.text_input("Medikamentenname *", value=default_name, placeholder="z.B. Aspirin 100mg")
        med_time = st.time_input("Einnahmezeit", value=default_time, step=1800)
        days     = st.multiselect("Wochentage *", options=DAYS, default=default_days)
        note     = st.text_area("Bemerkung (optional)", value=default_note, placeholder="z.B. zum Essen einnehmen")

        submitted = st.form_submit_button("💾 Speichern", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Bitte gib einen Medikamentennamen ein.")
            elif not days:
                st.error("Bitte wähle mindestens einen Wochentag aus.")
            else:
                days_str = ",".join(days)
                time_str = med_time.strftime("%H:%M")

                if editing_row is not None:
                    # Update
                    idx = st.session_state["medications_df"].index[
                        st.session_state["medications_df"]["id"] == editing_id
                    ].tolist()
                    if idx:
                        st.session_state["medications_df"].at[idx[0], "name"]  = name.strip()
                        st.session_state["medications_df"].at[idx[0], "time"]  = time_str
                        st.session_state["medications_df"].at[idx[0], "days"]  = days_str
                        st.session_state["medications_df"].at[idx[0], "note"]  = note.strip()
                    # Medikamentenname in Einnahmen synchronisieren
                    intakes = st.session_state["intakes_df"]
                    if not intakes.empty:
                        mask = intakes["medication_id"] == editing_id
                        st.session_state["intakes_df"].loc[mask, "medication_name"] = name.strip()
                        st.session_state["data_manager"].save_user_data(st.session_state["intakes_df"], "intakes.csv")
                    st.session_state["editing_medication_id"] = None
                    st.success(f"✅ '{name.strip()}' wurde aktualisiert.")
                else:
                    # Neu anlegen
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