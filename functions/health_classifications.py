"""
functions/health_classifications.py
Medizinische Klassifizierungen für Blutdruck und Blutzucker
nach DGK-Leitlinien und Deutscher Diabetes Gesellschaft.
"""

from utils.translations import t


def classify_bp(systolic, diastolic):
    """
    Klassifiziert Blutdruckwerte nach DGK-Leitlinien.
    Erkennt auch Sonderfälle (isolierte systolische/diastolische Hypertonie).
    Gibt (status_key, status_text) zurück.
    """
    # Sonderfälle zuerst prüfen
    if systolic >= 140 and diastolic < 90:
        return t("bp_isolated_sys"), t("bp_isolated_sys")
    if systolic < 140 and diastolic >= 90:
        return t("bp_isolated_dia"), t("bp_isolated_dia")

    if systolic >= 180 or diastolic >= 110:
        return t("bp_hyp3"), t("bp_hyp3")
    if systolic >= 160 or diastolic >= 100:
        return t("bp_hyp2"), t("bp_hyp2")
    if systolic >= 140 or diastolic >= 90:
        return t("bp_hyp1"), t("bp_hyp1")
    if systolic >= 130 or diastolic >= 85:
        return t("bp_highnorm"), t("bp_highnorm")
    if systolic >= 120 or diastolic >= 80:
        return t("bp_normal"), t("bp_normal")
    if systolic < 100 and diastolic < 60:
        return t("bp_hypo"), t("bp_hypo")
    return t("bp_optimal"), t("bp_optimal")


def classify_bs(value):
    """
    Klassifiziert Blutzucker-Nüchternwerte in mmol/l.
    Gibt (status_key, status_text) zurück.
    """
    if value < 3.0:
        return t("bs_crit_low"), t("bs_crit_low")
    if value < 3.9:
        return t("bs_warn_low"), t("bs_warn_low")
    if value <= 5.5:
        return t("bs_normal"), t("bs_normal")
    if value < 7.0:
        return t("bs_warn_high"), t("bs_warn_high")
    return t("bs_crit_high"), t("bs_crit_high")


def bp_color(status):
    """Gibt die Farbe für einen Blutdruck-Status zurück."""
    s = status.lower()
    if "hyp3" in s or "grad 3" in s or "kritisch" in s: return "#dc2626"
    if "hyp2" in s or "grad 2" in s:                     return "#ef4444"
    if "hyp1" in s or "grad 1" in s:                     return "#f97316"
    if "hoch" in s or "high" in s or "élevé" in s:       return "#f59e0b"
    if "normal" in s and "hoch" not in s:                return "#84cc16"
    if "optimal" in s:                                    return "#22c55e"
    if "hypo" in s:                                       return "#a855f7"
    return "#6b7280"


def bs_color(status):
    """Gibt die Farbe für einen Blutzucker-Status zurück."""
    s = status.lower()
    if "kritisch" in s or "critic" in s: return "#dc2626"
    if "auffällig" in s or "anormal" in s or "anomalo" in s or "abnormal" in s: return "#f59e0b"
    if "normal" in s: return "#22c55e"
    return "#6b7280"


def badge_css(status, color):
    """Erzeugt CSS-String für einen Status-Badge mit Hintergrund- und Textfarbe."""
    bg_map = {
        "#dc2626": "#fee2e2", "#ef4444": "#fee2e2",
        "#f97316": "#ffedd5", "#f59e0b": "#fef3c7",
        "#84cc16": "#ecfccb", "#22c55e": "#dcfce7",
        "#a855f7": "#f3e8ff",
    }
    bg = bg_map.get(color, "#f3f4f6")
    return f"background:{bg};color:{color};padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600"


def risk_badge(status, color):
    """Gibt HTML-Badge für einen Status zurück."""
    return f'<span style="{badge_css(status, color)}">{status}</span>'