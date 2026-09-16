# Prüfung der Transformations- und Viabilitätserweiterung

Revision 3.2, 16. September 2026. **18 von 18 neuen synthetischen Prüfgruppen bestanden.** Die Resultate stehen in [transformation_results.json](verification/transformation_results.json); das ausführbare Skript ist [verify_transformations.py](verification/verify_transformations.py).

Die Dokumente enthalten die Herleitungen einschließlich ihrer Voraussetzungen. Das Skript prüft konkrete Fälle durch unabhängige numerische Differentiation, Integration, Quadratur, Matrixrechnungen und gezielte Gegenbeispiele. Das ist eine Fehlerkontrolle der Rechnungen und keine empirische Bestätigung über reale Domänen hinweg. Die Prüfgruppenzahl bezeichnet weder unabhängige Experimente noch die Zahl einzelner Assertions.

## Reproduktion

Python 3.10 oder neuer und NumPy 2.x; tatsächlich ausgeführt mit Python 3.12.14 und NumPy 2.3.5. Keine Einzelpakete des Ökosystems werden importiert.

```bash
python -m pip install -r verification/requirements_transformations.txt
python verification/verify_transformations.py
```

Die Bibliothek wird nur installiert, falls sie in der eigenen Umgebung noch fehlt. Ohne Parameter schreibt das Skript neben sich `transformation_results.json`. Ein anderer Ausgabeort ist mit `--output PFAD` möglich. Es endet bei einer fehlgeschlagenen Prüfung mit einem Fehlercode; die Prüfungen bleiben auch unter `python -O` aktiv. Zufallsprüfungen haben feste Seeds. Bei erneutem Ausführen ändern sich insbesondere der Zeitstempel und gegebenenfalls Rundungsdetails anderer Plattformen.

## Abgedeckte Aussagen

| ID | Konkrete Prüfung | Grenze der Aussage |
|---|---|---|
| T01 | Ableitungen mit Kontext, beweglicher Schwelle und Normierung | deterministische glatte Beispiele |
| T02 | Zustandsabhängige Zeitänderung; endlicher transformierter Horizont | keine allgemeine globale Orbitklassifikation |
| T03 | Vollständige Ableitung bei zustandsabhängigem Parameter | Gegenfall zum Einfrieren |
| T04 | Zusammengesetzte Abbildungen, Zeitfaktoren und Residuen | numerisch geprüfte glatte Skalarfälle |
| T05 | Skalare Lösungen, Randbedingung und erster Grenzkontakt | konstantes lineares Modell |
| T06 | Summen-/Differenzdynamik und Rücktransformation in 100 Fällen | gleiche Rückkehrraten |
| T07 | Zwei gleiche Summen mit unterschiedlichen Ableitungen | konkreter Nichtgeschlossenheitsbeleg |
| T08 | Gedächtnisformel mit und ohne Antrieb gegen vollständige Lösung | lineares Zweikomponentenmodell |
| T09 | 600 Randprüfungen in 100 Parameterfällen; knappe Budgets | numerische Ergänzung des analytischen Beweises |
| T10 | Geteiltes Budget: Einzel- versus gemeinsame Durchführbarkeit | vorgegebene Eingriffsmenge |
| T11 | Grenzzeit ln 9 und fünf andere zulässige Steuerungen | Unmöglichkeit für alle Steuerungen folgt aus dem Beweis, nicht aus fünf Stichproben |
| T12 | Geschlossene Summe verliert lokale Sicherheitsinformation | Aufgabe x₁≥0 und x₂≥0 |
| T13 | Bewegliche Grenzen und deren zusätzliche Ratenanforderung | vorgegebene glatte Grenzverläufe |
| T14 | Endlicher Eingriffsvorrat und gemeinsame Defizitbilanz | keine Behauptung, dass die obere Zeitschranke erreichbar ist |
| T15 | Exakte Schließung mit wechselnder Partition | festgelegte Darstellungsfolge |
| T16 | Teleskopidentität und nichttriviale Totalvariationsschranke, 30 Folgen | kein statistisches Konfidenzintervall |
| T17 | Residuum zu Verlaufsfehler einschließlich L=0 | scharfe lineare Kontrollfälle für die bewiesene Abschätzung |
| T18 | Flussbilanz über zwei aufeinanderfolgende Zerlegungen | keine automatische Schließung aller verbleibenden Terme |

Bei der Gedächtnisrechnung lag die größte Abweichung der verwendeten Quadratur von der vollständigen linearen Lösung unter 1,3×10⁻⁹. Der Fehler der numerischen Zweikomponentenlösung beim Kontakt t=ln 9 lag unter 4×10⁻¹⁵. Solche Zahlen beschreiben ausschließlich diese Rechnungen und ihre Toleranzen.

## Verhältnis zu den früheren Prüfungen

Die 19 Basis- und 16 Literatur-/Erweiterungsprüfungen der Revision 3 sind unverändert und wurden für diese gezielte Vertiefung nicht erneut ausgeführt. Ihre frühere Reproduktion ist ein eigener Arbeitsnachweis. **Neu ausgeführt wurden hier 18 Prüfgruppen.** Daraus wird keine Aussage „53 neue Bestätigungen“ abgeleitet.

Noch offen sind empirische Kalibrierung, Identifikation veränderlicher Kopplungen und Regeln, Messunsicherheit, beschränkte Beobachtung, Eingriffsverzögerungen sowie reale Ressourcenkosten. Die Dokumente geben dafür bereits Modellstellen und überprüfbare Fragen vor.
