Auftrag: Teil 2, Milestone 12 ("Dirac Structure Composition") —
natürliche Erweiterung von `coupling`, aus derselben unabhängig
geprüften DeepResearch-Recherche wie Milestone 11
(`prompts/Answers/Mathematische Erweiterungen Scoped Correspondence.docx`
— Cervera, van der Schaft & Baños 2007, DOI
10.1016/j.automatica.2006.08.014, von Claude gegen die Quelle geprüft).

## Kontext

`coupling.check_generic_structure` (M2, gemergt) ist ein reiner
Strukturtest auf EINER Kopplungsmatrix `J` (schiefsymmetrisch) und `M`
(symmetrisch PSD). Cervera, van der Schaft & Baños (2007) zeigen, dass
die Komposition von Dirac-Strukturen zweier bereits verifizierter
Teilsysteme über eine leistungserhaltende Interkonnektion (gemeinsamer
Port, Effort-/Flow-Kopplung) wieder eine gültige, insbesondere
schiefsymmetrische Gesamtstruktur ergibt — ohne die Systemfreiheits-
grade neu von Grund auf zu prüfen.

## Umfang dieses Auftrags

### 1. `coupling.dirac_composition.compose_skew_symmetric(J1, J2, interconnection)`

Für zwei bereits einzeln geprüfte antisymmetrische Kopplungsmatrizen
`J1`, `J2` (je über `coupling.check_generic_structure` bestätigt — nur
Aufruf, keine Änderung an `coupling/core.py`) und eine
leistungserhaltende Interkonnektionsbedingung (analog zur "neutralen
Interkonnektion" aus dem bereits geprüften Dissipativitäts-Beispiel in
`ChatGPTAstra3.md`: `u1=-y2, u2=y1`, sodass sich die Leistungsterme
`y1·u1+y2·u2=0` aufheben): baue die zusammengesetzte Blockmatrix
`J_total` und zeige, dass sie wieder schiefsymmetrisch ist —
`J_total.T == -J_total` über `check_generic_structure`s bereits
vorhandene Antisymmetrie-Prüfung (aufrufen, nicht neu implementieren).

### 2. Durchgerechnetes Beispiel

Zwei konservative 2D-Subsysteme mit je einer antisymmetrischen `J_i`
(z.B. `J1=[[0,1],[-1,0]]`, `J2=[[0,2],[-2,0]]` — frei wählbar, solange
beide einzeln `check_generic_structure`-antisymmetrisch sind), über
eine Schnittstellenmatrix im Sinne einer leistungserhaltenden
Interkonnektion gekoppelt. Zeige:
- Die zusammengesetzte Gesamtmatrix bleibt exakt schiefsymmetrisch.
- Die Gesamtleistung an der Schnittstelle ist exakt Null für
  beliebige Zustände (analog zum bereits verifizierten
  Dissipativitäts-Rechenbeispiel `ẋ_i=-x_i+u_i`, `V̇_total=-5` bei
  `x1=1,x2=2` — hier aber für die reversible/Poisson-Struktur, nicht
  die dissipative Seite).

### 3. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `coupling/core.py` — nur Aufruf von
  `check_generic_structure`.
- Keine allgemeine Bond-Graph-/Port-Hamilton-Bibliothek — nur der
  konkrete, hier durchgerechnete Kompositionsfall für zwei Subsysteme.
- Keine Aussage über die `M`-Matrix (dissipativer Teil) — dieser
  Auftrag behandelt ausschließlich die `J`-Komposition (Poisson-
  Struktur).
- Keine Änderung an `closure/`, `validation/` oder einem anderen Modul.

## Verifikation

`verify_dirac_composition_core.py`: keine bestehende Legacy-Prüfung —
frisches Beispiel. Prüfungen: (1) `J1`, `J2` einzeln antisymmetrisch
(via `check_generic_structure`), (2) zusammengesetzte `J_total`
antisymmetrisch, (3) Leistungserhaltung an der Schnittstelle exakt
Null für mindestens zwei verschiedene Zustandsvektoren.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_dirac_composition_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Cervera/van der Schaft/Baños 2007 (DOI oben)
   und `coupling/core.py`s `check_generic_structure`.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente (explizit inklusive `coupling_layer_afet.md`).
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m12-dirac-composition` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 11 (`closure`) und Milestone 13 (`validation`)
bearbeitet werden. Claude reviewed jeden Branch einzeln und merged erst
nach Johanns OK.
