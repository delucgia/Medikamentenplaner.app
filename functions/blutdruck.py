"""
functions/blutdruck.py
Spezifische Hilfsfunktionen für die Blutdruck-Ansicht.
"""

from utils.translations import t
from functions.format_helpers import e


def badge_css(status):
    """CSS-Klasse für einen Blutdruck-Status-Badge."""
    m = {
        t("bp_hypo"): "status-hypo", t("bp_optimal"): "status-optimal",
        t("bp_normal"): "status-normal", t("bp_highnorm"): "status-highnorm",
        t("bp_hyp1"): "status-hyp1", t("bp_hyp2"): "status-hyp2",
        t("bp_hyp3"): "status-hyp3",
    }
    return m.get(status, "status-normal")


def point_color(status):
    """Farbe für einen Blutdruck-Messpunkt im Chart."""
    m = {
        t("bp_hypo"): "#8b5cf6", t("bp_optimal"): "#22c55e",
        t("bp_normal"): "#86efac", t("bp_highnorm"): "#fbbf24",
        t("bp_hyp1"): "#f97316", t("bp_hyp2"): "#ef4444",
        t("bp_hyp3"): "#b91c1c",
    }
    return m.get(status, "#22c55e")


def risk_badge(status):
    """HTML-Badge für einen Blutdruck-Status."""
    css = badge_css(status)
    return f'<span class="{css}">{e(status)}</span>'