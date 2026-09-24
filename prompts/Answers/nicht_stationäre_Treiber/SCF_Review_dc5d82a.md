# SCF: Review der sechs Ausbaupakete

Geprüft am 24. September 2026. Commit: **dc5d82a868fa04af2f0b1bc1d2f8486ed8fcec34**, sechs Commits nach **0d43898**. Repository: GenesisAeon/scoped-correspondence-formalism.

**Urteil:** Alle sechs Pakete sind vorhanden und die zurückgestellten Teile sind ausdrücklich dokumentiert. Eine vollständige Abnahme ist noch nicht gerechtfertigt. Es gibt vier technische beziehungsweise semantische Befunde mit unmittelbarem Korrekturbedarf sowie zwei Korrekturen der wissenschaftlichen Interpretation.

**Was unabhängig geprüft wurde**

- Commitfolge, aktueller Baum, 27 geänderte oder neue relevante Dateien und der GitHub-Actions-Lauf zum geprüften Commit.
- 172 lokale Quell-, Daten- und Verifikationsdateien stimmen per Git-Blob-SHA mit diesem Commit überein.
- Die fünf neuen Verifikationsskripte wurden lokal ausgeführt: **23/23 Einzelprüfungen bestanden** unter Python 3.12.14, NumPy 2.3.5 und SciPy 1.17.0.
- Der CI-Ausfall des Gedächtnismoduls wurde unter **NumPy 2.4.6** unabhängig reproduziert: **2/4 Prüfungen bestanden**.
- Zwei minimale Kompatibilitätskorrekturen wurden ausschließlich im Prüfprozess ausprobiert. Danach bestanden unter NumPy 2.4.6 **4/4 Prüfungen** des Gedächtnismoduls. Keine Repository-Datei wurde dafür geändert.
- Eigene Gegenbeispiele prüfen Informationsverfügbarkeit, globale Extrema, endliche Zeithorizonte, Kontrollbarrieren und die beanspruchte Kalibrierungsgarantie.
- Ein zusätzlicher COVID-Vergleich trennt Wochentagskorrektur und Negativ-Binomial-Verteilung bei denselben 42 Prognosefällen und derselben vorgelagerten Kalibrierungsperiode.

Es wurde **keine neue vollständige lokale Ausführung aller 74 Skripte** behauptet. Für den Gesamtstand wurden die tatsächlichen CI-Ergebnisse gelesen.

| Paket | Review-Ergebnis |
|---|---|
| 0 — Konsolidierung | Struktur, Testaufruf und CI vorhanden; aktueller CI-Lauf scheitert am neuen Gedächtnismodul. |
| 1 — Adaptive Kalibrierung | Referenzbeispiel reproduzierbar; bei überlappenden Horizonten fließen zukünftige Treffer-/Fehlerinformationen in den Anpassungszustand. Die gekappte Variante besitzt die zitierte universelle Abdeckungsgarantie nicht. |
| 2 — Beobachtungsmodell | Berichtete Zahlen reproduziert. Eine Ablation zeigt: NB ohne Wochentagseffekt ist auf diesem Ausschnitt besser als die kombinierte Variante. |
| 3 — Gedächtnisreduktion | Herleitung des linearen Kerns stimmt; zwei NumPy-Inkompatibilitäten sowie eine unzuverlässige globale Minimumsuche. |
| 4 — Transiente Verstärkung | Kanonisches Beispiel stimmt; die allgemeinere 2×2-API kann Grenzverletzungen fälschlich als sicher klassifizieren. |
| 5 — Begrenzte Eingriffe | Momentane QP-Bedingungen sind nachvollziehbar; die Ausgaben unterscheiden momentane CBF-Zulässigkeit noch nicht ausreichend von Sicherheit einer Trajektorie. |

**R1 — P1: Der aktuelle CI-Lauf ist rot; zwei konkrete NumPy-Inkompatibilitäten**

