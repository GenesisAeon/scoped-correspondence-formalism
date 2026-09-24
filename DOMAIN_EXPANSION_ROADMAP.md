# Themenbreite erweitern — Roadmap (2026-09-24)

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/Astra7.txt` und die
zugehörige `SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md` (Astra, 2026-09-24,
Referenzcommit `bd87a44`) — ein ausgearbeiteter Vorschlag, SCF an vier neuen
Anwendungsdomänen zu erproben: Warteschlangen, Hydrologie, Batteriealterung,
kooperative Agenten. Anders als `CAPABILITY_EXPANSION_ROADMAP.md` (die
bestehende Module härtete) fügt dieser Plan **neue Domänenmodule** hinzu.

Johanns Auftrag (2026-09-24): "Volle Roadmap B0–B7" (nach expliziter
Rückfrage zum Umfang, inkl. der beiden echten Datenpiloten CAMELS-DE und
NASA-Batterie).

Gleiche Disziplin wie bei den vorherigen Roadmaps: additive Module, Hand-
Nachrechnung vor Code, unabhängige Reproduktion jedes Astra-Befunds vor dem
Fix, `verify_*.py` mit Scope-Verletzungen, volle Suiten-Regression nach
jedem Paket, negative/neutrale Ergebnisse zählen genauso wie positive.

## Pakete

| Paket | Inhalt | Status |
|---|---|---|
| B0 | Zeiteinheitenfehler in `_analytic_component_critical_times` (skalenabhängige absolute Diskriminantenschwelle) | ✅ erledigt |
| B1 | Protokoll, Provenienz, Testzuordnung, diese Roadmap | ✅ erledigt |
| B2a | Fluidrückstau und Bestandsbrücke | ⏳ offen |
| B2b | CTMC-Erstpassage und Queue-Pilot | ⏳ offen |
| B3a | Lineare Reservoirs und Gedächtnisbrücke | ⏳ offen |
| B3b | CAMELS-DE-Datenpilot (echte externe Daten) | ⏳ offen |
| B4 | Diffusions-Erstpassage (Brownsche Bewegung mit Drift) | ⏳ offen |
| B5a | Kapazitätsmodelle und Beobachtungs-Ablation | ⏳ offen |
| B5b | NASA-Batteriedatenpilot (echte externe Daten, Lizenz laut Astra ungeklärt) | ⏳ offen |
| B6a | Endliche kooperative Agentenaufgaben | ⏳ offen |
| B6b | Wiederholte Aufgabe / OpenSpiel | ausdrücklich optional, nicht Teil dieser Runde |
| B7 | Gemeinsamer Ergebnisvergleich, Fähigkeitsübersicht | ⏳ offen |

Themenatlas (Ökologie, Energie, Verkehr, Lieferketten, Neurowissenschaft,
Astronomie) ist explizit **zweite Ausbaurunde**, nicht Teil dieses Auftrags.

## B0 — Zeiteinheitenfehler (erledigt)

Unabhängig reproduziert: `A=[[-0.1,-10],[10,-0.1]]`, `x0=[0,1]`, `H=10`,
Grenze `0.95` klassifiziert bei `c=1` korrekt als `transient_violation`
(Peak `0.9844639845000663` bei `t≈0.1561`, deckt sich mit der analytischen
Herleitung `arctan(100)/10`). Unter `A_new=c*A`, `H_new=H/c`, `c=1e-6`
(exakte Zeit-Umskalierung derselben Trajektorie) meldete der Code
fälschlich `no_violation_in_horizon` mit Peak `0.186` am Horizontende
`t=1e7` — der absolute Diskriminanten-Schwellwert `±1e-9` griff nicht mehr,
da `D` selbst wie `c²` skaliert.

**Fix:** `_analytic_component_critical_times` vergleicht jetzt den
skaleninvarianten relativen Diskriminanten `D / scale` (mit
`scale = max(tr(A)², 4·|det(A)|)`, skaliert exakt wie `D` unter `A→c·A`)
gegen eine dimensionslose Schwelle `1e-9`. `scale == 0` (erzwingt `D == 0`,
z. B. Nullmatrix) wird direkt dem Doppelwurzel-Zweig zugeordnet.

**Verifiziert:** `verify_transient_amplification.py`,
`astra_b0_scale_invariant_discriminant_classification` (9/9 Checks
insgesamt) — identische Peak-Höhe/Klassifikation für `c ∈ {1e-6, 1, 1e6}`,
Peak-Zeit skaliert exakt mit `1/c`; Nullmatrix und exakte Doppelwurzel als
Randfälle abgedeckt; alle bisherigen Regressionen unverändert grün.

Docs: `docs/transient_amplification.md` (neuer Correction-Block).

## B1 — Gemeinsame Versuchskonventionen (erledigt)

Diese Roadmap-Datei selbst erfüllt den Kern von B1 für die erste
Pilotenrunde. Weitergehende Infrastruktur (Manifest-Schema-Erweiterung,
`available_at`-Filterhilfen, Ereignisbericht-Serialisierung) wird direkt an
dem Piloten ergänzt, der sie zuerst tatsächlich braucht (B2b für das
Ereignisbericht-Schema, B3b für die Manifest-Erweiterung) — kein
vorgezogenes generisches Framework ohne konkreten ersten Nutzer, siehe
Plan Abschnitt 7 ("Nicht vorziehen").

## Nächste Schritte

B2a (Fluidrückstau, rein synthetisch/analytisch) als nächstes.
