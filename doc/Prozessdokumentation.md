# Prozessdokumentation – MediTrack

**Modul:** Informatik 2  
**Applikationsname:** MediTrack – Medikamenten- und Gesundheitstracker  
**Technologie:** Python · Streamlit · SwitchDrive (WebDAV) · fpdf2 · Plotly · SVG 
**Zeitraum:** April 2026 - Mai 2026

---

## 1. Projektübersicht

MediTrack ist eine webbasierte Gesundheits-App, die mit dem Python-Framework **Streamlit** entwickelt wurde. Sie ermöglicht es Nutzerinnen und Nutzern, ihre tägliche Medikamenteneinnahme zu verwalten, Gesundheitswerte wie Blutdruck und Blutzucker zu tracken, ihre Stimmung zu erfassen und alle Daten als PDF zu exportieren.

Die App ist mehrsprachig (Deutsch, Französisch, Italienisch, Englisch), vollständig personalisierbar (9 Farbthemen, 3 Maskottchen) und speichert alle Daten sicher in der Cloud via **SwitchDrive** (WebDAV). Ein integriertes Maskottchen und Abzeichen-System machen die App motivierend und einzigartig.

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
- Motivierende Elemente (Maskottchen, Streak, Abzeichen) für eine nachhaltige Nutzung

---

## 3. Funktionen im Detail

### 3.1 Dashboard
Die Startseite begrüsst die Nutzerin oder den Nutzer personalisiert (Guten Morgen/Mittag/Abend) und zeigt:

- **Maskottchen mit Sprechblase** – Das gewählte Maskottchen erscheint oben rechts mit einer kontextabhängigen Nachricht
- **Streak-Banner** – Wie viele Tage in Folge wurden alle Medikamente eingenommen?
- **3 Metriken** – Anzahl Medikamente, heute eingenommen (X/Y), Einnahmen diese Woche
- **Erinnerungs-Banner** – Für jedes noch ausstehende Medikament erscheint ein gelber Hinweis
- **Heutige Medikamente** – Übersicht mit Bestätigen-Button und farbigem Status-Badge
- **Einnahmetreue** – Pro Medikament ein Fortschrittsbalken (grün/orange/rot)
- **Letzte Gesundheitswerte** – Letzter Blutdruck und Blutzucker mit Trend-Indikator (↑↓→)

### 3.2 Medikamente
- Medikamente hinzufügen mit Name, Uhrzeit, Wochentagen (Multiselect) und Bemerkung
- Bearbeiten und Löschen direkt in der Übersicht
- Wochentage werden intern immer als DE-Kürzel gespeichert und in der jeweiligen Sprache angezeigt

### 3.3 Einnahmeverlauf
- Chronologisch gruppiert: Monat → Kalenderwoche → Tag
- Farbige Punkte: Grün = bestätigt, Rot = nicht bestätigt
- Filter nach Zeitraum und Medikament
- Statistik-Tab mit Gesamt-Metriken und Adherence-Punktedarstellung
- Tab zum manuellen Erfassen und Bearbeiten von Einnahmen
- PDF-Export-Button direkt im Verlauf

### 3.4 Blutdruck-Tagebuch
- Klassifizierung nach **DGK-Leitlinien**: Hypotonie / Optimal / Normal / Hoch-normal / Hypertonie Grad 1–3
- **Sonderfälle** werden erkannt: Isolierte systolische und diastolische Hypertonie
- Plotly-Chart mit 7 farbigen Risikozonen
- Handlungsempfehlungen in ganzen Sätzen (auf Deutsch, mit Disclaimer in anderen Sprachen)

### 3.5 Blutzucker-Tagebuch
- Nüchternblutzucker in mmol/l
- Klassifizierung: Normal / Auffällig tief & hoch / Kritisch tief & hoch
- Plotly-Chart mit 6 Risikozonen und farbigen Messpunkten

### 3.6 Tagesstimmung
- 5 Stufen mit Emoji-Skala: 😄 😙 😐 😕 😞
- Optionaler Freitext-Kommentar
- Plotly-Verlaufschart mit übersetzten Achsenbeschriftungen
- Letzte 7 Einträge als Karten, Löschfunktion

### 3.7 Abzeichen-System (Achievements)
11 freischaltbare Abzeichen motivieren zu einer konsequenten Nutzung der App:

| Abzeichen | Bedingung |
|---|---|
| 🌱 Erster Schritt | Erste Einnahme bestätigt |
| 🔥 On Fire | 7 Tage Streak |
| 💪 Eiserner Wille | 30 Tage Streak |
| 👑 Legende | 100 Tage Streak |
| 💚 Grüne Zone | Blutdruck 7× optimal |
| 🩸 Zuckerfrei | Blutzucker 5× normal |
| 📊 Daten-Fan | 20 Gesundheitswerte erfasst |
| 🧘 Ausgeglichen | 7× Stimmung "Sehr gut" |
| 📄 Arztprofi | Ersten PDF exportiert |
| 🏅 Treuer Begleiter | 50 Einnahmen bestätigt |
| ✨ Vollständig | Profil vollständig ausgefüllt |

