# 💊 MediTrack
### Die App für smarte Medikamenten- und Gesundheitsverwaltung

Folgender Link führt dich direkt zur App: https://medikamentenplanerapp.streamlit.app

MediTrack unterstützt Nutzerinnen und Nutzer dabei, ihre Medikamente zuverlässig zu verwalten, Gesundheitswerte zu tracken und den Überblick über ihre persönliche Gesundheit zu behalten. Die App erhöht die Medikamentensicherheit und erleichtert den Alltag – für mehr Lebensqualität.

---

## 🚀 Funktionen

### 💊 Medikamentenverwaltung
- Medikamente hinzufügen, bearbeiten und löschen
- Einnahmezeiten und Wochentage individuell planen
- Automatische Erinnerungen für ausstehende Einnahmen

### 📋 Einnahmeverlauf
- Chronologische Übersicht nach Monat, Woche und Tag
- Einnahmetreue pro Medikament in Prozent
- Statistiken und Auswertungen auf einen Blick

### ❤️ Gesundheitswerte
- **Blutdruck-Tagebuch** mit Klassifizierung nach DGK-Leitlinien und Risikozonen-Chart
- **Blutzucker-Tagebuch** (Nüchternwerte) mit medizinischer Bewertung
- Trend-Analyse (steigend / sinkend / stabil) für alle Werte

### 😊 Tagesstimmung
- Stimmungserfassung mit Emoji-Skala und optionalem Kommentar
- Verlaufschart mit wählbarem Zeitraum (7 Tage bis 1 Jahr)

### 🔥 Streak-System
- Motivierende Anzeige wie viele Tage in Folge alle Medikamente eingenommen wurden

### 🏆 Abzeichen-System
- 11 freischaltbare Achievements für Meilensteine (Streaks, Gesundheitsziele, Nutzung)
- Eigene Seite mit Fortschrittsanzeige und Übersicht aller Abzeichen

### 🐾 Maskottchen
- Persönliches Maskottchen das durch die App begleitet und motiviert
- 3 wählbare Charaktere: **Vita** (Herz), **Medi** (Pille), **Dr. Care** (Doktor)
- 4 kontextabhängige Stimmungen: reagiert auf Streak, Gesundheitswerte, ausstehende Medikamente und Tageszeit (fröhlich, aufgeregt, besorgt, müde)
- Die Maskottchen wurden mithilfe von KI als SVG-Grafiken kreiert

### 📄 PDF-Export
- Export von Einnahmen, Blutdruck, Blutzucker und Stimmung als PDF
- Auswahl der gewünschten Bereiche
- Ideal für den nächsten Arztbesuch

### 👤 Persönliches Profil
- Persönliche Angaben, Blutgruppe, Allergien, Vorerkrankungen und Notfallkontakt speichern

### ⚙️ Personalisierung
- **4 Sprachen:** 🇩🇪 Deutsch · 🇫🇷 Français · 🇮🇹 Italiano · 🇬🇧 English
- **9 Farbthemen:** Ozean-Blau, Lila, Smaragd, Rosa, Sonnenschein, Türkis, Himmelblau, Minze, Lavendel
- **3 Maskottchen:** Vita, Medi, Dr. Care

---

## 🎯 Zielgruppe

- Personen mit regelmässiger Medikamenteneinnahme
- Patientinnen und Patienten mit chronischen Erkrankungen
- Ältere Menschen, die Unterstützung bei der Medikamentenplanung benötigen
- Angehörige, die die Medikation einer nahestehenden Person mitverwalten

---

## 🛠️ Technologien

| Technologie | Verwendung |
|---|---|
| Python | Programmiersprache |
| Streamlit | Web-Framework und UI |
| Pandas | Datenverarbeitung |
| Plotly | Interaktive Charts |
| fpdf2 | PDF-Generierung |
| SVG | Maskottchen-Illustration |
| SwitchDrive (WebDAV) | Cloud-Datenspeicherung |
| GitHub | Versionskontrolle |

---

## 🔒 Datenspeicherung

Alle nutzerspezifischen und sensiblen Daten werden **pro Benutzer sicher in der SwitchDrive-Cloud** gespeichert – nicht im GitHub-Repository. Die Speicherung erfolgt ausschliesslich über die Methoden des `DataManager` (`save_user_data`, `load_user_data`, `save_app_data`, `load_app_data`).

---

## 👩‍💻 Entwicklerinnen

Dieses Projekt wurde im Rahmen des Moduls **Informatik 2** an der **ZHAW** entwickelt.

| Name | E-Mail |
|---|---|
| Giada De Luca | delucgia@students.zhaw.ch |
| Priscilla Baccaro | baccapri@students.zhaw.ch |
| Ana Lucia Gomes Carvalho | gomesana@students.zhaw.ch |

---

*ZHAW – Zürcher Hochschule für Angewandte Wissenschaften · Informatik 2 · Mai 2026*