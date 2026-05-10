"""
views/pdf_export.py
PDF-Export: Nutzer wählt welche Daten exportiert werden sollen.
Vollständig übersetzt via utils/translations.py
"""

import streamlit as st
import pandas as pd
from utils.translations import t
from utils.themes import inject_theme, get_theme

inject_theme()
theme = get_theme()

st.markdown(f"## 📄 {t('pdf_title')}")
st.markdown(
    f'<p style="color:#6b7280">{t("pdf_subtitle")}</p>',
    unsafe_allow_html=True
)
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
    st.info(t("no_data"))
    st.stop()

# ── Auswahl ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{theme['card']};border:1px solid {theme['border']};
            border-radius:16px;padding:1.25rem 1.5rem;margin-bottom:1rem">
    <div style="font-size:14px;font-weight:600;color:#111827;margin-bottom:1rem">
        {t('pdf_what')}
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if has_intakes:
        inc_intakes = st.checkbox(
            f"💊 {t('pdf_intakes')} ({len(intakes_df)} {t('pdf_entries')})",
            value=True
        )
    else:
        st.checkbox(f"💊 {t('pdf_intakes')} ({t('pdf_no_data')})", value=False, disabled=True)
        inc_intakes = False

    if has_bp:
        inc_bp = st.checkbox(
            f"❤️ {t('health_bp')} ({len(bp_df)} {t('pdf_measurements')})",
            value=True
        )
    else:
        st.checkbox(f"❤️ {t('health_bp')} ({t('pdf_no_data')})", value=False, disabled=True)
        inc_bp = False

with col2:
    if has_bs:
        inc_bs = st.checkbox(
            f"🩸 {t('health_bs')} ({len(bs_df)} {t('pdf_measurements')})",
            value=True
        )
    else:
        st.checkbox(f"🩸 {t('health_bs')} ({t('pdf_no_data')})", value=False, disabled=True)
        inc_bs = False

    if has_mood:
        inc_mood = st.checkbox(
            f"😊 {t('mood_title')} ({len(mood_df)} {t('pdf_entries')})",
            value=True
        )
    else:
        st.checkbox(f"😊 {t('mood_title')} ({t('pdf_no_data')})", value=False, disabled=True)
        inc_mood = False

st.markdown("</div>", unsafe_allow_html=True)

# ── Profil-Info ───────────────────────────────────────────────────────────────
firstname = profile.get("firstname", "")
lastname  = profile.get("lastname", "")
fullname  = f"{firstname} {lastname}".strip()

if fullname or profile.get("doctor"):
    st.markdown(f"""
    <div style="background:{theme['metric_bg']};border:1px solid {theme['border']};
                border-radius:12px;padding:0.75rem 1rem;margin-bottom:1rem;font-size:13px">
        <span style="color:#6b7280">{t('pdf_for')}: </span>
        <strong>{fullname or t('pdf_unknown')}</strong>
        {f" · {profile.get('doctor','')}" if profile.get('doctor') else ""}
    </div>
    """, unsafe_allow_html=True)
else:
    st.info(f"💡 {t('pdf_tip')} 👤 {t('nav_profile')} {t('pdf_tip2')}")

# ── Vorschau ──────────────────────────────────────────────────────────────────
selected_sections = []
if inc_intakes and has_intakes: selected_sections.append(f"💊 {t('pdf_intakes')}")
if inc_bp and has_bp:           selected_sections.append(f"❤️ {t('health_bp')}")
if inc_bs and has_bs:           selected_sections.append(f"🩸 {t('health_bs')}")
if inc_mood and has_mood:       selected_sections.append(f"😊 {t('mood_title')}")

if selected_sections:
    st.markdown(
        f'<p style="font-size:13px;color:#6b7280">{t("pdf_selected")}: '
        f'{" · ".join(selected_sections)}</p>',
        unsafe_allow_html=True
    )

# ── Export-Button ─────────────────────────────────────────────────────────────
if not selected_sections:
    st.warning(t("pdf_select_min"))
else:
    if st.button(t("pdf_create"), use_container_width=True, type="primary"):
        try:
            from utils.pdf_export import generate_pdf
            with st.spinner("PDF..."):
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

            parts = []
            if inc_intakes and has_intakes: parts.append("einnahmen")
            if inc_bp and has_bp:           parts.append("blutdruck")
            if inc_bs and has_bs:           parts.append("blutzucker")
            if inc_mood and has_mood:       parts.append("stimmung")
            filename = f"meditrack_{'_'.join(parts)}.pdf"

            st.download_button(
                label=t("pdf_download"),
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
            )
            st.success(f"✅ {t('pdf_success')}")

        except ImportError:
            st.error(t("pdf_error_fpdf"))
        except Exception as ex:
            st.error(f"Error: {ex}")