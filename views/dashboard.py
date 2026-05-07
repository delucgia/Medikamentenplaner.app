"""
views/dashboard.py
Tagesübersicht: Begrüssung, Metriken, heutige Medikamente,
Einnahmetreue, letzte Gesundheitswerte.
"""

import html
import streamlit as st
import pandas as pd
from datetime import date, datetime

# ── Styling ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 10px; margin-bottom: 1.25rem; }
.metric-card { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 14px; padding: 1rem 1.1rem; }
.metric-label { font-size: 12px; color: #6b7280; margin-bottom: 4px; }
.metric-value { font-size: 24px; font-weight: 700; color: #111827; }
.metric-sub { font-size: 11px; color: #9ca3af; margin-top: 2px; }

.alert-banner { background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px;
                padding: 0.65rem 1rem; font-size: 13px; color: #92400e;
                display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem; }

.pill-card { background: white; border: 1px solid #e5e7eb; border-radius: 14px;
             padding: 0.85rem 1rem; margin-bottom: 0.5rem;
             display: flex; align-items: center; gap: 12px; }
.pill-icon { width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
             display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }
.pill-icon-blue   { background: #eff6ff; }
.pill-icon-yellow { background: #fffbeb; }
.pill-icon-gray   { background: #f9fafb; }
.pill-body { flex: 1; min-width: 0; }
.pill-name { font-size: 14px; font-weight: 600; color: #111827; }
.pill-meta { font-size: 12px; color: #6b7280; margin-top: 1px; }
.pill-right { display: flex; flex-direction: column; align-items: flex-end; gap: 5px; flex-shrink: 0; }
.time-chip { font-size: 11px; font-weight: 600; background: #f3f4f6; color: #374151;
             padding: 2px 8px; border-radius: 7px; font-family: monospace; }
.badge-done { font-size: 11px; font-weight: 600; color: #15803d;
              background: #dcfce7; padding: 2px 8px; border-radius: 999px; }
.badge-pending { font-size: 11px; font-weight: 600; color: #b45309;
                 background: #fef3c7; padding: 2px 8px; border-radius: 999px; }
.badge-later { font-size: 11px; font-weight: 600; color: #6b7280;
               background: #f3f4f6; padding: 2px 8px; border-radius: 999px; }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 0.25rem; }
.section-label { font-size: 13px; font-weight: 600; color: #6b7280;
                 text-transform: uppercase; letter-spacing: 0.05em;
                 margin: 1.25rem 0 0.65rem; }

.adhere-card { background: white; border: 1px solid #e5e7eb; border-radius: 14px;
               padding: 0.9rem 1.1rem; margin-bottom: 0.5rem; }
.adhere-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; }
.adhere-name { font-size: 13px; font-weight: 600; color: #111827; }
.adhere-count { font-size: 11px; color: #9ca3af; }
.adhere-pct { font-size: 15px; font-weight: 700; }
.progress-track { height: 6px; background: #f3f4f6; border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 99px; }

.health-card { background: white; border: 1px solid #e5e7eb; border-radius: 14px;
               padding: 1rem 1.1rem; margin-bottom: 0.5rem; }
.health-title { font-size: 12px; color: #6b7280; margin-bottom: 3px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.health-value { font-size: 22px; font-weight: 700; color: #111827; }
.health-unit { font-size: 13px; font-weight: 400; color: #9ca3af; margin-left: 3px; }
.health-status { font-size: 12px; font-weight: 600; margin-top: 3px; }
.health-date { font-size: 11px; color: #9ca3af; margin-top: 2px; }
.status-ok     { color: #15803d; }
.status-warn   { color: #b45309; }
.status-crit   { color: #b91c1c; }
.status-hypo   { color: #6d28d9; }

div.stButton > button { border-radius: 10px; font-weight: 600; min-height: 38px; font-size: 13px; }
</style>""", unsafe_allow_html=True)

# ── Hilfsfunktionen ─────────────────────────────────────────────────────────────
DAY_MAP  = {0:"Mo",1:"Di",2:"Mi",3:"Do",4:"Fr",5:"Sa",6:"So"}
DAYS_ALL = ["Mo","Di","Mi","Do","Fr","Sa","So"]
MONTHS_DE = {1:"Januar",2:"Februar",3:"März",4:"April",5:"Mai",6:"Juni",
             7:"Juli",8:"August",9:"September",10:"Oktober",11:"November",12:"Dezember"}
WEEKDAYS_DE = {0:"Montag",1:"Dienstag",2:"Mittwoch",3:"Donnerstag",
               4:"Freitag",5:"Samstag",6:"Sonntag"}

def e(t): return html.escape(str(t))

def get_today_day():
    return DAY_MAP[datetime.today().weekday()]

def format_days(days_str):
    if not days_str or pd.isna(days_str):
        return "—"
    days = [d.strip() for d in str(days_str).split(",")]
    if days == DAYS_ALL: return "Täglich"
    if days == ["Mo","Di","Mi","Do","Fr"]: return "Mo–Fr"
    return ", ".join(days)

def med_due_today(days_str):
    if not days_str or pd.isna(days_str):
        return False
    return get_today_day() in [d.strip() for d in str(days_str).split(",")]

def intake_exists_today(medication_id):
    df = st.session_state["intakes_df"]
    if df.empty: return False
    today = date.today().isoformat()
    return not df[(df["medication_id"] == medication_id) & (df["date"] == today)].empty

def is_confirmed(val):
    return str(val).strip().lower() in ["true","1","yes"]

def next_id(df):
    if df.empty or "id" not in df.columns: return 1
    return int(df["id"].max()) + 1

def save_intake(medication_id, med_name, intake_date, intake_time, confirmed, note):
    dm = st.session_state["data_manager"]
    df = st.session_state["intakes_df"]
    new_row = pd.DataFrame([{
        "id": next_id(df),
        "medication_id": medication_id,
        "medication_name": med_name,
        "date": intake_date.isoformat(),
        "time": intake_time,
        "confirmed": confirmed,
        "note": note,
        "created_at": pd.Timestamp.now(),
    }])
    updated = pd.concat([df, new_row], ignore_index=True)
    st.session_state["intakes_df"] = updated
    dm.save_user_data(updated, "intakes.csv")

def classify_bp(sys, dia):
    if sys < 100 or dia < 60: return "Hypotonie", "status-hypo"
    if sys >= 180 or dia >= 110: return "Hypertonie Grad 3", "status-crit"
    if sys >= 160 or dia >= 100: return "Hypertonie Grad 2", "status-crit"
    if sys >= 140 or dia >= 90:  return "Hypertonie Grad 1", "status-warn"
    if sys >= 130 or dia >= 85:  return "Hoch-normal",        "status-warn"
    if sys >= 120 or dia >= 80:  return "Normal",             "status-ok"
    return "Optimal", "status-ok"

def classify_bs(value):
    if value < 3.0: return "Kritisch tief", "status-crit"
    if value < 3.9: return "Auffällig tief", "status-warn"
    if value <= 5.5: return "Normal", "status-ok"
    if value < 7.0: return "Auffällig hoch", "status-warn"
    return "Kritisch hoch", "status-crit"

# ── Daten laden ──────────────────────────────────────────────────────────────────
meds_df    = st.session_state["medications_df"]
intakes_df = st.session_state["intakes_df"]
bp_df      = st.session_state["blood_pressure_df"]
bs_df      = st.session_state["blood_sugar_df"]
today_iso  = date.today().isoformat()
today_dt   = datetime.today()

# ── Begrüssung ───────────────────────────────────────────────────────────────────
hour = today_dt.hour
greeting = "Guten Morgen" if hour < 12 else ("Guten Mittag" if hour < 17 else "Guten Abend")
date_label = f"{WEEKDAYS_DE[today_dt.weekday()]}, {today_dt.day}. {MONTHS_DE[today_dt.month]} {today_dt.year}"

st.markdown(f"## 👋 {greeting}!")
st.markdown(f'<p style="color:#6b7280;margin-top:-0.5rem;margin-bottom:1.25rem">{date_label} — Hier ist dein täglicher Überblick.</p>', unsafe_allow_html=True)

# ── Metriken ─────────────────────────────────────────────────────────────────────
todays_meds = meds_df[meds_df["days"].apply(med_due_today)] if not meds_df.empty else pd.DataFrame()
taken_today = sum(1 for _, r in todays_meds.iterrows() if intake_exists_today(r["id"]))
total_today = len(todays_meds)
pct_today   = int(taken_today / total_today * 100) if total_today > 0 else 0

confirmed_total = 0
if not intakes_df.empty and "confirmed" in intakes_df.columns:
    confirmed_total = int(intakes_df["confirmed"].apply(is_confirmed).sum())

week_count = 0
if not intakes_df.empty:
    df_w = intakes_df.copy()
    df_w["date_dt"] = pd.to_datetime(df_w["date"], errors="coerce")
    week_count = int((df_w["date_dt"] >= pd.Timestamp.today() - pd.Timedelta(days=6)).sum())

# Letzter Blutdruck
bp_metric_val, bp_metric_sub, bp_metric_color = "—", "kein Eintrag", "#9ca3af"
if not bp_df.empty:
    bp_last = bp_df.sort_values("date").iloc[-1]
    sys_v, dia_v = int(bp_last["systolic"]), int(bp_last["diastolic"])
    bp_status, bp_css = classify_bp(sys_v, dia_v)
    color_map = {"status-ok":"#15803d","status-warn":"#b45309","status-crit":"#b91c1c","status-hypo":"#6d28d9"}
    bp_metric_val   = f"{sys_v}/{dia_v}"
    bp_metric_sub   = bp_status
    bp_metric_color = color_map.get(bp_css, "#9ca3af")

st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-label">💊 Medikamente</div>
    <div class="metric-value">{len(meds_df)}</div>
    <div class="metric-sub">aktiv geplant</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">✅ Heute eingenommen</div>
    <div class="metric-value">{taken_today}/{total_today}</div>
    <div class="metric-sub">{pct_today}% erledigt</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">📅 Diese Woche</div>
    <div class="metric-value">{week_count}</div>
    <div class="metric-sub">Einnahmen erfasst</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">❤️ Letzter Blutdruck</div>
    <div class="metric-value" style="font-size:20px">{e(bp_metric_val)}</div>
    <div class="metric-sub" style="color:{bp_metric_color};font-weight:600">{e(bp_metric_sub)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Erinnerungs-Banner ───────────────────────────────────────────────────────────
if not todays_meds.empty:
    pending = [r for _, r in todays_meds.iterrows() if not intake_exists_today(r["id"])]
    for med in pending:
        st.markdown(
            f'<div class="alert-banner">⏰ <strong>{e(med["name"])}</strong> ist heute um {e(med["time"])} Uhr fällig – noch nicht bestätigt.</div>',
            unsafe_allow_html=True
        )

st.divider()

# ── Heutige Medikamente ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Heute geplante Medikamente</div>', unsafe_allow_html=True)

if meds_df.empty or todays_meds.empty:
    st.info("Für heute sind keine Medikamente geplant.")
else:
    todays_sorted = todays_meds.sort_values("time")
    for _, med in todays_sorted.iterrows():
        already    = intake_exists_today(med["id"])
        note_text  = str(med["note"]).strip() if pd.notna(med.get("note")) and str(med.get("note","")).strip() else "keine Bemerkung"
        icon_class = "pill-icon-blue" if already else "pill-icon-yellow"
        badge_html = '<span class="badge-done">✓ Bestätigt</span>' if already else '<span class="badge-pending">Ausstehend</span>'

        st.markdown(f"""
        <div class="pill-card">
            <div class="pill-icon {icon_class}">💊</div>
            <div class="pill-body">
                <div class="pill-name">{e(med['name'])}</div>
                <div class="pill-meta">{e(format_days(med['days']))} · {e(note_text)}</div>
            </div>
            <div class="pill-right">
                <span class="time-chip">{e(med['time'])}</span>
                {badge_html}
            </div>
        </div>""", unsafe_allow_html=True)

        if not already:
            if st.button(f"✅ Einnahme bestätigen – {med['name']}", key=f"confirm_{med['id']}", use_container_width=True):
                save_intake(med["id"], med["name"], date.today(), str(med["time"]), True, "")
                st.success(f"'{med['name']}' wurde als eingenommen markiert!")
                st.rerun()

st.divider()

# ── Einnahmetreue + Gesundheitswerte ─────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-label">Einnahmetreue</div>', unsafe_allow_html=True)

    if meds_df.empty or intakes_df.empty:
        st.info("Noch keine Daten vorhanden.")
    else:
        df_s = intakes_df.copy()
        df_s["confirmed_bool"] = df_s["confirmed"].apply(is_confirmed)
        any_shown = False

        for _, med in meds_df.iterrows():
            med_intakes = df_s[df_s["medication_id"] == med["id"]]
            if med_intakes.empty: continue
            any_shown  = True
            total      = len(med_intakes)
            confirmed  = int(med_intakes["confirmed_bool"].sum())
            pct        = int(confirmed / total * 100)

            if pct >= 80:   bar_color, pct_color = "#22c55e", "#15803d"
            elif pct >= 50: bar_color, pct_color = "#f59e0b", "#b45309"
            else:           bar_color, pct_color = "#ef4444", "#b91c1c"

            st.markdown(f"""
            <div class="adhere-card">
                <div class="adhere-header">
                    <div>
                        <div class="adhere-name">{e(str(med['name']))}</div>
                        <div class="adhere-count">{confirmed} von {total} bestätigt</div>
                    </div>
                    <div class="adhere-pct" style="color:{pct_color}">{pct}%</div>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{pct}%;background:{bar_color}"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        if not any_shown:
            st.info("Noch keine Einnahmen erfasst.")

with col_right:
    st.markdown('<div class="section-label">Letzte Gesundheitswerte</div>', unsafe_allow_html=True)

    # Blutdruck
    if not bp_df.empty:
        bp_last   = bp_df.sort_values("date").iloc[-1]
        sys_v     = int(bp_last["systolic"])
        dia_v     = int(bp_last["diastolic"])
        bp_status, bp_css = classify_bp(sys_v, dia_v)
        bp_date   = str(bp_last["date"])[:10]
        st.markdown(f"""
        <div class="health-card">
            <div class="health-title">❤️ Blutdruck</div>
            <div class="health-value">{sys_v} / {dia_v}<span class="health-unit">mmHg</span></div>
            <div class="health-status {bp_css}">{e(bp_status)}</div>
            <div class="health-date">gemessen: {e(bp_date)}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="health-card">
            <div class="health-title">❤️ Blutdruck</div>
            <div class="health-value" style="font-size:16px;color:#9ca3af">Noch kein Eintrag</div>
        </div>""", unsafe_allow_html=True)

    # Blutzucker
    if not bs_df.empty:
        bs_last   = bs_df.sort_values("date").iloc[-1]
        bs_val    = float(bs_last["value"])
        bs_status, bs_css = classify_bs(bs_val)
        bs_date   = str(bs_last["date"])[:10]
        st.markdown(f"""
        <div class="health-card">
            <div class="health-title">🩸 Nüchternblutzucker</div>
            <div class="health-value">{bs_val:.1f}<span class="health-unit">mmol/l</span></div>
            <div class="health-status {bs_css}">{e(bs_status)}</div>
            <div class="health-date">gemessen: {e(bs_date)}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="health-card">
            <div class="health-title">🩸 Nüchternblutzucker</div>
            <div class="health-value" style="font-size:16px;color:#9ca3af">Noch kein Eintrag</div>
        </div>""", unsafe_allow_html=True)