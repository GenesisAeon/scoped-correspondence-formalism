Auftrag: Teil 2, neuer eigenständiger Baustein "chemical_organization"
— KEIN Erweiterungs-Milestone, sondern ein komplett neues,
eigenständiges Modul. Aus Runde 3, Spur C (CREP/UTAC/AFET-
Inspirationsliteratur ehrlich neu geprüft). Von ALLEN VIER
unabhängigen Rechercheagenten übereinstimmend als Ergebnis geliefert:
"Autopoiesis selbst hat keine anerkannte, vollständige mathematische
Formalisierung — Chemical Organization Theory (COT) operationalisiert
aber einen echten Teilaspekt (Selbst-Erhaltung/Abschluss unter
Reaktionen), seriös und handprüfbar."

## Vorgeschichte (Pflichtkontext für den Docstring)

Dieses Projekt war ursprünglich u.a. von Maturana & Varelas
**Autopoiesis** inspiriert. Autopoiesis selbst — ein Netzwerk von
Prozessen, das seine eigenen Komponenten UND seine eigene Grenze
erzeugt — hat in der Literatur KEINE allgemein anerkannte
mathematische Formalisierung mit handprüfbarem Beispiel (bestätigt von
allen vier Rechercheagenten unabhängig). **Dieser Baustein heißt daher
NICHT `autopoiesis`, sondern `chemical_organization`, und behauptet an
keiner Stelle, Autopoiesis vollständig zu formalisieren** — der
Docstring MUSS diese Einschränkung wörtlich enthalten.

## KRITISCHE Namenskollision — Pflichtauflage für die gesamte API

Chemical Organization Theory nennt ihr Kernkonzept im Original
"closed"/"closure". Das kollidiert mit dem bereits bestehenden
`closure`-Baustein dieses Repos (`PC=CQ`, Markov-Makro-Geschlossenheit
— ein KOMPLETT ANDERES mathematisches Objekt, das zufällig dasselbe
englische Wort trägt). **Deshalb gilt für diesen gesamten Auftrag eine
harte Namensregel:**

- Das Wort "closure"/"closed" darf NIRGENDS als Funktions-, Klassen-
  oder Attributname auftauchen.
- Stattdessen: `is_reaction_closed(...)` statt `is_closed`,
  `is_self_maintaining(...)`, `is_organization(...)`.
- Zusätzlich kollidiert der COT-"Organisationsverband" begrifflich mit
  dem bereits gemergten M27 (`membership.formal_concept_analysis`,
  Galois-Verband auf der Mitgliedschaftsmatrix) — beide heißen
  zufällig "Verband"/"Lattice", sind aber unterschiedliche
  mathematische Objekte (Ordnung über Organisationen vs.
  Galois-Verbindung auf einer binären Matrix). Der Docstring MUSS
  BEIDE Kollisionen (mit `closure` UND mit M27) explizit als
  "gleiches Wort, verschiedenes Objekt, keine gemeinsame Basisklasse"
  benennen.

## Quelle

P. Dittrich & P. Speroni di Fenizio, "Chemical Organisation Theory",
Bulletin of Mathematical Biology 69(4), 1199–1231 (2007), DOI
10.1007/s11538-006-9130-8. Von allen vier Agenten per Crossref-API
verifiziert (Titel, beide Autoren, Zeitschrift, Band, Seiten, Jahr
exakt). Vorläufer: W. Fontana & L. W. Buss, "'The arrival of the
fittest': Toward a theory of biological organization", Bulletin of
Mathematical Biology 56(1), 1–64 (1994), DOI 10.1007/BF02458289.

## Kernformel

Für ein Reaktionsnetzwerk `⟨M,R⟩` (Spezies `M`, Reaktionen `R`) und
eine Teilmenge `A ⊆ M`:

- **reaction-closed**: jede Reaktion, deren Edukte in `A` liegen,
  erzeugt nur Produkte in `A`.
- **self-maintaining**: es existiert ein Flussvektor `v>0` über die in
  `A` anwendbaren Reaktionen mit `(S·v)ᵢ≥0` für alle `i∈A` (`S` =
  Stöchiometriematrix).
