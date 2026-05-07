"""
views/blutdruck.py
Blutdruck-Tagebuch: Eingabe, Plotly-Chart mit Risikozonen, Status-Tabelle.
Kategorien nach Leitlinien der Deutschen Gesellschaft für Kardiologie (DGK).
Arbeitet mit st.session_state["blood_pressure_df"].
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
.status-optimal  { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                   background:#dcfce7; color:#15803d; font-size:0.78rem; font-weight:600; }
.status-normal   { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                   background:#d1fae5; color:#065f46; font-size:0.78rem; font-weight:600; }
.status-highnorm { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                   background:#fef9c3; color:#854d0e; font-size:0.78rem; font-weight:600; }
.status-hyp1     { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                   background:#fef3c7; color:#b45309; font-size:0.78rem; font-weight:600; }
.status-hyp2     { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                   background:#ffedd5; color:#c2410c; font-size:0.78rem; font-weight:600; }
.status-hyp3     { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                   background:#fee2e2; color:#b91c1c; font-size:0.78rem; font-weight:600; }
.status-hypo     { display:inline-block; padding:0.18rem 0.6rem; border-radius:999px;
                   background:#ede9fe; color:#6d28d9; font-size:0.78rem; font-weight:600; }
div.stButton > button { border-radius:12px; font-weight:600; min-height:40px; }
</style>""", unsafe_allow_html=True)

# ── Grenzwerte (mmHg) nach DGK-Leitlinien ────────────────────────────────────
BP_HYPO_SYS     = 100
BP_HYPO_DIA     = 60
BP_OPTIMAL_SYS  = 120
BP_OPTIMAL_DIA  = 80
BP_NORMAL_SYS   = 129
BP_NORMAL_DIA   = 84
BP_HIGHNORM_SYS = 139
BP_HIGHNORM_DIA = 89
BP_HYP1_SYS     = 159
BP_HYP1_DIA     = 99
BP_HYP2_SYS     = 179
BP_HYP2_DIA     = 109

def e(t): return html.escape(str(t))

def classify_bp(sys: int, dia: int) -> str:
    """Klassifiziert einen Blutdruckwert nach DGK-Leitlinien."""
    if sys < BP_HYPO_SYS or dia < BP_HYPO_DIA:
        return "Hypotonie"
    if sys >= 180 or dia >= 110:
        return "Hypertonie Grad 3"
    if sys >= 160 or dia >= 100:
        return "Hypertonie Grad 2"
    if sys >= 140 or dia >= 90:
        return "Hypertonie Grad 1"
    if sys >= 130 or dia >= 85:
        return "Hoch-normal"
    if sys >= 120 or dia >= 80:
        return "Normal"
    return "Optimal"

def risk_badge(status: str) -> str:
    css = {
        "Hypotonie":         "status-hypo",
        "Optimal":           "status-optimal",
        "Normal":            "status-normal",
        "Hoch-normal":       "status-highnorm",
        "Hypertonie Grad 1": "status-hyp1",
        "Hypertonie Grad 2": "status-hyp2",
        "Hypertonie Grad 3": "status-hyp3",
    }
    return f'<span class="{css.get(status, "status-normal")}">{e(status)}</span>'

def point_color(status: str) -> str:
    return {
        "Hypotonie":         "#8b5cf6",
        "Optimal":           "#22c55e",
        "Normal":            "#86efac",
        "Hoch-normal":       "#fbbf24",
        "Hypertonie Grad 1": "#f97316",
        "Hypertonie Grad 2": "#ef4444",
        "Hypertonie Grad 3": "#b91c1c",
    }.get(status, "#22c55e")

