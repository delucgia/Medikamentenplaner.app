"""
views/pdf_export.py
PDF-Export: Nutzer wählt welche Daten exportiert werden sollen.
"""

import streamlit as st
import pandas as pd
from utils.themes import inject_theme, get_theme

inject_theme()
theme = get_theme()

st.markdown("## 📄 PDF-Export")
st.markdown('<p style="color:#6b7280">Wähle aus welche Gesundheitsdaten du exportieren möchtest.</p>',
            unsafe_allow_html=True)
st.write("")

# ── Verfügbare Daten prüfen ───────────────────────────────────────────────────
intakes_df = st.session_state.get("intakes_df", pd.DataFrame())
bp_df      = st.session_state.get("blood_pressure_df", pd.DataFrame())
bs_df      = st.session_state.get("blood_sugar_df", pd.DataFrame())
mood_df    = st.session_state.get("mood_df", pd.DataFrame())
profile    = st.session_state.get("profile", {})

has_intakes = not intakes_df.empty
has_bp      = not bp_df.empty
has_bs      = not bs_df.empty
has_mood    = not mood_df.empty

if not any([has_intakes, has_bp, has_bs, has_mood]):
    st.info("Noch keine Daten vorhanden. Erfasse zuerst einige Werte.")
    st.stop()

# ── Auswahl-Karten ────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{theme['card']};border:1px solid {theme['border']};
            border-radius:16px;padding:1.25rem 1.5rem;margin-bottom:1rem">
    <div style="font-size:14px;font-weight:600;color:#111827;margin-bottom:1rem">
        Was soll im PDF enthalten sein?
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    inc_intakes = st.checkbox(
        f"💊 Medikamenten-Einnahmen {'(' + str(len(intakes_df)) + ' Einträge)' if has_intakes else '(keine Daten)'}",
        value=has_intakes, disabled=not has_intakes
    )
    inc_bp = st.checkbox(
        f"❤️ Blutdruck {'(' + str(len(bp_df)) + ' Messungen)' if has_bp else '(keine Daten)'}",
        value=has_bp, disabled=not has_bp
    )

with col2:
    inc_bs = st.checkbox(
        f"🩸 Blutzucker {'(' + str(len(bs_df)) + ' Messungen)' if has_bs else '(keine Daten)'}",
        value=has_bs, disabled=not has_bs
    )
    inc_mood = st.checkbox(
        f"😊 Stimmungsverlauf {'(' + str(len(mood_df)) + ' Einträge)' if has_mood else '(keine Daten)'}",
        value=has_mood, disabled=not has_mood
    )

st.markdown("</div>", unsafe_allow_html=True)

# ── Profil-Info ───────────────────────────────────────────────────────────────
firstname = profile.get("firstname","")
lastname  = profile.get("lastname","")
fullname  = f"{firstname} {lastname}".strip()

if fullname or profile.get("doctor"):
    st.markdown(f"""
    <div style="background:{theme['metric_bg']};border:1px solid {theme['border']};
                border-radius:12px;padding:0.75rem 1rem;margin-bottom:1rem;font-size:13px">
        <span style="color:#6b7280">Das PDF wird erstellt für: </span>
        <strong>{fullname or "Unbekannt"}</strong>
        {f" · {profile.get('doctor','')}" if profile.get('doctor') else ""}
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("💡 Tipp: Ergänze dein Profil unter 👤 Profil für ein vollständigeres PDF.")

# ── Vorschau ──────────────────────────────────────────────────────────────────
selected = []
if inc_intakes and has_intakes: selected.append("💊 Einnahmen")
if inc_bp and has_bp:           selected.append("❤️ Blutdruck")
if inc_bs and has_bs:           selected.append("🩸 Blutzucker")
if inc_mood and has_mood:       selected.append("😊 Stimmung")

if selected:
    st.markdown(f'<p style="font-size:13px;color:#6b7280">Ausgewählt: {" · ".join(selected)}</p>',
                unsafe_allow_html=True)

# ── Export-Button ─────────────────────────────────────────────────────────────
if not selected:
    st.warning("Bitte wähle mindestens einen Bereich aus.")
else:
    if st.button("📄 PDF erstellen", use_container_width=True, type="primary"):
        try:
            from utils.pdf_export import generate_pdf
            with st.spinner("PDF wird erstellt..."):
                pdf_bytes = generate_pdf(
                    profile=profile,
                    include_intakes=inc_intakes and has_intakes,
                    include_bp=inc_bp and has_bp,
                    include_bs=inc_bs and has_bs,
                    include_mood=inc_mood and has_mood,
                    intakes_df=intakes_df if inc_intakes else None,
                    bp_df=bp_df if inc_bp else None,
                    bs_df=bs_df if inc_bs else None,
                    mood_df=mood_df if inc_mood else None,
                )

            sections = "_".join([
                "einnahmen" if inc_intakes else "",
                "blutdruck" if inc_bp else "",
                "blutzucker" if inc_bs else "",
                "stimmung" if inc_mood else "",
            ]).strip("_").replace("__","_")

            filename = f"meditrack_{sections}.pdf"

            st.download_button(
                label="💾 PDF herunterladen",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
            )
            st.success("✅ PDF erfolgreich erstellt!")

        except ImportError:
            st.error("fpdf2 ist nicht installiert. Bitte füge 'fpdf2' zur requirements.txt hinzu.")
        except Exception as ex:
            st.error(f"Fehler beim Erstellen des PDFs: {ex}")