from datetime import datetime
import pytz

def parse_list(s: str):
    try:
        return [float(x.strip()) for x in s.split(",") if x.strip() != ""]
    except:
        return []

def weighted_average(grades, weights=None):
    if not grades:
        avg = None
    else:
        if weights and len(weights) == len(grades):
            tot = sum(weights)
            if tot == 0:
                avg = None
            else:
                avg = sum(g * w for g, w in zip(grades, weights)) / tot
        else:
            avg = sum(grades) / len(grades)

    return {
        "timestamp": datetime.now(pytz.timezone("Europe/Zurich")),
        "grades": grades,
        "weights": weights if weights is not None else [],
        "average": round(avg, 2) if avg is not None else None,
        "label": grade_label(avg) if avg is not None else "",
    }

def grade_label(avg):
    if avg is None:
        return ""
    if avg >= 5.5:
        return "Sehr gut"
    if avg >= 5.0:
        return "Gut"
    if avg >= 4.5:
        return "Befriedigend"
    if avg >= 4.0:
        return "Genügend (Bestanden)"
    return "Ungenügend (Nicht bestanden)"
