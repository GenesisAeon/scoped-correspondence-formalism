Auftrag: Teil 2, Vorbereitung von Milestone 6 ("Uncertainty & Validation" —
realer Datenpilot) — KEIN Code-Auftrag. Ziel ist eine Kandidatenliste für
Johanns Domänenentscheidung, nicht die Entscheidung selbst und kein Pilot.

## Kontext

`identifiability` (M5) ist gemergt — die *formal durchgerechneten* Teile
von "Uncertainty & Validation" sind fertig. Offen ist der zweite Teil:
"Dataset Manifest, Train/Holdout, ein echter Pilot mit realen Daten"
(ARCHITECTURE_ROADMAP.md). `ROADMAP.md` §3 verlangt dafür zuerst:

> Eine Domäne, eine überprüfbare Makrovariable: Zustände, Eingaben,
> Sampling und Beobachtung festlegen ... Keine gleichzeitige
> Universalitätsbehauptung über alle Pakete.

Diese Entscheidung trifft Johann, nicht Aeon oder Claude — siehe die
Diskussion, warum ein aus mehreren Domänen "zurückgerechneter" gemeinsamer
Stamm methodisch genau der Fehler wäre, der in Revision 2/3 bereits
korrigiert wurde (geteiltes σ=2,2 als Scheinuniversalität). Dieser Auftrag
liefert daher NUR eine Faktenbasis, aus der Johann wählt.

## Aufgabe: Kandidaten-Survey (kein Pilot, kein Code)

Für 4-6 Kandidaten aus dem GenesisAeon-Ökosystem (Vorschlag als Startpunkt,
nicht abschließend — siehe `ROADMAP.md` §5, priorisierte Gruppe:
`afet-tensions`, `amoc-utac`, `cygnus-jet-utac`, `neural-avalanche-utac`,
`solar-flare-utac`; weitere aus `PACKAGE_REGISTRY.md`/`ECOSYSTEM_INVENTORY.md`
sind erlaubt, wenn sie dieselben Kriterien erfüllen) jeweils dokumentieren:

1. **Datenherkunft:** reale Beobachtung, Simulation, oder beides getrennt
   ausgewiesen? (F06: "Beobachtungs- und Simulationspfade für Γ verfolgen"
   — noch offen, hier erstmals pro Kandidat beantworten.)
   `afet-tensions` hat laut `ROADMAP.md` bereits einen "echten
   Mehrdaten-Refit von Γ/κ" — dort zuerst prüfen, ob reale Rohdaten
   (nicht nur der Refit-Code) tatsächlich vorliegen und zugänglich sind.
2. **Makrovariable:** genau EINE klar benennbare, beobachtbare Größe pro
   Kandidat (kein Bündel mehrerer Metriken).
3. **Datenmenge:** reicht sie für einen Kalibrierungs-/Holdout-Split
   (mindestens zwei unabhängige Zeitabschnitte oder Trajektorien,
   `ROADMAP.md` §3 Punkt 4)?
4. **Bestehende Formelanknüpfung:** welche(s) der bereits gemergten Module
   (`dynamics`, `observation`, `coupling`, `closure`, `viability`,
   `identifiability`) würde diese Domäne am ehesten testen — rein als
   Fakt ("dieses Paket nutzt Relaxationsdynamik ähnlich `dynamics.core`"),
   NICHT als Erwartung, dass der Test positiv ausgeht.
5. **Zugriffsaufwand:** liegt die Datei bereits im Repo/Paket, oder
   müsste sie neu beschafft werden (externe Quelle, Download, Lizenz)?

## Ausdrücklich verbotenes Auswahlkriterium

**Nicht bewerten, wie gut die Domäne voraussichtlich zur Formel passen
würde.** Kein "Kandidat X passt wahrscheinlich gut zu `dynamics.core`,
deshalb empfehlenswert". Auswahlkriterien sind ausschließlich
Datenverfügbarkeit, Datenqualität und Durchführbarkeit des
Kalibrierung/Holdout-Splits — nicht erwarteter theoretischer Erfolg.
Ein Kandidat, bei dem die Formel wahrscheinlich NICHT passt, ist genauso
zulässig wie jeder andere; das herauszufinden ist der Zweck des Piloten.

## Format der Lieferung

Eine Markdown-Tabelle (kein Code, kein Skript, keine neue Datei unter
`src/`) mit den fünf Spalten oben, plus je einem Satz "Was noch fehlt,
um startklar zu sein" pro Kandidat. Kein Ranking, keine Empfehlung
welcher Kandidat "der beste" ist — nur die Fakten, damit Johann
entscheidet. Direkt als Markdown-Antwort oder kurze Datei im
`prompts/Answers/`-Ordner, kein Branch nötig (kein Code-Merge).

## Explizit NICHT Teil dieses Auftrags

- Kein `verify_*.py`, kein neues Modul, keine Code-Änderung.
- Keine Kalibrierung, kein Fit, kein tatsächlicher Datenzugriff über das
  Prüfen von Verfügbarkeit hinaus.
- Keine Entscheidung, welcher Kandidat gewählt wird — das bleibt Johann.
- Kein Dataset-Manifest-Schema (kommt erst NACH der Domänenentscheidung,
  als eigener Folgeauftrag mit Code).

## Nächster Schritt nach dieser Lieferung

Johann wählt einen Kandidaten (oder verwirft alle und nennt einen
eigenen). Erst danach schreibe ich den Code-Auftrag für Dataset Manifest
+ Train/Holdout-Split + `ValidationReport` für genau diese eine Domäne.
