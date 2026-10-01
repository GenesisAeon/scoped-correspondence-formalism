# SCF — Adaptive modulare Netzwerke und beobachtbare Information — Roadmap (2026-10-01)

Antwort auf [`SCF_ORGANOID_NETWORK_IMPLEMENTATION_PLAN.md`](prompts/Answers/nicht_stationäre_Treiber/SCF_ORGANOID_NETWORK_IMPLEMENTATION_PLAN.md)
(01.10.2026) samt Begleitpaket `SCF_ORGANOID_NETWORK_CLAUDE_PAKET.zip`.
Quellenaudit: [`docs/organoid_network_source_audit.md`](docs/organoid_network_source_audit.md).

Johanns Auftrag (2026-10-01): weiteres Followup, wie die übrigen
„ruhig direkt mit einbauen“. Disziplin nach `CLAUDE.md`: Herleitung vor
Code, ein Paket pro Commit, volle Regression und Linkprüfung vor jedem
Commit, Branch `j-series`.

**Leitfrage:** Wann verbessern Kopplung und Anpassung eines modularen
Netzwerks die Unterscheidbarkeit seiner Eingänge, und welchen Anteil hat
der Beobachtungszugang daran? System, Beobachtung, Auslesen und Schluss
bleiben getrennt. **Keine** Drei-Modul-Schwelle, kein Intelligenzscore,
keine Pflicht, dass Trios gewinnen; ein negatives oder gemischtes Ergebnis
ist zulässig.

## Pakete

| Paket | Inhalt | Status |
|---|---|---|
| ON0 | Quellen, Umfang, API-Audit, Handkontrollen | ✅ erledigt (dieser Commit) |
| ON1 | Exakte Beobachtungs- und Strukturkontrollen ($W(\delta)$, Voll-/Summenbeobachter) | ✅ erledigt |
| ON2 | Messrauschen und endliche Kanäle | ✅ erledigt |
| ON3 | Begrenzte adaptive Dynamik (N=12, Module, Hebb-Regel) | ✅ erledigt |
| ON4 | Decoder und hierarchischer Vergleich | ✅ erledigt |
| ON5 | Information, PID und Gerichtetheit | ✅ erledigt |
| ON6a | Synthetischer Benchmark und Evidenzbericht | ✅ erledigt |
| ON6b | Optionaler Realdatenadapter | ⛔ blockiert (Daten-Gates) |
| ON7 | CLI, Dokumentation, Abschluss | ⬜ offen |

## ON0 — Quellen, Umfang, Handkontrollen (erledigt)

### Arbeitsstand

Branch `j-series`, aufbauend auf J0–J12, MU0–MU7 und den
Kandidatenpiloten. Der Plan wurde gegen `4a7ed38` geschrieben; seine
Anschlüsse wurden am aktuellen Stand neu geprüft. Die J-Bausteine
existieren inzwischen (z. B. `epistemic`-Fasern, J1-Paarvergleiche,
J6-Identifizierbarkeit, `assurance`-Berichte); der Plan setzt sie nicht
voraus, ON nutzt sie nur, wo ihr Scope passt.

### Beilage geprüft

`SCF_ORGANOID_NETWORK_CLAUDE_PAKET.zip`: alle vier SHA-256-Summen aus
`SHA256SUMS` stimmen; der Plan in der Beilage ist bytegleich mit dem
eingecheckten. Frischer Lauf von `independent_organoid_controls.py`:
**23/23**, Ergebnis-JSON identisch mit dem mitgelieferten.

### Bestehende APIs bestätigt (Pfade unter `src/scoped_correspondence/`)

