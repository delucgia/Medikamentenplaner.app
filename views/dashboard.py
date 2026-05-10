"""
views/dashboard.py
Tagesübersicht: Begrüssung, Streak-Banner, Metriken, heutige Medikamente,
Einnahmetreue, Trend-Analyse, letzte Gesundheitswerte.
Vollständig übersetzt via utils/translations.py
"""

import html
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from utils.translations import t
from utils.themes import inject_theme, get_theme

inject_theme()
theme = get_theme()


def e(text):
    return html.escape(str(text))


def get_today_day_short():
    """Gibt das heutige Wochentag-Kürzel in der aktuellen Sprache zurück."""
    shorts = t("weekdays_short").split(",")
    return shorts[datetime.today().weekday()]


def format_days(days_str):
    """Formatiert den days-String (DE-intern) in die aktuelle Sprache."""
    if not days_str or pd.isna(days_str):
        return "—"
    days = [d.strip() for d in str(days_str).split(",")]
    all_days_de = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    if days == all_days_de:
        return t("daily")
    if days == ["Mo", "Di", "Mi", "Do", "Fr"]:
        return t("mo_fr")
    shorts_de = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    shorts_translated = t("weekdays_short").split(",")
    mapped = [
        shorts_translated[shorts_de.index(d)] if d in shorts_de else d
        for d in days
    ]
    return ", ".join(mapped)


def med_due_today(days_str):
    """Prüft ob ein Medikament heute fällig ist (DE-Kürzel intern)."""
    if not days_str or pd.isna(days_str):
        return False
    today_de = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][datetime.today().weekday()]
    return today_de in [d.strip() for d in str(days_str).split(",")]


def is_confirmed(val):
    return str(val).strip().lower() in ["true", "1", "yes"]


def intake_exists_today(medication_id):
    """Prüft ob für dieses Medikament heute bereits eine Einnahme existiert."""
    df = st.session_state["intakes_df"]
    if df.empty:
        return False
    today = date.today().isoformat()
    return not df[
        (df["medication_id"] == medication_id) & (df["date"] == today)
    ].empty


def next_id(df):
    if df.empty or "id" not in df.columns:
        return 1
    return int(df["id"].max()) + 1


def save_intake(medication_id, med_name, intake_date, intake_time, confirmed, note):
    """Speichert eine neue Einnahme."""
    data_manager = st.session_state["data_manager"]
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
    data_manager.save_user_data(updated, "intakes.csv")


def classify_bp(systolic, diastolic):
    """Klassifiziert einen Blutdruckwert."""
    if systolic < 100 or diastolic < 60:
        return t("bp_hypo"), "status-hypo"
    if systolic >= 180 or diastolic >= 110:
        return t("bp_hyp3"), "status-crit"
    if systolic >= 160 or diastolic >= 100:
        return t("bp_hyp2"), "status-crit"
    if systolic >= 140 or diastolic >= 90:
        return t("bp_hyp1"), "status-warn"
    if systolic >= 130 or diastolic >= 85:
        return t("bp_highnorm"), "status-warn"
    if systolic >= 120 or diastolic >= 80:
        return t("bp_normal"), "status-ok"
    return t("bp_optimal"), "status-ok"


def classify_bs(value):
    """Klassifiziert einen Blutzuckerwert."""
    if value < 3.0:
        return t("bs_crit_low"), "status-crit"
    if value < 3.9:
        return t("bs_warn_low"), "status-warn"
    if value <= 5.5:
        return t("bs_normal"), "status-ok"
    if value < 7.0:
        return t("bs_warn_high"), "status-warn"
    return t("bs_crit_high"), "status-crit"