def show_status_message(sys: int, dia: int, status: str):
    """Zeigt eine kontextbezogene Meldung in ganzen Sätzen an."""

    # ── Kritische Sonderfälle zuerst prüfen ───────────────────────────────────
    if sys >= 140 and dia < 60:
        st.error(
            "🔴 Ihr systolischer Wert ist stark erhöht und Ihr diastolischer Wert ist gleichzeitig "
            "zu tief – das ist eine ungewöhnliche Kombination die dringend ärztlich abgeklärt werden muss. "
            "Der erhöhte obere Wert weist auf eine Hypertonie hin, während der tiefe untere Wert "
            "auf eine mögliche isolierte systolische Hypertonie oder ein Herzproblem hindeuten kann. "
            "Diese Kombination tritt gelegentlich bei älteren Personen auf, ist aber in jedem Fall "
            "abklärungsbedürftig. Bitte suchen Sie zeitnah eine Ärztin oder einen Arzt auf "
            "und bringen Sie Ihre Blutdrucktabelle mit."
        )
        return

    if sys < 100 and dia >= 90:
        st.error(
            "🔴 Ihr systolischer Wert ist zu tief und Ihr diastolischer Wert ist gleichzeitig "
            "erhöht – das entspricht dem Bild einer isolierten diastolischen Hypertonie mit "
            "gleichzeitiger Hypotonie, einer seltenen und medizinisch auffälligen Kombination. "
            "Ein tiefer oberer Wert bei gleichzeitig hohem unteren Wert kann auf eine "
            "Funktionsstörung des Herzens oder der Herzklappen hinweisen. "
            "Bitte suchen Sie umgehend eine Ärztin oder einen Arzt auf, "
            "da diese Kombination einer genauen Abklärung bedarf."
        )
        return

    # ── Einzelne Kategorien ───────────────────────────────────────────────────
    if status == "Optimal":
        st.success(
            "✅ Ihr Blutdruck ist optimal (unter 120/80 mmHg). "
            "Das ist der ideale Wert für Ihre Herzgesundheit. "
            "Halten Sie Ihren gesunden Lebensstil mit ausgewogener Ernährung "
            "und regelmässiger Bewegung bei!"
        )
    elif status == "Normal":
        st.success(
            "✅ Ihr Blutdruck liegt im normalen Bereich (120–129 / 80–84 mmHg). "
            "Das ist ein guter Wert. Achten Sie weiterhin auf eine ausgewogene Ernährung, "
            "regelmässige Bewegung und ausreichend Schlaf, um Ihren Blutdruck stabil zu halten."
        )
    elif status == "Hoch-normal":
        st.warning(
            "🟡 Ihr Blutdruck ist hoch-normal (130–139 / 85–89 mmHg). "
            "Dieser Bereich gilt zwar noch nicht als Bluthochdruck, erhöht aber das Risiko "
            "für Herz-Kreislauf-Erkrankungen, insbesondere bei Vorerkrankungen wie Diabetes. "
            "Reduzieren Sie Ihren Salzkonsum, bewegen Sie sich regelmässig und vermeiden Sie "
            "Stress sowie übermässigen Alkohol. "
            "Informieren Sie Ihre Ärztin oder Ihren Arzt, wenn der Wert mehrfach in diesem Bereich liegt."
        )
    elif status == "Hypertonie Grad 1":
        st.warning(
            "🟠 Ihr Blutdruck liegt im Bereich einer Hypertonie Grad 1 (140–159 / 90–99 mmHg). "
            "Das bedeutet, Ihr Blutdruck ist dauerhaft erhöht und sollte ärztlich abgeklärt werden. "
            "Änderungen des Lebensstils wie Gewichtsreduktion, salzarme Ernährung, "
            "regelmässige Bewegung und Rauchstopp können den Blutdruck deutlich senken. "
            "Sprechen Sie mit Ihrer Ärztin oder Ihrem Arzt, ob zusätzlich eine medikamentöse "
            "Behandlung notwendig ist."
        )
    elif status == "Hypertonie Grad 2":
        st.error(
            "🔴 Ihr Blutdruck ist deutlich erhöht – Hypertonie Grad 2 (160–179 / 100–109 mmHg). "
            "Bei diesen Werten ist eine ärztliche Behandlung dringend empfohlen, da ein stark "
            "erhöhtes Risiko für Herzinfarkt, Schlaganfall und Nierenschäden besteht. "
            "Suchen Sie zeitnah eine Ärztin oder einen Arzt auf. "
            "Vermeiden Sie körperliche Anstrengung und Stress bis zur Abklärung. "
            "Falls Sie bereits blutdrucksenkende Medikamente nehmen, überprüfen Sie bitte, "
            "ob diese korrekt eingenommen wurden."
        )
    elif status == "Hypertonie Grad 3":
        st.error(
            "🔴 Ihr Blutdruck ist kritisch hoch – hypertensiver Notfall (≥ 180 / ≥ 110 mmHg). "
            "Bei diesen Werten besteht unmittelbares Risiko für lebensbedrohliche Komplikationen "
            "wie Herzinfarkt, Schlaganfall oder Nierenversagen. "
            "Rufen Sie sofort den Notarzt (144) oder lassen Sie sich umgehend in eine "
            "Notaufnahme bringen. "
            "Setzen Sie sich hin, beruhigen Sie sich und messen Sie den Wert nach einigen "
            "Minuten erneut. "
            "Fahren Sie in diesem Zustand auf keinen Fall Auto."
        )
    elif status == "Hypotonie":
        st.warning(
            "🟣 Ihr Blutdruck ist zu tief – Hypotonie (unter 100/60 mmHg). "
            "Niedriger Blutdruck ist häufig harmlos, kann aber zu Schwindel, Schwächegefühl "
            "oder Ohnmacht führen, besonders beim schnellen Aufstehen. "
            "Trinken Sie ausreichend Wasser, stehen Sie langsam auf und vermeiden Sie "
            "langes Stehen in der Wärme. "
            "Wenn die Symptome anhalten oder Sie sich unwohl fühlen, sprechen Sie bitte "
            "mit Ihrer Ärztin oder Ihrem Arzt."
        )

    # ── Grenzwertige Sonderfälle als zusätzlicher Hinweis ────────────────────
    if sys >= 140 and 60 <= dia <= 70:
        st.info(
            "ℹ️ Zusätzlicher Hinweis: Ihr diastolischer Wert ist zwar noch im akzeptablen Bereich, "
            "aber relativ tief im Verhältnis zum erhöhten systolischen Wert. "
            "Diese Kombination entspricht einer isolierten systolischen Hypertonie und tritt häufiger "
            "bei älteren Personen auf. Erwähnen Sie diesen Befund bitte Ihrer Ärztin oder "
            "Ihrem Arzt bei der nächsten Kontrolle."
        )

    if 100 <= sys <= 110 and dia >= 90:
        st.info(
            "ℹ️ Zusätzlicher Hinweis: Ihr systolischer Wert ist vergleichsweise tief, "
            "während der diastolische Wert erhöht ist. "
            "Diese Kombination entspricht dem Bild einer isolierten diastolischen Hypertonie "
            "und ist ungewöhnlich – sie kann auf eine Funktionsstörung hinweisen. "
            "Bitte besprechen Sie diesen Befund mit Ihrer Ärztin oder Ihrem Arzt."
        )

