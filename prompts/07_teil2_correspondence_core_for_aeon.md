Auftrag: Teil 2, Milestone 1 ("Naming & Contract Freeze" + Start "Core
Extraction") des Scoped Correspondence Formalism umsetzen — NICHT den
gesamten 16-20-Wochen-Plan auf einmal, siehe Scope-Begrenzung unten.

## Kontext

D:\mandala\scoped-correspondence-formalism\ (vormals crep-utac-afet-
formalism) ist der umbenannte Formalismus — siehe GLOSSARY.md für die
vollständige Begriffszuordnung (CREP→Observation, UTAC→Dynamics,
AFET→Coupling, "Selbstähnlichkeit"→Correspondence, F08→Contextuality,
F09→Information Decomposition) und ARCHITECTURE_ROADMAP.md für den
vollständigen Zehn-Module-Plan, aus dem dieser Auftrag nur den ersten
Ausschnitt umsetzt.

Aktuell ist das Repo reine Dokumentation (FORMALISM.md und sieben
Layer-/Erweiterungsdokumente) plus fünf eigenständige, bereits
verifizierte verify_*.py-Skripte (66 grüne Prüfungen insgesamt, siehe
VERIFICATION.md/TRANSFORMATION_VERIFICATION.md). Es gibt noch KEINEN
src/-Baum, kein installierbares Python-Paket, keine echte API.

## Umfang dieses Auftrags (bewusst begrenzt)

NUR:
1. Test-ID-Namespace/Alias-Schicht für die bestehenden 66 Prüfungen
   (Provenienz erhalten, keine Neunummerierung) — siehe
   ARCHITECTURE_ROADMAP.md, Abschnitt "Migrationsprinzip für
   bestehende Tests" für das vorgeschlagene Schema (VER-CORE-*,
   VER-COR-T01…T18, VER-CTX-*, VER-PID-* usw.).
2. Ein minimaler `Correspondence`-Kern als echtes Python-Modul
   (`src/scoped_correspondence/correspondence/contract.py` o.ä.):
   Quelle, Ziel, Zustandsabbildung, Zeitabbildung, Scope, Residuum,
   Fehlermaß als typisierte Datenstruktur — siehe
   ARCHITECTURE_ROADMAP.md für die Skizze
   (`Correspondence(source, target, state_map, scope, ...)`) und
   FORMALISM.md §1 ("Selbstähnlichkeit präzise untersuchen",
   `T∘Φ_j^t ≈ Φ_k^{ct}∘T`) sowie context_transformations.md §3-5
   (T1-T4, die tatsächlichen mathematischen Beziehungen, die der
   Contract abbilden soll) als inhaltliche Grundlage.
3. Diesen Correspondence-Kern gegen mindestens drei bestehende Fälle
   aus den aktuellen Verify-Skripten verifizieren (z.B. die
   topologische-Konjugation-Fälle aus verify_extensions.py, die
   T1-T4-Fehlerfortpflanzungsfälle aus verify_transformations.py) —
   die Zahlen müssen mit den bereits etablierten Werten exakt
   übereinstimmen, das ist ein Äquivalenztest zwischen alter und
   neuer API, kein neuer Inhalt.

NICHT in diesem Auftrag: Observation/Dynamics/Coupling-Module,
Closure/Viability/Membership, GENERIC-Contracts, Lean-Beweise,
Empirical-Validation-Pipeline. Das sind spätere, separate Aufträge
nach Review dieser ersten Lieferung.

## Warum diese Reihenfolge

`Correspondence` ist laut ARCHITECTURE_ROADMAP.md die Grundlage, auf
der alle anderen neun Module aufbauen — und der Test-ID-Namespace
muss zuerst stehen, damit jede folgende Lieferung ihre Prüfungen
korrekt einordnen kann, statt am Ende alles neu zu sortieren.

## Abnahmebedingungen (Astra-Standard, unverändert seit F08/F09)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_*.py` mit reproduzierbarem JSON-Report unter `verification/`
   — reiner stdlib + numpy, wie die bestehenden fünf Skripte als Stil-
   Vorbild.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF, keine
   erfundenen Werte in Kommentaren/Dokumentation.
4. Explizites Mapping auf bestehende Begriffe (T1-T4, `Φ_j^t`,
   Konjugation/Semikonjugation aus FORMALISM.md §1) — keine parallele
   Terminologie ohne Brücke.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente — das ist reiner Software-Zusatz neben dem
   bestehenden Dokumentbestand, analog zu F08/F09.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status — diese
   Lieferung ist ein Vorschlag zur Prüfung, kein bereits akzeptiertes
   Ergebnis.

## Lieferformat

ZIP mit `apply_manifest.json` (Pfad, Aktion add/replace_after_base_check,
SHA-256, ggf. bekannte Ausgangsprüfsumme) — exakt wie bei den
vorherigen F08/F09- und Revisions-Paketen, damit Claude es sicher
gegen den aktuellen Stand einspielen kann. Neue Dateien voraussichtlich:
`src/scoped_correspondence/correspondence/contract.py`,
`docs/correspondence_core.md` (Kurzdokumentation + Mapping-Tabelle),
`verification/verify_correspondence_core.py`,
`verification/verify_correspondence_core_results.json`,
`verification/test_id_namespace.md` (die Alias-Tabelle für die 66
bestehenden Prüfungen).

Claude reviewed anschließend wie gewohnt (Checksummen, Skript selbst
nachrechnen, mindestens einen Äquivalenzfall von Hand gegenprüfen)
bevor irgendetwas als "Kern" gilt oder in README.md/GLOSSARY.md
verlinkt wird.