| API | Datei:Zeile | Befund |
|---|---|---|
| `mutual_information_dmc(r, Q, *, log_base=2)` | `observation/arimoto_blahut.py:196` | ✅ I(X;Y) eines festen DMC unter Prior r |
| `blahut_arimoto_capacity(Q, *, r0, tol, max_iter, log_base)` → `ArimotoBlahutResult` | `observation/arimoto_blahut.py:243` (Ergebnis `:77`) | ✅ lehnt negative / nicht zeilenstochastische Kanäle ab |
| `directed_information(joint_sequences)` → `DirectedInformationReport` | `observation/directed_information.py:277` | ✅ exakte endliche Sequenzverteilung — **normalisiert nicht normierte Eingaben still** („renormalised if needed“) |
| `broja_pid_bivariate(joint_r1r2y, *, n_starts, tol, rng)` → `BivariatePIDReport` | `information_decomposition/broja.py:420` (Ergebnis `:379`) | ✅ Achsen (r1, r2, y); **normalisiert intern still** |
| `evaluate_xor_task`, `evaluate_redundancy_task`, `evaluate_noisy_xor_task` | `validation/cooperative_agents_pilot.py:100,110,120` | ✅ vorhandene Informationskontrollen |
| `observation_fiber`, `identified_values` | `epistemic/observation_fibers.py:75,152` | ✅ endliche Kandidaten |
| `AssumptionSpec`, `FiniteDomainSpec` | `epistemic/records.py:78,104` | ✅ |
| `_EXPLICIT_CATEGORY` | `scripts/run_verification_suite.py` | ✅ |
| `docs/real_data_provenance.md` | — | ✅ |

**Befund ON0-B1:** Zwei vorhandene Informations-APIs renormalisieren
nicht normierte Eingaben still. ON-C21 verlangt dagegen, negative, nicht
normierte und nicht endliche Kanäle **zurückzuweisen**. Die ON-Adapter
(ON2/ON5) prüfen deshalb vor jedem Aufruf selbst; die bestehenden Module
bleiben unverändert (additiv). Ob sie selbst strikter werden sollen, ist
eine Entscheidung für Johann (Backlog).

### ON-C01–ON-C23 unabhängig hergeleitet

Zuerst von Hand aus dem Plantext, dann mit eigenem SCF-freiem Skript
[`verification/plan_controls/on_series_independent_controls.py`](verification/plan_controls/on_series_independent_controls.py)
(vor dem Lesen des Beilagencodes geschrieben): **23/23**
([Ergebnisse](verification/plan_controls/on_series_independent_controls_results.json)).
Zusätzlich die Beilage: 23/23.

| ID | Bestätigter Befund | Eigener Weg |
|---|---|---|
| ON-C01 | $W(1/2)$: $(3/2,1/2)$, $(1/2,3/2)$; Summe je 2; $\det W=4\delta$ | exakt, drei δ |
| ON-C02 | Vollbeobachtung 1 Bit, Summe 0 Bit; grobe Faser $\{0,1\}$; δ=0: 0 Bit | eigene MI-Funktion |
| ON-C03 | Sensorpermutation erhält 1 Bit | — |
| ON-C04 | $A^*=\tfrac12(1+\operatorname{erf}1)=0{,}9213503964748575$ | zwei äquivalente Formeln |
| ON-C05 | BSC ε=1: 1 Bit, naive Accuracy 0, optimale 1 | — |
| ON-C06 | Accuracy je 3/4: BSC $I=0{,}188722$, Z-Kanal $I=0{,}311278$, $C=\log_2(5/4)$ | Kapazität zusätzlich per Priorscan unterschritten |
| ON-C07 | $Y=(S,N)$: 1 Bit; $Z=N$: 0 Bit | — |
| ON-C08 | $Y=S\oplus H$: 0 Bit, gegeben $H$: 1 Bit | — |
| ON-C09 | Codeinvertierung: eingefroren 0, angepasst 1, Information 1 Bit | — |
| ON-C10 | Konstanter Decoder, Prior 0,9: Accuracy 0,9, balanced 0,5, Information 0 | — |
| ON-C11 | Hebb-Zeile roh $(5/8,0,1/8)$ → normiert $(5/12,0,1/12)$; Zeilensummen 1/2 | exakt |
| ON-C12 | η=0 erhält A; Schranke $1-\ell+\ell\gamma=3/4$ | — |
| ON-C13 | XOR: beste einzelne affine Schwelle 3/4, XOR-Decoder 1 | ganzzahliger Scan **plus** Widerspruchsbeweis (Summe der Ungleichungen) |
| ON-C14 | XOR-Signatur (0,0,1), Kopie (1,1,1) | eigene Randverteilungen |
| ON-C15 | $A=(U,0)$, $B=(0,U)$: gerichtete Information 1 Bit, gegeben $U$ 0, do(A₁) ändert B₂ nicht | Zerlegung $I(A_1;B_1)+I(A^2;B_2\mid B_1)$ |
| ON-C16 | Blockzeit = Label: 1 Bit; randomisiert 0 | — |
| ON-C17 | Präparatwerte 0…4: Gruppen-SEM² 1/2; gepoolt mit 100 Kopien fälschlich 2/499 | exakt |
| ON-C18 | fünf positive Differenzen: $p=2/32=1/16$ | volle Enumeration |
| ON-C19 | $1/4-3/20=1/10$ | — |
| ON-C20 | Training (0,2): Mittel 1; mit Testwert 100 fälschlich 34 | — |
| ON-C21 | negativ, nicht normiert, nicht endlich → abgelehnt | — |
| ON-C22 | N=12, γ=4/5: Zeilensumme 4/5; c=1/4, M>1: Intergewicht 1/5 | exakt für M=1,2,3 |
| ON-C23 | M=1, M=2 (c=6/11), M=3 (c=8/11): identische Matrix, Nebendiagonalen 4/55 | exakt |