def save_bp():
    """Speichert blood_pressure_df in die Cloud."""
    st.session_state["data_manager"].save_user_data(
        st.session_state["blood_pressure_df"], "blood_pressure.csv"
    )

# ── Seiteninhalt ─────────────────────────────────────────────────────────────────
st.markdown("## ❤️ Blutdruck-Tagebuch")
st.markdown(
    '<p style="color:#6b7280">Systolisch & diastolisch in mmHg – Kategorien nach DGK-Leitlinien.</p>',
    unsafe_allow_html=True
)
st.write("")

# ── Eingabe ───────────────────────────────────────────────────────────────────────
with st.form("bp_form"):
    bp_date = st.date_input("Datum", value=date.today())
    c1, c2  = st.columns(2)
    with c1:
        bp_sys = st.number_input(
            "Systolisch – oberer Wert (mmHg)",
            min_value=50, max_value=300, value=120, step=1,
            help="Der obere Wert beim Herzschlag."
        )
    with c2:
        bp_dia = st.number_input(
            "Diastolisch – unterer Wert (mmHg)",
            min_value=30, max_value=200, value=80, step=1,
            help="Der untere Wert in der Entspannungsphase."
        )
    submitted = st.form_submit_button("💾 Blutdruck speichern", use_container_width=True)

