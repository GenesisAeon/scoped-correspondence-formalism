Auftrag: Teil 2, Milestone 13 ("Split Conformal Prediction") —
natürliche Erweiterung von `validation`, aus `ChatGPTAstra3.md`
(Lei, G'Sell, Rinaldo, Tibshirani, Wasserman 2018, DOI
10.1080/01621459.2017.1307116, von Claude gegen die Quelle geprüft).

## Kontext

`validation` (M6, gemergt) implementiert bisher nur den konkreten
Cygnus-Piloten (`DatasetManifest`, `split_epochs`,
`persistence_baseline`, `ValidationReport`). Split Conformal Prediction
ergänzt eine allgemeine, verteilungsfreie Methode für
Vorhersageintervalle mit endlicher Coverage-Garantie unter
Austauschbarkeit — passt direkt zur bereits etablierten Kalibrierungs-/
Holdout-Disziplin dieses Moduls.

## Umfang dieses Auftrags

### 1. `validation.conformal.calibrate_split_conformal(residuals, alpha)`

Für Kalibrierungs-Residuen `R_i=|Y_i-f̂(X_i)|` und Signifikanzniveau
`alpha`: berechnet das Quantil `q` als den `⌈(n+1)(1-alpha)⌉`-ten
sortierten Wert der Residuen (Finite-Sample-Korrektur, NICHT das
naive `(1-alpha)`-Quantil — muss die `+1`/Ceiling-Korrektur exakt
umsetzen und im Docstring begründen, warum ein naives Quantil die
Coverage-Garantie verletzen würde).

### 2. `validation.conformal.predict_interval(y_hat, q)`

Liefert `C(x) = [ŷ-q, ŷ+q]`.

### 3. `validation.conformal.SplitConformalReport`

Typisiertes Ergebnis: `alpha`, `quantile`, `calibration_size`,
`coverage_kind="marginal_exchangeable"` (NICHT "guaranteed" oder
"exact" — die Garantie gilt marginal unter Austauschbarkeit, nicht
pro Punkt; das muss im Docstring explizit stehen).

### 4. Durchgerechnetes Beispiel (bereits von Claude vorab bestätigt)

Kalibrierungs-Residuen `R=(1,1,2,3)`, `alpha=0,2`. Bei `n=4` liegt der
finite-sample Rang bei `⌈(n+1)(1-alpha)⌉=⌈4⌉=4` — der 4. sortierte Wert
von `(1,1,2,3)` ist `3`, also `q=3`. Für `ŷ=10`: `C(x)=[7,13]`. Diese
Zahlen im Skript exakt reproduzieren.

### 5. Anti-Leck-Schutz (Pflicht, nicht optional)

`validation.conformal` muss einen expliziten Test/Guard enthalten, der
sicherstellt, dass Kalibrierungs- und Holdout-Zeilen sich NICHT
überlappen (analog zu `validation.split_epochs`s Anti-Data-Snooping-
Guard aus M6 — gleiches Prinzip, hier für Conformal-Kalibrierung
angewandt). Test-ID-Vorschlag: `VAL-CONF-LEAK-001`.

### 6. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `validation/core.py` (Cygnus-Pilot-Code) — nur
  neues, separates Modul `validation/conformal.py`.
- Keine Anwendung auf den Cygnus-Datensatz selbst — reines,
  eigenständiges Verfahren mit synthetischem/direktem Zahlenbeispiel.
- Keine Weighted/Adaptive-Conformal-Varianten — nur die Basis-Split-
  Conformal-Methode aus der zitierten Quelle.

## Verifikation

`verify_conformal_prediction_core.py`: keine bestehende Legacy-
Prüfung — frisches Beispiel. Prüfungen: (1) `q=3` für das obige
Beispiel exakt reproduziert, (2) `C(10)=[7,13]` exakt, (3) Anti-Leck-
Guard löst bei überlappenden Kalibrierungs-/Holdout-Indizes aus, (4)
ein zweites, unabhängiges Zahlenbeispiel mit anderem `alpha`/anderen
Residuen zur Gegenprobe.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_conformal_prediction_core.py` mit reproduzierbarem
   JSON-Report unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Lei et al. 2018 (DOI oben) und
   `validation/core.py`s bestehende Kalibrierungs-/Holdout-Disziplin.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m13-conformal-prediction` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 11 (`closure`) und Milestone 12 (`coupling`)
bearbeitet werden. Claude reviewed jeden Branch einzeln und merged erst
nach Johanns OK.
