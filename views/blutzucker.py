"""
views/blutzucker.py
Blutzucker-Tagebuch: Eingabe, Plotly-Chart mit Risikozonen, Status-Tabelle.
Alle Werte beziehen sich auf Nüchternblutzucker (morgens vor dem Essen).
Arbeitet mit st.session_state["blood_sugar_df"].

Grenzwerte (mmol/l, Nüchternblutzucker):
  Normal:           3.9 – 5.5
  Auffällig tief:   3.0 – 3.9
  Auffällig hoch:   5.6 – 7.0
  Kritisch tief:    < 3.0
  Kritisch hoch:    >= 7.0
"""

import html
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# ── Styling ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.app-card { background:white; padding:1.25rem 1.5rem; border-radius:20px;
            box-shadow:0 4px 20px rgba(0,0,0,0.05); border:1px solid #e5e7eb;
            margin-bottom:1rem; overflow-x:auto; }
.status-normal    { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                    background:#dcfce7; color:#15803d; font-size:0.78rem; font-weight:600; }
.status-warning   { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                    background:#fef3c7; color:#b45309; font-size:0.78rem; font-weight:600; }
.status-warning-h { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                    background:#ffedd5; color:#c2410c; font-size:0.78rem; font-weight:600; }
.status-critical  { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                    background:#fee2e2; color:#b91c1c; font-size:0.78rem; font-weight:600; }
div.stButton > button { border-radius:12px; font-weight:600; min-height:40px; }
</style>""", unsafe_allow_html=True)

# ── Grenzwerte Nüchternblutzucker (mmol/l) ────────────────────────────────────
BS_CRIT_LOW    = 3.0
BS_WARN_LOW    = 3.5
BS_NORMAL_LOW  = 3.9
BS_NORMAL_HIGH = 5.5
BS_WARN_HIGH   = 7.0
BS_CRIT_HIGH   = 7.0

def e(t): return html.escape(str(t))

def classify_bs(value: float) -> str:
    """Klassifiziert einen Nüchternblutzuckerwert (mmol/l)."""
    if value < BS_CRIT_LOW:
        return "Kritisch tief"
    if value < BS_NORMAL_LOW:
        return "Auffällig tief"
    if value <= BS_NORMAL_HIGH:
        return "Normal"
    if value < BS_CRIT_HIGH:
        return "Auffällig hoch"
    return "Kritisch hoch"

def risk_badge(status: str) -> str:
    css = {
        "Normal":         "status-normal",
        "Auffällig tief": "status-warning",
        "Auffällig hoch": "status-warning-h",
        "Kritisch tief":  "status-critical",
        "Kritisch hoch":  "status-critical",
    }
    return f'<span class="{css.get(status, "status-normal")}">{e(status)}</span>'

def point_color(status: str) -> str:
    return {
        "Normal":         "#22c55e",
        "Auffällig tief": "#f59e0b",
        "Auffällig hoch": "#f97316",
        "Kritisch tief":  "#ef4444",
        "Kritisch hoch":  "#ef4444",
    }.get(status, "#22c55e")

def show_status_message(value: float, status: str):
    """Zeigt eine kontextbezogene Meldung in ganzen Sätzen an."""
    if status == "Normal":
        st.success(
            "✅ Ihr Nüchternblutzucker liegt im Normalbereich. "
            "Weiter so – halten Sie Ihre gesunde Routine bei!"
        )
    elif status == "Auffällig tief":
        st.warning(
            "🟡 Ihr Nüchternblutzucker ist auffällig tief (3.0 – 3.9 mmol/l). "
            "Ihr Wert liegt unter dem Normalbereich und kann ein Hinweis auf eine beginnende "
            "Unterzuckerung sein. Beobachten Sie Ihren Wert in den nächsten Tagen regelmässig "
            "und achten Sie auf Symptome wie Schwindel, Zittern oder Schwächegefühl. "
            "Essen Sie nach der Messung eine kleine Mahlzeit. "
            "Wenn der Wert wiederholt unter 3.9 mmol/l liegt, empfehlen wir Ihnen, "
            "eine Ärztin oder einen Arzt aufzusuchen."
        )
    elif status == "Auffällig hoch":
        st.warning(
            "🟠 Ihr Nüchternblutzucker ist auffällig hoch (5.6 – 7.0 mmol/l). "
            "Ihr Wert liegt über dem Normalbereich und kann ein Hinweis auf einen Prädiabetes sein – "
            "eine Vorstufe von Diabetes Typ 2. "
            "Achten Sie auf eine zuckerarme und ausgewogene Ernährung und versuchen Sie, "
            "sich regelmässig körperlich zu bewegen, da das den Blutzucker senken kann. "
            "Wiederholen Sie die Messung an mehreren aufeinanderfolgenden Tagen und "
            "informieren Sie Ihre Ärztin oder Ihren Arzt – eine ärztliche Abklärung ist empfehlenswert."
        )
    elif status == "Kritisch tief":
        st.error(
            "🔴 Ihr Nüchternblutzucker ist kritisch tief – Hypoglykämie (< 3.0 mmol/l). "
            "Eine Hypoglykämie ist ein medizinischer Notfall, der sofortiges Handeln erfordert. "
            "Nehmen Sie umgehend 15 bis 20 Gramm schnelle Kohlenhydrate zu sich, "
            "zum Beispiel ein Glas Fruchtsaft, drei bis vier Stück Traubenzucker oder ein Glas Cola. "
            "Messen Sie den Blutzucker nach 15 Minuten erneut. "
            "Wenn sich Ihr Zustand nicht bessert, rufen Sie sofort den Notarzt (144). "
            "Fahren Sie in diesem Zustand kein Auto und bleiben Sie nicht alleine. "
            "Klären Sie anschliessend mit Ihrer Ärztin oder Ihrem Arzt die Ursache ab."
        )
    elif status == "Kritisch hoch":
        st.error(
            "🔴 Ihr Nüchternblutzucker ist kritisch hoch – Diabetes-Verdacht (≥ 7.0 mmol/l). "
            "Ein Nüchternwert ab 7.0 mmol/l ist laut Deutscher Diabetes Gesellschaft ein klarer "
            "Hinweis auf Diabetes mellitus. Suchen Sie zeitnah eine Ärztin oder einen Arzt auf, "
            "da eine gesicherte Diagnose mindestens zwei erhöhte Messungen an verschiedenen Tagen erfordert. "
            "Meiden Sie bis zur Abklärung zuckerreiche Speisen und Getränke. "
            "Achten Sie auf typische Symptome wie starken Durst, häufiges Wasserlassen "
            "oder anhaltende Müdigkeit. "
            "Stellen Sie bitte keine Selbstdiagnose – die ärztliche Untersuchung ist zwingend notwendig."
        )

def save_bs():
    """Speichert blood_sugar_df in die Cloud."""
    st.session_state["data_manager"].save_user_data(
        st.session_state["blood_sugar_df"], "blood_sugar.csv"
    )

# ── Seiteninhalt ─────────────────────────────────────────────────────────────────
st.markdown("## 🩸 Blutzucker-Tagebuch")
st.markdown(
    '<p style="color:#6b7280">Nüchternblutzucker in mmol/l – gemessen morgens vor dem Essen.</p>',
    unsafe_allow_html=True
)
st.write("")

# ── Eingabe ───────────────────────────────────────────────────────────────────────
with st.form("bs_form"):
    bs_date  = st.date_input("Datum", value=date.today())
    bs_value = st.number_input(
        "Nüchternblutzucker (mmol/l)",
        min_value=0.0, max_value=30.0,
        value=5.0, step=0.1, format="%.1f",
        help="Bitte den Wert morgens vor dem Essen messen (mind. 8h nüchtern)."
    )
    submitted = st.form_submit_button("💾 Blutzucker speichern", use_container_width=True)

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
    st.markdown(
        f"**Gespeicherter Wert:** {bs_value:.1f} mmol/l &nbsp; {risk_badge(status)}",
        unsafe_allow_html=True
    )
    st.write("")
    show_status_message(bs_value, status)

st.divider()

# ── Einträge anzeigen ─────────────────────────────────────────────────────────────
bs_df = st.session_state["blood_sugar_df"]

if bs_df.empty:
    st.info("Noch keine Blutzuckerwerte eingetragen.")
else:
    df = bs_df.copy()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    # Datum als reines Datum ohne Uhrzeit
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%d.%m.%Y")
    df = df.dropna().sort_values("date")

    # ── Plotly Chart mit Risikozonen ──────────────────────────────────────────────
    st.markdown("#### 📈 Verlauf mit Risikozonen (Nüchternwerte)")

    y_max = max(df["value"].max(), 8.0) + 0.5
    y_min = max(min(df["value"].min(), BS_CRIT_LOW) - 0.3, 0)

    fig = go.Figure()

    for y0, y1, color, label in [
        (0,              BS_CRIT_LOW,    "rgba(239,68,68,0.15)",  "Kritisch tief (< 3.0)"),
        (BS_CRIT_LOW,    BS_WARN_LOW,    "rgba(251,191,36,0.20)", "Auffällig tief (3.0–3.5)"),
        (BS_WARN_LOW,    BS_NORMAL_LOW,  "rgba(251,191,36,0.10)", "Grenzwertig (3.5–3.9)"),
        (BS_NORMAL_LOW,  BS_NORMAL_HIGH, "rgba(34,197,94,0.13)",  "Normal (3.9–5.5)"),
        (BS_NORMAL_HIGH, BS_CRIT_HIGH,   "rgba(251,191,36,0.20)", "Auffällig hoch (5.6–7.0)"),
        (BS_CRIT_HIGH,   y_max,          "rgba(239,68,68,0.15)",  "Kritisch hoch (≥ 7.0)"),
    ]:
        if y1 > y_min:
            fig.add_hrect(
                y0=max(y0, y_min), y1=min(y1, y_max),
                fillcolor=color, line_width=0,
                annotation_text=label, annotation_position="left",
                annotation_font_size=9, annotation_font_color="#9ca3af"
            )

    point_colors = df["value"].apply(lambda v: point_color(classify_bs(v)))

    fig.add_trace(go.Scatter(
        x=df["date"], y=df["value"],
        name="Nüchternblutzucker (mmol/l)",
        mode="lines+markers",
        line=dict(color="#8b5cf6", width=2.5),
        marker=dict(size=9, color=point_colors, line=dict(width=1.5, color="white")),
    ))

    fig.update_layout(
        height=380, margin=dict(l=10, r=10, t=20, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(
            showgrid=False,
            title="Datum",
            tickangle=-30,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f3f4f6",
            title="Blutzucker (mmol/l)",
            range=[y_min, y_max]
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Tabelle mit Status-Spalte ──────────────────────────────────────────────────
    st.markdown("#### 📋 Eintragsübersicht")
    rows_html = ""
    for _, row in df.sort_values("date", ascending=False).iterrows():
        status = classify_bs(row["value"])
        rows_html += f"""<tr>
            <td style='padding:0.5rem 0.75rem'>{e(str(row['date']))}</td>
            <td style='padding:0.5rem 0.75rem;text-align:center'>{row['value']:.1f}</td>
            <td style='padding:0.5rem 0.75rem;text-align:center'>{risk_badge(status)}</td>
        </tr>"""

    st.markdown(f"""
    <div class="app-card">
    <table style='width:100%;border-collapse:collapse;font-size:0.9rem'>
        <thead><tr style='border-bottom:2px solid #e5e7eb'>
            <th style='padding:0.5rem 0.75rem;text-align:left'>Datum</th>
            <th style='padding:0.5rem 0.75rem;text-align:center'>Nüchternblutzucker (mmol/l)</th>
            <th style='padding:0.5rem 0.75rem;text-align:center'>Status</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table></div>""", unsafe_allow_html=True)

    # ── Referenzwerte ──────────────────────────────────────────────────────────────
    with st.expander("ℹ️ Referenzwerte (Nüchternblutzucker)"):
        st.markdown("""
        > ⚠️ **Wichtig:** Diese Werte gelten ausschliesslich für den **Nüchternblutzucker**
        > – gemessen morgens vor dem Essen nach mindestens 8 Stunden ohne Nahrung.

        | Status | mmol/l | Bedeutung |
        |---|---|---|
        | 🟢 Normal | 3.9 – 5.5 | Gesunder Nüchternwert |
        | 🟡 Auffällig tief | 3.0 – 3.9 | Zu tief, beobachten |
        | 🟠 Auffällig hoch | 5.6 – 7.0 | Möglicher Prädiabetes |
        | 🔴 Kritisch tief | < 3.0 | Hypoglykämie – sofort handeln |
        | 🔴 Kritisch hoch | ≥ 7.0 | Diabetes-Verdacht – ärztlich abklären |

        *Quelle: Deutsche Diabetes Gesellschaft / Helios Gesundheit*
        """)

    # ── Löschen ───────────────────────────────────────────────────────────────────
    with st.expander("🗑️ Eintrag löschen"):
        options  = sorted(bs_df["date"].astype(str).tolist(), reverse=True)
        del_date = st.selectbox("Datum wählen", options=options, key="bs_del")
        if st.button("Eintrag löschen", key="bs_del_btn"):
            st.session_state["blood_sugar_df"] = bs_df[
                bs_df["date"].astype(str) != del_date
            ].reset_index(drop=True)
            save_bs()
            st.success("Eintrag gelöscht.")
            st.rerun()