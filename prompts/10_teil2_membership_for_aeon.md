Auftrag: Teil 2, Milestone 4 ("Membership & Shared Resources") — ein Modul,
auf `correspondence`/`observation`/`dynamics`/`coupling`/`closure`/`viability`
(Milestones 1-3, alle gemergt) aufbauend.

## Kontext

`src/scoped_correspondence/{correspondence,observation,dynamics,coupling,
closure,viability}/` existieren bereits und sind verifiziert (26/26 neue
Prüfungen über M1-M3, siehe FOLLOWUP_TICKETS.md F16/F17/F18). Insbesondere
`viability/core.py` enthält bereits `shared_budget_conflict(...)` — den
gekoppelten Zwei-Puffer-Fall mit **fest verdrahteter** Zugehörigkeit (jede
Einheit gehört zu genau einem der zwei Systeme). Dieser Auftrag verallgemeinert
das auf beliebige, ggf. überlappende Zugehörigkeit.

Wichtiger Unterschied zu M1-M3: Für dieses Modul gibt es **keine bereits
bestehende dedizierte numerische Legacy-Prüfung** (kein `t_xx`/`e_xx`/`p_xx`
für `M_eα` selbst). `t10_shared_budget_conflict` ist der nächstliegende
Fall, aber er testet nur den Spezialfall disjunkter Zugehörigkeit. Für
`M_eα` und `T5` sind daher **neue, direkt aus dem Formalismustext abgeleitete
Beispiele** zu bauen — keine erfundenen Zahlen, sondern Beispiele, die sich
von Hand aus `context_transformations.md` §1/§2/§6 nachrechnen lassen.

## Umfang dieses Auftrags (bewusst begrenzt)

### 1. Zugehörigkeitsmatrix `M_eα` (context_transformations.md §1)

Quelle: §1 "Eine Einheit, mehrere Zusammenhänge".
- `MembershipMatrix`: Datentyp für `M_{eα}(t) ∈ {0,1}` (Einheiten × Systeme).
  Mehrere Einsen pro Zeile sind ausdrücklich erlaubt (Mehrfachzugehörigkeit).
- Explizit dokumentieren (Docstring + `ScopeViolationError` bei Verstoß):
  `M` ist **keine** Wahrscheinlichkeits- oder Bestandsanteilsmatrix — eine
  gewichtete Variante bräuchte eine eigene, hier nicht mitgelieferte
  Bedeutung ihrer Gewichte (§1, dritter Absatz). Binärwerte (0/1) sind der
  einzige in diesem Auftrag abgedeckte Fall.
- `MembershipMatrix` ist **nicht** die Partitionsmatrix `C` aus
  `closure/core.py` (`partition_matrix`) — beide bleiben getrennte Typen
  (§1: "Beide Matrizen haben unterschiedliche Aufgaben"). Keine gemeinsame
  Basisklasse, kein impliziter Cast zwischen beiden — analog zur bewussten
  Trennung von `AijInfluence`/`LijTransport` in `coupling/core.py`.
- `view(...)`: `y_α = π_α(z, c, t)` als generische Projektionsschnittstelle
  für eine gegebene Sicht α (kein neues physikalisches Modell — nur die
  Signatur/den Aufruf-Mechanismus aus §1 abbilden).

### 2. Doppelzählungsschutz (context_transformations.md §1, Tabelle)

- Aus der Tabelle in §1: derselbe physische Bestand `x_e` darf bei
  mehreren Zugehörigkeiten **nicht** einfach pro Zugehörigkeit aufsummiert
  werden — Reserve, Rolle und zulässige Handlung sind kontextbezogen,
  der Bestand selbst bleibt bei gleicher Messdefinition und Zeitpunkt
  derselbe. Baue eine Funktion, die für eine gegebene `MembershipMatrix`
  und einen Bestandsvektor `x` demonstriert, was bei naiver Summation über
  überlappende Systeme falsch würde (`total_naive = M.T @ x` zählt
  Mehrfachmitglieder doppelt) vs. dem korrekten, nicht-doppelt-zählenden
  Bestand pro Einheit. Konkretes durchgerechnetes Beispiel: mindestens
  eine Einheit mit Zugehörigkeit zu zwei Systemen, Zahlen von Hand
  nachrechenbar.

### 3. Gemeinsame Eingriffsmenge T5 (context_transformations.md §6)

