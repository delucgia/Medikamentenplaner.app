# Prozessdokumentation – MediTrack

**Modul:** Informatik 2  
**Applikationsname:** MediTrack – Medikamenten- und Gesundheitstracker  
**Technologie:** Python · Streamlit · SwitchDrive (WebDAV) · fpdf2 · Plotly  
**Zeitraum:** Mai 2026

---

## 1. Projektübersicht

MediTrack ist eine webbasierte Gesundheits-App, die mit dem Python-Framework **Streamlit** entwickelt wurde. Sie ermöglicht es Nutzerinnen und Nutzern, ihre tägliche Medikamenteneinnahme zu verwalten, Gesundheitswerte wie Blutdruck und Blutzucker zu tracken, ihre Stimmung zu erfassen und alle Daten als PDF zu exportieren.

Die App ist mehrsprachig (Deutsch, Französisch, Italienisch, Englisch), vollständig personalisierbar (9 Farbthemen) und speichert alle Daten sicher in der Cloud via **SwitchDrive** (WebDAV).

---

## 2. Ausgangslage und Zielsetzung

### Ausgangslage
Im Rahmen des Moduls Informatik 2 sollte eine praxisnahe Web-Applikation entwickelt werden, die einen echten Mehrwert für Nutzerinnen und Nutzer bietet. Die Idee entstand aus dem Alltag: Viele Menschen – insbesondere ältere Personen oder chronisch Erkrankte – vergessen ihre Medikamente oder haben keinen einfachen Überblick über ihre Gesundheitswerte.

### Ziele
- Eine intuitive App zur Verwaltung von Medikamenten und Gesundheitswerten
- Sichere, cloudbasierte Datenspeicherung pro Benutzer
- Mehrsprachigkeit für den Schweizer Kontext (DE/FR/IT/EN)
- Ansprechendes, professionelles UI-Design
- PDF-Export für den Arztbesuch

---

## 3. Projektstruktur

```
Medikamentenplaner.app-1/
│
├── docs/                               # Dokumentation
│   ├── MVP-Reflexion.md
│   ├── Persona.md
│   ├── Produkt-Roadmap.md
│   ├── Prozessdokumentation.md
│   ├── Wireframe-Nutzertests.md
│   └── Wireframes/                     # Wireframe-Skizzen und Storyboard
│
├── utils/                              # Hilfsmodule
│   ├── __init__.py
│   ├── data_handler.py                 # Daten-Handler
│   ├── data_manager.py                 # SwitchDrive WebDAV – Daten laden und speichern
│   ├── login_manager.py                # Login und Registrierung
│   └── pdf_export.py                   # PDF-Generierung mit fpdf2
│
├── views/                              # Alle Seiten der App
│   ├── blutdruck.py                    # Blutdruck-Tagebuch mit Plotly-Chart und Risikozonen
│   ├── blutzucker.py                   # Blutzucker-Tagebuch mit Plotly-Chart
│   ├── dashboard.py                    # Tagesübersicht mit Streak, Metriken, Gesundheitswerte
│   ├── einstellungen.py                # Sprache und Farbthema wählen
│   ├── home.py                         # Startseite / Landingpage
│   ├── medikamente.py                  # Medikamentenverwaltung (CRUD)
│   ├── pdf_export.py                   # PDF-Export-Seite mit Auswahl der Datenbereiche
│   ├── profil.py                       # Persönliches Profil und Notfallkontakt
│   ├── stimmung.py                     # Tagesstimmung mit Emoji-Skala und Verlaufschart
│   └── verlauf.py                      # Einnahmeverlauf mit Statistik und Monatsgruppierung
│
├── .gitignore
├── README.md
├── app.py                              # Einstiegspunkt, Login, Navigation, Theme-Injection
├── requirements.txt                    # Abhängigkeiten (streamlit, pandas, plotly, fpdf2)
├── themes.py                           # 9 Farbthemen mit CSS-Injection
└── translations.py                     # Übersetzungen DE/FR/IT/EN (130+ Keys pro Sprache)
```

---

## 4. Funktionen im Detail

### 4.1 Dashboard
Die Startseite begrüsst die Nutzerin oder den Nutzer personalisiert (Guten Morgen/Mittag/Abend) und zeigt:

