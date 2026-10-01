# SCF — Kandidatenpiloten Polyeder, Sakurai, Saturn — Roadmap (2026-10-01)

Antwort auf [`SCF_POLYEDER_SAKURAI_SATURN_ANSCHLUSSBEWERTUNG.md`](prompts/Answers/nicht_stationäre_Treiber/SCF_POLYEDER_SAKURAI_SATURN_ANSCHLUSSBEWERTUNG.md).
Johanns Auftrag (2026-10-01): die Followups „ruhig direkt mit einbauen“.
Umgesetzt wird der **begrenzte** Auftrag, den die Bewertung selbst
vorschlägt (§7): TP0–TP1 als kleiner epistemischer Pilot, SK0–SK3 als
synthetischer Dynamik-vs.-Beobachtung-Pilot, Saturn zunächst nur SA0.
Keine Promotion des Turing-Review-Pakets zum Kern. Aus thematischer Nähe
folgt keine gemeinsame physikalische Ursache der drei Phänomene.

**Kontrollen:** Das Begleitskript der Bewertung (12 Kontrollgruppen) lag
nicht vor; alle verwendeten Kontrollen sind hier selbst hergeleitet und in
den Prüfskripten exakt geprüft.

## Pakete

| Paket | Inhalt | Status |
|---|---|---|
| TP0 | Quellen- und Statusnotiz; abstrakte Gruppe vs. räumliche Transformation | ✅ erledigt |
| TP1 | Endliche Beobachtungsabbildungen C8 / C4⊔C4, Anschluss an Beobachtungsfasern | ✅ erledigt |
| TP2 | exakter Inzidenz-/Topologieprüfer | ⬜ Option (nicht beauftragt) |
| TP3 | Einbettungsprüfer, auditierte Paper-Reproduktion | ⬜ Option (braucht vollständige Koordinaten) |
| SK0 | Quellenmatrix (Epochen, gemessen vs. angenommen) | ✅ erledigt |
| SK1 | Freisetzung, Zwischenspeicher, Erhaltung, Grenzfall α=β | ✅ erledigt |
| SK2 | Ein-/Mehrband-Messoperator | ✅ erledigt |
| SK3 | Windskalierung; Dynamik vs. Beobachtung | ✅ erledigt |
| SK4 | echter Spektral-/Zeitreihenpilot | ⬜ Option |
| SA0 | Quellen- und Größenregister Saturn | ✅ erledigt (nur Dokumentation) |
| SA1–SA4 | Fourier-Messoperator, Betaebene, Mechanismenvergleich, Datenpilot | ⬜ Option |

## TP0 — Quellen- und Statusnotiz

| Quelle | Status (2026-10-01) |
|---|---|
| Mizhaev, arXiv:2609.17700, *Integer Realization of an Equivelar Octahedron of Genus 3* | arXiv-Seite erreichbar, Titel bestätigt; Koordinaten **nicht** auditiert |
| Röst & Vígh, arXiv:2609.32998v1, *A second eight-faced polyhedron …* | HTML-Fassung erreichbar; Kombinatorik nicht nachgeprüft |

Präzisierungen der Bewertung, hier übernommen: Mizhaevs Symmetrie wird
durch $T(x,y,z)=(y,-x,-z)$ erzeugt — eine **Drehspiegelung**
($\det T=-1$, $T^4=I$), abstrakt zyklisch der Ordnung vier, **keine**
reine Vierteldrehung. Ganzzahlige Koordinaten **ermöglichen** exakte
Prüfungen; deren Durchführung (TP3) steht aus — keine Behauptung einer
Koordinatenzertifizierung.

## TP1 — Beobachtungsfasern (`validation/polyhedral_observation_pilot.py`)

Prüfung `verify_polyhedral_observation_pilot.py` (math) **4/4**:
TP-C01 ($V-E+F=-4$; $g=3$ **nur** unter deklarierten
Mannigfaltigkeitsvoraussetzungen — ohne Kreis-Knotenlinks keine
Genusaussage), TP-C02 (C8 und C4⊔C4 teilen die grobe Faser
(V, E, Gradfolge) und werden durch „Anzahl der Komponenten“ getrennt; reine
Graphaussage, kein Polyedernachweis), TP-C03 ($T^4=I$, $\det T=-1$;
Vierteldrehung hätte $\det=+1$), TP-C04 (exakte Koplanarität; eine
Abweichung $10^{-12}$ wird nicht auf die Ebene gerundet; Floats im exakten
Modus abgelehnt).

## SK0 — Quellenmatrix Sakurai

