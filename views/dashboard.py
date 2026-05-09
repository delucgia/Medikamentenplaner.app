"""
views/dashboard.py
Tagesübersicht mit Streak (inkl. heute), Metriken, Trend-Analyse, Gesundheitswerte.
"""

import html
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from utils.translations import t
from utils.themes import inject_theme, get_theme

inject_theme()
theme = get_theme()

def e(x): return html.escape(str(x))

DAY_MAP     = {0:"Mo",1:"Di",2:"Mi",3:"Do",4:"Fr",5:"Sa",6:"So"}
DAYS_ALL    = ["Mo","Di","Mi","Do","Fr","Sa","So"]
MONTHS_DE   = {1:"Januar",2:"Februar",3:"März",4:"April",5:"Mai",6:"Juni",7:"Juli",8:"August",9:"September",10:"Oktober",11:"November",12:"Dezember"}
MONTHS_FR   = {1:"janvier",2:"février",3:"mars",4:"avril",5:"mai",6:"juin",7:"juillet",8:"août",9:"septembre",10:"octobre",11:"novembre",12:"décembre"}
MONTHS_IT   = {1:"gennaio",2:"febbraio",3:"marzo",4:"aprile",5:"maggio",6:"giugno",7:"luglio",8:"agosto",9:"settembre",10:"ottobre",11:"novembre",12:"dicembre"}
MONTHS_EN   = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
WEEKDAYS_DE = {0:"Montag",1:"Dienstag",2:"Mittwoch",3:"Donnerstag",4:"Freitag",5:"Samstag",6:"Sonntag"}
WEEKDAYS_FR = {0:"Lundi",1:"Mardi",2:"Mercredi",3:"Jeudi",4:"Vendredi",5:"Samedi",6:"Dimanche"}
WEEKDAYS_IT = {0:"Lunedì",1:"Martedì",2:"Mercoledì",3:"Giovedì",4:"Venerdì",5:"Sabato",6:"Domenica"}
WEEKDAYS_EN = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}

def get_today_day():
    return DAY_MAP[datetime.today().weekday()]

def format_days(days_str):
    if not days_str or pd.isna(days_str): return "—"
    days = [d.strip() for d in str(days_str).split(",")]
    if days == DAYS_ALL: return "Täglich"
    if days == ["Mo","Di","Mi","Do","Fr"]: return "Mo–Fr"
    return ", ".join(days)

def med_due_today(days_str):
    if not days_str or pd.isna(days_str): return False
    return get_today_day() in [d.strip() for d in str(days_str).split(",")]

def is_confirmed(val):
    return str(val).strip().lower() in ["true","1","yes"]

def intake_exists_today(medication_id):
    df = st.session_state["intakes_df"]
    if df.empty: return False
    today = date.today().isoformat()
    return not df[(df["medication_id"] == medication_id) & (df["date"] == today)].empty

def next_id(df):
    if df.empty or "id" not in df.columns: return 1
    return int(df["id"].max()) + 1

def save_intake(medication_id, med_name, intake_date, intake_time, confirmed, note):
    dm  = st.session_state["data_manager"]
    df  = st.session_state["intakes_df"]
    new = pd.DataFrame([{"id": next_id(df), "medication_id": medication_id,
                          "medication_name": med_name, "date": intake_date.isoformat(),
                          "time": intake_time, "confirmed": confirmed,
                          "note": note, "created_at": pd.Timestamp.now()}])
    updated = pd.concat([df, new], ignore_index=True)
    st.session_state["intakes_df"] = updated
    dm.save_user_data(updated, "intakes.csv")

def classify_bp(sys, dia):
    if sys < 100 or dia < 60:     return "Hypotonie",        "status-hypo"
    if sys >= 180 or dia >= 110:  return "Hypertonie Grad 3","status-crit"
    if sys >= 160 or dia >= 100:  return "Hypertonie Grad 2","status-crit"
    if sys >= 140 or dia >= 90:   return "Hypertonie Grad 1","status-warn"
    if sys >= 130 or dia >= 85:   return "Hoch-normal",       "status-warn"
    if sys >= 120 or dia >= 80:   return "Normal",            "status-ok"
    return "Optimal", "status-ok"

def classify_bs(value):
    if value < 3.0:   return "Kritisch tief",  "status-crit"
    if value < 3.9:   return "Auffällig tief", "status-warn"
    if value <= 5.5:  return "Normal",          "status-ok"
    if value < 7.0:   return "Auffällig hoch", "status-warn"
    return "Kritisch hoch", "status-crit"

