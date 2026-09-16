# Designentscheidungen — Revision 3

Stand: 16. September 2026. Aktuelle mathematische Fassung: [FORMALISM.md](FORMALISM.md).

## Ursprung und Leitidee

Johanns Absicht bleibt: die Beschaffenheit von Information, die Modellierung daraus gebildeter Systeme und die Kopplung verschiedener Systemtypen gemeinsam beschreiben. Die vier Informationsrollen Halten, Bewegen, Transformieren, Aufnehmen strukturieren die Untersuchung. **Selbstähnlichkeit über Domänen und Skalen ist die Leitidee; Gleichheit verschiedener Größen ist keine Ausgangsforderung.**

Die Revision korrigiert die eingeschlichenen Identitätsbehauptungen. Sie trennt eine strukturelle Analogie, eine mathematisch spezifizierte Strukturabbildung und empirisch geprüfte Selbstähnlichkeit. Die konkrete Prüfform steht in FORMALISM.

## Entscheidungen vom 16. September

| ID | Entscheidung | Grund und Folge |
|---|---|---|
| D01 | S/K/R/V sind Rollen mit typisierten Metrikinstanzen. | Nicht jede Domäne besitzt denselben Kanal, dieselbe Zeit oder dasselbe Stabilitätsproblem. Nicht bestimmbare Werte bleiben ausgewiesen. |
| D02 | `beta_response` und `S_rec` werden getrennt. | Gleiche Antwortkurven können verschiedene Erholungszeiten besitzen. |
| D03 | `eta_info`, `A_ij`, `L_ij` werden getrennt. | Nutzung, dynamische Wirkung und thermodynamischer Transport haben verschiedene Definitionen. Beziehungen benötigen Modelle. |
| D04 | Zustandsvariable z/x von Kontrollparameter u/R_ctrl unterscheiden. | Eine Umbenennung darf nicht gleichzeitig die Modellrolle wechseln. |
| D05 | Eine zentrierte, dimensionslose kubische Normalform mit Zeitskala τ verwenden. | Der frühere Wechsel von R³ zu (R−Θ)³ veränderte die Dynamik. |
| D06 | `a=-tau*S_rec(0)` ausschließlich bedingt angeben. | Gilt am symmetrischen Referenzgleichgewicht; keine allgemeine Parameterelimination. |
| D07 | Beckenwahrscheinlichkeit, Grenzabstand und Erholungsrate getrennt messen. | Sie reagieren unterschiedlich auf Geometrie, Koordinaten, Störungsverteilung und Zeit. |
| D08 | Excess-S ist eine Kompositionshypothese. | Kein nachgewiesenes universelles Individuations- oder Autopoiesiskriterium. |
| D09 | Thermodynamik setzt Bilanz und konjugierte Kräfte voraus. | Eine Einflussregistry oder ein gerichteter Funktionsaufruf erfüllt das nicht allein. |
| D10 | exp/tanh nur mit Modellbegründung oder transparentem Fit verwenden. | Observable-Einheit bzw. Normierung legt die Form nicht fest. |
| D11 | Eine Bifurkation nicht als neue unabhängige Dimension ausgeben. | Neue Gleichgewichte können im unveränderten Zustandsraum entstehen. |
| D12 | Referenzmaßstab und Druckgewicht der Frame-Hypothese offenführen. | Einheitenkorrektheit ist notwendig, aber keine empirische Kalibrierung. |
| D13 | Kalibrierung, Reproduktion der Kalibrierdaten und Vorhersagetest unterscheiden. | Inverse Anpassung ist zulässig; dieselben Daten sind keine unabhängige Bestätigung. |

## Revisionsgrund und Reviewstatus

Die Gegenprüfung vom 15. September identifizierte dimensionswidrige Gleichsetzungen, einen Modellwechsel in der kubischen Herleitung und zu starke Folgerungen aus Code-Abhängigkeiten. Johann lieferte am 16. September die unabhängige Bestätigung der acht Gegenbeispiele, des Formelwechsels und zweier Codebefunde zurück und beauftragte diese Überarbeitung.

