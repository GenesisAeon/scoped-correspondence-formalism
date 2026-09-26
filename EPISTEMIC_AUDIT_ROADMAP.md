# SCF — Annahmen, Gegenmodelle und Entscheidungen unter begrenzter Beobachtung — Roadmap (2026-09-26)

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/SCF_ASSUMPTION_EVIDENCE_IMPLEMENTATION_PLAN.md`
(26. September 2026, geprüfter Ausgangsstand `84848a4`, tatsächlicher
Start-Commit dieser Roadmap: `398b919`, nach dem Followup-Review-Fix).

Johanns Auftrag (2026-09-26): "mach gern alles als Roadmap fertig und
dann arbeite es gern Schritt für Schritt ab" — dieselbe Disziplin wie bei
G0–G7 und den B/C-Serien: additive Module, Hand-Nachrechnung vor Code,
unabhängige Reproduktion jedes Kontrollfalls, `verify_*.py` mit gezielten
Verletzungen, volle Suiten-Regression nach jedem Paket.

## Pakete

| Paket | Inhalt | Abhängigkeit | Status |
|---|---|---|---|
| H0 | Bestandsaufnahme und Quellenvertrag | keine | ✅ erledigt |
| H1 | Endliche Aussagen und nichtleere Evidenz | H0 | ✅ erledigt |
| H2 | Tragende Annahmen und Inkonsistenzkerne | H1 | ✅ erledigt |
| H3 | Beobachtungsabhängige Identifikation | H1 | ✅ erledigt |
| H4 | Endliche Entscheidungen unter deklarierter Ungewissheit | H1 | ✅ erledigt |
| H5 | Integrierter Pufferpilot (K5, kontinuierlich) | H1, H4 | offen |
| H6a | Adapter an bestehende SCF-Berichte (Pflicht) | H1–H3 | offen |
| H6b | Optional: synthetischer Galaxienfall | H6a | offen |
| H6c | Zurückgestellt: echte SPARC-Berichte | H6a | 🚫 zurückgestellt |
| H7 | Dokumentation, CLI, CI, Abschluss | H1–H6a | offen |

Reihenfolge (Plan Abschnitt 14.1): H0 → H1 → H2 → H3 → H4 → H5 → H6a → H7.
K7 (Randomisierung) bleibt optionale Vertiefung, kein Pflichtteil.

## H0 — Bestandsaufnahme und Quellenvertrag (erledigt)

### Ausgangslage bestätigt

- Aktueller HEAD bei Beginn: `398b919` (Followup-Review-Fix, danach
  dieses Paket). Volle Regression zu diesem Zeitpunkt: 99/99
  `verify_*.py` grün (siehe `GALAXY_DYNAMICS_ROADMAP.md`).
- **Galaxien-Abhängigkeiten aus Plan §3.1 sind tatsächlich behoben, nicht
  nur behauptet:** F1 (lokales statt globales Minimum in der
  Profil-Likelihood) und F2 (Modellgüten auf unterschiedlichen
  Teilmengen gültiger Punkte) wurden im Followup-Review-Fix (`398b919`)
  unabhängig reproduziert und korrigiert — siehe
  `GALAXY_DYNAMICS_ROADMAP.md` Abschnitt "Followup-Review-Fix". Damit
  blockieren sie H6b nicht mehr (H6b nutzt ohnehin nur die
  Zwei-Radien-Anpassung aus `verify_galaxy_observation_maps.py`, die von
  F1/F2 nicht betroffen war). Yoons fehlender Volltext (G6) ist für
  dieses Paket ohne Bedeutung.

### Vorhandene APIs bestätigt (Code direkt geprüft, nicht nur Plantext übernommen)

| Baustein | Datei | Bestätigt |
|---|---|---|
| `partition_indicator` | `correspondence/controlled_markov.py:54` | ✅ existiert |
| `check_controlled_correspondence` | `correspondence/controlled_markov.py:149` | ✅ existiert, ein Bericht PRO Mikroaktion |
| `is_union_of_classes` | `correspondence/controlled_markov.py:305` | ✅ existiert, nimmt Partitionsmatrix `C`, nicht Labels direkt |
| `Scope`, `CorrespondenceReport`, `verify_conjugacy` | `correspondence/contract.py` | ✅ existiert (siehe G2-Nutzung) |
| `identifiability/core.py` | — | ✅ existiert, Produkt-Invarianzen/Rangkontrollen |
| `BufferSpec`, `sustained_safety_over_horizon` | `viability/coupled_buffer_cbf_qp.py:89,135` | ✅ existiert |
| `bellman_value` | `validation/sequential_information_pilot.py:82` | ✅ existiert |
| `DatasetManifest`, `ValidationReport` | `validation/core.py:92,191` | ✅ existiert |
| `MetaRuleUpdate` | `metarules/core.py:51` | ✅ existiert |
| Burkert/NFW Zwei-Radien-Anpassung | `verification/verify_galaxy_observation_maps.py` (`check_observation_equivalence_cross_family_degeneracy`) | ✅ existiert (aus G3) |

Kein einziger im Plan referenzierter Baustein war falsch benannt oder
fehlend — die Quellenlage des Plans ist zuverlässig.

### K1–K8 unabhängig nachgerechnet (vor jeder Implementierung, ohne die mitgelieferte Referenz zu nutzen)

Eigenständiges Python-Skript (bool/int/rational, kein SCF-Import, kein
Optimierer) — exakte Übereinstimmung mit allen im Plan genannten Werten:

| Fall | Nachgerechnet | Ergebnis |
|---|---|---|
| K1 | Minimale Supports von {A1,A2,A3,A4} für C=r | `{A1,A4}` und `{A1,A2,A3}` — genau 2, beide bestätigt |
| K1 | Minimale Inkonsistenzkerne mit A5=¬r | `{A1,A4,A5}` und `{A1,A2,A3,A5}` — bestätigt |
| K2 | A={¬p}: `\|S_A\|=4`, `p⇒q` überall wahr, `p` nirgends wahr | bestätigt; A={p,¬p}: `S_A=∅` bestätigt |
| K3 | `x²≤1` auf W={-1,0,1} vs. W'={-1,0,1,2} | gilt auf W, Gegenmodell `x=2` auf W' — bestätigt |
| K4 | F(2)={(0,2),(1,1),(2,0)}, nur (1,1) erfüllt "beide≥1" | bestätigt; `q=(x1-x2)²` Wertemenge `{0,4}` bestätigt |
| K5 | `min{x_i(0), x_i(0)+u_i-1}≥0`, B=1 unmöglich/B=2 möglich für gemeinsamen Eingriff | von Hand hergeleitet (affine Trajektorie, Minimum an den Intervallenden): (0,2)→u=(1,0), (1,1)→u=(0,0), (2,0)→u=(0,1); gemeinsamer Eingriff bräuchte `u1≥1 UND u2≥1`, also `u1+u2≥2` — bestätigt |
| K6 | Minimax wählt B (Worst-Case 6 vs. 10), Minimax-Regret wählt A (Regret 4 vs. 6) | bestätigt; Erwartungswert-Kreuzung bei `p=0,6` bestätigt |
| K7 | Beste deterministische Entscheidung: Regret 1; randomisiert `α=1/2`: Regret 1/2 | bestätigt (optionale Vertiefung) |
| K8 | `PC=CQ` exakt bei `P=I4`, Partition `{{0,1},{2,3}}`; `E={1}` keine Vereinigung von Makroklassen | bestätigt |

Alle 10 Prüfpunkte bestätigt. Das schafft Vertrauen in die Formeln, bevor
sie in H1–H5 als Code implementiert werden — es ist noch keine
Implementierung.

### Quellen (`docs/epistemic_sources.md`)

Siehe eigene Datei. Kurzfassung: S1/S2 (Gödel/Scott-Formalisierung,
AFP/IJCAI, nur als Beispiel für explizite Semantik referenziert, keine
eigene Isabelle-Anbindung), S3 (Alloy-Doku zur Scope-Grenze endlicher
Gegenmodellsuche), S4/S5 (Vacuity Detection, nur der explizite
Antezedens-Check wird implementiert, keine volle CTL*-Analyse), S6
(minimale vs. kleinste Mengen), S7/S8 (Manski: Identifikation und
Entscheidung bei Unterbestimmtheit), S9 (robuste Optimierung), S10
(CEGAR, nur als spätere Perspektive).

### Umfangsgrenze (Plan §6.3, hier übernommen)

Kein Freitext-Parser, kein `eval`. Exakter Kern nutzt bool/int/`Fraction`
(Python `fractions.Fraction`, keine neue Abhängigkeit). Explizite Budgets
(Standard: 4096 Kandidaten, 4096 untersuchte Annahmenteilmengen, insgesamt
1.000.000 Prädikatauswertungen). Ein Budgetabbruch bestätigt weder
Minimalität noch universelle Gültigkeit.

## H1 — Endliche Aussagen und nichtleere Evidenz (erledigt, Commit `649cd95`)

`src/scoped_correspondence/epistemic/{records,finite}.py` implementieren
die ausführbare Form der H0-Ergebnistabelle: `audit_finite_claim(domain,
assumptions, claim, *, budget)` liefert einen `ClaimReport` mit genau
einem der fünf Logikstatus (`no_admissible_model_in_scope`,
`entailed_in_scope`, `negation_entailed_in_scope`, `underdetermined`,
`incomplete`), Zwei-Zeugen-Frühabbruch, und der B⇒C-Vakuitätsprüfung
(`antecedent_reachable_in_scope`, `vacuity_kind`).

Zwei Bugs beim ersten Testlauf (4/9 grün) gefunden und behoben, bevor
committet wurde:

- `finite.py`: die Vakuitätsprüfung lief auch bei `n_admissible==0`
  (widersprüchliche Annahmen) und setzte fälschlich
  `antecedent_reachable_in_scope=False` statt `None` — das sind zwei
  verschiedene Fälle (`docs/epistemic_scope.md` §2). Mit
  `n_admissible > 0`-Wächter behoben.
- `verify_epistemic_finite.py`: `check_abort_before_after_witnesses`
  erwartete für `budget=2` `"incomplete"`, obwohl beide Zeugen (0 gerade,
  1 ungerade) innerhalb des Budgets gefunden werden — der
  Zwei-Zeugen-Frühabbruch greift dort bereits VOR Budgeterschöpfung,
  also ist das per Definition `"underdetermined"`. Test korrigiert und um
  einen echten Budget-Erschöpfung-vor-Gegenzeuge-Fall (Kandidaten in
  gerade-dann-ungerade-Reihenfolge) ergänzt.

9/9 `verify_epistemic_finite.py` grün, volle lokale Regression (100/100)
und Linkprüfung (0 kaputte relative Links) grün.

## H2 — Tragende Annahmen und Inkonsistenzkerne (erledigt)

`src/scoped_correspondence/epistemic/supports.py` implementiert
`find_minimal_support(domain, assumptions, claim, *, background=(),
subset_budget, candidate_budget) -> SupportReport` und
`find_minimal_inconsistent_core(domain, assumptions, *, background=(),
subset_budget, candidate_budget) -> InconsistentCoreReport`.

Beide nutzen dasselbe Löschverfahren (S6, Marques-Silva & Janota):
Start bei einer bereits tragenden bzw. bereits unerfüllbaren
Ausgangsmenge (ein anderer Start wird explizit verweigert, nicht
stillschweigend "repariert"), dann Entfernungsversuche in genau der vom
Aufrufer übergebenen Reihenfolge — jede Entfernung wird über
`audit_finite_claim` unabhängig neu geprüft und der volle `ClaimReport`
als Zeuge im `DeletionStep` gespeichert, nie nur ein Bool. Eine
Inkonsistenzkern-Suche braucht keine eigene Zielaussage: intern wird ein
konstant-wahres `_SATISFIABILITY_PROBE`-Ziel an `audit_finite_claim`
übergeben, wodurch `logical_status` allein zwischen
`no_admissible_model_in_scope` (unerfüllbar) und `entailed_in_scope`
(erfüllbar) unterscheidet.

Teilmengenminimal ist NICHT kleinste Kardinalität: unterschiedliche
Entfernungsreihenfolgen liefern für K1 absichtlich unterschiedliche,
beide gültige Ergebnisse — es gibt keinen versteckten "finde alle"-Modus
(Plan §4.3). `background`-Annahmen werden immer angewendet, sind aber nie
Entfernungskandidaten und erscheinen nie in `support_ids`/`core_ids`,
nur separat in `background_ids`.

Beide Suchen teilen sich EIN laufendes Kandidaten-Scan-Budget über alle
verschachtelten `audit_finite_claim`-Aufrufe hinweg (Plan §6.3: "Die
Gesamtgrenze gilt auch über verschachtelte Supportprüfungen hinweg"),
zusätzlich zu einer separaten Obergrenze für die Anzahl versuchter
Annahmenteilmengen (`subset_budget`).

K1 vor der Implementierung von Hand nachvollzogen (Reihenfolge
[A1,A2,A3,A4] → Löschversuche A1 kept, A2 removed, A3 removed, A4 kept →
{A1,A4}; Reihenfolge [A1,A4,A3,A2] → A1 kept, A4 removed, A3 kept, A2
kept → {A1,A2,A3}; mit A5=¬r analog für beide Inkonsistenzkerne) —
stimmt exakt mit den in H0 unabhängig berechneten Referenzwerten
überein und wurde danach 1:1 vom Code reproduziert.

`verify_epistemic_supports.py` deckt alle in Plan §7 geforderten
Pflichtprüfungen ab: K1 vollständig (beide Kardinalitäten für Supports
UND Kerne), Löschzeugen (jeder Schritt trägt seinen eigenen
`ClaimReport`), konstante wahre Aussage mit leerem Support,
widersprüchlicher Ausgangsfall (wird verweigert, nicht "repariert"),
mehrere alternative Supports (aus derselben Eingabe, nur andere
Reihenfolge), Budgetabbruch (sowohl `subset_budget` als auch
`candidate_budget` einzeln getestet, nie als falsche Minimalität
gemeldet), unveränderte Hintergrundannahmen.

7/7 `verify_epistemic_supports.py` grün, `verify_epistemic_finite.py`
weiterhin 9/9 grün, volle lokale Regression grün, Linkprüfung 0 kaputte
relative Links.

## H3 — Beobachtungsabhängige Identifikation (erledigt)

`src/scoped_correspondence/epistemic/observation_fibers.py` implementiert
`observation_fiber(domain, assumptions, observation, observed, *,
budget) -> FiberReport` (F_A(y)) und `identified_values(fiber, target) ->
IdentifiedSetReport` (Q_A(y)). Eine leere Faser wird explizit als
Unvereinbarkeit von Beobachtung und Modellraum markiert (`empty_fiber`,
erklärende `notes`), nie als vakuos "perfekt identifiziert". Mehrere
mögliche Werte werden als vollständige Menge (`values`) berichtet;
`min_value`/`max_value` sind zusätzliche Bequemlichkeitsfelder, die die
Menge nie ersetzen.

K4 (X={0,1,2}², h=x1+x2, y=2 → F(2)={(0,2),(1,1),(2,0)}) vor der
Implementierung von Hand nachvollzogen: die boolesche Aussage "beide
Reserven ≥1" ist bei y=2 NICHT identifiziert (beide Wahrheitswerte in der
Faser), und q=(x1−x2)² hat exakt die Wertemenge {0,4} — bestätigt, ohne
dass das Intervall [0,4] fälschlich Zwischenwerte suggeriert. Die
Verfeinerung h_f=(x1+x2, min(x1,x2)) zerlegt die Faser in {(1,1)}
(m=1, punktidentifiziert: Aussage=wahr, q=0) und {(0,2),(2,0)} (m=0):
dort identifiziert m bereits sowohl die Aussage (falsch, da min=0) als
auch q (4) OHNE den rohen Zustand selbst zu identifizieren — genau der im
Plan (§4.4) beschriebene Unterschied zwischen Aussage-/Zielgrößen-
Identifikation und vollständiger Zustandsrekonstruktion. Beide
verfeinerten Wertemengen sind echte Teilmengen der groben Menge {0,4},
wie vom Plan für Informationsverfeinerung gefordert.

`macro_dynamics_and_observability` bündelt die vorhandenen Funktionen
`check_controlled_correspondence` und `is_union_of_classes`
(`correspondence/controlled_markov.py`) für K8: P=I4, Partition
{{0,1},{2,3}} ergibt exakte PC=CQ mit Q=I2 (`dynamics_exact=True`), aber
das Ereignis {1} ist keine Vereinigung von Makroklassen
(`event_is_union_of_classes=False`) — beide Ergebnisse werden als
getrennte Felder nebeneinander ausgegeben, nie zu einem Bool verschmolzen.
Zum Vergleich: das vollständige Klassenereignis {0,1} IST eine
Vereinigung von Makroklassen.

`verify_epistemic_identification.py`: 6/6 Checks grün (K4-Faser und
Boolesche Nichtidentifikation, disjunkte Wertemenge nicht auf Intervall
kollabiert, Verfeinerung schrumpft die Wertemenge, leere Faser wird
markiert statt als perfekte Identifikation missverstanden, K8
Dynamik-vs-Beobachtbarkeit, Budgetabbruch propagiert Unvollständigkeit
statt sie stillschweigend zu verschweigen). `verify_epistemic_finite.py`
weiterhin 9/9 und `verify_epistemic_supports.py` weiterhin 7/7 grün,
volle lokale Regression grün, Linkprüfung 0 kaputte relative Links.

## H4 — Endliche Entscheidungen unter deklarierter Ungewissheit (erledigt)

`src/scoped_correspondence/epistemic/decisions.py` implementiert
`uniform_safe_actions(fiber, actions, safety) -> ActionSetReport` und
`compare_decisions(loss_matrix, *, criterion, probabilities=None) ->
DecisionReport`.

`uniform_safe_actions` hält die beiden im Plan (§4.5) ausdrücklich
getrennten Aussagen auseinander: zustandsweise zulässig (`forall w exists
u: safe(w,u)`) vs. uniform zulässig (`exists u forall w: safe(w,u)`,
`U_uniform(F) = ∩ U_safe(w)`). K5 (dieselbe Faser F(2)={(0,2),(1,1),(2,0)}
wie K4, endlich diskretisiert auf u∈{0,1}²) reproduziert exakt den
Plan-Befund: bei Budget 1 (Aktionen (0,0),(1,0),(0,1)) ist jeder Zustand
einzeln kontrollierbar, aber `U_uniform(F)=∅` — erst mit der Budget-2-
Aktion (1,1) wird die Faser uniform zulässig, `U_uniform(F)={(1,1)}`. Eine
leere oder unvollständig gescannte Faser liefert nie eine zulässige
Handlung.

`compare_decisions` validiert die Verlusttabelle streng (endliche Werte,
identische Zustandsmengen über alle Aktionen, bei `expected_loss`
explizit deklarierte, auf 1 summierende Wahrscheinlichkeiten — die
Kandidatenzahl ist niemals ein impliziter Gleichverteilungs-Prior) und
implementiert drei bewusst NICHT austauschbare Kriterien: `minimax`,
`minimax_regret`, `expected_loss`. K6 vor der Implementierung von Hand
nachvollzogen: Minimax wählt B (Verlust 6 < 10), Minimax-Regret wählt A
(Regret 4 < 6) — auf DERSELBEN Tabelle unterschiedliche Entscheidungen.
Der Erwartungsverlust-Vergleich mit exakten `Fraction`-Wahrscheinlich-
keiten kippt exakt bei p=3/5=0,6 (Gleichstand exakt an der Grenze, kein
Rundungsartefakt durch Gleitkommazahlen). Unentschieden werden immer als
vollständige Menge gebundener Aktionen gemeldet, nie willkürlich
aufgelöst.

`verify_epistemic_decisions.py`: 8/8 Checks grün (K5 zustandsweise-aber-
nicht-uniform bei Budget 1, K5 uniform zulässig bei Budget 2, leere/
unvollständige Faser nie vakuos zulässig, K6 Minimax-vs-Minimax-Regret-
Widerspruch, K6 Erwartungsverlust-Kreuzung exakt bei p=0,6, Unentschieden-
Behandlung, Validierung verwirft unendliche/NaN-Verluste und ungültige
Wahrscheinlichkeiten, expliziter `uniformly_feasible=False`-Fall).
`verify_epistemic_finite.py` weiterhin 9/9, `verify_epistemic_supports.py`
weiterhin 7/7, `verify_epistemic_identification.py` weiterhin 6/6 grün,
volle lokale Regression grün, Linkprüfung 0 kaputte relative Links.