# Worked Example — Pufferfähigkeit bei fortlaufender Belastung

Revision 3, 16. September 2026. Synthetisches skalares Modell. Eine mögliche UTAC-Operationalisierung von Pufferfähigkeit; kein kalibrierter Klima- oder Biologiebefund.

## Modell und Einheiten

\[
\dot z=-r(z-z_{eq})+u-w,\qquad r>0,
\quad 0\le u\le U,\quad 0\le w\le W.
\]

z und z_eq sind Bestandsgrößen, r hat die Einheit 1/Zeit; u,w,U,W sind Bestandsraten. Der zulässige Bereich sei z≥b. u ist eine verfügbare Stabilisierungsmaßnahme, w eine Belastung. Dieser Bereich wird aus der Domänenaufgabe vorgegeben.

Die lokale Rückkehrrate bei konstanten Eingaben ist r. Sie bleibt unverändert, wenn die Belastung die Gleichgewichtslage über die zulässige Grenze verschiebt.

## Eigene Grenzrechnung

Am Rand z=b liefert die stärkste zulässige Maßnahme gegen die stärkste Belastung

\[
\dot z\big|_{b,u=U,w=W}=r(z_{eq}-b)+U-W.
\]

Ist dieser Ausdruck nichtnegativ, hält u=U den Halbraum unter jeder messbaren Belastung w(t)∈[0,W] invariant. Die Aussage folgt hier direkt aus dem skalaren Vergleich bzw. der expliziten Lösung. Allgemeine Barrierenbedingungen sind ein Literaturanschluss mit zusätzlichen Regularitätsanforderungen. [Ames et al.](https://arxiv.org/abs/1903.11199).

Für dieses Modell ist daher

\[
W_{crit}=r(z_{eq}-b)+U
\]

eine Grenze für die maximal dauerhaft abfangbare Belastungsrate des gesamten sicheren Halbraums. Negative W_crit-W bedeutet: Schon am Rand kann ein zulässiger Störer trotz maximalem u nach außen treiben. W_crit ist keine dimensionslose Wahrscheinlichkeit und kein Abstand im Zustandsraum.

## Zwei Fälle bei identischer Erholungsrate

Wähle r=1, z_eq=1, b=0, U=0 und z(0)=1, in festgelegten Bestand-/Zeiteinheiten.

| Konstante Belastung | Gleichgewicht | Verhalten |
|---|---|---|
| w=0,5 | z*=0,5 | z(t)=0,5+0,5e^(−t), bleibt zulässig |
| w=1,5 | z*=−0,5 | z(t)=−0,5+1,5e^(−t), erreicht die Grenze bei t=ln 3 und unterschreitet sie danach |

Beide Systeme haben dieselbe lineare Rate 1. Der Unterschied liegt in Belastung, Gleichgewichtslage und zulässiger Grenze. Ein guter Erholungswert allein beschreibt diese Pufferfrage nicht.

Für einen endlichen Horizont kann auch eine nicht dauerhaft abfangbare Belastung zunächst erträglich sein. Deshalb werden gemeinsam berichtet: aktueller Abstand z−b, Zeithorizont, Störungsbudget, zulässige Maßnahmen und Grenzverletzungszeit. Die bisherige Frame-Formel wird durch diese Rechnung weder hergeleitet noch kalibriert.

## Prüfung

Das Skript kontrolliert die beiden analytischen Lösungen gegen die ODE, den ersten Grenzkontakt bei ln 3 sowie die Randbedingung bei W unterhalb, gleich und oberhalb W_crit. Für reale Systeme wären Eingriffsverzögerung, Unsicherheit, Ressourcenverbrauch und Beobachtungsfehler zusätzlich zu modellieren.

Ergebnisse: [VERIFICATION.md](VERIFICATION.md).
