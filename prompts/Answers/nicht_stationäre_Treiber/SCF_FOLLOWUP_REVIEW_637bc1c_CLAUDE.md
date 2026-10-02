# SCF: Folgereview und Merge-Beurteilung zu 637bc1c

Datum: 1. Oktober 2026. Für Johann und Claude-Code.

**Urteil: bedingtes GO nach zwei eng begrenzten Abschlusskorrekturen.** Die ursprünglichen Gegenbeispiele sind behoben. Es bleiben ein numerischer Randfall im Sign-Flip-Test und eine falsche Aussage über die Rückwärtskompatibilität der Conformal-Ränge. Dafür ist keine neue Roadmap erforderlich.

## 1. Tatsächlich geprüft

- Commit: `637bc1cd36736f51da494f289bc3629548c0f83a`, Branch `j-series`.
- Der [GitHub-Actions-Lauf 36905207646](https://github.com/GenesisAeon/scoped-correspondence-formalism/actions/runs/36905207646) ist erfolgreich; Mathematik-, Realdaten- und Link-Job wurden einzeln überprüft.
- Zum Prüfzeitpunkt: `j-series` liegt 33 Commits vor `master`, keinen dahinter.
- Alle Änderungen an den Produktionsdateien dieses Reparaturcommits wurden gelesen, dazu ausgewählte gezielte Regressionstests und die Backlog-Korrekturen.
- **31 gezielte eigene Kontrollen** gegen die heruntergeladenen Originalfunktionen bestanden. Darunter: beide CTMC-Grenzfälle, ungültige volle Dynamik, separater TV-Vertrag, nicht endliche Eingaben, Decoder-Dimensionen, exakte Alpha-Eingaben, verschachteltes JSON und ungültige Hebb-Maske.
- Der vollständige voreingestellte ON-Benchmark mit sechs Läufen und sieben Bedingungen wurde erneut ausgeführt.
- Die komplette Suite mit gemeldeten 139 Skripten und die Mutationstest-Registry wurden lokal nicht noch einmal ausgeführt. Die erfolgreichen CI-Jobs wurden direkt bestätigt; die Zahl 115/116 Mutanten wird hier nicht als eigener Wiederholungslauf ausgegeben.
- Kein Merge, keine Veröffentlichung und keine Produktionsänderung durch diese Review. Die Beurteilung ist auf den Reparaturcommit und die benannten Aufrufpfade begrenzt, keine erneute Vollprüfung der gesamten J-Serie.

## 2. Bestätigter Abschluss der ursprünglichen Befunde

| Punkt | Ergebnis der Nachprüfung |
|---|---|
| R1: CTMC-Nullgrenzfall | Für `Theta=0` und `Theta=1e-20` liefert der ursprüngliche Gegenfall jetzt Schranke 2 statt 0. Der allgemeine L1-Modus bleibt erhalten. |
| R2: volle Dynamik und TV | Nicht stochastisches `P`, ungültiges `Q` und unzulässiger TV-Vertrag werden abgelehnt. Die stationäre allgemeine L1-Ungleichung wurde sinnvoll separat behandelt. |
| R3: NaN-p-Wert | NaN, ±∞ und bool werden abgelehnt; die bisherigen exakten Kontrollwerte stimmen. Siehe den zusätzlichen Ganzzahlrandfall F1 unten. |
| R4: Informationsmaße | DI und BROJA lehnen nicht endliche Massen früh ab. Die dokumentierte Gewichtsnormalisierung bleibt bestehen. |
| R5: Decoder | Fehlender Fit, NaN und falsche Featurezahl werden abgewiesen; eine leere Matrix mit korrekter Featurezahl ist ausdrücklich zulässig. |
| E3: JSON | ±∞ erhalten explizite Marker, verschachteltes NaN wird abgewiesen. |
| E4: Alpha | `Fraction(7,10)` und `"0.7"` ergeben im Kontrollfall q=3, Float `0.7` ergibt q=4. Die allgemeine Kompatibilitätsaussage muss korrigiert werden, siehe F2. |
| §5: Auswertungsprotokoll | Beide Decoder verwenden jetzt denselben späteren Testsatz. Die Featurepermutationskontrolle wurde ergänzt. |

Erneut erhaltene Konfigurations-ID: **`e5017540ea171f9d`**.

Ausgewählte reproduzierte Benchmarkwerte:

| Bedingung | Δ, neu trainiert | Accuracy nachher, neu trainiert | Accuracy nachher, eingefroren |
|---|---:|---:|---:|
| M3, getrennte Eingänge, Anpassung | −0,091908092 | 0,908091908 | 0,593554594 |
| M1, gleichförmiger Operator | 0,355584231 | 0,883681134 | 0,507575758 |
| M3, c=8/11, identischer Operator | 0,355584231 | 0,883681134 | 0,507575758 |
| M3, Sensorumordnung, feste Gewichte | 0 | 1 | 0,658369408 |

Die Aussage über unveränderte Δ- und neu trainierte Werte ist damit nachvollziehbar. Die Änderung der eingefrorenen Scores wird durch das geänderte gepaarte Protokoll erklärt und sichtbar versioniert.

## 3. F1 — P2: NumPy-Ganzzahlen laufen im Sign-Flip-Test über

**Ort:** `src/scoped_correspondence/validation/modular_networks/decoders.py`, `_finite_real` um Zeile 184 und `sign_flip_test` um Zeile 207.

Der Validator lässt `np.integer` ausdrücklich zu, gibt den Wert aber unverändert zurück. Dadurch werden Summen und Vorzeichenprodukte mit begrenzter NumPy-Ganzzahlarithmetik ausgeführt. Das widerspricht der zugesagten Behandlung exakter Ganzzahlen.

Reproduktion am geprüften Commit:

```python
from fractions import Fraction
import numpy as np
from scoped_correspondence.validation.modular_networks.decoders import sign_flip_test

v = 2**62
print(sign_flip_test([v, v, v]))                       # 1/4, korrekt
print(sign_flip_test(np.array([v, v, v], np.int64)))   # 1, falsch
```

Unabhängige Herleitung: Bei drei gleichen positiven Differenzen haben nur die Muster `+++` und `---` den maximalen absoluten Summenwert. Zwei von acht Vorzeichenmustern ergeben daher **p=1/4**. Die Größe der gemeinsamen positiven Skala darf das Ergebnis nicht ändern.

**Minimaler Fix:** NumPy-Ganzzahlen vor jeglicher Addition, Multiplikation oder Betragsbildung in unbegrenzte Python-`int` umwandeln. Den Bool-Ausschluss vorher beibehalten, `Fraction` nicht in Float verwandeln.

```python
if isinstance(d, (bool, np.bool_)):
    raise ScopeViolationError(...)
if isinstance(d, np.integer):
    return int(d)
if isinstance(d, (int, Fraction)):
    return d
```

Eine isolierte lokale Gegenprobe mit genau dieser Konvertierung ergab für dreifach gleiche Werte jeweils korrekt `1/4`: `np.int64(2**62)`, `np.int64(2**63-1)`, `np.int64(-2**63)` und `np.uint64(2**64-1)`. Dabei wurde keine Produktionsdatei verändert.

**Abnahme:** Der ursprüngliche Gegenfall und diese Typgrenzen stimmen mit der Python-int-Referenz überein. Gemischte Vorzeichen und vorhandene Fraction-/NaN-Kontrollen bleiben korrekt. Ein gezielter Mutant, der die Konvertierung auslässt, wird erkannt.

**Reichweite:** Dies ist ein Fehler der allgemein zugänglichen numerischen API. Die üblichen begrenzten Accuracy-Differenzen des ON-Benchmarks sind davon nicht betroffen. Der ursprüngliche NaN-Fix bleibt richtig.

## 4. F2 — P2: Float-Ergebnisse von Conformal sind nicht allgemein unverändert

**Ort:** `validation/conformal.py`, exakte Rangberechnung; falsche Kompatibilitätsaussage in `DEEP_RESEARCH_BACKLOG.md`, Abschnitt E, insbesondere die Aussage zum Scan `n <= 59`.

Die alte Funktion berechnete Subtraktion und Multiplikation als Float, bevor sie `ceil` anwendete. Die neue Funktion interpretiert den Float zunächst als exakten Binärbruch und rechnet danach exakt. Das ist eine nachvollziehbare Semantik, aber kein allgemein identisches Verhalten.

Direkter Vergleich der Originalfunktionen aus `6b3a331` und `637bc1c`, jeweils mit Residuen `1,...,n`:

| n | Alpha als Float | q vorher | q jetzt |
|---:|---:|---:|---:|
| 9 | 0.3 | 7 | 8 |
| 19 | 0.15 | 17 | 18 |
| 9 | 0.7 | 4 | 4 |

Beide geänderten Fälle liegen bereits innerhalb von `n <= 59`. Der unveränderte Einzelkontrollfall `0.7` reicht nicht als Kompatibilitätsnachweis.

Herleitung für `0.3`: Der exakte Wert dieses Floats ist

\[
5404319552844595/18014398509481984 < 3/10.
\]

Damit liegt `10 * (1 - Fraction(0.3))` echt oberhalb von 7 und der neue Rang ist 8. Die alte Float-Multiplikation rundete auf 7. Mit dem ausdrücklich dezimal gemeinten String `"0.3"` ist der Rang weiterhin 7.

**Empfehlung:** Die neue, dokumentierte Binärwert-Semantik beibehalten. Die neue Rechnung ist in diesen Beispielen nicht falsch. Korrigiert werden müssen die Aussage über unverändertes Verhalten und der bisher unzureichende Kompatibilitätstest.

**Konkrete Aufgaben:**

1. Backlog und Migrationshinweis berichtigen: Bestimmte Float-Eingaben ändern ihren Rang gegenüber der vorherigen gerundeten Zwischenrechnung.
2. Die zwei zusätzlichen Fälle als Regression aufnehmen: Float `0.3 -> 8`, String `"0.3" -> 7`; Float `0.15 -> 18`, String `"0.15" -> 17`, jeweils bei dem genannten n.
3. Betroffene Conformal-Aufrufer anhand ihrer tatsächlich verwendeten Alpha-Werte und Kalibriergrößen prüfen. Etwaige Änderungen veröffentlichter Resultate dokumentieren; keine Beeinträchtigung behaupten, bevor sie nachgewiesen wurde.
4. Dezimal gewünschte Konfidenzniveaus in neuen Konfigurationen ausdrücklich als String oder Fraction angeben. Kein Epsilon vor `ceil` einführen.

Minimaler Kontrollblock für die neue Semantik:

```python
from scoped_correspondence.validation.conformal import calibrate_split_conformal

assert calibrate_split_conformal(range(1, 10), 0.3) == 8
assert calibrate_split_conformal(range(1, 10), "0.3") == 7
assert calibrate_split_conformal(range(1, 20), 0.15) == 18
assert calibrate_split_conformal(range(1, 20), "0.15") == 17
```

## 5. Entscheidungsempfehlung: strikter PMF-Modus

**Ja, als zusätzlich wählbaren Modus.** Der bisher dokumentierte Gewichtsmodus sollte vorerst der Standard bleiben. Eine optionale Keyword-Erweiterung muss bestehende Aufrufe nicht brechen und braucht keinen unmittelbaren Wechsel des Standardverhaltens.

Vorgeschlagene Oberfläche für DI und BROJA:

```python
input_mode="weights"   # bestehendes Verhalten, Standard
input_mode="pmf"       # verlangt eine normierte Wahrscheinlichkeitsverteilung
```

- Beide Modi prüfen Endlichkeit, Vorzeichen, Dimensionen und positive Gesamtmasse.
- `weights`: Normierung ist ausdrücklich gewollt. Eine Multiplikation aller gültigen Gewichte mit demselben positiven Faktor soll innerhalb des unterstützten numerischen Bereichs die Informationswerte erhalten.
- `pmf`: Falsch summierte Eingaben werden außerhalb einer dokumentierten Toleranz abgelehnt. Exakte Eingaben und Float-Toleranzen dürfen nicht still verwechselt werden.
- Falls innerhalb der Float-Toleranz technisch nachnormiert wird, diesen Umstand und die ursprüngliche Gesamtmasse in der Dokumentation bzw. den Berichtsmetadaten kenntlich machen.
- Pflichtkontrollen: normierte Verteilung, dieselbe Verteilung mit doppelter Masse, Nullmasse, negative und nicht endliche Werte sowie vorhandene Informations-Kontrollfälle.

Diese Erweiterung ist eine sinnvolle nächste Aufgabe, **keine zusätzliche Merge-Bedingung für die bereits reparierten Befunde**. Bestehende strikte ON-Adapter bleiben vorerst ausreichend für ihre eigenen Aufrufpfade.

## 6. Begrenzter Abschlussauftrag

1. F1 und F2 am genannten Commit unabhängig reproduzieren.
2. F1 mit Python-int-Konvertierung beheben; F2 durch präzise Migrationsdokumentation, Grenzfalltests und Prüfung tatsächlich betroffener Aufrufer abschließen.
3. Vorhandene Regression und Links gemäß `CLAUDE.md` ausführen, Ergebnisse in einem Review-Fix-Commit festhalten.
4. Bei grünem Ergebnis und ohne neue Auswirkung auf veröffentlichte Resultate besteht **aus dieser gezielten Folgereview kein verbleibender Einwand gegen die Übernahme von j-series**.

ON6b und die nicht anwendbaren bzw. noch nicht an Produktionsfunktionen anschließbaren Oracle-Gruppen dürfen sichtbar offen bleiben. Eine Merge-Beurteilung setzt nicht voraus, dass jede zurückgestellte Forschungsfrage gelöst wird. Die Versions- und Release-Entscheidung bleibt davon getrennt.