def compute_streak():
    """
    Berechnet den Streak: wie viele Tage in Folge (inkl. heute)
    alle fälligen Medikamente bestätigt wurden.
    """
    df   = st.session_state["intakes_df"]
    meds = st.session_state["medications_df"]
    if df.empty or meds.empty: return 0

    streak     = 0
    check_date = date.today()  # Heute miteinbeziehen

    for _ in range(365):
        day_name  = DAY_MAP[check_date.weekday()]
        due_meds  = meds[meds["days"].apply(
            lambda d: day_name in [x.strip() for x in str(d).split(",")]
            if pd.notna(d) else False
        )]
        if due_meds.empty:
            check_date -= timedelta(days=1)
            continue

        day_intakes = df[df["date"].astype(str) == check_date.isoformat()]
        all_confirmed = all(
            not day_intakes[
                (day_intakes["medication_id"] == mid) &
                (day_intakes["confirmed"].apply(is_confirmed))
            ].empty
            for mid in due_meds["id"]
        )
        if all_confirmed:
            streak    += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak

def compute_trend(df, value_col, days=7):
    if df is None or df.empty or len(df) < 2: return None
    df2 = df.copy()
    df2["date_dt"] = pd.to_datetime(df2["date"], errors="coerce")
    recent = df2.sort_values("date_dt").tail(days)
    if len(recent) < 2: return None
    mid  = len(recent) // 2
    avg1 = recent.head(mid)[value_col].mean()
    avg2 = recent.tail(mid)[value_col].mean()
    diff = avg2 - avg1
    threshold = recent[value_col].std() * 0.3 if recent[value_col].std() > 0 else 1
    if abs(diff) < threshold: return "stable"
    return "up" if diff > 0 else "down"

def trend_html(direction, good="down"):
    if not direction: return ""
    icons  = {"up":"↑","down":"↓","stable":"→"}
    labels = {"up": t("dashboard_trend_up"), "down": t("dashboard_trend_down"), "stable": t("dashboard_trend_stable")}
    colors = {
        "up":     "#15803d" if good == "up"   else "#b91c1c",
        "down":   "#15803d" if good == "down" else "#b91c1c",
        "stable": "#6b7280"
    }
    return f'<span style="font-size:12px;font-weight:600;color:{colors[direction]}">{labels[direction]}</span>'

# ── Daten ─────────────────────────────────────────────────────────────────────
meds_df    = st.session_state["medications_df"]
intakes_df = st.session_state["intakes_df"]
bp_df      = st.session_state["blood_pressure_df"]
bs_df      = st.session_state["blood_sugar_df"]
today_iso  = date.today().isoformat()
today_dt   = datetime.today()
lang       = st.session_state.get("language", "de")

# ── Begrüssung ────────────────────────────────────────────────────────────────
hour = today_dt.hour
greet_key = "dashboard_greeting_morning" if hour < 12 else ("dashboard_greeting_noon" if hour < 17 else "dashboard_greeting_evening")

months_map   = {"de":MONTHS_DE,"fr":MONTHS_FR,"it":MONTHS_IT,"en":MONTHS_EN}
weekdays_map = {"de":WEEKDAYS_DE,"fr":WEEKDAYS_FR,"it":WEEKDAYS_IT,"en":WEEKDAYS_EN}
month_name   = months_map.get(lang, MONTHS_DE)[today_dt.month]
weekday_name = weekdays_map.get(lang, WEEKDAYS_DE)[today_dt.weekday()]
date_label   = f"{weekday_name}, {today_dt.day}. {month_name} {today_dt.year}"

profile   = st.session_state.get("profile", {})
firstname = profile.get("firstname","")
name_part = f", {firstname}!" if firstname else "!"

st.markdown(f"## 👋 {t(greet_key)}{name_part}")
st.markdown(f'<p style="color:#6b7280;margin-top:-0.5rem;margin-bottom:1rem">{date_label} — {t("dashboard_subtitle")}</p>', unsafe_allow_html=True)

# ── Streak berechnen (wird in Metric-Karte angezeigt) ─────────────────────────
streak = compute_streak()

