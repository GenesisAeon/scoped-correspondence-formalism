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
| G2 | Exakter Homologievertrag mit Zeitabbildung | G1 | offen |
| G3 | Kontrollmodelle und Beobachtungsäquivalenz | G1–G2 | offen |
| G4 | Reproduzierbarer SPARC-Adapter | G0 | offen |
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
`verification/verify_galaxy_*.py`) existiert damit; `verify_galaxy_homology.py`,
`verify_galaxy_observation_maps.py`, `verify_sparc_adapter.py`,
`verify_galaxy_pilot.py` folgen erst mit G2/G3/G4/G5.