Die Abzeichen-Seite zeigt freigeschaltete Badges grün umrandet und gesperrte ausgegraut. Das Maskottchen reagiert auf den Fortschritt.

### 3.8 Maskottchen
Das Maskottchen begleitet die Nutzerin oder den Nutzer durch die gesamte App. Es erscheint auf dem Dashboard und der Abzeichen-Seite mit einer kontextabhängigen Sprechblase.

**3 wählbare Charaktere:**
- **Vita** 🩷 – Herz-Figur, fürsorglich und warm
- **Medi** 💊 – Pille-Figur, verspielt und lustig
- **Dr. Care** 🩺 – Doktor-Figur, professionell und kompetent

**4 Stimmungen je nach Kontext:**
- 😄 **Fröhlich** – Standard, Morgen/Mittag/Abend-Begrüssung
- 🔥 **Aufgeregt** – Bei Streak ≥ 7 Tage oder neuem Achievement
- 😟 **Besorgt** – Bei schlechten Gesundheitswerten oder ausstehenden Medikamenten
- 😴 **Müde** – Nach 20 Uhr

Die Maskottchenwahl wird in den Einstellungen gespeichert und bleibt über alle Sitzungen erhalten.

### 3.9 Profil
- 3 Tabs: Persönlich / Medizinisch / Notfall
- Geburtsdatum als 3 separate Zahlenfelder (Jahr 1900 bis heute)
- Gespeicherte Angaben als strukturierte Übersicht

### 3.10 Einstellungen
- **4 Sprachen:** DE / FR / IT / EN
- **9 Farbthemen** mit Vorschau
- **3 Maskottchen** mit Vorschau
- Einstellungen werden in `settings.json` pro User auf SwitchDrive gespeichert

### 3.11 PDF-Export
- Eigene Sidebar-Seite mit Checkboxen
- Zeigt Anzahl verfügbarer Einträge pro Bereich
- Generiert PDF via fpdf2 (ohne Emojis für Helvetica-Kompatibilität)

---

## 4. Technische Umsetzung

### 4.1 Datenspeicherung

| Datei | Inhalt |
|---|---|
| `medications.csv` | id, name, time, days, note, created_at |
| `intakes.csv` | id, medication_id, medication_name, date, time, confirmed, note, created_at |
| `blood_pressure.csv` | date, systolic, diastolic |
| `blood_sugar.csv` | date, value |
| `mood.csv` | date, mood_key, mood_value, mood_label, note |
| `profile.json` | firstname, lastname, birthdate, doctor, emergency, emergency_phone, blood_type, allergies |
| `settings.json` | language, theme, mascot |

### 4.2 Mehrsprachigkeit

Die Übersetzungen sind in `utils/translations.py` strukturiert. Jede Sprache hat ein Dictionary mit über 160 Keys. Die Funktion `t(key)` gibt den übersetzten Text zurück, mit Deutsch als Fallback.

**Designentscheidung:** Medizinische Handlungsempfehlungen bleiben auf Deutsch — eine fehlerhafte Übersetzung medizinischer Anweisungen wäre gesundheitlich riskant. In anderen Sprachen erscheint ein Disclaimer-Hinweis.

### 4.3 Theme-System

9 helle Farbthemen in `utils/themes.py`. `inject_theme()` wird in `app.py` **vor** `pg.run()` aufgerufen — der einzige Weg, die Sidebar-Farbe global zu setzen.

### 4.4 Maskottchen-System

Das Maskottchen-System in `utils/vita.py` generiert SVG-Vektorgrafiken direkt in Python. Jeder Charakter hat 4 Stimmungen die als SVG-String zurückgegeben und via `st.markdown(..., unsafe_allow_html=True)` gerendert werden. Kein externes Bild-File nötig.

```python
# Stimmungslogik
def get_vita_mood(hour, streak, has_pending, bp_status, bs_status):
    if streak >= 7:      return "excited", "WOW! {streak} Tage Streak!"
    if bp_bad or bs_bad: return "worried", "Deine Werte machen mir Sorgen..."
    if has_pending:      return "worried", "Medikamente warten noch!"
    if hour >= 20:       return "sleepy",  "Gute Nacht!"
    return "happy", "Hallo! Schön dich zu sehen!"
```

### 4.5 Abzeichen-System

Die Achievements werden beim Laden der Seite live aus den gespeicherten Daten berechnet — kein separates Speichern nötig. Die Funktion `check_achievements()` prüft Streak, Anzahl bestätigter Einnahmen, Gesundheitswerte und Profilvollständigkeit.

### 4.6 Streak-Berechnung

Der Streak wird rückwärts von heute berechnet. Für jeden Tag wird geprüft, ob alle fälligen Medikamente bestätigt wurden. Tage ohne fällige Medikamente werden übersprungen.

### 4.7 Trend-Analyse

Vergleicht den Durchschnitt der ersten und zweiten Hälfte der letzten 7 Messungen. Liegt die Differenz unter 30% der Standardabweichung → stabil, sonst steigend oder sinkend.

