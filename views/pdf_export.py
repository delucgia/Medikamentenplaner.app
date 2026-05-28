"""
views/pdf_export.py
PDF-Export: Nutzer wählt welche Daten exportiert werden sollen.
"""

import streamlit as st
import pandas as pd
from utils.translations import t
from functions.data_helpers import load_all_health_data
from utils.themes import inject_theme, get_theme

inject_theme()
theme = get_theme()

# ── Titel ─────────────────────────────────────────────────────────────────────
st.markdown(f"## 📄 {t('pdf_title')}")
st.caption(t("pdf_subtitle"))
st.write("")

# ── Daten laden ───────────────────────────────────────────────────────────────
intakes_df, bp_df, bs_df, mood_df, _, profile = load_all_health_data()

has_intakes = not intakes_df.empty
has_bp      = not bp_df.empty
has_bs      = not bs_df.empty
has_mood    = not mood_df.empty

if not any([has_intakes, has_bp, has_bs, has_mood]):
    st.info(t("no_data"))
    st.stop()

# ── Auswahl ───────────────────────────────────────────────────────────────────
st.markdown(f"**{t('pdf_what')}**")

col1, col2 = st.columns(2)

with col1:
    if has_intakes:
        inc_intakes = st.checkbox(
            f"💊 {t('pdf_intakes')} ({len(intakes_df)} {t('pdf_entries')})",
            value=True
        )
    else:
        st.checkbox(
            f"💊 {t('pdf_intakes')} ({t('pdf_no_data')})",
            value=False, disabled=True
        )
        inc_intakes = False

    if has_bp:
        inc_bp = st.checkbox(
            f"❤️ {t('health_bp')} ({len(bp_df)} {t('pdf_measurements')})",
            value=True
        )
    else:
        st.checkbox(
            f"❤️ {t('health_bp')} ({t('pdf_no_data')})",
            value=False, disabled=True
        )
        inc_bp = False

with col2:
    if has_bs:
        inc_bs = st.checkbox(
            f"🩸 {t('health_bs')} ({len(bs_df)} {t('pdf_measurements')})",
            value=True
        )
    else:
        st.checkbox(
            f"🩸 {t('health_bs')} ({t('pdf_no_data')})",
            value=False, disabled=True
        )
        inc_bs = False

    if has_mood:
        inc_mood = st.checkbox(
            f"😊 {t('mood_title')} ({len(mood_df)} {t('pdf_entries')})",
            value=True
        )
    else:
        st.checkbox(
            f"😊 {t('mood_title')} ({t('pdf_no_data')})",
            value=False, disabled=True
        )
        inc_mood = False

st.write("")

# ── Profil-Info ───────────────────────────────────────────────────────────────
firstname = profile.get("firstname", "")
lastname  = profile.get("lastname", "")
fullname  = f"{firstname} {lastname}".strip()
doctor    = profile.get("doctor", "")

if fullname or doctor:
    info_text = f"**{t('pdf_for')}:** {fullname or t('pdf_unknown')}"
    if doctor:
        info_text += f"  ·  {doctor}"
    st.info(info_text)
else:
    st.info(f"💡 {t('pdf_tip')} 👤 {t('nav_profile')} {t('pdf_tip2')}")

# ── Vorschau ──────────────────────────────────────────────────────────────────
selected_sections = []
if inc_intakes and has_intakes: selected_sections.append(f"💊 {t('pdf_intakes')}")
if inc_bp and has_bp:           selected_sections.append(f"❤️ {t('health_bp')}")
if inc_bs and has_bs:           selected_sections.append(f"🩸 {t('health_bs')}")
if inc_mood and has_mood:       selected_sections.append(f"😊 {t('mood_title')}")

if selected_sections:
    st.caption(f"{t('pdf_selected')}: {'  ·  '.join(selected_sections)}")

# ── Export-Button ─────────────────────────────────────────────────────────────
st.write("")

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