# Anwendungsprüfung: scope-resilience

Revision 2, 16. September 2026. Grundlage: bereitgestellte Analyse und am 15. September geprüfter [Quellstand](https://github.com/GenesisAeon/scope-resilience/tree/61bfce858ec854ad734b701a8d3d92dbc17fa8da).

## Reale Funktionen und Evidenz

`PathDriftMonitor` sammelt Werte entlang aufeinanderfolgender Aufrufe und bestimmt eine Änderungsrate. Ein beobachteter Gesprächspfad ist damit darstellbar. Das belegt noch kein geschlossenes autonomes Zustandsmodell, keinen Lyapunov-Exponenten und keinen Excess-S-Vorteil. Beobachtung, externe Eingaben und interne Dynamik müssen getrennt werden.

Die Kennzeichnung von Proxys, Warnungen für unkalibrierte r-Werte und ein expliziter Kalibrierpfad sind sinnvolle Evidenzmechanismen. Eine inhaltsbasierte Alternative ist näher an den Textdaten; sie ist allein deshalb noch keine validierte Messung tatsächlicher semantischer Stabilität oder Halluzination.

## Fixpunktkorrektur ist erledigt

Die motivierende Gleichung `dot H=r*H*(1-H/K)*tanh(sigma*Gamma)` hat bei festem Γ mit nichtverschwindendem Vorfaktor die Fixpunkte 0 und K. `K*tanh(sigma*Gamma)` ist nicht ihr nichttrivialer Fixpunkt. Bei verschwindendem Vorfaktor ist jedes H stationär; dieser degenerierte Fall wird gesondert behandelt.

Die korrigierte Dokumentation des Pakets führt `K*tanh(sigma*Gamma)` bereits als algebraischen Referenz-/Schwellenwert. `attractor()` integriert keine ODE. Diese Änderung ist übernommen und wird nicht als weiterhin offener Fehler geführt.

## Bedeutung der Schwellenentscheidung

Der Vergleich `H_sem<H_reference` ist im Code eine Klassifikationsregel. Dass sie implementiert ist, belegt nicht automatisch eine empirisch zuverlässige Erkennung von Halluzinationen. Dafür braucht es gelabelte Aufgaben, Vergleichsverfahren, Fehlerraten und getrennte Kalibrier-/Testdaten.

Eine dynamische Kopplung mehrerer semantischer Pfade wurde im geprüften Beispiel nicht nachgewiesen. Es wird kein Onsager-L ergänzt, um ein Feld der Schnittstelle auszufüllen.

## Selbstähnlichkeit als Untersuchungsfrage

Die Struktur Beobachtung→Referenz→Regimeentscheidung kann mit anderen Schwellenmodellen verglichen werden. Eine mathematische Abbildung müsste die semantischen Variablen, ihre Zeitbasis und die Klassifikationsfunktion explizit einbeziehen. Ein ähnlicher Funktionsname reicht nicht.

Historie: [ursprüngliche Analyse](archive/2026-09-15/worked_example_scope_resilience.md). Weitere Code- oder Releaseänderungen wurden in dieser Dokumentrevision nicht vorgenommen.
