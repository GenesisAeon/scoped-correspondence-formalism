Auftrag: Teil 2, Milestone 25 ("Arimoto–Blahut-Kanalkapazität") —
natürliche Erweiterung von `observation`, aus einer unabhängigen
Claude-Agenten-Recherche (Runde 2 zu `prompts/33_...md`), von BEIDEN
unabhängigen Agenten übereinstimmend vorgeschlagen (identisches
Rechenbeispiel).

## Quellen

- S. Arimoto, "An algorithm for computing the capacity of arbitrary
  discrete memoryless channels", IEEE Trans. Inf. Theory 18(1), 14–20
  (1972), DOI 10.1109/TIT.1972.1054753.
- R. Blahut, "Computation of channel capacity and rate-distortion
  functions", IEEE Trans. Inf. Theory 18(4), 460–473 (1972), DOI
  10.1109/TIT.1972.1054855.

Beide DOIs wurden von zwei unabhängigen Agenten live gegen die
Crossref-API geprüft (Titel/Autor/Jahrgang/Heft/Seiten exakt
bestätigt).

## Kontext

`observation/core.py` implementiert bisher NUR
`channel_capacity(bandwidth, snr)` — Shannon-Hartley, also exakt EIN
Kanalmodell (bandbegrenzter AWGN-Kanal). `retention`/`realized_rate`
setzen aber allgemein eine Kapazität `K_info` für ein "konkretes
Kanalmodell" voraus (FORMALISM.md §2/§3) — für jeden anderen diskreten
Kanal (asymmetrisch, mit Übersprechen, etc.) gibt es bisher keine
Berechnungsmöglichkeit.

Der Arimoto-Blahut-Algorithmus berechnet die Kapazität für einen
BELIEBIGEN diskreten gedächtnislosen Kanal (DMC) mit gegebener
Übergangsmatrix, per alternierender Maximierung.

## Umfang dieses Auftrags

### 1. `observation.arimoto_blahut.blahut_arimoto_capacity(Q, ...)`

`Q` ist eine Übergangsmatrix (Zeilen = Eingabesymbole, Spalten =
Ausgabesymbole, zeilenstochastisch). Implementiert die alternierende
Iteration aus Arimoto (1972)/Blahut (1972):

    q(x|y)^(n) = r_x^(n) Q(y|x) / sum_x' r_x'^(n) Q(y|x')
    r_x^(n+1) ∝ exp( sum_y Q(y|x) log q(x|y)^(n) )

bis Konvergenz (dokumentierte Toleranz + Iterationslimit). Rückgabe:
Kapazität `C` (bit/use) UND die konvergierte optimale Eingabeverteilung
`r*`. `ScopeViolationError` wenn `Q` nicht zeilenstochastisch ist oder
negative Einträge hat.

### 2. Pflicht-Validierung: Z-Kanal-Beispiel

Z-Kanal mit Übersprungwahrscheinlichkeit ε=0,5 (Eingabe 0 → Ausgabe 0
mit Wahrscheinlichkeit 1; Eingabe 1 → Ausgabe 1 mit 0,5, Ausgabe 0 mit
0,5). Geschlossene Form (zur Gegenprobe im Skript, nicht als
Eingabeparameter): `C = log2(1 + (1-ε)·ε^(ε/(1-ε)))`. Bei ε=0,5 ergibt
das `C = log2(1,25) = 0,3219280948873623` bit, mit optimaler
Eingabeverteilung `r* = (0,6; 0,4)`. Der Algorithmus MUSS — ausgehend
von einer uniformen Startverteilung — gegen exakt diese beiden Werte
konvergieren (Toleranz dokumentieren).

### 3. Pflicht-Kontrollfall: symmetrischer Kanal

Ein binärer symmetrischer Kanal (BSC) mit p=0,1: geschlossene Form
`C=1-H_2(0,1)=0,5310044064107189` bit, optimale Eingabe uniform
(0,5; 0,5) — bei diesem Kanal muss der Algorithmus bereits ab der
uniformen Startverteilung (nahezu) sofort konvergieren, da die
Startverteilung schon optimal ist. Dient als zweiter, unabhängiger
Gegencheck.

### 4. Explizit NICHT Teil dieses Auftrags

- KEIN Rate-Distortion-Zweig (`R(D)`) — kann eine spätere, eigene
  Erweiterung sein, hier nicht verlangt.
- KEINE Änderung an `channel_capacity`/`retention`/`realized_rate` in
  `observation/core.py` — nur additiver Aufruf zur Einordnung, falls
  sinnvoll (z.B. Docstring-Verweis, dass dies EIN weiteres, allgemeineres
  Kanalmodell neben Shannon-Hartley ist, kein Ersatz).
- KEINE Behauptung, dass dieses Ergebnis mit dem AWGN-Kanal aus
  `channel_capacity` "dieselbe Formel" ist — unterschiedliche
  Kanalmodelle, unterschiedliche Voraussetzungen (diskret vs.
  bandbegrenzt kontinuierlich), im Docstring explizit festhalten.
- KEINE allgemeine Informationstheorie-Bibliothek — nur Kapazität für
  eine gegebene, endliche Übergangsmatrix.

## Verifikation

`verify_arimoto_blahut_capacity.py`: (1) Z-Kanal-Beispiel oben exakt
reproduziert (Zahlen aus dem Skriptlauf, nicht hartkodiert als
Referenzwert im Test — die geschlossene Form wird im Skript SELBST
berechnet und gegen das Konvergenzergebnis verglichen), (2) BSC-
Kontrollfall, (3) Konvergenztest: Iterationszahl bis zur dokumentierten
Toleranz wird berichtet.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_arimoto_blahut_capacity.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF (Z-Kanal +
   BSC-Kontrolle).
4. Explizites Mapping auf Arimoto (1972)/Blahut (1972) UND auf
   `observation/core.py`s bestehende `K_info`-Rolle — mit der
   ausdrücklichen Klarstellung, dass dies ein zusätzliches, allgemeineres
   Kanalmodell ist, kein Ersatz für Shannon-Hartley.
5. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m25-arimoto-blahut-capacity` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 26 (`coupling`), 27 (`membership`), 28
(`viability`) und 29 (`dynamics`) bearbeitet werden — alle fünf
betreffen unterschiedliche Module. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
