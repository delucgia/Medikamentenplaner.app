"""
utils/vita.py
MediTrack-Maskottchen: Vita (Herz), Medi (Pille), Dr. Care (Doktor).
Jedes Maskottchen hat 4 Stimmungen: happy, excited, worried, sleepy.
"""


def get_mascot() -> str:
    """Gibt das aktuell gewählte Maskottchen zurück."""
    import streamlit as st
    return st.session_state.get("mascot", "vita")


def mascot_svg(mood: str = "happy", size: int = 100, mascot: str = None) -> str:
    """
    Gibt SVG-Code für das gewählte Maskottchen zurück.
    mascot: 'vita' | 'medi' | 'drcare' (None = aus session_state)
    mood:   'happy' | 'excited' | 'worried' | 'sleepy'
    """
    if mascot is None:
        mascot = get_mascot()

    if mascot == "medi":
        return medi_svg(mood, size)
    elif mascot == "drcare":
        return drcare_svg(mood, size)
    else:
        return vita_svg(mood, size)


# ── VITA (Herz-Figur) ─────────────────────────────────────────────────────────

def vita_svg(mood: str = "happy", size: int = 100) -> str:
    s = size
    h = int(s * 1.3)

    if mood == "happy":
        return f"""<svg width="{s}" height="{h}" viewBox="0 0 100 130" xmlns="http://www.w3.org/2000/svg">
  <path d="M50 95 C15 70 15 28 50 40 C85 28 85 70 50 95Z" fill="#f472b6"/>
  <ellipse cx="30" cy="64" rx="6" ry="4" fill="#fda4af" opacity="0.6"/>
  <ellipse cx="70" cy="64" rx="6" ry="4" fill="#fda4af" opacity="0.6"/>
  <circle cx="40" cy="54" r="6" fill="white"/>
  <circle cx="60" cy="54" r="6" fill="white"/>
  <circle cx="41" cy="55" r="3" fill="#9d174d"/>
  <circle cx="61" cy="55" r="3" fill="#9d174d"/>
  <circle cx="40" cy="53" r="1" fill="white"/>
  <circle cx="60" cy="53" r="1" fill="white"/>
  <path d="M42 68 Q50 76 58 68" stroke="#9d174d" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M20 58 Q8 48 10 36" stroke="#f472b6" stroke-width="8" stroke-linecap="round" fill="none"/>
  <path d="M80 58 Q92 48 90 36" stroke="#f472b6" stroke-width="8" stroke-linecap="round" fill="none"/>
  <circle cx="10" cy="34" r="6" fill="#fb7185"/>
  <circle cx="90" cy="34" r="6" fill="#fb7185"/>
  <path d="M44 94 Q40 110 36 120" stroke="#f472b6" stroke-width="8" stroke-linecap="round" fill="none"/>
  <path d="M56 94 Q60 110 64 120" stroke="#f472b6" stroke-width="8" stroke-linecap="round" fill="none"/>
  <ellipse cx="34" cy="123" rx="8" ry="4.5" fill="#ec4899"/>
  <ellipse cx="66" cy="123" rx="8" ry="4.5" fill="#ec4899"/>
</svg>"""

    elif mood == "excited":
        return f"""<svg width="{s}" height="{h}" viewBox="0 0 100 130" xmlns="http://www.w3.org/2000/svg">
  <path d="M50 95 C15 70 15 28 50 40 C85 28 85 70 50 95Z" fill="#f472b6"/>
  <ellipse cx="30" cy="64" rx="6" ry="4" fill="#fda4af" opacity="0.7"/>
  <ellipse cx="70" cy="64" rx="6" ry="4" fill="#fda4af" opacity="0.7"/>
  <circle cx="40" cy="54" r="6" fill="white"/>
  <circle cx="60" cy="54" r="6" fill="white"/>
  <text x="34" y="59" font-size="12" fill="#9d174d" font-family="sans-serif">★</text>
  <text x="54" y="59" font-size="12" fill="#9d174d" font-family="sans-serif">★</text>
  <path d="M42 68 Q50 78 58 68" stroke="#9d174d" stroke-width="2" fill="#fda4af" opacity="0.6"/>
  <path d="M42 68 Q50 78 58 68" stroke="#9d174d" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M20 55 Q6 38 10 22" stroke="#f472b6" stroke-width="8" stroke-linecap="round" fill="none"/>
  <path d="M80 55 Q94 38 90 22" stroke="#f472b6" stroke-width="8" stroke-linecap="round" fill="none"/>
  <circle cx="10" cy="20" r="6" fill="#fb7185"/>
  <circle cx="90" cy="20" r="6" fill="#fb7185"/>
  <path d="M44 94 Q40 110 36 120" stroke="#f472b6" stroke-width="8" stroke-linecap="round" fill="none"/>
  <path d="M56 94 Q60 110 64 120" stroke="#f472b6" stroke-width="8" stroke-linecap="round" fill="none"/>
  <ellipse cx="34" cy="123" rx="8" ry="4.5" fill="#ec4899"/>
  <ellipse cx="66" cy="123" rx="8" ry="4.5" fill="#ec4899"/>
</svg>"""

    elif mood == "worried":
        return f"""<svg width="{s}" height="{h}" viewBox="0 0 100 130" xmlns="http://www.w3.org/2000/svg">
  <path d="M50 95 C15 70 15 28 50 40 C85 28 85 70 50 95Z" fill="#fda4af"/>
  <ellipse cx="30" cy="64" rx="6" ry="4" fill="#fda4af" opacity="0.3"/>
  <ellipse cx="70" cy="64" rx="6" ry="4" fill="#fda4af" opacity="0.3"/>
  <circle cx="40" cy="54" r="7" fill="white"/>
  <circle cx="60" cy="54" r="7" fill="white"/>
  <circle cx="40" cy="56" r="3.5" fill="#9d174d"/>
  <circle cx="60" cy="56" r="3.5" fill="#9d174d"/>
  <circle cx="39" cy="53" r="1" fill="white"/>
  <circle cx="59" cy="53" r="1" fill="white"/>
  <path d="M35 47 Q40 44 45 47" stroke="#f472b6" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M55 47 Q60 44 65 47" stroke="#f472b6" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M43 72 Q50 68 57 72" stroke="#9d174d" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M20 62 Q10 74 14 84" stroke="#fda4af" stroke-width="8" stroke-linecap="round" fill="none"/>
  <path d="M80 62 Q90 74 86 84" stroke="#fda4af" stroke-width="8" stroke-linecap="round" fill="none"/>
  <circle cx="14" cy="85" r="6" fill="#fda4af"/>
  <circle cx="86" cy="85" r="6" fill="#fda4af"/>
  <path d="M44 94 Q40 110 36 120" stroke="#fda4af" stroke-width="8" stroke-linecap="round" fill="none"/>
  <path d="M56 94 Q60 110 64 120" stroke="#fda4af" stroke-width="8" stroke-linecap="round" fill="none"/>
  <ellipse cx="34" cy="123" rx="8" ry="4.5" fill="#f472b6"/>
  <ellipse cx="66" cy="123" rx="8" ry="4.5" fill="#f472b6"/>
</svg>"""

    elif mood == "sleepy":
        return f"""<svg width="{s}" height="{h}" viewBox="0 0 100 130" xmlns="http://www.w3.org/2000/svg">
  <path d="M50 95 C15 70 15 28 50 40 C85 28 85 70 50 95Z" fill="#c084fc"/>
  <ellipse cx="30" cy="64" rx="6" ry="4" fill="#f0abfc" opacity="0.4"/>
  <ellipse cx="70" cy="64" rx="6" ry="4" fill="#f0abfc" opacity="0.4"/>
  <ellipse cx="40" cy="57" rx="6" ry="3.5" fill="white"/>
  <ellipse cx="60" cy="57" rx="6" ry="3.5" fill="white"/>
  <ellipse cx="40" cy="58" rx="3" ry="1.8" fill="#6b21a8"/>
  <ellipse cx="60" cy="58" rx="3" ry="1.8" fill="#6b21a8"/>
  <path d="M34 55 Q40 52 46 55" stroke="#a855f7" stroke-width="2" fill="#c084fc" stroke-linecap="round"/>
  <path d="M54 55 Q60 52 66 55" stroke="#a855f7" stroke-width="2" fill="#c084fc" stroke-linecap="round"/>
  <path d="M43 70 Q50 74 57 70" stroke="#6b21a8" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  <path d="M20 62 Q12 76 16 86" stroke="#c084fc" stroke-width="8" stroke-linecap="round" fill="none"/>
  <path d="M80 62 Q88 76 84 86" stroke="#c084fc" stroke-width="8" stroke-linecap="round" fill="none"/>
  <circle cx="16" cy="87" r="6" fill="#d8b4fe"/>
  <circle cx="84" cy="87" r="6" fill="#d8b4fe"/>
  <path d="M44 94 Q40 110 36 120" stroke="#c084fc" stroke-width="8" stroke-linecap="round" fill="none"/>
  <path d="M56 94 Q60 110 64 120" stroke="#c084fc" stroke-width="8" stroke-linecap="round" fill="none"/>
  <ellipse cx="34" cy="123" rx="8" ry="4.5" fill="#a855f7"/>
  <ellipse cx="66" cy="123" rx="8" ry="4.5" fill="#a855f7"/>
</svg>"""

    return vita_svg("happy", size)


