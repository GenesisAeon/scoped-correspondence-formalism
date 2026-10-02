# Bereichsverträge, Verfeinerung und Komposition (J4)

Paket J4 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §10. Code: `src/scoped_correspondence/assurance/records.py`,
`src/scoped_correspondence/correspondence/domains.py`,
`.../contracts.py`, `.../composition.py`. Prüfung:
`verification/verify_correspondence_contracts.py` (math). Die bestehenden
Objekte in `correspondence/contract.py` (`Scope`, `Correspondence`,
`t4_composition_residual`) bleiben unverändert. Lizenz der Dokumentation:
CC BY 4.0.

## 1. Berichte: `ProofReport`

Neben `epistemic.records.ClaimReport` (endliche Domänen) trägt
`ProofReport` getrennte Achsen: Urteil (`proved`, `refuted`, `undecided`,
`undefined_on_domain`, bei Stichproben `observed_pass`/`observed_fail`),
Verfahrensstatus (`completed`, `budget_exhausted`, `invalid_input`,
`unsupported_structure`, `numerical_failure`, `incompatible`),
Evidenzart und Empiriestatus (Vokabulare aus `epistemic.records`
importiert), Arithmetik, `empty_domain`, `conclusion_complete` vs.
`domain_exhausted`, Zeugen und Abhängigkeiten.

Erzwungene Invarianten: `proved` nur mit `completed`; ein Budgetabbruch
beweist nie; eine numerische Stichprobe trägt nie `proved`. JSON mit
`allow_nan=False`, Brüche exakt. `certificate_id` ist ein Inhaltshash —
er **identifiziert**, er **beweist nicht**. Der Adapter
`proof_report_from_claim_report` referenziert bestehende endliche
Audits, ohne sie umzudeuten.

## 2. Unterstützte Bereiche

| Klasse | Universelle Aussagen |
|---|---|
| `FiniteSet` | exakt durch Aufzählung (`exhaustive_finite`) |
| `RationalBox` (achsenparallel, rational; leer wenn $lo>hi$) | exakt über Grenzvergleich |
| `HalfspaceSet` (Box ∩ lineare Ungleichungen) | Box ⊆ Polyeder exakt über Ecken; Polyeder ⊆ … ist `unsupported` |
| `OpaquePredicate` | nur Punktmitgliedschaft; nie eine universelle Inklusion |

`preimage_constraint(T, D2, D1)` berechnet $D_1\cap T^{-1}(D_2)$
**exakt**. Hängt jede Ausgabekoordinate von höchstens einer Eingabe ab,
ist das Ergebnis wieder eine Box (negative Skalen werden korrekt
gespiegelt, konstante Ausgaben ergeben ganz oder leer). Sonst bleibt
das Urbild als `HalfspaceSet` symbolisch erhalten und wird **nie** still
durch eine größere Box ersetzt.

**Anfangszustand vs. Trajektorie:** Aus $x_0\in D$ folgt nicht, dass die
Bewegung in $D$ bleibt. Invarianz ist ein eigenes Zertifikat und wird hier
nicht geliefert.

## 3. Funktionale Verträge und Verfeinerung

`FunctionalContract`: Annahmebereich, Fehlerschranke unter einer
**benannten** Metrik, benannte Koordinaten, Einheiten und Uhr.
`check_refinement(impl, spec)` beweist Verfeinerung genau dann, wenn
`spec.assumption ⊆ impl.assumption` (exakt zertifiziert) und
`impl.error_bound ≤ spec.error_bound`. Abweichende Metrik, Koordinaten,
Einheiten oder Uhr ergeben `incompatible` — ein anderes Ergebnis als
„Verfeinerung widerlegt“. Implementiert ist nur dieser funktionale
Spezialfall, nicht die Theorie reaktiver Assume–Guarantee-Verträge (S07).

**J-C08:** Spezifikation $[0,1]$, Fehler ≤ $1/5$; Implementierung
$[-1,2]$, Fehler ≤ $1/10$ — vorwärts bewiesen, rückwärts widerlegt (mit
Zeugenpunkt).

## 4. Getypte Komposition

Ein `CorrespondenceLink` trägt auf beiden Seiten Modell-ID, Koordinaten,
Einheiten und Uhr; die Abbildung ist exakt affin, der Zeitfaktor eine
positive Konstante. **Gleiche Modellnamen sind kein
Kompatibilitätsbeweis:** Modell-ID, Koordinaten, Einheiten und Uhr der
Zwischenschicht müssen alle übereinstimmen, sonst `incompatible`.

| Größe | Komposition |
|---|---|
| Bereich | $D_{12}=D_1\cap T_1^{-1}(D_2)$ (exakt; leer wird markiert: jede All-Aussage ist dann vakuos) |
| Uhr | $c_{12}=c_1c_2$ |
| Horizont (Quellzeit) | $H_{12}=\min(H_1,H_2/c_1)$ |
| Flussfehler | $\delta_{12}\le L_2\delta_1+\delta_2(c_1t)$ — nur mit Lipschitzzertifikat für $T_2$, das die **Verbindungsstrecken** abdeckt; $\delta_2$ wird zur abgebildeten Zeit ausgewertet, nicht mit $c_1$ multipliziert |
| Feldresiduum | $\lVert r_{12}\rVert\le M\varepsilon_1+A\varepsilon_2$ mit $M\ge\lVert DT_2\rVert$ (für affines $T_2$ exakt die induzierte ∞-Norm) und $A\ge\lvert a_1\rvert$ |

Ein kleines Vektorfeldresiduum ist ohne zusätzliche Dynamikabschätzung
**keine** gleich große Flussabweichung; beide Schranken stehen in
getrennten Berichten. Jede Komponentenschranke trägt ihre Evidenzart; die
**schwächste** bestimmt die Komposition (eine numerisch geschätzte
Komponente macht aus `proved` ein `observed_pass`). Fehlt ein Lipschitz-
zertifikat, gibt es keine zusammengesetzte Flussschranke (`undecided`).

Zustandsabhängige Zeitabbildungen bleiben in den vorhandenen Punkt- und
Numerikroutinen; ein allgemeiner verifizierter Kompositionsnachweis dafür
ist optional und bräuchte eine eigene Herleitung.

### Handkontrollen

- **J-C05:** $T_1=2x$, $D_1=D_2=[0,1]$ → $D_{12}=[0,1/2]$; $x=3/4\mapsto3/2\notin D_2$.
- **J-C06:** $c_1=c_2=1/2$ → $c_{12}=1/4$; $H_1=4$, $H_2=1$ → $H_{12}=2$.
- **J-C07:** Fluss $3\cdot\tfrac1{10}+\tfrac15=\tfrac12$; Feld $3\cdot1+2\cdot3=9$ auf $[0,1/2]$, am Rand erreicht; $r_{12}(1/4)=15/2$.
- **J-C08:** siehe §3.

### Identität und Assoziativität

`identity_link` ist neutral (gleiche Abbildung, gleicher Scope, gleicher
Horizont). Beide Klammerungen dreier Verbindungen ergeben exakt dieselbe
Abbildung, denselben Zeitfaktor, denselben Horizont und **gleiche**
Scope-Bedingungen. Konservative Fehlerschranken verschiedener
Klammerungen dürfen sich unterscheiden, ohne die Assoziativität der
Abbildungen zu verletzen; im geprüften Fall konstanter Schranken sind sie
nach Distributivität gleich ($11/28$).

## 5. Quelle

S07 Benveniste et al. (2018), *Contracts for System Design* — Links siehe
Plan §21; nur der ausdrücklich definierte funktionale Spezialfall ist
implementiert.
