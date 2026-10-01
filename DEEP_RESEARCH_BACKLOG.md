# Offene Punkte für eine spätere DeepResearch-/Volltextrecherche

Gesammelt während der J-, MU- und Kandidatenserien (ab 2026-10-01) auf
Johanns Wunsch: Was mit einfachem Abruf **nicht** belastbar geprüft werden
konnte, wird hier festgehalten statt stillschweigend als geprüft geführt.
Jeder Eintrag nennt, was fehlt, warum es zählt und welches Paket darauf
wartet. Erledigte Punkte werden mit Datum abgehakt, nicht gelöscht.

Lizenz: CC BY 4.0.

## A. Fehlende Artefakte (keine Recherche, sondern Nachlieferung)

- [x] **Begleitskript `independent_controls.py`** zum Myonium-Plan und zur
  Kandidatenbewertung — nachgeliefert mit dem Review (2026-10-01) in
  `SCF_MYONIUM_UND_KANDIDATEN_CLAUDE_PAKET.zip` (SHA-256 geprüft, frischer
  Lauf 29/29 identisch). Gegenprobe gegen die **Produktion**:
  [`verify_mu_candidate_oracle_crosscheck.py`](verification/verify_mu_candidate_oracle_crosscheck.py)
  — 21 Gruppen stimmen (13 MU, 4 TP, 4 SK; rel. 1e-12, MU-C02 exakt);
  MU-C07/C11/C15/C17 ohne direkte Produktions-API (nur eigene Herleitung),
  SA-C01..C04 nicht anwendbar (SA0 nur Dokumentation). Kein Widerspruch zu
  den eigenen MU-Werten.

## B. Myonium (MU-Serie)

- [ ] **MU-S1 Volltext** (Zhang et al., Nature Physics 2026): die
  tatsächlich berichtete Geschwindigkeit (~2180 m/s) samt Breite der
  Geschwindigkeitsverteilung, Ratenreferenz, Nachweiseffizienz und die
  verwendete Geometrie-/Faktorkonvention (Einzelbahn $aT^2/2$ vs.
  relative Verschiebung $aT^2$ vs. Phase $2\pi aT^2/d$). *Wartet:* MU2,
  MU6-Kalibrierung.
- [ ] **MU-S2 vs. MU-S1:** Unterschiede zwischen arXiv-Vorabfassung und
  Verlagsfassung (Zahlen, Unsicherheiten, Formeln). *Wartet:* MU6.
- [ ] **MU-S5 Dateninhalt:** Spaltenschema, Einheiten, Version der CSV;
  welche Strahl-/Detektorparameter enthalten sind. Lizenz bereits geprüft:
  InC-NC → nur lokal, nicht einchecken. *Wartet:* MU6 (sonst `deferred`).
- [ ] **MU-S3 Volltext** (Antognini et al., *Atoms* 2018, Verlag blockt
  Abruf; arXiv erreichbar): Interferometergeometrie und historische
  Strahlannahmen, nur als Kontext. *Wartet:* MU-Doku, nicht blockierend.

## C. J-Serie: Quellen nur auf Auflösbarkeit/Metadaten geprüft

Für S01–S16 wurde bisher geprüft, dass DOIs/Links auflösen bzw. die
bibliografischen Metadaten stimmen — **kein Volltextaudit**. Vor J7–J10
sollten mindestens diese Stellen im Volltext abgeglichen werden:

- [ ] **S13** Tibshirani et al. (2019), gewichtetes Conformal: genaue
  Quantilkonvention bei Gleichstand und die Split-Variante der Garantie.
  *Wartet:* J8.
- [ ] **S14** Rubenstein et al. (2017), Definition 3 (exakte
  Transformation, surjektive ordnungserhaltende Interventionsabbildung):
  genaue Ordnungsdefinition. *Wartet:* J9 (J0-Befund B3 hängt daran).
- [ ] **S15** Pearl & Bareinboim (2014), Definition 8 / Korollar 1
  (S-Admissibilität, Standardisierung). *Wartet:* J10.
- [ ] **S11/S12** Saltelli 2010 / Kucherenko 2012: Schätzerkonventionen
  (Normierung, Varianzschätzer) der Pick-Freeze-Formeln. *Wartet:* J7.
- [ ] **S06** Chen et al. (2018), Autorenfassung bei HKU blockt Abruf;
  Crossref-Metadaten bestätigt. Nur Kontext. *Nicht blockierend.*

## D. Kandidatenbewertung (Polyeder / Sakurai / Saturn)

- [ ] **Mizhaev, arXiv:2609.17700**: vollständige Koordinatenkonstruktion
  (laut Bewertung scheiterte schon dort der Volltextabruf). *Wartet:* TP3
  (optional); TP0–TP1 nicht blockiert.
- [ ] **Röst & Vígh, arXiv:2609.32998**: Kombinatorik der doppelt
  benachbarten Flächen (Achterzyklus vs. zwei Viererzyklen) für einen
  späteren exakten Vergleich. *Wartet:* TP1-Dokumentation (Kontext).
- [ ] **Marcolino et al., MNRAS 2026 (Sakurai)**: Beobachtungsepochen,
  gemessene vs. angenommene Parameter für die SK0-Quellenmatrix.
  *Wartet:* SK0.
