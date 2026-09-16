# Anwendungsprüfung: cygnus-jet-utac

Revision 2, 16. September 2026. Grundlage: bereitgestelltes Beispiel mit Nachtrag und am 15. September geprüfter [Quellstand](https://github.com/GenesisAeon/cygnus-jet-utac/tree/f7372d6fa6a52938777156e251973f805a7bff7e).

## Dynamische und algebraische Teile

Der geprüfte Fallback-Integrator verwendet `dot H=r*H*(1-H/H*)`, `H*=K*tanh(sigma*Gamma)`, mit RK4-Schritten. Für konstantes Γ und H*>0 ist die lokale kontinuierliche Ableitung am Fixpunkt `-r`. Die Antwortfunktion H*(Γ) und die Erholungsrate sind verschiedene Größen. Bei variierendem Γ sowie mit Rauschen oder Clipping ist diese lokale Aussage nicht ungeprüft auf den gesamten Prozess übertragbar.

Eine analytisch ausgewertete Umlaufphase beschreibt ebenfalls eine Dynamik. Ein getriebener/diffusiver Jet-Zustand bleibt ein dynamischer Modellteil, auch wenn er keine autonome Rückstellkraft besitzt. Die frühere pauschale Einstufung dieser Teile als „keine Systeme“ wird daher durch konkrete Rollenbeschreibungen ersetzt. Ein Excess-S-Kriterium wurde für die Komposition nicht berechnet.

## Abhängigkeiten

Orbital-, Wind-, CREP-, H- und Jet-Berechnungen enthalten tatsächliche gerichtete Datenabhängigkeiten. Der ungenutzte Parameter `jet_pos` im dokumentierten Windpfad begründet keine Rückwirkung; nach dem ursprünglichen Bericht ist die Verwendung des Ansatzpunktes beabsichtigt. Der Datenfluss sollte als solcher beschrieben werden, einschließlich einer eventuell vorhandenen Rückführung über H-abhängige Γ-Komponenten. Er wird nicht pauschal als lineare Kette oder Onsager-Matrix ausgegeben.

## Bereits umgesetzte Einordnung

Γ_jet wird aus einem eingesetzten Wirkungsgrad bei festgelegtem σ invers berechnet. Die Rückgewinnung des Wirkungsgrades prüft die Umrechnung. Eingabe-Echos, auf Zielwerte skalierte Ausgaben und auf einen Ereigniszählwert angepasste Rauschparameter sind keine sechs unabhängigen Vorhersagetests.

Die Folgearbeit hat diese Einschränkungen bereits dokumentiert und die Behauptung einer unabhängigen CREP-Domänenbestätigung korrigiert; Changelog 1.0.2. Die Zahlenwerte wurden dabei nicht willkürlich ersetzt. Das ist eine abgeschlossene Kennzeichnungskorrektur.

## Selbstähnlichkeitsfrage

Die lokale Relaxationsform lässt sich mit anderen Modellen vergleichen. Die Normierung muss ausdrücklich angegeben werden; gemeinsame Parameterwerte aus einem Ökosystem-Default liefern keinen zusätzlichen Nachweis. Für eine astrophysikalische Bewährung braucht es unabhängige Daten und Vorhersagen, die nicht schon die Eingaben des Modells sind.

Die mathematische Modellstruktur bleibt nutzbar. Eine thermodynamische Identifikation erfordert zusätzlich Flüsse, Kräfte und eine Bilanz. Ausführliche ursprüngliche Auflistung der Komponenten und Benchmarks: [Archiv](archive/2026-09-15/worked_example_cygnus_jet_utac.md).
