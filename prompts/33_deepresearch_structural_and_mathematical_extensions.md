Wissenschaftlicher DeepResearch-Auftrag (Runde 2): weitere natürliche
Erweiterungen UND strukturell passende, aber eigenständige Themenfelder
für den Scoped-Correspondence-Formalismus

Zielformat: DeepResearch-Modus (ChatGPT/Astra, Gemini oder vergleichbar).
Bitte zusammen mit der aktuellen `README.md` des Repos übergeben — dieser
Prompt ersetzt sie nicht, sondern ergänzt sie um den konkreten
Rechercheauftrag. Kein Code-Auftrag, keine Domänenentscheidung — reine
Literaturrecherche.

## Ausgangslage

Wir betreiben ein kleines, formal geprüftes Software-Repository
(`scoped-correspondence-formalism`), das aus mehreren unabhängig
voneinander stehenden, mathematisch geprüften Modulen besteht — KEINE
vereinheitlichte Theorie, sondern einzelne, für sich bewiesene/verifizierte
Bausteine, verbunden über einen expliziten Übersetzungsvertrag
(`correspondence`: Konjugation `T∘Φ≈Φ∘T`, Transformationsregeln T1-T4).

**Stand 19. September 2026:** eine erste Recherche-Runde (zwei
unabhängige DeepResearch-Antworten) hat bereits 17 Erweiterungsvorschläge
geliefert — ALLE sind inzwischen unabhängig geprüft (Zitate gegen
DOI/arXiv, Zahlen von Hand nachgerechnet) und gemergt. Vollständige
Bausteinliste mit allen bereits umgesetzten Erweiterungen: siehe
`EXTENSIONS_ROADMAP.md` im Repo (bitte VOR der Recherche lesen, um keine
bereits umgesetzten Vorschläge zu wiederholen).

Bestehende Bausteine (Kurzfassung — Details in README.md/EXTENSIONS_ROADMAP.md):
`correspondence` (Übersetzungsvertrag + Approximation Certificates,
Contraction-Verweis), `observation` (Kanalkapazität, Directed
Information), `dynamics` (kubische Normalform, Contraction Analysis),
`coupling` (GENERIC-Struktur, Dirac-Komposition, Dissipativity),
`closure` (Makro-Geschlossenheit, CTMC-Lumpability, Fehlerschranken),
`viability` (sichere Eingriffsübertragung, Control Barrier Functions),
`membership` (Zugehörigkeitsstruktur), `metarules` (Regelzustand-
Eigendynamik), `identifiability` (SVD, Profile Likelihood, Fisher-
Sloppiness), `validation` (Datenpilot, Split Conformal Prediction),
`contextuality` (Sheaf-CF, CSW-Grapheninvarianten, Čech-Kohomologie),
`information_decomposition` (Williams-Beer, Blackwell-RB, BROJA),
`thermo` (GENERIC-Wärmebeispiel, Schnakenberg-Netzwerkthermodynamik).

## Zwei getrennte Recherchespuren

### Spur A: weitere direkt anschließbare Erweiterungen (wie Runde 1)

Finde WEITERE, bisher nicht in Betracht gezogene mathematische Theorien,
Sätze oder Formalismen, die sich NATÜRLICH an einen oder mehrere der
oben genannten Bausteine anschließen ließen — genau wie in Runde 1 (siehe
`EXTENSIONS_ROADMAP.md` für das exakte Format und die harten
Ausschlusskriterien unten). Da 17 Vorschläge bereits umgesetzt sind, wird
diese Spur schwieriger — das ist normal und ehrlich zu berichten, falls
zu einem Baustein nichts Neues gefunden wird.

### Spur B: strukturell passende, aber eigenständige Themenfelder (NEU)

Johann hat folgende Ausgangsideen genannt, die bisher nicht direkt
abgedeckt sind: **Randbedingungen/Grenzflächen (boundaries)**,
**Aggregatzustandswechsel/Phasenübergänge**, **Fluiddynamik/
Kontinuumsmechanik**. Diese Themen teilen STRUKTURELLE Muster mit
unseren Bausteinen, ohne dass bereits ein konkreter Satz identifiziert
wurde. Beispiele für mögliche Anknüpfungspunkte (zur Orientierung, nicht
als vorgegebenes Ergebnis):

- **Randbedingungen:** `viability`s sichere Mengen (`h(x)≥0`, CBF) und
  `closure`s Makro-Grenzen berühren das Thema bereits am Rande. Freie-
  Rand-Probleme (z.B. Stefan-Problem — eine sich bewegende Phasengrenze,
  verbindet "Randbedingung" UND "Aggregatwechsel" wörtlich) könnten ein
  eigenständiger, gut zitierbarer Anschluss sein.
- **Aggregatwechsel/Phasenübergänge:** `dynamics`s Cusp-Katastrophe ist
  bereits ein Spielzeug-Phasenübergangsmodell. Landau-Theorie,
  Universalitätsklassen, kritische Exponenten (Renormierungsgruppe) sind
  ein größeres, in früheren Revisionen bewusst zurückgestelltes Feld
  ("RG-Universalität ist keine Voraussetzung, eigene Herleitung nötig")
  — falls ein konkreter, eng begrenzter Satz gefunden wird, darf er
  erneut vorgeschlagen werden, jetzt mit echtem Zitat und Beispiel.
