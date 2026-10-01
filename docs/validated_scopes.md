# Nachweise über ganze unterstützte Bereiche (J5)

Paket J5 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §11. Code: `src/scoped_correspondence/assurance/rational_intervals.py`,
`.../expressions.py`, `.../scope_certification.py`. Prüfung:
`verification/verify_validated_scopes.py` (math). Lizenz der
Dokumentation: CC BY 4.0.

## 1. Was bewiesen werden kann

Aussagen der Form

$$\forall x\in B:\ e(x)\le\varepsilon\qquad\text{bzw.}\qquad \forall x\in B:\ e(x)\ge\varepsilon$$

für eine rationale achsenparallele Box $B$ und einen Ausdruck $e$ aus
der unterstützten Klasse: Konstanten, Variablen, $+$, $-$, $\times$,
Vorzeichenwechsel, ganzzahlige Potenzen $n\ge0$ und Division, sofern der
Nennerbereich null ausschließt. `certify_abs_bound` liefert
$|e|\le\varepsilon$ als **zwei getrennte** Berichte.

**Nicht** unterstützt: beliebige Python-Callbacks (häufigeres Auswerten
macht daraus keinen beweisfähigen Ausdruck), transzendente Funktionen,
numerische ODE-Lösungen. Eine ODE-Lösung mit `atol`/`rtol` ist kein
validierter Flussnachweis; validierte Integration wäre ein eigenes Paket
(Plan §22).

## 2. Arithmetik

Rationale Intervallendpunkte (`fractions.Fraction`) machen jede
Grundoperation exakt einschließend — kein Gleitkomma, also auch keine
gerichtete Rundung nötig. Gerade Potenzen sind scharf ($x^2$ auf
$[-1,2]$ ist $[0,4]$), das Produkt $x\cdot x$ dagegen nicht ($[-2,4]$,
Abhängigkeitseffekt). Ein Nenner, dessen Einschluss null enthält, löst
`DenominatorContainsZero` aus — nie ein „unendliches“ oder leeres
Intervall.

Konstanten sind exakt. Dezimalzahlen kommen als Zeichenkette
(`Const("0.1")` = $1/10$). Ein binärer Float ist nur über
`Const.of_float` zulässig und behält dann seinen **exakten Binärwert**
($0.1\mapsto3602879701896397/2^{55}$) — `Fraction(str(float))` würde
still eine andere Zahl bedeuten.

## 3. Algorithmus (`certify_bound`)

1. Ausdruck, Box, Schranke und Budget validieren (Gleitkommaschranken,
   ungebundene Variablen und Callbacks sind Eingabefehler).
2. Je Box zuerst exakte Punktauswertungen (Mitte, dann Ecken): eine
   Verletzung ist ein **Gegenbeispiel** (`refuted`, ohne den Rest
   abzusuchen); ein Nenner null an einem solchen Punkt ergibt
   `undefined_on_domain` mit Zeugenpunkt.
3. Natürlicher Einschluss; impliziert er die Schranke, gilt die Box als
   bewiesen.
4. Sonst deterministische Halbierung (breiteste Achse, bei Gleichstand
   die erste Variable); beide Hälften überdecken die Mutterbox exakt. Ein
   Nennereinschluss mit null wird ebenfalls weiter unterteilt.
5. Bei Budgetende: `undecided`/`budget_exhausted` mit den **ungelösten
   Restboxen** als Zeugen — kein universeller Erfolg. Enthielten dabei
   Nennereinschlüsse die Null, sagt der Bericht ausdrücklich, dass die
   Definitionsvoraussetzung nicht nachgewiesen ist.
6. Leere Box: vakuos wahr, `empty_domain` markiert, kein Zertifikat.

Ergebnisse bleiben getrennt: **bewiesen**, **widerlegt**,
**unentschieden** und **nicht definierte Eingabe**.

## 4. Erneute Prüfbarkeit

Jeder Beweis liefert ein `BoundCertificate` (Ausdruck, Seite, Schranke,
Bereich, Partition mit den Einschlüssen). `recheck_certificate` prüft
unabhängig: jede Box liegt im Bereich, ihr Einschluss wird exakt
reproduziert und impliziert die Schranke, die Boxen überlappen nicht im
Volumen, und ihre Volumina summieren sich zum Bereichsvolumen. Eine
fehlende Box, ein geschönter Einschluss oder die Wiederverwendung der
Partition für eine strengere Schranke werden erkannt.

## 5. Kontrollen

- **J-C09:** $p=x(1-x)$ auf $[0,1]$: Bei 64 gleichen Teilintervallen ist
  die größte natürliche Obergrenze genau $33/128$; $p\le13/50$ wird
  bewiesen (zertifikatsgeprüft), $p\le6/25$ durch $x=1/2$ (Wert $1/4$)
  widerlegt. Die scharfe Grenze $1/4$ bleibt mit natürlicher
  Intervallrechnung unter endlichem Budget **unentschieden** — vom Plan
  ausdrücklich zugelassen; sie wird nie fälschlich widerlegt.
- **J-C10:** $x-x$ auf $[0,1]$ hat den natürlichen Einschluss $[-1,1]$;
  die scharfe Nullschranke wird ohne symbolische Vereinfachung nicht
  bewiesen, eine nicht scharfe ($\le1/2$) dagegen durch Unterteilung.
  $1/x$ auf $[-1,1]$: `undefined_on_domain`, Zeuge $x=0$.
- **Nenner nahe null, drei Fälle:** (a) $1/x\le1000$ auf $[-1,1/2]$ ist
  wahrhaft falsch nahe $0^+$ → widerlegt; (b) $1/(x^2-x+1)$ auf $[0,1]$:
  der Nenner ist $\ge3/4$, sein natürlicher Einschluss $[0,2]$ enthält
  aber null → nach Unterteilung bewiesen; (c) $x/x$ auf $[-1,1/2]$: überall
  außer in 0 gleich 1, die dyadische Halbierung trifft 0 nie →
  unentschieden mit Definitionswarnung.
- **J4-Anschluss:** Das Feldresiduum aus J-C07,
  $r_{12}=3(2x-2\cdot0)+2(3\cdot0+3)=6x+6$, als Ausdrucksbaum aus den
  T4-Bausteinen aufgebaut: $|r_{12}|\le9$ auf $[0,1/2]$ bewiesen, Grenze
  bei $x=1/2$ erreicht, $r_{12}(1/4)=15/2$.

Weitere Prüfungen: genaue Grenzberührung bei linearem Ausdruck
($2x+1\le3$ wird bewiesen), negative Koeffizienten, einfache und
wiederholte Variablen, zweidimensionale Box mit Ober- und Untergrenze,
Restboxen bei Budgetende, leere Box.

## 6. Quelle

S08 JuliaIntervals (IntervalArithmetic.jl, IntervalRootFinding.jl,
TaylorModels.jl) — Links siehe Plan §21. Kein Pflichtimport; die
rationale Erstversion ist eigenständig. Ein späterer Anschluss an
etablierte validierte Arithmetik ist möglich.
