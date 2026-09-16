# CREP–UTAC–AFET: Information, Systeme und Kopplung

**Revision 2 · 16. September 2026 · methodischer Entwurf mit geprüften Modellrechnungen**

Johanns Ausgangsabsicht bleibt die Grundlage: CREP beschreibt Information, UTAC Systeme und deren Dynamik, AFET die Kopplung mit einer ausdrücklich ausgewiesenen thermodynamischen Spezialisierung. Die Revision ersetzt die unzutreffenden Größenidentitäten des Entwurfs vom 15. September durch definierte Schnittstellen und bedingte Modellbeziehungen.

Der gemeinsame Rahmen beschreibt, **was an einem System gemessen wird, wie es sich entwickelt und wie andere Systeme darauf wirken**. Seine Leitidee ist die von Johann am 16. September nochmals klargestellte **Selbstähnlichkeit**: wiederkehrende Strukturen mit unterschiedlichen Größen, Parametern und Skalen. Die zuvor eingeschlichenen Gleichsetzungen waren Fehler der Ausarbeitung, nicht die beabsichtigte Ausgangsthese.

Eine strukturelle Analogie ist ein Ausgangspunkt. Mathematische Selbstähnlichkeit benötigt eine angegebene Transformation und einen Geltungsbereich; empirisch geprüfte Selbstähnlichkeit zusätzlich Daten und einen quantifizierten Vergleich. Diese Ebenen werden im Formalismus ausdrücklich auseinandergehalten.

## Einstieg

| Datei | Inhalt |
|---|---|
| [FORMALISM.md](FORMALISM.md) | Zusammenhängende Übersicht und verbindliche Notation |
| [information_layer_crep.md](information_layer_crep.md) | S/K/R/V als Rollen mit expliziten Messverfahren |
| [system_layer_utac.md](system_layer_utac.md) | Zustand, Antwort, Erholung, Becken und korrigierte kubische Dynamik |
| [coupling_layer_afet.md](coupling_layer_afet.md) | Datenfluss, dynamische Kopplung und thermodynamischer Sonderfall |
| [worked_example_heat_exchange.md](worked_example_heat_exchange.md) | Vollständig gerechnetes positives Kopplungsbeispiel |
| [DESIGN.md](DESIGN.md) | Entscheidungen und zurückgezogene Schlussfolgerungen |
| [ROADMAP.md](ROADMAP.md) | Erreichter Paketstand und nächste fachliche Prüfungen |
| [FOLLOWUP_TICKETS.md](FOLLOWUP_TICKETS.md) | Offene Codefragen und bisherige Reparaturen |
| [REVISION_2026-09-16.md](REVISION_2026-09-16.md) | Änderungsliste, Grenzen und Übergabe |
| [VERIFICATION.md](VERIFICATION.md) | Reproduktion und Aussagekraft der Prüfungen |

Die acht vorhandenen `worked_example_*.md` sind auf diese Notation und den bereits erreichten Reparaturstand abgestimmt. Sie unterscheiden Modellstruktur, tatsächlichen Aufrufpfad und empirische Bewährung. Die unveränderten Ausgangsfassungen stehen im vollständigen Übergabepaket unter `archive/2026-09-15/`.

## Was die Revision festlegt

- Antwortsteilheit `beta_response` und lokale Erholungsrate `S_rec` sind getrennte Größen.
- Informationsnutzung `eta_info`, dynamischer Einfluss `A_ij` und thermodynamischer Koeffizient `L_ij` erhalten getrennte Definitionen und Einheiten.
- Die korrigierte kubische Modellfamilie lautet `tau * dx/dt = -x^3 + a*x + b`, mit dimensionslosem Zustand x und `tau>0`.
- `a = -tau*S_rec(0)` gilt nur am Gleichgewicht x=0 des symmetrischen Modells b=0. Es ist eine Modellbeziehung, keine allgemeine Parameterelimination.
- Beckenwahrscheinlichkeit, Abstand zur Grenze und lokale Rate werden gesondert gemessen.
- Positive Excess-Stabilität ist eine zu testende Eigenschaft einer gewählten Komposition, kein bereits bewiesenes allgemeines Kriterium für „System-Sein“.
- Etablierte Sätze, eigene Modellableitungen, synthetische Prüfungen und reale Messungen werden getrennt gekennzeichnet.

Die Revision bearbeitet die bereitgestellten Dokumente und neue Verifikationsbeispiele. Die erreichten Korrekturen in den veröffentlichten Einzelpaketen bleiben als Fortschritt dokumentiert. Für die hier aufgeführten weiteren Codefragen liegt noch kein Patch oder neuer Release vor.

## Ausführen

```bash
python verification/verify_formalism.py
```

Das Skript benötigt nur die Python-Standardbibliothek. Es prüft die korrigierten Modellbeziehungen, acht Gegenbeispiele zu den alten Allgemeinbehauptungen und den Dokumentverbund. Es ersetzt keine empirische Validierung und keine Paket-Testsuite.

## Status

Die Drei-Schichten-Architektur ist ein expliziter Forschungs- und Beschreibungsrahmen. Die aufgeführten Standardmodelle sind unter ihren Voraussetzungen mathematisch prüfbar. Die universelle Anwendbarkeit, ein universeller Individuationsschwellenwert und universelle Zahlenwerte wie 0,84 oder 1/16 sind dadurch nicht nachgewiesen.
