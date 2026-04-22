import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime, time

st.set_page_config(page_title="MediTrack", page_icon="💊", layout="wide")

# =========================================================
# Dateien
# =========================================================
MEDICATIONS_FILE = "medications.json"
INTAKES_FILE = "intakes.json"
BLOOD_PRESSURE_FILE = "blood_pressure.json"
BLOOD_SUGAR_FILE = "blood_sugar.json"

DAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
DAY_MAP = {
    0: "Mo",
    1: "Di",
    2: "Mi",
    3: "Do",
    4: "Fr",
    5: "Sa",
    6: "So",
}

# =========================================================
# Daten laden / speichern
# =========================================================
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================================================
# Session State
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "medications" not in st.session_state:
    st.session_state.medications = load_data(MEDICATIONS_FILE)

if "intakes" not in st.session_state:
    st.session_state.intakes = load_data(INTAKES_FILE)

if "blood_pressure_entries" not in st.session_state:
    st.session_state.blood_pressure_entries = load_data(BLOOD_PRESSURE_FILE)

if "blood_sugar_entries" not in st.session_state:
    st.session_state.blood_sugar_entries = load_data(BLOOD_SUGAR_FILE)

if "editing_medication_id" not in st.session_state:
    st.session_state.editing_medication_id = None

if "editing_intake_id" not in st.session_state:
    st.session_state.editing_intake_id = None

if "last_success_message" not in st.session_state:
    st.session_state.last_success_message = "Super!"


