"""
views/blutzucker.py
Blutzucker-Tagebuch – vollständig übersetzt.
Medizinische Hinweistexte sind auf Deutsch (Sicherheit).
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from utils.translations import t
from functions.format_helpers import e
from functions.data_helpers import save_bs
from functions.health_classifications import classify_bs
from functions.blutzucker import badge_css, point_color, risk_badge
from utils.themes import inject_theme, get_theme

inject_theme()
theme = get_theme()

# ── Grenzwerte (mmol/l) ───────────────────────────────────────────────────────
BS_CRIT_LOW=3.0; BS_WARN_LOW=3.5; BS_NORMAL_LOW=3.9
BS_NORMAL_HIGH=5.5; BS_WARN_HIGH=7.0; BS_CRIT_HIGH=7.0


def badge_css(status):
    return {
        t("bs_normal"):    "status-normal",
        t("bs_warn_low"):  "status-warning",
        t("bs_warn_high"): "status-warning-h",
        t("bs_crit_low"):  "status-critical",
        t("bs_crit_high"): "status-critical",
    }.get(status, "status-normal")

def point_color(status):
    return {
        t("bs_normal"):    "#22c55e",
        t("bs_warn_low"):  "#f59e0b",
        t("bs_warn_high"): "#f97316",
        t("bs_crit_low"):  "#ef4444",
        t("bs_crit_high"): "#ef4444",
    }.get(status, "#22c55e")

def risk_badge(status):
    return f'<span class="{badge_css(status)}">{e(status)}</span>'

def show_status_message(value, status):
    if show_health_disclaimer_if_needed():
        return
    n=t("bs_normal"); wl=t("bs_warn_low"); wh=t("bs_warn_high")
    cl=t("bs_crit_low"); ch=t("bs_crit_high")
    if status == n:
        st.success("✅ Ihr Nüchternblutzucker liegt im Normalbereich. Weiter so!")
    elif status == wl:
        st.warning("🟡 Auffällig tiefer Nüchternwert (3.0–3.9 mmol/l). Beobachten Sie den Wert regelmässig und sprechen Sie mit Ihrer Ärztin / Ihrem Arzt wenn er wiederholt unter 3.9 liegt.")
    elif status == wh:
        st.warning("🟠 Auffällig hoher Nüchternwert (5.6–7.0 mmol/l). Dies kann auf einen Prädiabetes hinweisen. Bitte ärztlich abklären lassen.")
    elif status == cl:
        st.error("🔴 Kritisch tiefer Wert – Hypoglykämie (< 3.0 mmol/l). Nehmen Sie sofort 15–20g schnelle Kohlenhydrate zu sich. Bei ausbleibender Besserung Notarzt (144) rufen.")
    elif status == ch:
        st.error("🔴 Kritisch hoher Wert – Diabetes-Verdacht (≥ 7.0 mmol/l). Bitte zeitnah eine Ärztin oder einen Arzt aufsuchen.")

def save_bs():
    st.session_state["data_manager"].save_user_data(st.session_state["blood_sugar_df"], "blood_sugar.csv")

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""<style>
.app-card{background:white;padding:1.25rem 1.5rem;border-radius:20px;box-shadow:0 4px 20px rgba(0,0,0,0.05);border:1px solid #e5e7eb;margin-bottom:1rem;overflow-x:auto}
.status-normal{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#dcfce7;color:#15803d;font-size:0.78rem;font-weight:600}
.status-warning{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#fef3c7;color:#b45309;font-size:0.78rem;font-weight:600}
.status-warning-h{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#ffedd5;color:#c2410c;font-size:0.78rem;font-weight:600}
.status-critical{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#fee2e2;color:#b91c1c;font-size:0.78rem;font-weight:600}
div.stButton>button{border-radius:12px;font-weight:600;min-height:40px}
</style>""", unsafe_allow_html=True)