**Anmerkung zu ON-C17:** Der Plan nennt die Präparatwerte nicht; die
Werte 0…4 sind die einfachste Belegung, die beide Sollwerte exakt ergibt
(festgehalten als Annahme).

### Umfang, Grenzen, Daten-Gate

- Pflicht: ON0–ON7 mit synthetischem Kern; ON6b (reale Reanalyse) ist
  **optional** und an Daten-Gates gebunden — fehlende Rohdaten blockieren
  den Kern nicht.
- Keine neue PID-, Entropie- oder Kapazitätsbibliothek; kleine Adapter
  über die bestehenden APIs.
- Benennung der Grenzen: Beobachtung (Summenbeobachter verliert alles),
  Decoder (Scoreabfall ≠ Informationsverlust), Gerichtetheit ≠ Kausalität,
  Replikationseinheit = Präparat bzw. Simulationslauf, nicht Versuch.

### Abnahme ON0 (Plan §10)

- [x] Drei-Modul-Schwelle nicht vorausgesetzt
- [x] Grenzen von Beobachtung und Decoder benannt
- [x] Daten-Gate sichtbar (ON6b optional)
- [x] keine J-Abhängigkeit erfunden (nur tatsächlich vorhandene Bausteine)
- [x] unabhängige Werte stimmen (23/23 eigen, 23/23 Beilage)
- [x] keine Produktions-API in diesem Paket

## ON1 — Exakte Beobachtungs- und Strukturkontrollen (erledigt)

`validation/modular_networks/observation_controls.py`: $W(\delta)$ exakt
(Fraction), Voll-, Summen- und permutierter Beobachter, exakte
Information im rauschfreien Modell (0 oder 1 Bit), Anschluss an die
vorhandene H3-Faser (`observation_fiber`). Funktion, Beobachtung und
Stimuluslabel sind getrennte Eingaben. Floats werden im exakten Modus
abgewiesen (Rauschen gehört nach ON2).

[`verify_organoid_observation_controls.py`](verification/verify_organoid_observation_controls.py)
4/4: ON-C01–C03; δ ∉ [0,1], falsche Dimension, nicht endliche Eingabe,
Float-δ abgewiesen; δ = 10⁻⁹ liefert rauschfrei 1 Bit — ausdrücklich
**keine** biologische Kippschwelle.

## ON2 — Messrauschen und endliche Kanäle (erledigt)

`validation/modular_networks/channels.py`: Bayes-Accuracy der
Gaußkontrolle mit expliziten σ=0-Grenzfällen; strikte Kanal- und
Priorprüfung **vor** jedem Aufruf der vorhandenen APIs (ON0-Befund B1);
`exact_channel_report` (MI am Prior über `mutual_information_dmc`,
Kapazität über `blahut_arimoto_capacity` samt `converged`) und
`estimated_channel_report` aus Zählungen: fehlende Klasse → unbekannte
Zeile, **keine** MI/Kapazität, kein Gleichverteilungs-Default;
Pseudocounts sichtbar als Annahme.

[`verify_organoid_channels.py`](verification/verify_organoid_channels.py)
5/5: ON-C04 (analytisch + Monte-Carlo-Nächster-Mittelwert, 4σ-Band;
Summenbeobachter klassengleich), ON-C05, ON-C06 (C = log₂(5/4) über BA),
ON-C07/C08, Datenverarbeitung (20 zufällige Vergröberungen fügen keine
Information hinzu), ON-C21.

