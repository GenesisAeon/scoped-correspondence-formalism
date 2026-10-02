# Gemeinsame Sensitivität statt einzelner Parameterbewegungen (J7)

Paket J7 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §13. Code: `src/scoped_correspondence/validation/global_sensitivity.py`
(Sobol-Kern, Szenarienraster), `.../galaxy_joint_sensitivity.py`
(Galaxienanschluss). Prüfungen: `verification/verify_global_sensitivity.py`
(math), `verification/verify_galaxy_joint_sensitivity.py` (data, lokale
SPARC-Dateien). Lizenz der Dokumentation: CC BY 4.0.

## 1. Zuerst das Unsicherheitsmodell

Vier Dinge bleiben getrennt:

| Begriff | Umsetzung | Was daraus **nicht** folgt |
|---|---|---|
| Szenarienraum | `JointScenarioGrid` (volles Raster deklarierter Werte, mit Herkunft je Eingang) | keine Wahrscheinlichkeit; Häufigkeiten von „Siegern“ sind keine empirischen Wahrscheinlichkeiten |
| Eingangsverteilung | `InputSpec` je Eingang, nur **unabhängige** Marginale | keine abhängigen Eingänge (dafür bräuchte es eine andere Zerlegung, S12) |
| Mess- vs. Modellunsicherheit | `InputSpec.kind` + Pflichtfeld `provenance` | keine erfundenen Fehlerbalken: Unbekanntes wird als Szenario deklariert |
| Zielgröße | vom Aufrufer gewählt | — |

## 2. Sobol-Kern

Erste und totale Indizes mit Pick-Freeze-Schätzern (Matrizen $A$, $B$,
$A_B^{(i)}$ mit Spalte $i$ aus $B$):
$\hat S_i=\overline{f(B)(f(A_B^{(i)})-f(A))}/\hat V$,
$\hat S_{T_i}=\overline{(f(A)-f(A_B^{(i)}))^2}/(2\hat V)$, $\hat V$ als
Stichprobenvarianz (Divisor $N-1$) aller $f(A),f(B)$. Endliche Schätzungen
dürfen außerhalb $[0,1]$ liegen und werden **nicht** beschnitten;
Standardfehler werden mitgeliefert. Konstante Ausgabe: `undefined_zero_variance`
(nicht 0). `independent=False`: `unsupported`.

Exakte Referenz: `analytic_sobol_polynomial` für Polynome in unabhängigen
$U[0,1]$-Eingängen (rational).

**J-C14:** $X+2Y$: $V=5/12$, $S=S_T=(1/5,4/5)$; $XY$: $V=7/144$,
$S=(3/7,3/7)$, $S_T=(4/7,4/7)$, reine Interaktion $1/7$. Der Schätzer
(Seed 7, $N=40000$) trifft die exakten Werte innerhalb weniger eigener
Standardfehler — exakte Gleichheit wird nicht verlangt.
**Negativkontrolle $Y=X$:** Wird das Einparametermodell $f=2X$ fälschlich
als $X+Y$ mit unabhängigem $Y$ behandelt, verteilt Sobol die Varianz
$1/2:1/2$ und unterschätzt sie ($1/6$ statt $1/3$) — ein Artefakt der
falschen Unabhängigkeitsdeklaration. **MR7:** Vertauschen der Eingänge
samt Etiketten permutiert die Indizes.

## 3. Galaxienpilot: gemeinsame Szenarien

Der bestehende Pilot variierte $D$ und $i$ **einzeln**
(`distance_inclination_sensitivity_mode_b`). Neu ist ein **gemeinsames**
Raster über $D$, $i$, $\Upsilon_{\rm disk}$, $\Upsilon_{\rm bul}$:
`joint_holdout_sensitivity` wendet je Punkt dieselbe physikalische
Transformation auf Trainings- **und** Testradien aller Modelle an (Radien
und baryonische Beiträge mit $D$, beobachtete Geschwindigkeit und Fehler
mit $i$ — dieselben Funktionen wie der bestehende Adapter), fittet nur auf
den transformierten Trainingsradien neu und bewertet auf den gehaltenen
Außenradien über den unveränderten `evaluate_baselines_on_holdout`-Pfad.
`galaxy_pilot.py` wurde nicht verändert (additiv, `CLAUDE.md`). Primäre
Zielgröße ist die **Differenz** der gehaltenen Verluste; Szenarien, in
denen ein Modell ungültige Testpunkte hat, werden gezählt, nicht still
entfernt. $a_0$ wird nicht gefittet.

**Ergebnis auf den lokalen SPARC-Dateien** (hashgeprüft, nicht
eingecheckt; erste Auswertungsgalaxie der eingefrorenen Auswahl,
NGC3109): Raster $D\in\{-1,0,1\}\sigma_D$, $i\in\{-1,0,1\}\sigma_i$
(Katalogfehler), $\Upsilon_{\rm disk}\in\{0{,}4;0{,}5;0{,}6\}$
(deklarierte Modellvarianten, kein gemessener Fehler),
$\Upsilon_{\rm bul}=0{,}7$. Alle 27 Szenarien vergleichbar; die Differenz
RMSE(MOND) − RMSE(Burkert) liegt zwischen $+4{,}8$ und $+12{,}7$ km/s,
Burkert ist in allen 27 Szenarien besser. **Lesart:** Der
Modellvorteil dieser einen Galaxie ist über den deklarierten
Szenarienraum vorzeichenstabil. Das ist weder eine Wahrscheinlichkeit
noch eine Populationsaussage noch ein Beleg für eine bestimmte
Halo-Physik; Unterschiede der Flexibilität (Burkert fittet zwei
Parameter, MOND keinen) zeigen sich im Testfehler und werden nicht
nachträglich pauschal abgezogen (Plan §2.1). Lizenzstatus der
SPARC-Daten: unverändert ungeklärt (lokaler Weg wie bisher).

## 4. Quellen

S11 Saltelli et al. (2010), S12 Kucherenko et al. (2012) — Links siehe Plan
§21; Schätzerkonventionen oben vollständig ausgeschrieben. Ein
Volltextabgleich der Normierungskonventionen steht in
[`DEEP_RESEARCH_BACKLOG.md`](../DEEP_RESEARCH_BACKLOG.md).
