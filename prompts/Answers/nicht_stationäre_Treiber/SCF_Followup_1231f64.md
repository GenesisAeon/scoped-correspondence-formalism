# Nachprüfung zu 1231f64

23. September 2026 · `GenesisAeon/scoped-correspondence-formalism` · Commit `1231f64530110e9ca8e9fceea55d180c9a61ce39` · Vergleich mit `3e8dce3`.

**Die beiden neuen Commits schließen die zwei Informationslecks und präzisieren B8 überzeugend. Die neue Kartierung ist ein sinnvoller Ausbau. Zwei frühere Punkte bleiben teilweise offen; hinzu kommt ein reproduzierbarer numerischer Grenzfall.**

Ich habe die geänderten Implementierungen, Verifikationen und Erläuterungen gelesen, 162 Quell-, Daten- und Prüfdateien gegen die Git-Blob-SHAs des aktuellen Commits geprüft und alle 67 lokal ausführbaren mathematischen Verifikationsskripte ausgeführt: **67 bestanden, 0 fehlgeschlagen**. Die zwei Dokumentationsprüfungen wurden wegen der schon zuvor lokal fehlenden binären DOCX-Datei weiterhin ausgelassen. Die Aussage ist deshalb keine eigene Bestätigung von 69 ausgeführten Skripten. Keine Änderungen am GitHub-Repository.

**Status der fünf vorherigen Befunde**

| Befund | Nachprüfung | Status |
|---|---|---|
| Zukunftsinformation in Intervallen | Die Bedingung `origin + step * step_size <= current_origin` ist umgesetzt. Auch ein Mehrschritt-Gegenbeispiel besteht. Zu kurze Vorgeschichte wird ausgewiesen. | Für die aktuelle Annahme sofort verfügbarer Beobachtungen repariert. |
| COVID-Zielwert im eigenen Mittelwert | Es werden sieben vorherige Kalendertage verwendet. +700 Fälle am 12.03.2020 ändern dessen Prognosemittelwert nicht mehr. | Repariert. |
| B8: konstantes R als Stationarität missverstanden | Kernmasse, Stationaritätsbedingung und deterministische/stochastische Objekte werden getrennt; R=0,8 und R=1,68 sind richtig eingeordnet. | Wesentlicher Befund behoben. |
| Offenes Profil als unbeschränkt interpretiert | Die Klimadokumentation wurde korrigiert. Die generische API liefert weiterhin `unbounded=True` am Scanrand. | Text repariert, maschinenlesbare Semantik offen. |
| Klimareferenzen vermischt | Beide Referenzvarianten und die umkehrende Rangfolge werden jetzt ausdrücklich ausgewiesen; die physikalische Einschränkung steht im Text. | Transparente Sensitivitätsanalyse, physikalische Referenz-/Initialisierungsfrage offen. |

Die entscheidende Verbesserung ist, dass die früheren Resultate nach der Korrektur tatsächlich neu berechnet wurden und ungünstige Ergebnisse sichtbar bleiben.

**Was die korrigierte Unsicherheitsauswertung jetzt zeigt**

| Modell | Nominelle Abdeckung | Beobachtete Abdeckung | Bewertete / ausgelassene Fälle | Mittlerer Intervallscore, kleiner besser |
|---|---:|---:|---:|---:|
| Energiebilanz mechanistisch | 80 % | 52,5 % (21/40) | 40 / 15 | 0,5191 |
| EBM-Vergleich: Persistenz | 80 % | 67,5 % (27/40) | 40 / 15 | 0,4167 |
| COVID Renewal, konstantes R | 80 % | 26,3 % (5/19) | 19 / 23 | 6048,43 |
| COVID exponentielle Extrapolation | 80 % | 57,9 % (11/19) | 19 / 23 | 7246,40 |
| COVID Persistenz | 80 % | 5,3 % (1/19) | 19 / 23 | 46004,70 |