Das frühere Gemini-Review bleibt ein historisches Ereignis. Die daraus gezogene Behauptung vollständiger Bestätigung wird zurückgenommen. Johann berichtet nach lokaler Einsicht, dass es die zurückgenommene Identitätsaussage positiv bewertet hatte und strukturell/namingorientiert war. Dieser übermittelte Quellenbefund wird dokumentiert; die Quelldatei wurde hier weiterhin nicht selbst eingesehen. Maßgeblich sind nachvollziehbare Herleitungen und reproduzierbare Tests, nicht die Anzahl zustimmender Modellantworten.

## Was aus der bisherigen Arbeit erhalten bleibt

Die Paketkorrekturen — Γ/κ-Refit, ehrliche Kalibrierungskennzeichnung, behobene AMOC-Richtung, Reset-/Fixpunktkorrekturen, CLI-/CI-Bereinigung, `bridge_adapted`-Kompatibilität und DESTINY+-Audit — werden nicht durch einen Fehler im Vereinheitlichungsdokument entwertet. Ihr genauer Stand ist in ROADMAP und FOLLOWUP dokumentiert.

Die Symbolumbenennung R→R_ctrl wurde zuvor lokal als umgesetzt gemeldet. Im am 15. September geprüften öffentlichen `utac-core`-Stand war sie noch nicht sichtbar. Diese Revision setzt die Dokumentnotation konsistent; sie beansprucht keine zusätzliche Paketänderung.

Die Literatur zu Autopoiesis, struktureller Kopplung, Emergenz und skalenübergreifenden Beziehungen bleibt als mögliche Begriffsquelle relevant. Die Verwendung dieser Begriffe ersetzt keine Äquivalenzherleitung zu den hier definierten Metriken.

## Historie und Rückverfolgbarkeit

Die vollständige ursprüngliche Entscheidungsfolge bleibt im Übergabepaket unter [archive/2026-09-15/DESIGN.md](archive/2026-09-15/DESIGN.md) erhalten. Sie enthält inzwischen überholte Schlussfolgerungen und beschreibt keinen aktuellen mathematischen Konsens. Die übrigen Ausgangsdateien sind dort ebenfalls unverändert archiviert. Revision 2 ist zusätzlich unter `archive/2026-09-16-revision-2/` erhalten; aktuelle Erweiterungen sind mit „Revision 3“ gekennzeichnet.

Die unveränderte ältere Reviewdatei bleibt ein eigener Prüfbericht. Ihre Hinweise werden hier umgesetzt und an Stellen präzisiert, an denen Selbstähnlichkeit, Parameteridentifikation oder thermodynamische Reziprozität eine genauere Unterscheidung verlangen.

## Entscheidungen zur Literaturerweiterung

| ID | Entscheidung | Folge |
|---|---|---|
| D14 | Art und Regularität der Strukturabbildung angeben. | Konjugation, Projektion und RG-Skalierung werden getrennt geprüft. |
| D15 | Takens als Rekonstruktionsresultat verwenden. | 2d+1 wird nicht zu einer notwendigen Typ-2-Schwelle erklärt. |
| D16 | Dynamische Geschlossenheit operationalisieren. | PC=CQ bzw. Fehler mit Zeithorizont gehört zu Markov-Makromodellen. |
| D17 | Interventionsensembles im EI-Vergleich offenlegen. | Unterschiedliche Zustandsgewichtungen werden sichtbar; kein vermeintlicher Bruch der Datenverarbeitung. |
| D18 | EI, SVD und Synergie getrennt führen. | Der Rang-eins-Gegenfall bleibt als Regressionstest erhalten. |
| D19 | Individuation als begrenzten Prüfvertrag ausarbeiten. | Kein neues unbewiesenes universelles „System genau dann, wenn …“. |
| D20 | GENERIC nur bei erfüllten Strukturbedingungen verwenden. | Im Wärmebeispiel abgeleitet; keine automatische Übertragung auf übrige Pakete. |
| D21 | Belastbarkeit mit zulässigen Bereichen und Störungsbudgets ergänzen. | Rückkehrrate, Abstand und dauerhafte Belastungsgrenze bleiben getrennt. |
| D22 | Lokale Zusatzdateien und spätere Bearbeitungen bewahren. | Ergänzungspaket mit Änderungeninventar; kein Git-Init, kein Löschabgleich. |

Die 2025er Arbeiten sind konkrete Forschungsanschlüsse, keine pauschalen Bestätigungen des Rahmens. Das unvoreingenommene Prüfen ihrer Grenzfälle gehört zur gleichen Arbeitsweise wie die Korrektur der eigenen Dokumente.
