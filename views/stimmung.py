"""
views/stimmung.py
Tagesstimmung erfassen: Emoji-Skala, gut/okay/schlecht und Freitext-Kommentar.
Daten werden in stimmung.csv gespeichert.
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

MOOD_OPTIONS = [
    {"key": "great",    "emoji": "😄", "label_key": "mood_great",    "value": 5, "color": "#22c55e"},
    {"key": "good",     "emoji": "🙂", "label_key": "mood_good",     "value": 4, "color": "#84cc16"},
    {"key": "okay",     "emoji": "😐", "label_key": "mood_okay",     "value": 3, "color": "#f59e0b"},
    {"key": "bad",      "emoji": "😕", "label_key": "mood_bad",      "value": 2, "color": "#f97316"},
    {"key": "terrible", "emoji": "😞", "label_key": "mood_terrible", "value": 1, "color": "#ef4444"},
]

dm = st.session_state["data_manager"]

# ── Stimmungsdaten laden ──────────────────────────────────────────────────────
if "mood_df" not in st.session_state:
    try:
        st.session_state["mood_df"] = dm.load_user_data(
            "mood.csv",
            initial_value=pd.DataFrame(columns=["date","mood_key","mood_value","mood_label","note"])
        ) or pd.DataFrame(columns=["date","mood_key","mood_value","mood_label","note"])
    except Exception:
        st.session_state["mood_df"] = pd.DataFrame(columns=["date","mood_key","mood_value","mood_label","note"])

# ── Seite ─────────────────────────────────────────────────────────────────────
st.markdown(f"## 😊 {t('mood_title')}")
st.markdown(f'<p style="color:#6b7280">{t("mood_subtitle")}</p>', unsafe_allow_html=True)
st.write("")

mood_df = st.session_state["mood_df"]
today_str = date.today().isoformat()

# Heute schon erfasst?
today_entry = None
if not mood_df.empty and "date" in mood_df.columns:
    today_rows = mood_df[mood_df["date"] == today_str]
    if not today_rows.empty:
        today_entry = today_rows.iloc[-1]

# ── Aktuelle Stimmung anzeigen ────────────────────────────────────────────────
if today_entry is not None:
    mood_match = next((m for m in MOOD_OPTIONS if m["key"] == today_entry["mood_key"]), MOOD_OPTIONS[2])
    st.markdown(f"""
    <div style="background:{theme['card']};border:1px solid {theme['border']};
                border-radius:16px;padding:1.25rem 1.5rem;margin-bottom:1rem;
                display:flex;align-items:center;gap:16px">
        <div style="font-size:3rem">{mood_match['emoji']}</div>
        <div>
            <div style="font-size:15px;font-weight:600;color:#111827">
                Heute: {t(mood_match['label_key'])}
            </div>
            <div style="font-size:13px;color:#6b7280;margin-top:2px">
                {e(str(today_entry.get('note','') or '')) or 'Kein Kommentar'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Stimmung erfassen / aktualisieren ─────────────────────────────────────────
st.markdown("#### Stimmung erfassen")

selected_mood = st.session_state.get("selected_mood_key", today_entry["mood_key"] if today_entry is not None else "okay")

# Emoji-Auswahl
cols = st.columns(5)
for i, mood in enumerate(MOOD_OPTIONS):
    with cols[i]:
        is_sel = selected_mood == mood["key"]
        border = f"3px solid {mood['color']}" if is_sel else f"1px solid {theme['border']}"
        bg     = f"{mood['color']}22" if is_sel else theme["card"]
        if st.button(mood["emoji"], key=f"mood_btn_{mood['key']}", use_container_width=True):
            st.session_state["selected_mood_key"] = mood["key"]
            st.rerun()
        st.markdown(
            f'<div style="text-align:center;font-size:11px;color:{mood["color"] if is_sel else "#9ca3af"};'
            f'margin-top:-8px;font-weight:{"600" if is_sel else "400"}">{t(mood["label_key"])}</div>',
            unsafe_allow_html=True
        )

st.write("")

with st.form("mood_form"):
    mood_date = st.date_input("Datum", value=date.today())
    note_in   = st.text_area(
        t("mood_note"),
        value=str(today_entry["note"]) if today_entry is not None and pd.notna(today_entry.get("note")) else "",
        placeholder="Wie war dein Tag? Irgendwelche Symptome? Besondere Ereignisse?",
        height=100
    )
    submitted = st.form_submit_button(t("mood_save"), use_container_width=True)

if submitted:
    sel_key   = st.session_state.get("selected_mood_key", "okay")
    sel_mood  = next((m for m in MOOD_OPTIONS if m["key"] == sel_key), MOOD_OPTIONS[2])
    date_str  = mood_date.isoformat()

    df = st.session_state["mood_df"]
    new_row = pd.DataFrame([{
        "date":       date_str,
        "mood_key":   sel_mood["key"],
        "mood_value": sel_mood["value"],
        "mood_label": t(sel_mood["label_key"]),
        "note":       note_in.strip(),
    }])

    if not df.empty and date_str in df["date"].astype(str).values:
        df = df[df["date"].astype(str) != date_str]

    df = pd.concat([df, new_row], ignore_index=True).sort_values("date")
    st.session_state["mood_df"] = df
    dm.save_user_data(df, "mood.csv")
    st.success(t("mood_saved"))
    st.rerun()

st.divider()

# ── Verlauf ───────────────────────────────────────────────────────────────────
st.markdown(f"#### 📈 {t('mood_history')}")

if mood_df.empty:
    st.info(t("mood_none"))
else:
    df_plot = mood_df.copy()
    df_plot["date"]       = pd.to_datetime(df_plot["date"], errors="coerce")
    df_plot["mood_value"] = pd.to_numeric(df_plot["mood_value"], errors="coerce")
    df_plot = df_plot.dropna().sort_values("date").tail(30)

    # Datum als sauberer String für X-Achse (chronologisch sortiert)
    df_plot["date_str"] = df_plot["date"].dt.strftime("%d.%m.%Y")

    point_colors = df_plot["mood_value"].apply(
        lambda v: "#22c55e" if v >= 4 else ("#f59e0b" if v == 3 else "#ef4444")
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot["date_str"],
        y=df_plot["mood_value"],
        mode="lines+markers",
        line=dict(color=theme["primary"], width=2.5),
        marker=dict(size=10, color=point_colors, line=dict(width=2, color="white")),
        text=df_plot["mood_value"].apply(
            lambda v: next((m["emoji"] for m in MOOD_OPTIONS if m["value"] == v), "")
        ),
        hovertemplate="%{x}<br>%{text}<extra></extra>",
    ))

    fig.update_layout(
        height=280, margin=dict(l=10,r=10,t=10,b=40),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(
            showgrid=False,
            title="Datum",
            tickangle=-30,
            tickfont=dict(size=11),
            categoryorder="array",
            categoryarray=df_plot["date_str"].tolist(),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#f3f4f6",
            tickvals=[1,2,3,4,5],
            ticktext=["😞 Sehr schlecht","😕 Schlecht","😐 Okay","🙂 Gut","😄 Sehr gut"],
            range=[0.5, 5.5],
            title="Stimmung",
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Letzte Einträge als Karten
    st.markdown("#### Letzte Einträge")
    for _, row in df_plot.sort_values("date", ascending=False).head(7).iterrows():
        mood_match = next((m for m in MOOD_OPTIONS if m["value"] == int(row["mood_value"])), MOOD_OPTIONS[2])
        note_text  = str(row["note"]).strip() if pd.notna(row.get("note")) and str(row.get("note","")).strip() else "—"
        st.markdown(f"""
        <div style="background:{theme['card']};border:1px solid {theme['border']};
                    border-radius:12px;padding:0.75rem 1rem;margin-bottom:0.4rem;
                    display:flex;align-items:center;gap:10px">
            <div style="font-size:1.5rem">{mood_match['emoji']}</div>
            <div style="flex:1">
                <div style="font-size:13px;font-weight:600">{t(mood_match['label_key'])}</div>
                <div style="font-size:12px;color:#6b7280">{e(note_text)}</div>
            </div>
            <div style="font-size:11px;color:#9ca3af">{row['date'].strftime('%d.%m.%Y')}</div>
        </div>
        """, unsafe_allow_html=True)