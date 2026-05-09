"""
views/blutdruck.py
Blutdruck-Tagebuch – vollständig übersetzt.
Medizinische Hinweistexte sind auf Deutsch (Sicherheit).
"""

import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from utils.translations import t
from utils.themes import inject_theme, get_theme

inject_theme()
theme = get_theme()

def e(x): return html.escape(str(x))

# ── Grenzwerte ────────────────────────────────────────────────────────────────
BP_HYPO_SYS=100; BP_HYPO_DIA=60; BP_OPTIMAL_SYS=120; BP_OPTIMAL_DIA=80
BP_NORMAL_SYS=129; BP_NORMAL_DIA=84; BP_HIGHNORM_SYS=139; BP_HIGHNORM_DIA=89
BP_HYP1_SYS=159; BP_HYP1_DIA=99; BP_HYP2_SYS=179; BP_HYP2_DIA=109

def classify_bp(sys, dia):
    if sys < BP_HYPO_SYS or dia < BP_HYPO_DIA:    return t("bp_hypo")
    if sys >= 180 or dia >= 110:                    return t("bp_hyp3")
    if sys >= 160 or dia >= 100:                    return t("bp_hyp2")
    if sys >= 140 or dia >= 90:                     return t("bp_hyp1")
    if sys >= 130 or dia >= 85:                     return t("bp_highnorm")
    if sys >= 120 or dia >= 80:                     return t("bp_normal")
    return t("bp_optimal")

def badge_css(status):
    m = {
        t("bp_hypo"): "status-hypo", t("bp_optimal"): "status-optimal",
        t("bp_normal"): "status-normal", t("bp_highnorm"): "status-highnorm",
        t("bp_hyp1"): "status-hyp1", t("bp_hyp2"): "status-hyp2",
        t("bp_hyp3"): "status-hyp3",
    }
    return m.get(status, "status-normal")

def point_color(status):
    m = {
        t("bp_hypo"): "#8b5cf6", t("bp_optimal"): "#22c55e",
        t("bp_normal"): "#86efac", t("bp_highnorm"): "#fbbf24",
        t("bp_hyp1"): "#f97316", t("bp_hyp2"): "#ef4444",
        t("bp_hyp3"): "#b91c1c",
    }
    return m.get(status, "#22c55e")

def risk_badge(status):
    css = badge_css(status)
    return f'<span class="{css}">{e(status)}</span>'

def show_status_message(sys, dia, status):
    lang = st.session_state.get("language","de")
    if lang != "de":
        st.info(t("health_notes_disclaimer"))
        return
    hyp3 = t("bp_hyp3"); hyp2 = t("bp_hyp2"); hyp1 = t("bp_hyp1")
    highn = t("bp_highnorm"); norm = t("bp_normal")
    opt = t("bp_optimal"); hypo = t("bp_hypo")

    if sys >= 140 and dia < 60:
        st.error("🔴 Ihr systolischer Wert ist stark erhöht und Ihr diastolischer Wert ist gleichzeitig zu tief – bitte dringend ärztlich abklären lassen.")
        return
    if sys < 100 and dia >= 90:
        st.error("🔴 Ihr systolischer Wert ist zu tief und Ihr diastolischer Wert ist gleichzeitig erhöht – bitte umgehend eine Ärztin oder einen Arzt aufsuchen.")
        return
    if status == opt:
        st.success("✅ Ihr Blutdruck ist optimal (unter 120/80 mmHg). Halten Sie Ihren gesunden Lebensstil bei!")
    elif status == norm:
        st.success("✅ Ihr Blutdruck liegt im normalen Bereich (120–129 / 80–84 mmHg). Weiter so!")
    elif status == highn:
        st.warning("🟡 Ihr Blutdruck ist hoch-normal (130–139 / 85–89 mmHg). Beobachten Sie den Wert und informieren Sie Ihre Ärztin / Ihren Arzt wenn er wiederholt in diesem Bereich liegt.")
    elif status == hyp1:
        st.warning("🟠 Hypertonie Grad 1 (140–159 / 90–99 mmHg). Ärztliche Abklärung empfohlen. Lebensstiländerungen können den Blutdruck senken.")
    elif status == hyp2:
        st.error("🔴 Hypertonie Grad 2 (160–179 / 100–109 mmHg). Bitte zeitnah eine Ärztin oder einen Arzt aufsuchen.")
    elif status == hyp3:
        st.error("🔴 Hypertensiver Notfall (≥ 180/110 mmHg). Rufen Sie sofort den Notarzt (144)!")
    elif status == hypo:
        st.warning("🟣 Hypotonie (unter 100/60 mmHg). Trinken Sie ausreichend Wasser und stehen Sie langsam auf.")
    if sys >= 140 and 60 <= dia <= 70:
        st.info("ℹ️ Zusatzhinweis: Isolierte systolische Hypertonie – bitte beim nächsten Arzttermin erwähnen.")
    if 100 <= sys <= 110 and dia >= 90:
        st.info("ℹ️ Zusatzhinweis: Isolierte diastolische Hypertonie – bitte ärztlich besprechen.")

