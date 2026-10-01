# Gepaarte Prognosevergleiche mit bedingter Inferenz (J1)

Paket J1 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §7. Code: `src/scoped_correspondence/validation/forecast_comparison.py`
(Kern) und `src/scoped_correspondence/validation/forecast_comparison_pilot.py`
(Realdatenpilot). Prüfungen: `verification/verify_forecast_comparison.py`
(math) und `verification/verify_forecast_comparison_noaa.py` (data).
Lizenz der Dokumentation: CC BY 4.0.

## 1. Was die Funktion beantwortet — und was nicht

`compare_paired_forecasts` beantwortet: *Wie groß ist der mittlere
Verlustunterschied zweier Modelle auf denselben Beobachtungen, mit
demselben Horizont und derselben Informationsmenge — und darf dafür
eine asymptotische DM-Referenz verwendet werden?*

Sie beantwortet **nicht**, welches Modell „wirklich“ besser ist. Ein
Diebold–Mariano-Test ist eine bedingte Inferenz über gepaarte
Verlustdifferenzen unter Zeitreihenannahmen (Stationarität bzw. schwache
Abhängigkeit, endliche Momente). Effektgröße, Untersuchungsdesign und
praktische Bedeutung bleiben eigene Größen. „Kein signifikanter
Unterschied“ ist **kein** Nachweis der Gleichwertigkeit
(`equivalence_tested` ist immer `False`; eine Äquivalenzprüfung mit
praktischer Toleranz wäre eine spätere eigene Funktion).

## 2. Datenvertrag: Paarung

`pair_raw_predictions` verbindet die rohen `RawHorizonPrediction`-Listen
zweier Modelle aus `rolling_origin.raw_predictions_by_horizon_step` über
den Schlüssel `(origin, step)`. Gleicher Ursprung heißt gleiche
verfügbare Informationsmenge.

| Situation | Ergebnis |
|---|---|
| Schlüssel nur auf einer Seite | `excluded`, Grund `missing_partner_in_model_a/b` — gezählt, nicht still entfernt |
| nicht endlicher Wert | `invalid`, Grund `non_finite_value` |
| gleicher Schlüssel, verschiedene Beobachtung | **Eingabefehler** (`ScopeViolationError`) |
| doppelter Schlüssel auf einer Seite | Eingabefehler |
| gleiche Modell-ID für A und B | Eingabefehler |

`PairedForecastRecord` trägt `series_id`, `origin`, `target_time`,
`horizon`, Beobachtung, beide Vorhersagen, Modell-, Daten- und
Split-IDs. Der Bericht nennt die angefragten, gepaarten, ausgeschlossenen
und ungültigen Punkte.

## 3. Mathematischer Kern

$d_t=L(y_t,\hat y_{A,t})-L(y_t,\hat y_{B,t})$ mit einer **vorab
benannten** Verlustfunktion (`squared_error` oder `absolute_error`; kein
beliebiges Callable, damit jedes Ergebnis aus seinem gespeicherten
Verlustnamen reproduzierbar bleibt). Ein negativer Mittelwert spricht
*im ausgewerteten Design* für A.

Bartlett-HAC mit der endlichen Konvention aus Plan §7 (Divisor $n$ für
jede Autokovarianz):

$$\hat\gamma_\ell=\frac1n\sum_{t=\ell+1}^n(d_t-\bar d)(d_{t-\ell}-\bar d),\qquad
\hat V=\hat\gamma_0+2\sum_{\ell=1}^{L}\Bigl(1-\frac{\ell}{L+1}\Bigr)\hat\gamma_\ell,\qquad
DM=\frac{\bar d}{\sqrt{\hat V/n}}.$$

`bartlett_hac_long_run_variance` rechnet für `Fraction`-Eingaben exakt
(J-C01: $\hat V=25/16$, Standardfehler $5/8$, DM $4/5$ — ein
Arithmetiktest, keine Rechtfertigung einer Asymptotik bei vier Punkten).

## 4. Anwendbarkeit wird deklariert, nicht behauptet

`InferenceApplicability` ist die **Erklärung des Aufrufers** mit
Begründungstext. Inferenzfelder (`long_run_variance`, `standard_error`,
`dm_statistic`, `p_value_two_sided`, `confidence_interval`) werden nur
gefüllt, wenn keiner dieser Gründe vorliegt:

| Grund | Bedeutung |
|---|---|
| `applicability_not_declared` | keine begründete Anwendbarkeitserklärung |
| `nested_models` | verschachtelte Modelle: DM ist dafür kein Auswahltest |
| `structural_break_suspected` | Strukturbruch vermutet |
| `temporal_order_unclear` | zeitliche Ordnung unklar |
| `series_too_short(n<…)` | kürzer als die **deklarierte** Mindestlänge (kein Standardwert — die Länge ist eine Designentscheidung, keine Konstante) |
| `lag_not_smaller_than_n` | HAC-Lag nicht kleiner als $n$ |

Der deskriptive Vergleich (mittlere Verluste, Differenz, Richtung) bleibt
in jedem Fall erhalten. Bei null oder numerisch unbrauchbarer
Langfristvarianz lautet der Status `degenerate_variance` — **nie** `p=0`
und nie ein automatischer Sieger. Für Gleitkommaeingaben gilt dabei die
numerische Schutzschwelle $\hat V\le10^{-12}\cdot\overline{d^2}$; ohne sie
erzeugen mathematisch konstante, nur in den letzten Bits schwankende
Differenzen einen Schein-DM in der Größenordnung $10^{15}$ (in
`verify_forecast_comparison.py` als Mutationstest belegt).

