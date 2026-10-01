# SCF — Myonium, Gravitationsmessung und identifizierbare Abweichungen — Roadmap (2026-10-01)

Antwort auf [`SCF_MUONIUM_GRAVITY_IMPLEMENTATION_PLAN.md`](prompts/Answers/nicht_stationäre_Treiber/SCF_MUONIUM_GRAVITY_IMPLEMENTATION_PLAN.md)
(01.10.2026, gelesener Repo-Stand des Plans `4a7ed38`). Quellenaudit:
[`docs/muonium_source_audit.md`](docs/muonium_source_audit.md).

Johanns Auftrag (2026-10-01): die Followups „ruhig direkt mit
einbauen“. Disziplin wie in `CLAUDE.md`: Herleitung vor Code, ein Paket
pro Commit, volle Regression und Linkprüfung vor jedem Commit.

**Was diese Serie nicht ist:** keine LEMING-Simulation, keine neue
Gravitations- oder Quantengravitationstheorie, keine Widerlegung
Einsteins, keine bereits erfolgte Myonium-Gravitationsmessung, keine
Bestätigung für CREP, UTAC oder AFET (Plan §1). Ein erfolgreicher
Abschluss kann ebenso eine nachgewiesene Nichtidentifizierbarkeit sein wie
eine präzise Schätzung.

## Pakete

| Paket | Inhalt | Status |
|---|---|---|
| MU0 | Quellenregister, Anschlussinventar, unabhängige Herleitungen | ✅ erledigt |
| MU1 | Kinematik, Einheiten, Geltungsbereich | ✅ erledigt |
| MU2 | Endliche Geschwindigkeitsmischung und Messoperator | ✅ erledigt |
| MU3 | Count-Likelihood und Schätzdiagnostik | ✅ erledigt |
| MU4 | Identifizierbarkeit und Interventionen | ✅ erledigt |
| MU5 | Design und bedingte Abdeckung | ⬜ offen |
| MU6 | Evidenzadapter, optionales Realdatenfenster | ⬜ offen (Realdaten voraussichtlich `deferred`) |
| MU7 | CLI, Fähigkeitsbilanz, Abschluss | ⬜ offen |