Renewal hat weiterhin den besten Intervallscore unter diesen COVID-Vergleichsmodellen. Daraus folgt keine ausreichende Kalibrierung: Die nominelle 80%-Abdeckung wird klar verfehlt. Beim EBM ist Persistenz unter dem Intervallscore besser. Die Stichproben sind klein, zeitlich abhängig und teilweise überlappend; diese Zahlen sind deskriptive Befunde, keine präzisen Schätzungen einer langfristigen Deckungswahrscheinlichkeit. Scores verschiedener Domänen und Einheiten nicht direkt vergleichen.

Die vorwärtsgerichtete COVID-Beobachtungsbewertung ergibt bei 23 Kalibrier- und 29 Holdout-Tagen α=0,75035, mittlere negative Log-Likelihood 1692,764 für Poisson und 9,953 für NB. Das belegt den besseren NB-Score **bei diesem vorgegebenen Mittelwert**. Ein positiver gefitteter Dispersionsparameter ist noch kein Signifikanztest; die Formulierung „positive and significant“ in `docs/covid_observation_model.md` ist ohne passende Inferenz zu stark. Auch Mittelwertfehler und Trendverzögerung können den Vorteil der breiteren Verteilung erklären. Die bereits dokumentierte Trennung epidemiologischer und meldetechnischer Streuung ist sinnvoll, sollte um diese Mittelwertfrage ergänzt werden.

**Neuer reproduzierbarer Befund: Zeitrasterfehler fehlt in der Grenzklassifikation**

Fundstellen:

- [`rate_dependent_buffer.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/1231f64530110e9ca8e9fceea55d180c9a61ce39/src/scoped_correspondence/viability/rate_dependent_buffer.py), Zeilen 145–160: Minimum aus 4001 Rasterpunkten.
- [`multidim_tipping_maps.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/1231f64530110e9ca8e9fceea55d180c9a61ce39/src/scoped_correspondence/viability/multidim_tipping_maps.py), Zeilen 149–155: Unsicherheitsband nur aus grober/feiner ODE-Lösung.

Beide ODE-Lösungen werden auf demselben Zeitraster ausgewertet. Sie können hervorragend übereinstimmen und beide das Minimum zwischen zwei Rasterpunkten verfehlen. Der neue Unsicherheitsstatus berücksichtigt diesen zweiten Fehler nicht.

Für r=τ=Spitzenhöhe=1 und z_eq=U=W₀=0 besitzt das lineare Modell mit Startwert z(t₀)=0 die unabhängig auswertbare Faltung

\[
z(t)=-\int_{t_0}^{t}e^{-(t-s)}e^{-s^2}\,ds
=-\frac{\sqrt\pi}{2}e^{1/4-t}\left[\operatorname{erf}(t-1/2)-\operatorname{erf}(t_0-1/2)\right].
\]

Die Gegenprobe verwendet diese Formel und eine kontinuierliche Minimierung, ohne den Repository-ODE-Löser zu verwenden:

| Größe | Wert |
|---|---:|
| Repository-Rasterminimum | −0,694752852300 |
| Kontinuierliches Minimum | −0,694753281070 |
| Fehler durch Rasterabtastung | 4,2877 × 10⁻⁷ |
| Grob-/Fein-Differenz der ODE-Lösungen | 3,2835 × 10⁻¹⁰ |
| Verwendetes Unsicherheitsband | 3,2835 × 10⁻⁹ |
| Prüfgrenze b | −0,694753066685 |
| Kartenurteil | `tracking` |
| Kontinuierliche Gegenrechnung | z_min < b, also Grenzverletzung |

Dies ist ein eng konstruierter Grenzfall. Er widerlegt **nicht** die deutlich getrennten bisherigen Tabellenpunkte. Er zeigt aber, dass das neue Unsicherheitsband und die Genauigkeit von `critical_b` nahe der Grenze noch nicht belastbar sind. Die Identität b*=minₜ z(t) ist mathematisch richtig; ihr numerischer Wert ist derzeit nur so genau wie die Rasterminimierung.

**Korrektur:** Extremstellen über dz/dt=0 oder lokale Minimierung der dichten ODE-Ausgabe bestimmen, einschließlich der Zeitintervallenden. Integrationsfehler und Fehler der Extremwertsuche getrennt kontrollieren. Der analytische Gaußpuls oben eignet sich als unabhängiger Regressionstest. Erwartung: Der Fall wird korrekt als Grenzverletzung oder konservativ als noch unentschieden klassifiziert, nicht als sicher. Ein reiner Vergleich zweier ODE-Toleranzen ist dabei kein rigoroses Gesamtfehlerzertifikat.

