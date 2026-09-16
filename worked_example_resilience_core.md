# Anwendungsprüfung: resilience-core

Revision 2, 16. September 2026. Grundlage: ursprüngliche Analyse und am 15. September geprüfter [Quellstand](https://github.com/GenesisAeon/resilience-core/tree/60a4e69264c149921893e7110fe7e1b6b2c94453).

## Rolle des Pakets

`ResilienceCore` ist überwiegend eine Berechnungskomponente für extern gelieferte Γ-Werte. Eine Engine kann Dynamik auswerten, ohne selbst eine eigenständige Trajektorie zu erzeugen. Dieser nützliche Softwarebefund ist von einer wissenschaftlichen Individuationsaussage zu trennen.

| Berechnung | Korrigierte Einordnung |
|---|---|
| `r*tanh(sigma*Gamma)^2` | angenommene lokale Ratenform; keine hier unabhängig aus Beobachtung geschätzte Lyapunov-Rate |
| `1-Gamma/Gamma_max` | normierter Abstand zur gewählten Obergrenze; kein automatisch bestimmter Beckenabstand |
| `CouplingMatrix` | gerichtetes Einfluss-/Lastregister mit dokumentierter Vorzeichenregel |
| `coupling_factor` | gekappter Faktor aus positiver Last; kein identifizierter Onsager-Koeffizient |
| Frame-Grenze über 1/16 | bestehende spezifische Modellregel; kein unabhängiger Beweis einer universellen Schwelle |

## Kopplungsbefund präzisiert

`total_load()` summiert destabilisierende Einträge für ein Ziel; stabilisierende Beiträge werden in dieser Lastsumme ausgelassen. Diese Semantik ist eine konkrete Modellentscheidung. Eine Registry von Einflüssen liefert noch keine entropiekonjugierten Kräfte, thermodynamische Flüsse oder PSD-Bedingung. Die frühere Bezeichnung „bereits korrekt implementierte Onsager-Matrix“ wird zurückgenommen.

Dass die Last durch eine kritische Last normiert wird, ist eine strukturelle Analogie zu Auslastungsmaßen. Es bestätigt weder die M/M/1-Annahmen noch den vorgeschlagenen Frame-Score. Ein Verhältnis in [0,1] ist dafür kein ausreichender Nachweis.

## Bereits erfolgte Paketkorrekturen

Die ursprüngliche Analyse fand Diskrepanzen zwischen behaupteten Kalibrierungszielen und Default-Ausgaben: Arctic 0 statt ungefähr 0,05; Sandpile ungefähr 0,222 statt 0,75; AMOC ungefähr 0,183 bei offenem Kalibrierstatus. Diese Zahlen stammen aus der damaligen Analyse; sie wurden in dieser Revision nicht erneut ausgeführt.

Die Folgearbeit hat die Kalibrierungsbehauptungen, Tests und CI bearbeitet. Diese Korrekturen bleiben dokumentierter Fortschritt. Eine nachträgliche Parameterskalierung zum Treffen eines Zielwerts wäre als Kalibrierung zu kennzeichnen; sie wäre kein unabhängiger Test derselben Zielzahl.

## Nächste Prüfung

Für jede Rate die zugrunde liegende Dynamik angeben. Für Kopplungen zunächst klären, ob eine Zustandsentwicklung oder ein Risiko-/Lastscore gemeint ist. Ein thermodynamischer Ausbau benötigt die zusätzliche Bilanz aus [coupling_layer_afet.md](coupling_layer_afet.md). Eine allgemeine Individuation oder Selbstähnlichkeit ist mit dem aktuellen Register allein nicht nachgewiesen.

Vollständige ursprüngliche Notizen: [Archiv](archive/2026-09-15/worked_example_resilience_core.md).
