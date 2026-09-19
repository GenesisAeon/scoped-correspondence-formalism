Auftrag: Teil 2, Milestone 27 ("Formal Concept Analysis auf der
Membership-Matrix") — natürliche Erweiterung von `membership`, aus
einer unabhängigen Claude-Agenten-Recherche (Runde 2 zu
`prompts/33_...md`). Schließt die bisherige "kein Kandidat"-Lücke in
`EXTENSIONS_ROADMAP.md`.

## Quelle

B. Ganter & R. Wille, "Formal Concept Analysis: Mathematical
Foundations", Springer Berlin Heidelberg (1999), DOI
10.1007/978-3-642-59830-2. Per Crossref-API verifiziert (Titel, beide
Autoren, Verlag, Buch, Jahr).

## Kontext

`membership.core.MembershipMatrix` ist eine binäre Matrix `M_eα ∈
{0,1}` (Entitäten × Systeme), mehrere Einsen pro Zeile erlaubt
(überlappende Zugehörigkeit). `EXTENSIONS_ROADMAP.md` führt
`membership` bisher als EINZIGEN Baustein ohne Kandidaten, mit der
Begründung "gewichtete/kontinuierliche Zugehörigkeit bewusst
zurückgestellt, Semantik unklar".

**Wichtig:** dieser Auftrag braucht KEINE gewichtete Semantik. Eine
binäre Entitäten×Systeme-Matrix ist WÖRTLICH ein "formaler Kontext"
`(G,M,I)` im Sinne von Ganter & Wille (G=Entitäten, M=Systeme, I=die
Einsen). Die zurückgestellte Begründung blockiert diesen Vorschlag
also nicht.

## Umfang dieses Auftrags

### 1. `membership.formal_concept_analysis.derive_up(entity_indices, M)`
### `membership.formal_concept_analysis.derive_down(system_indices, M)`

Die Galois-Operatoren:

    A↑ = { α : für alle e in A gilt M[e,α]=1 }   (A ⊆ Entitäten)
    B↓ = { e : für alle α in B gilt M[e,α]=1 }   (B ⊆ Systeme)

Nimmt eine `MembershipMatrix` (bereits gemergt, aus `membership.core`)
entgegen — KEINE eigene Matrix-Repräsentation einführen.

### 2. `membership.formal_concept_analysis.all_concepts(M)`

Enumeriert ALLE Formalen Konzepte `(A,B)` mit `A↑=B` und `B↓=A` (Brute-
Force über alle Teilmengen ist für die Matrixgrößen dieses Repos
ausreichend — dokumentieren, warum kein NextClosure-Algorithmus nötig
ist). Rückgabe als Liste von `(A,B)`-Paaren, geordnet nach `|A|`
absteigend (größte Extension zuerst = "top" des Verbands).

### 3. `membership.formal_concept_analysis.is_concept(A, B, M)`

Prüft die Abschlusseigenschaft `A↑=B ∧ B↓=A` für ein gegebenes Paar.

### 4. Durchgerechnetes Beispiel

4 Entitäten × 3 Systeme:

    M = [[1,1,0],
         [1,0,1],
         [1,1,1],
         [0,1,0]]

(e1: s1,s2 / e2: s1,s3 / e3: s1,s2,s3 / e4: s2)

Der VOLLSTÄNDIGE Konzeptverband hat GENAU 6 Konzepte:

    ({e1,e2,e3,e4}, {})
    ({e1,e2,e3}, {s1})
    ({e1,e3,e4}, {s2})
    ({e1,e3}, {s1,s2})
    ({e2,e3}, {s1,s3})
    ({e3}, {s1,s2,s3})

Das Skript MUSS diese 6 Konzepte aus `M` selbst herleiten (nicht
hartkodieren) und mindestens EINE abgeleitete Implikation explizit
berichten: aus dem Konzept `({e2,e3},{s1,s3})` folgt, dass die
Extension von "s3" (={e2,e3}) in der Extension von "s1" (={e1,e2,e3})
enthalten ist — d.h. Mitgliedschaft in s3 impliziert (in diesem
Datensatz) Mitgliedschaft in s1. Diese Implikation soll als lesbares
Ergebnisfeld im JSON-Report erscheinen, nicht nur implizit im
Konzeptverband stecken.

### 5. Explizit NICHT Teil dieses Auftrags

- KEINE gewichtete/kontinuierliche Zugehörigkeit — bleibt binär wie
  `MembershipMatrix` selbst.
- KEINE Änderung an `membership/core.py` — nur Aufruf von
  `MembershipMatrix`.
- KEIN NextClosure- oder sonstiger Skalierungsalgorithmus für große
  Kontexte — Brute-Force reicht für dieses Repo, im Docstring
  begründen.
- KEINE Verbindung zu `metarules.priority_joint_control_set` oder
  anderen Modulen behaupten — reine `membership`-Erweiterung.

## Verifikation

`verify_formal_concept_analysis.py`: (1) Beispiel oben exakt
reproduziert — alle 6 Konzepte, aus dem Skriptlauf, (2) Abschluss-
Eigenschaft für mindestens 2 der 6 Konzepte explizit per
`is_concept` gegengeprüft, (3) Negativtest: eine NICHT-abgeschlossene
Teilmenge (z.B. `A={e1,e2}`, `B={s1}`) zeigen, dass `is_concept` dafür
`False` liefert (`A↑={s1}`, aber `{s1}↓={e1,e2,e3} ≠ A`).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_formal_concept_analysis.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen/Konzepten AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Ganter & Wille (1999) UND auf
   `membership.core.MembershipMatrix`.
5. KEINE Mutation von FORMALISM.md, `context_transformations.md` oder
   einem der anderen sechs Kerndokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m27-formal-concept-analysis` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 25 (`observation`), 26 (`coupling`), 28
(`viability`) und 29 (`dynamics`) bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
