"""
views/profil.py
Profilseite: Persönliche Angaben, Notfallkontakt, Blutgruppe, Allergien.
"""

import streamlit as st
import pandas as pd
from datetime import date
from utils.translations import t
from utils.themes import inject_theme, get_theme

inject_theme()
theme = get_theme()

st.markdown(f"## 👤 {t('profile_title')}")
st.markdown(f'<p style="color:#6b7280">{t("profile_subtitle")}</p>', unsafe_allow_html=True)
st.write("")

dm = st.session_state["data_manager"]

if "profile" not in st.session_state:
    try:
        st.session_state["profile"] = dm.load_user_data("profile.json", initial_value={}) or {}
    except Exception:
        st.session_state["profile"] = {}

profile = st.session_state["profile"]

# ── Profil-Header ─────────────────────────────────────────────────────────────
firstname = profile.get("firstname", "")
lastname  = profile.get("lastname", "")
initials  = f"{firstname[:1]}{lastname[:1]}".upper() if (firstname or lastname) else "?"

st.markdown(f"""
<div style="display:flex;align-items:center;gap:16px;margin-bottom:1.5rem;
            background:{theme['card']};border:1px solid {theme['border']};
            border-radius:16px;padding:1.25rem 1.5rem">
    <div style="width:64px;height:64px;border-radius:50%;
                background:{theme['gradient']};
                display:flex;align-items:center;justify-content:center;
                font-size:1.5rem;font-weight:700;color:white;flex-shrink:0">
        {initials}
    </div>
    <div>
        <div style="font-size:1.2rem;font-weight:700;color:#111827">
            {(firstname + " " + lastname).strip() or t("profile_no_name")}
        </div>
        <div style="font-size:13px;color:#6b7280;margin-top:2px">
            {profile.get("doctor", t("profile_no_doctor"))}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tab_personal, tab_medical, tab_emergency = st.tabs([
    f"👤 {t('profile_personal_tab')}",
    f"🏥 {t('profile_medical_tab')}",
    f"🆘 {t('profile_emergency_tab')}"
])

# ── Tab 1: Persönlich ─────────────────────────────────────────────────────────
with tab_personal:
    with st.form("profile_personal"):
        c1, c2 = st.columns(2)
        with c1:
            firstname_in = st.text_input(t("profile_firstname"), value=profile.get("firstname",""))
        with c2:
            lastname_in  = st.text_input(t("profile_lastname"),  value=profile.get("lastname",""))

        st.markdown(f"**{t('profile_birthdate')}**")
        bd_str = profile.get("birthdate","")
        try:
            from datetime import datetime
            bd_parsed = datetime.strptime(bd_str, "%Y-%m-%d")
            bd_day, bd_month, bd_year = bd_parsed.day, bd_parsed.month, bd_parsed.year
        except Exception:
            bd_day, bd_month, bd_year = 1, 1, 1970

        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            day_in   = st.number_input(t("profile_birthdate_day"),   min_value=1,    max_value=31,  value=bd_day,   step=1)
        with bc2:
            month_in = st.number_input(t("profile_birthdate_month"), min_value=1,    max_value=12,  value=bd_month, step=1)
        with bc3:
            year_in  = st.number_input(t("profile_birthdate_year"),  min_value=1900, max_value=date.today().year, value=bd_year, step=1)

        doctor_in = st.text_input(t("profile_doctor"), value=profile.get("doctor",""))

        if st.form_submit_button(t("save"), use_container_width=True):
            try:
                bd_out = date(int(year_in), int(month_in), int(day_in)).isoformat()
            except Exception:
                bd_out = ""
                st.warning(t("profile_invalid_date"))
            profile.update({
                "firstname": firstname_in.strip(),
                "lastname":  lastname_in.strip(),
                "birthdate": bd_out,
                "doctor":    doctor_in.strip(),
            })
            st.session_state["profile"] = profile
            dm.save_user_data(profile, "profile.json")
            st.success(t("profile_saved"))
            st.rerun()

# ── Tab 2: Medizinisch ────────────────────────────────────────────────────────
with tab_medical:
    with st.form("profile_medical"):
        blood_options = ["—","A+","A−","B+","B−","AB+","AB−","0+","0−"]
        current_blood = profile.get("blood_type","—")
        blood_idx     = blood_options.index(current_blood) if current_blood in blood_options else 0
        blood_type_in = st.selectbox(t("profile_blood_type"), options=blood_options, index=blood_idx)
        allergies_in  = st.text_area(t("profile_allergies"), value=profile.get("allergies",""), height=100)
        if st.form_submit_button(t("save"), use_container_width=True):
            profile.update({"blood_type": blood_type_in, "allergies": allergies_in.strip()})
            st.session_state["profile"] = profile
            dm.save_user_data(profile, "profile.json")
            st.success(t("profile_saved"))

# ── Tab 3: Notfall ────────────────────────────────────────────────────────────
with tab_emergency:
    with st.form("profile_emergency"):
        emergency_in = st.text_input(t("profile_emergency"), value=profile.get("emergency",""))
        emergency_phone_in = st.text_input(t("profile_emergency_phone"), value=profile.get("emergency_phone",""))
        if st.form_submit_button(t("save"), use_container_width=True):
            profile.update({
                "emergency":       emergency_in.strip(),
                "emergency_phone": emergency_phone_in.strip(),
            })
            st.session_state["profile"] = profile
            dm.save_user_data(profile, "profile.json")
            st.success(t("profile_saved"))

# ── Übersicht ─────────────────────────────────────────────────────────────────
if any([profile.get("firstname"), profile.get("blood_type"), profile.get("emergency")]):
    st.divider()
    st.markdown(f"#### 📋 {t('profile_saved_data')}")

    def row(label, value):
        if value and str(value).strip() and str(value) != "—":
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:0.4rem 0;'
                f'border-bottom:1px solid #f3f4f6;font-size:14px">'
                f'<span style="color:#6b7280">{label}</span>'
                f'<span style="font-weight:500">{value}</span></div>',
                unsafe_allow_html=True
            )

    row(f"{t('profile_firstname')} / {t('profile_lastname')}",
        f"{profile.get('firstname','')} {profile.get('lastname','')}".strip())
    row(t("profile_birthdate"),       profile.get("birthdate",""))
    row(t("profile_doctor"),          profile.get("doctor",""))
    row(t("profile_blood_type"),      profile.get("blood_type",""))
    row(t("profile_allergies"),       profile.get("allergies",""))
    row(t("profile_emergency"),       profile.get("emergency",""))
    row(t("profile_emergency_phone"), profile.get("emergency_phone",""))