# Anwendungsprüfung: afet-tensions

Revision 2, 16. September 2026. Grundlage: bereitgestelltes Worked Example, Folgearbeiten und der im Review vom 15. September geprüfte [Quellstand](https://github.com/GenesisAeon/afet-tensions/tree/1fa06907f8953212fc5a468feddce293f39b9394). Keine erneute Ausführung der Paket-Testsuite in dieser Revision.

## Komponenten und tatsächliche Beziehungen

`BetaHierarchyModel` ist eine algebraische Antwort-/Umrechnungsfunktion. `CREPRedshiftEvolution` integriert ein Modell für Γ(z). Hubble-, S₈-, LIGO-, Euclid- und DESI-Klassen verwenden oder präsentieren daraus abgeleitete Größen. Daraus folgt eine nachvollziehbare Softwarestruktur; die frühere wissenschaftliche Zählung „genau zwei individuierte Systeme“ ist ohne definierten Excess-S-Vergleich nicht belegt.

In `DESIPrediction.h0_bao()` moduliert `Gamma(z)/Gamma(0)` den effektiven β-Eingang. Der Rückweg β→Γ ist in diesem geprüften Pfad nicht implementiert. Das ist eine gerichtete algebraische Abhängigkeit. Ein thermodynamischer Fluss, seine konjugierte Kraft und eine Entropiebilanz sind dort nicht identifiziert; `L_BA` oder eine Verletzung von Reziprozität werden deshalb daraus nicht abgeleitet.

## Dynamik und Zeit

Die Gleichung `dGamma/dz=kappa*Gamma*(1-Gamma)` verwendet Rotverschiebung als unabhängige Variable. Im expandierenden FLRW-Modell gilt `dz/dt=-(1+z)H(z)`. Stabilität entlang zunehmender z ist daher nicht ohne Umrechnung Stabilität in kosmischer Zeit. Eine positive κ alleine ist kein universeller zeitlicher Stabilitätswert.

## Bereits behoben und weiter offen

Der neue Fit verwendet `GAMMA_DOMAIN=0.6403419953108261` und κ≈0.0004226902943. Er ersetzt den früheren algebraischen Zwei-Punkt-Ansatz; der Fit-Schritt ist nicht mehr offen. Die fünf H₀-Messungen und drei Weak-Lensing-Messungen sind Kalibrierdaten, keine dadurch unabhängigen Testdaten. Voraussetzungen der β-Zuordnung, Kovarianzen, Anker und Unsicherheitsfortpflanzung bleiben explizit zu prüfen.

`beta_from_h0(h0_local())` gibt wieder den eingesetzten β-Wert zurück. Das ist ein redundanter Rundtrip, für sich kein ungültiger Fit. Zirkulär wäre seine Präsentation als unabhängige Bestätigung.

Die exp/tanh-Ansätze bleiben phänomenologische Modellformen. Die frühere Herleitung aus „unbeschränkte Rate“ bzw. „normierte Amplitude“ ist zurückgenommen. S₈ ist nicht definitionsgemäß auf [0,1] begrenzt.

## Aussage zur Selbstähnlichkeit

Die beobachtbare Abfolge Zustand/Parameter→Antwort→abgeleitete Ausgabe kann mit anderen Paketen strukturell verglichen werden. Eine mathematische oder empirische Selbstähnlichkeit benötigt eine konkrete Transformation und unabhängige Prüfung. Insbesondere wird Γ nicht allein aufgrund dieser Struktur zu einem Onsager-Koeffizienten.

Historische Details und ursprüngliche Aussagen: [Ausgangsfassung](archive/2026-09-15/worked_example_afet_tensions.md). Aktuelle Definitionen: [FORMALISM.md](FORMALISM.md).