**Einordnung in die Gesamtreihenfolge** (siehe
[`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Abschnitt „Einbindung der Followups“): MU beginnt nach J6, weil MU1 die
J2-Dimensionsprüfung, MU4 die exakte affine Identifizierbarkeit aus J6
und MU5 Bausteine aus J6/J7 nutzen kann. Der MU-Plan verlangt
ausdrücklich, J-Bausteine erst nach Prüfung ihrer **tatsächlichen**
Existenz anzuschließen — am MU0-Stand existieren J0–J6 und J11
committet; J7–J10 und J12 noch nicht, MU setzt sie nicht voraus.

## MU0 — Quellenregister und Anschlussinventar (erledigt)

### Arbeitsstand

Branch `j-series` (Worktree), aufbauend auf den committeten Paketen J0–J6
und J11 (siehe J-Roadmap). Der Plan selbst wurde gegen `4a7ed38` gelesen;
die dort aufgeführten Anschlüsse wurden am aktuellen Stand neu geprüft.

### Bestehende Anschlüsse bestätigt (Datei:Zeile, Pfade unter `src/scoped_correspondence/`)

| Anschluss | Datei:Zeile | Befund |
|---|---|---|
| `profile_parameter`, `classify_identifiability`, `likelihood_interval` | `identifiability/profile_likelihood.py:161,245,312` | ✅; Rückgabetyp `Profile = List[Tuple[float, float]]` (`:31`) — **keine Optimiererdiagnosen**, wie vom Plan angegeben |
| `profile_parameter_nlp` | `identifiability/profile_likelihood_nlp.py:42` | ✅ beschränktes `least_squares` mit fixiertem Parameter; kein NLL-Optimierer, lokale Läufe |
| `poisson_log_score` | `validation/scoring_rules.py:113` | ✅ verlangt `predicted_mean > 0` (`:119`) — Grenzfall λ=0 muss MU3 selbst exakt behandeln |
| `observation_fiber` | `epistemic/observation_fibers.py:75` | ✅ endliche Faser |
| `audit_finite_claim` | `epistemic/finite.py:56` | ✅ |
| `claim_report_from_correspondence` | `epistemic/adapters.py:65` | ✅ |
| `Scope`, `Correspondence` | `correspondence/contract.py:64,113` | ✅ |
| `docs/real_data_provenance.md` | — | ✅ Realdatenprotokoll |
| **neu seit dem Plan-Stand:** `dimensions/` (J2), `identifiability/exact_linear.py` (J6), `assurance/records.py` (J4) | — | existieren committet; nutzbar für MU1 (Einheiten), MU4 (affine Rangfälle MU-C09/C10), Berichte |

### Unabhängige Herleitungen MU-C01–MU-C17

Alle 17 Kontrollgruppen zuerst von Hand aus dem Plantext hergeleitet,
dann mit eigenem SCF-freiem Skript
[`verification/plan_controls/mu_series_independent_controls.py`](verification/plan_controls/mu_series_independent_controls.py)
nachgerechnet: **17/17**
([Ergebnisse](verification/plan_controls/mu_series_independent_controls_results.json)).

**Fehlendes Oracle:** Der Plan verweist auf ein Begleitskript
`independent_controls.py` („29/29“, davon 17 MU-Gruppen). Es lag **nicht**
im Eingangsordner. Die Planaussage „29/29“ ist hier daher nicht
reproduziert; die 17 MU-Werte stammen ausschließlich aus eigener
Herleitung.

| Fall | Ergebnis (bestätigt) | Herleitung |
|---|---|---|
| MU-C01 | $\delta=1/10\Rightarrow\eta=2/21$; η undefiniert bei $\delta=-2$ | $\eta=2\delta/(2+\delta)$ exakt |
| MU-C02 | $z(2T)-2z(T)+z(0)=aT^2$; Einzelbahn $aT^2/2$ | exakt rational |
| MU-C03 | $L=9{,}592$ mm; Absenkung nach τ $23{,}7402$ pm; $gT^2=189{,}9216$ pm; Phase $0{,}0119331260663604$ rad; $e^{-4}$; $1\,\%$: $119{,}331\,\mu$rad bzw. $1{,}899216$ pm | Gleitkomma, relativ $10^{-9}$; $K=2\pi L^2/(dv^2)=2\pi T^2/d$ |
| MU-C04 | $e^{-4}=0{,}0183156388887342$; $T_{\rm opt}=2\tau$ | $\frac{d}{dT}\log\sigma=1/\tau-2/T$ exakt; Vorzeichenwechsel geprüft |
| MU-C05 | Einheitenwechsel (m→mm, s→µs) invariant; $(1{,}01)^2=1{,}0201$ → $2{,}01\,\%$ | exakt |
| MU-C06 | $E[1/v^2]=5/8\ne1/E[v]^2=4/9$ ($v\in\{1,2\}$ gleichgewichtet); Gegenphasen 0 und π: Kontrast 0, Phasenmittel π/2 täuscht Information vor | exakt bzw. komplex |
| MU-C07 | Überleben $1/4$, $1/2$ bei gleichem Eingang → detektiert $1/3$, $2/3$ | exakt |
| MU-C08 | NLL(0;0)=0, NLL(n>0;0)=∞; Deviance = 2·(NLL − gesättigte NLL); Nullzählung $2\lambda$ | drei Prüfpunkte |
| MU-C09 | entfaltete Phase: Rang 1 (eine Zeit) bzw. 2 ($u=(1,4)$); $p=(3,6)\Rightarrow A=1,b=2$ | exakt |
| MU-C10 | $p=u(A+B)+b$: Rang 2 trotz vier Flugzeiten | exakt |
| MU-C11 | Umkehr trennt geraden Offset ($p_+-p_-=2(A+B)$), ungerader Bias $B$ bleibt mit $A$ verbunden | exakt |
| MU-C12 | Vierphasenscan $I_\phi=NC^2/2=8$; Quadratur $NC^2=16$ ($N=400$, $C=1/5$) | exakte Summe der Einzelinformationen |
| MU-C13 | $\approx5{,}73265035\cdot10^8$ Ereignisse für $\sigma_a/g=1\,\%$ ($C=0{,}35$); äquivalenter Gitterversatz $1{,}899216$ pm | Gleitkomma, relativ $10^{-8}$ |
| MU-C14 | $a\to a+d/T^2$ verschiebt die Phase um genau $2\pi$ | exakt |
| MU-C15 | Quadratur: Zählrate fällt mit φ; arcsin nur lokal invers; $\phi$ und $\pi-\phi$ gleiche Zählrate | Gleitkomma |
| MU-C16 | $C=0$: keine Beschleunigungsinformation | trivial exakt |
| MU-C17 | $K_2=4K_1$: gemeinsamer Alias (Phasen verschieben um 1 bzw. 4 Umläufe) | exakt |

Alle Planwerte bestätigt; keine Abweichung zum Plantext.

### Quellenstatus (Details im Quellenaudit)

| Kennung | Status am 2026-10-01 |
|---|---|
| MU-S1 Zhang et al., Nature Physics | ✅ Verlagsseite erreichbar; Titel „Generation of a high-intensity, superthermal muonium beam for gravity and laser spectroscopy experiments“, veröffentlicht **14.09.2026** — stimmt mit dem Plan überein. Strahlquelle, **keine** gemessene Fallbeschleunigung. |
| MU-S2 arXiv:2512.19923v1 | ✅ erreichbar; Vorabfassung, nicht mit der Verlagsfassung mischen |
| MU-S3 Antognini et al. 2018 | arXiv ✅; Verlagsseite HTTP 403, **bibliografisch per Crossref bestätigt** (*Atoms*, 09.04.2018) — historischer Vorschlag |
| MU-S4 ETH-Mitteilung | ✅ erreichbar; institutionelle Statusmeldung, keine Datenquelle |
| MU-S5 Datenreferenz `10.3929/ethz-c-000802445` | DOI/Research Collection HTTP 429/500; **per DataCite-API geprüft**: CSV-Daten zur MU-S1-Arbeit, Lizenz **InC-NC** („In Copyright – Non-Commercial Use Permitted“) → **nicht einchecken**; höchstens lokaler, hashgeprüfter Lesezugriff für Strahl-/Nachweiskalibrierung. Inhalt/Schema ungeprüft → MU6-Realdatenzweig vorerst `deferred` |

Volltextfragen, die einfacher Abruf nicht klären konnte, stehen in
[`DEEP_RESEARCH_BACKLOG.md`](DEEP_RESEARCH_BACKLOG.md).

**Ausdrücklich:** Keine Behauptung eines gemessenen $g_\mu$. Alle
Zahlenwerte der Kontrollfälle sind illustrative Designannahmen des Plans
(g = 9,81 m/s², τ gerundet auf 2,2 µs).

### Offene Datenfragen

Inhalt, Format, Einheitenschema, Version und Lizenz der Datenreferenz
MU-S5; ob sie Strahl- oder Detektorparameter enthält, die MU6 zur
Kalibrierung (nicht zur Gravitation) nutzen dürfte.

### Abnahme MU0 (Plan §10)

- [x] Quellenstatus korrekt und getrennt (heutige Quelle / historischer Vorschlag / eigene Designwerte)
- [x] keine Behauptung eines gemessenen $g_\mu$
- [x] unabhängige Herleitungen abgelegt (17/17)
- [x] reale API-Signaturen bestätigt
- [x] keine Produktions-API in diesem Paket
- [x] bisherige Tests und Links unverändert grün (siehe Commit)

## MU1 — Kinematik, Einheiten, Geltungsbereich (erledigt)

Code: `muonium/kinematics.py`. Prüfung: `verify_muonium_kinematics.py` (math) **7/7** — MU-C01–C05, MU-C14; ungleiche Flugzeiten abgelehnt, η-Nenner null → undefiniert (nicht erfunden), ungültige Geometrie, nicht endliche Eingaben; negative $a$ zulässig; Phase per J2-Dimensionsprüfung dimensionslos.

Regression: gemeinsamer Lauf über den Stand mit MU1–MU7 (additiv; jede MU-Prüfung importiert nur MU-Module bis zu ihrem eigenen Paket) — `--category all` **122/122** bestanden, 0 übersprungen, 13 min 12 s; `--category links` 0 kaputt.

## MU2 — Endliche Geschwindigkeitsmischung und Messoperator (erledigt)

Code: `muonium/forward.py`. Prüfung: `verify_muonium_forward.py` (math) **7/7** — MU-C06, MU-C07, MU-C16; Nullsignal, $F=0$ ohne `arg(0)`, $C=0$/$C=1$, Messzeit je Bin (Gesamtzeit nicht je Bin wiederverwendet), unzulässige Gewichte, Einzelgeschwindigkeits-Grenzfall, Phase bei mittlerer Geschwindigkeit ≠ Mischung.

**Korrektur vor dem Commit:** `VelocityClass` hatte die Voreinstellungen $A=1$, $C=1$ — per Konstruktion eine Verletzung von $A(1+C)\le1$, die das Modell zu Recht ablehnte. Transmission und Kontrast sind jetzt Pflichtangaben ohne Voreinstellung.

Regression: gemeinsamer Lauf über den Stand mit MU1–MU7 (additiv) — `--category all` **122/122**, `--category links` 0 kaputt.

## MU3 — Count-Likelihood und Schätzdiagnostik (erledigt)

Code: `muonium/likelihood.py`. Prüfung: `verify_muonium_likelihood.py` (math) **5/5** — MU-C08 (Nullfälle, Deviance = 2·(NLL − gesättigt)), MU-C14 (alle Alias-Moden im Abstand $d/T^2$ berichtet), MU-C15; Randtreffer und Fehlläufe sichtbar, keine globale Aussage aus Mehrfachstart; nur rohe ganzzahlige Zählungen.

Regression: gemeinsamer Lauf über den Stand mit MU1–MU7 (additiv) — `--category all` **122/122**, `--category links` 0 kaputt.

## MU4 — Identifizierbarkeit und Interventionen (erledigt)

Code: `muonium/identifiability.py` (auf J6 aufbauend). Prüfung: `verify_muonium_identifiability.py` (math) **9/9** — alle acht Gegenbeispiele aus Plan §7, MU-C09–C11, MU-C14, MU-C17; ausdrücklich: mehr Flugzeiten und Umkehrungen entfernen nicht jede Störung; endliche Faser nur für die gelisteten Kandidaten.

Regression: gemeinsamer Lauf über den Stand mit MU1–MU7 (additiv) — `--category all` **122/122**, `--category links` 0 kaputt.

