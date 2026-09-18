Auftrag: Teil 2, Milestone 20 ("Profile Likelihood") — natürliche
Erweiterung von `identifiability`, aus `ChatGPTAstra3.md` (Raue et al.
2009, DOI 10.1093/bioinformatics/btp358, von Claude gegen die Quelle
geprüft).

## Kontext

`identifiability` (M5, gemergt) hat bereits SVD/Konditionierungs-
Diagnostik und `parameter_scaling_invariance`/`identifiability_jacobian_rank`
(strukturelle Nichtidentifizierbarkeit, `σ·a`-Kollinearität). Profile
Likelihood (Raue et al. 2009) liefert die PRAKTISCHE Ergänzung: für
jeden Parameter `θ_i` wird über alle anderen Parameter neu optimiert:

\[
\chi^2_{PL}(\theta_i)=\min_{\theta_{j\ne i}}\chi^2(\theta).
\]

Ein FLACHES Profil (kein eindeutiges Minimum entlang `θ_i`) zeigt
strukturelle Nichtidentifizierbarkeit; ein Profil mit endlichem
Konfidenzintervall zeigt praktische Identifizierbarkeit.

## Umfang dieses Auftrags

### 1. `identifiability.profile_likelihood.profile_parameter(chi2_fn, theta_fixed_index, theta_init, fixed_values)`

Für eine gegebene `χ²`-Funktion (Callable) und einen festzuhaltenden
Parameterindex: minimiert über die restlichen Parameter für jeden Wert
in `fixed_values`, liefert das Profil (Liste von `(fixed_value,
chi2_min)`-Paaren).

### 2. `identifiability.profile_likelihood.classify_identifiability(profile, atol)`

Klassifiziert ein Profil als `"flat"` (strukturell nichtidentifizierbar
— Varianz des `chi2_min` über das Profil `< atol`) oder
`"identifiable"` (endliches Minimum mit messbarer Krümmung).

### 3. `identifiability.profile_likelihood.likelihood_interval(profile, threshold)`

Extrahiert das Konfidenzintervall (Werte von `θ_i`, für die
`chi2_min <= threshold`) — bei einem flachen Profil ist das Intervall
unbeschränkt (explizit als solches berichten, nicht stillschweigend
abschneiden).

### 4. Durchgerechnetes Beispiel (bereits von Claude bestätigt)

**Nichtidentifizierbar:** Modell `y=θ1·θ2`, Beobachtung `y=6`,
`χ²(θ1,θ2)=(θ1·θ2-6)²`. Profil über `θ1∈{1,2,3,4,5}`: für jedes `θ1`
liefert `θ2=6/θ1` exakt `χ²=0`. Profil ist FLACH (`chi2_min=0` für
alle getesteten `θ1`) → `classify_identifiability` muss `"flat"`
liefern.

**Identifizierbar (Kontrollfall, Pflicht):** ein zweites Modell mit
eindeutigem Minimum (z.B. `χ²(θ)=(θ-3)²`, oder ein quadratisches
Modell mit zwei Parametern, die NICHT kollinear sind) — Profil zeigt
ein klares Minimum mit endlichem Konfidenzintervall.
`classify_identifiability` muss `"identifiable"` liefern.

### 5. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `identifiability/core.py` — eigenes, separates
  Modul.
- Kein allgemeiner nichtlinearer Optimierer für beliebige ODE-Modelle
  — die beiden oben genannten, algebraisch einfachen `χ²`-Fälle
  genügen für dieses Milestone.
- Keine Verbindung zu `identifiability_jacobian_rank`/SVD als
  gemeinsame Formel — Profile Likelihood bleibt eine eigenständige,
  komplementäre Diagnose (lokale Krümmung vs. globale Profilstruktur,
  wie in der Quelle beschrieben), keine Gleichsetzung.

## Verifikation

`verify_profile_likelihood_core.py`: (1) `θ1·θ2=6`-Fall: `chi2_min=0`
für alle getesteten `θ1`-Werte, `classify_identifiability="flat"`,
unbeschränktes Intervall, (2) Kontrollfall: `classify_identifiability=
"identifiable"`, endliches Intervall mit konkreten Grenzen aus dem
Skriptlauf.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_profile_likelihood_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Raue et al. 2009 (DOI oben) und
   `identifiability/core.py`s bestehende SVD-/Konditionierungs-
   Diagnostik (nur als Kontext, keine gemeinsame Formel).
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m20-profile-likelihood` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 17 (`information_decomposition`), 18 (`thermo`)
und 19 (`contextuality`) bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