**Horizonte und Serien:** Ergebnisse entstehen je `(series_id, horizon)`.
Überlappende Horizonte werden nie zu einer Stichprobe zusammengelegt,
verschiedene Serien (Einzugsgebiete, Galaxien) nie zu einer künstlichen
Zeitreihe verkettet. Die Lagwahl ist pro Aufruf zu begründen
(`lag_justification`); $h-1$ ist keine universell ausreichende Wahl.

**Mehrfachtests:** `holm_adjust` (Holm 1979, Rückgabe in
Originalreihenfolge, exakt für `Fraction`; J-C02: $(0{,}01;0{,}04;0{,}03)
\mapsto(0{,}03;0{,}06;0{,}06)$). `holm_adjust_family` korrigiert nur eine
**vorab deklarierte** Familie (`DeclaredTestFamily`): Ergebnisse
außerhalb der Familie oder fehlende Mitglieder sind Eingabefehler;
Mitglieder ohne Inferenz machen die Familie `incomplete_family` statt sie
still zu verkleinern; eine nicht vorab deklarierte Familie bekommt
`not_predeclared` und keine korrigierten Werte. Eine explorative
Nachauswahl der besten von vielen Konfigurationen wird durch keinen
einzelnen p-Wert repariert.

**Siegerformulierung:** `describe_comparison` erzeugt den einzigen
vorgesehenen Ergebnissatz; er nennt immer Serie und Zeitraum (Ursprünge),
$n$, Horizont, Verlust, Effektgröße und Inferenzstatus.

## 5. Realdatenpilot: NOAA-Jahresanomalie

**Vorab festgelegtes Design** (im Code fixiert, bevor ein Ergebnis
betrachtet wurde): Daten `data/noaa_global_temp_anomaly_1880_2025.csv`
(SHA-256 gegen `data/real_data_manifest.json` geprüft, Public Domain);
Modell A = linearer Trend über die letzten 30 Jahre, Modell B =
Persistenz (beide bereits in `validation/noaa_temp_pilot.py`, an jedem
Ursprung nur mit Daten bis zum Ursprung neu angepasst); jährliche
Ursprünge ab 1960; Horizonte $h=1$ und $h=5$ getrennt; quadratischer
Fehler; Lag $\max(h-1,\lfloor4(n/100)^{2/9}\rfloor)$.

**Warum das Primärergebnis deskriptiv ist:** Die Reihe ist eine
einzelne, trendbehaftete Realisierung des Klimasystems. Ob die
Verlustdifferenzen 1960–2025 annähernd stationär sind, ist nicht belegt.
Das Design trägt die DM-Annahmen daher nicht nachgewiesen — das korrekte
Primärergebnis ist eine deskriptive Auswertung (Plan §7). Zusätzlich wird
ein **ausdrücklich bedingtes** Ergebnis berichtet, bei dem Stationarität
*angenommen* wird; es steht neben dem Primärergebnis, nie an seiner
Stelle.

| Horizont | $n$ | mittl. Verlust A | mittl. Verlust B | Differenz A−B | Primär | bedingt (angenommene Stationarität) |
|---|---:|---:|---:|---:|---|---|
| 1 | 65 (1960–2024) | 0,011557 | 0,013411 | −0,001854 | deskriptiv: A niedriger | Lag 3, DM −1,04, p 0,30, 95 %-KI [−0,00533; 0,00163] |
| 5 | 61 (1960–2020) | 0,016222 | 0,029216 | −0,012995 | deskriptiv: A niedriger | Lag 4, DM −3,64, p 0,00027, 95 %-KI [−0,0200; −0,0060] |

(Einheiten: °C² für die Verluste.) Lesart: Auf dieser Reihe hatte der
30-Jahre-Trend bei beiden Horizonten den geringeren mittleren
quadratischen Fehler; unter der *nicht geprüften* Stationaritätsannahme
wäre der Unterschied bei $h=5$ deutlich, bei $h=1$ nicht von null
unterscheidbar — was keine Gleichwertigkeit bedeutet. Die beiden
Horizonte wurden nicht als Testfamilie vorab deklariert; es gibt daher
keine Mehrfachtestkorrektur, und die bedingten p-Werte sind einzeln zu
lesen.

Die mittleren Verluste stimmen mit dem bestehenden
`rolling_origin.error_by_horizon_step` (RMSE²) überein, der bedingte DM
mit einer im Prüfskript unabhängig geschriebenen NumPy-HAC-Rechnung
(beides auf $10^{-10}$ relativ).

## 6. Quellen

S01 Diebold & Mariano (1995), S02 Diebold (2015), S03 Newey & West,
S04 Holm (1979) — Links siehe Plan §21. In J1 wurde geprüft, dass die
DOIs bzw. Links auflösen (doi.org → Taylor & Francis für S01/S02, NBER
t0055 und Holm-PDF HTTP 200); ein Volltextaudit wird nicht behauptet. Die
implementierte endliche HAC-Konvention ist oben vollständig
ausgeschrieben und an J-C01 exakt geprüft.
