# Modul-Fähigkeitsübersicht

Kompakte, pro Modul gleich strukturierte Übersicht — Fragestellung,
Modellklasse, Voraussetzungen, Evidenzart, Prüfsammlung, bekannte Grenzen.
Geschrieben 2026-09-24 als Antwort auf Astras Konsolidierungsvorschlag
(`prompts/Answers/nicht_stationäre_Treiber/SCF_Faehigkeiten_und_Ausbauplan_2026-09-24.md`,
Priorität 0): **jede starke README-Aussage soll auf eine hier begründete,
entsprechend begrenzte Aussage zurückführen**, nicht umgekehrt.

Maschinenlesbare Fassung (identischer Inhalt, für Tooling/CI):
[capability_overview.json](capability_overview.json).

Diese Übersicht ersetzt keine Einzeldokumentation — jedes Modul mit
Realdaten-Piloten (Energiebilanz, COVID, Erdbeben) hat weiterhin ein
eigenes ausführliches `docs/*.md`. Sie beantwortet nur: *was kann ich mit
diesem Modul konkret untersuchen, worauf beruht das, und wo hört die
Aussagekraft auf?*

| Modul | Fragestellung | Evidenzart | Prüfsammlung | Wesentliche Grenze |
|---|---|---|---|---|
| `correspondence/` | Erhalten Zustands-/Zeitabbildung die Dynamik, wie groß ist das Residuum? | analytisch + synthetische Stichproben | `verify_correspondence_core.py`, `verify_approximation_core.py` | Zertifikat auf Stichproben ≠ globale Äquivalenz |
| `observation/` | Welche Information bleibt erhalten, ist redundant/synergistisch? | analytisch + synthetisch | `verify_observation_core.py`, `verify_arimoto_blahut_capacity.py`, `verify_directed_information_core.py` | Kein Realdatensatz; Ergebnis hängt von gewählter Verteilung/Zerlegung ab |
| `dynamics/` | Wie erzeugen Rückkopplung, Erholung, Treiberrate Übergänge? | gemischt: analytische Normalformen + 2 Realdaten-Piloten (Mauna-Loa-CO2/NOAA, USGS) | `verify_dynamics_core.py`, `verify_rate_dependent.py`, `verify_energy_balance.py`, `verify_etas.py`, u.a. (11 Skripte) | χ-Diagnose ist richtungssicher, aber ihre Schwelle ist rastergebunden, nicht exakt; Energiebilanz-Parameter C_s/C_d/alpha auf ±50%-Fenster schwach eingeschränkt |
| `coupling/` | Welche Kopplungen bilden Einfluss/Transport/Energieerhaltung/Dissipation ab? | analytisch | `verify_coupling_core.py`, `verify_casimir_residual.py`, u.a. (6 Skripte) | Strukturprüfung an Einzelbeispielen ≠ physikalische Validierung beliebiger Systeme |
| `closure/` | Wann ist ein Makromodell selbstständig beschreibbar, wann fehlt Gedächtnis? | analytisch | `verify_closure_core.py`, `verify_generator_lumpability_core.py`, u.a. (4 Skripte) | Keine allgemeine datenbasierte Reduktionspipeline (Priorität 3) |
| `viability/` | Wann verletzen Last/Reserve/Kopplung eine Sicherheitsgrenze? | analytisch + unabhängig hand-nachgerechnete Regression | `verify_viability_core.py`, `verify_control_barrier_core.py`, `verify_multidim_tipping_maps.py`, u.a. (5 Skripte) | Kontrollbarriere bisher skalar (Priorität 5); Puffer-Minimum-Lokalisierung hatte einen behobenen Rasterfehler (Paket 6) |
| `membership/` | Wie klassifizieren Systeme in überlappende Kategorien? | analytisch | `verify_membership_core.py`, `verify_formal_concept_analysis.py` | Kleine Referenzbeispiele, kein Realdatenbezug |
| `identifiability/` | Welche Parameter legen die Daten tatsächlich fest? | analytisch + auf Realdaten-Fits angewandt | `verify_identifiability_core.py`, `verify_profile_likelihood_core.py`, u.a. (3 Skripte) | `established_unbounded` ist ab Paket 9 NIE allein aus Rasterdaten ableitbar — `flat_in_scanned_range` ist die ehrliche, rasterbezogene Aussage |
| `validation/` | Schlagen mechanistische Modelle einfache Baselines out-of-sample, Punkt UND Intervall? | echte Daten: OWID/JHU-COVID, NOAA, USGS; Cygnus X-1 explizit als unverifiziert markiert | `verify_rolling_origin.py`, `verify_mechanistic_probabilistic_evaluation.py`, `verify_adaptive_interval_calibration.py`, `verify_covid_latent_renewal_observation.py`, u.a. (16 Skripte) | Ursprüngliche LOO-Konstruktion: 52,5% (Energiebilanz, n=40) / 26,3% (COVID, n=19) Abdeckung bei nominell 80%. Eine zweite, symmetrische Betrags-Quantil-Konstruktion (Priorität 1) erreicht 70-85% bei Energiebilanz, aber 0% bei COVID-Persistenz. Priorität 2 (`docs/covid_latent_renewal_observation.md`) zeigt: dieselbe Renewal-Dynamik + nur eine Wochentag-Meldequote + Negativ-Binomial-Überdispersion hebt COVID-Abdeckung von 2,4% auf 73,8% (42 Versuche) — ein Großteil der COVID-Unterdeckung war ein Beobachtungs-, kein Dynamikproblem. Echter Meldeverzug (Report-Datum×Episoden-Datum-Matrix) bleibt außerhalb des Geltungsbereichs |
| `contextuality/` | Ist ein Satz lokaler Wahrscheinlichkeitsmodelle global darstellbar? | analytisch, extern geprüft (F08) | `verify_contextuality_core.py`, `verify_sheaf_contextuality.py`, u.a. (4 Skripte) | Kleine Referenzbeispiele, optionales Modul |
| `information_decomposition/` | Wie zerfällt gemeinsame Information in redundant/einzigartig/synergistisch? | analytisch, extern geprüft (F09) | `verify_information_decomposition_core.py`, `verify_pid_rb.py`, u.a. (3 Skripte) | Optionales Modul; Zerlegungswahl beeinflusst Zahlenwerte (bekanntes PID-Literaturproblem) |
| `thermo/` | Welche Netzwerke erfüllen thermodynamische Konsistenz? | analytisch | `verify_thermo_core.py`, `verify_schnakenberg_core.py`, `verify_crooks_core.py` | Kleine Referenznetzwerke, keine echten Messdaten |
| `chemical_organization/` | Welche Teilnetzwerke sind selbsterhaltend und produktionsabgeschlossen? | analytisch | `verify_chemical_organization_core.py` | Ein einzelnes kleines Referenzbeispiel |
| `percolation/` | Ab welcher Verzweigungswahrscheinlichkeit perkoliert eine Baumstruktur? | analytisch, geschlossene Form | `verify_percolation_core.py` | Idealisierter Baum, kein reales endliches Netzwerk |
| `pattern_formation/` | Bei welchen Parametern entsteht eine Turing-Instabilität? | analytisch | `verify_pattern_formation_core.py` | Nur lineare Stabilitätsanalyse, keine nichtlineare Simulation |
| `free_boundary/` | Wie entwickelt sich eine bewegte Phasengrenze? | analytisch, geschlossene Form | `verify_free_boundary_core.py` | Eine idealisierte Geometrie |
| `metarules/` | Welche repo-übergreifenden Konventionen muss jedes Modul einhalten? | statische Regelprüfung | `verify_metarules_core.py` | Prozessdisziplin, keine eigenständige fachliche Aussage |
| `legacy/` | Reproduzieren die ursprünglichen Revision-2/3-Beispiele noch? | analytisch (historisch) | `verify_extensions.py`, `verify_formalism.py`, `verify_transformations.py` | Eingefrorener historischer Geltungsbereich |

## Zusammenfassung nach Astras Fähigkeitstabelle

Astras eigene Bereichs-Zusammenfassung (2026-09-24, sieben breitere
Bereiche statt 18 Einzelmodule) bleibt die richtige Einstiegsebene für
Leser, die keine Modul-für-Modul-Details brauchen — siehe
`Astra4.txt` in `prompts/Answers/nicht_stationäre_Treiber/` und die obige
README-Zusammenfassung. Diese Datei liefert die dazugehörige Detailebene.