if submitted:
    date_str  = bp_date.isoformat()
    df        = st.session_state["blood_pressure_df"]
    new_entry = pd.DataFrame([{
        "date": date_str, "systolic": int(bp_sys), "diastolic": int(bp_dia)
    }])

    if not df.empty and date_str in df["date"].astype(str).values:
        df.loc[df["date"].astype(str) == date_str, ["systolic", "diastolic"]] = [int(bp_sys), int(bp_dia)]
    else:
        df = pd.concat([df, new_entry], ignore_index=True)

    df = df.sort_values("date").reset_index(drop=True)
    st.session_state["blood_pressure_df"] = df
    save_bp()

    status = classify_bp(bp_sys, bp_dia)
    st.markdown(
        f"**Gespeicherter Wert:** {bp_sys}/{bp_dia} mmHg &nbsp; {risk_badge(status)}",
        unsafe_allow_html=True
    )
    st.write("")
    show_status_message(bp_sys, bp_dia, status)

st.divider()

# ── Einträge anzeigen ─────────────────────────────────────────────────────────────
bp_df = st.session_state["blood_pressure_df"]

if bp_df.empty:
    st.info("Noch keine Blutdruckwerte eingetragen.")
else:
    df = bp_df.copy()
    df["systolic"]  = pd.to_numeric(df["systolic"],  errors="coerce")
    df["diastolic"] = pd.to_numeric(df["diastolic"], errors="coerce")
    df["date"]      = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%d.%m.%Y")
    df = df.dropna().sort_values("date")

    # ── Plotly Chart mit Risikozonen ──────────────────────────────────────────────
    st.markdown("#### 📈 Verlauf mit Risikozonen")

    y_max = max(df["systolic"].max(), 185) + 10
    y_min = max(min(df["diastolic"].min(), 55) - 5, 0)

    fig = go.Figure()

    # Farbzonen mit Fachbegriff-Beschriftung, ohne Zahlen
    for y0, y1, color, label in [
        (0,               BP_HYPO_SYS,     "rgba(139,92,246,0.12)", "Hypotonie"),
        (BP_HYPO_SYS,     BP_OPTIMAL_SYS,  "rgba(34,197,94,0.15)",  "Optimal"),
        (BP_OPTIMAL_SYS,  BP_NORMAL_SYS,   "rgba(34,197,94,0.09)",  "Normal"),
        (BP_NORMAL_SYS,   BP_HIGHNORM_SYS, "rgba(251,191,36,0.12)", "Hoch-normal"),
        (BP_HIGHNORM_SYS, BP_HYP1_SYS,     "rgba(251,191,36,0.20)", "Hypertonie Grad 1"),
        (BP_HYP1_SYS,     BP_HYP2_SYS,     "rgba(239,68,68,0.15)",  "Hypertonie Grad 2"),
        (BP_HYP2_SYS,     y_max,            "rgba(185,28,28,0.18)",  "Hypertonie Grad 3"),
    ]:
        if y1 > y_min:
            fig.add_hrect(
                y0=max(y0, y_min), y1=min(y1, y_max),
                fillcolor=color, line_width=0,
                annotation_text=label,
                annotation_position="left",
                annotation_font_size=9,
                annotation_font_color="#6b7280",
            )

    colors = df.apply(
        lambda r: point_color(classify_bp(int(r["systolic"]), int(r["diastolic"]))), axis=1
    )

    fig.add_trace(go.Scatter(
        x=df["date"], y=df["systolic"],
        name="Systolisch", mode="lines+markers",
        line=dict(color="#ef4444", width=2.5),
        marker=dict(size=8, color=colors, line=dict(width=1.5, color="white")),
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["diastolic"],
        name="Diastolisch", mode="lines+markers",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=8, color=colors, line=dict(width=1.5, color="white")),
    ))

    fig.update_layout(
        height=400, margin=dict(l=10, r=10, t=20, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(
            showgrid=False,
            title="Datum",
            tickangle=-30,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f3f4f6",
            title="Blutdruck (mmHg)",
            range=[y_min, y_max]
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Tabelle mit Status-Spalte ──────────────────────────────────────────────────
    st.markdown("#### 📋 Eintragsübersicht")
    rows_html = ""
    for _, row in df.sort_values("date", ascending=False).iterrows():
        status = classify_bp(int(row["systolic"]), int(row["diastolic"]))
        rows_html += f"""<tr>
            <td style='padding:0.5rem 0.75rem'>{e(str(row['date']))}</td>
            <td style='padding:0.5rem 0.75rem;text-align:center'>{int(row['systolic'])}</td>
            <td style='padding:0.5rem 0.75rem;text-align:center'>{int(row['diastolic'])}</td>
            <td style='padding:0.5rem 0.75rem;text-align:center'>{risk_badge(status)}</td>
        </tr>"""

    st.markdown(f"""
    <div class="app-card">
    <table style='width:100%;border-collapse:collapse;font-size:0.9rem'>
        <thead><tr style='border-bottom:2px solid #e5e7eb'>
            <th style='padding:0.5rem 0.75rem;text-align:left'>Datum</th>
            <th style='padding:0.5rem 0.75rem;text-align:center'>Systolisch</th>
            <th style='padding:0.5rem 0.75rem;text-align:center'>Diastolisch</th>
            <th style='padding:0.5rem 0.75rem;text-align:center'>Status</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table></div>""", unsafe_allow_html=True)

    # ── Referenzwerte ──────────────────────────────────────────────────────────────
    with st.expander("ℹ️ Referenzwerte nach DGK-Leitlinien"):
        st.markdown("""
        | Kategorie | Systolisch (mmHg) | Diastolisch (mmHg) |
        |---|---|---|
        | 🟣 Hypotonie | < 100 | < 60 |
        | 🟢 Optimal | < 120 | < 80 |
        | 🟢 Normal | 120 – 129 | 80 – 84 |
        | 🟡 Hoch-normal | 130 – 139 | 85 – 89 |
        | 🟠 Hypertonie Grad 1 | 140 – 159 | 90 – 99 |
        | 🔴 Hypertonie Grad 2 | 160 – 179 | 100 – 109 |
        | 🔴 Hypertonie Grad 3 | ≥ 180 | ≥ 110 |

        *Quelle: Deutsche Gesellschaft für Kardiologie (DGK) / Herzstiftung*

        ---

        **⚠️ Medizinische Sonderfälle**

        | Sonderfall | Systolisch (mmHg) | Diastolisch (mmHg) | Bedeutung |
        |---|---|---|---|
        | Isolierte systolische Hypertonie (kritisch) | ≥ 140 | < 60 | Oberer Wert zu hoch, unterer kritisch tief – dringend ärztlich abklären |
        | Isolierte systolische Hypertonie (grenzwertig) | ≥ 140 | 60 – 70 | Oberer Wert erhöht, unterer grenzwertig tief – beim Arzt erwähnen |
        | Isolierte diastolische Hypertonie (kritisch) | < 100 | ≥ 90 | Oberer Wert zu tief, unterer zu hoch – seltener Befund, sofort abklären |
        | Isolierte diastolische Hypertonie (grenzwertig) | 100 – 110 | ≥ 90 | Oberer Wert tief, unterer erhöht – ungewöhnlich, ärztlich besprechen |

        *Diese Sonderfälle erfordern stets eine individuelle ärztliche Beurteilung.*
        """)

    # ── Löschen ───────────────────────────────────────────────────────────────────
    with st.expander("🗑️ Eintrag löschen"):
        options  = sorted(bp_df["date"].astype(str).tolist(), reverse=True)
        del_date = st.selectbox("Datum wählen", options=options, key="bp_del")
        if st.button("Eintrag löschen", key="bp_del_btn"):
            st.session_state["blood_pressure_df"] = bp_df[
                bp_df["date"].astype(str) != del_date
            ].reset_index(drop=True)
            save_bp()
            st.success("Eintrag gelöscht.")
            st.rerun()