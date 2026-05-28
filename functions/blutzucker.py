"""
functions/blutzucker.py
Spezifische Hilfsfunktionen für die Blutzucker-Ansicht.
"""

from utils.translations import t
from functions.format_helpers import e


def badge_css(status):
    """CSS-Klasse für einen Blutzucker-Status-Badge."""
    m = {
        t("bs_normal"):    "status-optimal",
        t("bs_warn_low"):  "status-highnorm",
        t("bs_warn_high"): "status-hyp1",
        t("bs_crit_low"):  "status-hyp3",
        t("bs_crit_high"): "status-hyp3",
    }
    return m.get(status, "status-normal")


def point_color(status):
    """Farbe für einen Blutzucker-Messpunkt im Chart."""
    m = {
        t("bs_normal"):    "#22c55e",
        t("bs_warn_low"):  "#fbbf24",
        t("bs_warn_high"): "#f97316",
        t("bs_crit_low"):  "#b91c1c",
        t("bs_crit_high"): "#b91c1c",
    }
    return m.get(status, "#22c55e")


def risk_badge(status):
    """HTML-Badge für einen Blutzucker-Status."""
    css = badge_css(status)
    return f'<span class="{css}">{e(status)}</span>'