Kleine Textkorrektur im selben Modul: Der Docstring von `buffer_reserve_frontier` vertauscht „above“ und „below“ für b relativ zu z_min. Implementierung und Verifikation haben das richtige Vorzeichen: b > z_min bedeutet Verletzung; b < z_min bedeutet Sicherheit, sofern die übrigen Scope-Bedingungen gelten.

**Die beiden verbleibenden Punkte der letzten Review**

1. In [`profile_likelihood.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/1231f64530110e9ca8e9fceea55d180c9a61ce39/src/scoped_correspondence/identifiability/profile_likelihood.py), Zeilen 429–442, bleibt das Gegenbeispiel bestehen: χ²(θ)=θ², Schwelle 1, Scan [−0,5;0,5] liefert `unbounded=True`, obwohl das vollständige Intervall [−1;1] ist. Ein eigener Status wie `open_at_scan_boundary` sollte nicht zugleich eine festgestellte Unbeschränktheit behaupten.
2. [`energy_balance_full_forcing.py`](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/1231f64530110e9ca8e9fceea55d180c9a61ce39/src/scoped_correspondence/validation/energy_balance_full_forcing.py) sagt nun selbst richtig, dass beide Referenzvarianten keine vollständig konsistente Reinitialisierung darstellen. Dies als offenen Modellschritt führen. Die nächste Änderung muss Temperatur-/Forcingreferenz und Anfangszustände gemeinsam behandeln; ein zusätzlicher freier Offset allein kann die Identifizierbarkeit weiter verschlechtern und braucht eine definierte Referenzkonvention.

**Empfohlene nächste Reihenfolge**

1. Kontinuierliches Pufferminimum absichern und den analytischen Grenzfall aufnehmen.
2. Profilstatus in der API korrigieren; veraltete Einleitungen zu Leave-one-out, Fallzahlen und COVID-Referenzmittelwert bereinigen. Beim Intervallmodul passen einige Kopftexte noch zum früheren Verfahren.
3. Unterabdeckung als aktuelles Hauptergebnis der Unsicherheitsmodelle behandeln. Mehr vorab festgelegte Prognoseursprünge und Zeitfenster sammeln; Kalibrierung pro Horizont und Regime untersuchen, ohne anhand des Testfensters nachzubessern. Mess- und Meldeverfügbarkeit gegebenenfalls als eigene Zeitstempel führen.
4. Klimareferenzmodell separat präzisieren und erst danach physikalische Modellvergleiche interpretieren.
5. Anschließend zeitabhängige Wirkungskerne und adaptive Grenzverfeinerung ausbauen. Bei der kubischen Karte Startzeit und Endhorizont getrennt variieren: `margin` verändert derzeit beides. Eine reine Endhorizontprüfung sollte dieselbe Anfangsbedingung zur selben Startzeit behalten.

Der Ausbau von Paket 6 ist wissenschaftlich besonders nützlich, wenn die Karte neben dem Ergebnis auch zeigt, **wo die numerische Aussage sicher, unsicher oder vom gewählten Beobachtungshorizont abhängig ist**. Dafür existiert jetzt eine gute Grundstruktur.

**Reproduktion:** Das Begleitarchiv enthält die unabhängigen Gegenproben, ihre JSON-Ergebnisse, 67 Ausführungslogs und das SHA-Verzeichnis. Einen eigenen Checkout des oben genannten Commits unter `repo/` neben die Prüfskripte legen. Mit Python und den Projektabhängigkeiten `python independent_probes.py` und `python run_verification.py` ausführen. Der Runner schreibt Ergebnisdateien im Checkout; deshalb eine separate Arbeitskopie verwenden. Dokumentiert sind Python 3.12.14, NumPy 2.3.5 und SciPy 1.17.0. Keine Repositoryquellen oder Rohdaten sind im Archiv dupliziert.