# ── Seite ─────────────────────────────────────────────────────────────────────
st.markdown(f"## 🩸 {t('bs_title')}")
st.markdown(f'<p style="color:#6b7280">{t("bs_subtitle")}</p>', unsafe_allow_html=True)
st.write("")

with st.form("bs_form"):
    bs_date  = st.date_input(t("date_col"), value=date.today())
    bs_value = st.number_input(t("bs_value"), min_value=0.0, max_value=30.0,
                               value=5.0, step=0.1, format="%.1f",
                               help="Mind. 8h nüchtern / At least 8h fasting")
    submitted = st.form_submit_button(t("bs_save"), use_container_width=True)

if submitted:
    date_str  = bs_date.isoformat()
    df        = st.session_state["blood_sugar_df"]
    new_entry = pd.DataFrame([{"date": date_str, "value": float(bs_value)}])
    if not df.empty and date_str in df["date"].astype(str).values:
        df.loc[df["date"].astype(str) == date_str, "value"] = float(bs_value)
    else:
        df = pd.concat([df, new_entry], ignore_index=True)
    df = df.sort_values("date").reset_index(drop=True)
    st.session_state["blood_sugar_df"] = df
    save_bs()
    status = classify_bs(bs_value)
    st.markdown(f'**{t("bs_saved_value")}:** {bs_value:.1f} mmol/l &nbsp; {risk_badge(status)}', unsafe_allow_html=True)
    st.write("")
    show_status_message(bs_value, status)

st.divider()

bs_df = st.session_state["blood_sugar_df"]

if bs_df.empty:
    st.info(t("bs_none"))