- **Streak-Banner** – Wie viele Tage in Folge wurden alle Medikamente eingenommen? (motivierendes Feature mit Flammen-Emoji)
- **3 Metriken** – Anzahl Medikamente, heute eingenommen (X/Y), Einnahmen diese Woche
- **Erinnerungs-Banner** – Für jedes noch ausstehende Medikament erscheint ein gelber Hinweis mit Uhrzeit
- **Heutige Medikamente** – Übersicht mit Bestätigen-Button, farbigem Status-Badge und direktem Link zu Bearbeiten
- **Einnahmetreue** – Pro Medikament ein Fortschrittsbalken (grün/orange/rot je nach Prozentsatz)
- **Letzte Gesundheitswerte** – Letzter Blutdruck und Blutzucker mit Statusanzeige und Trend-Indikator (↑↓→)

### 4.2 Medikamente
- Medikamente hinzufügen mit Name, Uhrzeit, Wochentagen (Multiselect) und Bemerkung
- Bearbeiten und Löschen direkt in der Übersicht
- Wochentage werden intern immer als DE-Kürzel gespeichert (Mo, Di, ...) und in der jeweiligen Sprache angezeigt

### 4.3 Einnahmeverlauf
- Chronologisch gruppiert: Monat → Kalenderwoche → Tag
- Farbige Punkte: Grün = bestätigt, Rot = nicht bestätigt
- Filter nach Zeitraum und Medikament
- Statistik-Tab mit Gesamt-Metriken und Einnahmetreue-Punktedarstellung pro Medikament
- Tab zum manuellen Erfassen und Bearbeiten von Einnahmen
- PDF-Export-Button direkt im Verlauf

### 4.4 Blutdruck-Tagebuch
- Eingabe von systolischem und diastolischem Wert
- Klassifizierung nach **DGK-Leitlinien** (Deutsche Gesellschaft für Kardiologie):
  - Hypotonie / Optimal / Normal / Hoch-normal / Hypertonie Grad 1–3
- **Sonderfälle** werden erkannt:
  - Isolierte systolische Hypertonie (hoher Oberwert, tiefer Unterwert)
  - Isolierte diastolische Hypertonie (tiefer Oberwert, hoher Unterwert)
- Plotly-Chart mit 7 farbigen Risikozonen (ohne Zahlenbeschriftung, nur Fachbegriff)
- Farbige Messpunkte je nach Kategorie
- Handlungsempfehlungen in ganzen Sätzen (auf Deutsch, mit Disclaimer in anderen Sprachen)
- Referenzwerte-Tabelle und Sonderfälle-Tabelle als Expander

### 4.5 Blutzucker-Tagebuch
- Nüchternblutzucker in mmol/l (morgens vor dem Essen)
- Klassifizierung: Normal / Auffällig tief / Auffällig hoch / Kritisch tief / Kritisch hoch
- Plotly-Chart mit 6 Risikozonen und farbigen Messpunkten
- Handlungsempfehlungen analog zum Blutdruck

### 4.6 Tagesstimmung
- 5 Stufen mit Emoji-Skala: 😄 Sehr gut / 🙂 Gut / 😐 Okay / 😕 Schlecht / 😞 Sehr schlecht
- Optionaler Freitext-Kommentar
- Heutiger Eintrag wird oben als Banner angezeigt
- Plotly-Verlaufschart mit übersetzten Y-Achsen-Labels
- Letzte 7 Einträge als Karten
- Löschfunktion via Expander

### 4.7 Profil
- 3 Tabs: Persönlich / Medizinisch / Notfall
- Geburtsdatum als 3 separate Zahlenfelder (Jahr 1900 bis heute, kein Streamlit-Limit)
- Initialen-Avatar mit Theme-Gradient
- Gespeicherte Angaben als strukturierte Übersicht

### 4.8 Einstellungen
- **4 Sprachen:** 🇩🇪 Deutsch / 🇫🇷 Français / 🇮🇹 Italiano / 🇬🇧 English
- **9 Farbthemen:** Ozean-Blau, Lila, Smaragd, Rosa, Sonnenschein, Türkis, Himmelblau, Minze, Lavendel
- Farbvorschau-Banner mit Gradient
- Einstellungen werden in `settings.json` pro User auf SwitchDrive gespeichert

