"""
views/verlauf.py
Einnahmeverlauf: Gruppiert nach Monat → Woche → Tag.
Vollständig übersetzt via utils/translations.py
"""

import html
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, time as dtime
from utils.translations import t
from utils.themes import get_theme

theme = get_theme()


def e(text):
    return html.escape(str(text))


DAYS_ALL = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def get_weekday_name(weekday_int):
    """Gibt den übersetzten Wochentagnamen zurück."""
    return t("weekdays_long").split(",")[weekday_int]


def get_month_name(month_int):
    """Gibt den übersetzten Monatsnamen zurück."""
    return t("months").split(",")[month_int - 1]


def format_days(days_str):
    """Formatiert den days-String (DE-intern) in die aktuelle Sprache."""
    if not days_str or pd.isna(days_str):
        return "—"
    days = [d.strip() for d in str(days_str).split(",")]
    if days == DAYS_ALL:
        return t("daily")
    if days == ["Mo", "Di", "Mi", "Do", "Fr"]:
        return t("mo_fr")
    shorts_de         = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    shorts_translated = t("weekdays_short").split(",")
    mapped = [
        shorts_translated[shorts_de.index(d)] if d in shorts_de else d
        for d in days
    ]
    return ", ".join(mapped)


def is_confirmed(val):
    return str(val).strip().lower() in ["true", "1", "yes"]


def next_id(df):
    if df.empty or "id" not in df.columns:
        return 1
    return int(df["id"].max()) + 1


def save_intakes():
    st.session_state["data_manager"].save_user_data(
        st.session_state["intakes_df"], "intakes.csv"
    )


