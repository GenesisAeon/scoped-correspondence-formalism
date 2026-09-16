# Worked Example — Rekonstruktion, Abtastung und fehlender Zustand

Revision 3, 16. September 2026. Zwei synthetische, vollständig vorgegebene Modelle. Sie erläutern die Forschungsfrage zur Beschreibungsdimension; sie sind kein empirischer Nachweis von Typ-2-Emergenz.

## 1. Ein Kreis braucht nicht zwingend drei Beobachtungskoordinaten

Zustand θ∈S¹, Dynamik θ̇=ω mit konstantem ω≠0, Beobachtung y=cos θ. Die Zustandsmannigfaltigkeit hat d=1. Eine einzelne Beobachtung unterscheidet θ und −θ nicht allgemein.

Für einen Zeitabstand τ und α=ωτ betrachte zwei vergangene Beobachtungen:

\[
D_2(\theta)=(\cos\theta,\cos(\theta-\alpha)).
\]

Die zweite Komponente lautet cosθ cosα+sinθ sinα. Falls sinα≠0, gilt daher

\[
\sin\theta=\frac{y(t-\tau)-y(t)\cos\alpha}{\sin\alpha}.
\]

Zusammen mit cosθ ist θ modulo 2π eindeutig bestimmt. Die Abbildung ist eine invertierbare lineare Transformation des eingebetteten Kreises (cosθ,sinθ). Sie ist eine glatte Einbettung in R². **Damit genügen in diesem konkreten Fall zwei Koordinaten, obwohl 2d+1=3 ist.** Das verletzt Takens' hinreichendes generisches Resultat nicht. [Theorem und Voraussetzungen](LITERATURE_CONNECTIONS.md).

Bei α=π bleiben die Paare (cosθ,−cosθ); θ und −θ fallen wieder zusammen. Beliebig viele Beobachtungen im gleichen Halbperiodenabstand beseitigen diese Mehrdeutigkeit nicht. Bei α nahe einem Vielfachen von π verstärkt die Division durch sinα Messfehler. Mathematische Injektivität und numerisch robuste Rekonstruktion sind getrennte Anforderungen.

**Prüfung:** mehrere Kreiszustände exakt rekonstruieren; θ und −θ bei α=π als Gegenfall zeigen. Der Test beweist keine generische Aussage über alle Dynamiken.

## 2. Eine Projektion kann Gedächtnis benötigen

Wir setzen dimensionslose Zustände x,y und eine feste Zeiteinheit:

\[
\dot x=-x+y,\qquad \dot y=-x-2y.
\]

Beobachtet wird nur x. Aus (x,y)=(0,1) folgt ẋ=1, aus (0,−1) dagegen ẋ=−1. Es kann deshalb keine einzige autonome Funktion ẋ=f(x) geben, die beide Zustände beschreibt.

Eliminieren von y liefert exakt

\[
\dot x(t)=-x(t)+e^{-2t}y_0
-\int_0^t e^{-2(t-s)}x(s)\,ds.
\]

Alternativ lässt sich der fehlende Zustand durch die zweite Ordnung darstellen:

\[
\ddot x+3\dot x+3x=0.
\]

Mit w=√3/2 ist

\[
x(t)=e^{-3t/2}\left[x_0\cos(wt)+\frac{x_0/2+y_0}{w}\sin(wt)\right],
\quad y(t)=\dot x(t)+x(t).
\]

Die drei Darstellungen — zweidimensionales Markov-Modell, skalare Gleichung mit Gedächtnis und Gleichung zweiter Ordnung — beschreiben hier denselben festgelegten Prozess. Die Gleichheit folgt aus der expliziten Elimination; sie ist keine schichtenübergreifende Identität von Metriken.

**Prüfung:** Die analytische Lösung wird gegen beide ODE-Komponenten per numerischer Ableitung und gegen das Gedächtnisintegral per Quadratur geprüft. Die beiden Anfangsdaten mit gleichem x bestätigen zusätzlich das Scheitern der skalaren Markov-Schließung.

## 3. Konsequenz für das Frame-Thema

Ein zusätzliches beobachtetes Merkmal kann erforderlich werden, weil eine vorherige Darstellung Zustände zusammengelegt hat. Der erste Fall betrifft Rekonstruktion und Abtastung, der zweite dynamische Geschlossenheit. Beide begründen konkrete Prüfaufgaben, ohne einen universellen Schwellenwert für die Entstehung von Dimensionen einzuführen.

Ausführung und Ergebnisse: [VERIFICATION.md](VERIFICATION.md).
