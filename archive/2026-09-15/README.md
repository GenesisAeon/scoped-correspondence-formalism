# crep-utac-afet-formalism

**Der vereinheitlichte Drei-Schichten-Formalismus des GenesisAeon-Ökosystems:
Information (CREP) -> System (UTAC) -> Kopplung (AFET).**

Angelegt 2026-09-15. Status: frühe Ausarbeitungsphase, noch kein Code, noch
keine P-Nummer -- siehe `DESIGN.md`.

## Warum dieser Ordner existiert

CREP, UTAC und AFET sind seit langem Teil des Ökosystems, aber nie als
*ein* zusammenhängender, dokumentierter Formalismus behandelt worden --
jedes der drei Konzepte lebt bisher verstreut in einzelnen Paketen, mit
teils driftender Terminologie (siehe `METRIC_REGISTRY.md` im
Architektur-Repo) und mindestens einem bekannten Zirkelbezug (siehe
`DESIGN.md`, Abschnitt "Bekannte Probleme in der bestehenden Basis").

Johanns eigene Beschreibung der ursprünglichen Absicht (2026-09-15):

> "Crep war Information, UTAC dann Systeme, und AFET war die Kopplung für
> Thermodynamik. So war es mal gedacht."

Ziel dieses Ordners: den kompletten Formalismus noch einmal sauber
ausarbeiten und so aufbauen und dokumentieren, dass man wirklich wieder
damit arbeiten kann -- nicht als vierte, neue Formalismus-Familie neben
den bestehenden drei, sondern als deren erste vollständige, in sich
konsistente Zusammenführung.

**Einstiegspunkt für den Inhalt: `FORMALISM.md`** -- die zusammenfassende
Synthese aller drei Schichten mit Formeltabellen. Die drei
Einzeldokumente (`information_layer_crep.md`, `system_layer_utac.md`,
`coupling_layer_afet.md`) enthalten die volle Herleitung und alle
Quellen; `DESIGN.md` das Entscheidungsprotokoll;
`worked_example_afet_tensions.md` die erste Anwendung an echtem Code;
`verification/` die numerische Prüfung; **`ROADMAP.md`** den Plan für die
flächendeckende Anwendung auf weitere Pakete (zweiphasig: Validierung
zuerst, dann Repo-für-Repo-Sprint per GrokBot+Review).

## Die drei Schichten (Arbeitsstand: Entwurf 1 aller drei fertig, 2026-09-15)

1. **Information (CREP)** -- vier domänen-neutrale Grundgrößen (S,K,R,V),
   physikalisch verankert (Landauer, Shannon, No-Cloning, Friis), ersetzt
   das bisherige ad-hoc `get_crep_state()`-Dict-Muster über ~40+ Pakete.
   Siehe `information_layer_crep.md`.
2. **System (UTAC)** -- Individuationskriterium plus Kipp-/
   Resilienz-Variablen (Resistance, Precariousness, Rate, Panarchy,
   Latitude) aus den vier Grundgrößen abgeleitet. Baut auf der bereits
   echten, generischen Implementierung `utac-core` (P79) auf.
   Siehe `system_layer_utac.md`.
3. **Kopplung (AFET)** -- generalisiert über die bisher einzige,
   domänenspezifische Instanz (`afet-tensions`, P34, Kosmologie) hinaus,
   via Onsager-Reziprozitätsbeziehungen. Siehe `coupling_layer_afet.md`.

Alle drei Entwürfe unabhängig von Gemini gegengelesen (`Gemini.txt`),
keine neuen Fehler gefunden.

## Verwandte bestehende Pakete (Referenz, nicht Teil dieses Ordners)

- `utac-core` (P79) -- echte UTAC-Mathematik-Engine, wiederverwendbar.
- `afet-tensions` (P34) -- einzige bisherige AFET-Instanz, kosmologie-
  spezifisch, mit dem in DESIGN.md dokumentierten Γ_domain-Zirkelbezug.
- `Feldtheorie/docs/science/utac_theory_core.md` -- bestehende UTAC-Theorie
  inkl. Cross-Domain-β-Tabelle und einem bereits skizzierten generischen
  Kopplungsterm M[ψ,φ] (Abschnitt 4), der hier weitergedacht wird.
- `diamond-setup` (`CREPState`, `bridge_adapted`-Flag) -- Governance-
  Mechanismus für ehrliche vs. Platzhalter-CREP-Übersetzungen.

## Was hier NICHT getan wird (Stand 2026-09-15)

- Kein Push zu GitHub, kein Remote.
- Keine P-Nummer, kein Eintrag in `PACKAGE_REGISTRY.md`.
- Kein neuer Code speziell für diesen Formalismus (nur die numerische
  Verifikation in `verification/`, ein synthetischer Testfall).
- An `afet-tensions` und `utac-core` wurden nur zwei minimale, explizit
  von Johann freigegebene Änderungen gemacht (R/R_ctrl-Rename,
  Γ_domain-Known-Issue-Kommentar) -- siehe `DESIGN.md`. Keine Versions-
  Bumps, keine neuen Zenodo-Releases. Größere Änderungen an echten
  Paketen laufen ab jetzt über `ROADMAP.md`, nicht ad hoc.