- **Fluiddynamik/Kontinuumsmechanik:** `coupling`/`thermo`s GENERIC-
  Formalismus hat einen dokumentierten Bezug zu Navier-Stokes und
  anderen Kontinuumsgleichungen (Öttinger, Grmela — "GENERIC" wurde
  ursprünglich genau dafür entwickelt). Auch: hydrodynamische Grenzwerte
  kinetischer Gleichungen (Chapman-Enskog-Entwicklung) sind wörtlich ein
  "Closure"-Problem im Sinne von `closure`s bereits vorhandener PC=CQ-
  Bedingung.
- **Und Ähnliches:** Perkolationstheorie, Domänenwand-/Grenzflächen-
  dynamik, Nichtgleichgewichts-Phasenübergänge, aktive Materie/
  Selbstorganisation — nur falls ein WIRKLICH konkreter, zitierbarer
  Satz mit Beispiel gefunden wird, keine bloße thematische Erwähnung.

**Für jeden Spur-B-Vorschlag MUSS explizit angegeben werden:**
1. Ist dies (a) eine echte, beweisbare Erweiterung EINES bestehenden
   Bausteins (mit Formel-zu-Formel-Anschluss wie in Spur A), oder (b) ein
   Kandidat für einen KOMPLETT NEUEN, eigenständigen Baustein (13. oder
   weiterer), der NICHT von einem bestehenden Baustein "abstammt"?
2. Diese Entscheidung darf nicht offengelassen werden — jeder Vorschlag
   gehört klar in (a) oder (b).

## Harte Ausschlusskriterien (für BEIDE Spuren, unverändert aus Runde 1)

Dieses Projekt hat mehrfach falsche Cross-Layer-Identitäten korrigieren
müssen (u.a. β≡Stabilität, V≡Panarchy≡Onsager-L, geteiltes σ=2,2 als
"Universalität", A_ij≡L_ij). Deshalb gilt zwingend:

1. **Keine Vorschläge, die zwei oder mehr Bausteine (oder ein Baustein
   und ein neues Themenfeld aus Spur B) gleichsetzen oder unter einem
   gemeinsamen Parameter/einer gemeinsamen Konstante vereinen.** Eine
   STRUKTURELLE Ähnlichkeit (z.B. "Fluiddynamik hat auch eine
   GENERIC-Struktur") ist ein Grund, das Thema als EIGENSTÄNDIGEN,
   separat verifizierten Kandidaten zu bauen — NIEMALS ein Beweis, dass
   zwei Bausteine "eigentlich dasselbe" sind. Diese Unterscheidung ist
   der ganze Sinn von Spur B — bitte nicht verwischen.
2. Keine "Universalitäts"- oder "Meta-Theorie"-Behauptungen.
3. Jede Quelle muss ein echtes, prüfbares arXiv/DOI-Zitat haben — keine
   Sekundärquellen, keine Blogposts, keine KI-generierten
   Zusammenfassungen ohne Primärquelle.
4. Bevorzugt: Theorien mit einem kleinen, von Hand durchrechenbaren
   Beispiel (analog zu unseren `verify_*.py`-Skripten) — keine reinen
   Existenzsätze ohne konstruktives Beispiel.
5. Wenn zu einem Vorschlag aus Spur B kein konkreter, zitierbarer Satz
   mit Beispiel gefunden wird, sondern nur eine vage thematische
   Verbindung — das EHRLICH so berichten, nicht erzwingen.

## Gewünschtes Ausgabeformat pro Vorschlag

1. Name der Theorie/des Satzes + Primärquelle (Autor, Jahr, arXiv/DOI).
2. Kernformel in Text/LaTeX (keine Bildformeln).
3. Spur A: An welchen bestehenden Baustein schließt es sich an, und
   warum — konkrete Formel-zu-Formel-Anknüpfung.
   Spur B: (a) oder (b) wie oben, plus Begründung.
4. Ein durchgerechnetes Mini-Beispiel mit konkreten Zahlen (falls in der
   Quelle vorhanden) oder ein klarer Hinweis, dass eines konstruiert
   werden müsste.
5. Geschätzter Umfang (klein/mittel/groß) für eine spätere Umsetzung
   nach unserem "Astra-Standard" (Textformeln, `verify_*.py` mit
   reproduzierbarem JSON-Report, durchgerechnetes Beispiel aus dem
   Skriptlauf, explizites Mapping, geprüfte Zitate).

Liefere für Spur A mindestens 3, für Spur B mindestens 3-5 Vorschläge,
sortiert nach Spur und innerhalb der Spur nach Baustein/Themenfeld
(nicht nach vermuteter Priorität — die Bewertung, was davon umgesetzt
wird, trifft Johann separat). Ehrlich vermerken, wo nichts Zitierfähiges
gefunden wurde, statt einen schwachen Vorschlag zu erzwingen.
