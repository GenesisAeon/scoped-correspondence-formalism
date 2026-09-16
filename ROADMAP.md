# Roadmap — Konsolidierung des selbstähnlichen Drei-Schichten-Rahmens

Revision 3, 16. September 2026. Die Paketarbeit ist bereits angelaufen und umfasst veröffentlichte Korrekturen. Das frühere GO war eine Arbeitsentscheidung; es wird nicht als Nachweis sämtlicher theoretischer Behauptungen interpretiert.

## 1. Erreichter Stand

| Bereich | Dokumentierter Fortschritt bis 15. September |
|---|---|
| Formalismus | Drei Rollen geklärt; acht bereitgestellte Worked Examples; Gegenprüfung mit reproduzierbaren Gegenbeispielen |
| `afet-tensions` | echter Mehrdaten-Refit von Γ/κ; Tests bereinigt; Changelog 1.0.2 |
| `resilience-core` / `scope-resilience` | Kalibrierungs-/Fixpunktbehauptungen korrigiert; Tests und CI bereinigt; Changelogs 1.0.3 / 1.0.2 |
| `amoc-utac` | falsche Wirkungsrichtung behoben und Γ-Datenpfade offengelegt; Changelog 1.3.3 |
| `cygnus-jet-utac` / `neural-avalanche-utac` | überzogene Kalibrierungs-/Universalitätsaussagen korrigiert; Changelogs 1.0.2 / 1.0.1 |
| `solar-flare-utac` | Reset-Begriff und Rundungsprüfung korrigiert, Zeitskalenlücke offengelegt; Changelog 1.0.1 |
| Weitere Pakete | Testkontamination, stale Installationen, Metadaten, Abhängigkeiten und Release-Infrastruktur bearbeitet; Details in FOLLOWUP und archivierter Roadmap |
| `phaethon-chimera` | Radius, Auswurfgeschwindigkeit und Missionszeitplan korrigiert; verbleibende Perihelzahl als zeitplanabhängig markiert |

Dies bündelt die bereitgestellten Arbeitsnachweise und die im Review vom 15. September gezielt geprüften Quellstände. Die Paket-Testsuiten, PyPI- und Zenodo-Veröffentlichungen werden durch diese Dokumentrevision nicht erneut verifiziert.

## 2. In dieser Revision erledigt

Die folgenden Konsolidierungen stammen aus Revision 2 und bleiben die Basis.

- [x] Selbstähnlichkeit als Leitidee von Größenidentität getrennt.
- [x] Größen, Einheiten, Zustände, Kontrollparameter und Evidenztypen konsolidiert.
- [x] Kubische Normalform korrigiert; Diskriminant und Zeitskala berücksichtigt.
- [x] Grenzen von Individuation, Basin Stability und Dimensionsentstehung angegeben.
- [x] Thermodynamischen Spezialfall mit Bilanz und zulässigen Kräften präzisiert.
- [x] Positives Wärmebeispiel und ausführbares Verifikationsskript ergänzt.
- [x] Acht Worked Examples auf aktuelle Begrifflichkeit und bekannte Reparaturen abgestimmt.

Die Ergebnisse der tatsächlich ausgeführten Prüfungen stehen in [VERIFICATION.md](VERIFICATION.md).

Mit Revision 3 ergänzt: Literaturabgleich; explizite Beobachtungs-/Dimensionsbegriffe; Makro-Geschlossenheit und Fehlerschranke; EI-Interventionsprotokoll; SVD- und Reversibilitätsgegenfälle; GENERIC-Wärmestruktur; Viabilitäts- und Rekonstruktionsbeispiele. Das sind Methoden- und Modellresultate. Mit Revision 3.2 ergänzt: Kontext-Transformationen und überlappende Systemzugehörigkeit. Mit F08/F09 (16. September, extern von Aeon geliefert, Checksummen/Skriptläufe von Claude nachgerechnet) ergänzt: optionale Sheaf-Kontextualitäts- und PID/Redundancy-Bottleneck-Module neben VB1 bzw. `EI_q`, ohne den Kern zu ändern. Die folgenden empirischen Arbeitspakete bleiben offen.

### Priorität für die nächste Untersuchung

1. **Eine Domäne, eine überprüfbare Makrovariable:** Zustände, Eingaben, Sampling und Beobachtung festlegen; erst die Markov-/Gedächtnisfrage klären. Keine gleichzeitige Universalitätsbehauptung über alle Pakete.
2. **Geschlossenheit und Prognose:** Kandidaten für Aggregation bzw. Delay-Zustände nur auf Trainingsdaten auswählen. Getrennte Zeitabschnitte/Trajektorien prüfen, inklusive Vergleich mit einer einfachen Persistenz-/Markov-Baseline und einem Gedächtnismodell.
3. **Intervention nur mit Begründung:** EI erst kausal interpretieren, wenn Simulationseingriffe oder Identifikationsannahmen tragen. Sonst Kanalinformation ausweisen. SVD als zusätzliche Diagnose, nicht als Freigabescore.
4. **Domänenvergleich danach:** Eine vorab bestimmte Strukturabbildung auf weitere Bedingungen übertragen und ihre Fehler messen. Gemeinsame Defaults nicht zur Kalibrierung des gewünschten Resultats verwenden.

Der thermodynamische Ausbau kann unabhängig am vollständig bilanzierten Wärmebeispiel entwickelt werden. Ein Projektionsschritt muss Energie-/Entropiebilanz und Markov-Geschlossenheit jeweils erhalten oder seinen Fehler offenlegen.

## 3. Nächster fachlicher Schritt: eine Selbstähnlichkeitsbehauptung prüfen