## ON3 — Begrenzte adaptive Dynamik (erledigt)

`validation/modular_networks/adaptive_model.py`: Zwei-Zeitskalen-Modell,
Modulpartition, Budgetmatrix (Zeilensumme γ, c für M=1 nicht anwendbar),
dauerhafte Kantenmaske, verzögerte Hebb-Regel ohne Labels, Kontraktions-
schranke (nur eingefrorene Gewichte), getrennte RNG-Ströme in
`NetworkConfig`.

[`verify_organoid_adaptive_model.py`](verification/verify_organoid_adaptive_model.py)
5/5: ON-C11 exakt, ON-C12 (η=0 exakt; empirisches Lipschitz-Verhältnis
≤ 3/4), ON-C22, ON-C23 inkl. identischer Trajektorien, gesperrte
Interkanten und Diagonale, Budget, Probe ändert A nicht.

**Befunde:**
- **Exaktheitsfehler gefunden:** `g / m` mit Integer-Null machte die
  exakte Hebb-Rechnung still zu Float (ON-C11 schlug fehl) — behoben
  (`Fraction(g, m)`).
- **Leere Assertion entfernt:** eine eigene Prüfung enthielt `… or True`;
  ersetzt durch echte Berichtsprüfungen.
- **Drift von c wird berichtet, nicht behauptet:** Hebb erhält die
  Zeilensummen, nicht den Inter-Anteil — im Lauf mit erlaubten
  Interkanten wandert er von 0,25 bis ≈ 0,74.
- **Testlücke per Mutant gefunden:** die Maske stand doppelt (in G und in
  Ã); der erste Mutant war äquivalent, der umgezielte überlebte ebenfalls,
  weil keine Prüfung Diagonale bzw. aktive gesperrte Kanten abdeckte.
  Redundanz entfernt, exakte Ein-Schritt-Kontrolle mit Aktivität auf allen
  Zuständen ergänzt — jetzt getötet.

## ON4 — Decoder und hierarchischer Vergleich (erledigt)

`validation/modular_networks/decoders.py`: Accuracy/balanced Accuracy,
Standardisierung nur am Training, Nächster-Klassenmittelwert, konstanter
Decoder, `evaluate_split` (Produktionssplitter: überlappende Versuchs-IDs
→ Fehler; neu trainiert oder eingefroren), Präparat-Zusammenfassungen,
SEM auf Präparatebene, exakter zweiseitiger Sign-Flip-Test (n ≤ 20),
Gruppenvergleich mit Überlappungsverbot.

[`verify_organoid_decoders.py`](verification/verify_organoid_decoders.py)
5/5: ON-C09, C10, C13 (Scan auf zwei Gittern + Beweis unten), C17
(doppelte Versuche erhöhen die Präparatzahl nicht), C18, C19, C20 (gegen
den Produktionssplitter). ON-C16 liegt im Plan bei ON4, ist hier in ON5
über `label_confounding` umgesetzt.

**Beweis ON-C13:** Eine einzige Schwelle $ax+by+c>0$ müsste (0,1) und
(1,0) positiv, (0,0) und (1,1) nicht positiv klassifizieren: $b+c>0$,
$a+c>0$, $c\le0$, $a+b+c\le0$. Summe der ersten beiden: $a+b+2c>0$; Summe
der letzten beiden: $a+b+2c\le0$ — Widerspruch für alle reellen Gewichte.

## ON5 — Information, PID und Gerichtetheit (erledigt)

`validation/modular_networks/information.py`: strikte PMF-Prüfung, dann
die vorhandenen APIs: `information_signature` (maßfrei),
`pid_report` (BROJA tatsächlich ausgeführt; Konvergenz, Startzahl und
Streuung der Optima getrennt berichtet), `directed_report` (immer
`causal_claim=False`), `intervention_effect` (do() an einem deklarierten
endlichen Generator, getrennt von DI), `label_confounding`.

[`verify_organoid_information.py`](verification/verify_organoid_information.py)
4/4: ON-C14 (XOR-Synergie 1 Bit, Kopie-Redundanz 1 Bit, Abgleich mit dem
vorhandenen `evaluate_xor_task`), ON-C15 (DI 1 Bit, do(A₁) ändert B₂ nicht;
Positivkontrolle mit echtem Effekt), ON-C16, strikte Ablehnung nicht
normierter Joints (die bestehenden Funktionen würden still normieren).