- **Organisation**: `A` ist reaction-closed UND self-maintaining.

## Umfang dieses Auftrags

Neues Paket `src/scoped_correspondence/chemical_organization/` mit
`__init__.py` und `core.py`.

### 1. `chemical_organization.is_reaction_closed(A, reactions)`

Prüft die Abschlusseigenschaft für eine gegebene Teilmenge `A` und
eine Liste von Reaktionen (Edukt-/Produktmengen).

### 2. `chemical_organization.is_self_maintaining(A, reactions, stoich_matrix)`

Prüft per LP-Machbarkeit (SciPy `linprog`, bereits Repo-Abhängigkeit),
ob ein strikt positiver Flussvektor `v` mit `(S·v)≥0` auf `A`
existiert.

### 3. `chemical_organization.is_organization(A, reactions, stoich_matrix)`

Kombiniert beide Prüfungen.

### 4. Durchgerechnetes Beispiel (Pflicht)

Spezies `{a,b}`, Reaktionen: `r1: a→b`, `r2: b→a`, `r3: b→∅`,
`r4: ∅→a`.

- OHNE `r4`: `A={a,b}` ist reaction-closed, aber NICHT
  self-maintaining (Nachweis per Hand: `(Sv)_a=-v1+v2≥0` und
  `(Sv)_b=v1-v2-v3≥0` addiert ergibt `-v3≥0`, Widerspruch zu `v3>0`) —
  einzige Organisation ist `∅`.
- MIT `r4`: `A={a,b}` ist Organisation mit Zeugen `v=(2,1,1,1)`:
  `(Sv)_a=-2+1+1=0≥0`, `(Sv)_b=2-1-1=0≥0`. Beide Fälle im Skriptlauf
  exakt nachrechnen (LP-Lösung UND die Handrechnung als Kommentar im
  JSON-Report).

### 5. Explizit NICHT Teil dieses Auftrags

- KEINE Behauptung, dies formalisiere Autopoiesis vollständig — nur
  Selbst-Erhaltung/Abschluss (siehe Vorgeschichte oben).
- KEINE Verwendung des Wortes "closure"/"closed" in Funktions-/Klassen-
  /Attributnamen (siehe Namenskollisions-Regel oben) — Abnahmekriterium.
- KEINE Änderung an `closure/core.py` oder `membership/`.
- KEIN vollständiger Organisationsverbands-Enumerator für große
  Netzwerke — Brute-Force über kleine, im Beispiel gegebene Netzwerke
  reicht (analog zu M27s Begründung für Brute-Force-Konzeptenumeration).

## Verifikation

`verify_chemical_organization_core.py`: (1) Beispiel oben exakt
reproduziert (beide Fälle, mit/ohne `r4`), (2) statische
Quellcode-Prüfung, dass KEIN Funktions-/Klassenname das Wort
"closure"/"closed" enthält (Regex-Scan über die neue Datei selbst als
Teil des Verify-Skripts), (3) Negativtest: `{b}` allein ist NICHT
self-maintaining (kein Nachschub ohne `a`).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/chemical_organization_core.md`, MIT
   Vorgeschichte UND BEIDEN Namenskollisions-Warnungen (closure UND
   M27-Verband) wörtlich.
3. `verify_chemical_organization_core.py` mit reproduzierbarem
   JSON-Report unter `verification/`, INKLUSIVE des Regex-Scans gegen
   das verbotene Wort.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Dittrich & Speroni di Fenizio (2007) und
   Fontana & Buss (1994).
6. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente, KEINE Änderung an irgendeinem bestehenden
   Baustein-Verzeichnis.
7. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m41-chemical-organization-theory`. Kann PARALLEL
zu den anderen Runde-3-Milestones bearbeitet werden — komplett
eigenständiges neues Verzeichnis. Bitte NICHT
`src/scoped_correspondence/__init__.py` oder irgendein bestehendes
Baustein-Verzeichnis anfassen. Claude reviewed und merged erst nach
Johanns OK.
