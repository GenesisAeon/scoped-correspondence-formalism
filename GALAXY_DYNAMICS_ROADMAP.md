# SCF — Galaxiendynamik, Flächendichten und prüfbare Strukturverwandtschaft — Roadmap (2026-09-26)

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/SCF_GALAXY_DYNAMICS_IMPLEMENTATION_PLAN.md`
(25. September 2026, Referenzstand `4ed0cd9`).

Johanns Auftrag (2026-09-26): "Yeah zurück zu SCF?" — direkte Fortsetzung
der Übergabe aus Abschnitt 15 des Plans ("Übernimm diese Übergabe als
additive Roadmap G0–G7. Beginne mit dem aktuellen Repository-Stand...").
Kein weiterer Rückfragebedarf zum Umfang: der Plan selbst legt Reihenfolge,
Abschlusskriterien und die G6-Blockade bereits fest.

Gleiche Disziplin wie bei B0–B7 und C0–C7: additive Module, Hand-
Nachrechnung vor Code, unabhängige Reproduktion jedes Kontrollfalls,
`verify_*.py` mit gezielten Verletzungen, volle Suiten-Regression nach
jedem Paket, negative/neutrale Ergebnisse zählen genauso wie positive.

## Pakete

| Paket | Inhalt | Abhängigkeit | Status |
|---|---|---|---|
| G0 | Quellen-, Einheiten- und Hypothesenregister | keine | ✅ erledigt |
| G1 | Sphärische Profile und getrennte Flächendichtebegriffe | G0 | ✅ erledigt |
| G2 | Exakter Homologievertrag mit Zeitabbildung | G1 | ✅ erledigt |
| G3 | Kontrollmodelle und Beobachtungsäquivalenz | G1–G2 | ✅ erledigt |
| G4 | Reproduzierbarer SPARC-Adapter | G0 | ✅ erledigt |
| G5 | Kleiner Datenpilot und Identifizierbarkeit | G3–G4 | offen |
| G6 | Quellengetreue Yoon-Reproduktion | vollständige Quelle plus G0–G3 | 🚫 blockiert (Quelle fehlt) |
| G7 | Dokumentation und Fähigkeitsbilanz | fertige Teilpakete | offen |

Reihenfolge (Plan Abschnitt 4): G0 → G1 → G2 → G3 → G4 → G5 → G7.
G6 wird eingeschoben, sobald eine vollständige Autor-, Preprint- oder
Verlagsfassung von Yoon (2026) legal beschafft ist; bis dahin bleibt es
als offener Blocker sichtbar, nicht als übersprungen oder erledigt markiert.

## G0 — Quellen-, Einheiten- und Hypothesenregister (erledigt)

Register: `docs/galaxy_dynamics_scope.md`. Jede physikalische Eingabe und
jeder behauptete Zielwert (Donato-Produkt, MOND-Flächendichte, Yoon-Wert)
trägt dort einen Status (belegt / modellabhängig / gefittet / blockiert)
mit Quelle.

Yoon-Quellenlage separat dokumentiert: `docs/yoon_2026_source_audit.md`.
Ergebnis: Volltext bei Erstellung dieser Roadmap weiterhin nicht
beschafft — nur Pressemitteilung, Abstract und DOI/PII-Referenzen liegen
vor. **G6 bleibt deshalb explizit blockiert.** G0–G5 und G7 hängen davon
nicht ab und werden unabhängig fortgeführt.

Unabhängig nachgerechnete Kontrollwerte aus Plan-Abschnitt 3.1, 6.2 und
8.2 (Python, `math`-Bibliothek, ohne den späteren Produktionscode zu
verwenden — siehe `docs/galaxy_dynamics_scope.md` Abschnitt "Unabhängig
nachgerechnete Kontrollwerte" für die volle Rechnung):

| Größe | Plan-Wert | Eigene Nachrechnung | Übereinstimmung |
|---|---:|---:|---|
| `10^(2.15±0.2)` Zentralwert | 141.25375446 | 141.2537544622754 | ✅ |
| `10^(2.24±0.09)` Zentralwert | 173.78008287 | 173.78008287493762 | ✅ |
| `Sigma_M = a0/(2 pi G)` [Msun/pc²] | 137.0180243872182 | 137.01802438721816 | ✅ |
| MOND `g/a0` bei `g_N=a0` | 1.272019649514069 | 1.272019649514069 | ✅ |
| Burkert `Sigma_col(0)` (Referenzfall) | 235.6194490192345 | 235.61944901923448 | ✅ |
| Burkert `M(<r0)/(rho0 r0^3)` | 1.597956070366127 | 1.5979560703661266 | ✅ |
| Burkert `M(<r0)` [Msun] | 2.157240694994272e9 | 2157240694.994271 | ✅ |
| Burkert `g(r0)` [m/s²] | 3.341025353735504e-11 | 3.3410253537355016e-11 | ✅ |
| Burkert `v_c(r0)` [km/s] | 55.61293113984169 | 55.61293113984166 | ✅ |

Alle neun Kontrollwerte stimmen mit dem Plan bis auf letzte Rundungsstellen
überein. Das schafft Vertrauen in die Formeln, bevor sie in G1/G2/G3 als
Code implementiert werden — es ist noch keine Implementierung.

**Keine Repository-Struktur unter `src/` oder `verification/` wurde für
G0 angelegt** — der Plan verlangt für G0 nur das Register, keinen Code.

## G1 — Sphärische Profile und getrennte Flächendichtebegriffe (erledigt)

Neu: `src/scoped_correspondence/astrophysics/` (`units.py`,
`spherical_profiles.py`), `verification/verify_galaxy_profiles.py`
(Kategorie `math`, rein synthetisch/analytisch, in `run_verification_suite.py`
explizit registriert).

Drei Halo-Profile implementiert, jeweils mit exakter geschlossener
Massenformel plus kleinwinkelstabiler Reihenentwicklung (Plan §6.2) gegen
Auslöschung nahe `x=0`:

- **Burkert** (`f(x)=1/[(1+x)(1+x^2)]`): `Sigma_col(0) = (pi/2)*mu_h`.
- **Pseudoisothermisch** (`f(x)=1/(1+x^2)`): `Sigma_col(0) = pi*mu_h`.
- **NFW** (`f(x)=1/[x(1+x)^2]`): zentrale Dichte divergiert — `mu_h` und
  `sigma_col0()` werden bewusst NICHT angeboten (`sigma_col0()` gibt
  `None` zurück); stattdessen ein eigenständig benanntes
  `scale_product() = rho_s*r_s`, das nirgends mit einem endlichen
  Zentraldichte-Produkt verwechselbar ist.

Drei getrennte Größen (Plan §6.1) bleiben durchgängig unterschiedlich
benannt: `mu_h` (Profilparameterprodukt), `sigma_col0()` (tatsächliche
zentrale Säulendichte), eine Apertur-gemittelte Projektionsdichte ist
bewusst NICHT implementiert (eigene, spätere Größe).

**10/10 Prüfungen grün** in `verify_galaxy_profiles.py`, jede gegen eine
vom Produktionscode unabhängige Route (`scipy.integrate.quad`, eigene
Handrechnung, oder Konsistenzbedingung):

- G0-Regressionsanker (Burkert-Referenzfall exakt reproduziert, inklusive
  SI-Umrechnung von `g(r0)`)
- Massen-Quadratur (Burkert/Pseudoisothermisch/NFW) bei `x` von 0.01 bis 50
- Zentrale Säulendichte per unabhängiger Linienintegration
  (`scipy.integrate.quad` bis `np.inf`)
- `pi/2`- bzw. `pi`-Faktor bestätigt und als verschieden nachgewiesen
- Positivität und Monotonie der eingeschlossenen Masse auf einem
  logarithmischen Radiusgitter
- Zentrale Grenzwerte `M(0)=0`, `g(0)=0`, `v_c(0)=0`; NFW-Zentraldichte
  bei `r=0` wirft explizit (kein stillschweigendes `inf`/`NaN`)
- Stetigkeit an der Reihen-/Geschlossene-Form-Umschaltstelle
- NFW `scale_product()` bleibt von `mu_h` streng getrennt

**Gefundene und behobene Fehler während der Implementierung** (alle vor
dem ersten grünen Lauf entdeckt, nicht nachträglich toleriert):
Vorzeichenfehler in der `pc`-Basis-Gravitationskonstante (`G_ASTRO_PC`
war fälschlich durch 1000 geteilt statt multipliziert — Faktor 10⁶-Fehler
in `g(r)` [SI], durch den G0-Regressionsanker sofort aufgedeckt);
0-dimensionale-Array-Handhabung bei skalarem `r=0` in `g()`/`circular_
velocity()` (numpy verweigert `float()` auf Shape-(1,)-Arrays); zu große
obere Integrationsgrenze (`5e6*r0` statt `np.inf`) ließ `scipy.integrate.
quad` divergent erscheinen.

Die für G1 vorgeschlagene Struktur (`src/scoped_correspondence/astrophysics/`,
`verification/verify_galaxy_*.py`) existiert damit; `verify_galaxy_observation_maps.py`,
`verify_sparc_adapter.py`, `verify_galaxy_pilot.py` folgen erst mit G3/G4/G5.

## G2 — Exakter Homologievertrag mit Zeitabbildung (erledigt)

Neu: `src/scoped_correspondence/astrophysics/galaxy_homology.py`,
`verification/verify_galaxy_homology.py` (Kategorie `math`, registriert).

Skalierungsfamilie `rho_lambda(r) = lambda^-1*rho(r/lambda)` (`HomologyScaling`)
für Burkert-Profile: `rho0 -> rho0/lambda`, `r0 -> lambda*r0`, `mu_h`
invariant. Zeitabbildung `c = sqrt(lambda)` exakt wie im gelesenen
Correspondence-Vertrag (`target_time = c*source_time`) — der Kehrwert
wäre falsch, siehe negative Kontrolle unten. Zwei getrennte,
komplementäre Prüfrouten statt einer einzigen "allgemeinen" Flow-Prüfung:

- **Kreisbahnen** (`circular_orbit_correspondence`): nutzt den
  bestehenden `Correspondence.verify_conjugacy`-Mechanismus aus
  `correspondence/contract.py` direkt (keine Neuerfindung), mit
  `T_lambda(r,theta)=(lambda*r, theta)` und analytischem Kreisbahn-Fluss
  `Phi^t(r,theta)=(r, theta+omega(r)*t)`. Ausdrücklich NICHT als
  allgemeiner Burkert-Fluss deklariert (Plan §7.2).
- **Allgemeine radiale Zustände**: algebraische Vektorfeld-Identität
  `g_source(r) = g_target(lambda*r)` (aus `DT_lambda F = sqrt(lambda)*
  F_lambda∘T_lambda` mit Jacobi-Matrix `diag(lambda,sqrt(lambda))`
  hergeleitet) — deckt "allgemeine Anfangszustände" ab, ohne einen
  ODE-Fluss zu integrieren.

**7/7 Prüfungen grün**, davon 4 negative Kontrollen, die tatsächlich eine
Verletzung erzeugen (nicht nur eine andere Benennung, Plan §7.2):

- Positivkontrolle: Plan-Referenzfall `lambda=4` exakt reproduziert
  (`M`-Verhältnis 16, `g`-Verhältnis 1, `v`-Verhältnis 2,
  Umlaufzeit-Verhältnis 2)
- Vektorfeld-Identität bei 5 `lambda`-Werten × 5 Radien
- Kreisbahn-Konjugation über `Correspondence.verify_conjugacy` bei 5
  `lambda`-Werten × 12 Zuständen × 4 Zeiten
- Negativ: falscher Zeitfaktor (`1/sqrt(lambda)` statt `sqrt(lambda)`) —
  `verify_conjugacy` meldet `ok=False`, Residuum > 1e-3
- Negativ: Vergleich bei festem statt korrespondierendem Radius — echte
  Abweichung > 0,1 %
- Negativ: geänderte Profilform (NFW statt skaliertem Burkert als "Ziel")
  — echte Abweichung > 0,1 %
- Negativ: unskalierte Punktmasse (Plan-Beispiel `G=1`) — exakt `1,25`
  statt `2` reproduziert, ko-skalierte Punktmasse stellt `2` wieder her

Volle Regression: 94/95 gruen (`verify_http_range_reader.py` isoliert
erneut lauffaehig 4/4 -- Flake unter Last, nicht durch G2 verursacht,
unveraendert seit vor G2).

## G3 — Kontrollmodelle und Beobachtungsäquivalenz (erledigt)

Neu: `src/scoped_correspondence/astrophysics/acceleration_relations.py`,
`verification/verify_galaxy_observation_maps.py` (Kategorie `math`,
registriert).

- **`effective_density(g_fn, r)`**: `rho_eff(r) = 1/(4 pi G r^2) *
  d/dr[r^2 g(r)]` (Plan §8.1), zentrale finite Differenz, modellunabhängig
  (`g_fn` beliebig). Gewinnt Burkerts eigene `density(r)` aus Burkerts
  eigener `g(r)` exakt zurück (relative Fehler 1e-8 bis 1e-12 je nach
  Radius) — die geforderte "Kugelprofil durch den Operator
  zurückgewinnen"-Kontrolle. Gibt NEGATIVE Werte unverändert zurück (Test
  mit `g~1/r^3`, überall negativ) statt sie stillschweigend auf 0 zu
  setzen.
- **`mond_g_total(g_N, a0)`**: deklarierter MOND-Kontrollfall, Standard-
  Interpolation `mu_M(x)=x/sqrt(1+x^2)`, geschlossene algebraische
  Lösung. Regressionsanker aus G0 bestätigt: `g/a0=1,272019649514069` bei
  `g_N=a0`, `g_N=0 -> g=0`, `g_N<0` wirft, `Sigma_M=137,0180243872182`
  Msun/pc². Grenzfälle `g/g_N->1` (groß) und `g/sqrt(a0*g_N)->1` (klein)
  bestätigt.
- **`mond_g_total_simple_interpolation_NOT_INTERCHANGEABLE`**: die
  alternative Funktion `x/(1+x)` implementiert und als messbar
  verschieden von der Standardfunktion bestätigt — aber die im Plan
  zitierte logarithmische Divergenz ihrer zentralen Phantom-Säulendichte
  wird NICHT numerisch nachgewiesen. Ein Versuch dazu (zentrale finite
  Differenzen über ~10 Größenordnungen im Radius, per `scipy.integrate.
  quad`) ergab instabile, auslöschungsdominierte Resultate — bewusst
  NICHT als Prüfung verschifft, weil eine konkrete Zahlenbehauptung aus
  dieser Rechnung unehrlich gewesen wäre. Die Divergenz bleibt eine aus
  Milgrom (2009) zitierte, nicht selbst nachgerechnete Aussage (Status
  siehe `docs/galaxy_dynamics_scope.md`).
- **Baselines A/B/C** (`baseline_total_g_halo`, `baseline_total_g_mond`):
  als strukturell verschieden bestätigt (paarweise Abweichung > 0,1 % bei
  gleicher Baryonenkomponente und vergleichbarer Halo-Skala).
- **Exakte Beobachtungsäquivalenz-Demonstration**: ein NFW-Profil wird
  über `scipy.optimize.fsolve` so gewählt, dass es ein festes
  Burkert-Profil bei GENAU zwei Radien exakt trifft (Residuum ~1e-13) —
  außerhalb dieser zwei Punkte weichen beide Profile um > 10 % ab. Zeigt
  konkret, dass zwei strukturell verschiedene Halo-Familien an endlich
  vielen Beobachtungspunkten ununterscheidbar sein können (Plan §8.1:
  "verschiedene Parametrisierungen können dieselbe Observable erzeugen") —
  motiviert direkt die Identifizierbarkeitsvorsicht aus G5.
- `circular_velocity_from_g(g,r) = sqrt(r*g)`: modellunabhängige
  Kreisgeschwindigkeit, bestätigt konsistent mit `BurkertProfile.
  circular_velocity` und mit einer zweiten unabhängigen Berechnung
  desselben MOND-`g`-Werts.

**7/7 Prüfungen grün.** Volle Regression: 96/96 grün (der zuvor
beobachtete `verify_http_range_reader.py`-Flake trat in diesem Lauf nicht
auf, bestätigt als Flake, nicht als Regression).

## G4 — Reproduzierbarer SPARC-Adapter (erledigt)

**Checkpoint mit Johann (2026-09-26):** vor dem Abruf echter SPARC-Daten
nachgefragt, da der Plan (§9.1) die Weiterverbreitungsrechte der
Rohdateien als ungeklärt (nicht verboten) markiert. Johanns Entscheidung
(Option 1): lokal herunterladen und das echte Byte-Schema prüfen; Quelle,
Abrufzeit, SHA-256 und Lizenzstatus "ungeklärt" dokumentieren, auch für
den lokalen Pilotlauf; Parser, Downloadanleitung, Doku und synthetische
Tests committen; Rohdaten und Ausschnitte davon vorerst außerhalb des
Repos halten. Genau so umgesetzt.

Neu: `src/scoped_correspondence/validation/sparc_data.py`,
`verification/verify_sparc_adapter.py` (Kategorie `math`, synthetische
Fixtures), `verification/verify_sparc_real_local.py` (Kategorie `data`,
echte lokale Dateien, skippt sauber mit Exit 0 wenn nicht vorhanden),
`docs/sparc_data_provenance.md` (vollständige Provenienz: Quelle,
Abrufzeitpunkt 2026-09-26T11:55:23Z, SHA-256 beider Dateien, Lizenzstatus
ungeklärt, lokaler Speicherort `D:\mandala\scf_external_data\sparc\`
außerhalb des Repos).

**Wichtiger Fund beim Abgleich mit den echten Live-Dateien:** Der eigene
gedruckte Byte-für-Byte-Header von `SPARC_Lelli2016c.mrt` (Metadatentabelle)
stimmt NICHT mit seinen eigenen Live-Daten überein — der Header nennt
Byte 12–13 für das Hubble-Typ-Feld `T`, aber alle 175 echten Datenzeilen
haben `T`s Ziffern tatsächlich bei Byte 13–14, und die Gesamtzeilenlänge
ist 131 Bytes statt der im Header implizierten 113. Reaktion: statt einem
nachweislich falschen Byte-Schema zu vertrauen, wird die Metadatentabelle
über validierte Whitespace-Tokenisierung geparst (exakt 19 Felder pro
Zeile gefordert, empirisch an allen 175 echten Zeilen bestätigt, bevor
diese Entscheidung fiel). Die Komponententabelle (`MassModels_Lelli2016c.mrt`)
wurde dagegen Byte für Byte gegen ihre eigene echte Kopfzeile bestätigt —
exakte Übereinstimmung mit Plan §9.2 — und behält den festen
Byte-Bereichs-Parser.

- **`combine_baryonic_v2`**: Plan-Beispiel `v_gas=-10, v_disk=40,
  Upsilon_d=0,5` ergibt exakt `700`, nicht `900`; zusätzlich an einer
  ECHTEN Zeile mit negativem `Vgas` ausgeführt (361 von 3391 echten
  Komponentenzeilen haben negatives `Vgas` — der Vorzeichenfall tritt in
  echten Daten tatsächlich auf, nicht nur im Lehrbuchbeispiel).
- **`scale_distance`**/**`scale_inclination`**: `g_bar=v_bar²/r`
  bestätigt entfernungsunabhängig am selben Winkelort; Inklinations-Hin-
  und-Rück-Transformation exakt reversibel.
- Validierung: doppelte Galaxiennamen (Metadaten), doppelte Radien und
  nicht-positive Radien/Fehler (Komponenten), fehlende `---`-Trennlinie —
  alle werfen klar, statt still falsch zu parsen.

**11/11 synthetische Prüfungen grün** (`verify_sparc_adapter.py`).
**5/5 echte Prüfungen grün, NICHT übersprungen** (`verify_sparc_real_local.py`,
gegen die tatsächlich heruntergeladenen Dateien: 175 Metadaten-Zeilen,
3391 Komponentenzeilen, identische Galaxienmengen in beiden Tabellen).
Volle Regression: 98/98 grün.