### 4.9 PDF-Export
- Eigene Seite in der Sidebar
- Checkboxen für jeden Bereich: Einnahmen / Blutdruck / Blutzucker / Stimmung
- Zeigt Anzahl verfügbarer Einträge
- Ausgegraut wenn keine Daten vorhanden
- Generiert sauberes PDF mit fpdf2 (ohne Emojis für Helvetica-Kompatibilität)
- Download-Button erscheint nach Generierung
- Dateiname enthält die gewählten Bereiche (z.B. `meditrack_blutdruck_blutzucker.pdf`)

---

## 5. Technische Umsetzung

### 5.1 Datenspeicherung

Alle Daten werden pro Benutzer in der **SwitchDrive-Cloud** via WebDAV gespeichert. Die Struktur:

| Datei | Inhalt |
|---|---|
| `medications.csv` | id, name, time, days, note, created_at |
| `intakes.csv` | id, medication_id, medication_name, date, time, confirmed, note, created_at |
| `blood_pressure.csv` | date, systolic, diastolic |
| `blood_sugar.csv` | date, value |
| `mood.csv` | date, mood_key, mood_value, mood_label, note |
| `profile.json` | firstname, lastname, birthdate, doctor, emergency, emergency_phone, blood_type, allergies |
| `settings.json` | language, theme |

### 5.2 Mehrsprachigkeit

Die Übersetzungen sind in `utils/translations.py` strukturiert. Jede Sprache hat ein Dictionary mit über 130 Keys. Die Funktion `t(key)` gibt den übersetzten Text zurück, mit Deutsch als Fallback.

```python
def t(key: str) -> str:
    lang = st.session_state.get("language", "de")
    result = TRANSLATIONS.get(lang, TRANSLATIONS["de"]).get(key)
    if result is None:
        result = TRANSLATIONS["de"].get(key, key)
    return result
```

**Designentscheidung:** Medizinische Handlungsempfehlungen (Notfallhinweise, detaillierte Anweisungen) bleiben auf Deutsch, da eine falsche Übersetzung gesundheitliche Risiken darstellen könnte. In anderen Sprachen erscheint ein Disclaimer-Hinweis.

### 5.3 Theme-System

Das Theme-System in `utils/themes.py` definiert 9 Farbthemen mit je 12 Attributen (Primärfarbe, Gradient, Sidebar-Hintergrund, etc.). `inject_theme()` wird in `app.py` **vor** `pg.run()` aufgerufen, damit das CSS global für alle Seiten gilt – einschliesslich der Sidebar.

```python
# app.py – Theme wird global injiziert
from utils.themes import inject_theme
inject_theme()
pg.run()
```

### 5.4 Streak-Berechnung

Der Streak wird rückwärts von heute berechnet. Für jeden Tag wird geprüft, ob alle fälligen Medikamente bestätigt wurden. Tage ohne fällige Medikamente werden übersprungen.

```python
def compute_streak():
    check_date = date.today()
    for _ in range(365):
        due_meds = ...  # Medikamente die an diesem Tag fällig sind
        if due_meds.empty:
            check_date -= timedelta(days=1)
            continue
        if all_confirmed(due_meds, check_date):
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak
```

### 5.5 Trend-Analyse

Die Trend-Analyse für Blutdruck und Blutzucker vergleicht den Durchschnitt der ersten und zweiten Hälfte der letzten 7 Messungen. Liegt die Differenz unter 30% der Standardabweichung, gilt der Wert als stabil.

---

## 6. Design-Entscheidungen

| Entscheidung | Begründung |
|---|---|
| Wochentage intern immer als DE-Kürzel | Einfache Handhabung unabhängig von Spracheinstellung |
| Geburtsdatum als 3 Zahlenfelder | Streamlit `date_input` ist auf Jahr 2000 begrenzt |
| Medizinische Texte nur auf Deutsch | Sicherheit – fehlerhafte Übersetzungen medizinischer Anweisungen wären gefährlich |
| `mood_df` immer frisch laden | Verhindert veraltete Daten nach App-Neustart |
| `inject_theme()` in `app.py` vor `pg.run()` | Einzige Möglichkeit, Sidebar-Farbe global zu setzen |
| fpdf2 ohne Emojis | Helvetica unterstützt keine Unicode-Emojis |
| Sonderfälle Blutdruck separat erkennen | Medizinisch korrekte Unterscheidung von isolierter systolischer/diastolischer Hypertonie |

