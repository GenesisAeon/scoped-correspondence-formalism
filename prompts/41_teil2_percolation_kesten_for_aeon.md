Auftrag: Teil 2, neuer eigenständiger Baustein "percolation"
(Kesten-Theorem / Verzweigungsprozess auf dem Bethe-Gitter) — KEIN
Erweiterungs-Milestone eines bestehenden Bausteins, sondern ein
komplett neues, eigenständiges Modul. Aus einer unabhängigen Claude-
Agenten-Recherche (Runde 2 zu `prompts/33_...md`) plus Johanns
expliziter Grundsatzentscheidung (2026-09-19).

## Warum ein NEUER Baustein statt einer `dynamics`/`membership`-Erweiterung

Perkolation ist eine Aussage über die a.s.-Existenz eines unendlichen
Clusters in einem ZUFÄLLIGEN Teilgraphen — kein Vektorfeld, kein
Fixpunkt, kein Eigenwert wie in `dynamics`; `membership.MembershipMatrix`
ist eine DEKLARIERTE (nicht zufällige) binäre Matrix ohne
Konnektivitätsbegriff. Beide unabhängigen Rechercheagenten stuften dies
unabhängig als (b) — eigener Baustein — ein.

**Pflicht-Warnhinweis (Docstring, wörtlich):** die Perkolationsschwelle
`p_c` und die Cusp-Schwelle in `dynamics` (`4a^3>27b^2`) werden beide
umgangssprachlich "Schwelle" genannt — das ist KEINE Verwandtschaft,
nur derselbe Alltagsbegriff für zwei mathematisch verschiedene Objekte.
Ebenso: der Zwischenwert `Q=1/16`, der bei bestimmten Parameterwahlen
im Verzweigungsprozess auftreten KANN, hat KEINERLEI Beziehung zu dem
bereits in `README.md` als verworfen gelisteten Wert "1/16" — falls das
gewählte Beispiel zufällig auf `1/16` trifft, MUSS das explizit als
Zufall vermerkt werden statt kommentarlos stehen zu bleiben.

## Quellen

- H. Kesten, "The critical probability of bond percolation on the
  square lattice equals 1/2", Communications in Mathematical Physics
  74(1), 41–59 (1980), DOI 10.1007/BF01197577.
- M. E. Fisher & J. W. Essam, "Some Cluster Size and Percolation
  Problems", Journal of Mathematical Physics 2(4), 609–619 (1961), DOI
  10.1063/1.1703745 (enthält die exakten Lösungen für Bethe-Gitter /
  Baum-Verzweigungsprozesse, auf denen das Rechenbeispiel unten
  beruht).

Beide DOIs von zwei unabhängigen Agenten per Crossref-API verifiziert.

## Umfang dieses Auftrags

Neues Paket `src/scoped_correspondence/percolation/` mit
`__init__.py` und `core.py`.

### 1. `percolation.critical_probability_tree(m)`

Für einen gewurzelten Baum, bei dem jeder Knoten genau `m` Kinder hat:
`p_c = 1/m`. `ScopeViolationError` bei `m < 1`.

### 2. `percolation.extinction_probability(p, m, tol=1e-12, max_iter=1000)`

Löst per Fixpunktiteration (Startwert `Q_0=0` oder `Q_0=0.5` —
dokumentieren) die Verzweigungsprozess-Gleichung

    Q = (1 - p + p*Q)^m

für die KLEINSTE nichtnegative Lösung `Q* <= 1` (Standard-Galton-
Watson-Aussterbewahrscheinlichkeit). Gibt `Q*`, Iterationszahl und
Residuum zurück.

### 3. `percolation.percolation_probability(p, m)`

`theta = 1 - Q*` unter Verwendung von `extinction_probability`.

### 4. Durchgerechnetes Beispiel (Pflicht) — binärer Baum, m=2

- `p_c = 1/m = 0,5` exakt (per `critical_probability_tree`).
- Bei `p=0,6`: die Fixpunktgleichung `Q=(0,4+0,6*Q)^2` hat die exakte
  algebraische Lösung `9Q^2-13Q+4=0` → `Q=(13±5)/18` → Wurzeln `{1;
  4/9}`. Die relevante (kleinste, physikalisch stabile) Wurzel ist
  `Q*=4/9≈0,444444`. Daraus `theta(0,6)=1-4/9=5/9≈0,555556`. Die
  Fixpunktiteration MUSS numerisch gegen `4/9` konvergieren — im
  Report BEIDE Werte nebeneinander zeigen (exakte algebraische Wurzel
  UND numerisches Konvergenzergebnis), Differenz < 1e-9.
- Kritischer Kontrollfall `p=0,5`: Gleichung wird zu `(Q-1)^2=0` →
  `Q*=1`, `theta=0` exakt — die Iteration muss ebenfalls hierauf
  konvergieren.
- Fall oberhalb der Schwelle, `p=0,8` (zur Illustration der Wertespanne,
  NICHT als Zielwert 1/16 gesucht — falls die Iteration bei diesem oder
  einem anderen Parameter zufällig nahe `1/16` landet, dies explizit im
  Report als Zufallskoinzidenz vermerken, siehe Pflicht-Warnhinweis
  oben).

### 5. Explizit NICHT Teil dieses Auftrags

- KEINE Monte-Carlo-Simulation auf `Z^2` (Kesten selbst ist ein
  Existenz-/Exaktheitssatz für das quadratische Gitter, keine
  numerische Nachbildung nötig oder gefordert) — nur der exakt lösbare
  Baum-/Bethe-Gitter-Fall.
- KEINE Änderung an `dynamics/core.py`, `membership/core.py` oder
  irgendeinem anderen bestehenden Modul.
- KEINE Gleichsetzung mit der Cusp-Schwelle aus `dynamics` — Pflicht-
  Warnhinweis oben ist Abnahmekriterium.
- KEIN Union-Find-/Newman-Ziff-Algorithmus — nicht nötig für den
  exakt lösbaren Baumfall.

## Verifikation

`verify_percolation_core.py`: (1) `p=0,6`-Beispiel exakt reproduziert
(exakte Wurzel UND numerische Konvergenz, beide im Report), (2)
kritischer Fall `p=0,5` exakt `Q*=1, theta=0`, (3) Kontrollfall
`p_c=1/m` für mindestens zwei verschiedene `m` (z.B. `m=2→p_c=0,5` und
`m=4→p_c=0,25`).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/percolation_core.md` — Format wie
   `docs/metarules_core.md` (Quellen, Formeln, durchgerechnetes
   Beispiel, Out-of-Scope-Abschnitt, BEIDE Pflicht-Warnhinweise aus
   dem Abschnitt oben wörtlich).
3. `verify_percolation_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Kesten (1980) und Fisher & Essam (1961).
6. Die beiden Pflicht-Warnhinweise (Schwellen-Wortgleichheit,
   1/16-Zufallskoinzidenz) MÜSSEN wörtlich im Docstring erscheinen —
   Abnahmekriterium, nicht optional.
7. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente, KEINE Änderung an irgendeinem bestehenden Baustein-
   Verzeichnis.
8. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m32-percolation-kesten` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu den beiden anderen neuen Bausteinen (Musterbildung, freie
Randbedingung) bearbeitet werden — komplett unabhängige, neue
Verzeichnisse. Bitte NICHT `src/scoped_correspondence/__init__.py`
oder irgendein bestehendes Baustein-Verzeichnis anfassen. Claude
reviewed und merged erst nach Johanns OK.