Wähle zwei bereits klar beschriebene Modelle und formuliere eine begrenzte gemeinsame Struktur. Für die erste Untersuchung eignet sich die lokale Relaxation, weil ihre Voraussetzungen und Gegenfälle explizit sind. Es ist zu unterscheiden, ob nur dieselbe Standardnormalform wiederkehrt oder ein zusätzlicher domänenübergreifender Vorhersagegewinn behauptet wird.

Vor dem Test festlegen:

1. Zustände, Systemgrenzen, Eingaben, Zeitskalen und Beobachtungen.
2. Transformation T, Zeitabbildung c und Parameterbeziehungen.
3. Bereich, in dem die Beziehung erwartet wird; Abweichungsmaß und relevante Toleranz.
4. Vergleichsmodelle, Daten für Kalibrierung und getrennte Daten für Vorhersageprüfung.
5. Auswertung von Unsicherheit und Gegenbefunden, einschließlich des möglichen Ergebnisses „keine über die Standardnormalform hinausgehende Gemeinsamkeit“.

Das Wärmebeispiel liefert eine vollständig gerechnete Referenz. Es bestätigt keine natürliche Selbstähnlichkeit zwischen Wärme, AMOC und neuronaler Dynamik; dafür braucht es die entsprechende Untersuchung.

## 4. Gezielte Code-Folgen statt automatischer Bedeutungsänderung

| Ticket | Arbeit | Erledigt, wenn … |
|---|---|---|
| F02 | Nutzer der alten Begriffe/Identitäten in Paketen und Registry erfassen | pro Fund zwischen Kommentar, Datenfeld, berechneter Größe und wissenschaftlicher Behauptung unterschieden ist |
| F03 | `effective_r()`-Zeitbezug in Neural Avalanche präzisieren | Δt bzw. Zeitstempel unterstützt oder Ein-Stunden-Annahme verbindlich validiert ist; Schätzung mit mindestens zwei Abständen geprüft |
| F04 | Solar-Aufrufpfad korrekt beschreiben | Peak-Ereignis und verfügbare Erholung getrennt ausgewiesen sind; eine etwaige Zustandsintegration separat entworfen ist |
| F05 | Resilience-Kopplungsregister typisieren | Einfluss-/Lastmodell korrekt dokumentiert ist; thermodynamische Kennzeichnung nur mit vollständiger Bilanz erscheint |
| F06 | Beobachtungs- und Simulationspfade für Γ verfolgen | Herkunft, Kalibrierung, tatsächlicher Verbraucher und Unabhängigkeitsstatus pro Pfad dokumentiert sind |
| F07 | Gemeinsame Modellformen an unabhängigen Daten untersuchen | Vergleich nach Abschnitt 3 abgeschlossen und sein Geltungsbereich angegeben ist |

Die Code-Tickets sind offen. Der aktuelle Auftrag überarbeitet die Dokumente und Verifikationsbeispiele, nicht sämtliche veröffentlichten Pakete. Bereits korrigierte Befunde werden nicht erneut als offene Fehler geführt. Eine Verdrahtung bislang ungenutzter Diagnostik verlangt eine inhaltliche Modellentscheidung.

## 5. Bisherige Paketgruppen und Ausnahmen

Die frühere Roadmap unterschied Kontaminationsbereinigung (3A), etwa 20 Kandidaten für vertiefte Modellprüfung (3B), `Feldtheorie` als eigenen Herkunfts-/Referenzfall (3C), schwache/namentliche Treffer ohne erzwungene Integration (3D) und die ausgenommene Climate/Ecology-Serie (3E). Diese Organisation bleibt als Arbeitsinventar nutzbar. Die genaue Liste und sämtliche früheren Fortschrittsnotizen sind in [archive/2026-09-15/ROADMAP.md](archive/2026-09-15/ROADMAP.md) erhalten.

Die damals priorisierte Gruppe umfasst `cygnus-jet-utac`, `amoc-utac`, `solar-flare-utac` und `neural-avalanche-utac`; ihre Beispiele sind hier aktualisiert. Für weitere Pakete wird der Begriff „struktureller Fit“ nur mit explizitem Modellbezug verwendet. Ein solcher Fit bestätigt keine gemeinsame Konstante und keine thermodynamische Kopplung.

Die Climate/Ecology-Ausnahme vom 31. August gilt weiterhin für die in eurer Registry entsprechend gekennzeichneten Literaturpakete. Die hier bereitgestellte Arctic-Analyse bleibt exploratorische Dokumentation; aus dieser Revision folgt keine Bridge oder Paketänderung. `amoc-utac` P18 gehört laut bereitgestellter Registry-Auswertung nicht zu dieser ausgeschlossenen Familie. Entscheidungen werden paketbezogen geprüft, nicht aus dem Wort „Klima“ abgeleitet.

`Feldtheorie` bleibt ein eigener fachlicher Abgleich mit seinen bisherigen Definitionen und Experimenten. Die neue Dokumentfassung ersetzt seine vorhandenen Module nicht automatisch. Der G03-Befund wird durch die Formalismusrevision weder bestätigt noch umgedeutet.

## 6. Arbeitsweise und Veröffentlichungen

Für jeden tatsächlichen Paketpatch gelten eng begrenzter Auftrag, Prüfung der verwendeten Codepfade, passende Tests und nachvollziehbare Änderungsnotiz. Dokumentationskorrektur, Verhaltensänderung und neue Modellannahme werden getrennt benannt. Reine Umbenennung gilt nicht als empirische Validierung. Unveränderte Pakete benötigen keinen künstlichen Versions-Bump.

Die zuvor festgelegte Einzelentscheidung für Zenodo-Veröffentlichungen bleibt bestehen. Diese Revision enthält keinen automatischen Release und keinen neuen Auftrag zur parallelen Umsetzung aller Kandidaten.
