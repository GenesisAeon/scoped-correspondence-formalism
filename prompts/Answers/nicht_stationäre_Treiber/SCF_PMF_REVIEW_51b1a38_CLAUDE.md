# SCF: Abschlussprüfung F1/F2 und Review des neuen PMF-Modus

Stand: 1. Oktober 2026. Geprüfter Commit: `51b1a38e563c3f99f06cb4955a0da99d39450d26` auf `j-series`.

## Urteil

**Die bisherigen Merge-Bedingungen F1 und F2 sind erfüllt.** Im danach hinzugekommenen optionalen PMF-Paket wurden zwei neue, begrenzte Befunde reproduziert. Für den aktuellen Branch empfehle ich deren Behebung vor der Übernahme. Die abgeschlossene vorherige Reparatur wird dadurch nicht wieder geöffnet.

Kein Merge und keine Änderung am Repository wurden durch diese Review vorgenommen. Produktionsdateien wurden am angegebenen Commit gelesen und in einer separaten lokalen Momentaufnahme ausgeführt.

## 1. Bestätigter Stand

- [GitHub Actions für 51b1a38](https://github.com/GenesisAeon/scoped-correspondence-formalism/actions/runs/36911353592): Mathematik-, Realdaten- und Link-Job erfolgreich. Die Workflow-Datei verwendet **Python 3.11**.
- F1: Dreifach gleiche NumPy-Ganzzahlen liefern jetzt korrekt `p=1/4`, geprüft für `int64(2**62)`, `int64` Maximum und Minimum sowie `uint64` Maximum.
- F2: Eigene vollständige Wiederholung über 99 Alpha-Werte und n=1…1000 ergibt **825 Rangänderungen: 764 nach oben, 61 nach unten, bei 32 Alpha-Werten**. Die neue Rangformel ist jeweils der kleinste ganzzahlige Rang oberhalb der exakten Schwelle für den übergebenen Binärwert.
- Die Beispiele `0.3 -> 8`, `"0.3" -> 7`, `0.15 -> 18`, `"0.15" -> 17` und `0.44, n=24 -> 14` stimmen.
- Die statistische Abdeckungsaussage bleibt an die Voraussetzungen von Split Conformal, insbesondere Austauschbarkeit, gebunden. Eine korrekte Rangberechnung allein garantiert keine Abdeckung bei beliebiger Drift.
- Der neue PMF-Modus ist sinnvoll als optionale Erweiterung; der Gewichtsmodus bleibt Standard.
- Die vollständige lokale 140-Skript-Suite und die Mutationstest-Registry wurden hier nicht erneut ausgeführt. Das neue Skript `verify_information_input_modes.py` wurde dagegen tatsächlich ausgeführt; Ergebnis unter **Python 3.12.14: eine von zwei Prüfgruppen bestanden**, siehe PMF2.

## 2. PMF1 — Priorität P2: negative exakte Masse wird im strikten PMF-Modus akzeptiert

Betroffene Dateien:

- `src/scoped_correspondence/observation/directed_information.py`, `_normalize_joint`, `_input_total` und `directed_information`.
- `src/scoped_correspondence/information_decomposition/broja.py`, `_validate_joint`, `_input_total` und `broja_pid_bivariate`.

Der neue Modus prüft die Original-Gesamtmasse, verwendet für die Vorzeichenprüfung aber weiter die bisherigen toleranten Validatoren. Kleine negative Massen werden dort entfernt bzw. auf null gesetzt. Daher genügt eine exakt normierte **signierte** Masse, um den strikten PMF-Vertrag zu passieren.

### Reproduktion am geprüften Commit

```python
from fractions import Fraction as F
from scoped_correspondence.observation.directed_information import directed_information
from scoped_correspondence.information_decomposition.broja import broja_pid_bivariate

eps = F(1, 10**15)
j = {
    ((0,), (0,)): F(1, 2),
    ((1,), (1,)): F(1, 2) + eps,
    ((0,), (1,)): -eps,
}
assert sum(j.values()) == 1
assert min(j.values()) < 0
di = directed_information(j, input_mode="pmf")
print(di.input_mode, di.input_total_mass, di.I_directed)
# aktuell: pmf 1.0 1.0

joint = [
    [[F(1, 2), -eps], [0, 0]],
    [[0, 0], [0, F(1, 2) + eps]],
]
pid = broja_pid_bivariate(joint, input_mode="pmf")
print(pid.input_mode, pid.input_total_mass, pid.redundancy, pid.converged)
# aktuell: pmf 1.0 1.0 True
```

**Erwartet:** Beide Aufrufe werfen `ScopeViolationError`. Exakte Normierung ersetzt nicht die Nichtnegativität einer Wahrscheinlichkeitsverteilung.

### Begrenzte Reparatur

1. Im PMF-Modus die **unveränderten Originalmassen** auf Nichtnegativität prüfen, bevor Clipping, Entfernen von Atomen oder Normierung als gültige PMF-Verarbeitung akzeptiert werden.
2. `Fraction`-Vorzeichen ohne vorherige Float-Konvertierung prüfen. Sonst könnte ein sehr kleiner negativer Bruch zu `-0.0` unterlaufen und erneut durchrutschen.
3. Die Toleranz für die Float-**Gesamtsumme** bleibt getrennt von der Vorzeichenprüfung. Nicht ohne ausdrücklichen Vertrag auf Einzelmassen übertragen.
4. Den bestehenden Gewichtsmodus für diesen Fix nicht unnötig ändern. Falls er weiterhin kleine negative Werte toleriert, die Aussage „beide Modi lehnen alle negativen Werte ab“ entsprechend präzisieren.
5. Die bisherigen R4-Tests und Mutanten zur frühen Ablehnung nicht endlicher Werte erhalten. Eine redundant gewordene Validierungsstelle wäre nicht allein ein mathematischer Fehler; die Tests müssen die zugesagten Verhaltensweisen absichern.

**Pflichtkontrollen:** obige Gegenfälle für DI und BROJA; negative Float-Masse `-1e-15`; exakter negativer Bruch mit Float-Unterlauf, etwa `-F(1,10**400)`; gültige exakte Drittel; gültige Float-PMF; doppelte Gesamtmasse; bestehende NaN-/Inf-Kontrollen. Ein PMF-spezifischer Mutant, der die strikte Vorzeichenprüfung entfernt, soll erkannt werden.

Reichweite: Die numerische Änderung im Beispiel ist klein; der Befund betrifft die falsche Annahme einer exakt gültigen Eingabeverteilung. Eine Beeinträchtigung der veröffentlichten ON-Benchmarkwerte wurde damit nicht nachgewiesen.

## 3. PMF2 — Priorität P2: neue Prüfung hängt vom Summationsalgorithmus der Python-Version ab

**Ort:** `verification/verify_information_input_modes.py`, Zeile 75:

```python
require(len(tenths) == 10 and sum(tenths.values()) != 1.0,
        "float tenths do not sum to exactly 1.0 in binary")
```

Unter dem hier eingesetzten Python **3.12.14** gilt:

```python
sum([0.1] * 10)       # 1.0
```

Deshalb ergibt der unveränderte Aufruf

```text
python verification/verify_information_input_modes.py
FAIL di_modes: float tenths do not sum to exactly 1.0 in binary
PASS broja_modes
1/2 checks passed
```

`pyproject.toml` erlaubt `requires-python = ">=3.10"`. Der Fehler liegt somit innerhalb des deklarierten Versionsbereichs. Die grüne CI unter Python 3.11 widerspricht dieser Reproduktion nicht.

Python hat die Float-Summation von `sum` ab 3.12 auf einen genaueren Algorithmus umgestellt. Primärquelle: [Python 3.12, Built-in Functions, sum](https://docs.python.org/3.12/library/functions.html#sum).

Die exakte rationale Summe der zehn gespeicherten Binärwerte ist zwar

\[
10\,\mathrm{Fraction}(0.1)=18014398509481985/18014398509481984>1,
\]

doch daraus folgt nicht, dass das gerundete Ergebnis von `sum` ungleich 1 sein muss.

### Reparatur und sinnvollere Toleranzkontrolle

- Die Anzahl der zehn Atome weiter prüfen. Die Behauptung über den konkreten Rückgabewert von `sum` entfernen.
- Falls die binäre Darstellung erklärt werden soll, sie mit `sum(F(v) for v in tenths.values()) != 1` exakt prüfen; dies ist eine andere Aussage als die bisherige Float-Assertion.
- Für den eigentlichen Toleranzvertrag bewusst eine gut darstellbare Abweichung verwenden: Massen `0.5` und `0.5 + 2**-42` liegen insgesamt innerhalb von `1e-12` und müssen akzeptiert werden. `0.5` und `0.5 + 2**-38` liegen außerhalb und müssen abgelehnt werden. Beide Verhaltensweisen wurden mit der bestehenden DI-Produktion bestätigt.
- Mindestens dieses neue Skript zusätzlich unter Python 3.12 ausführen. Ein kleiner CI-Vergleich für 3.11 und 3.12 verhindert genau diese erneute Lücke; eine beliebig große Testmatrix ist hierfür nicht nötig.

## 4. Übergabe und Versionsentscheidung

1. Die zwei PMF-Befunde unabhängig reproduzieren.
2. Strikte Vorzeichenprüfung und versionsunabhängige Testannahme korrigieren; die zugesagten bestehenden Modi erhalten.
3. PMF-Skript unter Python 3.11 und 3.12 prüfen, danach die vorhandene vollständige Regression und Linkprüfung gemäß `CLAUDE.md`.
4. Ein begrenzter Review-Fix-Commit für dieses neue Paket genügt. Die vorherigen F1-/F2-Befunde bleiben abgeschlossen.

**Versionsempfehlung:** Nach Zusammenführung des reparierten Gesamtstands ist **`0.42.0a1`** eine plausible nächste Alpha-Version: neue Fähigkeiten und eine dokumentierte Änderung der Conformal-Semantik verdienen eine unterscheidbare Versionskennung. Metadaten, Versionsangaben und Release-Notizen gemeinsam aktualisieren; ein Merge muss nicht zugleich eine Paketveröffentlichung sein. Bis dahin kann `0.41.0a1` bestehen bleiben.

Die offenen Realdaten- und Literaturfragen bleiben ausdrücklich dokumentierte Forschungsgrenzen. Sie sind keine neuen Merge-Bedingungen dieser Review.