| Größe | Status laut Quelle (Marcolino et al., MNRAS, DOI 10.1093/mnras/stag1533) |
|---|---|
| Beobachtungsepoche | VLT/FORS2-Spektren **2023** — die Publikation von 2026 ist keine Messung des Zustands im Oktober 2026 |
| Temperatur | bevorzugt ≈ 30,5 kK, konservativ 27–36 kK (modellabhängig, NLTE) |
| Entfernung, Extinktion, Leuchtkraft | stark entartet; Leuchtkraft und Klumpungsfaktor im bevorzugten Modell **angenommen** |
| Zentralstern | nicht direkt abgebildet |
| Weitere Abkühlungsausflüge | modellabhängig zugelassen |

Nicht übernommen: „Helium aufgebraucht, weiterer Puls ausgeschlossen“,
„Energiespeicher verbraucht“, „Staub lichtet sich seit 2021“ (ohne
geprüfte Messreihe). Quellenstatus: Verlagsseite blockt automatischen
Abruf (403); bibliografisch über Crossref bestätigt (Titel, MNRAS).
**Offene Kleinigkeit:** Crossref nennt den 12.09.2026, die Bewertung den
16.09.2026 — vermutlich Online- vs. Ausgabedatum; nicht geklärt.

## SK1–SK3 — Speicherpuls und Messoperator (`validation/stellar_pulse_observation.py`)

Prüfung `verify_stellar_pulse_observation.py` (math) **4/4**:
SK-C01 (lineares Freisetzungsmodell als **Nullkontrolle**: Erhaltung,
Positivität, stetiger Grenzfall α=β, Maximum bei $t=\ln2$ mit
$(f,E,Q)=(1/4,1/2,1/4)$ für α=2, β=1 — ein Puls entsteht bereits ohne
Nichtlinearität), SK-C02 ($L e^{-\tau}$: $(1,0)\sim(e,1)$; ein Band trennt
$L$ und $\tau$ nicht), SK-C04 (zwei bekannte, verschiedene
Extinktionskoeffizienten: exakter Rang 2 über J6; gleiche Koeffizienten:
Rang 1; unbekannte Spektralform je Band: wieder nicht identifizierbar),
SK-C03 ($R_*\to4R_*$, $\dot M\to8\dot M$ hält $R_*(v_\infty/\dot M)^{2/3}$
exakt — über die dritte Potenz — und skaliert $L$ um 16; die Gleichheit
realer Spektren wird **nicht** behauptet).

Das Modell erklärt keine thermonukleare Zündung, Konvektion oder
Sternstruktur und ist kein Sakurai-Modell; eine Verbindung zu
kosmologischen Hypothesen bräuchte eigene unterscheidende Vorhersagen.

## SA0 — Quellen- und Größenregister Saturn

| Größe | Bedeutung | Nicht gleichsetzen mit |
|---|---|---|
| Gasgeschwindigkeit | Windgeschwindigkeit im Jet | Musterdrift |
| Musterdrift $\Omega_p$ | Bewegung des sechseckigen Musters | Rotation des Bezugssystems |
| Bezugssystem | Rotationsperiode (System III o. ä.) | Gas- oder Muster-Geschwindigkeit |
| Höhe | Troposphäre vs. Stratosphäre | „zweites Hexagon“ als unabhängiges System |

Quellen: Yadav & Bloxham (2020), PNAS, DOI 10.1073/pnas.2000317117 —
Verlagsseite blockt automatischen Abruf (403), bibliografisch per
Crossref bestätigt („Deep rotating convection generates the polar hexagon
on Saturn“); Fletcher et al. (2018), Nature Communications, DOI
10.1038/s41467-018-06017-3 — erreichbar. Südpol-Zehneck,
JWST-Ionosphäre, Jupitervergleich und Medienzahlen sind **nicht** bis zu
Originaldaten auditiert und werden nicht als Randbedingungen verwendet.
Ein Pilot (SA1/SA2: Fourier-Messoperator, lineare Betaebene,
Randbedingungs-Ausschluss) ist eine eigene Ausbauentscheidung.

## Regression

Vor dem Commit (Arbeitsstand TP0–TP1 + SK0–SK3 + SA0): `python scripts/run_verification_suite.py --category all` → **131/131 bestanden** (129 vorher + 2 neue Prüfskripte, 13 min); `--category links` grün. Gezielte Mutanten (`scripts/run_targeted_mutations.py`, Bericht `verification/targeted_mutations_report.json`): **6/6** Kandidaten-Mutanten durch Inhaltsassertion getötet (`tp_genus_without_premises`, `tp_components_ignored`, `tp_coplanarity_rounded`, `sk_alpha_equals_beta_limit_wrong`, `sk_peak_time_wrong`, `sk_shape_terms_ignored`); Gesamtbericht 89 Mutanten, 88 getötet, 1 als äquivalent vorregistriert.

**Testlücke gefunden und geschlossen:** Der Grenzfall α=β war zunächst nur bei α=1 geprüft — dort fällt die falsche Formel $t\,e^{-\alpha t}$ mit der richtigen $\alpha t\,e^{-\alpha t}$ zusammen, der Mutant überlebte. Seit der Prüfung zusätzlich bei α=β=2 wird er getötet.
