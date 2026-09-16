# Revision 3.2 — Transformation und überlappende Systemzugehörigkeit

16. September 2026. Vertiefung der zwei bereitgestellten Dokumente und Erweiterung des Kernformalismus auf Johanns ausdrücklichen Wunsch.

## Inhaltlicher Ausgangspunkt

Eine Einheit kann intern ein System sein und zugleich zu mehreren Systemen gehören. Diese Zugehörigkeiten können andere Einflüsse, Bezugsgrößen, Anforderungen und Regeln mitbringen. Daraus können unterschiedliche kontextbezogene Werte entstehen; Variation ist möglich, aber nicht zwingend. Untersucht werden selbstähnliche Muster beim Zusammensetzen, Zerlegen und Transformieren solcher dynamischen Beschreibungen.

## Was geändert wurde

- `context_transformations.md` führt eine gemeinsame Notation und Verträglichkeitsbedingungen für Kontext, Zugehörigkeiten, geteilte Größen, dynamische Darstellungen, Komposition, Zerlegung und Metaregeln ein.
- `FORMALISM.md` verankert diese Regeln im Kern und verbindet sie ausdrücklich mit CREP, UTAC und AFET. Paarweise additive Kopplung wird als ein möglicher Ansatz eingeordnet.
- `emergence_and_closure.md` behält die bisherigen Rechnungen bei und ergänzt kontextabhängige Schließung, einen Verlaufsfehler aus lokalen Residuen, wechselnde Markov-Partitionen und die Trennung von Dynamikschließung und Aufgabeninformation. Die universell klingende Überschrift der bereitgestellten Fassung wird an Johanns tatsächliche Leitthese angepasst.
- `worked_example_viability.md` behält den skalaren Ausgangsfall bei und arbeitet zwei gekoppelte Bestände durch: gemeinsame Ressourcen, Summe und Verteilung, exakte Invarianzbedingungen, optimale Grenzzeit im symmetrischen Beispiel, interne Zerlegung, bewegliche Grenzen und endliche Eingriffsvorräte.
- `verification/verify_transformations.py` ergänzt 18 reproduzierbare Prüfgruppen. [Prüfumfang und Resultate](TRANSFORMATION_VERIFICATION.md).

Die wichtigsten neuen Ergebnisse sind begrenzte Ableitungen in den angegebenen Modellen. Die Notations- und Prüfverträge sind Projektdefinitionen. Literaturanschlüsse zu Lumpability, Gedächtnis und Barrieren bleiben als solche gekennzeichnet; die projektbezogene Zusammenführung wird diesen Quellen nicht als bereits bewiesene Gesamttheorie zugeschrieben.

## Anwendung dieses Ergänzungspakets

Dieses ZIP ist eine gezielte Ergänzung eines vorhandenen Formalismus-Verzeichnisses. Seine vier inhaltlichen Zieldateien sind `FORMALISM.md`, `context_transformations.md`, `emergence_and_closure.md` und `worked_example_viability.md`. Es enthält außerdem diese Änderungsnotiz, die Prüfübersicht, das neue Skript, Anforderungen und Ergebnisse. Bestehende Referenzdokumente, weitere Beispiele, alte Prüfsuiten und Archive werden nicht mit älteren Kopien überschrieben.

`apply_manifest_revision_3_2.json` nennt für jede Zieldatei Pfad, Aktion, neue SHA-256-Prüfsumme und für Ersetzungen bekannte Ausgangsprüfsummen. Es ist ein eigenes Manifest dieser Ergänzung. Die bisherigen globalen Manifeste werden dadurch nicht automatisch neu erzeugt. Wer nach der Integration ein globales Gesamtmanifest verwendet, muss es für den tatsächlichen gemeinsamen Endstand aktualisieren.

Die beiden vertieften Dokumente basieren auf den zuletzt angehängten Fassungen der Revision 3. Für `FORMALISM.md` wurde der vorhandene konsolidierte Stand 3.1 verwendet. Die gelesenen Ausgangsdateien sind unverändert im Unterordner `baseline/` enthalten. Zusätzlich erkannte ältere Varianten der beiden Anhänge werden im Manifest nur als bekannte Vergleichsstände vermerkt.

Vor dem Ersetzen eines lokal weiterentwickelten Dokuments dessen Prüfsumme mit den bekannten Ausgangsständen vergleichen. Bei Abweichung den Text zusammenführen. Das Paket führt selbst keine Schreib- oder Löschoperationen aus und initialisiert kein Git-Repository.

Relative Verweise auf bereits vorhandene Dateien wie `LITERATURE_CONNECTIONS.md`, `VERIFICATION.md` und die übrigen Layer-/Beispieldokumente setzen das bestehende Formalismus-Verzeichnis voraus. Die neuen Verweise wurden gegen diesen Bestand geprüft. Die Prüfsummen im Ergänzungsmanifest erfassen die eigentlichen Zieldateien; dieses Manifest kann sich nicht selbst mit seiner eigenen Prüfsumme erfassen.

## Nächster empirischer Schritt

Ein konkreter Anwendungsfall sollte dieselbe Einheit in zwei tatsächlich beobachtbaren Systemzusammenhängen erfassen: gemeinsamer physischer Zustand, unterschiedliche Aufgaben, ihre Eingriffe und die gemeinsam verfügbare Ressource. Dann werden eine reine Zustandsbeschreibung, eine kontexterweiterte Beschreibung und ein Modell mit Gedächtnis unter denselben Daten- und Eingriffsbedingungen verglichen. Der Vergleich kann zeigen, wo Transformation Information erhält, wo zusätzliche Zustände nötig sind und ob das angenommene Kompositionsmuster außerhalb des synthetischen Beispiels trägt.
