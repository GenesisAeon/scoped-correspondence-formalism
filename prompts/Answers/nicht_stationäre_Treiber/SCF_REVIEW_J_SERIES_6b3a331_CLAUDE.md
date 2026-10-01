# SCF: gezielte Review von j-series bei 6b3a331

Stand: 1. Oktober 2026. Übergabe an Johann und Claude-Code.

**Empfehlung: eine begrenzte Reparaturrunde vor dem Merge.** Der synthetische Organoid-Benchmark ist nachvollziehbar und angemessen eingeordnet. Bei der Prüfung der offenen API-Entscheidungen wurden jedoch falsche Fehlerschranken und die Verarbeitung ungültiger numerischer Eingaben reproduziert. Die grünen bisherigen Prüfungen decken diese Gegenbeispiele nicht ab.

## 1. Prüfstand und Reichweite

- Repository: https://github.com/GenesisAeon/scoped-correspondence-formalism
- Geprüfter Commit: `6b3a3313e908578b2f83f99d930559f53c831edf`, Branch `j-series`.
- GitHub meldete zum Prüfzeitpunkt 32 Commits vor `master`, keinen dahinter. Das beschreibt die Abstammung, keine vollständige Merge-Freigabe.
- Der [GitHub-Actions-Lauf 36895233724](https://github.com/GenesisAeon/scoped-correspondence-formalism/actions/runs/36895233724) ist erfolgreich. Die Jobs Mathematik, Realdaten und interne Markdown-Links wurden einzeln geprüft.
- Die Zahl **138/138** stammt aus dem Implementierungsbericht. In dieser Review wurde nicht die gesamte Suite erneut ausgeführt.
- Originaldateien wurden über den GitHub-Zugriff am genannten Commit gelesen und lokal unverändert für gezielte Reproduktionen verwendet. Der gesamte voreingestellte ON-Benchmark wurde mit sechs Läufen und sieben Bedingungen erneut ausgeführt.
- Schwerpunkt: ON-Auswertung, Decoder, adaptive Dynamik und die vier Entscheidungen in `DEEP_RESEARCH_BACKLOG.md`, Abschnitt E. Keine Vollprüfung sämtlicher J-, MU-, TP-, SK- und SA-Module.
- Keine Änderungen am Repository, kein Merge und keine Release-Veröffentlichung durch diese Review.

## 2. Bestätigte Ergebnisse des synthetischen Benchmarks

Die erneute Ausführung von `run_benchmark(BenchmarkConfig(), Path("configs/organoid_minimal.json"))` ergab:

| Bedingung | Mittelwert Δ Accuracy, neu trainiert | SEM von Δ über Läufe | Accuracy nachher, eingefroren | Accuracy nachher, neu trainiert |
|---|---:|---:|---:|---:|
| M3, getrennte Eingänge, volle Beobachtung, feste Gewichte | 0,000000 | 0,000000 | 1,000000 | 1,000000 |
| M3, getrennte Eingänge, volle Beobachtung, Anpassung | −0,091908 | 0,054629 | 0,551599 | 0,908092 |
| M3, gemeinsame Eingangsregion, Anpassung | 0,353901 | 0,085893 | 0,496528 | 0,881998 |
| M3, Summenbeobachtung, Anpassung | 0,329180 | 0,075614 | 0,500000 | 0,878233 |
| M1, gleichförmiger Operator, Anpassung | 0,355584 | 0,085570 | 0,496528 | 0,883681 |
| M3, c = 8/11, derselbe Operator, Anpassung | 0,355584 | 0,085570 | 0,496528 | 0,883681 |
| M3, Sensorumordnung, feste Gewichte | 0,000000 | 0,000000 | 0,631755 | 1,000000 |

Beim letzten Kontrollarm lauten die sechs eingefrorenen Scores ungefähr `0.5500, 0.6667, 0.5909, 0.8125, 0.6250, 0.5455`.

Diese Resultate tragen die vorsichtige Interpretation im Repo: Ausgangsniveau, Beobachtung und Ausleseverfahren beeinflussen die Ergebnisse; die Modulbezeichnung allein erzeugt keinen Vorteil. Der Benchmark bestätigt keine biologische Drei-Modul-Schwelle. Die Unterscheidung zwischen eingefrorenem und neu trainiertem Decoder ist inhaltlich wertvoll.

Die folgenden Befunde sind keine Feststellung, dass diese veröffentlichten Benchmarkzahlen falsch seien. Die gezielt verwendeten ungültigen Eingaben kommen im erneut ausgeführten Standardbenchmark nicht vor.

## 3. Reproduzierte Befunde und Reparaturen

### R1 — P1: falsche Nullschranke im allgemeinen CTMC-L1-Zweig

**Ort:** `src/scoped_correspondence/closure/error_bounds.py`, `transient_reduction_bound`, insbesondere der Zweig `theta_inf == 0.0` um Zeile 290. Bereits vorhandenes Modul; kein durch ON eingeführter Fehler.

Der Code setzt dort `l1 = e0`. Aus fehlender reduzierter Dynamik folgt jedoch nicht, dass die volle Dynamik den Fehler unverändert lässt.

Verwende

\[
\Theta=(0),\quad A=(1/2,0),\quad \pi_0=(2),\quad p_0=(1,0),\quad
Q=\begin{pmatrix}-1&1\\0&0\end{pmatrix},\quad t=1.
\]

`Q` ist ein gültiger Generator, `p0` eine Wahrscheinlichkeitsverteilung und `pi0 @ A == p0`. Die allgemeine L1-Reduktion erlaubt eine nicht normierte reduzierte Anfangskoordinate und ein nicht stochastisches Lifting. Das sind keine ungültigen Eingaben für diesen allgemeinen Zweig.

Die reduzierte Rekonstruktion bleibt `(1,0)`. Die volle Verteilung wird `(exp(-t), 1-exp(-t))`. Deshalb beträgt der tatsächliche Fehler

\[
\|e_1\|_1=2(1-e^{-1})=1.2642411176571153.
\]

**Aktuelles Ergebnis:** `bound=0.0`, `norm="L1"`. Auch bei `Theta=[[1e-20]]` wird in der lokalen Reproduktion durch Auslöschung in `exp(x)-1` eine Nullschranke geliefert.

**Reparatur:** Setze für den allgemeinen Zweig mit `kappa=||Theta||_inf`

\[
\phi(t,\kappa)=\begin{cases}t,&\kappa=0,\\
\operatorname{expm1}(t\kappa)/\kappa,&\kappa>0,
\end{cases}\qquad
B=e_0+\|\pi_0\|_1\|\Theta A-AQ\|_\infty\phi(t,\kappa).
\]

Für das Nullgenerator-Beispiel ist diese Schranke **2**, nicht 0. Sie liegt korrekt oberhalb des tatsächlichen Fehlers. Der Grenzfall folgt direkt durch Integration der konstanten Fehlerwachstumsschranke bzw. durch stetige Fortsetzung. `expm1` vermeidet die gezeigte Auslöschung; es macht eine Gleitkommaauswertung noch nicht zu einer rigorosen Intervallschranke.

**Regressionen:** exakt `kappa=0`, sehr kleines positives `kappa`, `t=0`, verschwindendes Residuum und ein normal großer Kontrollwert. Erwartete Schranke und tatsächlichen Fehler unabhängig berechnen. Den allgemeinen L1-Zweig erhalten; nicht durch pauschales Erzwingen von `sum(pi0)==1` verstecken.

**Reichweite:** Der J11-Vertragsadapter prüft `pi0` für seinen eingeschränkten Item-3-Vertrag und weist dieses Beispiel zurück. Der Gegenfall betrifft die ältere, öffentlich aufrufbare allgemeine Funktion.

### R2 — P1: Voraussetzungen der vollen Dynamik fehlen

**Ort:** dieselbe Funktion; die Ergebnisannahmen behaupten sogar `A, P arbitrary finite` bzw. `A, Q arbitrary finite`.

Das beliebige Lifting `A` ist im allgemeinen L1-Satz zulässig. Eine beliebige volle Dynamik `P` oder `Q` ist es für die verwendete kontraktive Markov-Schranke nicht.

Diskretes Gegenbeispiel:

\[
\Pi=(1),\quad A=(1,0),\quad P=\operatorname{diag}(2,1),\quad
\pi_0=(1),\quad p_0=(1,0),\quad k=2.
\]

Aktuell wird `bound=2.0` zurückgegeben; der tatsächliche L1-Fehler ist **3**. `P` ist absichtlich keine stochastische Matrix. Die API müsste die Eingabe ablehnen, statt dafür diese Schranke auszustellen.

**Reparatur und Scope:**

1. Volles `P` als quadratische, endliche, zeilenstochastische Matrix prüfen; volles `Q` als quadratischen, endlichen CTMC-Generator prüfen. Dimensionen aller Matrizen und Vektoren gemeinsam prüfen.
2. Im L1-Zweig die ausdrücklich unterstützten allgemeinen `A`, `Pi/Theta` und reduzierten Anfangsvektoren erhalten. Eine Erweiterung auf beliebige volle lineare Dynamik würde zusätzliche Verstärkungsfaktoren benötigen und ist kein kleiner Validierungsfix.
3. Für `norm="TV"` einen klaren Wahrscheinlichkeitsvertrag verlangen: insbesondere stochastisches Lifting und normierte nichtnegative Anfangsverteilungen sowie passende Markov-Dynamik. Allgemeine halbe L1-Normen nicht ohne diesen Vertrag als Distanz zwischen Wahrscheinlichkeitsverteilungen ausgeben.
4. `stationary_reduction_bound` separat anhand seiner algebraischen Ungleichung prüfen. Nicht unbesehen sämtliche transienten Einschränkungen auf diesen anderen Satz übertragen.
5. Die Formulierungen `P/Q arbitrary finite` korrigieren und die verwendete Primärquellenversion richtig angeben: **arXiv v3**, nicht v2, enthält die hier zitierten Satznummern und den erweiterten allgemeinen Rahmen.

**Regressionen:** obiges ungültiges `P`; ungültiger Generator; transponierte Orientierung; gültige allgemeine L1-Reduktion; TV mit nicht stochastischem Lifting. Ablehnungen sollen `ScopeViolationError` bzw. einen dokumentierten Invaliditätsstatus liefern.

### R3 — P1: NaN erzeugt einen scheinbar extremen Signifikanzbefund

**Ort:** `validation/modular_networks/decoders.py`, `sign_flip_test`, um Zeile 160. Neues ON-Modul.

```python
sign_flip_test([float("nan"), 1.0, 1.0])  # aktuell Fraction(0, 1)
```

`obs` wird `NaN`; sämtliche Vergleiche `>= obs` sind falsch. Daraus entsteht `hits=0` und damit `p=0`. Ungültige Daten werden in einen irreführenden statistischen Befund umgewandelt.

**Reparatur:** Alle Differenzen vor der Enumeration auf erlaubte reelle Typen und Endlichkeit prüfen. `NaN`, `+inf`, `-inf` ablehnen. Keine stillschweigende Entfernung von Präparaten; eine etwaige Ausschlussregel muss vorab separat greifen und berichtet werden. Exakte `int`-/`Fraction`-Eingaben ohne verlustbehaftete Float-Konvertierung erhalten.

**Regressionen:** alle drei nicht endlichen Werte an unterschiedlichen Positionen; `[0,0,0] -> 1`; `[1,1,1] -> 1/4`; fünf gleiche positive Differenzen `-> 1/16`. Bei endlichen Daten und vollständiger zweiseitiger Enumeration mit `>=` ist `p=0` unmöglich: das beobachtete Vorzeichenmuster ist enthalten.

Die statistische Interpretation zusätzlich explizit an Vorzeichen-Austauschbarkeit unter der Nullhypothese binden. Vollständiges Durchzählen allein macht diese Annahme nicht wahr.

### R4 — P2: directed_information verwirft NaN-Masse stillschweigend

**Ort:** `observation/directed_information.py`, `_normalize_joint`, um Zeile 142. Bereits vorhandenes Modul.

```python
directed_information({
    ((0,), (0,)): 0.5,
    ((1,), (1,)): float("nan"),
})  # aktuell gültig wirkender Bericht mit I_directed=I_mutual=0
```

Für `NaN` sind sowohl der Negativtest als auch `m > _EPS` falsch. Das Atom verschwindet und die verbleibende Masse wird normiert. Das ist ein anderer Fehler als die dokumentierte Annahme unnormierter Gewichte.

**Reparatur:** Nicht endliche Einzelmassen vor Vergleichen zurückweisen; auch die Gesamtsumme prüfen. Gültige Gewichte und ungültige numerische Werte getrennt behandeln. Bei sehr großen endlichen Gewichten einen möglichen Summenüberlauf berücksichtigen.

BROJA sollte dieselbe frühe Endlichkeitsprüfung erhalten. In dieser Review führten `NaN`/`inf` bei einem kleinen BROJA-Gegenfall bereits zu einer späteren Ausnahme wegen negativer Synergie. Es wurde **kein** erfolgreicher BROJA-Bericht mit diesen ungültigen Eingaben nachgewiesen. Der Verbesserungsbedarf dort ist die frühe, sachlich richtige Validierung statt eines irreführenden Optimierungsfehlers.

### R5 — P2: Decoder akzeptiert fehlende Features und NaN beim Vorhersagen

**Ort:** `validation/modular_networks/decoders.py`, `NearestMeanDecoder.predict`, um Zeile 82. Neues ON-Modul.

Nach Training mit zwei Features:

```python
d = NearestMeanDecoder().fit([[0., 0.], [1., 1.]], [0, 1])
d.predict([[float("nan"), float("nan")]])  # aktuell [0]
d.predict([[0.]])                           # aktuell [0]
```

Im zweiten Fall füllt NumPy das fehlende Feature durch Broadcasting. Im ersten liefert der Distanzvergleich trotz ungültiger Werte eine Klasse. Beides kann eine kaputte Messpipeline verdecken.

**Reparatur:** Vorhersage verlangt einen trainierten Decoder, eine endliche zweidimensionale Matrix und exakt die trainierte Featurezahl. Kein Broadcasting zur Reparatur fehlender Sensoren. Fitted-State und zulässige Leer-Eingabe explizit definieren.

**Regressionen:** beide Fälle oben; zu viele Features; eindimensionaler Input; Vorhersage vor Training; gültige zwei-Feature-Eingabe. Die vorgesehene Sensorpermutation muss als Transformation vollständiger Daten weiterhin funktionieren.

## 4. Empfehlungen zu den vier Entscheidungen in Backlog E

| Entscheidung | Empfehlung | Kompatibilität und Grenze |
|---|---|---|
| DI/BROJA normieren Gewichte automatisch | Endlichkeit sofort erzwingen; strikten PMF-Modus und expliziten Gewichtsmodus unterscheiden. | Automatische Normierung ist in beiden bestehenden Docstrings ausdrücklich beschrieben. Sie ist deshalb nicht allein ein Implementierungsbug. Einen veränderten Standardmodus als API-Änderung dokumentieren; vorhandene Aufrufer prüfen und migrieren. |
| Voraussetzungen der Reduktionsschranke | R1 und R2 beheben, TV-Vertrag in der Kernfunktion prüfen. | Allgemeine L1-Reduktionen bleiben zulässig. Der J11-Adapter schützt nur seine eigenen Aufrufpfade. |
| NaN/Infinity in JSON | Nach Definition eines Schemas `allow_nan=False` verwenden. | Mathematisch unbeschränkte Intervalle sind legitim. Sie brauchen eine explizite Darstellung, z. B. `null` plus `bound_status="unbounded"`. Unbekannt, ungültig und unbeschränkt unterscheiden; keine Umwandlung in 0. Auch verschachtelte Felder testen. |
| Conformal-Quantil und Dezimal-alpha | Exakte `Fraction`-/Dezimalstring-Eingaben nach einheitlicher J8-Konvention ermöglichen; gemeinsam genutzte Rangberechnung bevorzugen. | Float-Semantik ausdrücklich festlegen. Kein pauschales Abrunden oder Epsilon-Abziehen vor `ceil`, das echte Werte oberhalb einer Grenze nach unten verschieben könnte. |

Der Conformal-Befund wurde reproduziert: Für `n=9`, `alpha=0.7` liefert die Float-Rechnung Rang **4**, während das ausdrücklich dezimal gemeinte `alpha=7/10` Rang **3** verlangt. Bei Residuen `1,…,9` wird damit aktuell `q=4` statt `q=3` ausgegeben. Dieses konkrete Beispiel ist konservativ. Daraus folgt keine allgemeine Aussage über sämtliche Float-Eingaben.

JSON wurde ebenfalls reproduziert: `report_to_json` gibt für eine Dataclass mit Float-NaN derzeit ein nacktes `NaN`-Token aus. Der Fix muss die im Repo fachlich zulässigen unbeschränkten Größen berücksichtigen, bevor er global aktiviert wird.

## 5. Begrenzte methodische Verbesserungen nach den Fehlerkorrekturen

### 5.1 Gemeinsamer Testsatz für eingefrorenen und neu trainierten Decoder

In `run_condition` ruft `evaluate` aktuell für beide Decoder getrennt `_dataset` und `_split` auf. Beide erhalten damit andere Rauschrealisierungen und andere Testsplits. Die Randmittelwerte können weiterhin sinnvoll sein; die direkte Differenz enthält aber zusätzliche Stichprobenvariation.

Pro späterer Epoche genau einen Testsatz festlegen. Den neuen Decoder auf einem davon getrennten Trainingssatz fitten und beide Decoder auf denselben Testversuchen auswerten. Trial-IDs und Split-IDs speichern. Das verbessert die gepaarte Vergleichbarkeit und macht keine neue biologische Behauptung erforderlich.

### 5.2 Exakte Permutationskontrolle vom verrauschten Beispiel trennen

Die jetzige Prüfung `after_refitted == before` trifft in der festgelegten Konfiguration zu, weil die Scores jeweils 1 sind. Unveränderte Information unter einer invertierbaren Transformation erzwingt keine bitgleiche Accuracy zweier unabhängig gezogener endlicher Stichproben.

Ergänze eine mechanistische Kontrolle mit denselben verrauschten Daten: Features sowohl im Training als auch im Test identisch permutieren und den Decoder entsprechend neu fitten. Die Predictions müssen für den verwendeten permutationsäquivarianten Decoder gleich bleiben. Das veröffentlichte Drift-Beispiel darf zusätzlich als festes Beispiel bestehen, soll aber nicht als allgemeines endliches Score-Invarianzgesetz beschrieben werden.

### 5.3 Öffentliche Eingänge der adaptiven Dynamik absichern

Die ergänzte Selbstkantenprüfung testet korrekt, dass eine gültige Maske verbotene Kanten null hält. Sie validiert nicht beliebige vom Aufrufer gelieferte Masken. `hebb_update` mit einer Eins auf der Maskendiagonale kann weiterhin Selbstkanten erzeugen. Das widerlegt die gemeldete Testreparatur nicht; es betrifft eine andere API-Grenze.

Falls diese Helfer als öffentliche API gelten: Maskenform, Diagonale, erlaubte Maskenwerte, nichtnegative endliche Aktivitäten und Gewichte sowie `gamma` prüfen. Andernfalls sie ausdrücklich als interne Helfer mit Vorbedingungen kennzeichnen. Änderungen der unterstützten Eingabedomäne und Änderungen der mathematischen Modellregel getrennt halten.

## 6. Kompakter Reproduktionsblock

Aus dem Repository-Stamm mit der installierten Projektumgebung ausführen. Dieser Block zeigt das **alte Verhalten** am geprüften Commit; er ist kein zukünftiger Grün-Test. Nach den Reparaturen durch gezielte Assertions und erwartete Exceptions ersetzen.

```python
import math
from dataclasses import dataclass
from fractions import Fraction

import numpy as np
from scipy.linalg import expm

from scoped_correspondence.closure.error_bounds import transient_reduction_bound
from scoped_correspondence.observation.directed_information import directed_information
from scoped_correspondence.epistemic.reporting import report_to_json
from scoped_correspondence.validation.conformal import calibrate_split_conformal
from scoped_correspondence.validation.modular_networks.decoders import (
    NearestMeanDecoder, sign_flip_test,
)

# R1: gültiges volles CTMC, allgemeine reduzierte Koordinate.
Q = np.array([[-1., 1.], [0., 0.]])
A = np.array([[0.5, 0.]])
pi0, p0 = np.array([2.]), np.array([1., 0.])
for eps in (0., 1e-20):
    theta = np.array([[eps]])
    result = transient_reduction_bound(
        theta, A, Q, pi0, p0, 1, continuous_time=True,
    )
    actual = np.linalg.norm(pi0 @ expm(theta) @ A - p0 @ expm(Q), 1)
    print("R1", eps, result.bound, actual)
print("R1 independent exact control", 2 * (1 - math.exp(-1)))

# R2: ungültige volle Übergangsmatrix darf keine Markov-Schranke erhalten.
result = transient_reduction_bound(
    [[1.]], [[1., 0.]], [[2., 0.], [0., 1.]], [1.], [1., 0.], 2,
)
print("R2 returned", result.bound, "actual", 3.)

print("R3", sign_flip_test([float("nan"), 1., 1.]))
print("R3 valid controls", sign_flip_test([0, 0, 0]),
      sign_flip_test([1, 1, 1]), sign_flip_test([1] * 5))

print("R4", directed_information({
    ((0,), (0,)): 0.5,
    ((1,), (1,)): float("nan"),
}))

d = NearestMeanDecoder().fit([[0., 0.], [1., 1.]], [0, 1])
print("R5 nonfinite", d.predict([[float("nan"), float("nan")]]))
print("R5 missing feature", d.predict([[0.]]))

@dataclass
class ExampleReport:
    value: float

print("E3", report_to_json(ExampleReport(float("nan"))))
print("E4 float q", calibrate_split_conformal(range(1, 10), 0.7))
print("E4 exact rank", math.ceil(10 * (1 - Fraction(7, 10))))
```

## 7. Arbeitsfolge und Abnahme für Claude-Code

1. Gegenbeispiele R1–R5 unverändert am Ausgangscommit reproduzieren; die genannten Scope-Unterschiede vor dem Editieren prüfen.
2. Reduktionsschranken reparieren: korrekter Nullgrenzfall, numerisch stabile Auswertung, volle Markov-Voraussetzungen, separater TV-Vertrag, korrigierte Quellenfassung. Zugehörige Regressionen ergänzen.
3. Ungültige Eingaben in Sign-Flip-Test, DI/BROJA und Decoder früh ablehnen. Exakte Brüche weiterhin erhalten. Die Ablehnung darf weder einen numerischen Ersatzwert noch eine scheinbare statistische Schlussfolgerung liefern.
4. JSON-Schema und exakte Alpha-Semantik mit dokumentierter Migration umsetzen. Fachlich legitime Unbeschränktheit erhalten.
5. Standardbenchmark erneut ausführen. Für reine Validierungsfixes bei gültigen Eingaben sind unveränderte Ergebnisse zu erwarten. Falls die gepaarte Auswertung aus §5.1 umgesetzt wird, neue Zahlen und geändertes Auswertungsprotokoll ausdrücklich ausweisen.
6. Vollständige vorhandene Regression und Linkprüfung ausführen. Wenige gezielte Mutanten zu R1–R5 ergänzen: Nullgrenzfall wieder entfernen, Endlichkeitsprüfung auslassen, Featurezahlprüfung auslassen. Relevante Kontrollassertions müssen diese Änderungen erkennen.
7. Backlog E und Review-Befunde mit Commit-Verweisen aktualisieren. ON6b bleibt ohne geeignete reale Daten offen. Eine erfolgreiche Reparaturrunde ersetzt kein Volltextaudit anderer offener Themen.
8. Danach neue Merge-Beurteilung. Die Version `0.41.0a1` kann während der Reparatur bestehen bleiben; eine Release-Nummer sollte den tatsächlich zusammengeführten und dokumentierten Stand bezeichnen.

**Abnahme:** Kein reproduzierter Gegenfall liefert weiterhin eine falsche Schranke, einen p-Wert aus nicht endlichen Daten oder eine stillschweigend reparierte Featurematrix. Gültige allgemeine L1-Eingaben bleiben unterstützt. Dokumentation, API-Verhalten und Tests stimmen überein.

## 8. Nachlieferung und Quellen

Das in Backlog A vermisste Begleitskript `independent_controls.py` ist im bereits erstellten Paket `SCF_MYONIUM_UND_KANDIDATEN_CLAUDE_PAKET.zip` enthalten, zusammen mit Ergebnissen und Prüfsummen. Es umfasst die 29 MU-/Kandidaten-Kontrollgruppen. Dies ist eine Artefakt-Nachlieferung und benötigt keine neue Literaturrecherche.

Für die neue Schrankenprüfung wurde die Primärquelle in der korrekten Fassung direkt gelesen:

- Michel & Siegle, *Formal Error Bounds for the State Space Reduction of Markov Chains*, **arXiv:2403.07618v3**, 6. August 2024, insbesondere §2.2 und Theorem 5: https://arxiv.org/html/2403.07618v3
- Versionshistorie und zugehöriger Verlags-DOI: https://arxiv.org/abs/2403.07618 ; https://doi.org/10.1016/j.peva.2024.102464

Die Gegenbeispiele, Grenzfallrechnung und Reparaturempfehlungen in dieser Review wurden eigenständig aus den Funktionen und den angegebenen Matrizen hergeleitet. Es wurde kein neues Volltextaudit der Organoid-Studie oder aller übrigen Backlog-Quellen durchgeführt.
