"""
views/verlauf.py
Einnahmeverlauf: Gruppiert nach Monat → Woche → Tag.
Verwendet native Streamlit-Elemente statt komplexem HTML.
"""

import html
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, time as dtime

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.week-label { font-size: 12px; font-weight: 600; color: #6b7280; letter-spacing: 0.03em; margin: 0.5rem 0 0.3rem; }
.day-label  { font-size: 13px; font-weight: 600; color: #374151; margin: 0.6rem 0 0.2rem; display: flex; align-items: center; gap: 8px; }
.day-date   { font-size: 12px; color: #9ca3af; font-weight: 400; }
.day-count  { font-size: 11px; color: #9ca3af; margin-left: auto; }
.intake-card {
    background: white; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 0.55rem 1rem; margin-bottom: 0.35rem;
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
}
.intake-left { display: flex; align-items: center; gap: 8px; }
.dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-green { background: #22c55e; }
.dot-red   { background: #ef4444; }
.intake-name { font-size: 13px; font-weight: 500; color: #111827; }
.intake-note { font-size: 11px; color: #9ca3af; }
.intake-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.time-tag { font-size: 11px; background: #f3f4f6; color: #6b7280; padding: 2px 7px; border-radius: 6px; font-weight: 500; }
.ok-badge  { font-size: 11px; padding: 2px 8px; border-radius: 99px; background: #dcfce7; color: #15803d; font-weight: 600; }
.no-badge  { font-size: 11px; padding: 2px 8px; border-radius: 99px; background: #fee2e2; color: #b91c1c; font-weight: 600; }
div.stButton > button { border-radius: 10px; font-weight: 600; min-height: 36px; font-size: 12px; }
</style>""", unsafe_allow_html=True)

def e(t): return html.escape(str(t))

def is_confirmed(val):
    return str(val).strip().lower() in ["true", "1", "yes"]

def next_id(df):
    if df.empty or "id" not in df.columns:
        return 1
    return int(df["id"].max()) + 1

def save_intakes():
    st.session_state["data_manager"].save_user_data(st.session_state["intakes_df"], "intakes.csv")

def get_week_range(dt):
    monday = dt - timedelta(days=dt.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

WEEKDAYS_DE = {0:"Montag", 1:"Dienstag", 2:"Mittwoch", 3:"Donnerstag",
               4:"Freitag", 5:"Samstag", 6:"Sonntag"}
MONTHS_DE   = {1:"Januar", 2:"Februar", 3:"März", 4:"April", 5:"Mai",
               6:"Juni", 7:"Juli", 8:"August", 9:"September",
               10:"Oktober", 11:"November", 12:"Dezember"}

# ── Seite ─────────────────────────────────────────────────────────────────────
st.markdown("## 📋 Einnahmeverlauf")
st.markdown('<p style="color:#6b7280">Alle erfassten Einnahmen – nach Monat, Woche und Tag gegliedert.</p>',
            unsafe_allow_html=True)
st.write("")

intakes_df = st.session_state["intakes_df"]
meds_df    = st.session_state["medications_df"]

tab_history, tab_stats, tab_form = st.tabs([
    "📅 Verlauf", "📊 Statistik", "➕ Einnahme erfassen / bearbeiten"
])

# ── Tab 1: Verlauf ─────────────────────────────────────────────────────────────
with tab_history:
    if intakes_df.empty:
        st.info("Noch keine Einnahmen erfasst.")
    else:
        df = intakes_df.copy()
        df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date_parsed"]).sort_values("date_parsed", ascending=False)

        with st.expander("🔍 Filter", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                filter_from = st.date_input("Von", value=date.today() - timedelta(days=29), key="hist_from")
            with c2:
                filter_to   = st.date_input("Bis", value=date.today(), key="hist_to")
            with c3:
                med_names  = ["Alle"] + sorted(df["medication_name"].dropna().unique().tolist())
                filter_med = st.selectbox("Medikament", options=med_names, key="hist_med")
            show_all = st.checkbox("Gesamten Verlauf anzeigen", value=False)

        filtered = df.copy()
        if not show_all:
            filtered = filtered[
                (filtered["date_parsed"].dt.date >= filter_from) &
                (filtered["date_parsed"].dt.date <= filter_to)
            ]
        if filter_med != "Alle":
            filtered = filtered[filtered["medication_name"] == filter_med]

        if filtered.empty:
            st.info("Keine Einnahmen im gewählten Zeitraum.")
        else:
            st.caption(f"{len(filtered)} Einträge gefunden")

            filtered["year_month"] = filtered["date_parsed"].dt.to_period("M")
            filtered["iso_week"]   = filtered["date_parsed"].dt.isocalendar().week.astype(int)
            filtered["iso_year"]   = filtered["date_parsed"].dt.isocalendar().year.astype(int)

            for ym, month_group in filtered.groupby("year_month", sort=False):
                month_dt    = ym.to_timestamp()
                month_label = f"{MONTHS_DE[month_dt.month]} {month_dt.year}"
                month_count = len(month_group)

                st.markdown(f"### 📅 {month_label} &nbsp; <span style='font-size:13px;color:#9ca3af;font-weight:400'>{month_count} Einnahmen</span>",
                            unsafe_allow_html=True)

                for (iso_year, iso_week), week_group in month_group.groupby(
                    ["iso_year", "iso_week"], sort=False
                ):
                    first_day      = week_group["date_parsed"].max().date()
                    monday, sunday = get_week_range(first_day)
                    week_label     = f"KW {iso_week}  ·  {monday.strftime('%d. %b')} – {sunday.strftime('%d. %b')}"

                    st.markdown(f'<div class="week-label">📆 {e(week_label)}</div>', unsafe_allow_html=True)

                    for day_date, day_group in week_group.groupby(
                        week_group["date_parsed"].dt.date, sort=False
                    ):
                        day_group = day_group.sort_values("time")
                        wd        = WEEKDAYS_DE[day_date.weekday()]
                        day_count = len(day_group)

                        st.markdown(
                            f'<div class="day-label">'
                            f'{e(wd)} <span class="day-date">{day_date.strftime("%d.%m.%Y")}</span>'
                            f'<span class="day-count">{day_count} Einnahme{"n" if day_count != 1 else ""}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                        for _, intake in day_group.iterrows():
                            confirmed  = is_confirmed(intake.get("confirmed", False))
                            dot_cls    = "dot-green" if confirmed else "dot-red"
                            badge_cls  = "ok-badge" if confirmed else "no-badge"
                            badge_text = "✓ Bestätigt" if confirmed else "✗ Nicht bestätigt"
                            note_text  = str(intake["note"]).strip() if pd.notna(intake.get("note")) and str(intake.get("note", "")).strip() else ""
                            note_html  = f'<div class="intake-note">{e(note_text)}</div>' if note_text else ""

                            st.markdown(
                                f'<div class="intake-card">'
                                f'  <div class="intake-left">'
                                f'    <div class="dot {dot_cls}"></div>'
                                f'    <div><div class="intake-name">{e(str(intake["medication_name"]))}</div>{note_html}</div>'
                                f'  </div>'
                                f'  <div class="intake-right">'
                                f'    <span class="time-tag">{e(str(intake["time"]))}</span>'
                                f'    <span class="{badge_cls}">{badge_text}</span>'
                                f'  </div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button(f"✏️ Bearbeiten", key=f"edit_int_{intake['id']}", use_container_width=True):
                                    st.session_state["editing_intake_id"] = int(intake["id"])
                                    st.rerun()
                            with col2:
                                if st.button(f"🗑️ Löschen", key=f"del_int_{intake['id']}", use_container_width=True):
                                    st.session_state["intakes_df"] = intakes_df[
                                        intakes_df["id"] != intake["id"]
                                    ].reset_index(drop=True)
                                    save_intakes()
                                    st.success("Einnahme gelöscht.")
                                    st.rerun()

                st.divider()

# ── Tab 2: Statistik ───────────────────────────────────────────────────────────
with tab_stats:
    if intakes_df.empty or meds_df.empty:
        st.info("Noch keine Daten für Statistiken vorhanden.")
    else:
        df_s = intakes_df.copy()
        df_s["confirmed_bool"] = df_s["confirmed"].apply(is_confirmed)

        total_intakes     = len(intakes_df)
        total_confirmed   = int(df_s["confirmed_bool"].sum())
        total_unconfirmed = total_intakes - total_confirmed
        c1, c2, c3 = st.columns(3)
        c1.metric("📋 Einnahmen gesamt", total_intakes)
        c2.metric("✅ Bestätigt", total_confirmed)
        c3.metric("❌ Nicht bestätigt", total_unconfirmed)

        st.divider()
        st.markdown("#### Einnahmetreue pro Medikament")
        st.caption("Jeder Punkt = eine Einnahme. Grün = bestätigt, grau = nicht bestätigt.")
        st.write("")

        for _, med in meds_df.iterrows():
            med_intakes = df_s[df_s["medication_id"] == med["id"]].sort_values("date")
            if med_intakes.empty:
                continue
            total     = len(med_intakes)
            confirmed = int(med_intakes["confirmed_bool"].sum())
            pct       = int(confirmed / total * 100)

            if pct >= 80:   pct_col = "#16a34a"
            elif pct >= 50: pct_col = "#d97706"
            else:           pct_col = "#dc2626"

            dots_html = "".join(
                f'<div style="width:9px;height:9px;border-radius:50%;flex-shrink:0;background:{"#22c55e" if r["confirmed_bool"] else "#e5e7eb"}" title="{e(str(r["date"]))}"></div>'
                for _, r in med_intakes.tail(30).iterrows()
            )
            last_date = med_intakes["date"].iloc[-1]

            st.markdown(
                f'<div style="background:white;border:1px solid #e5e7eb;border-radius:14px;'
                f'padding:1rem 1.25rem;margin-bottom:0.6rem;display:flex;align-items:center;'
                f'justify-content:space-between;gap:1rem">'
                f'  <div style="flex:1">'
                f'    <div style="font-weight:600;font-size:0.95rem;color:#111827;margin-bottom:0.2rem">💊 {e(str(med["name"]))}</div>'
                f'    <div style="font-size:0.8rem;color:#6b7280;margin-bottom:0.4rem">{confirmed} von {total} bestätigt &nbsp;·&nbsp; Letzte: {e(str(last_date))}</div>'
                f'    <div style="display:flex;gap:4px;flex-wrap:wrap">{dots_html}</div>'
                f'  </div>'
                f'  <div style="font-size:1.5rem;font-weight:700;color:{pct_col};min-width:52px;text-align:right">{pct}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )

# ── Tab 3: Formular ────────────────────────────────────────────────────────────
with tab_form:
    if meds_df.empty:
        st.info("Bitte zuerst ein Medikament anlegen.")
    else:
        editing_id  = st.session_state.get("editing_intake_id")
        editing_row = None
        if editing_id is not None and not intakes_df.empty:
            matches = intakes_df[intakes_df["id"] == editing_id]
            if not matches.empty:
                editing_row = matches.iloc[0]

        if editing_row is not None:
            st.markdown(f"**Bearbeite Einnahme** vom {editing_row['date']}")
            if st.button("↩️ Abbrechen"):
                st.session_state["editing_intake_id"] = None
                st.rerun()

        med_options   = {f"{r['name']} ({r['time']})": int(r["id"]) for _, r in meds_df.iterrows()}
        option_labels = list(med_options.keys())

        if editing_row is not None:
            sel_label    = next((l for l, mid in med_options.items() if mid == editing_row["medication_id"]), option_labels[0])
            default_idx  = option_labels.index(sel_label)
            default_date = datetime.strptime(str(editing_row["date"]), "%Y-%m-%d").date()
            default_time = datetime.strptime(str(editing_row["time"]), "%H:%M").time()
            default_conf = is_confirmed(editing_row.get("confirmed", True))
            default_note = str(editing_row["note"]) if pd.notna(editing_row.get("note")) else ""
        else:
            default_idx, default_date, default_time = 0, date.today(), dtime(8, 0)
            default_conf, default_note = True, ""

        with st.form("intake_form", clear_on_submit=True):
            sel_med     = st.selectbox("Medikament", options=option_labels, index=default_idx)
            intake_date = st.date_input("Datum", value=default_date)
            intake_time = st.time_input("Uhrzeit", value=default_time, step=300)
            confirmed   = st.checkbox("Einnahme bestätigt", value=default_conf)
            note        = st.text_area("Bemerkung (optional)", value=default_note)

            submitted = st.form_submit_button("💾 Speichern", use_container_width=True)
            if submitted:
                med_id   = med_options[sel_med]
                med_name = meds_df[meds_df["id"] == med_id].iloc[0]["name"]
                time_str = intake_time.strftime("%H:%M")

                if editing_row is not None:
                    idx = st.session_state["intakes_df"].index[
                        st.session_state["intakes_df"]["id"] == editing_id
                    ].tolist()
                    if idx:
                        st.session_state["intakes_df"].at[idx[0], "medication_id"]    = med_id
                        st.session_state["intakes_df"].at[idx[0], "medication_name"]  = med_name
                        st.session_state["intakes_df"].at[idx[0], "date"]             = intake_date.isoformat()
                        st.session_state["intakes_df"].at[idx[0], "time"]             = time_str
                        st.session_state["intakes_df"].at[idx[0], "confirmed"]        = confirmed
                        st.session_state["intakes_df"].at[idx[0], "note"]             = note.strip()
                    st.session_state["editing_intake_id"] = None
                    st.success("✅ Einnahme aktualisiert.")
                else:
                    new_row = pd.DataFrame([{
                        "id":              next_id(st.session_state["intakes_df"]),
                        "medication_id":   med_id,
                        "medication_name": med_name,
                        "date":            intake_date.isoformat(),
                        "time":            time_str,
                        "confirmed":       confirmed,
                        "note":            note.strip(),
                        "created_at":      pd.Timestamp.now(),
                    }])
                    st.session_state["intakes_df"] = pd.concat(
                        [st.session_state["intakes_df"], new_row], ignore_index=True
                    )
                    st.success("✅ Einnahme gespeichert.")

                save_intakes()
                st.rerun()