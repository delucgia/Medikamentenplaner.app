"""
utils/themes.py
Farbthemen für MediTrack – 9 helle Themen, kein Dunkel-Modus.
inject_theme() wird in app.py einmalig aufgerufen und gilt für alle Seiten.
"""

THEMES = {
    "blue": {
        "name": "Ozean-Blau", "emoji": "🌊",
        "primary": "#2563eb", "primary_light": "#eff6ff", "primary_text": "#1d4ed8",
        "accent": "#0ea5e9", "bg": "#f4f6fb", "card": "#ffffff", "border": "#e5e7eb",
        "pill_icon_bg": "#eff6ff", "metric_bg": "#f9fafb",
        "sidebar_bg": "#1e3a5f", "sidebar_text": "#e0f0ff",
        "gradient": "linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%)",
    },
    "purple": {
        "name": "Lila", "emoji": "💜",
        "primary": "#7c3aed", "primary_light": "#f5f3ff", "primary_text": "#6d28d9",
        "accent": "#a78bfa", "bg": "#faf5ff", "card": "#ffffff", "border": "#e9d5ff",
        "pill_icon_bg": "#f5f3ff", "metric_bg": "#faf5ff",
        "sidebar_bg": "#3b1f6e", "sidebar_text": "#ede9fe",
        "gradient": "linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%)",
    },
    "green": {
        "name": "Smaragd", "emoji": "🌿",
        "primary": "#059669", "primary_light": "#ecfdf5", "primary_text": "#047857",
        "accent": "#34d399", "bg": "#f0fdf4", "card": "#ffffff", "border": "#d1fae5",
        "pill_icon_bg": "#ecfdf5", "metric_bg": "#f0fdf4",
        "sidebar_bg": "#14532d", "sidebar_text": "#d1fae5",
        "gradient": "linear-gradient(135deg, #059669 0%, #34d399 100%)",
    },
    "rose": {
        "name": "Rosa", "emoji": "🌹",
        "primary": "#e11d48", "primary_light": "#fff1f2", "primary_text": "#be123c",
        "accent": "#fb7185", "bg": "#fff5f7", "card": "#ffffff", "border": "#fecdd3",
        "pill_icon_bg": "#fff1f2", "metric_bg": "#fff5f7",
        "sidebar_bg": "#881337", "sidebar_text": "#fecdd3",
        "gradient": "linear-gradient(135deg, #e11d48 0%, #fb7185 100%)",
    },
    "orange": {
        "name": "Sonnenschein", "emoji": "🌅",
        "primary": "#ea580c", "primary_light": "#fff7ed", "primary_text": "#c2410c",
        "accent": "#fb923c", "bg": "#fff7ed", "card": "#ffffff", "border": "#fed7aa",
        "pill_icon_bg": "#fff7ed", "metric_bg": "#fff7ed",
        "sidebar_bg": "#7c2d12", "sidebar_text": "#fed7aa",
        "gradient": "linear-gradient(135deg, #ea580c 0%, #fb923c 100%)",
    },
    "teal": {
        "name": "Türkis", "emoji": "🩵",
        "primary": "#0d9488", "primary_light": "#f0fdfa", "primary_text": "#0f766e",
        "accent": "#2dd4bf", "bg": "#f0fdfa", "card": "#ffffff", "border": "#99f6e4",
        "pill_icon_bg": "#f0fdfa", "metric_bg": "#f0fdfa",
        "sidebar_bg": "#134e4a", "sidebar_text": "#ccfbf1",
        "gradient": "linear-gradient(135deg, #0d9488 0%, #2dd4bf 100%)",
    },
    "sky": {
        "name": "Himmelblau", "emoji": "☀️",
        "primary": "#0284c7", "primary_light": "#f0f9ff", "primary_text": "#0369a1",
        "accent": "#38bdf8", "bg": "#f0f9ff", "card": "#ffffff", "border": "#bae6fd",
        "pill_icon_bg": "#e0f2fe", "metric_bg": "#f0f9ff",
        "sidebar_bg": "#0c4a6e", "sidebar_text": "#e0f2fe",
        "gradient": "linear-gradient(135deg, #0284c7 0%, #38bdf8 100%)",
    },
    "mint": {
        "name": "Minze", "emoji": "🌱",
        "primary": "#16a34a", "primary_light": "#f0fdf4", "primary_text": "#15803d",
        "accent": "#4ade80", "bg": "#f7fef9", "card": "#ffffff", "border": "#bbf7d0",
        "pill_icon_bg": "#dcfce7", "metric_bg": "#f0fdf4",
        "sidebar_bg": "#14532d", "sidebar_text": "#bbf7d0",
        "gradient": "linear-gradient(135deg, #16a34a 0%, #4ade80 100%)",
    },
    "lavender": {
        "name": "Lavendel", "emoji": "🪻",
        "primary": "#8b5cf6", "primary_light": "#f5f3ff", "primary_text": "#7c3aed",
        "accent": "#c4b5fd", "bg": "#faf9ff", "card": "#ffffff", "border": "#ddd6fe",
        "pill_icon_bg": "#ede9fe", "metric_bg": "#f5f3ff",
        "sidebar_bg": "#4c1d95", "sidebar_text": "#ede9fe",
        "gradient": "linear-gradient(135deg, #8b5cf6 0%, #c4b5fd 100%)",
    },
}

