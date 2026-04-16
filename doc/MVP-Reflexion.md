# MVP-Reflexion (V1.0)

## 1 Konnte das MVP wie geplant umgesetzt werden?
- Kurzantwort: Teilweise / Ja / Nein (bitte Zutreffendes ankreuzen und ggf. kurz begründen).
- Erreichte Kernfunktionen (Beispiele, anpassen):
  - Medikament hinzufügen, bearbeiten, löschen — umgesetzt
  - Tages-/Wochen-Plananzeige — umgesetzt
  - Erinnerungssystem (Grundfunktion) — teilweise umgesetzt (Scheduler rudimentär)
  - Persistenz (lokal / Cloud) — lokal umgesetzt; Cloud-Deployment vorhanden in README
- Kurzer Zustand: (1–2 Sätze, z. B.) "Die Grundfunktionalität zur Anlage und Darstellung von Medikationsplänen ist implementiert; erweiterte Erinnerungs-/Synchronisationsfunktionen fehlen noch."

## 2 Was konnte nicht umgesetzt werden und warum?
- Liste der offenen Punkte (konkret, kurz):
  - Push-/Hintergrund-Erinnerungen: noch nicht stabil / fehlt wegen Zeitaufwand und Hintergrund-API-Komplexität
  - Automatisierte Tests / Testabdeckung: unvollständig, da Fokus auf Feature-Implementierung lag
  - UI-Feinschliff / Barrierefreiheit: Priorität nach Stabilisierung
  - CI/CD (Automatischer Build & Release in GitHub Cloud): Grundkonfiguration fehlt
- Gründe (Kurz):
  - Zeitlimit der Übungsstunden
  - Technische Schwierigkeiten bei asynchronen Hintergrund-Tasks
  - Abhängigkeiten (z. B. externe Libraries, Zugriffsrechte für Cloud)

## 3 Müssen wir die Roadmap anpassen und falls ja, wie?
- Vorschlag zur Anpassung (Priorisierung / Meilensteine):
  1. Stabilität & Bugfixing (hohe Priorität, Sprint 1)
  2. Erinnerungs-Engine vervollständigen (Scheduler, Tests) (Sprint 2)
  3. UI-Polishing & Accessibility (Sprint 3)
  4. CI/CD & Deployment in GitHub Community Cloud (Sprint 4)
- Konkrete Änderungen an Produkt-Roadmap.md:
  - Verschiebe Cloud-Sync und erweiterte Erinnerungen um 1–2 Sprints.
  - Füge Test-Coverage und CI-Setup als eigene Milestones hinzu.
  - Ergänze Deadlines: Abgabe Vor-Kulturwoche (Sonntag) = MVP-Release; Finale Abgabe = +1 Woche.

## 4 Welche Unterstützung brauchen wir, um unsere Ziele zu erreichen?
- Technische Unterstützung:
  - Hilfe bei Hintergrund-Tasks / Scheduler-Implementierung (macOS/iOS specifics)
  - Unterstützung beim Einrichten von CI (GitHub Actions) und Deployment in Community Cloud
  - Kurzcode-Review für kritische Module (Persistenz, Erinnerungen)
- Organisatorische Unterstützung:
  - Feste Pair-Programming-Slots in den verbleibenden Übungsstunden
  - Priorisierungshilfe beim Roadmap-Review (Dozent / Tutor)
- Sonstiges:
  - Zugang zu Testgeräten (falls nötig) / Anleitung für Testinstallation aus Community Cloud

## 5 Konkrete nächste Schritte bis zur Abgabe (Kurzfristig)
- Bis V2:
  - Stabilitätsfixes für Kernpfade (Verantwortlich: ___)
  - README: Link zur App in GitHub Community Cloud überprüfen (Verantwortlich: ___)
  - Produkt-Roadmap.md gemäss Feedback überarbeiten (Verantwortlich: ___)
- Bis finale Abgabe (+1 Woche):
  - Erinnerungs-Engine fertigstellen
  - CI-Grundsetup + automatischer Build

---