# ── MEDI (Pille-Figur) ────────────────────────────────────────────────────────

def medi_svg(mood: str = "happy", size: int = 100) -> str:
    s = size
    h = int(s * 1.3)

    # Farben je nach Stimmung
    colors = {
        "happy":   ("#818cf8", "#a5b4fc", "#6366f1", "#3730a3"),
        "excited": ("#818cf8", "#a5b4fc", "#6366f1", "#3730a3"),
        "worried": ("#a5b4fc", "#c7d2fe", "#818cf8", "#4338ca"),
        "sleepy":  ("#c084fc", "#d8b4fe", "#a855f7", "#6b21a8"),
    }
    body, top, dark, eye = colors.get(mood, colors["happy"])

    smile = "M43 42 Q50 48 57 42" if mood in ("happy", "excited") else "M43 44 Q50 40 57 44"
    arm_l = "M28 42 Q18 50 20 60" if mood != "excited" else "M28 40 Q14 30 16 18"
    arm_r = "M72 42 Q82 50 80 60" if mood != "excited" else "M72 40 Q86 30 84 18"
    hand_l_cy = "61" if mood != "excited" else "16"
    hand_r_cy = "61" if mood != "excited" else "16"
    hand_l_cx = "20" if mood != "excited" else "16"
    hand_r_cx = "80" if mood != "excited" else "84"

    eye_extra = ""
    if mood == "excited":
        eye_extra = f'<text x="34" y="39" font-size="10" fill="{eye}" font-family="sans-serif">★</text><text x="54" y="39" font-size="10" fill="{eye}" font-family="sans-serif">★</text>'
    elif mood == "worried":
        eye_extra = f'<path d="M36 28 Q42 25 48 28" stroke="{dark}" stroke-width="1.2" fill="none" stroke-linecap="round"/><path d="M52 28 Q58 25 64 28" stroke="{dark}" stroke-width="1.2" fill="none" stroke-linecap="round"/>'
    elif mood == "sleepy":
        eye_extra = f'<ellipse cx="42" cy="35" rx="5" ry="2.5" fill="{body}"/><ellipse cx="58" cy="35" rx="5" ry="2.5" fill="{body}"/>'

    return f"""<svg width="{s}" height="{h}" viewBox="0 0 100 130" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="50" cy="38" rx="22" ry="28" fill="{body}"/>
  <path d="M28 38 Q28 10 50 10 Q72 10 72 38 Z" fill="{top}"/>
  <line x1="28" y1="38" x2="72" y2="38" stroke="{dark}" stroke-width="1.5"/>
  <ellipse cx="50" cy="38" rx="22" ry="28" fill="none" stroke="{dark}" stroke-width="1.5"/>
  <circle cx="42" cy="33" r="4" fill="white"/>
  <circle cx="58" cy="33" r="4" fill="white"/>
  <circle cx="43" cy="34" r="2" fill="{eye}"/>
  <circle cx="59" cy="34" r="2" fill="{eye}"/>
  <circle cx="44" cy="33" r="0.8" fill="white"/>
  <circle cx="60" cy="33" r="0.8" fill="white"/>
  {eye_extra}
  <path d="{smile}" stroke="{eye}" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  <ellipse cx="37" cy="41" rx="4" ry="2.5" fill="#f9a8d4" opacity="0.5"/>
  <ellipse cx="63" cy="41" rx="4" ry="2.5" fill="#f9a8d4" opacity="0.5"/>
  <path d="{arm_l}" stroke="{body}" stroke-width="6" stroke-linecap="round" fill="none"/>
  <path d="{arm_r}" stroke="{body}" stroke-width="6" stroke-linecap="round" fill="none"/>
  <circle cx="{hand_l_cx}" cy="{hand_l_cy}" r="5" fill="{top}"/>
  <circle cx="{hand_r_cx}" cy="{hand_r_cy}" r="5" fill="{top}"/>
  <path d="M44 64 Q42 80 38 90" stroke="{body}" stroke-width="6" stroke-linecap="round" fill="none"/>
  <path d="M56 64 Q58 80 62 90" stroke="{body}" stroke-width="6" stroke-linecap="round" fill="none"/>
  <ellipse cx="37" cy="92" rx="7" ry="4" fill="{dark}"/>
  <ellipse cx="63" cy="92" rx="7" ry="4" fill="{dark}"/>
</svg>"""