def get_theme():
    import streamlit as st
    return THEMES.get(st.session_state.get("theme", "blue"), THEMES["blue"])

def inject_theme():
    """
    Injiziert das komplette Theme-CSS.
    Muss in app.py VOR pg.run() aufgerufen werden damit es auf allen Seiten gilt.
    """
    import streamlit as st
    theme = get_theme()

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
        background-color: {theme['bg']} !important;
        color: #111827;
    }}
    .main {{ background-color: {theme['bg']} !important; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}

    /* Cards & components */
    .metric-card {{ background:{theme['metric_bg']};border:1px solid {theme['border']};border-radius:14px;padding:1rem 1.1rem; }}
    .metric-label {{ font-size:12px;color:#6b7280;margin-bottom:4px; }}
    .metric-value {{ font-size:24px;font-weight:700;color:#111827; }}
    .metric-sub   {{ font-size:11px;color:#9ca3af;margin-top:2px; }}
    .pill-card    {{ background:{theme['card']};border:1px solid {theme['border']};border-radius:14px;padding:0.85rem 1rem;margin-bottom:0.5rem;display:flex;align-items:center;gap:12px; }}
    .pill-icon    {{ width:40px;height:40px;border-radius:10px;background:{theme['pill_icon_bg']};display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0; }}
    .pill-name    {{ font-size:14px;font-weight:600;color:#111827; }}
    .pill-meta    {{ font-size:12px;color:#6b7280;margin-top:1px; }}
    .pill-right   {{ display:flex;flex-direction:column;align-items:flex-end;gap:5px;flex-shrink:0; }}
    .time-chip    {{ font-size:11px;font-weight:600;background:{theme['metric_bg']};color:#6b7280;padding:2px 8px;border-radius:7px;font-family:monospace; }}
    .badge-done   {{ font-size:11px;font-weight:600;color:#15803d;background:#dcfce7;padding:2px 8px;border-radius:999px; }}
    .badge-pending{{ font-size:11px;font-weight:600;color:#b45309;background:#fef3c7;padding:2px 8px;border-radius:999px; }}
    .alert-banner {{ background:#fffbeb;border:1px solid #fde68a;border-radius:12px;padding:0.65rem 1rem;font-size:13px;color:#92400e;display:flex;align-items:center;gap:8px;margin-bottom:0.4rem; }}
    .adhere-card  {{ background:{theme['card']};border:1px solid {theme['border']};border-radius:14px;padding:0.9rem 1.1rem;margin-bottom:0.5rem; }}
    .progress-track {{ height:6px;background:{theme['border']};border-radius:99px;overflow:hidden; }}
    .progress-fill  {{ height:100%;border-radius:99px; }}
    .health-card  {{ background:{theme['card']};border:1px solid {theme['border']};border-radius:14px;padding:1rem 1.1rem;margin-bottom:0.5rem; }}
    .app-card     {{ background:{theme['card']};padding:1.25rem 1.5rem;border-radius:20px;border:1px solid {theme['border']};margin-bottom:1rem;overflow-x:auto; }}
    .section-label{{ font-size:13px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;margin:1.25rem 0 0.65rem; }}
    .status-ok    {{ color:#15803d; }} .status-warn {{ color:#b45309; }}
    .status-crit  {{ color:#b91c1c; }} .status-hypo {{ color:#6d28d9; }}
    .muted        {{ color:#6b7280;font-size:0.9rem; }}
    div.stButton > button {{ border-radius:10px;font-weight:600;min-height:38px;font-size:13px; }}

    /* Sidebar — gilt global für alle Pages */
    section[data-testid="stSidebar"] {{
        background: {theme['sidebar_bg']} !important;
    }}
    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] a {{
        color: {theme['sidebar_text']} !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button {{
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: {theme['sidebar_text']} !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button:hover {{
        background: rgba(255,255,255,0.15) !important;
    }}
    /* Streamlit navigation links in sidebar */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span {{
        color: {theme['sidebar_text']} !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li[aria-selected="true"] {{
        background: rgba(255,255,255,0.15) !important;
        border-radius: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)