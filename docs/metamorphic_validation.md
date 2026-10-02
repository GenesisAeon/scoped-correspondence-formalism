# Metamorphe Prüfungen und gezielte Fehlermutationen (J3)

Paket J3 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §9. Code: `scripts/run_targeted_mutations.py`; Prüfungen:
`verification/verify_metamorphic_relations.py`,
`verification/verify_targeted_mutation_runner.py` (beide math). Lizenz der
Dokumentation: CC BY 4.0.

Ziel ist der Nachweis, dass wichtige Prüfungen **relevante Fehler
tatsächlich entdecken** — keine globale Mutation aller Dateien und kein
eigenes Testframework.

## 1. Metamorphe Relationen

Eine metamorphe Prüfung vergleicht Ergebnisse unter einer
Transformation, deren Wirkung mathematisch feststeht. Jede Relation
steht mit ihrer Begründung im Prüfskript.

| ID | Relation | Begründung | Status |
|---|---|---|---|
| MR1 | Einheitenwechsel Jahr→Tag (und weitere Faktoren) am linearen Reservoir, 50 zufällige exakte Parametersätze | $q/k$ und $kt$ sind exakt invariant (J-C04) | aktiv |
| MR2 | gleichzeitige Permutation von Mikrozuständen, Makroklassen und Aktionsnamen bei `check_controlled_correspondence` | reine Umbenennung: Exaktheit und Defektgröße bleiben gleich; exakte und nicht exakte Fälle kommen beide vor | aktiv |
| MR3 | Identität und Assoziativität von Korrespondenzen über `t4_composition_residual` | mit $T_2=\mathrm{id}$, $a_2=1$ ist $r_{12}=r_1$; beide Klammerungen dreier linearer Abbildungen ergeben dieselbe direkte Abweichung, und die T4-Identität (`direct = composed`) gilt für jede Klammerung | aktiv |
| MR4 | A/B-Tausch im Prognosevergleich (20 zufällige Designs) | $d_t$ wechselt das Vorzeichen; die HAC-Varianz ist eine quadratische Form | aktiv |
| MR5 | Split-Conformal-Quantil: Permutation und positive Skalierung der Kalibrierresiduen | Ordnungsstatistik einer Multimenge; positive Homogenität | aktiv |
| MR6 | gemeinsame positive Skalierung der Conformal-Gewichte | Normierung kürzt sich | **ausstehend, aktiviert mit J8** |
| MR7 | Vertauschung unabhängiger Sobol-Eingänge samt Etiketten | Indizes sind etikettengebunden | **ausstehend, aktiviert mit J7** |
| MR8 | Umbenennung von SCM-Variablen samt Eingriffen | reine Umbenennung | **ausstehend, aktiviert mit J9** |

Ausstehende Relationen werden ausdrücklich ausgegeben und **nicht** als
bestanden gezählt. Den vollständigen vereinbarten Satz verlangt J12.

**Korrektur während J3:** MR3 prüfte zunächst nur die direkten
Abweichungen, nicht die T4-Identität selbst. Der als Ziel eingetragene
Mutant „Zeitfaktor in T4 entfernt“ wäre von MR3 damit nicht erfasst
worden. Ergänzt um `r.value` (= |direct − composed|) für jede Klammerung.

## 2. Gezielter Mutationslauf

`scripts/run_targeted_mutations.py` enthält ein explizites Register:
je Mutant Datei, exakter Suchtext, Ersetzung, Zielprüfungen, erwartete
Wirkung und das Paket, dessen Prüfungen ihn fangen sollen. Jeder Mutant
läuft auf einer **temporären Kopie** von `src/`, `verification/` und
`data/`. Die mutierten Quelldateien im echten Arbeitsbaum werden vor und
nach dem Lauf gehasht; jede Abweichung bricht ab.

| Ausgang | Bedeutung |
|---|---|
| `killed` (`assertion`) | eine Zielprüfung meldete einen Fehlschlag |
| `killed` (`error`) | nur ungefangene Exception (Absturz) — berichtet, aber schwächerer Beleg |
| `survived` | alle Zielprüfungen bestanden weiter |
| `invalid` | Suchtext nicht genau einmal gefunden, mutierte Datei nicht kompilierbar oder unmutierte Basislinie einer Zielprüfung bereits rot — **kein** Fehlernachweis |
| `timeout` | Zeitlimit überschritten — kein Fehlernachweis |
| `equivalent_or_unresolved` | überlebt, aber **vorab** mit Begründung als möglicherweise äquivalent registriert; außerhalb des Nenners, separat gelistet |

Ein hoher Anteil erkannter Mutanten ist **keine
Vollständigkeitsgarantie**.

### Planpflichtige Fehlerklassen (Plan §9)

| Klasse | Mutant | Status |
|---|---|---|
| Ungleichung umdrehen | `tv_comparison_inequality_inverted`, `j1_series_too_short_inverted` | im Register |
| Zeitfaktor in T4 entfernen | `t4_time_factor_removed` | im Register |
| Lipschitzfaktor entfernen | — | **aktiviert mit J4** (Flussfehlerkomposition) |
| Testpunktmasse bei Conformal weglassen | `conformal_test_point_mass_dropped` (bestehendes `conformal.py`, $n+1\to n$) | im Register; gewichtete Variante mit J8 |
| Faktor zwei bei TV/L1 | `tv_l1_factor_two` | im Register |
| Scope-Verträglichkeit umgehen | — | **aktiviert mit J4** |

Dazu kommen die Mutanten der Pakete J1 (7) und J2 (8).

### Zwei Fehler im Runner selbst, gefunden durch seinen eigenen Test

`verify_targeted_mutation_runner.py` baut ein Wegwerf-Spielrepository
und prüft jede Ausgangsklasse. Das deckte vor dem ersten Commit auf:

1. **Veralteter Bytecode:** Die Basisläufe schreiben `.pyc`-Dateien. Eine
   Mutation gleicher Länge (`2 * x` → `1 * x`, ebenso `<=` → `>=`), die in
   derselben Sekunde geschrieben wird, besteht Pythons
   mtime+Größe-Prüfung; ausgeführt wird dann der **unmutierte**
   Bytecode — ein falsches `survived`. Behoben mit
   `PYTHONDONTWRITEBYTECODE=1` für alle Kindprozesse. Der Fehler kann nur
   falsche Überlebende erzeugen, nie falsche Erkennungen; frühere
   „erkannt“-Ergebnisse bleiben gültig.
2. **Zu grobe Fehlereinstufung:** Ältere Prüfskripte melden
   Fehlschläge als JSON (`"failed": [...]`) statt mit `FAIL`-Zeilen und
   wurden als Absturz eingestuft. Jetzt gilt: `error` nur bei
   ungefangener Exception (Traceback), jeder andere Exit ≠ 0 ist ein
   gemeldeter Fehlschlag.

## 3. Ergebnis

Siehe Roadmap-Abschnitt J3 und
`verification/targeted_mutations_report.json` (Lauf auf dem J3-Stand).
Der Mutationslauf ist bewusst **nicht** Teil der schnellen Suite
(`--category all`), weil jeder Mutant vollständige Prüfskripte ausführt;
sein Selbsttest dagegen schon.

## 4. Quelle

S06 Chen et al. (2018), *Metamorphic Testing: A Review of Challenges and
Opportunities* — Links siehe Plan §21; der konkrete SCF-Mutationskatalog
ist eigener Entwurf.