# =========================================================
# Styling
# =========================================================
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f7fb;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .app-card {
        background: white;
        padding: 1.25rem;
        border-radius: 22px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        border: 1px solid #ececf2;
        margin-bottom: 1rem;
    }
    .title-main {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .muted {
        color: #6b7280;
        font-size: 0.95rem;
    }
    .pill-card {
        background: #fafafa;
        border: 1px solid #ececf2;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    .time-badge {
        float: right;
        background: #f3f4f6;
        color: #111827;
        padding: 0.2rem 0.55rem;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .ok-badge {
        display: inline-block;
        padding: 0.22rem 0.55rem;
        border-radius: 999px;
        background: #e8f8ec;
        color: #15803d;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .no-badge {
        display: inline-block;
        padding: 0.22rem 0.55rem;
        border-radius: 999px;
        background: #fef2f2;
        color: #b91c1c;
        font-size: 0.8rem;
        font-weight: 600;
    }
    div.stButton > button {
        border-radius: 14px;
        font-weight: 600;
        min-height: 42px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Helper
# =========================================================
def go_to(page_name: str):
    st.session_state.page = page_name
    st.rerun()


def next_id(items):
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def format_days(days):
    if days == DAYS:
        return "Täglich"
    if days == ["Mo", "Di", "Mi", "Do", "Fr"]:
        return "Mo–Fr"
    return ", ".join(days)


def get_medication_by_id(med_id):
    for med in st.session_state.medications:
        if med["id"] == med_id:
            return med
    return None


def get_intake_by_id(intake_id):
    for intake in st.session_state.intakes:
        if intake["id"] == intake_id:
            return intake
    return None


def get_today_day_name():
    return DAY_MAP[datetime.today().weekday()]


def medication_is_due_today(med):
    return get_today_day_name() in med["days"]


# =========================================================
# CRUD Medikamente
# =========================================================
def create_medication(name, med_time, days, note):
    st.session_state.medications.append(
        {
            "id": next_id(st.session_state.medications),
            "name": name.strip(),
            "time": med_time.strftime("%H:%M"),
            "days": days,
            "note": note.strip(),
        }
    )
    save_data(MEDICATIONS_FILE, st.session_state.medications)


def update_medication(med_id, name, med_time, days, note):
    med = get_medication_by_id(med_id)
    if med:
        med["name"] = name.strip()
        med["time"] = med_time.strftime("%H:%M")
        med["days"] = days
        med["note"] = note.strip()
        save_data(MEDICATIONS_FILE, st.session_state.medications)


def delete_medication(med_id):
    st.session_state.medications = [
        m for m in st.session_state.medications if m["id"] != med_id
    ]
    st.session_state.intakes = [
        i for i in st.session_state.intakes if i["medication_id"] != med_id
    ]
    save_data(MEDICATIONS_FILE, st.session_state.medications)
    save_data(INTAKES_FILE, st.session_state.intakes)


# =========================================================
# CRUD Einnahmen
# =========================================================
def create_intake(medication_id, intake_date, intake_time, confirmed, note):
    med = get_medication_by_id(medication_id)
    if med is None:
        return

    st.session_state.intakes.append(
        {
            "id": next_id(st.session_state.intakes),
            "medication_id": medication_id,
            "medication_name": med["name"],
            "date": intake_date.isoformat(),
            "time": intake_time.strftime("%H:%M"),
            "confirmed": confirmed,
            "note": note.strip(),
        }
    )
    save_data(INTAKES_FILE, st.session_state.intakes)


def update_intake(intake_id, medication_id, intake_date, intake_time, confirmed, note):
    intake = get_intake_by_id(intake_id)
    med = get_medication_by_id(medication_id)

    if intake and med:
        intake["medication_id"] = medication_id
        intake["medication_name"] = med["name"]
        intake["date"] = intake_date.isoformat()
        intake["time"] = intake_time.strftime("%H:%M")
        intake["confirmed"] = confirmed
        intake["note"] = note.strip()
        save_data(INTAKES_FILE, st.session_state.intakes)


def delete_intake(intake_id):
    st.session_state.intakes = [
        i for i in st.session_state.intakes if i["id"] != intake_id
    ]
    save_data(INTAKES_FILE, st.session_state.intakes)


# =========================================================
# Blutdruck / Blutzucker Funktionen
# =========================================================
def upsert_blood_pressure(entry_date, systolic, diastolic):
    entry_date_str = pd.to_datetime(entry_date).strftime("%Y-%m-%d")
    entries = st.session_state.blood_pressure_entries

    existing_index = next(
        (i for i, entry in enumerate(entries) if entry["date"] == entry_date_str),
        None
    )

    new_entry = {
        "date": entry_date_str,
        "systolic": int(systolic),
        "diastolic": int(diastolic),
    }

    if existing_index is not None:
        entries[existing_index] = new_entry
    else:
        entries.append(new_entry)

    entries.sort(key=lambda x: x["date"])
    st.session_state.blood_pressure_entries = entries
    save_data(BLOOD_PRESSURE_FILE, entries)


def upsert_blood_sugar(entry_date, value):
    entry_date_str = pd.to_datetime(entry_date).strftime("%Y-%m-%d")
    entries = st.session_state.blood_sugar_entries

    existing_index = next(
        (i for i, entry in enumerate(entries) if entry["date"] == entry_date_str),
        None
    )

    new_entry = {
        "date": entry_date_str,
        "value": float(value),
    }

    if existing_index is not None:
        entries[existing_index] = new_entry
    else:
        entries.append(new_entry)

    entries.sort(key=lambda x: x["date"])
    st.session_state.blood_sugar_entries = entries
    save_data(BLOOD_SUGAR_FILE, entries)


def delete_blood_pressure(entry_date_str):
    st.session_state.blood_pressure_entries = [
        entry for entry in st.session_state.blood_pressure_entries
        if entry["date"] != entry_date_str
    ]
    save_data(BLOOD_PRESSURE_FILE, st.session_state.blood_pressure_entries)


def delete_blood_sugar(entry_date_str):
    st.session_state.blood_sugar_entries = [
        entry for entry in st.session_state.blood_sugar_entries
        if entry["date"] != entry_date_str
    ]
    save_data(BLOOD_SUGAR_FILE, st.session_state.blood_sugar_entries)


# =========================================================
# Sidebar
# =========================================================
with st.sidebar:
    st.markdown("## 💊 MediTrack")
    st.caption("Medikamente planen und Einnahmen dokumentieren")

    if st.button("Dashboard", use_container_width=True):
        go_to("dashboard")

    if st.button("Medikamente", use_container_width=True):
        go_to("medications")

    if st.button("Medikament hinzufügen", use_container_width=True):
        st.session_state.editing_medication_id = None
        go_to("medication_form")

    if st.button("Einnahme erfassen", use_container_width=True):
        st.session_state.editing_intake_id = None
        go_to("intake_form")

    if st.button("Verlauf", use_container_width=True):
        go_to("history")

    if st.button("Blutdruck-Tagebuch", use_container_width=True):
        go_to("blood_pressure")

    if st.button("Blutzucker-Tagebuch", use_container_width=True):
        go_to("blood_sugar")


# =========================================================
# Screens
# =========================================================
def screen_dashboard():
    st.markdown('<div class="title-main"></div>', unsafe_allow_html=True) #Leere Zeile für Abstand
    st.markdown('<div class="title-main">MediTrack</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="muted">Behalte deine Medikamente und Einnahmen im Blick.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Medikamente", len(st.session_state.medications))
    with col2:
        confirmed_count = sum(1 for i in st.session_state.intakes if i["confirmed"])
        st.metric("Bestätigte Einnahmen", confirmed_count)
    with col3:
        today = date.today().isoformat()
        today_count = sum(1 for i in st.session_state.intakes if i["date"] == today)
        st.metric("Einträge heute", today_count)

    st.write("")
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown("### Heute geplante Medikamente")

    todays_meds = [m for m in st.session_state.medications if medication_is_due_today(m)]
    todays_meds = sorted(todays_meds, key=lambda x: x["time"])

    if not todays_meds:
        st.info("Für heute sind noch keine Medikamente geplant.")
    else:
        for med in todays_meds:
            st.markdown(
                f"""
                <div class="pill-card">
                    <strong>{med['name']}</strong>
                    <span class="time-badge">{med['time']}</span><br>
                    <span class="muted">Tage: {format_days(med['days'])}</span><br>
                    <span class="muted">Bemerkung: {med['note'] if med['note'] else '—'}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"Einnahme bestätigen: {med['name']}", key=f"confirm_{med['id']}"):
                    intake_time = datetime.strptime(med["time"], "%H:%M").time()
                    create_intake(med["id"], date.today(), intake_time, True, "")
                    st.session_state.last_success_message = "Super! Die Einnahme wurde gespeichert."
                    go_to("success")

            with c2:
                if st.button(f"Medikament bearbeiten: {med['name']}", key=f"edit_med_{med['id']}"):
                    st.session_state.editing_medication_id = med["id"]
                    go_to("medication_form")

    st.markdown("</div>", unsafe_allow_html=True)


def screen_medications():
    st.markdown("## Meine Medikamente")

    if not st.session_state.medications:
        st.info("Noch keine Medikamente vorhanden.")
        return

    meds = sorted(st.session_state.medications, key=lambda x: x["time"])

    for med in meds:
        st.markdown(
            f"""
            <div class="pill-card">
                <strong>{med['name']}</strong>
                <span class="time-badge">{med['time']}</span><br>
                <span class="muted">Tage: {format_days(med['days'])}</span><br>
                <span class="muted">Bemerkung: {med['note'] if med['note'] else '—'}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Bearbeiten", key=f"edit_med_list_{med['id']}", use_container_width=True):
                st.session_state.editing_medication_id = med["id"]
                go_to("medication_form")
        with c2:
            if st.button("Löschen", key=f"delete_med_{med['id']}", use_container_width=True):
                delete_medication(med["id"])
                st.session_state.last_success_message = "Super! Das Medikament wurde gelöscht."
                go_to("success")


def screen_medication_form():
    editing_id = st.session_state.editing_medication_id
    editing_med = get_medication_by_id(editing_id) if editing_id else None

    st.markdown("## Medikament erfassen" if editing_med is None else "## Medikament bearbeiten")

    default_name = editing_med["name"] if editing_med else ""
    default_time = (
        datetime.strptime(editing_med["time"], "%H:%M").time()
        if editing_med
        else time(8, 0)
    )
    default_days = editing_med["days"] if editing_med else []
    default_note = editing_med["note"] if editing_med else ""

    with st.form("medication_form"):
        name = st.text_input("Medikamentenname", value=default_name)
        med_time = st.time_input("Uhrzeit", value=default_time, step=1800)
        days = st.multiselect("Wochentage", options=DAYS, default=default_days)
        note = st.text_area("Bemerkung", value=default_note)

        submitted = st.form_submit_button("Speichern")

        if submitted:
            if not name.strip():
                st.error("Bitte gib einen Medikamentennamen ein.")
            elif not days:
                st.error("Bitte wähle mindestens einen Wochentag aus.")
            else:
                if editing_med:
                    update_medication(editing_med["id"], name, med_time, days, note)
                    st.session_state.last_success_message = "Super! Das Medikament wurde aktualisiert."
                else:
                    create_medication(name, med_time, days, note)
                    st.session_state.last_success_message = "Super! Das Medikament wurde gespeichert."

                st.session_state.editing_medication_id = None
                go_to("success")


def screen_intake_form():
    st.markdown(
        "## Einnahme erfassen"
        if st.session_state.editing_intake_id is None
        else "## Einnahme bearbeiten"
    )

    if not st.session_state.medications:
        st.info("Bitte zuerst ein Medikament anlegen.")
        return

    intake = (
        get_intake_by_id(st.session_state.editing_intake_id)
        if st.session_state.editing_intake_id
        else None
    )

    medication_options = {
        f"{med['name']} ({med['time']})": med["id"]
        for med in st.session_state.medications
    }
    option_labels = list(medication_options.keys())

    if intake:
        selected_label = next(
            (label for label, med_id in medication_options.items() if med_id == intake["medication_id"]),
            option_labels[0],
        )
        default_index = option_labels.index(selected_label)
        default_date = datetime.strptime(intake["date"], "%Y-%m-%d").date()
        default_time = datetime.strptime(intake["time"], "%H:%M").time()
        default_confirmed = intake["confirmed"]
        default_note = intake["note"]
    else:
        default_index = 0
        default_date = date.today()
        default_time = time(8, 0)
        default_confirmed = True
        default_note = ""

    with st.form("intake_form"):
        selected_medication = st.selectbox("Medikament", options=option_labels, index=default_index)
        intake_date = st.date_input("Datum der Einnahme", value=default_date)
        intake_time = st.time_input("Uhrzeit der Einnahme", value=default_time, step=300)
        confirmed = st.checkbox("Einnahme bestätigt", value=default_confirmed)
        note = st.text_area("Bemerkung", value=default_note)

        submitted = st.form_submit_button("Speichern")

        if submitted:
            medication_id = medication_options[selected_medication]

            if intake:
                update_intake(intake["id"], medication_id, intake_date, intake_time, confirmed, note)
                st.session_state.editing_intake_id = None
                st.session_state.last_success_message = "Super! Die Einnahme wurde aktualisiert."
            else:
                create_intake(medication_id, intake_date, intake_time, confirmed, note)
                st.session_state.last_success_message = "Super! Die Einnahme wurde gespeichert."

            go_to("success")


def screen_history():
    st.markdown("## Einnahmeverlauf")

    if not st.session_state.intakes:
        st.info("Noch keine Einnahmen erfasst.")
        return

    sorted_intakes = sorted(
        st.session_state.intakes,
        key=lambda x: (x["date"], x["time"]),
        reverse=True,
    )

    for intake in sorted_intakes:
        status_html = (
            '<span class="ok-badge">Bestätigt</span>'
            if intake["confirmed"]
            else '<span class="no-badge">Nicht bestätigt</span>'
        )

        st.markdown(
            f"""
            <div class="pill-card">
                <strong>{intake['medication_name']}</strong>
                <span class="time-badge">{intake['time']}</span><br>
                <span class="muted">Datum: {intake['date']}</span><br>
                <span class="muted">Status: {status_html}</span><br>
                <span class="muted">Bemerkung: {intake['note'] if intake['note'] else '—'}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Einnahme bearbeiten", key=f"edit_intake_{intake['id']}", use_container_width=True):
                st.session_state.editing_intake_id = intake["id"]
                go_to("intake_form")
        with c2:
            if st.button("Einnahme löschen", key=f"delete_intake_{intake['id']}", use_container_width=True):
                delete_intake(intake["id"])
                st.session_state.last_success_message = "Super! Die Einnahme wurde gelöscht."
                go_to("success")


def screen_blood_pressure():
    st.markdown("## Mein Blutdruck-Tagebuch")

    with st.form("blood_pressure_form"):
        bp_date = st.date_input("Datum", value=date.today(), key="bp_date")

        c1, c2 = st.columns(2)
        with c1:
            bp_systolic = st.number_input(
                "Systolisch (mmHg)",
                min_value=50,
                max_value=300,
                value=120,
                step=1,
                key="bp_systolic"
            )

        with c2:
            bp_diastolic = st.number_input(
                "Diastolisch (mmHg)",
                min_value=30,
                max_value=200,
                value=80,
                step=1,
                key="bp_diastolic"
            )

        bp_submit = st.form_submit_button("Blutdruck speichern")

        if bp_submit:
            upsert_blood_pressure(bp_date, bp_systolic, bp_diastolic)
            st.success("Super! Der Blutdruckeintrag wurde gespeichert.")

            if bp_systolic > 180 or bp_diastolic > 120 or bp_systolic < 80 or bp_diastolic < 50:
                st.error("Kritischer Blutdruckwert. Bitte dringend ärztlich abklären.")
            elif bp_systolic > 140 or bp_diastolic > 90 or bp_systolic < 90 or bp_diastolic < 60:
                st.warning("Auffälliger Blutdruckwert. Bitte beobachten und gegebenenfalls ärztlich abklären.")

    entries = st.session_state.blood_pressure_entries

    if entries:
        bp_df = pd.DataFrame(entries)
        bp_df["date"] = pd.to_datetime(bp_df["date"])
        bp_df = bp_df.sort_values("date")

        bp_table = bp_df.copy()
        bp_table["date"] = bp_table["date"].dt.strftime("%Y-%m-%d")
        bp_table = bp_table.rename(
            columns={
                "date": "Datum",
                "systolic": "Systolisch (mmHg)",
                "diastolic": "Diastolisch (mmHg)",
            }
        )

        st.dataframe(bp_table, use_container_width=True, hide_index=True)

        bp_chart = bp_df[["date", "systolic", "diastolic"]].copy().set_index("date")
        st.line_chart(bp_chart, use_container_width=True)

        with st.expander("Blutdruckeintrag löschen"):
            bp_delete_options = [entry["date"] for entry in entries]
            bp_delete_date = st.selectbox(
                "Welches Datum möchtest du löschen?",
                options=bp_delete_options,
                key="bp_delete_date"
            )
            if st.button("Blutdruckeintrag löschen", key="delete_bp_button"):
                delete_blood_pressure(bp_delete_date)
                st.success("Blutdruckeintrag wurde gelöscht.")
                st.rerun()
    else:
        st.info("Noch keine Blutdruckwerte eingetragen.")


def screen_blood_sugar():
    st.markdown("## Mein Blutzucker-Tagebuch")

    with st.form("blood_sugar_form"):
        bs_date = st.date_input("Datum", value=date.today(), key="bs_date")

        bs_value = st.number_input(
            "Blutzucker (mmol/l)",
            min_value=0.0,
            max_value=40.0,
            value=5.5,
            step=0.1,
            format="%.1f",
            key="bs_value"
        )

        bs_submit = st.form_submit_button("Blutzucker speichern")

        if bs_submit:
            upsert_blood_sugar(bs_date, bs_value)
            st.success("Super! Der Blutzuckereintrag wurde gespeichert.")

            if bs_value > 15 or bs_value < 3:
                st.error("Kritischer Blutzuckerwert. Bitte dringend ärztlich abklären.")
            elif bs_value > 10 or bs_value < 3.5:
                st.warning("Auffälliger Blutzuckerwert. Bitte beobachten und gegebenenfalls ärztlich abklären.")

    entries = st.session_state.blood_sugar_entries

    if entries:
        bs_df = pd.DataFrame(entries)
        bs_df["date"] = pd.to_datetime(bs_df["date"])
        bs_df = bs_df.sort_values("date")

        bs_table = bs_df.copy()
        bs_table["date"] = bs_table["date"].dt.strftime("%Y-%m-%d")
        bs_table = bs_table.rename(
            columns={
                "date": "Datum",
                "value": "Blutzucker (mmol/l)",
            }
        )

        st.dataframe(bs_table, use_container_width=True, hide_index=True)

        bs_chart = bs_df[["date", "value"]].copy().set_index("date")
        st.line_chart(bs_chart, use_container_width=True)

        with st.expander("Blutzuckereintrag löschen"):
            bs_delete_options = [entry["date"] for entry in entries]
            bs_delete_date = st.selectbox(
                "Welches Datum möchtest du löschen?",
                options=bs_delete_options,
                key="bs_delete_date"
            )
            if st.button("Blutzuckereintrag löschen", key="delete_bs_button"):
                delete_blood_sugar(bs_delete_date)
                st.success("Blutzuckereintrag wurde gelöscht.")
                st.rerun()
    else:
        st.info("Noch keine Blutzuckerwerte eingetragen.")


def screen_success():
    message = st.session_state.get("last_success_message", "Super!")

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display:flex; justify-content:center; margin-bottom:1rem;">
            <div style="width:84px;height:84px;border-radius:50%;background:#e8f8ec;color:#16a34a;display:flex;align-items:center;justify-content:center;font-size:2rem;">✓</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<h2 style='text-align:center;'>Super!</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='muted' style='text-align:center;'>{message}</p>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Zur Übersicht", use_container_width=True):
            go_to("dashboard")
    with c2:
        if st.button("Zum Verlauf", use_container_width=True):
            go_to("history")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# Router
# =========================================================
pages = {
    "dashboard": screen_dashboard,
    "medications": screen_medications,
    "medication_form": screen_medication_form,
    "intake_form": screen_intake_form,
    "history": screen_history,
    "blood_pressure": screen_blood_pressure,
    "blood_sugar": screen_blood_sugar,
    "success": screen_success,
}

current_page = st.session_state.page
pages.get(current_page, screen_dashboard)()