## ON6a — Synthetischer Benchmark und Evidenzbericht (erledigt)

`validation/modular_networks/evaluation.py` +
[`configs/organoid_minimal.json`](configs/organoid_minimal.json)
(Konfigurations-ID `e5c9921b5aa974ad`, vor der Auswertung gespeichert;
abweichende oder fehlende Konfiguration → Abbruch). Sieben vorab
deklarierte Bedingungen × 6 Läufe (Lauf = Einheit, getrennte Seeds für
Topologie/Adaptation/Decoder/Test), Kontrast Δ = balanced Accuracy nach −
vor (neu trainierter Decoder), eingefrorener Decoder getrennt berichtet.
`OrganoidEvidenceRecord` mit allen Pflichtfeldern aus Plan §9 und nur
erlaubten Vokabular-Kombinationen. Laufzeit ≈ 2 s.

[`verify_organoid_benchmark.py`](verification/verify_organoid_benchmark.py)
5/5 — nur **Invarianten**: Vorab-Konfiguration, Determinismus,
identischer Operator unter Modulnamen (M=1 vs. M=3, c=8/11: identische
Läufe und A-Hashes), Beobachtung ändert das System nicht (gleicher A-Hash
voll vs. Summe), η=0 ohne Anpassung, Drift-Gegenbeispiel, Vokabular.

**Deskriptive Ergebnisse (kein Gate, keine Siegerbehauptung):**

| Bedingung | Δ (Mittel ± SEM, 6 Läufe) | eingefroren nach | neu trainiert nach |
|---|---|---|---|
| M3, getrennte Eingänge, voll, η=0 | 0 ± 0 | 1,00 | 1,00 |
| M3, getrennt, voll, angepasst | −0,092 ± 0,055 | 0,55 | 0,91 |
| M3, geteilte Eingänge (ein Modul), angepasst | +0,354 ± 0,086 | 0,50 | 0,88 |
| M3, getrennt, Summenbeobachtung, angepasst | +0,329 ± 0,076 | 0,50 | 0,88 |
| M1 uniform, angepasst | +0,356 ± 0,086 | 0,50 | 0,88 |
| M3, c = 8/11 (= M1-Matrix), angepasst | +0,356 ± 0,086 | 0,50 | 0,88 |
| M3, getrennt, η=0, Sensor-Umordnung | 0 ± 0 | 0,63 | 1,00 |

Lesart: Die Δ-Unterschiede folgen hier vor allem dem **Ausgangsniveau**
(getrennte Eingänge starten bei 1,0 = Decke, geteilte nahe Zufall) — genau
die Auswahlfalle aus Plan §8.4, kein Moduleffekt. Anpassung verändert den
Code (eingefrorene Decoder fallen auf ≈ Zufall), ohne dass daraus ein
Informationsverlust folgt. Das Drift-Gegenbeispiel (invertierbare
Umordnung, Information unverändert) trennt Decoderstabilität von
Information. Ein erster Versuch mit konstantem Messversatz brach den
eingefrorenen Decoder **nicht** — verworfen und als Befund festgehalten.

## ON6b — Optionaler Realdatenadapter (blockiert)

Status **`blocked`**: Es liegt kein Organoid-Datensatz mit Präparat-IDs,
Versuchslabels, Provenienz und Wiederverwendungslizenz vor; Verfügbarkeit
und Lizenz der Diagrammquelldaten von ON-S1 sind ungeprüft
([Backlog D2](DEEP_RESEARCH_BACKLOG.md)). Kein Parser mit synthetischen
Platzhaltern; die CLI verweigert `--scenario real` mit Exit-Code 2. Keine
Autorenanfrage ohne Johanns Auftrag.

## Regression

Vor den ON-Commits (Arbeitsstand ON0–ON7): `--category all` → **138/138 bestanden** (131 vorher + 7 neue ON-Prüfskripte, 13 min);
`--category links` → 0 defekte relative Links (378 geprüft). Gezielte Mutanten: **16/16** ON-Mutanten durch Inhaltsassertion getötet (Bericht danach 105 Mutanten: 104 getötet, 1 vorregistriert äquivalent); ein Masken-Mutant deckte eine Testlücke auf (siehe ON3).
