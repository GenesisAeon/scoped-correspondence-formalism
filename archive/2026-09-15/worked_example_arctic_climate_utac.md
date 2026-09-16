# Durchgespielt: arctic-climate-utac (P127) -- Phase 1, Beispiel 2/3 (2026-09-15)

## Ergebnis: N/A -- explizit durch bestehende Policy ausgenommen, nicht durch fehlende Eignung

Anders als bei `afet-tensions` und `resilience-core` gibt es hier keine
Individuations-/Kopplungsanalyse durchzuführen: das Paket besteht
ausschließlich aus eingefrorenen (`@dataclass(frozen=True)`) Literatur-
Konstanten und booleschen Vergleichsfunktionen (`is_..._consensus()` etc.)
-- keine Zeitentwicklung, kein Kontrollparameter, keine Trajektorie.
Kategorisch kein "System" in unserem Sinne, sondern ein Zitations-Atlas.

**Wichtiger, weiterreichender Fund:** das ist kein Zufall dieses einen
Pakets. `DISCLAIMER.md` zitiert eine kanonische, bereits am 2026-08-31
getroffene Entscheidung (`PACKAGE_REGISTRY.md`, Abschnitt "Why no
UTAC/CREP/AFET bridge in the climate/ecology series"): eine GANZE
Paketfamilie -- P59, P60, P87–P97, P99–P103, P105–P121 (`carbon-sinks-utac`
P59 als dokumentierte Ausnahme mit eigener spekulativer Bridge) -- ist
bewusst von jeder CREP/UTAC/AFET-Anbindung ausgenommen.

## Die ursprüngliche Begründung (2026-08-31, verbatim aus PACKAGE_REGISTRY.md)

Zwei separate Gründe, nicht einer:
1. "the cited literature already provides the necessary quantitative
   structure on its own" -- ein Aussagekraft-/Evidenz-Argument.
2. "this project's highly speculative AFET/UTAC experiments must never
   stand in the way of the climate/ecology topics being accessible and
   usable to people who don't work inside this construct" -- ein
   Zugänglichkeits-/Prinzipien-Argument, unabhängig vom Evidenzstatus.

## Klarstellung (2026-09-15, auf Johanns ausdrücklichen Wunsch)

Grund 1 (Evidenzlage von CREP/UTAC/AFET) hat sich seit dem 2026-08-31
messbar verändert: die heutige Arbeit hat die vier Grundgrößen physikalisch
verankert (Landauer, Shannon, No-Cloning, Friis), eine echte Herleitung
produziert (`a=−S(Θ)`), das numerisch verifiziert, und mit
`resilience-core`s bereits realer Onsager-Kopplungsmatrix ein echtes
Anwendungsbeispiel im Ökosystem selbst gefunden -- der Vorwurf
"unbewiesenes Konstrukt" trifft in dieser pauschalen Form nicht mehr
zu.

**Das ändert aber NICHTS an der Gültigkeit oder Berechtigung der
2026-08-31-Entscheidung selbst.** Sie war angesichts des damaligen
Kenntnisstands richtig und umsichtig -- keine nachträgliche
Bloßstellung, keine "Aufhebung der Glaubwürdigkeit" von
`arctic-climate-utac` oder der Serie. Zwei Dinge bleiben davon
ausdrücklich unberührt:
- Grund 2 (Zugänglichkeit für Menschen außerhalb des CREP/UTAC/AFET-
  Konstrukts) ist vom Evidenzstatus des Formalismus komplett unabhängig
  -- selbst ein vollständig validierter Formalismus rechtfertigt nicht
  automatisch, echte Klimawissenschaft an ihn zu koppeln, wenn das
  Zugänglichkeit für fachfremde Leser kostet.
- Ob die Serie (oder einzelne Pakete daraus) jemals eine Bridge bekommt,
  bleibt Johanns eigene, explizite, spätere Entscheidung -- diese Notiz
  ist eine Tatsachenfeststellung zur veränderten Evidenzlage, kein
  Vorschlag, die Policy jetzt zu ändern.

## Konsequenz für ROADMAP.md

Die komplette climate/ecology-Serie (P59, P60, P87–P97, P99–P103,
P105–P121) gehört nicht in die reguläre "flächendeckende Anwendung"
(kein Code, keine Bridge an den Originalpaketen). Dritter
Enumerations-Ausgang für die Methodik bestätigt: **N/A durch bestehende
Policy**, geprüft VOR jeder Individuations-/Kopplungsanalyse, nicht danach.

**Ergänzung (2026-09-15, Johanns Vorschlag):** die Serie wird trotzdem
nicht komplett übersprungen -- eine rein exploratorische Analyse ("wie
WÜRDE der Formalismus hier aussehen, rein hypothetisch") ist weiterhin
möglich, aber ausschließlich als eigenständiges Dokument in
`crep-utac-afet-formalism/`, niemals als Änderung an
`arctic-climate-utac` selbst. Das respektiert Grund 2 der
2026-08-31-Entscheidung (Zugänglichkeit, s.o.) vollständig, während die
Serie trotzdem nicht komplett unbetrachtet bleibt.