- [ ] **Yadav & Bloxham 2020, Fletcher et al. 2018 (Saturn)**: Größen-
  und Bezugssystemregister (Gas, Muster, Rotation, Höhe). *Wartet:* SA0.

## D2. Organoid-Netzwerke (ON-Serie)

- [ ] **ON-S1 Volltext** (Chow et al., Communications Biology 2026):
  Präparatzahlen je Konfiguration, Auswahlregel der Eingangspaare,
  Trainings-/Testaufteilung, Konnektivitätsschätzer — bisher nur laut Plan,
  hier nur Titel/Datum geprüft. *Wartet:* ON6a-Dokumentation (Kontext).
- [ ] **ON-S1 Daten:** Verfügbarkeit, Format, Lizenz der verlinkten
  Diagrammquelldaten und etwaiger Rohsignale (MEA-Spikezüge, Versuchslabels,
  Präparat-IDs). *Wartet:* ON6b (sonst `deferred`).

## E. Entscheidungen für Johann (keine Recherche)

Stand nach Followup-Review-Fix `SCF_REVIEW_J_SERIES_6b3a331_CLAUDE.md`, 2026-10-01: Das Review hat drei der vier Punkte mit konkreten
Gegenbeispielen bestätigt und Empfehlungen gegeben; diese sind umgesetzt
(rückgängig machbar, je mit Regressionstest und Mutant).

- [x] **DI/BROJA normalisieren still** (ON0-Befund B1).
  - *R4 umgesetzt:* Nicht endliche Massen und überlaufende Summen werden
    früh abgelehnt. Vorher verschwand eine NaN-Masse in
    `directed_information` stillschweigend.
  - *PMF-Modus umgesetzt (2026-10-01):* nach der Empfehlung des Folgereviews
    `SCF_FOLLOWUP_REVIEW_637bc1c` §5 als zusätzlich wählbarer Modus
    `input_mode="pmf"`.
    - Exakte Eingaben müssen genau 1 ergeben, Floats 1 ± 1e‑12.
    - Seit dem PMF-Review `SCF_PMF_REVIEW_51b1a38` (PMF1) werden alle
      Originalmassen streng auf Nichtnegativität geprüft, Brüche exakt.
      Vorher kam eine exakt normierte Masse mit Vorzeichen durch.
    - Standard bleibt `"weights"`, keine Aufrufer-Migration nötig.
    - Der Bericht nennt `input_mode` und `input_total_mass`.
- [x] **`transient_reduction_bound`** (R1/R2 + TV-Vertrag): falsche
  Nullschranke im allgemeinen CTMC-Zweig behoben (`expm1`, Grenzfall
  φ(t,0)=t); volle Dynamik muss Markov sein (P zeilenstochastisch, Q
  Generator), sonst `ScopeViolationError`; TV nur mit Wahrscheinlichkeits-
  vertrag; Quellenfassung auf arXiv v3 korrigiert. Allgemeine L1-Reduktion
  bleibt unterstützt. Siehe `docs/error_bounds_core.md`.
- [x] **`report_to_json`** (E3): striktes JSON (`allow_nan=False`); ±∞ als
  Marker `{"__nonfinite__": "+inf"|"-inf"}` (unbeschränkt), NaN abgelehnt
  (ungültig; „unbekannt“ gehört als `None` ins Datenmodell). Migration: vorher
  nacktes `NaN`/`Infinity` (kein gültiges JSON); die Audit-CLI erzeugt keine
  solchen Werte.
- [x] **`calibrate_split_conformal`** (E4): α als `Fraction`, `int` oder
  Dezimalstring exakt; Float-α bedeutet seinen exakten Binärwert (Rang exakt
  per `Fraction`, kein Epsilon). `0.7` → q = 4 (unverändert), `Fraction(7,10)`
  bzw. `"0.7"` → q = 3.

  **Korrektur (Folgereview `SCF_FOLLOWUP_REVIEW_637bc1c`, F2):** Die frühere
  Aussage „für Float-Eingaben im Scan n ≤ 59 keine Rangänderung“ war
  **falsch**. Der damalige Scan enthielt nur acht α-Werte, darunter weder
  0,3 noch 0,15.

  Ein vollständiger Scan über α ∈ {0,01 … 0,99} und n ≤ 1000 (99.000 Paare)
  ergibt 825 Rangänderungen bei 32 α-Werten:
  - 764 Fälle mit größerem Rang, z. B. 0,3 bei n = 9: 7 → 8;
  - 61 Fälle mit kleinerem Rang, bei α = 0,19 und 0,44–0,46, z. B. 0,44 bei
    n = 24: 15 → 14. Dort war die alte Float-Rechnung überkonservativ.

  Der neue Rang ist immer der minimale gültige Rang für den übergebenen
  Binärwert, die Garantie bleibt also erhalten.

  Die einzigen Aufrufer im Repo sind die drei Prüfskripte
  `verify_conformal_prediction_core.py`, `verify_metamorphic_relations.py`
  und `verify_weighted_conformal.py`. Sie liefern mit alter und neuer
  Funktion identische Ergebnisse, inklusive der berichteten J8-Abdeckungen.
  Kein veröffentlichtes Resultat ändert sich.
