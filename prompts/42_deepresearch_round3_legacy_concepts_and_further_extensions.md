Wissenschaftlicher DeepResearch-Auftrag (Runde 3): Wiederaufnahme der
ursprünglichen CREP/UTAC/AFET-Inspirationsliteratur — diesmal ohne
künstliche Übersetzung — plus weitere natürliche Erweiterungen und
eigenständige Themenfelder

Zielformat: DeepResearch-/Recherche-Modus (für zwei unabhängige
Grok-Agenten, via Aeon beauftragt). Bitte zusammen mit der aktuellen
`README.md`, `GLOSSARY.md` und `EXTENSIONS_ROADMAP.md` des Repos
übergeben — dieser Prompt ersetzt sie nicht, sondern ergänzt sie um den
konkreten Rechercheauftrag. Kein Code-Auftrag, keine Domänenentscheidung
— reine Literaturrecherche.

**Wichtig für beide Agenten:** arbeitet UNABHÄNGIG voneinander, ohne
Kenntnis des jeweils anderen Ergebnisses. Jedes Zitat MUSS gegen eine
echte, prüfbare Primärquelle (arXiv/DOI) verifiziert werden — keine
Sekundärquellen, keine Blogposts, keine unbelegten Zusammenfassungen.

## Ausgangslage

Wir betreiben ein kleines, formal geprüftes Software-Repository
(`scoped-correspondence-formalism`), das aus mehreren unabhängig
voneinander stehenden, mathematisch geprüften Bausteinen besteht — KEINE
vereinheitlichte Theorie, sondern einzelne, für sich bewiesene/verifizierte
Module, verbunden über einen expliziten Übersetzungsvertrag
(`correspondence`: Konjugation `T∘Φ≈Φ∘T`, Transformationsregeln T1-T4).

**Stand 19. September 2026:** das Projekt hat inzwischen 15 Bausteine
(`correspondence`, `observation`, `dynamics`, `coupling`, `closure`,
`viability`, `membership`, `metarules`, `identifiability`, `validation`,
`contextuality`, `information_decomposition`, `thermo`,
`pattern_formation`, `free_boundary`, `percolation`). Zwei
Recherche-Runden haben bereits 25 Erweiterungsvorschläge geliefert —
ALLE sind unabhängig geprüft (Zitate gegen DOI/arXiv, Zahlen von Hand
nachgerechnet) und gemergt. Vollständige Liste: siehe
`EXTENSIONS_ROADMAP.md` im Repo (bitte VOR der Recherche lesen, um
keine bereits umgesetzten Vorschläge zu wiederholen).

## Vorgeschichte, die für Spur C wichtig ist

Dieses Projekt hieß ursprünglich „CREP–UTAC–AFET" und war von
Konzepten aus der Ökologie und Systemtheorie inspiriert — insbesondere
Holling's **Panarchy**/adaptive-cycle-Theorie und Maturana & Varelas
**Autopoiesis**. Eine frühere Revision hat versucht, diese Konzepte
DIREKT mit den hier definierten Größen gleichzusetzen. Das war ein
Fehler und wurde vollständig zurückgenommen, u.a.:

- `β (beta_response) ≡ Stabilität` — falsch, zwei verschiedene Größen
  mit verschiedenen Einheiten (siehe `dynamics.recovery_rate_from_relaxation`s
  Docstring: "Independence of beta_response").
- `V ≡ Panarchy ≡ Onsager-L` — falsch, drei unabhängige Konzepte ohne
  gemeinsame Herleitung wurden unter einem Symbol vereinigt.
- geteiltes `σ≈2,2` als "Universalität" — falsch, eine zufällige
  Zahlenkoinzidenz wurde als Bestätigung fehlinterpretiert (siehe
  `README.md`s Status-Abschnitt, wo dieser Fehler bis heute explizit
  als Warnung steht).
- `A_ij ≡ L_ij` — falsch, dynamischer Einfluss und thermodynamischer
  Transportkoeffizient haben unterschiedliche Einheiten und
  Bedeutungen (`coupling/core.py` hält sie seither bewusst als
  getrennte Dataclasses ohne gemeinsame Basisklasse).

**Diese Vorgeschichte bedeutet NICHT, dass Panarchy, Autopoiesis oder
verwandte Konzepte für immer ausgeschlossen sind — nur, dass jeder neue
Versuch eine ECHTE, EINZELN GEPRÜFTE mathematische Verbindung
liefern muss statt einer Namens-Gleichsetzung.** Johann möchte
ausdrücklich prüfen lassen, ob es inzwischen (oder schon immer)
seriöse, formal ausgearbeitete Fassungen dieser Konzepte gibt, die
sich — OHNE künstliche Übersetzung — ehrlich an einen bestehenden
Baustein anschließen lassen oder einen eigenständigen neuen Baustein
rechtfertigen.

