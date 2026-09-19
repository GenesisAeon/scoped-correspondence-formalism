Auftrag: Teil 2, Milestone — Generalisierte Synchronisation
(Pecora-Carroll) als mathematische Fassung "struktureller Kopplung" —
Erweiterung von `coupling`. Aus Runde 3, Spur C. Von ALLEN VIER
unabhängigen Rechercheagenten übereinstimmend vorgeschlagen.

## Vorgeschichte (Pflichtkontext für den Docstring)

Dieses Projekt war ursprünglich u.a. von Luhmanns Konzept
"struktureller Kopplung" inspiriert — einem soziologischen, nicht
mathematischen Begriff. Pecora & Carrolls Synchronisationstheorie ist
KEINE Übersetzung von Luhmann, sondern eine eigenständige, echte
mathematische Theorie über gekoppelte dynamische Systeme, die
zufällig denselben Alltagsbegriff nahelegt. Im Docstring explizit
festhalten: "mathematische Fassung im Sinne dynamischer Mitführung,
KEINE Luhmann-Soziologie, KEINE Gleichsetzung."

## Quelle

L. M. Pecora & T. L. Carroll, "Synchronization in chaotic systems",
Phys. Rev. Lett. 64, 821–824 (1990), DOI 10.1103/PhysRevLett.64.821.
Von allen vier Agenten per Crossref-API verifiziert (exakter Titel,
beide Autoren, Band, Seiten, Jahr).

## Kernformel

Drive-Response-System: `ẋ = f(x)` (Treiber), `ẏ = g(y,x)` (Antwort).
Variationsgleichung entlang der Antwort: `δẏ = D_y g(x(t),y(t))·δy`.
Bedingung: sind ALLE bedingten Lyapunov-Exponenten (CLE) dieser
Variationsgleichung NEGATIV, synchronisiert die Antwort mit dem
Treiber (`y(t)→Φ(x(t))` für eine Funktion `Φ`).

## Umfang dieses Auftrags

Neue Datei `src/scoped_correspondence/coupling/generalized_sync.py`.

### 1. `coupling.generalized_sync.conditional_lyapunov_linear(a_response)`

Für den linearen Spezialfall `δẏ = a·δy` (skalar): CLE `= a`.
Synchronisation ⟺ `a<0`.

### 2. `coupling.generalized_sync.linear_drive_response_map(c, k)`

Für `ẋ=-x` (Treiber), `ẏ=-ky+cx` (Antwort): sucht `y=φ·x` mit
`φ=c/(k-1)` (für `k≠1`), gibt `φ` und die CLE (`=-k`) zurück.
`ScopeViolationError` bei `k=1`.

### 3. Durchgerechnetes Beispiel (Pflicht)

`c=4, k=3`: `φ=4/(3-1)=2`, CLE`=-3<0` — Synchronisation, `y(t)→2x(t)`.
Gegenprobe: `d(y-2x)/dt = ẏ-2ẋ = (-3y+4x)-2(-x) = -3y+6x = -3(y-2x)` —
zeigt exakt exponentielles Abklingen mit Rate 3. Negativfall `c=4,
k=-1`: `φ=4/(-2)=-2` (formal definiert), aber CLE`=+1>0` —
KEINE Synchronisation trotz existierender formaler Abbildung `φ`
(`‖y-φx‖` wächst wie `e^t`). Dieser Kontrast (Abbildung existiert vs.
Abbildung wird tatsächlich erreicht) MUSS im Report explizit als
zwei getrennte Felder erscheinen.

### 4. Pflicht-Brücken-Vermerk (Docstring, wörtlich)

"Das CLE<0-Kriterium hier ähnelt strukturell der bereits gemergten
Kontraktionsanalyse (M14, `dynamics/contraction.py`, Lohmiller &
Slotine 1998) — beide sind Vorzeichenkriterien an einer
Variationsgleichung. Das ist KEINE Identität: M14 prüft globale
metrische Kontraktion EINES Systems, dieses Modul prüft
Drive-Response-Synchronisation ZWISCHEN zwei gekoppelten Systemen in
`coupling`. Eine mögliche künftige `correspondence`-Brücke zwischen
den beiden Kriterien ist denkbar, aber HIER NICHT behauptet oder
implementiert — offener, unbewiesener Kandidat, analog zum
dokumentierten Turing↔dynamics-Brückenkandidaten in
`pattern_formation/core.py`."

### 5. Explizit NICHT Teil dieses Auftrags

- KEIN chaotisches/hochdimensionales Beispiel (z.B. Lorenz-Treiber) —
  nur der lineare Fall, exakt handprüfbar.
- KEINE Änderung an `coupling/core.py` oder `dynamics/contraction.py`.
- KEINE Luhmann-Zitate oder soziologische Begründung — rein
  mathematisch.

## Verifikation

`verify_generalized_sync_core.py`: (1) Beispiel oben exakt reproduziert
(beide Fälle, positiv und negativ), (2) der Brücken-Vermerk erscheint
wörtlich im JSON-Report als Textfeld.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/generalized_sync_core.md`, MIT Vorgeschichte
   und Brücken-Vermerk.
3. `verify_generalized_sync_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Pecora & Carroll (1990).
6. Der Brücken-Vermerk aus Punkt 4 MUSS wörtlich im Docstring UND im
   JSON-Report erscheinen — Abnahmekriterium.
7. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente.
8. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m39-pecora-carroll-sync`. Kann PARALLEL zu den
anderen Runde-3-Milestones bearbeitet werden (auch zu Milestone 38,
GENERIC-NS, das ebenfalls `coupling` betrifft). Bitte NICHT
`src/scoped_correspondence/__init__.py`, `coupling/core.py` oder
`dynamics/contraction.py` anfassen. Claude reviewed und merged erst
nach Johanns OK.
