# Offene Punkte für eine spätere DeepResearch-/Volltextrecherche

Gesammelt während der J-, MU- und Kandidatenserien (ab 2026-10-01) auf
Johanns Wunsch: Was mit einfachem Abruf **nicht** belastbar geprüft werden
konnte, wird hier festgehalten statt stillschweigend als geprüft geführt.
Jeder Eintrag nennt, was fehlt, warum es zählt und welches Paket darauf
wartet. Erledigte Punkte werden mit Datum abgehakt, nicht gelöscht.

Lizenz: CC BY 4.0.

## A. Fehlende Artefakte (keine Recherche, sondern Nachlieferung)

- [ ] **Begleitskript `independent_controls.py`** zum Myonium-Plan und
  zur Kandidatenbewertung („29/29“: 17 MU- + 12 TP/SK/SA-Gruppen). Liegt
  nicht im Eingangsordner. Ohne es sind die MU-/Kandidatenwerte nur durch
  eigene Herleitung abgesichert (MU: 17/17 eigen). *Wartet:* nichts
  blockiert, aber der Zweitabgleich fehlt.

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

## E. Entscheidungen für Johann (keine Recherche)

- [ ] `closure/error_bounds.transient_reduction_bound` rechnet TV als halbe
  L1-Schranke ohne Prüfung, dass Lifting und $p_0$ Wahrscheinlichkeiten
  sind (J11-Befund). Im J11-Adapter abgefangen; soll die bestehende
  Funktion selbst eine Prüfung bekommen (verändert ein verifiziertes
  Modul)?
- [ ] `epistemic/reporting.report_to_json` erlaubt NaN/Infinity (J0-Befund
  B2): auf `allow_nan=False` umstellen? Würde bestehende Berichte
  betreffen.
