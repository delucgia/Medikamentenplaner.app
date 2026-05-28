"""
views/dashboard.py
Tagesübersicht: Begrüssung, Streak-Banner, Metriken, heutige Medikamente,
Einnahmetreue, Trend-Analyse, letzte Gesundheitswerte.
Vollständig übersetzt via utils/translations.py
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from utils.translations import t
from utils.themes import inject_theme, get_theme
from utils.vita import mascot_svg, get_vita_mood
from functions.format_helpers import e, is_confirmed, format_days, WEEKDAYS_DE_SHORT
from functions.data_helpers import save_intakes, save_intake, med_due_today, intake_exists_today, compute_streak, compute_trend
from functions.health_classifications import classify_bp, classify_bs, bp_color, bs_color

inject_theme()
theme = get_theme()



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

# ── Streak + Vita ────────────────────────────────────────────────────────────
streak = compute_streak()

# Letzte Gesundheitswerte für Vita-Stimmung
bp_status_str = ""
bs_status_str = ""
if not bp_df.empty:
    bl = bp_df.sort_values("date").iloc[-1]
    bp_status_str, _ = classify_bp(int(bl["systolic"]), int(bl["diastolic"]))
if not bs_df.empty:
    bl2 = bs_df.sort_values("date").iloc[-1]
    bs_status_str, _ = classify_bs(float(bl2["value"]))

# todays_meds hier berechnen damit Vita es nutzen kann
todays_meds = meds_df[meds_df["days"].apply(med_due_today)] if not meds_df.empty else pd.DataFrame()
has_pending = any(
    not intake_exists_today(r["id"]) for _, r in todays_meds.iterrows()
) if not todays_meds.empty else False

vita_mood, vita_msg = get_vita_mood(
    hour=today_dt.hour,
    streak=streak,
    has_pending=has_pending,
    bp_status=bp_status_str,
    bs_status=bs_status_str,
)
vita_html = mascot_svg(vita_mood, size=90)

col_greet, col_vita = st.columns([3, 1])
with col_greet:
    st.markdown(f"## 👋 {t(greeting_key)}{name_part}")
    st.markdown(
        f'<p style="color:#6b7280;margin-top:-0.5rem;margin-bottom:0.5rem">'
        f'{date_label} — {t("dashboard_subtitle")}</p>',
        unsafe_allow_html=True
    )
    # Vita Sprechblase
    st.markdown(
        f'<div style="background:{theme["metric_bg"]};border:1px solid {theme["border"]};'
        f'border-radius:14px;border-bottom-left-radius:4px;padding:0.65rem 1rem;'
        f'font-size:13px;color:#374151;margin-bottom:1rem;display:inline-block;max-width:95%">'
        f'{vita_msg}</div>',
        unsafe_allow_html=True
    )
with col_vita:
    st.markdown(
        f'<div style="display:flex;justify-content:center;align-items:flex-end;height:100%">'
        f'{vita_html}</div>',
        unsafe_allow_html=True
    )

if streak > 0:
    st.markdown(
        f'<div style="background:{theme["gradient"]};border-radius:16px;padding:1rem 1.5rem;'
        f'color:white;display:flex;align-items:center;gap:16px;margin-bottom:1rem">'
        f'<div style="font-size:2.5rem;font-weight:700;line-height:1">{streak}</div>'
        f'<div><div style="font-size:15px;font-weight:600">🔥 {t("dashboard_streak")}</div>'
        f'<div style="font-size:12px;opacity:0.85">{streak} {t("streak_days_label")}</div></div>'
        f'<div style="margin-left:auto;font-size:2rem">{"🔥" * min(streak, 5)}</div></div>',
        unsafe_allow_html=True
    )

# ── Metriken ──────────────────────────────────────────────────────────────────
# todays_meds wurde bereits oben für Vita berechnet
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
        bp_status, _ = classify_bp(sys_val, dia_val)
        bp_trend = compute_trend(bp_df.copy().rename(columns={"systolic": "value"}), "value")
        bp_trend_str = trend_html(bp_trend, good="down")

        with st.container(border=True):
            st.caption(f"❤️ {t('health_bp').upper()}")
            st.markdown(f"**{sys_val} / {dia_val}** mmHg")
            st.markdown(
                f'<span style="font-size:12px;font-weight:600;color:{bp_color(bp_status)}">'
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
        bs_status, _ = classify_bs(bs_val)
        bs_trend = compute_trend(bs_df.copy(), "value")
        bs_trend_str = trend_html(bs_trend, good="stable")

        with st.container(border=True):
            st.caption(f"🩸 {t('health_bs').upper()}")
            st.markdown(f"**{bs_val:.1f}** mmol/l")
            st.markdown(
                f'<span style="font-size:12px;font-weight:600;color:{bs_color(bs_status)}">'
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