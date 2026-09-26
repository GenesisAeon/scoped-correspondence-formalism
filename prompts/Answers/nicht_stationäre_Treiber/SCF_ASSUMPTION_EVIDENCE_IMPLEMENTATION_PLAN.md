# SCF: Annahmen, Gegenmodelle und Entscheidungen unter begrenzter Beobachtung

**Implementierungsplan für Claude-Code · H0–H7 · 26. September 2026**

Repository: [GenesisAeon/scoped-correspondence-formalism](https://github.com/GenesisAeon/scoped-correspondence-formalism)

Geprüfter Ausgangsstand: [`84848a464bfba6a6d1160de303b2eacc429114eb`](https://github.com/GenesisAeon/scoped-correspondence-formalism/tree/84848a464bfba6a6d1160de303b2eacc429114eb).

Status dieses Dokuments: recherchierter Entwurf mit unabhängig ausgeführten Kontrollrechnungen. **Keine Implementierung der neuen Produktivmodule, keine Änderung oder Veröffentlichung im Repository.** Die Namen H0–H7 sind Vorschläge; bei inzwischen belegten Namen anpassen.

## 1. Entscheidung und wissenschaftlicher Nutzen

Die Erweiterung passt zu SCF. Ihr Gegenstand ist die **Prüfbarkeit einer Aussage relativ zu Annahmen, Beobachtungen und Handlungsmöglichkeiten**.

SCF beschreibt bereits Korrespondenzen mit Geltungsbereich, Beobachtungsabbildungen, Identifizierbarkeit, kontrollierte Vergröberung und begrenzte Eingriffe. Die neue Schicht verbindet diese Fähigkeiten zu beantwortbaren Fragen:

1. Welche Annahmen tragen eine Schlussfolgerung, und sind sie im deklarierten Modellraum gemeinsam erfüllbar?
2. Gibt es konkrete Gegenmodelle oder nur eine unvollständige Suche ohne Fund?
3. Unterscheiden die vorhandenen Beobachtungen die für die Aussage relevanten Zustände?
4. Welche Handlungen bleiben über alle noch möglichen Zustände zulässig?
5. Welche zusätzliche Beobachtung würde eine Aussage oder einen Eingriff ermöglichen?

Der wissenschaftliche Mehrwert liegt in dieser Verbindung und ihren überprüfbaren Anwendungen. Die zugrunde liegenden Logik-, Identifikations- und Entscheidungsverfahren sind etablierte Mathematik; ihre Implementierung begründet keinen Anspruch auf eine neue allgemeine Erkenntnistheorie.

**Empfohlener Kern:** endliche, exakt auswertbare Modellmengen; überprüfbare Zeugen; minimale Annahmenmengen; Beobachtungsfasern; uniforme Eingriffe unter Ungewissheit. Der erste Durchlauf benötigt keine neuen Fremdbibliotheken und keine neuen realen Datensätze.

## 2. Was wir aus Pascal und Gödel übernehmen können

Der [Spektrum-Artikel](https://www.spektrum.de/kolumne/kann-mathematik-die-existenz-gottes-beweisen/2343717) ist der Gesprächsanlass. Für die Implementierung sind die Primärquellen in Abschnitt 15 maßgeblich.

Pascal-artige Wetten betreffen Entscheidungen bei vorgegebenen Wahrscheinlichkeiten und Nutzenwerten. Gödel/Scott-artige Argumente betreffen logische Folgerungen aus formalisierten Axiomen. Das sind unterschiedliche Aufgaben. Ein günstiger erwarteter Nutzen macht die zugrunde gelegte Existenzbehauptung nicht wahrscheinlicher, solange keine zusätzliche Evidenz vorliegt.

Eine besonders konkrete Anschlussstelle ist bereits vorhanden: Scott's Fassung ist im **Archive of Formal Proofs** in Isabelle/HOL formalisiert, einschließlich expliziter modallogischer Semantik [S1]. Eine andere Arbeit rekonstruiert die Inkonsistenz der ursprünglichen Gödel-Fassung; beide Fassungen dürfen nicht gleichgesetzt werden [S2].

Für SCF ergibt sich daraus eine methodische Trennung:

| Frage | Passende Evidenz | Was daraus allein nicht folgt |
|---|---|---|
| Folgt C aus A? | Ableitung oder vollständige Auswertung des deklarierten endlichen Modellraums | A gilt in einem realen System |
| Ist A erfüllbar? | Ein nachprüfbares Modell | Dieses Modell ist physikalisch realisiert |
| Lässt sich C aus y bestimmen? | C ist konstant auf der Beobachtungsfaser | Der gesamte Zustand ist rekonstruierbar |
| Ist eine Handlung robust zulässig? | Ein gemeinsamer Eingriff für alle kompatiblen Zustände | Ein einzelner geschätzter Zustand sei wahr |
| Hat sich das Modell empirisch bewährt? | Geeignete Daten, Messmodell, Auswertungsprotokoll und Baselines | Universelle Gültigkeit außerhalb dieses Versuchs |

Ein kurzer dokumentarischer Exkurs zu Pascal/Gödel ist sinnvoll. Eine eigene Gottesbeweis-Engine, eine Wahrscheinlichkeit für Gott oder eine metaphysische SCF-Ableitung gehören nicht in dieses Paket. Die vorhandene AFP-Formalisation wird referenziert; sie muss nicht in Python nachgebaut werden.

## 3. Anschluss an den tatsächlich vorhandenen Code

Die folgenden Pfade und Funktionen wurden am oben genannten Commit geprüft.

| Vorhandener Baustein | Bereits vorhanden | Ergänzung |
|---|---|---|
| `FORMALISM.md`, insbesondere §7–9 | Evidenzstatus, Beobachtungsgrenzen, Schließungsbedingungen | Regeln maschinenlesbar berichten und an Beispielen durchsetzen |
| `correspondence/contract.py`: `Scope`, `CorrespondenceReport`, `verify_conjugacy` | Textuelle Annahmen, Zustands-/Zeitscope, numerische Residuen; leere Stichprobe wird bereits zurückgewiesen | Additiver Bericht über Art und Reichweite der Evidenz |
| `correspondence/controlled_markov.py`: `partition_indicator`, `check_controlled_correspondence`, `is_union_of_classes` | Aktionsweise Lumpability und Prüfung, ob ein Ereignis aus Makroklassen besteht | Verbindung zwischen erhaltener Dynamik und beobachtbaren Aussagen |
| `identifiability/core.py` | Produkt-Invarianzen, Rangkontrollen, konkrete ununterscheidbare Zustände | Mengenwertige Aussage-/Zielgrößenberichte über endliche Fasern |
| `viability/coupled_buffer_cbf_qp.py`: `BufferSpec`, `sustained_safety_over_horizon` | Sicherheit bei gehaltenem Eingriff, Grenzen und gemeinsames Budget | Eingriff muss für eine ganze Beobachtungsfaser funktionieren |
| `validation/sequential_information_pilot.py`: `bellman_value` | Sequentielle Beobachtungsentscheidung mit spezifizierten Wahrscheinlichkeiten | Ergänzender Fall mit deklarierter Zustandsmenge ohne priorisierte Wahrscheinlichkeiten |
| `validation/core.py`: `DatasetManifest`, `ValidationReport` | Datenprovenienz und Pilotberichte | Referenzen übernehmen, keinen zweiten Provenienzstandard bauen |
| `metarules/core.py`: `MetaRuleUpdate` | Beschreibungsänderungen versus tatsächlich durchgesetzte Regeländerungen | Als Interpretationsgrenze berücksichtigen; kein allgemeiner Axiomenprüfer vorhanden |
| `verification/verify_galaxy_observation_maps.py` | Zwei Halo-Familien mit numerisch angeglichenen Beschleunigungen an zwei Radien | Optionaler Bericht über beobachtungsabhängige Unterscheidbarkeit |

Alle Codepfade dieser Tabelle sind relativ zu `src/scoped_correspondence/`, außer ausdrücklich genannten Dokumenten und Verification-Skripten.

**Wichtige Sprachkorrektur beim Adapter:** `check_controlled_correspondence` verwendet eine Toleranz; sein Feld `exact` ist ein numerischer Test dieser algebraischen Bedingung. `verify_conjugacy` prüft ausgewählte Zustands-Zeit-Paare. Keines dieser bestehenden Resultate wird durch einen neuen Wrapper zu einem allgemeinen maschinengeprüften Beweis.

### 3.1 Vorhandene Review-Abhängigkeiten

Am Ausgangsstand sind die Folgebefunde zur Galaxien-Profiloptimierung und zur Vergleichbarkeit modellabhängig gültiger Testpunkte relevant:

- Die Burkert-Profilkurve verwendet eine einzelne beschränkte skalare Optimierung; konkurrierende Minima und Endpunkte können fehlen. Ein gültiger Gegenkandidat bei NGC3917 senkt an einem geprüften Profilpunkt den Zielfunktionswert von etwa 1253,496 auf 459,788.
- Modellgüten können auf verschiedenen Teilmengen gültiger Beobachtungen beruhen. Solche Werte sind ohne gemeinsame Auswertungsregel nicht direkt vergleichbar.

H0 prüft, ob diese Befunde inzwischen behoben sind. **Sie blockieren nur die entsprechende reale Galaxien-Anbindung**, nicht den endlichen Kern oder den Pufferpiloten. Der neue Plan soll nicht heimlich den gesamten letzten Review-Zyklus erneut eröffnen. Yoons noch fehlender Volltext ist für diese Erweiterung ohne Bedeutung.

## 4. Mathematischer Kern und Ergebnissemantik

### 4.1 Endliche Modellmengen

Sei W eine explizit deklarierte, nichtleere endliche Menge von Kandidaten. Ein Kandidat kann eine Wahrheitsbelegung, einen Zustand oder eine endliche Parametrisierung darstellen. Für formal ausgewertete Annahmen A gilt

\[
S_A=\{w\in W:\ \forall a\in A,\ a(w)=\mathrm{wahr}\}.
\]

Für eine Aussage C werden positive und negative Zeugen gesucht:

\[
S_A^+=\{w\in S_A:C(w)\},\qquad S_A^-=\{w\in S_A:\neg C(w)\}.
\]

Nach vollständiger, fehlerfreier Auswertung:

| Ergebnis | Bedingung | Bericht |
|---|---|---|
| `no_admissible_model_in_scope` | S_A ist leer | Annahmen im angegebenen Scope gemeinsam nicht erfüllbar |
| `entailed_in_scope` | S_A nichtleer; S_A^- leer | C gilt für alle zulässigen Kandidaten dieses Scopes |
| `negation_entailed_in_scope` | S_A nichtleer; S_A^+ leer | Nicht-C gilt für alle zulässigen Kandidaten dieses Scopes |
| `underdetermined` | Beide Teilmengen nichtleer | Ein positiver und ein negativer Zeuge werden ausgegeben |

Für eine abgebrochene Suche gilt grundsätzlich `incomplete`. Schon gefundene gültige Zeugen bleiben aussagekräftig: Ein Gegenbeispiel widerlegt die universelle Aussage; zwei gegensätzliche Zeugen belegen Unterbestimmtheit bereits ohne Vollständigkeit. Aus einer unvollständigen Suche darf dagegen weder universelle Gültigkeit noch Nichtexistenz zulässiger Modelle abgeleitet werden. `search_complete` bleibt ein separates Feld.

**Kein Gegenmodell gefunden** und **kein Gegenmodell im vollständig durchsuchten Scope vorhanden** sind verschiedene Ergebnisse. Eine endliche Kandidatenliste ist kein Beweis über einen darunter gedachten kontinuierlichen Parameterraum. Die offizielle Alloy-Dokumentation illustriert genau diese Scope-Grenze [S3].

Leere Domäneneingabe ist ein Eingabefehler. Eine nichtleere Domäne, aus der die Annahmen alle Kandidaten ausschließen, ist ein mathematisches Ergebnis. Prädikatfehler, NaN und fehlende Angaben werden nicht in `False` oder in einen stillen Ausschluss umgewandelt.

### 4.2 Nichtleere Voraussetzungen und inhaltsleere Erfüllung

Für eine bedingte Aussage B⇒C muss zusätzlich geprüft werden, ob

\[
S_{A,B}=\{w\in S_A:B(w)\}\ne\varnothing.
\]

Falls S_A nichtleer, aber S_{A,B} leer ist, kann die Implikation formal gelten, ohne einen einzigen relevanten Fall zu betreffen. Der Bericht nennt dann `antecedent_reachable_in_scope=false` und `vacuity_kind="antecedent_never_holds"`.

Das unterscheidet sich von widersprüchlichen Annahmen. H1 behandelt diese beiden elementaren Fälle. Die umfassende temporallogische Vacuity-Analyse aus [S4, S5] wird ausdrücklich nicht behauptet.

### 4.3 Minimale Annahmenmengen und Inkonsistenzkerne

Eine Menge B⊆A ist eine **teilmengenminimale tragende Annahmenmenge**, wenn S_B nichtleer ist, C dort überall gilt und nach Entfernen jedes einzelnen Elements mindestens ein Gegenmodell existiert.

Ein **teilmengenminimaler Inkonsistenzkern** K⊆A hat S_K=∅, während jede Entfernung eines Elements wieder mindestens ein Modell zulässt.

Teilmengenminimal bedeutet nicht kleinste Kardinalität. Mehrere verschiedene Kerne und Supports sind möglich [S6]. Standardmäßig reicht ein deterministisch gefundener minimaler Support/Kern; alle Lösungen nur bei ausdrücklich kleinem Suchbudget.

Ein Löschverfahren darf für den Support nur von einer erfüllbaren, bereits tragenden Ausgangsmenge starten. Unter deren Teilmengen bleibt Erfüllbarkeit erhalten. Ein beliebiges Prädikat „erfüllbar UND impliziert C“ ist über allen Annahmenmengen nicht monoton; diesen Unterschied nicht wegabstrahieren.

Minimale Supports bezeichnen logische Abhängigkeiten relativ zu W. Sie beweisen keine kausale Notwendigkeit und keine empirische Glaubwürdigkeit. Festgehaltene Hintergrundannahmen und Domänengrenzen sind separat aufzuführen; man darf sie beim Ausgeben eines „minimalen“ Kerns nicht unsichtbar machen.

### 4.4 Beobachtungsfasern und identifizierbare Zielgrößen

Für eine deterministische exakte Beobachtung h und einen beobachteten Wert y:

\[
F_A(y)=\{w\in S_A:h(w)=y\},\qquad
Q_A(y)=\{q(w):w\in F_A(y)\}.
\]

- Eine boolesche Aussage ist bei y identifizierbar, wenn die nichtleere Faser ausschließlich denselben Wahrheitswert enthält.
- Eine numerische Zielgröße ist bei y punktidentifizierbar, wenn Q_A(y) genau einen Wert enthält.
- Mehrere mögliche Werte werden als Menge berichtet. Min/Max sind zusätzlich möglich, ersetzen eine nicht zusammenhängende Menge aber nicht.
- Eine leere Faser ist eine Unvereinbarkeit von Beobachtung und deklariertem Modellraum, keine besonders gute Identifikation.

Sind h_f und h_c durch h_c=r∘h_f verknüpft, enthält jede feine Faser nur Zustände einer gröberen Faser. Daher schrumpft die Menge möglicher Zielgrößen bei dieser Informationsverfeinerung. Das gilt bei unveränderten Annahmen und passender exakter Beobachtung; eine Änderung von Rauschmodell oder Toleranz ist keine solche Verfeinerung.

Das ist im endlichen deterministischen Fall eine exakt auswertbare Identifikationsfrage. Bei realen endlichen Stichproben müssen strukturelle Identifikation und statistische Unsicherheit getrennt bleiben [S7]. Eine Likelihood-Schwelle auf einem Gitter liefert zunächst eine **Kandidaten-Kompatibilitätsmenge** mit dokumentierter Schwelle, kein automatisch kalibriertes Konfidenzgebiet und kein vollständiges Identifikationsgebiet.

### 4.5 Aussagewissen und Handlungswissen

Für einen Zustand w sei U_safe(w) die Menge zulässiger sicherer Eingriffe. Ohne weitere Beobachtung ist über einer Faser F nötig:

\[
U_{\mathrm{uniform}}(F)=\bigcap_{w\in F}U_{\mathrm{safe}}(w).
\]

Dabei sind

\[
\forall w\in F\ \exists u:\mathrm{safe}(w,u)
\quad\text{und}\quad
\exists u\ \forall w\in F:\mathrm{safe}(w,u)
\]

verschiedene Aussagen. Der erste Ausdruck erlaubt einen zustandsabhängigen Eingriff, der zweite fordert einen gemeinsamen. Eine beobachtungsbasierte Politik π darf nur von tatsächlich verfügbaren Messwerten abhängen:

\[
\exists\pi\ \forall w:\mathrm{safe}(w,\pi(h(w))).
\]

Für endliche Ein-Schritt-Probleme ohne zusätzliche Kopplung zwischen Beobachtungsklassen existiert eine solche Politik genau dann, wenn jede erreichbare Faser einen gemeinsamen zulässigen Eingriff besitzt. Das ist kein Satz über allgemeine POMDPs, dynamische Spiele oder unendliche Horizonte.

### 4.6 Entscheidungen bei verbleibender Mehrdeutigkeit

Nach einer harten Zulässigkeitsprüfung kann eine endliche Verlusttabelle L(a,w) verglichen werden:

\[
a_{\mathrm{worst}}\in\arg\min_a\max_{w\in F}L(a,w),
\]

\[
a_{\mathrm{regret}}\in\arg\min_a\max_{w\in F}
\left[L(a,w)-\min_b L(b,w)\right].
\]

Die Menge F, die Handlungsmöglichkeiten und die Verlustwerte sind explizite Eingaben. Der Regret-Vergleich benennt insbesondere, ob b aus derselben festen Aktionsmenge stammt oder zustandsabhängige Zulässigkeit hat. Für H4 wird zunächst eine gemeinsame feste Aktionsmenge mit vollständig definierter endlicher Verlustmatrix verwendet.

Manski verbindet partielle Identifikation und Entscheidungstheorie ausdrücklich, auch in einer aktuellen Arbeit von 2026 [S7, S8]. Daraus folgt nicht, dass Minimax oder Minimax-Regret ohne Wertentscheidung universell „richtig“ wären. Beide Kriterien bleiben auswählbare Annahmen.

Wahrscheinlichkeiten werden nur verwendet, wenn eine Verteilung ausdrücklich angegeben wurde. Die Anzahl von Kandidaten in einer Liste ist kein Prior. Verlust- und Erwartungswertfunktionen akzeptieren hier nur endliche Werte; ±∞, NaN und unzulässige Wahrscheinlichkeiten ergeben einen klaren Fehler. Ein sehr großer endlicher Nutzen darf nicht als semantischer Ersatz für unendlichen Nutzen ausgegeben werden.

## 5. Unabhängig berechnete Kontrollfälle

Die acht Gruppen in `controls/verify_reference_controls.py` wurden vor Erstellung dieses Plans erfolgreich mit boolescher, ganzzahliger und rationaler Arithmetik ausgeführt. Das Skript importiert kein SCF und keinen Optimierer. Es ist eine kleine Referenzrechnung, keine vorgeschriebene Produktivarchitektur.

### K1 — Zwei verschiedene minimale Supports

W={0,1}³ für p,q,r; Ziel C=r.

\[
A_1=p,\quad A_2=(p\Rightarrow q),\quad
A_3=(q\Rightarrow r),\quad A_4=(p\Rightarrow r).
\]

Die vollständige Menge ist erfüllbar und impliziert r. Exakt zwei teilmengenminimale Supports:

- {A1,A4}, Kardinalität 2;
- {A1,A2,A3}, Kardinalität 3.

A2, A3 und A4 sind jeweils einzeln aus der vollen Menge entfernbar; sie dürfen deshalb nicht alle gleichzeitig entfernt werden. Ergänzt man A5=¬r, ergeben sich genau die minimalen Inkonsistenzkerne {A1,A4,A5} und {A1,A2,A3,A5}. Für jede Entfernung muss ein konkreter Zeuge ausgegeben und erneut geprüft werden.

### K2 — Eine wahre Implikation ohne Anwendungsfall

Bei A={¬p} sind vier der acht Belegungen zulässig. Auf allen gilt p⇒q, aber auf keiner gilt p. Ergebnis: nichtleerer Modellraum, erfüllte Implikation, nicht realisierte Voraussetzung. Davon getrennt A={p,¬p}: kein zulässiges Modell.

### K3 — Scope-Erweiterung widerlegt eine zuvor gültige Aussage

Für W={−1,0,1} gilt x²≤1 überall. Für W'={−1,0,1,2} liefert x=2 ein Gegenmodell. Damit wird ein versehentlicher Übergang von `entailed_in_scope` zu „global bewiesen“ gezielt abgefangen.

### K4 — Genug Information für Sicherheit, zu wenig für Rekonstruktion

Zustände X={0,1,2}², Beobachtung h(x)=x1+x2, Messwert y=2:

\[
F(2)=\{(0,2),(1,1),(2,0)\}.
\]

Die Aussage „beide Reserven mindestens 1“ gilt nur in (1,1). Die Summe identifiziert diese Aussage nicht. Eine zusätzliche Messung m=min(x1,x2) genügt für die Aussage, ohne bei m=0 die beiden Randzustände zu unterscheiden.

Die Zielgröße q=(x1−x2)² hat die exakte Wertemenge {0,4}; das ausgegebene Intervall [0,4] allein würde unzulässig Zwischenwerte suggerieren.

### K5 — Kontrollierbar bei bekanntem Zustand, nicht bei bekannter Summe

Für dieselbe Faser gilt während t∈[0,1]:

\[
\dot x_i=-1+u_i,\qquad 0\le u_i\le1,\qquad u_1+u_2\le B.
\]

Die Steuerung wird bei t=0 gewählt und bis t=1 gehalten. Sicherheitsgrenze hier: x_i(t)≥0. Diese Grenze ist ausdrücklich eine andere Frage als die Reserveschwelle 1 aus K4.

Wegen der affinen Trajektorie ist die notwendige und hinreichende Bedingung

\[
\min\{x_i(0),\ x_i(0)+u_i-1\}\ge0.
\]

| Anfangszustand | Kleinster ausreichender Eingriff | Minimaler Verbrauch |
|---|---|---:|
| (0,2) | (1,0) | 1 |
| (1,1) | (0,0) | 0 |
| (2,0) | (0,1) | 1 |

Bei B=1 ist jeder Zustand einzeln kontrollierbar. Ein gemeinsamer Eingriff müsste aber aus dem ersten Zustand u1≥1 und aus dem letzten u2≥1 erfüllen. Damit wäre u1+u2≥2: **unmöglich bei B=1**, möglich bei B=2.

Dieser Unmöglichkeitsbeweis gilt für alle kontinuierlichen Eingriffe in den angegebenen Grenzen, nicht nur für ein Aktionsgitter. Die Referenzrechnung prüft zusätzlich ausgewählte Aktionen.

- Die Beobachtung von min(x1,x2) löst K4, lässt aber bei m=0 die beiden entgegengesetzten Eingriffe weiterhin offen.
- Eine vor dem Eingriff verfügbare Messung des Vorzeichens von x1−x2 unterscheidet die drei Zustände dieser Faser; eine passende Politik benötigt im ungünstigsten Fall Budget 1.
- Die Mittelung (1/2,1/2) verletzt in beiden Randzuständen die Sicherheitsgrenze vor dem Horizont. Das Mitteln guter zustandsabhängiger Lösungen liefert hier keine robuste Lösung.
- Eine zufällige Auswahl zwischen (1,0) und (0,1) ist ein anderes Verfahren als deren physische Mittelung. Sie erzeugt ebenfalls keine pfadweise Sicherheitsgarantie.

Die Sicherheitswerte dieses Beispiels wurden zusätzlich mit der vorhandenen Funktion `sustained_safety_over_horizon` reproduziert. Diese verwendet eine numerische Toleranz von 1e−9; die unabhängige Herleitung oben ist exakt.

Optionaler Kostenkontrollfall: Bei linearen Ressourcenkosten und einer perfekten, verzögerungsfreien Messung mit festem Preis c≥0 beträgt der minimale Worst-Case-Aufwand ohne Messung 2, mit Messung 1+c. Die Messung verbessert dieses spezifische Kriterium für c<1. Kosten, Verzögerung und Perfektion sind Annahmen, kein behaupteter allgemeiner Wert von Information.

### K6 — Minimax und Minimax-Regret sind nicht austauschbar

| Verlust | Zustand 1 | Zustand 2 | Maximaler Verlust | Maximaler Regret |
|---|---:|---:|---:|---:|
| Aktion A | 0 | 10 | 10 | 4 |
| Aktion B | 6 | 6 | 6 | 6 |

Minimax wählt B; Minimax-Regret wählt A. Dieser Kontrollfall verhindert, dass beide APIs versehentlich dasselbe Kriterium implementieren. Bei explizitem p=P(Zustand 2) wechselt die Erwartungsverlustentscheidung an p=0,6, mit Gleichstand genau an der Grenze.

### K7 — Optionale Vertiefung: Randomisierung kann Regret reduzieren

Separater Lehrfall: Nicht-Eingreifen hat Erwartungsverlust 10p, Eingreifen Verlust 2, p∈[0,1;0,3]. Die beste deterministische Entscheidung hat maximalen Regret 1; eine mit Wahrscheinlichkeit α gewählte Intervention hat maximalen Regret max(α,1−α). Das Minimum liegt exakt bei α=1/2 und beträgt 1/2.

Das folgt durch Betrachtung der Intervallendpunkte; auf beiden Seiten von p=0,2 ist der Regret affin. Der Fall wird als optionale Referenz mitgeliefert. Eine allgemeine Optimierung randomisierter Politiken ist kein Pflichtteil von H0–H7. Er darf insbesondere nicht mit der harten Sicherheitsforderung von K5 vermischt werden [S7].

### K8 — Exakte Makrodynamik garantiert keine beobachtbare Sicherheitsfrage

Für P=I4 und Partition {{0,1},{2,3}} gilt exakt PC=CQ mit Q=I2. Das Ereignis E={1} ist dennoch keine Vereinigung von Makroklassen: Die Makrobeobachtung unterscheidet 0 und 1 nicht.

Die vorhandenen Funktionen `check_controlled_correspondence` und `is_union_of_classes` reproduzieren diesen Unterschied. Die neue Schicht soll beide Ergebnisse nebeneinander sichtbar machen: Dynamikverträglichkeit und Aussagebeobachtbarkeit sind separate Anforderungen.

## 6. Architektur und begrenzte API

Vorgeschlagener neuer Namensraum: `scoped_correspondence.epistemic`. „Epistemic“ ist hier der technische Name für die Wissens-/Annahmenprüfung, keine neue physikalische Schicht.

Kleine, getrennte Dateien:

```text
src/scoped_correspondence/epistemic/
    __init__.py
    records.py
    finite.py
    supports.py
    observation_fibers.py
    decisions.py
    adapters.py
src/scoped_correspondence/validation/
    epistemic_buffer_pilot.py
```

Diese Pfade sind Vorschläge. Vorhandene geeignete Datentypen sollen wiederverwendet werden. Die Aufteilung darf vereinfacht werden; entscheidend sind die Ergebnisverträge.

### 6.1 Datentypen

`AssumptionSpec`:

- stabile ID, verständlicher Text, Rolle: `structural`, `measurement`, `statistical`, `numerical`, `decision` oder `definition`;
- Quelle/Herleitung, gegebenenfalls registrierte Prädikat-ID;
- `justification_status`, getrennt von der Frage, ob ein endlicher Kandidat das Prädikat erfüllt;
- explizite Hintergrundannahmen, keine stillen globalen Defaults.

`FiniteDomainSpec`:

- deklarierte Kandidaten oder kartesische endliche Domänen mit eindeutigen IDs;
- Kardinalität, Darstellungsart, Scope-Text, Einheiten falls nötig;
- `coverage_of_declared_domain`: `complete` oder `partial`;
- `relationship_to_target_space`: etwa `entire_finite_space`, `restricted_candidates`, `grid_of_continuous_space`;
- Registry-/Definitionsversion und reproduzierbare Reihenfolge.

`ClaimSpec`:

- ID, formale Aufgabe, menschliche Lesart;
- Scope, verwendete Annahmen, Zielprädikat/Zielgröße;
- optional eigenes Antezedens;
- bei Entscheidungen Reihenfolge von Beobachtung und Eingriff, Horizont, Aktions- und Informationsbeschränkungen.

`ClaimReport`:

- `logical_status`, `search_complete`, `arithmetic_kind`, ausgewertete Kandidaten und Fehler;
- positiver Zeuge, Gegenmodell und Ergebnis ihres Replays;
- `evidence_kind`: etwa `exhaustive_finite`, `numerical_sample`, `analytic_argument`, `empirical_evaluation`, `not_evaluated`;
- `empirical_status`: getrennt, z. B. `not_tested`, `synthetic_only`, `evaluated_on_declared_data`;
- `scope`, Quellen, Code-Commit, Input-Digests, Toleranzen und bekannte offene Verpflichtungen.

Kein globales `confidence=0.97`; keine einzelne Ampel, die diese Achsen zusammenzieht. Ein Quellenverweis auf eine Herleitung ist noch kein maschinengeprüftes Beweiszertifikat. Ein Hash sichert die Referenz auf bestimmte Bytes, nicht deren wissenschaftliche Richtigkeit.

### 6.2 Funktionsentwurf

```python
audit_finite_claim(domain, assumptions, claim, *, budget) -> ClaimReport
find_minimal_support(domain, assumptions, claim, *, budget) -> SupportReport
find_minimal_inconsistent_core(domain, assumptions, *, budget) -> CoreReport
observation_fiber(domain, assumptions, observation, observed) -> FiberReport
identified_values(fiber, target) -> IdentifiedSetReport
uniform_safe_actions(fiber, actions, safety) -> ActionSetReport
compare_decisions(loss_matrix, *, criterion, probabilities=None) -> DecisionReport
```

`uniform_safe_actions` gilt zunächst nur für die vollständig deklarierte endliche Aktionsmenge. Der kontinuierliche Spezialfall K5 erhält eine eigene analytische Herleitung und einen dafür benannten Adapter; keine falsche Übertragung eines endlichen Tests auf alle reellen Steuerungen.

### 6.3 Implementierungsgrenzen

- Kein Freitext-Parser und kein `eval` von JSON-Inhalten. Prädikate werden im Code definiert, eindeutig registriert und als solche referenziert.
- Der exakte Kern verwendet boolesche Werte, Integer und rationale Zahlen. Bestehende Float-Funktionen werden als numerische Evidenz integriert.
- Bool-Prädikate liefern wirklich boolesche Ergebnisse; `None`, Strings oder fehlgeschlagene Berechnungen sind Fehler.
- Gültige Zustands- und Aktions-IDs sind eindeutig. Keine Normalisierung, die verschiedene Kandidaten versehentlich zusammenfallen lässt.
- Kandidatenzahl, Prädikatauswertungen und Supportsuche erhalten explizite Budgets. Ein Budgetabbruch bestätigt weder Minimalität noch universelle Gültigkeit.
- Für die erste Version sind beispielsweise höchstens 4096 Kandidaten, 4096 untersuchte Annahmenteilmengen und insgesamt 1000000 Prädikatauswertungen vernünftige Standardgrenzen. Alle Limits sind getrennt konfigurierbar und im Bericht sichtbar. Die Gesamtgrenze gilt auch über verschachtelte Supportprüfungen hinweg; ein innerer Aufruf erhält nicht jedes Mal ein frisches unbegrenztes Budget.
- Eine Markierung `partial` kann auch bedeuten, dass alle gelieferten Stichproben geprüft wurden, aber der behauptete Zielraum nicht vollständig erfasst ist. Beide Ebenen werden getrennt geführt.
- Rationale Zahlen werden im JSON als Zähler/Nenner oder kanonische Bruchstrings serialisiert; keine Umwandlung in Float im exakten Beweispfad.
- Widersprüchliche und unterbestimmte Ergebnisse sind erwartete wissenschaftliche Ergebnisse. Ein korrekt bestandener Regressionstest kann genau ein solches Ergebnis bestätigen.

## 7. H0 — Bestandsaufnahme und Quellenvertrag

**Zweck:** Doppelarbeit verhindern, die neuen Aussagen begrenzen und Abhängigkeiten prüfen.

Lieferungen:

- `EPISTEMIC_AUDIT_ROADMAP.md` mit getrennten Feldern für Implementation, Tests, Evidenzstatus und offene Teile;
- `docs/epistemic_scope.md` mit den Ergebnissen aus Abschnitt 4;
- `docs/epistemic_sources.md` auf Basis von Abschnitt 15;
- Liste der vorhandenen APIs und der minimal nötigen Adapter;
- aktueller Commit und Ausgangsregression, inklusive echter Skip-Zahlen.

Abnahme:

1. H-Namensraum prüfen, vorhandene Review-Fixes nicht überschreiben.
2. Die Galaxien-Abhängigkeiten aus §3.1 nur dann als erledigt markieren, wenn Gegenfälle tatsächlich behoben sind.
3. Quellen als Primärpapier, formales Artefakt, offizielle Tool-Dokumentation oder bloßer Anlass kennzeichnen.
4. Keine neue Paketabhängigkeit im Pflichtumfang.

## 8. H1 — Endliche Aussagen und nichtleere Evidenz

**Zweck:** Ausführbare Ergebnissemantik etablieren, bevor komplexere Auswertungen entstehen.

Implementiere `records.py`, `finite.py`, Exporte und `verification/verify_epistemic_finite.py`.

Pflichtprüfungen:

- alle vier vollständigen Fälle der Tabelle in §4.1;
- Gegenmodell widerlegt die universelle Behauptung, ohne automatisch das Gegenteil universell zu beweisen;
- leerer Input versus leere zulässige Menge;
- K2 und K3, einschließlich gesonderter Antezedensprüfung;
- Abbruch vor erstem Zeugen, nach positivem Zeugen und nach Gegenmodell;
- nachprüfbare Zeugen mit stabilen IDs und erneut ausgewerteten Annahmen;
- Prädikatfehler bleibt Fehler; keine stille Kandidatenentfernung;
- `grid_of_continuous_space` erhält niemals einen globalen Gültigkeitsstatus.

Abnahme: Der Bericht unterscheidet Vollständigkeit, logischen Befund, Rechenart und empirischen Status. Das ist die Voraussetzung für alle weiteren Pakete.

## 9. H2 — Tragende Annahmen und Inkonsistenzkerne

**Zweck:** Erklären, warum eine Aussage gilt oder eine Spezifikation leerläuft.

Implementiere `supports.py`, `verification/verify_epistemic_supports.py`.

Vorgehen:

1. Erfüllbarkeit beziehungsweise anfängliches Tragen der Aussage prüfen.
2. Für einen einzelnen Support/Kern ein deterministisches Löschverfahren verwenden.
3. Im Ergebnis jeden Einzelschritt durch Zeugen belegen; abschließend Minimalität erneut prüfen.
4. Alle minimalen Lösungen nur für kleine Fälle und mit separatem Limit enumerieren.

Pflichtprüfungen: K1 vollständig, beide Kardinalitäten, Löschzeugen, konstante wahre Aussage mit leerem Support, widersprüchlicher Ausgangsfall, mehrere alternative Supports, Budgetabbruch, unveränderte Hintergrundannahmen.

Abnahme: Ein Ergebnis heißt nur dann `subset_minimal_verified`, wenn alle benötigten Prüfungen abgeschlossen sind. `minimum_cardinality_verified` wird nur bei entsprechend vollständiger Suche gesetzt. Logische Redundanz wird nicht als empirische Unwichtigkeit bezeichnet.

## 10. H3 — Beobachtungsabhängige Identifikation

**Zweck:** Bestimmen, welche Aussage sich mit einer gegebenen Beobachtung überhaupt entscheiden lässt.

Implementiere `observation_fibers.py`, `verification/verify_epistemic_identification.py`.

Pflichtumfang:

- exakte endliche Fasern und mögliche Zielwerte;
- `point_identified`, `set_identified` und `incompatible_observation` nur im erklärten Scope;
- boolesche Aussagen mit zwei gegensätzlichen Zeugen bei Unterbestimmtheit;
- Prüfung einer deklarierten Verfeinerungsabbildung h_c=r∘h_f;
- K4 und K8; `is_union_of_classes` nutzen, statt denselben Sachverhalt unverbunden neu einzuführen;
- mindestens ein Beispiel für identifizierbare Aussage trotz nicht identifiziertem Gesamtzustand;
- Darstellung der nicht zusammenhängenden Wertemenge {0,4}.

Eine Toleranzrelation wie |h(w)−y|≤ε darf später kompatible Kandidaten definieren. Sie ist nicht allgemein transitiv und darf nicht ungeprüft zu Äquivalenzklassen zusammengefasst werden. Keine „fast gleich“-Partition durch willkürliches Clustering im exakten Pfad.

Abnahme: Zusätzliche Information kann gezielt bewertet werden, ohne vollständige Zustandsrekonstruktion als notwendiges Ziel vorauszusetzen.

## 11. H4 — Endliche Entscheidungen unter deklarierter Ungewissheit

**Zweck:** Handlungen vergleichen, obwohl keine einzelne Kandidatenbeschreibung ausgewählt wurde.

Implementiere `decisions.py`, `verification/verify_epistemic_decisions.py`.

Pflichtumfang:

- gemeinsame sichere Aktionen als Schnitt endlicher Aktionsmengen;
- explizite Flags `statewise_feasible` und `uniformly_feasible`;
- Erwartungsverlust nur mit validierter vorgegebener Verteilung;
- Worst-Case-Verlust und Minimax-Regret mit getrennten Ergebnissen;
- alle Gleichstände zurückgeben, keine wissenschaftliche Aussage aus einem willkürlichen Tie-Breaker;
- K6 und die endliche Aktionsversion von K5;
- endliche und vollständige Verlustmatrix, keine NaN/Infinity, keine negativen Wahrscheinlichkeiten, keine stille Renormalisierung;
- leere kompatible Menge und leere zulässige Aktionsmenge jeweils eigener Status.

Eine harte Sicherheitsverletzung wird nicht durch günstige mittlere Kosten kompensiert. Gibt es keine robuste zulässige Aktion, lautet das Ergebnis `no_uniform_feasible_action`; ein separat gewünschter Vergleich unsicherer Alternativen muss ausdrücklich als andere Aufgabe gekennzeichnet werden.

K7 bleibt dokumentierte optionale Vertiefung. Eine allgemeine Bibliothek für robuste dynamische Programmierung, priorfreie Bayes-Updates oder distributionell robuste Optimierung ist nicht Bestandteil dieses Pakets.

## 12. H5 — Integrierter Pufferpilot

**Zweck:** Den neuen Rahmen in einer bereits vorhandenen SCF-Domäne nutzbar machen.

Implementiere `validation/epistemic_buffer_pilot.py`, `docs/epistemic_buffer_pilot.md`, `verification/verify_epistemic_buffer_pilot.py`.

Drei Informationsmodi für K5:

| Modus | Verfügbar bei t=0 vor der Steuerungswahl | Sicherheit bei Budget 1 |
|---|---|---|
| A | Summe x1+x2=2 | Keine uniforme sichere Aktion |
| B | Summe und Minimum | In der Faser min=0 weiterhin keine uniforme sichere Aktion |
| C | Summe und Vorzeichen von x1−x2 | Beobachtungsbasierte sichere Politik für alle drei Zustände |

Die notwendige Budgetgrenze 2 versus 1 analytisch herleiten, anschließend mit vorhandener Puffer-API und unabhängigem rationalem Oracle vergleichen. Das konkrete Beispiel erlaubt analytische Beschränkung über kontinuierliche Aktionen. Diese Herleitung wird separat von der endlichen Aufzählung dokumentiert.

Zusätzliche Pflichtgegenkontrollen:

- Budget knapp unter 1 verhindert bereits die Versorgung des leeren Einzelpuffers; bei 1 exakt Grenzfall.
- Budget knapp unter 2 verhindert den uniformen Eingriff; bei 2 ist (1,1) möglich.
- Grenzberührung genau bei t=1 ist bei der nichtstrikten Grenze erlaubt.
- Unsicherer Anfangszustand darf nicht durch spätere Erholung als über den ganzen Horizont sicher gelten.
- Eine erst nach der Steuerungswahl verfügbare Beobachtung darf nicht in die Wahl einfließen.
- Die Sicherheit bei gehaltenem Eingriff nicht mit beliebigem Feedback, beliebigen Drains oder unbegrenztem Horizont verwechseln.

Bericht: Annahmen, Faser, zustandsweise Aktionen, uniforme Aktionen, verwendete Beobachtung, Handlungspolitik, Budget, Horizont, Toleranzen und Scope. Noch keine empirische Aussage über reale Tanks, Batterien oder Wasserreservoirs.

## 13. H6 — Bestehende Berichte anbinden

**Pflichtteil H6a: kleine additive Adapter.**

1. `CorrespondenceReport` mit deklarierter Stichprobe und Toleranzen als `numerical_sample` berichten. Ein `ok=True` wird nicht zu `exhaustive_finite` über einen kontinuierlichen Zustandsraum.
2. Den Markov-Kontrollfall K8 über vorhandene APIs aufrufen und Dynamikverträglichkeit getrennt von Ereignisbeobachtbarkeit darstellen.
3. `Scope.assumptions` bleibt kompatibel. Wo strukturierte IDs fehlen, sind Textannahmen zunächst dokumentiert, nicht automatisch formal geprüft.

Lieferungen: `adapters.py`, `verification/verify_epistemic_adapters.py`, mindestens zwei maschinenlesbare Beispielberichte und deren verständliche Markdown-Ausgabe.

**Optional H6b: synthetischer Galaxienfall.**

Die in `verify_galaxy_observation_maps.py` bereits vorhandene Burkert/NFW-Anpassung an zwei Radien wird referenziert oder in einen kleinen wiederverwendbaren Helfer ausgelagert. Sie demonstriert numerische Ununterscheidbarkeit innerhalb der deklarierten Toleranz an diesen Radien und Abweichungen an anderen Radien. Keine erneute Behauptung vollständiger Beobachtungsäquivalenz aller Messverfahren oder aller Radien.

**Zurückgestellt H6c: reale SPARC-Berichte.**

Erst nach Prüfung der Review-Abhängigkeiten aus §3.1. Eine Profilkurve wird dann als numerische Evidenz mit Optimierungs- und Randdiagnostik eingebunden; keine automatische Umbenennung in ein rigoroses Identifikationsgebiet. Vorhandene Datenprovenienz und lokale Lizenzregeln gelten weiter. Für H0–H7 werden weder Rohdaten neu heruntergeladen noch eingecheckt.

Abnahme H6a: Die Wrapper erhöhen die Transparenz und verändern die Bedeutung vorhandener Resultate nicht. H6b und H6c bekommen eigene Statuszeilen; ein offener optionaler Teil wird nicht als abgeschlossen mitgezählt.

## 14. H7 — Dokumentation, CLI, CI und Abschluss

Ein kleiner Einstieg `scripts/run_epistemic_audit.py` soll registrierte Kontrollfälle ausführen und JSON/Markdown ausgeben. Beispielhafte Benutzerschnittstelle, noch kein existierender Befehl:

```bash
python scripts/run_epistemic_audit.py --case buffer_information --format json
python scripts/run_epistemic_audit.py --case buffer_information --format markdown
```

Freie Codeausführung aus Eingabedokumenten ist nicht vorgesehen. Registrierung weniger überprüfbarer Fälle genügt.

Neue Tests ausdrücklich in `_EXPLICIT_CATEGORY` von `scripts/run_verification_suite.py` als `math` registrieren. Alle Pflichtfälle sind synthetisch/analytisch. Falls später ein echter Datenadapter hinzukommt, gehört sein tatsächlicher Datenlauf in `data`.

Bestehende Aufrufe weiterverwenden:

```bash
python scripts/run_verification_suite.py --category math
python scripts/run_verification_suite.py --category data
python scripts/run_verification_suite.py --category links
```

Keine feste zukünftige Suitezahl vorgeben. Tatsächlich ausgeführte, bestandene, fehlgeschlagene und übersprungene Tests getrennt berichten. Eine grüne CI bedeutet korrekte Prüfung der kodierten Erwartungen, keine Bestätigung aller in einem Beispiel diskutierten Behauptungen.

### 14.1 Abschlusskriterien

- [ ] H1–H4 unterscheiden alle in §4 geforderten Befunde und besitzen Zeugen/Gegenzeugen.
- [ ] K1–K6 und K8 sind unabhängig hergeleitet und im Repository sinnvoll verankert.
- [ ] H5 belegt den Quantorenunterschied und die Budgetgrenzen exakt.
- [ ] H6a nutzt vorhandene APIs; deren numerischer Status bleibt sichtbar.
- [ ] Dokumentation erklärt, wann eine Aussage identifizierbar ist, obwohl der Zustand es nicht ist.
- [ ] Prüfbarkeit, statistische Kalibrierung, empirische Bewährung und Handlungspräferenz werden nicht gleichgesetzt.
- [ ] Keine globale Gültigkeit aus Raster-, Stichproben- oder Budgetabbrüchen.
- [ ] Keine automatische Gleichverteilung über Kandidaten und keine unendlichen Nutzenwerte im endlichen API-Pfad.
- [ ] Roadmap benennt H6b/H6c, K7 und weitere Rückstellungen einzeln.
- [ ] Bestehende Regression, neue gezielte Prüfungen und Linkprüfung erfolgreich; Skips ehrlich ausgewiesen.

**Sinnvolle Implementierungsreihenfolge:** H0 → H1 → H2 → H3 → H4 → H5 → H6a → H7. Die kleinste bereits nützliche Zwischenversion endet nach H3. Der größte zusätzliche Anwendungsnutzen entsteht mit H5. Commits pro kohärentem Paket; Veröffentlichung nur im vom Nutzer beauftragten Arbeitsablauf.

### 14.2 Definition des tatsächlich erreichten Nutzens

Nach Abschluss kann SCF für seine deklarierten endlichen Fälle angeben:

> Diese Aussage folgt aus diesen Annahmen in diesem Modellraum. Hier sind ein erfüllendes Modell, gegebenenfalls ein Gegenmodell und die für die Aussage tragenden Annahmen. Diese Beobachtung lässt jene Alternativen offen. Diese Handlungen sind unter allen verbleibenden Alternativen zulässig; jene zusätzliche Messung verändert die Handlungsmöglichkeiten.

Das ist ein konkreter Fähigkeitszuwachs, der vorhandene Domänen verbindet.

## 15. Quellenregister und gezielte Verwendung

Recherche geprüft am 26.09.2026. „Volltext“ bedeutet hier: Volltext zugänglich und die für den Plan relevanten Abschnitte eingesehen; keine Behauptung, sämtliche Beweise dieser Arbeiten unabhängig formal verifiziert zu haben. Die Kontrollfälle K1–K8 sind eigene, kleine Ableitungen dieses Plans.

### S1 — Vorhandene formale Gödel/Scott-Implementierung

Christoph Benzmüller und Bruno Woltzenlogel Paleo, **Gödel's God in Isabelle/HOL**, Archive of Formal Proofs, 12.11.2013.

- [Offizieller Eintrag](https://isa-afp.org/entries/GoedelGod.html).
- Geprüft: Metadaten, formalisierte Scott-Fassung, QML KB als Einbettung in HOL, BSD-Lizenz; verlinkte Proof-Artefakte sind vorhanden. Kein eigener Isabelle-Lauf in dieser Recherche.
- Nutzen: konkretes Beispiel für explizite logische Semantik und getrennte Fassung eines Arguments.
- Grenze: kein empirischer Existenznachweis und keine Verpflichtung, Isabelle zu SCF hinzuzufügen.

### S2 — Inkonsistenzsuche und verständliche Rekonstruktion

Christoph Benzmüller und Bruno Woltzenlogel Paleo, **The Inconsistency in Gödel’s Ontological Argument: A Success Story for AI in Metaphysics**, IJCAI 2016, S. 936–942.

- [Primärvolltext](https://www.ijcai.org/Proceedings/16/Papers/137.pdf).
- Geprüft: insbesondere §4; entdeckte Inkonsistenz, manuelle Erklärung und Rekonstruktion in Isabelle.
- Nutzen: Erfüllbarkeitsprüfung vor einer inhaltlich belastbaren Schlussfolgerung; automatisch gefundene Resultate brauchen lesbare Begründungen.
- Grenze: ursprüngliche Gödel-Fassung und Scott-Variante ausdrücklich unterscheiden.

### S3 — Geltungsbereich endlicher Gegenmodellsuche

Alloy Project, **Official Alloy Tutorial: File System, assertions and scope**.

- [Offizielle Dokumentation](https://alloytools.org/tutorials/online/maintext-FS-1.html).
- Geprüft: endlicher Scope und Bedeutung von „kein Gegenbeispiel gefunden“; keine Garantie für größere Scopes.
- Nutzen: Berichtsemantik in H1.
- Grenze: offizielle Tool-Dokumentation, kein empirischer Nachweis, dass kleine Scopes alle Fehler finden. Alloy wird zunächst nicht als Abhängigkeit benötigt.

### S4 — Vacuity Detection

Orna Kupferman und Moshe Y. Vardi, **Vacuity detection in temporal model checking**, STTT 4, 224–233, 2003; online 2002.

- [DOI und Verlagsabstract](https://doi.org/10.1007/s100090100062).
- Geprüft: bibliografische Angaben und Abstract; Verlagsvolltext nicht frei zugänglich, Autoren-Volltextlink in dieser Recherche nicht erfolgreich abrufbar.
- Nutzen: Ein bestandener Spezifikationstest kann inhaltsleer sein, wenn seine Voraussetzung nie eintritt.
- Grenze: Der Plan implementiert nur den expliziten endlichen Antezedenscheck, nicht die gesamte CTL*-Analyse.

### S5 — Qualität einer Spezifikation

Dana Fisman, Orna Kupferman, Sarai Sheinvald-Faragy und Moshe Y. Vardi, **A Framework for Inherent Vacuity**, HVC 2008.

- [Autoren-Volltext](https://www.cs.rice.edu/~vardi/papers/hvc08.pdf).
- Geprüft: Einleitung und Definitionen zur Spezifikationsqualität und inhärenten Vacuity.
- Nutzen: Motivation, nicht nur Implementierungen, sondern auch die Aussageform selbst zu prüfen.
- Grenze: Vollständige temporallogische Mutation und Synthese werden zurückgestellt.

### S6 — Minimale Mengen sind nicht notwendig die kleinsten

João Marques-Silva und Mikoláš Janota, **Computing Minimal Sets on Propositional Formulae I: Problems & Reductions**, arXiv:1402.3011v2, 2014.

- [Primärvolltext](https://arxiv.org/pdf/1402.3011v2).
- Geprüft: Definition minimaler Mengen, Funktionprobleme und gesonderte Optimierung nach Kardinalität.
- Nutzen: präzise Support-/Kernsemantik in H2.
- Grenze: endliche Referenzalgorithmen übernehmen diese Begriffe; sie beanspruchen keine SAT-Skalierbarkeit.

### S7 — Identifikation und statistische Entscheidung

Charles F. Manski, **Identification and Statistical Decision Theory**, arXiv:2204.11318, zuerst 2022; eingesehener Volltext mit Stand August 2023.

- [Versionen und Metadaten](https://arxiv.org/abs/2204.11318), [Primärvolltext](https://arxiv.org/pdf/2204.11318).
- Geprüft: Einleitung sowie §2–4; Trennung zwischen Kenntnis der beobachtbaren Verteilung und endlichen Stichproben, Entscheidungskriterien, Rolle von Randomisierung.
- Nutzen: H3/H4 und die klare Begrenzung statistischer Aussagen.
- Grenze: Die endlichen SCF-Kontrollfälle ersetzen keine allgemeine frequentistische Entscheidungsanalyse.

### S8 — Direkter aktueller Anschluss an die Ausgangsidee

Charles F. Manski, **Coping with Inductive Risk When Theories are Underdetermined: Decision Making with Partial Identification**, arXiv:2602.00355v2, 08.04.2026; erste Einreichung 30.01.2026.

- [Versionierter Primärbeleg](https://arxiv.org/abs/2602.00355v2), [Volltext](https://arxiv.org/pdf/2602.00355v2).
- Geprüft: Abstract, §2 zur Identifikation sowie §5 zu Entscheidungen bei verbleibender Unterbestimmtheit.
- Nutzen: besonders direkte Forschungsbrücke zwischen wissenschaftlicher Unterbestimmtheit und konkretem Entscheiden.
- Status: hier als Preprint verwendet; kein ungeprüfter Peer-Review-Status behauptet.
- Grenze: Unterstützung des methodischen Anschlusses, keine Bestätigung einer spezifischen SCF-Theorie.

### S9 — Robuste Entscheidungen und Informationszeitpunkt

Bram L. Gorissen, İhsan Yanıkoğlu und Dick den Hertog, **A Practical Guide to Robust Optimization**, arXiv:1501.02634, 2015.

- [Primärvolltext](https://arxiv.org/pdf/1501.02634).
- Geprüft: Modellannahmen, Unsicherheitsmenge und robuste Zulässigkeit; hier-und-jetzt-Entscheidungen.
- Nutzen: gemeinsamer Eingriff über eine Unsicherheitsmenge und ausdrückliche Entscheidung darüber, wann Information verfügbar ist.
- Grenze: K5 ist ein separat hergeleiteter Spezialfall. Keine universelle Sicherheitsgarantie außerhalb der deklarierten Unsicherheitsmenge.

### S10 — Perspektive für spätere gegenbeispielgeleitete Verfeinerung

Edmund Clarke, Orna Grumberg, Somesh Jha, Yuan Lu und Helmut Veith, **Counterexample-guided Abstraction Refinement**, CAV 2000.

- [Autoren-Volltext](https://www.cs.cmu.edu/~emc/papers/Conference%20Papers/Counterexample-guided%20Abstraction%20Refinement.pdf).
- Geprüft: abstrakte gegenüber konkret nachvollziehbaren Gegenbeispielen und Verfeinerung.
- Nutzen: spätere Erweiterung der vorhandenen Vergröberungs-/Schließungsmodule.
- Grenze: Ein bloßes Aufteilen einer Beobachtungsfaser implementiert noch kein vollständiges CEGAR-Verfahren. Dafür wären nachgewiesene Abstraktionsbeziehungen und Pfadprüfung nötig.

## 16. Bewusst zurückgestellte Erweiterungen

| Thema | Natürlicher Anschluss | Voraussetzung |
|---|---|---|
| SAT/SMT-Backend | Größere endliche Annahmensysteme | Profilierte Skalierungsgrenze des einfachen Oracles; gleiche Scope- und Unknown-Semantik |
| Lean/Isabelle-Zertifikate | Mechanisierte Beweise ausgewählter algebraischer Sätze | Kleiner konkreter Satz und Nutzen gegenüber separatem Handbeweis |
| Temporallogik / CEGAR | Vergröberte Trajektorien und Gegenbeispiele | Soundness der Abstraktion, Zeithorizont und konkretes Replay geklärt |
| Statistische partielle Identifikation | Rauschende Realbeobachtungen, Konfidenzmengen | Daten-generierendes Modell, Coverage-Ziel und unabhängige Kalibrierung |
| Mehrstufige robuste Politiken | Wiederholte Messung und spätere Eingriffe | Explizite Informationsstruktur; keine Antizipation künftiger Daten |
| Kausale Annahmensensitivität | Mechanismenvergleich bei Interventionen | Eigene strukturelle Kausalmodelle und begründete Interventionssemantik |
| Randomisierte Entscheidungen | K7 und Verlustoptimierung | Klare Trennung von erwarteter Güte und harter Sicherheitsgarantie |

## 17. Kompakter Arbeitsauftrag an Claude-Code

Implementiere den Pflichtumfang H0–H7 dieses Plans additiv auf dem aktuellen Repository-Stand. Prüfe zunächst den aktuellen Commit, vorhandene lokale Anweisungen und bereits erledigte Review-Fixes. Halte den exakten endlichen Kern klein und verwende die vorhandenen SCF-Module für Markov-, Korrespondenz- und Pufferbeispiele.

Leite K1–K6 und K8 selbst nach, bevor du die mitgelieferten Referenzwerte als Regression verwendest. Das Begleitskript ist ein unabhängiger Vergleich, kein zu kopierender Ersatz für diese Prüfung. Bewahre bei jedem Bericht den Unterschied zwischen vollständiger endlicher Prüfung, numerischem Stichprobentest und empirischem Ergebnis.

Bearbeite zunächst H0–H3, danach Entscheidungen und den integrierten Pufferpiloten. Schließe mit den beiden Pflichtadaptern H6a und H7 ab. Dokumentiere optionale oder blockierte Teile einzeln. Eine leere Modellmenge, ein Gegenmodell oder ein unmöglicher uniformer Eingriff sind zulässige wissenschaftliche Resultate und dürfen nicht für eine positivere Zusammenfassung umgedeutet werden.
