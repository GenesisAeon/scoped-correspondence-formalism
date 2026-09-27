# SCF H0–H7: unabhängiger Review und Korrekturauftrag

**Stand:** 27. September 2026 · **geprüfter Commit:** `9dde420561fc131c29c82f413081cfb2c60f4561` · **Ergebnis:** Änderungen erforderlich, bevor die epistemische Schicht als vollständig abgenommen gelten sollte.

Die Architektur ist sinnvoll und die zentralen Kontrollbeispiele funktionieren. Die Implementierung enthält jedoch Fehler, durch die unvollständige oder ungültige Auswertungen als logische, minimale oder sichere Ergebnisse ausgegeben werden. Gerade eine Evidenzschicht muss diese Übergänge zuverlässig verhindern.

Dieser Review verändert keinen Produktionscode. Er liefert kleine Gegenfälle, erwartete Ergebnisse und konkrete Abnahmekriterien. Priorität P1 bedeutet: vor Verwendung der betreffenden Zertifikate beheben. P2 bedeutet: Vertrag, Nachvollziehbarkeit oder Planabdeckung vervollständigen.

## 1. Prüfgrundlage und belastbarer Stand

- [Geprüfter Commit](https://github.com/GenesisAeon/scoped-correspondence-formalism/commit/9dde420561fc131c29c82f413081cfb2c60f4561).
- [GitHub-CI für genau diesen Commit](https://github.com/GenesisAeon/scoped-correspondence-formalism/actions/runs/36268363004): abgeschlossen, `success`.
- Referenz: `SCF_ASSUMPTION_EVIDENCE_IMPLEMENTATION_PLAN.md`, insbesondere §§4, 6.3, 9 und 12–14.
- Alle 235 nicht archivierten Python-Dateien des lokalen Review-Snapshots wurden gegen die Git-Blob-Hashes dieses Commits geprüft. Zwei archivierte Python-Dateien gehören nicht zum Snapshot. Der Snapshot ist kein vollständiger Git-Checkout aller historischen Dokumente und Binärdateien.
- Alle sechs neuen H-Verifikationen bestehen unabhängig: **9 + 7 + 6 + 8 + 6 + 5 = 41 Prüfungen**.
- Vollständiger lokaler Suite-Aufruf: **105 Skripte; 102 bestanden, 1 übersprungen, 2 fehlgeschlagen**. Die zwei Fehlschläge sind Dokument-Linkprüfungen und betreffen beide dieselbe im Snapshot fehlende DOCX. Ihr Vorhandensein im gepushten Git-Baum ist bestätigt. Daraus folgt kein Repository-Linkfehler. Der übersprungene Test ist `verify_sparc_real_local.py`.
- Deshalb wird hier kein unabhängig grüner lokaler „105/105“-Lauf behauptet. Der grüne GitHub-Lauf und die lokalen Resultate werden getrennt ausgewiesen.
- Die CLI wurde ausgeführt. Zusätzlich wurden **21 gezielte Fälle** ausgewertet. Sie sind Varianten und Vertragstests zu den untenstehenden Befundgruppen, keine 21 eigenständigen Bugs.

Der vorhergehende Galaxien-Fix-Commit `398b919` ist vorhanden. Eine erneute vollständige fachliche Abnahme dieser Galaxienänderungen war nicht Gegenstand dieses Reviews. H6c bleibt als zurückgestellt dokumentiert; hier wurde keine neue Lizenzprüfung vorgenommen.

## 2. Was bereits trägt

Die Trennung von Annahmen, Beobachtungsfasern und Entscheidungen ist fachlich produktiv. K1 demonstriert unterschiedliche inklusionsminimale Supports; K4 erhält eine diskrete Zielwertmenge statt sie in ein scheinbar ausgefülltes Intervall umzudeuten. K5 zeigt den Quantorenunterschied zwischen zustandsweise möglichen und gemeinsam sicheren Eingriffen. K6 unterscheidet Minimax und Minimax-Regret. K8 hält Dynamikverträglichkeit und Ereignisbeobachtbarkeit getrennt.

Auch die Kennzeichnung numerischer Adapter als `numerical_sample` ist ein guter Ausgangspunkt. Die folgenden Befunde betreffen vor allem die Zuverlässigkeit und Bedeutung der zurückgegebenen Zertifikate.

## 3. Prioritäten

| ID | Priorität | Befund | Betroffene Teile |
|---|---|---|---|
| R1 | P1 | Unvollständige letzte Löschprüfung bestätigt trotzdem Minimalität | H2 |
| R2 | P1 | `None` als Kandidat kollidiert mit dem fehlenden Zeugen | H1 |
| R3 | P1; numerische Ergänzungen P2 | Ungültige Prädikatwerte werden Wahrheit, Ausschluss oder Sicherheit | H1, H3, H4 |
| R4 | P1; Quantorenklärung P2 | Adapter erklären Rechenfehler zu Widerlegungen; leere Evidenz wird bestätigt | H6a |
| R5 | P2 | Suchvollständigkeit und Zielraumabdeckung werden vermischt bzw. verloren | H1–H4 |
| R6 | P2 | Doppelte Annahmen-IDs verfälschen die Löschsuche | H2 |
| R7 | P2 | Budgetvertrag ist unvollständig; Nullbudget wird teilweise übergangen | H1–H3 |
| R8 | P2 | Informationsmodus und vollständige Berichtsausgabe fehlen gegenüber dem Plan | H5–H7 |

## R1 — Minimalität trotz unvollständiger letzter Prüfung

**Stellen:** [supports.py, Zeilen 132–159](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/9dde420561fc131c29c82f413081cfb2c60f4561/src/scoped_correspondence/epistemic/supports.py#L132-L159) und Zeilen 204–227.

Die Löschsuche interpretiert eine nicht abgeschlossene Teilprüfung als Grund, eine Annahme zu behalten. Liegt der Abbruch in der letzten Iteration, folgt dennoch `search_complete=True`.

**Gegenfall Support:** W={0,1}, eine überall wahre Annahme A, überall wahre Zielaussage C, `candidate_budget=3`. Die Ausgangsprüfung verbraucht zwei Kandidaten; beim Entfernen von A bleibt nur eine Auswertung. Diese Teilprüfung ist `incomplete`. Trotzdem liefert die Funktion A als fertigen minimalen Support. Tatsächlich ist der leere Support ausreichend.

**Gegenfall Inkonsistenzkern:** W={0,1}, A₁ überall falsch, A₂ überall wahr, `candidate_budget=5`. Die letzte Prüfung ist unvollständig. Zurückgegeben wird der vermeintlich fertige Kern {A₁,A₂}. Der minimale Kern ist {A₁}.

**Korrektur:** Löschentscheidungen brauchen drei Ergebnisse: Entbehrlichkeit bestätigt, Notwendigkeit bestätigt, unbekannt. Ein unbekanntes Ergebnis darf keine Minimalitätsbestätigung erzeugen. Ein vorläufiger Support/Kern darf erhalten bleiben, muss aber als nicht minimalitätsverifiziert ausgewiesen werden.

Vollständiges Durchsuchen ist nicht für jede Entscheidung nötig: Ein gültiger Gegenzeuge kann bereits beweisen, dass eine gelöschte Annahme benötigt wird; ein zulässiges Modell kann die Konsistenz einer Kern-Teilmenge belegen. Entscheidend ist ein ausreichender Zeuge für genau die Löschentscheidung.

**Abnahme:** Beide Fälle reproduzieren und beheben; Abbruch innerhalb der letzten Teilprüfung testen; Fehler während einer Löschprüfung ebenso behandeln. Ein fertiges Minimalitätszertifikat braucht gültige Löschzeugen für alle verbliebenen Annahmen. Inklusionsminimalität bleibt von kleinster Kardinalität getrennt.

## R2 — Ein zulässiger `None`-Kandidat kann falsche Entailments erzeugen

**Stelle:** [finite.py, Zeilen 52–107](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/9dde420561fc131c29c82f413081cfb2c60f4561/src/scoped_correspondence/epistemic/finite.py#L52-L107).

`None` bedeutet intern „kein Zeuge gefunden“. `FiniteDomainSpec` lässt `None` jedoch als eindeutigen, hashbaren Kandidaten zu.

| Domäne und Aussage | Tatsächlich ausgegeben | Richtig |
|---|---|---|
| W=(None,), C(w)=False | `entailed_in_scope` | `negation_entailed_in_scope` |
| W=(None,0), C(w)=(w is not None) | `entailed_in_scope` | `underdetermined` |
| W=(0,None), dieselbe Aussage | `entailed_in_scope` | `underdetermined` |

**Korrektur:** Intern einen eindeutigen Sentinel oder separate `has_positive_witness`/`has_negative_witness`-Flags verwenden. Bei JSON-Ausgabe müssen „Zeuge vorhanden, Wert null“ und „kein Zeuge“ ebenfalls unterscheidbar bleiben. Alternativ wäre ein explizites Verbot von `None` eine engere API; still akzeptieren und falsch klassifizieren ist unzulässig.

**Abnahme:** Die drei Fälle sowie gültige falsy Nutzwerte wie `0` und `False` testen. Unterschiedliche Kandidaten dürfen durch Normalisierung nicht versehentlich zusammenfallen.

## R3 — Ungültige Prädikate werden zu Evidenz oder Sicherheit

**Stellen:** [finite.py, Zeilen 63 und 123](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/9dde420561fc131c29c82f413081cfb2c60f4561/src/scoped_correspondence/epistemic/finite.py#L63), `observation_fibers.py:88`, `decisions.py` in `uniform_safe_actions`.

Die Zielaussage wird auf `bool` geprüft, Annahmen und Antezedens werden dagegen mit `bool(...)` umgewandelt. Sicherheitsprüfungen verwenden Python-Truthiness.

**Reproduziert:**

- Annahme liefert `None`: alle Kandidaten werden ausgeschlossen; Ergebnis `no_admissible_model_in_scope`, null Fehler.
- Annahme liefert `NaN` oder den String `"false"`: als wahr akzeptiert, null Fehler.
- Antezedens liefert `None`: als „Antezedens niemals erfüllt“ zertifiziert.
- Sicherheitsprädikat liefert `NaN`: die Aktion wird als uniform sicher ausgegeben.

Das verletzt den expliziten Planvertrag: Bool-Prädikate liefern boolesche Ergebnisse; fehlende Angaben und Rechenfehler werden nicht in Wahrheitswerte umgedeutet.

**Korrektur:** Eine gemeinsame geprüfte Bool-Auswertung für Annahmen, Zielaussagen, Antezedens und Sicherheit verwenden. Zulässige Bool-Typen ausdrücklich definieren. Ungültige Rückgaben entweder klar ablehnen oder als Auswertungsfehler mit unbekanntem Ergebnis dokumentieren. Keine positive Sicherheitsgarantie aus einem Fehler erzeugen. Der Antezedensdurchlauf benötigt dieselbe Fehlerbehandlung wie der Hauptdurchlauf.

**Numerische Ergänzungen (P2):**

1. `identified_values` akzeptiert einen überall unendlichen Zielwert und meldet Punktidentifikation. Für eine ausdrücklich erweiterte reelle Zielgröße wäre das mathematisch möglich. Der aktuelle Vertrag erklärt diese Bedeutung jedoch nicht. Numerische Zielwerttypen und der Umgang mit NaN/±∞ müssen festgelegt werden; ein pauschales Verbot für beliebige kategoriale Zielwerte wäre überzogen.
2. `compare_decisions` prüft die Endlichkeit der Eingabeverluste, nicht der berechneten Regrets. Folgende endlichen Eingaben erzeugen einen falschen Gleichstand:

| Aktion | Verlust in s₁ | Verlust in s₂ |
|---|---:|---:|
| A | −1e308 | 1e308 |
| B | 1e308 | −9e307 |

Die tatsächlichen maximalen Regrets sind ungefähr 1,9e308 für A und 2e308 für B; A gewinnt. Float-Subtraktion liefert für beide `inf`, die API wählt beide. Ein klarer Überlauffehler genügt als erste Korrektur; alternativ skaliert oder exakt rechnen. Jedenfalls keinen rechnerisch entstandenen Gleichstand als Entscheidung ausweisen.

**Abnahme:** Ungültige Rückgaben an allen vier Bool-Einstiegen; Fehler im Antezedens; nichtendliche berechnete Entscheidungsscores. Fehlerstatus und mathematische Falschaussage bleiben getrennt.

## R4 — Adapter verlieren Fehler- und Quantorensemantik

**Stellen:** [adapters.py, Zeilen 57–80](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/9dde420561fc131c29c82f413081cfb2c60f4561/src/scoped_correspondence/epistemic/adapters.py#L57-L80), Zeilen 106–126.

### R4a: Rechenfehler und leere Evidenz (P1)

Ein mit der echten Korrespondenz-API erzeugter Bericht mit nichtendlichem Residuum trägt `all_finite=False`. Der Adapter macht daraus `negation_entailed_in_scope`, `search_complete=True`, `n_errors=0`. Ein ungültiges Residuum beweist keine mathematische Negation.

Ein leerer Satz von Aktionsberichten wird über `all([])` zu `dynamics_exact=True`. Der Adapter liefert `entailed_in_scope` bei `n_domain=0`, ohne Vakuumsmarkierung. Das umgeht die sonst ausdrücklich geforderte Trennung zwischen leerer Eingabe und gültiger Evidenz.

**Korrektur:** Gültigkeit, Vollständigkeit und Fehler des Ausgangsberichts übernehmen. Leere Evidenz klar ablehnen oder als nicht ausgewertet kennzeichnen. Nichtendliche Berechnungen als Fehler behandeln; zusätzliche gültige Gegenzeugen dürfen nur die Aussagen stützen, die sie tatsächlich belegen.

### R4b: Negation einer Gesamtaussage versus Negation pro Kandidat (P2)

Ein tatsächlicher Korrespondenztest mit Residuen [0,1] enthält einen erfüllenden und einen verletzenden Punkt. Der Adapter liefert dennoch `negation_entailed_in_scope`. Dasselbe geschieht bei einer exakten und einer nicht exakten Makroaktion.

Die Unterscheidung lautet:

`¬∀w C(w)` ist etwas anderes als `∀w ¬C(w)`.

Die Negation der globalen Aussage „alle getesteten Paare bestehen“ ist bei einem Fehler durchaus richtig. Das ist eine mögliche Interpretation des Adapter-Docstrings. Die aktuellen Kandidatenzähler und die gemeinsam verwendeten H1-Statusnamen lassen diese globale Proposition jedoch wie eine Aussage über jeden einzelnen Kandidaten aussehen.

**Zwei saubere Lösungen:**

1. Pro-Paar-/Pro-Aktions-Semantik: gemischte Ergebnisse werden `underdetermined`; beide Zeugen ausgeben.
2. Aggregierte Proposition: Quantor und Prüfgegenstand explizit speichern; die globale Proposition als solche auswerten und ihre Stichprobenzahl separat führen. Ein Gegenbeispiel widerlegt diese globale Proposition, sagt aber nicht, dass jedes Paar scheitert.

Die Quelle enthält derzeit nicht alle per-Paar-Toleranzinformationen, um jeden Adapterstatus nachträglich verlässlich zu rekonstruieren. Benötigte Pass/Fail-Metadaten und Toleranzen im Ausgangsbericht ergänzen oder die Adapteraussage entsprechend begrenzen.

**Abnahme:** echte Quellberichte mit gemischten Ergebnissen, nichtendlichen Residuen und leerer Aktionsmenge prüfen. Den vorhandenen Test, der „irgendeine Verletzung → Negation“ ohne diese Quantorenklärung festschreibt, fachlich anpassen.

## R5 — Suchvollständigkeit und Abdeckung des Zielraums gehen verloren

**Stellen:** [finite.py:93–95](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/9dde420561fc131c29c82f413081cfb2c60f4561/src/scoped_correspondence/epistemic/finite.py#L93-L95); `records.py:23–27,80`; Weitergabe über `FiberReport` und nachgelagerte Berichte.

**Fall 1:** W={0,…,9}, C(w)=„w gerade“, Budget 2. Zwei gegensätzliche Zeugen reichen für `underdetermined`. Das Ergebnis ist richtig. `search_complete=True` bei zwei von zehn geprüften Kandidaten beschreibt hingegen nicht die abgeschlossene Suche, sondern die Gewissheit dieses einzelnen Schlusses.

**Fall 2:** `coverage="partial"` wird validiert, danach jedoch nicht ausgewertet oder weitergereicht. Für dieselbe Kandidatenliste sind Claim- und Faserbericht bei `complete` und `partial` identisch. Auch Identifikation und sichere Aktionen verlieren diese Information.

**Korrektur:** Drei Achsen erhalten:

- Ist dieser logische Schluss bereits belegt?
- Wurden alle gelieferten Kandidaten fehlerfrei untersucht?
- Decken diese Kandidaten den behaupteten Zielraum vollständig ab?

Ein lokal vollständiger Scan einer partiellen Kandidatenliste darf weiterhin lokale Aussagen tragen. Er benötigt den eingeschränkten Geltungsbereich im Bericht. Nicht jede partielle Abdeckung muss pauschal jeden lokalen Status auf `incomplete` setzen.

**Abnahme:** Frühstoppfall bleibt logisch `underdetermined`, hat aber keine vollständige Kandidatensuche. `coverage`, Zielraumbeziehung und Scope werden durch Claim → Faser → Identifikation → Entscheidung erhalten. Den vorhandenen Test `abort_before_after_witnesses`, der derzeit `search_complete=True` verlangt, entsprechend korrigieren.

## R6 — Nicht eindeutige Annahmen-IDs verfälschen Supports

**Stelle:** `supports.py:144,215`; `AssumptionSpec` prüft nur, ob die ID nicht leer ist.

**Gegenfall:** W={0,1}. A₁: w=0, A₂: True; beide mit ID `same`. C: w=0. Die Löschung nach ID entfernt beide Prädikate gleichzeitig. Das Ergebnis enthält zweimal `same` und gilt als vollständig, obwohl A₂ redundant ist.

**Korrektur:** Eindeutigkeit von Annahmen-IDs vor der Suche validieren, auch über Hintergrund- und veränderbare Annahmen hinweg. Kollisionen nicht still zusammenführen. Stabile ID und tatsächliche Prädikatdefinition müssen eindeutig zusammenpassen.

**Abnahme:** Gleiche ID mit unterschiedlichen Prädikaten sowie ID-Kollision mit Hintergrundannahmen erzeugen einen erklärten Eingabefehler; gültige eindeutige Fälle bleiben unverändert.

## R7 — Budgetvertrag vervollständigen

**Stellen:** `finite.py`, `observation_fibers.py`, `supports.py:103–111,176–184`; Plan §6.3.

Die API begrenzt momentan Kandidatenscans. Der Plan verlangt getrennte Grenzen für Kandidaten, Prädikatauswertungen und Supportsuche sowie eine gemeinsame Grenze über verschachtelte Aufrufe. Die Zahlen 4096/4096/1000000 waren Beispielwerte; entscheidend ist die getrennte, überprüfbare Semantik.

**Reproduziert:** Bei drei Kandidaten, einer immer wahren Annahme, wahrer Aussage und falschem Antezedens ergeben sich sechs Annahmen-, drei Ziel- und drei Antezedensaufrufe. `n_evaluated=3` zählt Kandidaten korrekt; ein Prädikatbudget wird damit aber nicht umgesetzt. Der zweite Durchlauf ist nicht eigens begrenzt.

`subset_budget=0` verhindert außerdem die anfängliche Teilmengenprüfung nicht: Bei leerer Annahmenliste wird trotzdem eine Teilmenge geprüft und ein fertiger leerer Support zurückgegeben.

**Korrektur:** Getrennte Zähler und Limits; gemeinsames Budgetobjekt oder gleichwertige Weitergabe durch innere Aufrufe; Prüfung vor jeder budgetierten Operation einschließlich Ausgangsprüfung und Antezedens. Nichtnegative ganze Limits validieren. Nullbudget-Semantik ausdrücklich festlegen; soll eine Startprüfung ausgenommen sein, benötigt sie einen separat benannten Zähler.

**Abnahme:** Kleine exakt zählbare Fälle, Nullbudget und Abbruch innerhalb verschachtelter Prüfungen. Kein stilles Auffüllen des Budgets bei jedem inneren Aufruf. Bereits verwendete Kandidatenbudgets nicht rückwirkend als Prädikatbudgets umbenennen.

## R8 — Offene Planabdeckung und Berichte

### R8a: Der informative Zwischenmodus fehlt im Pufferpilot

Plan §12 verlangt Summe, Summe+Minimum, Summe+Vorzeichen. `evaluate_information_modes` liefert stattdessen Summe, Vorzeichen und Vollzustand. Diese Vergleiche sind sinnvoll, ersetzen aber den geplanten Zwischenfall nicht.

Auf der Summenfaser {(0,2),(1,1),(2,0)} identifiziert das Minimum die Aussage „beide Komponenten mindestens 1“. Bei beobachtetem Minimum 0 bleiben jedoch {(0,2),(2,0)} möglich. Die Aussage ist damit bestimmt, ein gemeinsam sicherer Eingriff bei Budget 1 existiert weiterhin nicht. Das ist der wesentliche Anschluss zwischen H3 und H4.

**Korrektur:** Minimum-Modus ergänzen, dessen verfeinerte Fasern tatsächlich durch die Sicherheits-API auswerten. Der Vollzustandsmodus darf als zusätzlicher Vergleich bleiben.

**Abnahme:** Minimum 0 → Eigenschaft identifiziert, uniforme Sicherheit bei Budget 1 unmöglich; Vorzeichen → beobachtungsabhängige sichere Politik mit Worst-Case-Budget 1; reine Summe → uniforme Grenze 2. Annahmen, Horizont und gehaltene Aktion bleiben explizit.

### R8b: Vollständige, selbstbeschreibende Berichtsausgabe

Die CLI funktioniert, unterstützt aber nur `--out` und gibt zusammengefasste JSON-Ergebnisse aus. Die in H6/H7 geforderten maschinenlesbaren Beispielberichte samt verständlicher Markdown-Ausgabe fehlen als durchgehender Export. Die im Plan beispielhaft genannten Flag-Namen sind dabei nicht verbindlich; die Funktionalität ist es.

`ClaimReport` verliert unter anderem Domain-ID, Scope-Text und verwendete Annahmen-IDs. Faser-, Identifikations-, Aktions- und Entscheidungsberichte tragen die Evidenz- und Empirieachsen nicht durchgehend, obwohl die Roadmap deren Trennung für jedes Ergebnis beansprucht.

**Korrektur:** Einen kleinen gemeinsamen Berichtskontext oder stabile Referenzen ergänzen: Prüfgegenstand, Scope, Domain/Abdeckung, Annahmen- und Zieldefinitionen, Evidenzart, empirischer Status, Budgets, ggf. Toleranzen und Quellbericht. Vorhandene Provenienzstrukturen wiederverwenden. Keine neue freie Textsprache und keinen zweiten Beweiskern dafür bauen.

**Abnahme:** Mindestens zwei vollständige Adapterberichte und ein integrierter Pufferbericht lassen sich als JSON und Markdown ausgeben; die Darstellung bewahrt die unterschiedlichen Statusachsen. Exakte rationale Werte bleiben exakt serialisiert.

### R8c: Redaktion und Reichweite

- Abschlusssumme der Roadmap auf 41 Prüfungen vereinheitlichen, wo noch 40 steht.
- Veraltete H0-Formulierungen wie „vor dem ersten Code“ als historischen Abschnitt markieren.
- CLI-Reichweite „K1–K6 und K8“ nennen. K7 ist optional; seine fehlende Implementierung ist kein Pflichtverstoß.
- H6b ist ein synthetisches numerisches Entartungsbeispiel. Die aktuelle Prüfung setzt nach dem Fit die Familienmenge direkt; das ist noch kein durchgehender epistemischer Adapterbericht. Entweder diese engere Reichweite klar benennen oder den Bericht ergänzen.
- H6c weiterhin sichtbar zurückgestellt lassen.

## 4. Empfohlene Korrekturreihenfolge und Abnahme

1. R2/R3: Zeugenrepräsentation und gemeinsame Validierung der Prädikate sichern.
2. R1/R6/R7: Löschsuche, eindeutige IDs und Budgets konsistent machen.
3. R4/R5: Status-, Quantoren- und Scope-Verträge festlegen und durch alle Berichte tragen.
4. R8: Minimum-Modus, Berichtsexporte und ehrliche Abschlussbilanz ergänzen.

Die vorhandenen grünen Tests erhalten, aber die zwei beschriebenen problematischen Statusannahmen in den Tests fachlich korrigieren. Neue Tests sollen den öffentlichen Vertrag und unabhängig bekannte Ergebnisse prüfen. Anschließend die volle bestehende Suite und die Linkprüfungen ausführen; Skips separat zählen.

Eine erfolgreiche Abnahme bedeutet hier: kein falsches Zertifikat aus unvollständiger Suche, ungültiger Auswertung oder verlorener Scope-Information; die ursprünglichen Kontrollwerte bleiben erhalten; dokumentierte Rückstellungen bleiben sichtbar. Weitere Domänen oder ein Theorem-Prover sind für diese Reparatur nicht erforderlich.

## 5. Reproduktion und Belege

Das begleitende ZIP enthält `reproduce_h_review.py`, die beobachteten Ergebnisse in `findings.json`, Quellhash-Nachweise, CI-Metadaten, die H-Verifikationsresultate, CLI-Ausgabe und das lokale Suite-Protokoll. Es enthält keine SPARC-Rohdaten und keinen vollständigen Repository-Checkout.

Ausführung mit den Repository-Abhängigkeiten:

```bash
python reproduce_h_review.py /pfad/zum/scoped-correspondence-formalism > findings_local.json
```

Referenzstand ist ausschließlich der oben genannte Commit. Das Skript importiert Produktionsfunktionen und verändert deren Dateien nicht. Ein Exitcode 0 bedeutet, dass die Reproduktion durchlief. `defect_reproduced=true` bedeutet, dass das beobachtete problematische Verhalten noch vorhanden ist; es ist kein bestandener Korrektheitstest. Der Fall zur unendlichen Zielgröße dokumentiert eine zu klärende Semantik, kein allgemeines mathematisches Verbot erweiterter reeller Werte.

Die Schlüssel im Skript entstanden vor der endgültigen Priorisierung. Zuordnung: `R1_*` → Review R1; `R2_*` → R2; `R3_*` und `R7_regret_overflow` → R3; `R5_*` → R4; `R4_*` → R5; `R6_duplicate_*` → R6; übrige `R6_*` → R7. R8 ist durch Plan-/Code-Abgleich belegt.

Die Gegenfälle sind als Ausgangspunkt für unabhängige Regressionstests gedacht. Die im Bericht erläuterte Quantorenwahl und die Policy für erweiterte reelle Zielwerte müssen zuerst entschieden werden, damit Tests anschließend den tatsächlich gewollten Vertrag absichern.