# ── Streak-Banner ─────────────────────────────────────────────────────────────
if streak > 0:
    day_word = "Tag" if streak == 1 else "Tage"
    st.markdown(f"""
    <div style="background:{theme['gradient']};border-radius:16px;padding:1rem 1.5rem;
                color:white;display:flex;align-items:center;gap:16px;margin-bottom:1rem">
        <div style="font-size:2.5rem;font-weight:700;line-height:1">{streak}</div>
        <div>
            <div style="font-size:15px;font-weight:600">🔥 {t('dashboard_streak')}</div>
            <div style="font-size:12px;opacity:0.85">{streak} {day_word} in Folge alle Medikamente eingenommen</div>
        </div>
        <div style="margin-left:auto;font-size:2rem">{'🔥' * min(streak, 5)}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Metriken ──────────────────────────────────────────────────────────────────
todays_meds = meds_df[meds_df["days"].apply(med_due_today)] if not meds_df.empty else pd.DataFrame()
taken_today = sum(1 for _, r in todays_meds.iterrows() if intake_exists_today(r["id"]))
total_today = len(todays_meds)
pct_today   = int(taken_today / total_today * 100) if total_today > 0 else 0

week_count = 0
if not intakes_df.empty:
    df_w = intakes_df.copy()
    df_w["date_dt"] = pd.to_datetime(df_w["date"], errors="coerce")
    week_count = int((df_w["date_dt"] >= pd.Timestamp.today() - pd.Timedelta(days=6)).sum())

streak_color = theme["primary"]
streak_sub   = f"🔥 {streak} Tag{'e' if streak != 1 else ''} in Folge" if streak > 0 else t("no_streak")

st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:1.25rem">
  <div style="background:{theme['metric_bg']};border:1px solid {theme['border']};border-radius:14px;padding:1rem 1.1rem">
    <div style="font-size:12px;color:#6b7280;margin-bottom:4px">💊 {t('dashboard_medications')}</div>
    <div style="font-size:24px;font-weight:700;color:#111827">{len(meds_df)}</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:2px">aktiv geplant</div>
  </div>
  <div style="background:{theme['metric_bg']};border:1px solid {theme['border']};border-radius:14px;padding:1rem 1.1rem">
    <div style="font-size:12px;color:#6b7280;margin-bottom:4px">✅ {t('dashboard_taken_today')}</div>
    <div style="font-size:24px;font-weight:700;color:#111827">{taken_today}/{total_today}</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:2px">{pct_today}% erledigt</div>
  </div>
  <div style="background:{theme['metric_bg']};border:1px solid {theme['border']};border-radius:14px;padding:1rem 1.1rem">
    <div style="font-size:12px;color:#6b7280;margin-bottom:4px">📅 {t('dashboard_this_week')}</div>
    <div style="font-size:24px;font-weight:700;color:#111827">{week_count}</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:2px">Einnahmen erfasst</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Erinnerungs-Banner ────────────────────────────────────────────────────────
if not todays_meds.empty:
    for _, med in todays_meds.iterrows():
        if not intake_exists_today(med["id"]):
            st.markdown(
                f'<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:12px;'
                f'padding:0.65rem 1rem;font-size:13px;color:#92400e;'
                f'display:flex;align-items:center;gap:8px;margin-bottom:0.4rem">'
                f'⏰ <strong>{e(str(med["name"]))}</strong> ist heute um {e(str(med["time"]))} Uhr fällig – noch nicht bestätigt.</div>',
                unsafe_allow_html=True
            )

st.divider()

# ── Heutige Medikamente ───────────────────────────────────────────────────────
st.markdown(f'<div style="font-size:13px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.65rem">{t("dashboard_planned")}</div>', unsafe_allow_html=True)

if meds_df.empty or todays_meds.empty:
    st.info(t("dashboard_none_planned"))
else:
    for _, med in todays_meds.sort_values("time").iterrows():
        already   = intake_exists_today(med["id"])
        note_text = str(med["note"]).strip() if pd.notna(med.get("note")) and str(med.get("note","")).strip() else t("no_note")
        icon_bg   = theme["pill_icon_bg"] if already else "#fffbeb"
        badge     = (f'<span style="background:#dcfce7;color:#15803d;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">{t("dashboard_confirmed")}</span>'
                     if already else
                     f'<span style="background:#fef3c7;color:#b45309;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">{t("dashboard_pending")}</span>')

        st.markdown(f"""
        <div style="background:{theme['card']};border:1px solid {theme['border']};border-radius:14px;
                    padding:0.85rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:12px">
            <div style="width:40px;height:40px;border-radius:10px;background:{icon_bg};
                        display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0">💊</div>
            <div style="flex:1;min-width:0">
                <div style="font-size:14px;font-weight:600;color:#111827">{e(str(med['name']))}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:1px">{e(format_days(med['days']))} · {e(note_text)}</div>
            </div>
            <div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px;flex-shrink:0">
                <span style="font-size:11px;font-weight:600;background:{theme['metric_bg']};color:#6b7280;padding:2px 8px;border-radius:7px;font-family:monospace">{e(str(med['time']))}</span>
                {badge}
            </div>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns([2,1])
        with c1:
            if not already:
                if st.button(t("dashboard_confirm"), key=f"confirm_{med['id']}", use_container_width=True):
                    save_intake(med["id"], med["name"], date.today(), str(med["time"]), True, "")
                    st.rerun()
        with c2:
            if st.button(t("edit"), key=f"edit_{med['id']}", use_container_width=True):
                st.session_state["editing_medication_id"] = int(med["id"])
                st.switch_page("views/medikamente.py")

st.divider()

# ── Einnahmetreue + Gesundheitswerte ─────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown(f'<div style="font-size:13px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.65rem">{t("dashboard_adherence")}</div>', unsafe_allow_html=True)
    if meds_df.empty or intakes_df.empty:
        st.info(t("no_data"))
    else:
        df_s = intakes_df.copy()
        df_s["confirmed_bool"] = df_s["confirmed"].apply(is_confirmed)
        for _, med in meds_df.iterrows():
            med_in = df_s[df_s["medication_id"] == med["id"]]
            if med_in.empty: continue
            total    = len(med_in)
            conf     = int(med_in["confirmed_bool"].sum())
            pct      = int(conf / total * 100)
            bar_col  = "#22c55e" if pct >= 80 else ("#f59e0b" if pct >= 50 else "#ef4444")
            pct_col  = "#15803d" if pct >= 80 else ("#b45309" if pct >= 50 else "#b91c1c")

            st.markdown(f"""
            <div style="background:{theme['card']};border:1px solid {theme['border']};border-radius:14px;
                        padding:0.9rem 1.1rem;margin-bottom:0.5rem;margin-top:-0.4rem">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px">
                    <div>
                        <div style="font-size:13px;font-weight:600;color:#111827">{e(str(med['name']))}</div>
                        <div style="font-size:11px;color:#9ca3af">{conf} von {total} bestätigt</div>
                    </div>
                    <div style="font-size:18px;font-weight:700;color:{pct_col}">{pct}%</div>
                </div>
                <div style="height:6px;background:{theme['border']};border-radius:99px;overflow:hidden">
                    <div style="height:100%;width:{pct}%;background:{bar_col};border-radius:99px"></div>
                </div>
            </div>""", unsafe_allow_html=True)

with col_right:
    st.markdown(f'<div style="font-size:13px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.65rem">{t("dashboard_health")}</div>', unsafe_allow_html=True)
    cmap = {"status-ok":"#15803d","status-warn":"#b45309","status-crit":"#b91c1c","status-hypo":"#6d28d9"}

    # Blutdruck — native Streamlit statt HTML
    if not bp_df.empty:
        bl       = bp_df.sort_values("date").iloc[-1]
        sv, dv   = int(bl["systolic"]), int(bl["diastolic"])
        bps, bpc = classify_bp(sv, dv)
        bpt      = compute_trend(bp_df.copy().rename(columns={"systolic":"value"}), "value")
        with st.container(border=True):
            st.caption("❤️ BLUTDRUCK")
            st.markdown(f"**{sv} / {dv}** mmHg")
            st.markdown(f'<span style="font-size:12px;font-weight:600;color:{cmap.get(bpc,"#6b7280")}">{e(bps)}</span>', unsafe_allow_html=True)
            t_str = trend_html(bpt, good="down")
            if t_str:
                st.markdown(t_str, unsafe_allow_html=True)
            st.caption(f"gemessen: {str(bl['date'])[:10]}")
    else:
        with st.container(border=True):
            st.caption("❤️ BLUTDRUCK")
            st.markdown(t("no_entry"))

    # Blutzucker — native Streamlit statt HTML
    if not bs_df.empty:
        bl2      = bs_df.sort_values("date").iloc[-1]
        bsv      = float(bl2["value"])
        bss, bsc = classify_bs(bsv)
        bst      = compute_trend(bs_df.copy(), "value")
        with st.container(border=True):
            st.caption("🩸 NÜCHTERNBLUTZUCKER")
            st.markdown(f"**{bsv:.1f}** mmol/l")
            st.markdown(f'<span style="font-size:12px;font-weight:600;color:{cmap.get(bsc,"#6b7280")}">{e(bss)}</span>', unsafe_allow_html=True)
            t_str = trend_html(bst, good="stable")
            if t_str:
                st.markdown(t_str, unsafe_allow_html=True)
            st.caption(f"gemessen: {str(bl2['date'])[:10]}")
    else:
        with st.container(border=True):
            st.caption("🩸 NÜCHTERNBLUTZUCKER")
            st.markdown(t("no_entry"))