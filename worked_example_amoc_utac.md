# Anwendungsprüfung: amoc-utac

Revision 2, 16. September 2026. Grundlage: bereitgestellte Analyse samt Nachtrag und am 15. September geprüfter [Quellstand](https://github.com/GenesisAeon/amoc-utac/tree/6b9dc57d5e864681737f61308a62048909109c4d). P18 liegt laut bereitgestellter Registry-Auswertung außerhalb der ausgeschlossenen Literaturatlas-Serie.

## Modellstruktur

`TippingPredictor` enthält eine integrierte Zustandsentwicklung; Loader und Diagnostik bereiten Daten auf, Wrapper und Gates verwenden Ergebnisse. Diese funktionale Trennung ist belegt. Die frühere Zählung „ein individuiertes System“ wird als Auswahl eines dynamischen Modellkerns geführt, nicht als ausgeführter Excess-S-Nachweis.

Nach dem bereits erfolgten Vorzeichenfix lautet die Modellgleichung

\[
\dot H=rH\left[(1-\tanh(\sigma\Gamma(t)))-H/K\right].
\]

Bei festem Γ und `h*=K*(1-tanh(sigma*Gamma))>0` ist H=h* ein stabiler Fixpunkt mit lokaler Ableitung `-r*h*/K`. Seine Erholungsrate ist also `r*(1-tanh(sigma*Gamma))`, nicht allgemein r und nicht die Steilheit einer statischen Sigmoidkurve. Bei zeitabhängigem Γ ist h*(t) eine eingefrorene Gleichgewichtsreferenz, keine ruhende tatsächliche Lösung.

## Erreichte Reparatur

Der frühere Ausdruck `K*tanh(sigma*Gamma)` führte bei wachsender Forcierung in die falsche Richtung. Changelog 1.3.3 und der geprüfte Code verwenden die abnehmende Form und zentralisieren ihren Aufruf. Das ist eine reale Verhaltenskorrektur. Die in der ursprünglichen Analyse genannten Vorher-/Nachher-Simulationswerte werden in dieser Revision nicht erneut berechnet.

## Bewusst getrennte Datenpfade

Die diagnostische Γ-Berechnung verwendet im dokumentierten Standardpfad synthetische Daten; der Prädiktor verwendet einen festgelegten Γ-Ausgangswert mit Trend. Das wurde bereits offengelegt. Die Pfade bleiben getrennt, und eine neue Verbindung wäre eine Modelländerung, keine automatisch richtige Bugreparatur.

`atanh(0.5)/2.2` ist eine inverse Parameterskalierung. Sie ist zulässig als Definition/Kalibrierung bei fixiertem σ; ihre Rücktransformation ist keine unabhängige Beobachtung. Eine Übereinstimmung mit einem anderen Paket unter identischen Eingaben belegt weder gleiche Physik noch empirische Selbstähnlichkeit.

## Geltungsbereich und nächste Prüfung

Das Modell untersucht eine gewählte Schwellenentwicklung. Ein berechnetes Schwellenjahr ist ohne belastbare Forcierung, Anfangsbedingungen, Datenabgleich und Unsicherheit keine validierte Prognose der realen AMOC. Die weiterhin dokumentierten fachlichen Quellen-/Gegenstimmen bleiben erhalten; neue Literaturprognosen werden hier nicht vorgenommen.

Selbstähnlichkeit lässt sich an der Form der normierten Dynamik und ihren Abweichungen prüfen. Dazu gehören die genaue Γ-Zuordnung, Zeitskala und die Unterscheidung zwischen einer bloßen lokalen Normalform und zusätzlicher Vorhersageleistung.

Historie und alle bisherigen Zahlen/Folgen: [Archiv](archive/2026-09-15/worked_example_amoc_utac.md).
