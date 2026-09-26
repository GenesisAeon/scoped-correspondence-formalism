# Yoon (2026) Source Audit — G6 Quellen-Gate

**Status:** Quellen-Gate BLOCKIERT (Stand 2026-09-26). G6 (Plan §11,
"Yoon-Reproduktion mit eigenem Quellen-Gate") darf ohne Erfüllung dieses
Dokuments nicht implementiert werden. G0–G5 und G7 sind davon unabhängig.

## Warum ein eigenes Gate

Plan §3.2: "Eine im Code selbst erfundene Formel darf nicht `yoon_2026`
heißen." Eine Pressemitteilung oder ein Abstract genügt, um zu sagen
"dieses Ergebnis wird berichtet" — nicht, um Gleichungen, Parameterfreiheit,
Fehlerrechnung oder Gültigkeitsbedingungen zu rekonstruieren.

## Bibliografischer Stand (öffentlich zugänglich, geprüft)

| Fund | Kennung | Was er belegt |
|---|---|---|
| Veröffentlichte Arbeit (laut Universitätsmitteilung) | DOI `10.1016/j.dark.2026.102462`, PII `S2212686426002499` | Titel: *A characteristic phantom-halo surface-density scale in Verlinde-inspired emergent gravity* |
| SSRN-Fassung | SSRN `7180683` | Titel: *Explanation of the constant central surface density of dark matter halos in galaxies by Verlinde's emergent gravity* — **abweichender Titel**, Versionsverhältnis zu obiger DOI ungeklärt |
| Pressemitteilung Sejong University, 23.09.2026 | phys.org, Anlassartikel Scinexx 24.09.2026 | Öffentliche Darstellung des Ergebnisses, **keine unabhängige Validierung**; nennt 20.09.2026 als Veröffentlichungstag (Nachrichtendatum ≠ Paperdatum ≠ Preprintdatum) |
| Mögliche Vorarbeit (2024) | PII `S221268642400133X`, SSRN `4781209` | *Testing Verlinde's emergent gravity with the low acceleration gravitational anomaly observed in wide binary stars* — Zusammenhang mit der 2026-Arbeit nicht bestätigt |

**Ergebnis dieser Prüfung (2026-09-26): kein Volltext beschafft.** Nur
Abstract/Pressemitteilung liegen vor. Der numerische Zielwert
(`10^(2.24±0.09) M_sun/pc^2` ≈ 173.78, siehe `galaxy_dynamics_scope.md`)
ist als berichtetes Ergebnis dokumentiert, aber nicht nachvollziehbar.

## Was für die Freigabe von G6 fehlt (Plan §11, unverändert als Checkliste)

- [ ] Exakte Version, Titel, Datum, DOI/Preprintkennung und Gleichungsnummern
- [ ] Definition der vorhergesagten Observable (tatsächliche Säulendichte,
      Burkert-äquivalentes Produkt, oder anderer Kennwert?)
- [ ] Vollständige Gleichungskette bis zum Zahlenwert, mit Regime jedes
      Näherungsschritts
- [ ] Alle Eingaben mit Dimensionen und Herkunft (kosmologische Skalen,
      Profilformen, vorher kalibrierte Beziehungen)
- [ ] Bedeutung und Herleitung von `±0.09` — Parameterstreuung,
      Näherungsfehler und Messfehler getrennt
- [ ] Vergleichsdaten und deren Unabhängigkeit von den zur Konstruktion
      verwendeten Daten
- [ ] Rolle der 2024-Vorarbeit (PII `S221268642400133X`) und die
      tatsächlich verwendete Superpositionsregel

## Vorgehen bis zur Freigabe

- G6 bleibt in `GALAXY_DYNAMICS_ROADMAP.md` als 🚫 blockiert markiert, nicht
  als übersprungen oder implizit erledigt.
- Kein Platzhalter-Adapter, der 170/173.78 zurückgibt, ohne die obige
  Checkliste zu erfüllen.
- Sobald ein Volltext (Autor-, Preprint- oder Verlagsfassung) legal verfügbar
  ist: dieses Dokument um die Checkliste ergänzen, dann erst Formeln
  implementieren und dimensionslos gegen Handrechnung prüfen.
- Zwei Ergebnisse bei Freigabe getrennt führen: **Reproduktion des
  publizierten Ergebnisses** und **zusätzlicher SCF-Test** (Plan §11) —
  eine gelungene Reproduktion ist noch keine neue Bestätigung durch
  unabhängige Daten.

## Nächste Prüfung

Diesen Audit bei nächster Gelegenheit erneut versuchen (z. B. wenn Johann
oder ein anderes Recherchewerkzeug Zugriff auf ScienceDirect/SSRN mit
vollem Volltext hat) und Datum/Ergebnis hier anhängen, statt eine neue
Datei anzulegen.