## Drei Recherchespuren

### Spur A: weitere direkt anschließbare Erweiterungen (wie Runde 1/2)

Finde WEITERE, bisher nicht in Betracht gezogene mathematische
Theorien, Sätze oder Formalismen, die sich NATÜRLICH an einen oder
mehrere der 15 Bausteine anschließen lassen. Nach 25 bereits
umgesetzten Vorschlägen ist diese Spur schwierig — ehrlich berichten,
falls nichts Neues gefunden wird.

### Spur B: weitere strukturell passende, aber eigenständige Themenfelder

Fortsetzung von Runde 2 (dort bereits umgesetzt: freie Randbedingungen
→ `free_boundary`, Musterbildung → `pattern_formation`, Perkolation →
`percolation`). Zwei Themen aus Runde 2s Auftrag (`prompts/33_...md`)
waren dort nur als Orientierung genannt und wurden NIE zu einem
eigenen Milestone — bitte diesmal konkret verfolgen:

- **GENERIC ↔ Navier-Stokes** (Öttinger & Grmela — GENERIC wurde
  ursprünglich genau für diesen Bezug entwickelt, u.a. Öttinger &
  Grmela, "Dynamics and thermodynamics of complex fluids II",
  Phys. Rev. E 56, 6633 (1997) — Zitat/DOI bitte selbst verifizieren,
  hier nur als Ausgangspunkt genannt). Passt das formelgenau an
  `coupling.check_generic_structure` bzw. `thermo`, mit einem
  durchrechenbaren Beispiel (z.B. ein einfaches viskoses 1D-Modell,
  bei dem die GENERIC-Dissipationsklammer auf den Navier-Stokes-
  Spannungstensor reduziert)?
- **Chapman-Enskog-Entwicklung** (Chapman & Cowling, "The
  Mathematical Theory of Non-Uniform Gases" — hydrodynamischer
  Grenzwert kinetischer Gleichungen, wörtlich ein "Closure"-Problem im
  Sinne von `closure`s bereits vorhandener `PC=CQ`-Bedingung). Gibt es
  eine konkrete, zitierfähige Formel (z.B. die Viskosität aus der
  Chapman-Enskog-Entwicklung erster Ordnung) mit durchrechenbarem
  Beispiel, die formelgenau an `closure` anschließt?

Weitere Kandidaten darüber hinaus willkommen, z.B. (zur Orientierung,
nicht als vorgegebenes Ergebnis): Nichtgleichgewichts-Phasenübergänge,
aktive Materie — nur falls ein WIRKLICH konkreter, zitierbarer Satz mit
Beispiel gefunden wird.

### Spur C (NEU, Schwerpunkt dieser Runde): CREP/UTAC/AFET-Inspirationsliteratur ehrlich neu prüfen

Untersuche, ob folgende Themenfelder — historisch die Inspiration
hinter CREP/UTAC/AFET, aber nie sauber angeschlossen — inzwischen eine
formal ausgearbeitete, zitierfähige Fassung mit durchrechenbarem
Beispiel besitzen:

- **Panarchy / Adaptive-Cycle-Theorie** (Holling 1973, 2001;
  Gunderson & Holling 2002): gibt es eine formale (nicht nur
  begriffliche) Fassung des Exploitation-Conservation-Release-
  Reorganization-Zyklus, z.B. über Faltungs-Bifurkation/Hysterese in
  einem dynamischen System? Falls ja: WELCHER bestehende Baustein
  (`dynamics`? `pattern_formation`?) passt formelgenau, oder
  rechtfertigt es einen eigenen Baustein?
- **Autopoiesis** (Maturana & Varela 1980 und Nachfolgearbeiten):
  Autopoiesis gilt in der Literatur als notorisch schwer zu
  formalisieren. Gibt es TROTZDEM eine anerkannte, mathematisch
  konkrete Operationalisierung (z.B. über chemische Organisationstheorie,
  Fontana & Buss 1994, oder ähnliches) mit einem durchrechenbaren
  Beispiel? Falls nicht: das ehrlich so berichten statt einen
  Begriffsvergleich als Ergebnis auszugeben.
- **Strukturelle Kopplung** (im Sinne Luhmanns, aber gesucht wird eine
  MATHEMATISCHE, nicht soziologische Fassung): Generalisierte
  Synchronisation gekoppelter dynamischer Systeme (z.B. Pecora &
  Carroll 1990, DOI 10.1103/PhysRevLett.64.821) ist ein Kandidat für
  eine seriöse, moderne Formalisierung dieses Konzepts — passt das
  formelgenau an `coupling`?