Quelle: §6, Formel T5:
```
U_joint(z,c,m,t) = U_physical ∩ ⋂_α U_α
```
- `joint_control_set(...)`: bildet für eine gegebene Menge von
  Zugehörigkeiten und deren jeweilige Beschränkungsmengen `U_α`
  (plus `U_physical`) den Schnitt. Für den in diesem Auftrag abgedeckten
  Fall genügen **Intervalle/Boxen** in einer gemeinsamen Steuerkoordinate
  (keine allgemeine Polytop-Bibliothek — das ist laut
  ARCHITECTURE_ROADMAP.md das größere, spätere `Viability & Safe Control`-
  Modul, hier nur T5 selbst).
- Leerer Schnitt muss als expliziter "Regel- oder Ressourcenwiderspruch"
  erkennbar sein (§6, letzter Absatz) — z.B. über ein Ergebnisfeld
  `conflict: bool` oder eine `ScopeViolationError`-Variante mit klarer
  Meldung (Design-Entscheidung liegt bei dir, bitte kurz begründen).
- Verallgemeinere `shared_budget_conflict` aus `viability/core.py` NICHT
  um — lass das bestehende Modul unverändert. Baue stattdessen im neuen
  `membership`-Modul ein zusätzliches, allgemeineres Beispiel, das
  `t10_shared_budget_conflict`s Zahlen (`r=[1,1], e=[0.2,0.2], W=[0.7,0.7],
  k=0.5, U=0.75` → `a=[0.5,0.5]`, `required_joint=1`, `conflict=True`) über
  eine `MembershipMatrix` mit zwei Einheiten in genau einem gemeinsamen
  System reproduziert — als Kreuzprobe, dass `joint_control_set`/T5 mit dem
  bereits verifizierten Fall aus `viability/core.py` übereinstimmt.

### 4. Explizit NICHT Teil dieses Auftrags

- Ein allgemeiner Viability-Kernel-Solver (Polytope/Level-Sets) —
  eigenes, späteres Modul.
- Gewichtete/kontinuierliche Zugehörigkeit (`M_eα ∈ [0,1]`) — nur binär
  in diesem Auftrag, siehe oben.
- Metaregeln `m′ = H(m,z,c,u,t)` (§6, zweiter Absatz) — eigener,
  späterer Auftrag, falls überhaupt benötigt.
- Änderungen an `closure/`, `viability/`, `coupling/` oder einem der
  bestehenden Module — nur Kreuzprobe/Aufruf, keine Refaktorierung.

## Verifikation

Da es keine bestehende Legacy-Prüfung für `M_eα`/T5 gibt, MUSS
`verify_membership_core.py` mindestens folgende, alle von Hand
nachrechenbaren Fälle enthalten:
1. Doppelzählungsbeispiel (Abschnitt 2 oben) — naive vs. korrekte Summe,
   Differenz explizit ausgewiesen.
2. T5-Schnitt mit nichtleerem Ergebnis (mind. 2 Systeme, überlappende
   Zugehörigkeit, konkrete Intervallgrenzen).
3. T5-Schnitt mit leerem Ergebnis (expliziter Konflikt).
4. Kreuzprobe gegen `t10_shared_budget_conflict` (Abschnitt 3 oben) —
   Zahlen müssen exakt mit `viability/core.py`s `shared_budget_conflict`
   übereinstimmen.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_membership_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF (keine
   erfundenen Werte — hier besonders wichtig, da es keine Legacy-Zahlen
   zum Abgleich gibt außer der Kreuzprobe in Abschnitt 3).
4. Explizites Mapping auf `context_transformations.md` §1/§2/§6 — jede
   neue Funktion referenziert ihre Herkunftsstelle.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m4-membership` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht (GitHub-
Connector, kein Zip nötig). Kein Push/Merge direkt nach `master`. Claude
reviewed (Diff, Skript selbst nachrechnen, mindestens einen Fall von Hand
gegenprüfen) und merged erst nach Johanns OK — wie bei M1/M2/M3.

## Anmerkung von Johann

Nur als Randbemerkung an Aeon: Die bisherige Arbeit über M1-M3 war sehr
sauber und diszipliniert (Scope eingehalten, Kern-Dokumente unangetastet,
Zahlen reproduzierbar) — weiter so.