# ── DR. CARE (Doktor-Figur) ───────────────────────────────────────────────────

def drcare_svg(mood: str = "happy", size: int = 100) -> str:
    s = size
    h = int(s * 1.35)

    smile = "M44 37 Q50 43 56 37" if mood in ("happy", "excited") else "M44 39 Q50 35 56 39"
    brow = ""
    if mood == "worried":
        brow = '<path d="M36 26 Q42 22 48 26" stroke="#92400e" stroke-width="1.2" fill="none" stroke-linecap="round"/><path d="M52 26 Q58 22 64 26" stroke="#92400e" stroke-width="1.2" fill="none" stroke-linecap="round"/>'
    arm_l = "M28 58 Q16 64 18 74" if mood != "excited" else "M28 54 Q12 40 14 26"
    arm_r = "M72 58 Q84 64 82 74" if mood != "excited" else "M72 54 Q88 40 86 26"
    hand_l = ("18","75") if mood != "excited" else ("14","24")
    hand_r = ("82","75") if mood != "excited" else ("86","24")

    eye_l = '<ellipse cx="43" cy="30" rx="4" ry="2.5" fill="#e2e8f0"/><ellipse cx="43" cy="31" rx="2" ry="1.2" fill="#1e293b"/>' if mood == "sleepy" else '<circle cx="43" cy="29" r="3.5" fill="white"/><circle cx="44" cy="30" r="1.8" fill="#1e293b"/><circle cx="45" cy="29" r="0.7" fill="white"/>'
    eye_r = '<ellipse cx="57" cy="30" rx="4" ry="2.5" fill="#e2e8f0"/><ellipse cx="57" cy="31" rx="2" ry="1.2" fill="#1e293b"/>' if mood == "sleepy" else '<circle cx="57" cy="29" r="3.5" fill="white"/><circle cx="58" cy="30" r="1.8" fill="#1e293b"/><circle cx="59" cy="29" r="0.7" fill="white"/>'
    star = ""
    if mood == "excited":
        star = '<text x="36" y="35" font-size="9" fill="#1e293b" font-family="sans-serif">★</text><text x="52" y="35" font-size="9" fill="#1e293b" font-family="sans-serif">★</text>'
        eye_l = ""
        eye_r = ""

    return f"""<svg width="{s}" height="{h}" viewBox="0 0 100 135" xmlns="http://www.w3.org/2000/svg">
  <rect x="28" y="45" width="44" height="42" rx="8" fill="white" stroke="#e2e8f0" stroke-width="1.5"/>
  <rect x="44" y="48" width="12" height="22" rx="2" fill="#e0f2fe"/>
  <circle cx="50" cy="76" r="2" fill="#0ea5e9"/>
  <circle cx="50" cy="83" r="2" fill="#0ea5e9"/>
  <path d="M36 52 Q30 58 32 65 Q34 70 40 68" stroke="#94a3b8" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <circle cx="41" cy="68" r="3" fill="#64748b"/>
  <circle cx="50" cy="30" r="18" fill="#fde68a"/>
  <circle cx="50" cy="30" r="18" fill="none" stroke="#fbbf24" stroke-width="1.2"/>
  <path d="M33 26 Q35 14 50 12 Q65 14 67 26" fill="#92400e"/>
  <rect x="36" y="14" width="28" height="6" rx="3" fill="#1e40af"/>
  {eye_l}
  {eye_r}
  {star}
  <rect x="38" y="25" width="10" height="7" rx="3" fill="none" stroke="#64748b" stroke-width="1"/>
  <rect x="52" y="25" width="10" height="7" rx="3" fill="none" stroke="#64748b" stroke-width="1"/>
  <line x1="48" y1="28" x2="52" y2="28" stroke="#64748b" stroke-width="1"/>
  {brow}
  <ellipse cx="50" cy="33" rx="2" ry="1.5" fill="#fbbf24" opacity="0.6"/>
  <ellipse cx="38" cy="35" rx="4" ry="2.5" fill="#fda4af" opacity="0.5"/>
  <ellipse cx="62" cy="35" rx="4" ry="2.5" fill="#fda4af" opacity="0.5"/>
  <path d="{smile}" stroke="#92400e" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  <path d="{arm_l}" stroke="#e2e8f0" stroke-width="7" stroke-linecap="round" fill="none"/>
  <path d="{arm_r}" stroke="#e2e8f0" stroke-width="7" stroke-linecap="round" fill="none"/>
  <circle cx="{hand_l[0]}" cy="{hand_l[1]}" r="5" fill="#fde68a"/>
  <circle cx="{hand_r[0]}" cy="{hand_r[1]}" r="5" fill="#fde68a"/>
  <path d="M43 87 Q41 100 37 110" stroke="#1e40af" stroke-width="6" stroke-linecap="round" fill="none"/>
  <path d="M57 87 Q59 100 63 110" stroke="#1e40af" stroke-width="6" stroke-linecap="round" fill="none"/>
  <ellipse cx="36" cy="112" rx="7" ry="3.5" fill="#1e3a8a"/>
  <ellipse cx="64" cy="112" rx="7" ry="3.5" fill="#1e3a8a"/>
</svg>"""