def compute_streak():
    """Berechnet den Streak (inkl. heute)."""
    df = st.session_state["intakes_df"]
    meds = st.session_state["medications_df"]
    if df.empty or meds.empty:
        return 0
    shorts_de = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    streak = 0
    check_date = date.today()
    for _ in range(365):
        day_name = shorts_de[check_date.weekday()]
        due_meds = meds[meds["days"].apply(
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
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak


def compute_trend(df, value_col, days=7):
    """Berechnet ob ein Wert steigend, sinkend oder stabil ist."""
    if df is None or df.empty or len(df) < 2:
        return None
    df2 = df.copy()
    df2["date_dt"] = pd.to_datetime(df2["date"], errors="coerce")
    recent = df2.sort_values("date_dt").tail(days)
    if len(recent) < 2:
        return None
    mid = len(recent) // 2
    avg1 = recent.head(mid)[value_col].mean()
    avg2 = recent.tail(mid)[value_col].mean()
    diff = avg2 - avg1
    threshold = recent[value_col].std() * 0.3 if recent[value_col].std() > 0 else 1
    if abs(diff) < threshold:
        return "stable"
    return "up" if diff > 0 else "down"


def trend_html(direction, good="down"):
    """Gibt einen farbigen Trend-HTML-Span zurück."""
    if not direction:
        return ""
    labels = {
        "up": t("dashboard_trend_up"),
        "down": t("dashboard_trend_down"),
        "stable": t("dashboard_trend_stable"),
    }
    colors = {
        "up":     "#15803d" if good == "up"   else "#b91c1c",
        "down":   "#15803d" if good == "down" else "#b91c1c",
        "stable": "#6b7280",
    }
    return f'<span style="font-size:12px;font-weight:600;color:{colors[direction]}">{labels[direction]}</span>'


# ── Daten laden ───────────────────────────────────────────────────────────────
meds_df    = st.session_state["medications_df"]
intakes_df = st.session_state["intakes_df"]
bp_df      = st.session_state["blood_pressure_df"]
bs_df      = st.session_state["blood_sugar_df"]
today_iso  = date.today().isoformat()
today_dt   = datetime.today()
lang       = st.session_state.get("language", "de")

# ── Begrüssung ────────────────────────────────────────────────────────────────
hour = today_dt.hour
if hour < 12:
    greeting_key = "dashboard_greeting_morning"
elif hour < 17:
    greeting_key = "dashboard_greeting_noon"
else:
    greeting_key = "dashboard_greeting_evening"

months_list   = t("months").split(",")
weekdays_list = t("weekdays_long").split(",")
date_label = f"{weekdays_list[today_dt.weekday()]}, {today_dt.day}. {months_list[today_dt.month - 1]} {today_dt.year}"

profile   = st.session_state.get("profile", {})
firstname = profile.get("firstname", "")
name_part = f", {firstname}!" if firstname else "!"

st.markdown(f"## 👋 {t(greeting_key)}{name_part}")
st.markdown(
    f'<p style="color:#6b7280;margin-top:-0.5rem;margin-bottom:1rem">'
    f'{date_label} — {t("dashboard_subtitle")}</p>',
    unsafe_allow_html=True
)

# ── Streak-Banner ─────────────────────────────────────────────────────────────
streak = compute_streak()
if streak > 0:
    st.markdown(f"""
    <div style="background:{theme['gradient']};border-radius:16px;padding:1rem 1.5rem;
                color:white;display:flex;align-items:center;gap:16px;margin-bottom:1rem">
        <div style="font-size:2.5rem;font-weight:700;line-height:1">{streak}</div>
        <div>
            <div style="font-size:15px;font-weight:600">🔥 {t('dashboard_streak')}</div>
            <div style="font-size:12px;opacity:0.85">{streak} {t('streak_days_label')}</div>
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
    df_week = intakes_df.copy()
    df_week["date_dt"] = pd.to_datetime(df_week["date"], errors="coerce")
    week_count = int((df_week["date_dt"] >= pd.Timestamp.today() - pd.Timedelta(days=6)).sum())

st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:1.25rem">
  <div style="background:{theme['metric_bg']};border:1px solid {theme['border']};border-radius:14px;padding:1rem 1.1rem">
    <div style="font-size:12px;color:#6b7280;margin-bottom:4px">💊 {t('dashboard_medications')}</div>
    <div style="font-size:24px;font-weight:700;color:#111827">{len(meds_df)}</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:2px">{t('active_planned')}</div>
  </div>
  <div style="background:{theme['metric_bg']};border:1px solid {theme['border']};border-radius:14px;padding:1rem 1.1rem">
    <div style="font-size:12px;color:#6b7280;margin-bottom:4px">✅ {t('dashboard_taken_today')}</div>
    <div style="font-size:24px;font-weight:700;color:#111827">{taken_today}/{total_today}</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:2px">{pct_today}% {t('adherence_confirmed')}</div>
  </div>
  <div style="background:{theme['metric_bg']};border:1px solid {theme['border']};border-radius:14px;padding:1rem 1.1rem">
    <div style="font-size:12px;color:#6b7280;margin-bottom:4px">📅 {t('dashboard_this_week')}</div>
    <div style="font-size:24px;font-weight:700;color:#111827">{week_count}</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:2px">{t('entries_this_week')}</div>
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
                f'⏰ <strong>{e(str(med["name"]))}</strong> '
                f'{t("pending_reminder")} {e(str(med["time"]))} {t("pending_reminder2")}</div>',
                unsafe_allow_html=True
            )

st.divider()

# ── Heutige Medikamente ───────────────────────────────────────────────────────
st.markdown(
    f'<div style="font-size:13px;font-weight:600;color:#6b7280;text-transform:uppercase;'
    f'letter-spacing:0.05em;margin-bottom:0.65rem">{t("dashboard_planned")}</div>',
    unsafe_allow_html=True
)

if meds_df.empty or todays_meds.empty:
    st.info(t("dashboard_none_planned"))
else:
    for _, med in todays_meds.sort_values("time").iterrows():
        already   = intake_exists_today(med["id"])
        note_text = (
            str(med["note"]).strip()
            if pd.notna(med.get("note")) and str(med.get("note", "")).strip()
            else t("no_note")
        )
        icon_bg = theme["pill_icon_bg"] if already else "#fffbeb"

        if already:
            badge_html = (
                f'<span style="background:#dcfce7;color:#15803d;padding:2px 8px;'
                f'border-radius:999px;font-size:11px;font-weight:600">'
                f'{t("dashboard_confirmed")}</span>'
            )
        else:
            badge_html = (
                f'<span style="background:#fef3c7;color:#b45309;padding:2px 8px;'
                f'border-radius:999px;font-size:11px;font-weight:600">'
                f'{t("dashboard_pending")}</span>'
            )

        st.markdown(f"""
        <div style="background:{theme['card']};border:1px solid {theme['border']};border-radius:14px;
                    padding:0.85rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:12px">
            <div style="width:40px;height:40px;border-radius:10px;background:{icon_bg};
                        display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0">💊</div>
            <div style="flex:1;min-width:0">
                <div style="font-size:14px;font-weight:600;color:#111827">{e(str(med['name']))}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:1px">
                    {e(format_days(med['days']))} · {e(note_text)}
                </div>
            </div>
            <div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px;flex-shrink:0">
                <span style="font-size:11px;font-weight:600;background:{theme['metric_bg']};
                             color:#6b7280;padding:2px 8px;border-radius:7px;font-family:monospace">
                    {e(str(med['time']))}
                </span>
                {badge_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            if not already:
                if st.button(
                    t("dashboard_confirm"),
                    key=f"confirm_{med['id']}",
                    use_container_width=True
                ):
                    save_intake(med["id"], med["name"], date.today(), str(med["time"]), True, "")
                    st.rerun()
        with col2:
            if st.button(
                t('edit'),
                key=f"edit_{med['id']}",
                use_container_width=True
            ):
                st.session_state["editing_medication_id"] = int(med["id"])
                st.switch_page("views/medikamente.py")

st.divider()

# ── Einnahmetreue + Gesundheitswerte ─────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown(
        f'<div style="font-size:13px;font-weight:600;color:#6b7280;text-transform:uppercase;'
        f'letter-spacing:0.05em;margin-bottom:0.65rem">{t("dashboard_adherence")}</div>',
        unsafe_allow_html=True
    )

    if meds_df.empty or intakes_df.empty:
        st.info(t("no_data"))
    else:
        df_adhere = intakes_df.copy()
        df_adhere["confirmed_bool"] = df_adhere["confirmed"].apply(is_confirmed)

        for _, med in meds_df.iterrows():
            med_intakes = df_adhere[df_adhere["medication_id"] == med["id"]]
            if med_intakes.empty:
                continue
            total    = len(med_intakes)
            confirmed_count = int(med_intakes["confirmed_bool"].sum())
            pct      = int(confirmed_count / total * 100)

            if pct >= 80:
                bar_color = "#22c55e"
                pct_color = "#15803d"
            elif pct >= 50:
                bar_color = "#f59e0b"
                pct_color = "#b45309"
            else:
                bar_color = "#ef4444"
                pct_color = "#b91c1c"

            st.markdown(f"""
            <div style="background:{theme['card']};border:1px solid {theme['border']};border-radius:14px;
                        padding:0.9rem 1.1rem;margin-bottom:0.5rem">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px">
                    <div>
                        <div style="font-size:13px;font-weight:600;color:#111827">{e(str(med['name']))}</div>
                        <div style="font-size:11px;color:#9ca3af">
                            {confirmed_count} {t('adherence_of')} {total} {t('adherence_confirmed')}
                        </div>
                    </div>
                    <div style="font-size:18px;font-weight:700;color:{pct_color}">{pct}%</div>
                </div>
                <div style="height:6px;background:{theme['border']};border-radius:99px;overflow:hidden">
                    <div style="height:100%;width:{pct}%;background:{bar_color};border-radius:99px"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.markdown(
        f'<div style="font-size:13px;font-weight:600;color:#6b7280;text-transform:uppercase;'
        f'letter-spacing:0.05em;margin-bottom:0.65rem">{t("dashboard_health")}</div>',
        unsafe_allow_html=True
    )

    css_color_map = {
        "status-ok":   "#15803d",
        "status-warn": "#b45309",
        "status-crit": "#b91c1c",
        "status-hypo": "#6d28d9",
    }

    # Blutdruck
    if not bp_df.empty:
        bp_last  = bp_df.sort_values("date").iloc[-1]
        sys_val  = int(bp_last["systolic"])
        dia_val  = int(bp_last["diastolic"])
        bp_status, bp_css = classify_bp(sys_val, dia_val)
        bp_trend = compute_trend(bp_df.copy().rename(columns={"systolic": "value"}), "value")
        bp_trend_str = trend_html(bp_trend, good="down")

        with st.container(border=True):
            st.caption(f"❤️ {t('health_bp').upper()}")
            st.markdown(f"**{sys_val} / {dia_val}** mmHg")
            st.markdown(
                f'<span style="font-size:12px;font-weight:600;color:{css_color_map.get(bp_css, "#6b7280")}">'
                f'{e(bp_status)}</span>',
                unsafe_allow_html=True
            )
            if bp_trend_str:
                st.markdown(bp_trend_str, unsafe_allow_html=True)
            st.caption(f"{t('measured_on')}: {str(bp_last['date'])[:10]}")
    else:
        with st.container(border=True):
            st.caption(f"❤️ {t('health_bp').upper()}")
            st.markdown(t("no_entry_yet"))

    # Blutzucker
    if not bs_df.empty:
        bs_last  = bs_df.sort_values("date").iloc[-1]
        bs_val   = float(bs_last["value"])
        bs_status, bs_css = classify_bs(bs_val)
        bs_trend = compute_trend(bs_df.copy(), "value")
        bs_trend_str = trend_html(bs_trend, good="stable")

        with st.container(border=True):
            st.caption(f"🩸 {t('health_bs').upper()}")
            st.markdown(f"**{bs_val:.1f}** mmol/l")
            st.markdown(
                f'<span style="font-size:12px;font-weight:600;color:{css_color_map.get(bs_css, "#6b7280")}">'
                f'{e(bs_status)}</span>',
                unsafe_allow_html=True
            )
            if bs_trend_str:
                st.markdown(bs_trend_str, unsafe_allow_html=True)
            st.caption(f"{t('measured_on')}: {str(bs_last['date'])[:10]}")
    else:
        with st.container(border=True):
            st.caption(f"🩸 {t('health_bs').upper()}")
            st.markdown(t("no_entry_yet"))