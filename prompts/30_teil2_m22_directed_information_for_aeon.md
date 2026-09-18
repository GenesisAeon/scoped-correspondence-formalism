Auftrag: Teil 2, Milestone 22 ("Directed Information") — natürliche
Erweiterung von `observation`, aus der `.docx`-Recherche (Massey 1990;
Permuter, Weissman & Goldsmith, IEEE Trans. Info Theory 55(2):644–662,
2009, von Claude gegen die Quelle geprüft — Titel: "Finite State
Channels With Time-Invariant Deterministic Feedback").

## Kontext

`observation` (M2, gemergt) misst Kanalkapazität/Retention über die
deklarierte, EINSTUFIGE Interventionsinformation. Das setzt implizit
voraus, dass keine verdeckte Rückkopplung vom Beobachter auf das System
zwischen aufeinanderfolgenden Zeitschritten stattfindet. Massey (1990)
und Permuter/Weissman/Goldsmith (2009) liefern die Erweiterung für
RÜCKGEKOPPELTE Kanäle: die gerichtete Information

\[
I(X^n\to Y^n)=\sum_{i=1}^n I(X^i;Y_i\mid Y^{i-1}),
\]

isoliert den echten vorwärtsgerichteten kausalen Fluss, während die
Standard-Transinformation `I(X^n;Y^n)` bei Rückkopplung den
Informationsfluss in beiden Richtungen aufsummiert und dadurch
überzeichnet (`I(X^n→Y^n) ≤ I(X^n;Y^n)`, Gleichheit nur ohne
Rückkopplung).

**Namenskonvention:** genau EINE Größe (`observation`), keine
Vermischung mit `information_decomposition`s `EI_q` oder PID-Atomen.

## Umfang dieses Auftrags

### 1. `observation.directed_information.directed_information(joint_sequences)`

Berechnet `I(X^n→Y^n)=Σ_i I(X^i;Y_i|Y^{i-1})` für eine gegebene Folge
gemeinsamer Verteilungen (Format nach Bedarf — z.B. eine Liste
bedingter Verteilungen pro Zeitschritt, oder eine explizite
Trajektorien-Tabelle für ein kleines `n`).

### 2. Durchgerechnetes Beispiel

Baue einen binären symmetrischen Kanal (BSC) mit Störwahrscheinlichkeit
`p` über `n=2` oder `n=3` Zeitschritte, bei dem eine Rückkopplung den
zweiten Kanaleingang direkt an den vorherigen Ausgang koppelt (Docstring
muss die exakte Konstruktion angeben). Zeige explizit:

- `I(X^n→Y^n) < I(X^n;Y^n)` (die gerichtete Information ist strikt
  kleiner als die Standard-Transinformation bei echter Rückkopplung).
- Ohne Rückkopplung (Kontrollfall, Pflicht): `I(X^n→Y^n) = I(X^n;Y^n)`
  exakt (auf Maschinengenauigkeit).

Alle Entropiewerte über die Standard-Binärentropie `H(p)` von Hand
nachrechenbar angeben.

### 3. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `observation/core.py` — eigenes, separates Modul.
- Keine Verbindung zu `EI_q`/PID als gemeinsame Formel — gerichtete
  Information bleibt eine eigenständige, komplementäre Größe.
- Keine allgemeine zeitkontinuierliche Verallgemeinerung — nur der
  zeitdiskrete Fall mit endlichem `n` aus der Quelle.

## Verifikation

`verify_directed_information_core.py`: (1) BSC-mit-Rückkopplung-Fall:
`I(X^n→Y^n) < I(X^n;Y^n)` mit konkreten Zahlen aus dem Skriptlauf, (2)
Kontrollfall ohne Rückkopplung: exakte Gleichheit, (3) jeder Summand
`I(X^i;Y_i|Y^{i-1})` einzeln nichtnegativ (Grundeigenschaft bedingter
Transinformation).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_directed_information_core.py` mit reproduzierbarem JSON-
   Report unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Massey 1990 / Permuter et al. 2009 und
   `observation/core.py`s bestehende Kanalkapazitäts-Diagnostik (nur
   als Kontext, keine gemeinsame Formel).
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m22-directed-information` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 21 (`closure`), 23 (`identifiability`) und 24
(`contextuality`) bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
