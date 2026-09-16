# Verifikation — Revision 2 als Basis, Erweiterungen der Revision 3

Stand: 16. September 2026. Basissuite: [verify_formalism.py](verification/verify_formalism.py), [Laufbericht](verification/verification_results.json). Erweiterungen: [verify_extensions.py](verification/verify_extensions.py), [Laufbericht](verification/extension_results.json). Die 18 Revision-3.2-Prüfungen (Transformation, Viabilität) stehen separat in [TRANSFORMATION_VERIFICATION.md](TRANSFORMATION_VERIFICATION.md); die beiden optionalen F08/F09-Module (Sheaf-Kontextualität, PID/RB) unten in Abschnitt „Optionale Module F08/F09“.

## Reproduktion

```bash
python -m pip install -r verification/requirements.txt
python verification/verify_extensions.py
python verification/verify_formalism.py
```

Die Basissuite benötigt nur die Python-Standardbibliothek; die Erweiterungen NumPy. Beide Skripte schreiben ihren jeweiligen Laufbericht neben sich und beenden sich bei einer fehlgeschlagenen Prüfung mit Exitcode 1. Optional lässt sich mit `--output PATH` ein anderer Ergebnisort wählen. Die Reihenfolge oben erzeugt den neuen Bericht vor dem übergreifenden Linktest. Es findet keine Netzwerkabfrage statt.

## Umfang

Acht Gegenbeispiele halten die Grenzen der alten Allgemeinbehauptungen fest: identische Sigmoidkurve bei unterschiedlicher Erholung; unzentrierte und zentrierte kubische Dynamik; positives a ohne Bistabilität; Beckenwahrscheinlichkeit versus Distanz; gerichtete Matrix mit negativer quadratischer Form; Zeitfensterfehler bei I/C; Einheitenabhängigkeit des alten Frame-Quotienten; S₈ oberhalb 1.

Weitere zehn mathematische Prüffälle betreffen die korrigierten kubischen Äste und Zeitskalen, die Diskriminantenregion einschließlich Grenzfällen, einen binären Informationskanal, die normierte Frame-Hypothese, einen zulässigen antisymmetrischen Matrixanteil, Wärmebilanz und Entropieproduktion, explizit normierte Selbstähnlichkeit linearer Relaxation, diskrete Raten und Δt-Schätzung sowie die lokalen AMOC-/Solar-Teilmodelle. Eine zusätzliche Prüfung kontrolliert die relativen Verweise der aktuellen Hauptdokumente.

## Aussagekraft

Diese 19 Prüfungen kontrollieren angegebene mathematische Zusammenhänge und den Dokumentverbund. Sie testen keine Universalität in der Natur. Die Selbstähnlichkeitsrechnung betrifft genau die festgelegte lineare Modellklasse; ein empirischer domänenübergreifender Nachweis ist damit nicht erbracht.

Für den Wärmefall werden die analytische Lösung, numerische Ableitungen, Energiebilanz und Entropieproduktion gegeneinander geprüft. Für die kubische Dynamik werden Gleichgewichte und ihre Ableitungen sowie die Wurzelstruktur verglichen. Die Δt-Schätzung ist ein demonstrierter Korrekturvorschlag, kein bereits eingespielter Patch in `neural-avalanche-utac`.

Die alten, in den Ausgangsdokumenten erwähnten Skripte aus `verification/` und `Gemini.txt` wurden hier nicht bereitgestellt. Johann berichtet ihre lokale Nachprüfung und die Archivierung der älteren Cusp-Verifikation; diese übermittelte Prüfung wird von unseren ausgeführten Tests getrennt. Der aktuelle [Verifikationshinweis](verification/README.md) macht den Status ausdrücklich kenntlich. Produktionspakete und ihre Testsuiten werden durch diese Dokumentrevision nicht neu ausgeführt.

Der tatsächliche Ausführungsstatus, Python-Version und alle Messwerte stehen im JSON-Laufbericht. Gegenbeispiele bleiben auch dann relevant, wenn eine spätere Modellfamilie um zusätzliche Annahmen erweitert wird: Dann ist ausdrücklich festzuhalten, welche Annahme den Geltungsbereich verändert.

## 16 Ergänzungsprüfungen

