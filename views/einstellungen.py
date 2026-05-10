"""
views/einstellungen.py
Einstellungen: Sprache (DE/FR/IT/EN), Farbthema (9 Optionen).
"""

import streamlit as st
from utils.translations import t, TRANSLATIONS
from utils.themes import inject_theme, THEMES, get_theme

inject_theme()
dm    = st.session_state["data_manager"]
theme = get_theme()

if "settings_loaded" not in st.session_state:
    try:
        saved = dm.load_user_data("settings.json", initial_value={}) or {}
        if saved.get("language"): st.session_state["language"] = saved["language"]
        if saved.get("theme"):    st.session_state["theme"]    = saved["theme"]
    except Exception:
        pass
    st.session_state["settings_loaded"] = True

st.markdown(f"## ⚙️ {t('settings_title')}")
st.write("")

# ── Sprache ───────────────────────────────────────────────────────────────────
st.markdown(f"#### 🌍 {t('settings_language')}")
lang_options = {
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "it": "🇮🇹 Italiano",
    "en": "🇬🇧 English",
}
current_lang = st.session_state.get("language", "de")
cols = st.columns(4)
for i, (code, label) in enumerate(lang_options.items()):
    with cols[i]:
        if st.button(label, key=f"lang_{code}", use_container_width=True):
            st.session_state["language"] = code
            st.rerun()
        is_sel = current_lang == code
        st.markdown(
            f'<div style="text-align:center;font-size:11px;'
            f'color:{theme["primary"] if is_sel else "#9ca3af"};margin-top:-8px">'
            f'{"✓ " + label.split(" ")[1] if is_sel else ""}</div>',
            unsafe_allow_html=True
        )

st.divider()

# ── Farbthema ─────────────────────────────────────────────────────────────────
st.markdown(f"#### 🎨 {t('settings_theme')}")
current_theme = st.session_state.get("theme", "blue")

theme_keys = list(THEMES.keys())
rows = [theme_keys[i:i+3] for i in range(0, len(theme_keys), 3)]

for row in rows:
    cols = st.columns(3)
    for i, key in enumerate(row):
        th = THEMES[key]
        with cols[i]:
            is_sel = current_theme == key
            theme_name = t(th["name_key"]) if "name_key" in th else th["name"]
            if st.button(f"{th['emoji']} {theme_name}", key=f"theme_{key}", use_container_width=True):
                st.session_state["theme"] = key
                st.rerun()
            color = th["primary"] if is_sel else "#9ca3af"
            st.markdown(
                f'<div style="text-align:center;font-size:11px;color:{color};margin-top:-8px">'
                f'{"✓" if is_sel else ""}</div>',
                unsafe_allow_html=True
            )

st.write("")

# Farbvorschau
th_p = THEMES[current_theme]
st.markdown(f"""
<div style="background:{th_p['gradient']};border-radius:14px;padding:1.25rem 1.5rem;
            color:white;display:flex;align-items:center;gap:12px;margin-bottom:1rem">
    <div style="font-size:2rem">{th_p['emoji']}</div>
    <div>
        <div style="font-size:15px;font-weight:600">{t(th_p["name_key"]) if "name_key" in th_p else th_p["name"]}</div>
        <div style="font-size:12px;opacity:0.85">{t('settings_theme_current')}</div>
    </div>
    <div style="margin-left:auto;display:flex;gap:8px">
        <div style="width:24px;height:24px;border-radius:50%;background:{th_p['primary']}"></div>
        <div style="width:24px;height:24px;border-radius:50%;background:{th_p['accent']}"></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Speichern ─────────────────────────────────────────────────────────────────
if st.button(t("save"), use_container_width=True):
    settings = {
        "language": st.session_state.get("language", "de"),
        "theme":    st.session_state.get("theme", "blue"),
    }
    try:
        dm.save_user_data(settings, "settings.json")
        st.success(t("settings_saved"))
    except Exception as ex:
        st.error(f"Fehler beim Speichern: {ex}")
    st.rerun()

st.caption(t("settings_cloud_note"))