def save_bp():
    st.session_state["data_manager"].save_user_data(st.session_state["blood_pressure_df"], "blood_pressure.csv")

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""<style>
.app-card{background:white;padding:1.25rem 1.5rem;border-radius:20px;box-shadow:0 4px 20px rgba(0,0,0,0.05);border:1px solid #e5e7eb;margin-bottom:1rem;overflow-x:auto}
.status-optimal{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#dcfce7;color:#15803d;font-size:0.78rem;font-weight:600}
.status-normal{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#d1fae5;color:#065f46;font-size:0.78rem;font-weight:600}
.status-highnorm{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#fef9c3;color:#854d0e;font-size:0.78rem;font-weight:600}
.status-hyp1{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#fef3c7;color:#b45309;font-size:0.78rem;font-weight:600}
.status-hyp2{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#ffedd5;color:#c2410c;font-size:0.78rem;font-weight:600}
.status-hyp3{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#fee2e2;color:#b91c1c;font-size:0.78rem;font-weight:600}
.status-hypo{display:inline-block;padding:0.18rem 0.6rem;border-radius:999px;background:#ede9fe;color:#6d28d9;font-size:0.78rem;font-weight:600}
div.stButton>button{border-radius:12px;font-weight:600;min-height:40px}
</style>""", unsafe_allow_html=True)

# ── Seite ─────────────────────────────────────────────────────────────────────
st.markdown(f"## ❤️ {t('bp_title')}")
st.markdown(f'<p style="color:#6b7280">{t("bp_subtitle")}</p>', unsafe_allow_html=True)
st.write("")

with st.form("bp_form"):
    bp_date = st.date_input(t("date_col"), value=date.today())
    c1, c2  = st.columns(2)
    with c1:
        bp_sys = st.number_input(t("bp_systolic"), min_value=50, max_value=300, value=120, step=1)
    with c2:
        bp_dia = st.number_input(t("bp_diastolic"), min_value=30, max_value=200, value=80, step=1)
    submitted = st.form_submit_button(t("bp_save"), use_container_width=True)

if submitted:
    date_str = bp_date.isoformat()
    df = st.session_state["blood_pressure_df"]
    new_entry = pd.DataFrame([{"date": date_str, "systolic": int(bp_sys), "diastolic": int(bp_dia)}])
    if not df.empty and date_str in df["date"].astype(str).values:
        df.loc[df["date"].astype(str) == date_str, ["systolic","diastolic"]] = [int(bp_sys), int(bp_dia)]
    else:
        df = pd.concat([df, new_entry], ignore_index=True)
    df = df.sort_values("date").reset_index(drop=True)
    st.session_state["blood_pressure_df"] = df
    save_bp()
    status = classify_bp(bp_sys, bp_dia)
    st.markdown(f'**{t("bp_saved_value")}:** {bp_sys}/{bp_dia} mmHg &nbsp; {risk_badge(status)}', unsafe_allow_html=True)
    st.write("")
    show_status_message(bp_sys, bp_dia, status)

st.divider()

bp_df = st.session_state["blood_pressure_df"]

if bp_df.empty:
    st.info(t("bp_none"))
else:
    df = bp_df.copy()
    df["systolic"]  = pd.to_numeric(df["systolic"],  errors="coerce")
    df["diastolic"] = pd.to_numeric(df["diastolic"], errors="coerce")
    df["date"]      = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%d.%m.%Y")
    df = df.dropna().sort_values("date")

    st.markdown(f"#### 📈 {t('bp_chart_title')}")
    y_max = max(df["systolic"].max(), 185) + 10
    y_min = max(min(df["diastolic"].min(), 55) - 5, 0)

    fig = go.Figure()
    for y0, y1, color in [
        (0,BP_HYPO_SYS,"rgba(139,92,246,0.12)"),
        (BP_HYPO_SYS,BP_OPTIMAL_SYS,"rgba(34,197,94,0.15)"),
        (BP_OPTIMAL_SYS,BP_NORMAL_SYS,"rgba(34,197,94,0.09)"),
        (BP_NORMAL_SYS,BP_HIGHNORM_SYS,"rgba(251,191,36,0.12)"),
        (BP_HIGHNORM_SYS,BP_HYP1_SYS,"rgba(251,191,36,0.20)"),
        (BP_HYP1_SYS,BP_HYP2_SYS,"rgba(239,68,68,0.15)"),
        (BP_HYP2_SYS,y_max,"rgba(185,28,28,0.18)"),
    ]:
        if y1 > y_min:
            fig.add_hrect(y0=max(y0,y_min), y1=min(y1,y_max), fillcolor=color, line_width=0)

    colors = df.apply(lambda r: point_color(classify_bp(int(r["systolic"]), int(r["diastolic"]))), axis=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["systolic"], name=t("bp_systolic_short"),
        mode="lines+markers", line=dict(color="#ef4444",width=2.5),
        marker=dict(size=8, color=colors, line=dict(width=1.5,color="white"))))
    fig.add_trace(go.Scatter(x=df["date"], y=df["diastolic"], name=t("bp_diastolic_short"),
        mode="lines+markers", line=dict(color="#3b82f6",width=2.5),
        marker=dict(size=8, color=colors, line=dict(width=1.5,color="white"))))
    fig.update_layout(height=400, margin=dict(l=10,r=10,t=20,b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        xaxis=dict(showgrid=False, title=t("date_col"), tickangle=-30),
        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", title="mmHg", range=[y_min,y_max]))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"#### 📋 {t('overview')}")
    rows_html = ""
    for _, row in df.sort_values("date", ascending=False).iterrows():
        status = classify_bp(int(row["systolic"]), int(row["diastolic"]))
        rows_html += f"""<tr>
            <td style='padding:0.5rem 0.75rem'>{e(str(row['date']))}</td>
            <td style='padding:0.5rem 0.75rem;text-align:center'>{int(row['systolic'])}</td>
            <td style='padding:0.5rem 0.75rem;text-align:center'>{int(row['diastolic'])}</td>
            <td style='padding:0.5rem 0.75rem;text-align:center'>{risk_badge(status)}</td>
        </tr>"""
    st.markdown(f"""<div class="app-card"><table style='width:100%;border-collapse:collapse;font-size:0.9rem'>
        <thead><tr style='border-bottom:2px solid #e5e7eb'>
            <th style='padding:0.5rem 0.75rem;text-align:left'>{t('date_col')}</th>
            <th style='padding:0.5rem 0.75rem;text-align:center'>{t('bp_systolic_short')}</th>
            <th style='padding:0.5rem 0.75rem;text-align:center'>{t('bp_diastolic_short')}</th>
            <th style='padding:0.5rem 0.75rem;text-align:center'>{t('status')}</th>
        </tr></thead><tbody>{rows_html}</tbody></table></div>""", unsafe_allow_html=True)

    with st.expander(f"ℹ️ {t('bp_ref_title')}"):
        st.markdown(f"""
| {t('ref_category') if 'ref_category' in dir() else 'Kategorie'} | {t('bp_systolic_short')} (mmHg) | {t('bp_diastolic_short')} (mmHg) |
|---|---|---|
| 🟣 {t('bp_hypo')} | < 100 | < 60 |
| 🟢 {t('bp_optimal')} | < 120 | < 80 |
| 🟢 {t('bp_normal')} | 120–129 | 80–84 |
| 🟡 {t('bp_highnorm')} | 130–139 | 85–89 |
| 🟠 {t('bp_hyp1')} | 140–159 | 90–99 |
| 🔴 {t('bp_hyp2')} | 160–179 | 100–109 |
| 🔴 {t('bp_hyp3')} | ≥ 180 | ≥ 110 |

*ESC/ESH / Deutsche Gesellschaft für Kardiologie (DGK)*
        """)

    with st.expander(f"🗑️ {t('bp_delete')}"):
        options  = sorted(bp_df["date"].astype(str).tolist(), reverse=True)
        del_date = st.selectbox(t("bp_delete_date"), options=options, key="bp_del")
        if st.button(t("bp_delete"), key="bp_del_btn"):
            st.session_state["blood_pressure_df"] = bp_df[bp_df["date"].astype(str) != del_date].reset_index(drop=True)
            save_bp()
            st.success("✅")
            st.rerun()