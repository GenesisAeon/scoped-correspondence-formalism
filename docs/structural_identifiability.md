# Strukturelle Identifizierbarkeit mit präzisem Umfang (J6)

Paket J6 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §12. Code: `src/scoped_correspondence/identifiability/exact_linear.py`,
`.../structural_reports.py`. Prüfung:
`verification/verify_structural_identifiability.py` (math). Die
bestehenden Module `identifiability/core.py`, `fim_sloppiness.py` und
`profile_likelihood*.py` bleiben unverändert und getrennt. Lizenz der
Dokumentation: CC BY 4.0.

## 1. Pflichtkern: exakte affine Beobachtungen

Für $z=A\theta+b$ mit rationaler Matrix $A$ gilt auf dem unbeschränkten
Parameterraum $\mathbb R^p$:

- Die Beobachtungsfaser von $z$ ist der affine Raum
  $\{\theta_0+Nt\}$ ($\theta_0$ eine partikuläre Lösung, $N$ eine
  Nullraumbasis) — oder **leer**, wenn $z$ nicht im Bild liegt. Eine
  leere Faser ist ein Modell-Daten-Widerspruch, kein
  Identifikationsergebnis.
- Eine Linearkombination $c^\top\theta$ ist genau dann eindeutig
  bestimmt, wenn $c$ im Zeilenraum von $A$ liegt
  (`is_identifiable_combination`).

`analyze_affine_identifiability(A, b, observation, parameter_domain)`
liefert Rang, Nullraumbasis, die Aussage auf $\mathbb R^p$ und — getrennt
davon — die Wirkung eines **deklarierten** Parameterbereichs: Für eine
rationale Box und einen eindimensionalen Nullraum wird die Faser auf der
Box exakt als Strecke berechnet; bleibt nur ein Punkt, heißt das
„identifiziert **auf diesem Bereich**“, die Aussage auf $\mathbb R^p$
bleibt unverändert. Bei höherdimensionalem Nullraum wird die
Einschränkung als `not_evaluated` ausgewiesen (dafür wäre LP nötig) und
nie stillschweigend angenommen. Die exakte lineare Algebra stammt aus
`dimensions.pi_groups` (J2), nicht aus einer Kopie.

**J-C11:** $A=\begin{pmatrix}1&1\\2&2\end{pmatrix}$: Rang 1, Nullraum
$\operatorname{span}(1,-1)$; die Summe ist identifizierbar, die
Aufteilung nicht. $z=(3,6)$: Faser $(3,0)+t(1,-1)$; $z=(3,7)$: leer.

## 2. Analytische Kontrollfamilien

**J-C12 (Reservoir):** $\dot x=-kx$, $y=cx$, $k,c,x_0>0$, ideale
kontinuierliche Beobachtung. $y(0)=cx_0$, $\dot y(0)=-kcx_0$, also
$k=-\dot y(0)/y(0)$ und das Produkt $cx_0$ identifizierbar; $c$ und
$x_0$ einzeln nicht, Zeuge $(c,x_0)\mapsto(c/\lambda,\lambda x_0)$. Mit
$k=2$, $c=3$, $x_0=5$: $15$ und $-30$; $\lambda=7$ ergibt $(3/7,\,35)$.
Ist $c$ bekannt, wird $x_0$ identifizierbar; ist die
**Anfangsbedingung** $x_0$ bekannt, wird $c$ identifizierbar. Die
Positivitätsannahme schließt das Nullsignal bewusst aus. Gegenprobe:
In Log-Koordinaten ist $\log y(0)=\log c+\log x_0$ exakt affin mit
$A=(1\ 1)$ — Rang 1, Summe identifizierbar, Aufteilung nicht.

**J-C13 (diskrete Mehrdeutigkeit):** $y=\theta^2$ bei $y=4$: Faser auf
$\mathbb R$ ist $\{-2,2\}$. An $\theta=2$ ist die Ableitung $4\ne0$:
**lokal** eindeutig, **global** auf $\mathbb R$ nicht; auf $\theta>0$
bleibt nur $2$.

## 3. Was getrennt bleibt

| Ergebnisart | Wo | Bedeutung |
|---|---|---|
| strukturell, exakt affin | `exact_linear` | Beweis auf $\mathbb R^p$ bzw. auf einem deklarierten Bereich |
| strukturell, analytisch | `structural_reports` | dokumentierte Herleitung für eine benannte Modellfamilie, Zeugen exakt geprüft |
| endliche Kandidatenfaser | `finite_candidate_fibre` (nutzt `epistemic.observation_fibers`) | gilt nur für die **aufgelisteten** Kandidaten, nie für alle reellen Parameter |
| numerischer Jacobi-Rang | `identifiability/core.py` | lokal; ein voller Rang zertifiziert **keine** globale Eindeutigkeit ($\theta^2$ an $\theta=2$: Rang 1, global trotzdem nicht identifizierbar) |
| Fisher-Information, Profil-Likelihood | bestehende Module | praktische Identifizierbarkeit aus Daten; ein breites Profil beweist keine strukturelle Nichtidentifizierbarkeit |

Außerhalb des implementierten Umfangs (allgemeine nichtlineare oder
rationale ODE-Modelle) lautet das Ergebnis ausdrücklich `unsupported` —
weder „identifizierbar“ noch „nicht identifizierbar“. Ein optionaler
Adapter an SIAN bzw. StructuralIdentifiability.jl müsste deren
lokale/globale/generische Aussageklassen und Wahrscheinlichkeitsparameter
erhalten; eine algorithmische Erfolgswahrscheinlichkeit ist kein
Konfidenzniveau für Messdaten (Plan §12, §22).

Anschluss an Bestehendes: Das Skalierungsbeispiel
`parameter_scaling_invariance` ($\sigma\gamma$ identifizierbar) stimmt
mit der exakten Log-affinen Analyse überein.

## 4. Quellen

S09 Hong, Ovchinnikov, Pogudin & Yap (2019), SIAN; S10 SciML
StructuralIdentifiability.jl — Links siehe Plan §21; keine Abhängigkeit
im Pflichtkern.