---

## 7. Herausforderungen und Lösungen

### Herausforderung 1: Sidebar-Farbe übernimmt Theme nicht
**Problem:** Das CSS-Theme wurde nur auf der aktuellen Seite angewendet, die Sidebar blieb immer grau.  
**Lösung:** `inject_theme()` wird einmalig in `app.py` vor `pg.run()` aufgerufen. Da Streamlit das CSS-Rendering zentralisiert, gilt die Injection dann für alle Seiten.

### Herausforderung 2: HTML-Code wird im Dashboard als Text angezeigt
**Problem:** Mehrzeilige `f"""..."""`-Strings mit eingebetteten Variablen wurden von Streamlit teilweise als Text gerendert statt als HTML.  
**Lösung:** HTML-Strings werden als zusammengesetzte Einzeiler gebaut, oder einzelne Elemente werden in separaten `st.markdown()`-Aufrufen ausgegeben.

### Herausforderung 3: Stimmungsdaten gehen nach Neustart verloren
**Problem:** `mood_df` wurde nur geladen wenn der Key nicht im Session State war. Nach einem Neustart wurde die CSV aus der Cloud nicht neu eingelesen.  
**Lösung:** `mood_df` wird in `app.py` bei jedem Start frisch von SwitchDrive geladen (kein `if ... not in st.session_state`-Check).

### Herausforderung 4: Plotly-Zeitachse zeigt Timestamps statt Datum
**Problem:** Pandas Datetime-Objekte wurden mit Uhrzeit (`2026-05-07 00:00:00`) auf der X-Achse dargestellt.  
**Lösung:** Datum wird mit `.dt.strftime("%d.%m.%Y")` in einen sauberen String umgewandelt. Plotly rendert String-Kategorien ohne Zeitanteil.

### Herausforderung 5: fpdf2 unterstützt keine Emojis
**Problem:** Beim PDF-Export erschien ein Fehler weil Helvetica keine Unicode-Emojis unterstützt.  
**Lösung:** Alle Emojis und Sonderzeichen (✓, ✗) wurden im PDF-Code durch normalen Text ersetzt.

---

## 8. Verwendete Bibliotheken

| Bibliothek | Version | Verwendung |
|---|---|---|
| `streamlit` | aktuell | Web-Framework, UI-Komponenten, Session State |
| `pandas` | aktuell | Datenverarbeitung, CSV-Import/Export |
| `plotly` | aktuell | Interaktive Charts (Blutdruck, Blutzucker, Stimmung) |
| `fpdf2` | aktuell | PDF-Generierung |
| `webdav4` | aktuell | SwitchDrive-Anbindung via WebDAV |

---

## 9. Reflexion

### Was gut funktioniert hat
- Das modulare Aufbau mit separaten Views und Utils-Modulen macht den Code gut wartbar
- Das Theme-System ist flexibel und visuell ansprechend
- Die Mehrsprachigkeit wurde durchgängig und konsequent umgesetzt
- Die medizinischen Klassifizierungen (DGK-Leitlinien) geben der App eine professionelle Qualität

### Was schwierig war
- Streamlits Rendering-Verhalten bei mehrzeiligem HTML erforderte viel Trial-and-Error
- Die globale Theme-Injection (Sidebar) war eine nicht dokumentierte Einschränkung von Streamlit
- Vollständige Mehrsprachigkeit bedeutete, jeden einzelnen String zu identifizieren und zu übersetzen

### Was man verbessern könnte
- Erinnerungen via E-Mail oder Push-Notification
- Diagramme zum Blutdruckverlauf über mehrere Monate im PDF
- Import von Medikamentendaten aus externen Quellen
- Dunkel-Modus mit dynamischer Umschaltung

---

## 10. Fazit

MediTrack ist eine vollständig funktionsfähige, professionell gestaltete Gesundheits-App, die weit über eine einfache CRUD-Applikation hinausgeht. Die Kombination aus medizinisch korrekten Klassifizierungen, mehrsprachiger Benutzeroberfläche, personalisiertem Design und Cloud-Datenspeicherung macht sie zu einer echten, praxistauglichen Anwendung.

---

*Dokumentation erstellt: Mai 2026*