def get_week_range(dt):
    monday = dt - timedelta(days=dt.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


# ── Seite ─────────────────────────────────────────────────────────────────────
st.markdown(f"## 📋 {t('history_title')}")
st.markdown(
    f'<p style="color:#6b7280">{t("history_subtitle")}</p>',
    unsafe_allow_html=True
)
st.write("")

intakes_df = st.session_state["intakes_df"]
meds_df    = st.session_state["medications_df"]

# ── PDF-Export ─────────────────────────────────────────────────────────────────
col_title, col_pdf = st.columns([3, 1])
with col_pdf:
    if not intakes_df.empty:
        if st.button("📄 PDF", use_container_width=True):
            try:
                from utils.pdf_export import generate_pdf
                profile   = st.session_state.get("profile", {})
                pdf_bytes = generate_pdf(
                    profile=profile,
                    include_intakes=True,
                    intakes_df=intakes_df
                )
                st.download_button(
                    label=t("pdf_download"),
                    data=pdf_bytes,
                    file_name="meditrack_verlauf.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as ex:
                st.error(f"{ex}")

tab_history, tab_stats, tab_form = st.tabs([
    f"📅 {t('history_title')}",
    f"📊 {t('history_stats')}",
    f"➕ {t('history_form')}"
])

# ── Tab 1: Verlauf ────────────────────────────────────────────────────────────
with tab_history:
    if intakes_df.empty:
        st.info(t("history_none"))
    else:
        df = intakes_df.copy()
        df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date_parsed"]).sort_values("date_parsed", ascending=False)

        with st.expander(f"🔍 {t('filter_label')}", expanded=False):
            col_from, col_to, col_med = st.columns([2, 2, 2])
            with col_from:
                filter_from = st.date_input(
                    t("history_from"),
                    value=date.today() - timedelta(days=29),
                    key="hf"
                )
            with col_to:
                filter_to = st.date_input(t("history_to"), value=date.today(), key="ht")
            with col_med:
                med_options = ["All"] + sorted(df["medication_name"].dropna().unique().tolist())
                filter_med  = st.selectbox(t("med_title"), options=med_options, key="hm")
            show_all = st.checkbox(t("show_all_label"), value=False)

        filtered = df.copy()
        if not show_all:
            filtered = filtered[
                (filtered["date_parsed"].dt.date >= filter_from) &
                (filtered["date_parsed"].dt.date <= filter_to)
            ]
        if filter_med != "All":
            filtered = filtered[filtered["medication_name"] == filter_med]

        st.caption(f"{len(filtered)} {t('entries_found')}")
        st.write("")

        if filtered.empty:
            st.info(t("no_intakes_period"))
        else:
            filtered["year_month"] = filtered["date_parsed"].dt.to_period("M")
            filtered["iso_week"]   = filtered["date_parsed"].dt.isocalendar().week.astype(int)
            filtered["iso_year"]   = filtered["date_parsed"].dt.isocalendar().year.astype(int)

            for year_month, month_group in filtered.groupby("year_month", sort=False):
                month_dt = year_month.to_timestamp()
                month_name = get_month_name(month_dt.month)
                entry_count = len(month_group)

                st.markdown(
                    f"### 📅 {month_name} {month_dt.year} &nbsp;"
                    f'<span style="font-size:13px;color:#9ca3af;font-weight:400">'
                    f'{entry_count} {t("intakes")}</span>',
                    unsafe_allow_html=True
                )

                for (iso_year, iso_week), week_group in month_group.groupby(
                    ["iso_year", "iso_week"], sort=False
                ):
                    first_day = week_group["date_parsed"].max().date()
                    monday, sunday = get_week_range(first_day)
                    week_label = (
                        f"{t('week_abbr')} {iso_week}  ·  "
                        f"{monday.strftime('%d. %b')} – {sunday.strftime('%d. %b')}"
                    )
                    st.markdown(
                        f'<div style="font-size:12px;font-weight:600;color:#6b7280;'
                        f'margin:0.5rem 0 0.3rem">{e(week_label)}</div>',
                        unsafe_allow_html=True
                    )

                    for day_date, day_group in week_group.groupby(
                        week_group["date_parsed"].dt.date, sort=False
                    ):
                        day_group      = day_group.sort_values("time")
                        weekday_name   = get_weekday_name(day_date.weekday())
                        day_count      = len(day_group)
                        intake_word    = t("intake") if day_count == 1 else t("intakes")

                        st.markdown(
                            f'<div style="font-size:13px;font-weight:600;color:#374151;'
                            f'margin:0.6rem 0 0.2rem;display:flex;align-items:center;gap:8px">'
                            f'{e(weekday_name)} '
                            f'<span style="font-size:12px;color:#9ca3af;font-weight:400">'
                            f'{day_date.strftime("%d.%m.%Y")}</span>'
                            f'<span style="font-size:11px;color:#9ca3af;margin-left:auto">'
                            f'{day_count} {intake_word}</span></div>',
                            unsafe_allow_html=True
                        )

                        for _, intake in day_group.iterrows():
                            confirmed = is_confirmed(intake.get("confirmed", False))
                            dot_color = "#22c55e" if confirmed else "#ef4444"

                            if confirmed:
                                badge_html = (
                                    f'<span style="background:#dcfce7;color:#15803d;'
                                    f'padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">'
                                    f'✓ {t("intake_confirmed")}</span>'
                                )
                            else:
                                badge_html = (
                                    f'<span style="background:#fee2e2;color:#b91c1c;'
                                    f'padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600">'
                                    f'✗ {t("intake_unconfirmed")}</span>'
                                )

                            note_text = (
                                str(intake["note"]).strip()
                                if pd.notna(intake.get("note")) and str(intake.get("note", "")).strip()
                                else ""
                            )
                            note_html = (
                                f'<div style="font-size:11px;color:#9ca3af;margin-top:1px">'
                                f'{e(note_text)}</div>'
                                if note_text else ""
                            )

                            card = (
                                f'<div style="background:white;border:1px solid {theme["border"]};border-radius:12px;padding:0.5rem 1rem;margin-bottom:0.3rem;display:flex;align-items:center;justify-content:space-between;gap:8px">'
                                f'<div style="display:flex;align-items:center;gap:8px">'
                                f'<div style="width:8px;height:8px;border-radius:50%;background:{dot_color};flex-shrink:0"></div>'
                                f'<div><div style="font-size:13px;font-weight:500;color:#111827">{e(str(intake["medication_name"]))}</div>{note_html}</div>'
                                f'</div>'
                                f'<div style="display:flex;align-items:center;gap:6px;flex-shrink:0">'
                                f'<span style="font-size:11px;font-weight:600;background:{theme["metric_bg"]};color:#6b7280;padding:2px 8px;border-radius:7px;font-family:monospace">{e(str(intake["time"]))}</span>'
                                f'{badge_html}'
                                f'</div>'
                                f'</div>'
                            )
                            st.markdown(card, unsafe_allow_html=True)

                            col_edit, col_del = st.columns(2)
                            with col_edit:
                                if st.button(
                                    f"✏️ {t('edit_intake')}",
                                    key=f"ei_{intake['id']}",
                                    use_container_width=True
                                ):
                                    st.session_state["editing_intake_id"] = int(intake["id"])
                                    st.rerun()
                            with col_del:
                                if st.button(
                                    f"🗑️ {t('delete_intake')}",
                                    key=f"di_{intake['id']}",
                                    use_container_width=True
                                ):
                                    st.session_state["intakes_df"] = intakes_df[
                                        intakes_df["id"] != intake["id"]
                                    ].reset_index(drop=True)
                                    save_intakes()
                                    st.success(t("intake_deleted"))
                                    st.rerun()

                st.divider()

# ── Tab 2: Statistik ──────────────────────────────────────────────────────────
with tab_stats:
    if intakes_df.empty or meds_df.empty:
        st.info(t("no_data"))
    else:
        df_stats = intakes_df.copy()
        df_stats["confirmed_bool"] = df_stats["confirmed"].apply(is_confirmed)

        total_count     = len(intakes_df)
        confirmed_count = int(df_stats["confirmed_bool"].sum())
        unconfirmed     = total_count - confirmed_count

        col1, col2, col3 = st.columns(3)
        col1.metric(f"📋 {t('stats_total')}",         total_count)
        col2.metric(f"✅ {t('stats_confirmed')}",      confirmed_count)
        col3.metric(f"❌ {t('stats_not_confirmed')}",  unconfirmed)

        st.divider()
        st.markdown(f"#### {t('adherence_per_med')}")
        st.caption(t("adherence_dot_hint"))
        st.write("")

        for _, med in meds_df.iterrows():
            med_intakes = df_stats[
                df_stats["medication_id"] == med["id"]
            ].sort_values("date")

            if med_intakes.empty:
                continue

            total    = len(med_intakes)
            conf     = int(med_intakes["confirmed_bool"].sum())
            pct      = int(conf / total * 100)
            last_d   = med_intakes["date"].iloc[-1]

            if pct >= 80:
                pct_color = "#15803d"
            elif pct >= 50:
                pct_color = "#b45309"
            else:
                pct_color = "#b91c1c"

            dots_html = "".join([
                f'<div style="width:9px;height:9px;border-radius:50%;flex-shrink:0;'
                f'background:{"#22c55e" if row["confirmed_bool"] else "#e5e7eb"}"></div>'
                for _, row in med_intakes.tail(30).iterrows()
            ])

            st.markdown(f"""
            <div style="background:white;border:1px solid {theme['border']};border-radius:14px;
                        padding:1rem 1.25rem;margin-bottom:0.6rem;
                        display:flex;align-items:center;justify-content:space-between;gap:1rem">
                <div style="flex:1">
                    <div style="font-weight:600;font-size:0.95rem;color:#111827;margin-bottom:0.2rem">
                        💊 {e(str(med['name']))}
                    </div>
                    <div style="font-size:0.8rem;color:#6b7280;margin-bottom:0.4rem">
                        {conf} {t('adherence_of')} {total} {t('adherence_confirmed')}
                        · {t('adherence_last')}: {e(str(last_d))}
                    </div>
                    <div style="display:flex;gap:4px;flex-wrap:wrap">{dots_html}</div>
                </div>
                <div style="font-size:1.5rem;font-weight:700;color:{pct_color};
                            min-width:52px;text-align:right">{pct}%</div>
            </div>
            """, unsafe_allow_html=True)

# ── Tab 3: Einnahme erfassen / bearbeiten ─────────────────────────────────────
with tab_form:
    if meds_df.empty:
        st.info(t("med_none"))
    else:
        editing_intake_id  = st.session_state.get("editing_intake_id")
        editing_intake_row = None
        if editing_intake_id is not None and not intakes_df.empty:
            matches = intakes_df[intakes_df["id"] == editing_intake_id]
            if not matches.empty:
                editing_intake_row = matches.iloc[0]

        if editing_intake_row is not None:
            st.markdown(f"**{t('editing_intake_of')}** {editing_intake_row['date']}")
            if st.button(f"↩️ {t('cancel_edit')}"):
                st.session_state["editing_intake_id"] = None
                st.rerun()

        # Medikament-Auswahl
        med_options    = {
            f"{row['name']} ({row['time']})": int(row["id"])
            for _, row in meds_df.iterrows()
        }
        option_labels  = list(med_options.keys())

        if editing_intake_row is not None:
            selected_label = next(
                (lbl for lbl, mid in med_options.items()
                 if mid == editing_intake_row["medication_id"]),
                option_labels[0]
            )
            default_index = option_labels.index(selected_label)
            default_date  = datetime.strptime(str(editing_intake_row["date"]), "%Y-%m-%d").date()
            default_time  = datetime.strptime(str(editing_intake_row["time"]), "%H:%M").time()
            default_conf  = is_confirmed(editing_intake_row.get("confirmed", True))
            default_note  = str(editing_intake_row["note"]) if pd.notna(editing_intake_row.get("note")) else ""
        else:
            default_index = 0
            default_date  = date.today()
            default_time  = dtime(8, 0)
            default_conf  = True
            default_note  = ""

        with st.form("intake_form", clear_on_submit=True):
            selected_med = st.selectbox(t("med_title"), options=option_labels, index=default_index)
            intake_date  = st.date_input(t("intake_date"), value=default_date)
            intake_time  = st.time_input(t("intake_time"), value=default_time, step=300)
            confirmed_cb = st.checkbox(t("intake_confirmed_cb"), value=default_conf)
            note_in      = st.text_area(t("intake_note"), value=default_note)
            submitted    = st.form_submit_button(t("save"), use_container_width=True)

            if submitted:
                med_id   = med_options[selected_med]
                med_name = meds_df[meds_df["id"] == med_id].iloc[0]["name"]
                time_str = intake_time.strftime("%H:%M")

                if editing_intake_row is not None:
                    idx = st.session_state["intakes_df"].index[
                        st.session_state["intakes_df"]["id"] == editing_intake_id
                    ].tolist()
                    if idx:
                        st.session_state["intakes_df"].at[idx[0], "medication_id"]   = med_id
                        st.session_state["intakes_df"].at[idx[0], "medication_name"] = med_name
                        st.session_state["intakes_df"].at[idx[0], "date"]            = intake_date.isoformat()
                        st.session_state["intakes_df"].at[idx[0], "time"]            = time_str
                        st.session_state["intakes_df"].at[idx[0], "confirmed"]       = confirmed_cb
                        st.session_state["intakes_df"].at[idx[0], "note"]            = note_in.strip()
                    st.session_state["editing_intake_id"] = None
                    st.success(t("intake_updated"))
                else:
                    new_row = pd.DataFrame([{
                        "id":              next_id(st.session_state["intakes_df"]),
                        "medication_id":   med_id,
                        "medication_name": med_name,
                        "date":            intake_date.isoformat(),
                        "time":            time_str,
                        "confirmed":       confirmed_cb,
                        "note":            note_in.strip(),
                        "created_at":      pd.Timestamp.now(),
                    }])
                    st.session_state["intakes_df"] = pd.concat(
                        [st.session_state["intakes_df"], new_row],
                        ignore_index=True
                    )
                    st.success(t("intake_saved"))

                save_intakes()
                st.rerun()