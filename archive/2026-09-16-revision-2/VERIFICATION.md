# Verifikation der Revision 2

Stand: 16. September 2026. Ausführbares Skript: [verify_formalism.py](verification/verify_formalism.py). Maschinenlesbarer Laufbericht: [verification_results.json](verification/verification_results.json).

## Reproduktion

```bash
python verification/verify_formalism.py
```

Die Python-Standardbibliothek genügt. Das Skript schreibt den Laufbericht neben sich und beendet sich bei einer fehlgeschlagenen Prüfung mit Exitcode 1. Optional lässt sich mit `--output PATH` ein anderer Ergebnisort wählen.

## Umfang

Acht Gegenbeispiele halten die Grenzen der alten Allgemeinbehauptungen fest: identische Sigmoidkurve bei unterschiedlicher Erholung; unzentrierte und zentrierte kubische Dynamik; positives a ohne Bistabilität; Beckenwahrscheinlichkeit versus Distanz; gerichtete Matrix mit negativer quadratischer Form; Zeitfensterfehler bei I/C; Einheitenabhängigkeit des alten Frame-Quotienten; S₈ oberhalb 1.

Weitere zehn mathematische Prüffälle betreffen die korrigierten kubischen Äste und Zeitskalen, die Diskriminantenregion einschließlich Grenzfällen, einen binären Informationskanal, die normierte Frame-Hypothese, einen zulässigen antisymmetrischen Matrixanteil, Wärmebilanz und Entropieproduktion, explizit normierte Selbstähnlichkeit linearer Relaxation, diskrete Raten und Δt-Schätzung sowie die lokalen AMOC-/Solar-Teilmodelle. Eine zusätzliche Prüfung kontrolliert die relativen Verweise der aktuellen Hauptdokumente.

## Aussagekraft

Diese 19 Prüfungen kontrollieren angegebene mathematische Zusammenhänge und den Dokumentverbund. Sie testen keine Universalität in der Natur. Die Selbstähnlichkeitsrechnung betrifft genau die festgelegte lineare Modellklasse; ein empirischer domänenübergreifender Nachweis ist damit nicht erbracht.

Für den Wärmefall werden die analytische Lösung, numerische Ableitungen, Energiebilanz und Entropieproduktion gegeneinander geprüft. Für die kubische Dynamik werden Gleichgewichte und ihre Ableitungen sowie die Wurzelstruktur verglichen. Die Δt-Schätzung ist ein demonstrierter Korrekturvorschlag, kein bereits eingespielter Patch in `neural-avalanche-utac`.

Die alten, in den Ausgangsdokumenten erwähnten Skripte aus `verification/` und `Gemini.txt` wurden nicht bereitgestellt. Dieses neue Skript ersetzt sie als Begleiter dieser Revision; es gibt nicht vor, ihre berichteten Läufe reproduziert zu haben. Die Produktionspakete und ihre Testsuiten wurden für diese Dokumentrevision nicht neu ausgeführt.

Der tatsächliche Ausführungsstatus, Python-Version und alle Messwerte stehen im JSON-Laufbericht. Gegenbeispiele bleiben auch dann relevant, wenn eine spätere Modellfamilie um zusätzliche Annahmen erweitert wird: Dann ist ausdrücklich festzuhalten, welche Annahme den Geltungsbereich verändert.