| Bereich | Tatsächlich implementierte Prüfung |
|---|---|
| Rekonstruktion | Kreiszustände aus zwei Beobachtungen rekonstruieren; Mehrdeutigkeit bei resonanter Abtastung und Konditionierung zeigen |
| Gedächtnis | analytische Zweizustandslösung gegen numerische Ableitungen und separat berechnetes Gedächtnisintegral |
| Geschlossenheit | PC=CQ und mehrere Zeitschritte; verschiedene Mikropräparationen; expliziter Gegenfall und Fehlergrenze |
| EI | Summenformel gegen Entropiedifferenz; uniforme und angeglichene Ensembles; Datenverarbeitung bei festem Ensemble |
| SVD | Singularwerte numerisch bestimmen; EI=0-Grenzfall für alle 15 Partitionen von vier Zuständen |
| Reversibilität | stochastische Inverse und Verletzung von Detailed Balance am Drei-Zyklus |
| Selbstähnlichkeit | topologische Konjugation bei verschiedenen Raten; σ-Reskalierung und Rangdefizit der Parametersensitivität |
| GENERIC | 32 Parameterkombinationen: Entropiegradient numerisch, PSD, Degeneration, Energiefluss und Entropieproduktion |
| Belastbarkeit | zwei Lösungen bei gleicher Rate, Grenzzeit ln 3 und robuste Randbedingung |
| Prädiktive Zustände | 128 Pfadwahrscheinlichkeiten konditionieren; persistente binäre Kette mit zwei Klassen versus IID-Prozess mit einer |
| Dokumentverbund | relative Links und geschlossene Codeblöcke in aktuellen Dokumenten |

19 Basisprüfungen plus 16 Ergänzungen ergeben 35 benannte Prüfungen. Die JSON-Berichte zeigen, welche davon beim jeweiligen Lauf bestehen. Ein einzelner benannter Test kann mehrere Parameterfälle enthalten. Der Zufallsvergleich nutzt einen festen Seed, die SVD-Rangprüfung eine offengelegte numerische Toleranz.

Die Checks beweisen keine allgemeine Takens-Garantie, keine RG-Universalität und keine empirische Individuation. Sie kontrollieren konkrete Ableitungen, Fehlergrenzen und Gegenbeispiele. NIS+, PID-Schätzer und vollständige Literaturdatensätze wurden nicht ausgeführt. Die verwendete NumPy-Version wird im Ergänzungsbericht protokolliert.

## Optionale Module F08/F09 (16. September 2026, nicht Teil des Kerns)

Geliefert von Aeon (GrokBot-Agent), Checksummen und Skriptläufe von Claude unabhängig nachgerechnet — keine Mutation von `FORMALISM.md`/`REVISION_3_2.md` (Prüfsummen identisch vor/nach Lieferung). Herkunft und Abnahmebedingungen: [reviews/2026-09-16_gemini_extensions_review_aeon.md](reviews/2026-09-16_gemini_extensions_review_aeon.md), [FOLLOWUP_TICKETS.md](FOLLOWUP_TICKETS.md) (F08/F09).

| Modul | Skript | Bericht | Ergebnis |
|---|---|---|---|
| Sheaf-Kontextualität (F08) | [verify_sheaf_contextuality.py](verification/verify_sheaf_contextuality.py) | [Laufbericht](verification/verify_sheaf_contextuality_results.json) | 6/6 — klassisch CF=0, PR-Box CF=1, CHSH-Tabelle CF=0,25, VB1-Widerspruchsfall ohne globales Assignment |
| PID/Redundancy Bottleneck (F09) | [verify_pid_rb.py](verification/verify_pid_rb.py) | [Laufbericht](verification/verify_pid_rb_results.json) | 7/7 — UNIQUE/XOR/AND/Vollkopie-Gatter, RB(0) gegen Blackwell-Referenz, `EI_q` neben PID berichtet statt gleichgesetzt |

Benötigt zusätzlich SciPy (`verification/requirements_sheaf_pid.txt`) für den LP-Löser der Contextual Fraction. Beide Module sind optional und stehen neben VB1 bzw. `EI_q`, nicht als deren Ersatz — siehe [sheaf_contextuality.md](sheaf_contextuality.md) und [pid_redundancy_bottleneck.md](pid_redundancy_bottleneck.md).