- **Resilienztheorie über das bereits Gebaute hinaus**: `viability`
  und `dynamics` decken bereits Beckenwahrscheinlichkeit,
  Erholungsrate und sichere Mengen ab. Early-Warning-Signale für
  kritische Übergänge (kritisches Verlangsamen: steigende Varianz/
  Autokorrelation nahe einer Bifurkation — Scheffer et al. 2009,
  Nature, DOI 10.1038/nature08227) sind ein konkreter, zitierfähiger,
  von Hand durchrechenbarer Kandidat, der NICHT bereits abgedeckt ist
  — passt das an `dynamics` oder `identifiability`?

**Für jeden Spur-C-Vorschlag MUSS explizit angegeben werden:**
1. Die GENAUE Formel/der genaue Satz aus einer echten Primärquelle
   (nicht nur der Begriff).
2. Ist dies (a) eine echte, beweisbare Erweiterung EINES bestehenden
   Bausteins (Formel-zu-Formel-Anschluss), oder (b) ein Kandidat für
   einen neuen, eigenständigen Baustein?
3. Falls zu einem der vier genannten Themen NICHTS Zitierfähiges mit
   Beispiel gefunden wird: das ehrlich berichten. Ein Scheitern dieser
   Spur ist ein valides, nützliches Ergebnis — besser als eine
   erzwungene Wiederholung des alten Fehlers.

## Harte Ausschlusskriterien (für ALLE drei Spuren, unverändert)

Dieses Projekt hat mehrfach falsche Cross-Layer-Identitäten korrigieren
müssen (siehe Vorgeschichte oben: β≡Stabilität, V≡Panarchy≡Onsager-L,
geteiltes σ=2,2, A_ij≡L_ij). Deshalb gilt zwingend:

1. **Keine Vorschläge, die zwei oder mehr Bausteine (oder ein Baustein
   und ein neues Themenfeld) gleichsetzen oder unter einem gemeinsamen
   Parameter/einer gemeinsamen Konstante vereinen.** Eine STRUKTURELLE
   Ähnlichkeit ist ein Grund, das Thema als EIGENSTÄNDIGEN, separat
   verifizierten Kandidaten zu bauen — NIEMALS ein Beweis, dass zwei
   Bausteine "eigentlich dasselbe" sind.
2. Keine "Universalitäts"- oder "Meta-Theorie"-Behauptungen.
3. Jede Quelle muss ein echtes, prüfbares arXiv/DOI-Zitat haben —
   keine Sekundärquellen, keine Blogposts, keine KI-generierten
   Zusammenfassungen ohne Primärquelle. Bitte angeben, WIE das Zitat
   verifiziert wurde (z.B. "DOI-Landingpage abgerufen und Titel/Autor/
   Jahr/Zeitschrift bestätigt").
4. Bevorzugt: Theorien mit einem kleinen, von Hand durchrechenbaren
   Beispiel — keine reinen Existenzsätze ohne konstruktives Beispiel.
5. Wenn zu einem Vorschlag kein konkreter, zitierbarer Satz mit
   Beispiel gefunden wird, sondern nur eine vage thematische
   Verbindung — das EHRLICH so berichten, nicht erzwingen. Das gilt
   besonders für Spur C (Autopoiesis ist historisch der
   wahrscheinlichste Kandidat für ein ehrliches "nichts gefunden").
6. Bereits verworfene Gleichsetzungen (siehe Vorgeschichte oben) dürfen
   unter KEINEM neuen Namen oder Umweg wieder eingeführt werden.

## Gewünschtes Ausgabeformat pro Vorschlag

1. Name der Theorie/des Satzes + Primärquelle (Autor, Jahr, arXiv/DOI,
   plus Verifikationsmethode).
2. Kernformel in Text/LaTeX (keine Bildformeln).
3. Spur A/B: An welchen bestehenden Baustein schließt es sich an, und
   warum — konkrete Formel-zu-Formel-Anknüpfung. Spur C: (a) oder (b)
   wie oben, plus Begründung.
4. Ein durchgerechnetes Mini-Beispiel mit konkreten Zahlen.
5. Geschätzter Umfang (klein/mittel/groß) für eine spätere Umsetzung
   nach unserem "Astra-Standard" (Textformeln, `verify_*.py` mit
   reproduzierbarem JSON-Report, durchgerechnetes Beispiel aus dem
   Skriptlauf, explizites Mapping, geprüfte Zitate).

Liefere für Spur A mindestens 2, für Spur B mindestens 2, für Spur C
alle vier genannten Themen (auch wenn das Ergebnis für einige davon
"nichts Zitierfähiges gefunden" lautet) — sortiert nach Spur. Ehrlich
vermerken, wo nichts gefunden wurde, statt einen schwachen Vorschlag zu
erzwingen. Die Bewertung, was davon umgesetzt wird, trifft Johann
separat.