# ── Stimmungslogik ────────────────────────────────────────────────────────────

def get_vita_mood(
    hour: int,
    streak: int,
    has_pending: bool,
    bp_status: str = "",
    bs_status: str = "",
    new_achievement: bool = False,
) -> tuple:
    """
    Bestimmt die Stimmung und Nachricht des Maskottchens.
    Gibt (mood, message) zurück.
    """
    from utils.translations import t

    if new_achievement:
        return "excited", t("vita_achievement")

    if streak >= 7:
        return "excited", t("vita_streak_long").format(streak=streak)

    bad_keywords = [
        "kritisch", "critique", "critico", "critically",
        "hypertonie", "hypertension", "ipertensione",
        "auffällig", "anormal", "anomalo", "abnormally",
    ]
    bp_bad = any(kw in bp_status.lower() for kw in bad_keywords)
    bs_bad = any(kw in bs_status.lower() for kw in bad_keywords)

    if bp_bad or bs_bad:
        return "worried", t("vita_worried_health")

    if has_pending:
        return "worried", t("vita_pending")

    if hour >= 20 or hour < 6:
        return "sleepy", t("vita_sleepy")

    if streak >= 3:
        return "happy", t("vita_streak_small").format(streak=streak)

    if hour < 12:
        return "happy", t("vita_morning")
    elif hour < 17:
        return "happy", t("vita_noon")
    else:
        return "happy", t("vita_evening")