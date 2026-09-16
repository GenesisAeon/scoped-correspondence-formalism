# Anwendungsprüfung: solar-flare-utac

Revision 2, 16. September 2026. Grundlage: bereitgestelltes Beispiel mit Nachtrag und am 15. September geprüfter [Quellstand](https://github.com/GenesisAeon/solar-flare-utac/tree/86ed000c70be276ba4352cc61105d5c423cd330f).

## Dynamik und Ereignisse

`MagneticActiveRegion` enthält kontinuierlichen Aufbau, Störung und einen Schwellen-/Resetmechanismus. Bei festem quiet-λ lautet das glatte Teilmodell `dot H=r_buildup*(1-H)-lambda_quiet*H`. Sein Fixpunkt ist `r_buildup/(r_buildup+lambda_quiet)`; seine Kontraktionsrate ist `r_buildup+lambda_quiet`.

Mit den dokumentierten Parametern ergeben sich ungefähr 0,923 und 0,065 pro Stunde. Der früher als Fixpunkt bezeichnete Wert 0,10 ist ein Reset-Wert. Die Paketdokumentation hat diese Unterscheidung bereits korrigiert.

Die Rate des glatten Teilmodells ist nicht automatisch der größte Lyapunov-Exponent des vollständigen verrauschten Reset-Prozesses. Die Störungsentwicklung muss auch Ereigniszeitpunkte und Reset-Abbildung berücksichtigen.

## Geomagnetische Auswertung: Aufrufpfad präzisiert

`GeomagneticStorm` stellt eine Peak-Vorhersage, einen gespeicherten Peakzustand sowie Methoden für exponentielle Erholung und ein synthetisches Sturmprofil bereit. Im geprüften `run_cycle()` wird bei einem Flare `predict_dst()` aufgerufen und der Spitzenwert protokolliert. `dst_recovery()` und `simulate_storm_profile()` laufen in diesem Pfad nicht als zweite kontinuierlich fortgeschriebene Dynamik mit.

Damit ist eine gerichtete Ereignis-/Datenabhängigkeit von Flare-Energie zu Dst-Peak belegt. Die frühere Aussage einer zweiten gleichzeitig mitlaufenden Relaxation ist zu weitgehend. Der zugehörige Faktor ist kein identifizierter Onsager-Koeffizient. Außerdem enthält die Peak-Berechnung Clipping; eine lineare/multiplikative Beziehung gilt höchstens innerhalb des ungesättigten Bereichs bei festgehaltenen anderen Parametern.

Eine exponentielle Erholung in der Zeit belegt auch keine allgemeine Regel für exponentielle statische Antwortfunktionen. Beide mathematischen Rollen werden getrennt.

## Erreichte Korrekturen und verbleibende Lücke

Changelog 1.0.1 dokumentiert den behobenen Rundungsfehler beim Γ-Check, die richtige Reset-Bezeichnung und die Kennzeichnung von Konstruktions-/Selbstkonsistenzprüfungen. Die etwa 20-fache Abweichung beim Rekonnexions-Zeitskalenbenchmark wurde bewusst offen gelassen; ohne unabhängige Daten würde das Erzwingen des Zielwertes keine Validierung schaffen.

Die alten Zahlen und Testberichte stammen aus der ursprünglichen Arbeit; die Paket-Testsuite wird in dieser Revision nicht erneut ausgeführt. Der frühere Stand „Trusted Publishing wartet“ ist durch die später bereitgestellten Follow-up-Notizen überholt; deren Erfolgsmeldung bleibt erhalten, wird hier aber nicht erneut als eigener Veröffentlichungscheck ausgegeben.

## Resilienz und Selbstähnlichkeit

Ein Abstand zur Eruptionsschwelle kann als konkrete Precariousness-Metrik definiert werden. Ein Reset-Ereignis ist nicht automatisch ein Attraktorwechsel und nicht automatisch Rate-Tipping. Basin-/Überlebensfragen können auch ohne zwei stationäre Becken sinnvoll sein, benötigen aber ein Zielereignis, eine Störungsverteilung und einen Zeithorizont.

Das Aufbau-Schwelle-Reset-Muster bietet eine strukturelle Selbstähnlichkeitsfrage zu anderen Ereignismodellen. Ein Nachweis braucht eine explizite Abbildung der Dynamik und Ereignisse; die Zahl der Softwareklassen oder eine gerichtete Kante liefert ihn nicht.

Ursprüngliche Analyse und historische Benchmark-Tabelle: [Archiv](archive/2026-09-15/worked_example_solar_flare_utac.md).