---

## 5. Design-Entscheidungen

| Entscheidung | Begründung |
|---|---|
| Maskottchen als SVG | Kein externes Bild nötig, skaliert perfekt, voll kontrollierbar |
| 3 Maskottchen zur Auswahl | Persönlichere Nutzererfahrung, höhere Identifikation |
| Achievements live berechnet | Kein separates Speichern, immer aktuell |
| Wochentage intern als DE-Kürzel | Einfache Handhabung unabhängig von Spracheinstellung |
| Geburtsdatum als 3 Zahlenfelder | Streamlit `date_input` ist auf Jahr 2000 begrenzt |
| Medizinische Texte nur auf Deutsch | Sicherheit – fehlerhafte medizinische Übersetzungen wären gefährlich |
| `mood_df` immer frisch laden | Verhindert veraltete Daten nach App-Neustart |
| `inject_theme()` vor `pg.run()` | Einzige Möglichkeit, Sidebar-Farbe global zu setzen |
| fpdf2 ohne Emojis | Helvetica unterstützt keine Unicode-Emojis |

---

## 6. Herausforderungen und Lösungen

### Herausforderung 1: Sidebar-Farbe übernimmt Theme nicht
**Problem:** Das CSS-Theme galt nur auf der aktuellen Seite.  
**Lösung:** `inject_theme()` einmalig in `app.py` vor `pg.run()` aufrufen.

### Herausforderung 2: HTML-Code wird als Text angezeigt
**Problem:** Mehrzeilige f-Strings mit Variablen wurden von Streamlit als Text statt HTML gerendert.  
**Lösung:** HTML-Strings als zusammengesetzte Einzeiler oder in separaten `st.markdown()`-Aufrufen.

### Herausforderung 3: Stimmungsdaten gehen nach Neustart verloren
**Problem:** `mood_df` wurde nur einmalig geladen und nicht neu eingelesen.  
**Lösung:** `mood_df` bei jedem App-Start frisch von SwitchDrive laden.

### Herausforderung 4: Plotly-Zeitachse zeigt Timestamps
**Problem:** Pandas Datetime-Objekte wurden mit Uhrzeit auf der X-Achse dargestellt.  
**Lösung:** Datum mit `.dt.strftime("%d.%m.%Y")` in sauberen String umwandeln.

### Herausforderung 5: fpdf2 unterstützt keine Emojis
**Problem:** Helvetica unterstützt keine Unicode-Emojis → Fehler beim PDF-Export.  
**Lösung:** Alle Emojis im PDF-Code durch normalen Text ersetzt.

### Herausforderung 6: Maskottchen-Variable vor `todays_meds` verwendet
**Problem:** `todays_meds` war noch nicht definiert als Vita die Variable brauchte.  
**Lösung:** `todays_meds` früher im Code berechnen, vor der Vita-Stimmungslogik.

---

## 7. Verwendete Bibliotheken

| Bibliothek | Verwendung |
|---|---|
| `streamlit` | Web-Framework, UI-Komponenten, Session State |
| `pandas` | Datenverarbeitung, CSV-Import/Export |
| `plotly` | Interaktive Charts (Blutdruck, Blutzucker, Stimmung) |
| `fpdf2` | PDF-Generierung |
| `webdav4` | SwitchDrive-Anbindung via WebDAV |

---

## 8. Reflexion

### Was gut funktioniert hat
- Das modulare Aufbau mit separaten Views und Utils macht den Code gut wartbar
- Das Maskottchen und das Abzeichen-System geben der App eine einzigartige Persönlichkeit
- Die Mehrsprachigkeit wurde durchgängig und konsequent umgesetzt
- Die medizinischen Klassifizierungen (DGK-Leitlinien) geben der App professionelle Qualität
- Das Theme-System mit 9 Farben und 3 Maskottchen ermöglicht echte Personalisierung

### Was schwierig war
- Streamlits Rendering-Verhalten bei mehrzeiligem HTML erforderte viel Trial-and-Error
- Die globale Theme-Injection (Sidebar) war eine nicht dokumentierte Einschränkung
- SVG-Maskottchen mit konsistenter Qualität für alle 3 Charaktere und 4 Stimmungen zu erstellen

### Was man verbessern könnte
- Konfetti-Animation beim Freischalten eines Achievements
- Erinnerungen via E-Mail oder Push-Notification
- Import von Medikamentendaten aus externen Quellen
- Mehr Maskottchen und Stimmungen

---

## 9. Fazit

MediTrack ist eine vollständig funktionsfähige, professionell gestaltete Gesundheits-App, die weit über eine einfache CRUD-Applikation hinausgeht. Die Kombination aus medizinisch korrekten Klassifizierungen, mehrsprachiger Benutzeroberfläche, personalisiertem Design mit 9 Farbthemen sowie dem einzigartigen Maskottchen- und Abzeichen-System macht sie zu einer echten, praxistauglichen und gleichzeitig motivierenden Anwendung.

---

*Dokumentation erstellt: Mai 2026*