Auftrag: Teil 2, Milestone 23 ("Fisher-Information-Sloppiness") —
natürliche Erweiterung von `identifiability`, aus der `.docx`-Recherche
(Transtrum, Machta & Sethna 2011, DOI 10.1103/PhysRevE.83.036701; Raju
et al. 2018, Phys. Rev. E 98, 052112, beide von Claude gegen die
Quellen geprüft).

## Kontext

`identifiability` hat bereits SVD/Konditionierungs-Diagnostik
(`svd_emergence_vs_ei`), `parameter_scaling_invariance`/
`identifiability_jacobian_rank` (M5) und `profile_likelihood` (M20,
gemergt). Transtrum/Machta/Sethna liefern die informationsgeometrische
Vertiefung: für eine Modellfunktion `f(θ)` mit Messvarianz `σ²`
definiert die Fisher-Informationsmatrix (FIM) das lokale
Bogenlängenelement

\[
g_{ij}=\frac1{\sigma^2}\sum_k\frac{\partial f_k}{\partial\theta_i}\frac{\partial f_k}{\partial\theta_j}.
\]

Komplexe dynamische Modelle zeigen typischerweise einen EXPONENTIELLEN
Abfall der FIM-Eigenwerte ("Sloppiness") — steile Eigenvektoren
("stiff", präzise identifizierbar) vs. flache Eigenvektoren ("sloppy",
trotz vieler Daten unidentifizierbar).

## Umfang dieses Auftrags

### 1. `identifiability.fim_sloppiness.fisher_information_matrix(jacobian, sigma)`

Berechnet `g = J^T @ J / sigma**2` für eine gegebene Jacobi-Matrix
`J = ∂f_k/∂θ_i` (Zeilen = Messpunkte, Spalten = Parameter).

### 2. `identifiability.fim_sloppiness.eigenspectrum_report(g)`

Eigenwerte/Eigenvektoren der FIM, sortiert absteigend, mit
Anisotropie-Verhältnis `λ_max/λ_min`.

### 3. Durchgerechnetes Beispiel (bereits von Claude bestätigt — von
### Hand nachrechenbares Zwei-Parameter-Modell)

Ein einfaches, algebraisch durchgerechnetes Modell mit ZWEI
Messzeitpunkten und zwei Parametern (z.B. `f(θ1,θ2,t)=θ1·e^{-θ2·t}` bei
zwei `t`-Werten) — Docstring MUSS die exakte Jacobi-Matrix und
resultierende FIM per Hand herleitbar angeben. Zeige:
- Einen "stiff" Eigenvektor mit großem Eigenwert (sensible
  Parameterkombination).
- Einen "sloppy" Eigenvektor mit kleinem Eigenwert (unempfindliche
  Parameterkombination).
- Konkretes Anisotropie-Verhältnis aus dem Skriptlauf.

### 4. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `identifiability/core.py` oder
  `identifiability/profile_likelihood.py` — eigenes, separates Modul.
- Keine Gleichsetzung mit `identifiability_jacobian_rank` (M5) als
  gemeinsame Formel — beide bleiben komplementäre, aber unterschiedliche
  Diagnosen (Rang-Kollinearität vs. FIM-Spektral-Anisotropie).
- Kein allgemeines ODE-Modell — nur die algebraisch geschlossene
  Zwei-Parameter-Demonstration.

## Verifikation

`verify_fim_sloppiness_core.py`: (1) FIM exakt aus der gegebenen
Jacobi-Matrix reproduziert, (2) Eigenwerte/-vektoren mit konkretem
Anisotropie-Verhältnis aus dem Skriptlauf, (3) mindestens ein
Kontrollfall mit ISOTROPER FIM (z.B. Identitätsmatrix) zur Gegenprobe
— Anisotropie-Verhältnis muss dort `1` sein.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_fim_sloppiness_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Transtrum et al. 2011 / Raju et al. 2018 und
   `identifiability/core.py`s bestehende SVD-Diagnostik (nur als
   Kontext, keine gemeinsame Formel).
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m23-fisher-sloppiness` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 21 (`closure`), 22 (`observation`) und 24
(`contextuality`) bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
