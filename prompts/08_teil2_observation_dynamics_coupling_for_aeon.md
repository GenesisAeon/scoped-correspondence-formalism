Auftrag: Teil 2, Milestone 2 ("Core Extraction", Fortsetzung) —
`observation`, `dynamics`, `coupling` als echte Python-Module, mit
Legacy-Adaptern gegen die bestehenden Formeln. `correspondence`
existiert bereits (Milestone 1, gemergt) und wird hier nicht verändert.

## Kontext

`src/scoped_correspondence/correspondence/contract.py` ist gemergt
und verifiziert (5/5 gegen Legacy-Fälle e11/T01-T04). GLOSSARY.md
enthält die vollständige Begriffszuordnung. FORMALISM.md §2
("Verbindliche Notation") ist die maßgebliche Tabelle für diesen
Auftrag — jede Zeile dort wird zu genau einem typisierten Feld/einer
Konstante im jeweiligen neuen Modul, NICHT zu einer neuen,
parallelen Bedeutung.

## Umfang dieses Auftrags (bewusst begrenzt)

Drei Module, je mit Legacy-Adapter und Verifikation gegen mindestens
zwei bestehende Prüfungen/Beispiele:

### 1. `observation` (vormals CREP)

Quelle: `information_layer_crep.md`, FORMALISM.md §3 und §2-Zeilen für
`K_info`, `R_info`, `eta_info`. Mindestens:
- `channel_capacity(bandwidth, snr) -> K_info` (Shannon-Hartley,
  FORMALISM.md §3).
- `retention(mutual_information, entropy) -> R_info` mit Bereichsprüfung
  `0 <= R_info <= 1` NUR für diskrete X mit `0 < H(X) < inf` — bei
  Verletzung dieser Voraussetzung einen `ScopeViolationError` werfen,
  nicht stillschweigend einen Wert zurückgeben (siehe FORMALISM.md §3,
  "Für kontinuierliche Variablen darf H nicht ungeprüft durch
  differentielle Entropie ersetzt werden").
- `realized_rate(rate, capacity) -> eta_info`, dimensionslos, mit
  derselben Kanal-/Zeiteinheiten-Prüfung wie in FORMALISM.md §3
  beschrieben.
- Verifikation gegen: `p03_information_channel`
  (verify_formalism.py) und `c06_information_window`
  (verify_formalism.py) — Zahlen müssen exakt übereinstimmen.

### 2. `dynamics` (vormals UTAC)

Quelle: `system_layer_utac.md`, FORMALISM.md §4-§5 für `beta_response`,
`S_rec`, `lambda_L`. Mindestens:
- `sigmoid_response(u, beta_response, theta_u, p_max) -> float`
  (statische Antwortkurve, FORMALISM.md §4).
- `recovery_rate_from_relaxation(tau) -> S_rec` = 1/tau, UND ein
  expliziter Test/Kommentar, der zeigt, dass dieser Wert unabhängig
  von `beta_response` ist (das war Befund A der ursprünglichen Review
  — `beta_response` und `S_rec` dürfen im Code niemals verwechselbar
  sein, siehe GLOSSARY.md "Unit"-Zeile für `\beta_{response}` vs
  `S_rec` in FORMALISM.md §2).
- Die korrigierte kubische Normalform (`FORMALISM.md` §5:
  `tau*dx/dt = -x^3+ax+b`) mit Fixpunkten und `S_rec` an den stabilen
  Ästen sowie am instabilen Ursprung (`S_rec(0)=-a/tau`,
  `S_rec(x*)=2a/tau` für b=0).
- Verifikation gegen: `p02_cusp_region` und `p01_cusp_branches_and_time`
  (verify_formalism.py) — Fixpunkte und Vorzeichen müssen exakt
  übereinstimmen.

### 3. `coupling` (vormals AFET)

Quelle: `coupling_layer_afet.md`, FORMALISM.md §6 für `A_ij`, `L_ij`.
Mindestens:
- Ein `PairwiseCoupling`-Typ für `dot z_i = f_i(z_i,u_i) + sum_j g_ij(...)`
  (FORMALISM.md §6).
- Eine GENERIC-Strukturprüfung als eigene Funktion
  `check_generic_structure(J, M, grad_E, grad_S)`, die `J^T=-J`,
  `M^T=M>=0`, `J @ grad_S == 0`, `M @ grad_E == 0` prüft (numerische
  Toleranz dokumentieren) — KEINE automatische Behauptung, dass ein
  beliebiges Kopplungsmodell GENERIC ist, nur der Strukturtest selbst.
- **Explizit NICHT:** `A_ij` und `L_ij` in derselben Klasse oder mit
  gemeinsamer Basisklasse — das war genau die zurückgenommene Identität
  (FORMALISM.md §6: "Es gibt keine allgemeine Identität zwischen
  eta_info, Panarchy, A_ij und L_ij"). Getrennte Typen, getrennte
  Einheiten im Docstring.
- Verifikation gegen: `p06_heat_balance_and_relaxation`
  (verify_formalism.py) — Energieerhaltung/Entropieproduktion-Zahlen
  müssen exakt übereinstimmen.

## Legacy-Adapter (für alle drei Module)

Ein dünner `legacy`-Namespace, der die alten Funktionsnamen/Symbole
(aus den sieben Layer-/Erweiterungsdokumenten) auf die neuen Funktionen
abbildet, OHNE die Dokumente selbst zu ändern — reine Software-Brücke.
Beispiel: `legacy.gamma_domain_style(...)` ruft intern die neue
`observation`/`dynamics`-Funktion auf. Zweck: bestehende Worked
Examples könnten später gegen den neuen Kern laufen, ohne dass ihre
Dokumentation umgeschrieben werden muss.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_*.py` mit reproduzierbarem JSON-Report unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf FORMALISM.md §2 (Notationstabelle) — jede neue
   Funktion/Konstante referenziert ihre Zeile dort.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Bevorzugt: eigener Branch `aeon/m2-observation-dynamics-coupling` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht (Repo-
Zugriff ist jetzt eingerichtet) — kein ZIP/Manifest mehr nötig. Falls
das aus irgendeinem Grund nicht geht: ZIP mit `apply_manifest.json`
als Fallback, exakt wie bei Milestone 1.

Kein Push/Merge direkt nach `master` — nur auf den eigenen Branch.
Claude reviewed (Checksummen bzw. Diff, Skripte selbst nachrechnen,
mindestens einen Fall pro Modul von Hand gegenprüfen) und merged erst
nach Johanns OK.