else:
    df = bs_df.copy()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"]  = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%d.%m.%Y")
    df = df.dropna().sort_values("date")

    st.markdown(f"#### 📈 {t('bs_chart_title')}")
    y_max = max(df["value"].max(), 8.0) + 0.5
    y_min = max(min(df["value"].min(), BS_CRIT_LOW) - 0.3, 0)

    fig = go.Figure()
    for y0, y1, color, label in [
        (0,BS_CRIT_LOW,"rgba(239,68,68,0.15)",f"{t('bs_crit_low')} (< 3.0)"),
        (BS_CRIT_LOW,BS_WARN_LOW,"rgba(251,191,36,0.20)",f"(3.0–3.5)"),
        (BS_WARN_LOW,BS_NORMAL_LOW,"rgba(251,191,36,0.10)",f"(3.5–3.9)"),
        (BS_NORMAL_LOW,BS_NORMAL_HIGH,"rgba(34,197,94,0.13)",f"{t('bs_normal')} (3.9–5.5)"),
        (BS_NORMAL_HIGH,BS_CRIT_HIGH,"rgba(251,191,36,0.20)",f"{t('bs_warn_high')} (5.6–7.0)"),
        (BS_CRIT_HIGH,y_max,"rgba(239,68,68,0.15)",f"{t('bs_crit_high')} (≥ 7.0)"),
    ]:
        if y1 > y_min:
            fig.add_hrect(y0=max(y0,y_min), y1=min(y1,y_max), fillcolor=color, line_width=0,
                annotation_text=label, annotation_position="left",
                annotation_font_size=9, annotation_font_color="#9ca3af")

    point_colors = df["value"].apply(lambda v: point_color(classify_bs(v)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["value"], name=t("bs_value_short"),
        mode="lines+markers", line=dict(color="#8b5cf6",width=2.5),
        marker=dict(size=9, color=point_colors, line=dict(width=1.5,color="white"))))
    fig.update_layout(height=380, margin=dict(l=10,r=10,t=20,b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False, title=t("date_col"), tickangle=-30),
        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", title="mmol/l", range=[y_min,y_max]))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"#### 📋 {t('overview')}")
    rows_html = ""
    for _, row in df.sort_values("date", ascending=False).iterrows():
        status = classify_bs(row["value"])
        rows_html += f"""<tr>
            <td style='padding:0.5rem 0.75rem'>{e(str(row['date']))}</td>
            <td style='padding:0.5rem 0.75rem;text-align:center'>{row['value']:.1f}</td>
            <td style='padding:0.5rem 0.75rem;text-align:center'>{risk_badge(status)}</td>
        </tr>"""
    st.markdown(f"""<div class="app-card"><table style='width:100%;border-collapse:collapse;font-size:0.9rem'>
        <thead><tr style='border-bottom:2px solid #e5e7eb'>
            <th style='padding:0.5rem 0.75rem;text-align:left'>{t('date_col')}</th>
            <th style='padding:0.5rem 0.75rem;text-align:center'>{t('bs_value_short')} (mmol/l)</th>
            <th style='padding:0.5rem 0.75rem;text-align:center'>{t('status')}</th>
        </tr></thead><tbody>{rows_html}</tbody></table></div>""", unsafe_allow_html=True)

    with st.expander(f"ℹ️ {t('bs_ref_title')}"):
        ref_meanings = {
            "de": ["Gesunder Nüchternwert", "Zu tief, beobachten", "Möglicher Prädiabetes", "Hypoglykämie – sofort handeln", "Diabetes-Verdacht – ärztlich abklären"],
            "fr": ["Valeur à jeun saine", "Trop bas, surveiller", "Possible prédiabète", "Hypoglycémie – agir immédiatement", "Suspicion de diabète – consulter un médecin"],
            "it": ["Valore a digiuno sano", "Troppo basso, monitorare", "Possibile prediabete", "Ipoglicemia – agire subito", "Sospetto diabete – consultare un medico"],
            "en": ["Healthy fasting value", "Too low, monitor", "Possible prediabetes", "Hypoglycemia – act immediately", "Suspected diabetes – see a doctor"],
        }
        lang = st.session_state.get("language", "de")
        meanings = ref_meanings.get(lang, ref_meanings["de"])
        fasting_note = {
            "de": "Diese Werte gelten für den **Nüchternblutzucker** (mind. 8h ohne Nahrung).",
            "fr": "Ces valeurs s'appliquent à la **glycémie à jeun** (min. 8h sans nourriture).",
            "it": "Questi valori si riferiscono alla **glicemia a digiuno** (min. 8h senza cibo).",
            "en": "These values apply to **fasting blood sugar** (min. 8h without food).",
        }.get(lang, "")
        source = {
            "de": "Deutsche Diabetes Gesellschaft / Helios Gesundheit",
            "fr": "Société Allemande du Diabète / Helios Santé",
            "it": "Società Tedesca del Diabete / Helios Salute",
            "en": "German Diabetes Society / Helios Health",
        }.get(lang, "")
        st.markdown(f"""
> ⚠️ {fasting_note}

| {t('status')} | mmol/l | {t('ref_meaning')} |
|---|---|---|
| 🟢 {t('bs_normal')} | 3.9–5.5 | {meanings[0]} |
| 🟡 {t('bs_warn_low')} | 3.0–3.9 | {meanings[1]} |
| 🟠 {t('bs_warn_high')} | 5.6–7.0 | {meanings[2]} |
| 🔴 {t('bs_crit_low')} | < 3.0 | {meanings[3]} |
| 🔴 {t('bs_crit_high')} | ≥ 7.0 | {meanings[4]} |

*{source}*
        """)

    with st.expander(f"🗑️ {t('bs_delete')}"):
        options  = sorted(bs_df["date"].astype(str).tolist(), reverse=True)
        del_date = st.selectbox(t("bs_delete_date"), options=options, key="bs_del")
        if st.button(t("bs_delete"), key="bs_del_btn"):
            st.session_state["blood_sugar_df"] = bs_df[bs_df["date"].astype(str) != del_date].reset_index(drop=True)
            save_bs()
            st.success("✅")
            st.rerun()