[GitHub-Actions-Lauf 35975893395](https://github.com/GenesisAeon/scoped-correspondence-formalism/actions/runs/35975893395):

- Mathematik: **57/58** Skripte erfolgreich.
- Daten: Job erfolgreich.
- Interne Links: Job erfolgreich.
- Fehlgeschlagen: `verify_linear_memory_projection.py`, dort **2/4** Prüfungen.

Die CI installiert NumPy 2.4.6. In `closure/linear_memory_projection.py` sind zwei Aufrufe inkompatibel:

1. Zeile 125: `float(B_row @ z)` erhält ein eindimensionales Array der Länge eins. NumPy 2.4 erlaubt diese implizite Skalarumwandlung nicht mehr. Tatsächlich reproduzierter Fehler: `TypeError: only 0-dimensional arrays can be converted to Python scalars`.
2. Zeile 184: `np.trapz(...)` wurde entfernt. Ein separater Aufruf der endlichen Gedächtnisapproximation reproduziert `AttributeError: module 'numpy' has no attribute 'trapz'`.

Minimaler, bereits im Prüfprozess erfolgreicher Vorschlag:

~~~python
from scipy.integrate import solve_ivp, trapezoid

dx = float(A) * x + float((B_row @ z).item()) + float(forcing(t))
mem = float(trapezoid(ker_vals * hist_x, dx=dt))
~~~

SciPys `trapezoid` vermeidet dabei, durch einen Wechsel zu `np.trapezoid` unbeabsichtigt NumPy ≥ 2.0 vorauszusetzen, während bisher NumPy ≥ 1.24 als Verifikationsabhängigkeit angegeben ist.

**Abnahme:** Gedächtnissuite in einer frischen CI-Installation grün; unterstützte Abhängigkeiten dokumentieren. Der Testläufer sollte bei Fehlern mehr als die letzten drei Ausgabezeilen ausgeben, damit die eigentliche Ausnahme im CI-Log sichtbar ist.

**R2 — P1: Zukunftsinformation gelangt über den Anpassungszustand in ACI und P+I**

Datei: `validation/adaptive_interval_calibration.py`, insbesondere Zeilen 232–265.

Die Residuenliste wird korrekt nach `target_time <= current_origin` gefiltert. Anschließend wird jedoch sofort mit dem Zielwert der gerade erstellten Prognose deren Trefferindikator berechnet und in `alpha_t` beziehungsweise `recent_errs` übernommen. Beim nächsten Ursprung kann dieser Zielzeitpunkt noch in der Zukunft liegen.

Unabhängiges Gegenbeispiel: tägliche Ursprünge, Horizont drei Tage. Nur die Beobachtung am Zielzeitpunkt 8 wird von 1 auf 100 geändert. Die am Ursprung 6 verfügbare Vergangenheit bleibt identisch.

| Verfahren | Intervallobergrenze am Ursprung 6 bei Zielwert 1 | Bei Zielwert 100 |
|---|---:|---:|
| Feste Referenz | 2,40 | 2,40 |
| ACI | **2,34** | **2,64** |
| P+I | **2,31** | **2,76** |

Ein noch nicht bekannter Wert darf diese früheren Intervalle nicht verändern. Der vorhandene Präfix-Test entdeckt das nicht: Der unerlaubt verwendete zukünftige Zielwert steht bereits in der Prognosezeile innerhalb beider verglichenen Präfixe.

Die Konstellation ist nicht nur hypothetisch: COVID-Ursprünge liegen fünf Tage auseinander, während bis zu sieben Tage vorausgesagt werden.

**Korrektur:** Ausgegebene Prognoseintervalle und ausstehendes Feedback getrennt speichern. Erst beim Erreichen der tatsächlichen Ziel-/Verfügbarkeitszeit den Trefferindikator bestimmen und genau einmal in `alpha_t` und `recent_errs` einarbeiten. Beobachtungen zur späteren Bewertung dürfen vorher nicht den Reglerzustand beeinflussen.

**Abnahme:** Mehrschritt-Prognosen mit überlappenden Horizonten; alle noch nicht verfügbaren Zielwerte verändern, ohne dass sich aktuelle Intervalle ändern. Auch verspätet eintreffendes Feedback prüfen. Danach betroffene Realwelt-Ergebnisse neu erzeugen.

**R3 — P1: Lokale Optimierung wird als globaler Sicherheitsnachweis verwendet**

Betroffene Stellen:

- `viability/transient_amplification.py`, Zeilen 157–164;
- `closure/linear_memory_projection.py`, Zeilen 192–195;
- entsprechend auch globale Aussagen über Maxima in `max_finite_time_gain`.

`minimize_scalar(method="bounded")` ist ein lokales Optimierungsverfahren. Ein kontinuierlicher Aufruf allein gewährleistet nicht, dass das größte oder kleinste Extremum eines oszillierenden Verlaufs gefunden wird. Randpunkte werden zudem nicht ausdrücklich als Kandidaten verglichen.

Reproduzierbares Beispiel innerhalb der erklärten 2×2-Modellklasse:

\[
A=\begin{pmatrix}-0{,}1&-10\\10&-0{,}1\end{pmatrix},
\qquad x(0)=(0,1),\qquad T=10,\qquad b=0{,}95.
\]

Hier ist \(|x_1(t)|=e^{-0{,}1t}|\sin(10t)|\). Das tatsächliche globale Maximum ist **0,9844639845** bei **t = 0,1560796660**. Die Grenze wird also überschritten.

Die API liefert dagegen:

- gefundenes Maximum: **0,5251994019** bei **t ≈ 6,43927**;
- `exceeds_boundary=False`;
- `classification="safe_no_violation"`.

Sogar die bereits berechneten Stützstellen enthalten einen Wert von **0,98286**, der der Klassifikation widerspricht.

Beim Gedächtnismodul liefert derselbe Verlauf ein Minimum von **−0,71905** statt **−0,98446**. Damit können auch dessen Vergleichsmetriken bei zulässigen oszillierenden Systemen falsch sein.

Hinzu kommt ein eigenständiges Horizontproblem: Für \(A=[[-1,10],[0,-1]]\), \(x(0)=(0,1)\), Grenze 1 und \(T=0,1\) wird ebenfalls `safe_no_violation` ausgegeben. Das Maximum im kurzen Fenster liegt bei ungefähr 0,905; bei \(t=1\) erreicht die Trajektorie aber \(10/e≈3,679\). Negative Eigenwerte beweisen langfristige Rückkehr, keine zwischenzeitliche Grenzfreiheit.

**Korrektur:** Für den verwendeten kubischen Spline sämtliche stationären Punkte über alle Teilintervalle und die Randpunkte auswerten. Das liefert ein globales Extremum dieses Interpolanten; dessen Abweichung von der eigentlichen Trajektorie muss weiterhin kontrolliert werden. Für allgemeine Zeitverläufe entweder eine geeignete analytische Extremsuche oder eine begrenzte numerische Aussage mit Fehlerkontrolle verwenden.

**Abnahme:** Oszillierende Systeme, Endpunktmaxima und -minima, mehrere lokale Extrema und verkürzte Horizonte. Klassifikation ausdrücklich als `no_violation_in_horizon` ausweisen, sofern keine globale Schranke vorliegt. Den früher korrigierten Pufferminimum-Code muss man dafür nicht zurücknehmen; dieser Befund betrifft die neu hinzugekommenen Routinen.

**R4 — P1: Momentane CBF-Erfüllung ist noch keine Sicherheit einer Trajektorie**

Datei: `viability/coupled_buffer_cbf_qp.py`, insbesondere Zeilen 115–121 und 190–194.

Der Code prüft die momentane Bedingung \(-d_i+u_i+x_i≥0\) und bezeichnet deren Erfüllung als `safe`. Es gibt keine zeitliche Simulation, keinen festgelegten Sicherheitshorizont und keinen Nachweis, dass die QP-Bedingungen entlang eines geschlossenen Regelkreises weiter erfüllbar bleiben.

Bereits das eigene Beispiel zeigt den Unterschied:

- \(x(0)=(1,5)\), Verbrauch \(d=(3,2)\), Gesamtbudget 3;
- momentanes QP-Optimum \(u=(2,0)\), Kosten 4, `safe=True\);
- bei Festhalten dieses Eingriffs gilt \(x_1(t)=1-t\); ab \(t>1\) ist Puffer 1 negativ.

Auch laufendes Nachregeln kann dauerhafte Sicherheit hier grundsätzlich nicht ermöglichen:

\[
\dot x_1+\dot x_2=-5+u_1+u_2\le-2,
\qquad x_1(t)+x_2(t)\le6-2t.
\]

Für \(t>3\) ist damit mindestens ein Puffer negativ, unabhängig davon, wie das zulässige Budget aufgeteilt wird.

Der Kostenvergleich **13 versus 4** ist ein Vergleich momentaner quadratischer Stellkosten. Zudem verletzt die feste Referenz \(u=(3,2)\) das Budget. Daraus folgt noch keine dreifache Kostenersparnis zweier zulässiger, über denselben Zeitraum sicherer Strategien.

**Korrektur:** Momentane CBF-Zulässigkeit, tatsächliche Zustandssicherheit und Sicherheit über einen Horizont als getrennte Felder ausgeben. Beispielsweise `cbf_condition_satisfied_now`, `state_in_safe_set` und ein separat berechnetes Ergebnis eines Regelverlaufs. Die analytischen beiden QP-Unzulässigkeitsgründe sind weiterhin nützlich, beziehen sich aber zunächst auf diese momentane Optimierungsaufgabe.

**Abnahme:** Geschlossene Regelkreise mit ausdrücklich festgelegtem Horizont und Abbruch bei Unzulässigkeit; Grenzereignisse und integrierte Kosten ausgeben. Strategien bei gleichen zulässigen Ressourcen und gleicher Sicherheitsanforderung vergleichen. Soll dauerhafte Sicherheit demonstriert werden, muss das Beispiel dafür überhaupt genügend langfristige Ressourcen besitzen.

**R5 — P2: Die gekappte ACI-Variante erbt die zitierte Garantie nicht automatisch**

Die Implementierung begrenzt \(\alpha_t\) auf \([0,001;0,999]\) und verwendet stets ein endliches empirisches Quantil vergangener Fehler. Die Dokumentation verweist dennoch auf langfristige Abdeckung unter beliebigen Verteilungsänderungen.

Ein direktes Gegenbeispiel sind strikt wachsende Fehlerbeträge \(e_t=t+1\) bei Prognosemittelwert null. Jede zukünftige Beobachtung ist größer als sämtliche vergangenen Fehler und damit auch größer als jedes daraus berechnete Quantil. Die Intervalle verfehlen deshalb dauerhaft jeden Zielwert.

Reproduziert: **0 % Abdeckung bei 197 bewerteten Prognosen**, obwohl 80 % angestrebt werden; \(\alpha_t\) bleibt schließlich bei 0,001. Das Argument gilt über beliebig lange Fortsetzung der Sequenz.

**Korrektur:** Entweder die für einen passenden Satz tatsächlich erforderliche Update- und Randfallsemantik implementieren und die Voraussetzungen nachweisen oder die vorhandene Methode ausdrücklich als begrenzte, ACI-inspirierte Heuristik beschreiben. Die bereits dokumentierte Einschränkung des P+I-Verfahrens sollte entsprechend auch für die modifizierte ACI gelten. Eine kurze empirische Abdeckung nahe 80 % ist zudem allein kein Nachweis langfristiger Kalibrierung.

**R6 — P2: COVID-Gewinn bestätigt; Wochentagsbeitrag und frühere Unterdeckung werden zu stark interpretiert**

Die berichteten **2,4 % → 73,8 %** und **1387,5 → 11,75** sind reproduzierbar. Die vor Beginn der Bewertungsperiode erfolgende Anpassung der Zusatzparameter ist grundsätzlich sauber.

Eine zusätzliche 2×2-Ablation auf denselben 42 Fällen liefert:

| Wochentagskorrektur | Verteilung | Abdeckung | Mittlerer negativer Log-Score ↓ | Mittlerer Intervallscore ↓ |
|---|---|---:|---:|---:|
| Nein | Poisson | 2,38 % | 1387,465 | 39051,57 |
| Ja | Poisson | 0,00 % | 2490,044 | 40706,45 |
| **Nein** | **Negativ-Binomial** | **73,81 %** | **10,192** | **15381,98** |
| Ja | Negativ-Binomial | 73,81 % | 11,751 | 23231,21 |

Die NB-Dispersion wird für jede der beiden Mittelwertvarianten ausschließlich aus denselben 18 Kalibrierungstagen vor dem ersten Ursprung geschätzt. Ohne Wochentagskorrektur ist sie ungefähr 0,82065, mit Korrektur ungefähr 0,91181.

In diesem Ausschnitt verbessert **Überdispersion** die Vorhersageverteilung deutlich; der geschätzte Wochentagseffekt verschlechtert beide Scores und erhöht die Abdeckung nicht. Die NB-Intervalle ohne Wochentagseffekt sind im Mittel sogar etwas schmaler: ungefähr **12997** gegenüber **13458** Fällen.

Zwei Aussagegrenzen sind erforderlich:

1. Die frühere **26,3-%-Abdeckung** bewertete geglättete Inzidenz mit anderen Intervallen und 19 bewerteten Prognosefällen. Die neuen **73,8 %** beziehen sich auf rohe Tageszahlen und 42 Fälle. Der neue Vergleich erklärt daher nicht rückwirkend den Mechanismus der früheren Unterdeckung.
2. Dass die Dynamik im Vergleich konstant gehalten wurde, isoliert den Effekt einer Änderung der Vorhersageverteilung. Es beweist nicht, dass die ursprüngliche Systemdynamik richtig oder der Datenfehler kausal ein Meldeproblem war. Eine breite NB-Verteilung kann auch andere Modellfehler teilweise auffangen.

**Korrektur:** Die vier Varianten als Standardablation aufnehmen; den NB-Ansatz ohne Wochentagskorrektur als starke Referenz behalten. Die beobachtete Verbesserung genau auf diesen Test und diese Zielgröße begrenzen. Neue Zeitfenster und Länder erst anschließend als eigenständige, vorab festgelegte Prüfung nutzen.

**Was bestehen bleibt und wie ich weitergehen würde**

Die sechs Pakete enthalten echte neue Fähigkeiten. Besonders wertvoll sind die explizite Trennung der QP-Unzulässigkeitsgründe, die korrekte lineare Gedächtnisherleitung, die klar dokumentierten Auslassungen und der messbare Nutzen einer angemesseneren Zähldatenverteilung. Die kanonische transiente Verstärkung und das synthetische adaptive Beispiel funktionieren.

Ich empfehle einen begrenzten Korrekturdurchgang:

1. R1 beheben und den CI-Fehler sichtbar diagnostizierbar machen.
2. R2 und R3 mit den Gegenbeispielen als Regressionstests korrigieren.
3. R4: Sicherheitssemantik präzisieren und einen vollständigen Regelverlauf ergänzen.
4. R5 und R6: Garantieaussagen, Ablation und Ergebnisinterpretation korrigieren.
5. Danach die betroffenen Ergebnisse neu erzeugen und den Roadmap-Abschluss erneut beurteilen.

Die transparent zurückgestellten größeren Erweiterungen müssen dafür nicht vorgezogen werden.

**Quellen und Fundstellen**

Alle Repository-Links sind auf den geprüften Commit festgelegt:

- [Änderungsvergleich der sechs Commits](https://github.com/GenesisAeon/scoped-correspondence-formalism/compare/0d4389804adf8d026923d2d9c08db5e3e902769a...dc5d82a868fa04af2f0b1bc1d2f8486ed8fcec34)
- [Adaptive Kalibrierung](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/dc5d82a868fa04af2f0b1bc1d2f8486ed8fcec34/src/scoped_correspondence/validation/adaptive_interval_calibration.py)
- [Gedächtnisprojektion](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/dc5d82a868fa04af2f0b1bc1d2f8486ed8fcec34/src/scoped_correspondence/closure/linear_memory_projection.py)
- [Transiente Verstärkung](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/dc5d82a868fa04af2f0b1bc1d2f8486ed8fcec34/src/scoped_correspondence/viability/transient_amplification.py)
- [CBF-QP](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/dc5d82a868fa04af2f0b1bc1d2f8486ed8fcec34/src/scoped_correspondence/viability/coupled_buffer_cbf_qp.py)
- [COVID-Auswertung](https://github.com/GenesisAeon/scoped-correspondence-formalism/blob/dc5d82a868fa04af2f0b1bc1d2f8486ed8fcec34/docs/covid_latent_renewal_observation.md)
- [NumPy 2.4: abgelaufene Deprecations](https://numpy.org/doc/2.4/release/2.4.0-notes.html)
- [SciPy: minimize_scalar ist lokale Optimierung](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize_scalar.html)
