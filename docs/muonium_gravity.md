# Myonium-Gravitation: Messmodell, Identifizierbarkeit und Design (MU1–MU7)

Teil von [`MUONIUM_GRAVITY_ROADMAP.md`](../MUONIUM_GRAVITY_ROADMAP.md);
Quellen: [`muonium_source_audit.md`](muonium_source_audit.md). Code:
`src/scoped_correspondence/muonium/`, CLI `scripts/run_muonium_pilot.py`.
Lizenz der Dokumentation: CC BY 4.0.

**Leitfrage:** Unter welchen Annahmen kann eine beobachtete
Zählratenmodulation einer effektiven Beschleunigung zugeordnet werden —
und welche Störgrößen erzeugen dieselben Beobachtungen? Ein Ergebnis kann
ebenso eine nachgewiesene Nichtidentifizierbarkeit sein wie eine Schätzung.
**Nichts hier ist eine Messung der Myonium-Gravitation.**

## MU1 — Kinematik und Geltungsbereich (`kinematics.py`)

Drei äquidistante Ebenen bei $0,T,2T$, $T=L/v$, konstante transversale
Beschleunigung $a$ entlang einer deklarierten Achse (positiv zur lokalen
Referenz $g_{\rm ref}>0$):

- relative Verschiebung $z(2T)-2z(T)+z(0)=aT^2$ (exakt; eliminiert $z_0$, $u_0$),
- Einzelbahnabsenkung $aT^2/2$ — eine **andere** Größe,
- Phase $\phi_g=K(v)a$, $K=2\pi L^2/(dv^2)=2\pi T^2/d$ (dimensionslos, mit J2 geprüft),
- Gitterkombination $h=G_3-2G_2+G_1$ → Phasenoffset $-2\pi h/d$,
- Überleben $e^{-2L/(v\tau)}$ (optional $\tau\to\gamma\tau$),
- $\delta_g=(a-g_{\rm ref})/g_{\rm ref}$, $\eta=2\delta/(2+\delta)$; η ist
  bei $a=-g_{\rm ref}$ **undefiniert** (`None`), nie eine erfundene Zahl.

Abgelehnt: ungleiche Flugzeiten, ungültige Geometrie, nicht endliche
Eingaben. Negative $a$ sind zulässig (keine Positivitätsannahme).

## MU2 — Geschwindigkeitsmischung und Messoperator (`forward.py`)

Endliche Flussmischung lebender Atome an Ebene 1 mit Gewichten (Summe 1),
Transmission $A$, Effizienz $\varepsilon$, Kontrast $C$ (mit
$A(1+C)\le1$ für eine Wahrscheinlichkeit — **ohne** Voreinstellung, weil
$A=C=1$ die Bedingung verletzen würde). Komplexer Kontrast
$F=\sum q A\varepsilon S C e^{i\phi}/W$ und
$\lambda_j=t_jb+t_jRW\{1+\mathrm{Re}(e^{i\alpha_j}F)\}$ mit **eigener**
Messzeit je Bin. $W=0$: kein Signal; $F=0$: Phase undefiniert (kein
`arg(0)`). Die Phase bei mittlerer Geschwindigkeit ersetzt die Summe nicht
($E[1/v^2]\ne1/E[v]^2$). Die **detektierte** Mischung unterscheidet sich
von der einfallenden (langsame Atome zerfallen häufiger).

## MU3 — Likelihood und Schätzdiagnostik (`likelihood.py`)

Poisson-NLL mit exakten Grenzfällen (NLL(0;0)=0, NLL(n>0;0)=∞, keine
künstliche Untergrenze), Deviance mit Nullterm $2\lambda$ und
vorzeichenbehafteten Wurzelresiduen. Nur rohe ganzzahlige Zählungen.
`multistart_fit` kapselt additiv einen beschränkten Mehrfachstart-
Optimierer und berichtet jeden Lauf (Konvergenz, Zielwert, Randtreffer,
Fehlschläge) sowie **alle** Moden im Suchbereich; lokale Konvergenz ist
keine globale Optimalität. Bei weitem Suchbereich erscheinen die
periodischen Aliase im Abstand $d/T^2$ als gleichwertige Moden.

## MU4 — Identifizierbarkeit (`identifiability.py`, nutzt J6)

Die acht Gegenbeispiele aus Plan §7, mit dem J6-Baustein exakt analysiert:
(1) eine Flugzeit + freier Offset: $(a,\phi_0)\to(a+c,\phi_0-Kc)$, auch auf
Zählebene; (2) zwei Flugzeiten $u=(1,4)$: lokal trennbar ($p=(3,6)\Rightarrow
A=1,b=2$) unter gemeinsamem Offset und korrekter Kalibrierung; (3)
Periodizität $a\to a+d/T^2$, bei $K_2=4K_1$ gemeinsame Aliase — voller
Rang des entfalteten linearen Modells ist **keine** globale Eindeutigkeit
des periodischen Zählmodells; (4) beschleunigungsähnliche Störung: Rang 2
für drei Parameter, egal wie viele Flugzeiten; (5) Umkehr: gerade Offsets
fallen heraus, ungerade bleiben mit der Gravitation verbunden
(Paritätstabelle; keine Aussage „Umkehr beweist Gravitation“); (6)
$a_{\rm fit}/a_{\rm true}=(1+e)^2$; (7) Gegenphasen ohne Kontrast; (8)
Fit mit einfallender statt detektierter Mischung ist verzerrt. Eine
endliche Kandidatenfaser gilt nur für die gelisteten Kandidaten.

## MU5 — Design und bedingte Abdeckung (`design.py`)

$I_\phi$ für Phasenscans; ideale Quadratur $I_a=NC^2K^2$ ⇒ lokale Grenze
$\sigma_a\ge1/(C\sqrt NK)$; Vierphasenscan $NC^2/2$ (8 vs. 16 bei
$N=400$, $C=0{,}2$); ≈ $5{,}73\cdot10^8$ detektierte Ereignisse für
$\sigma_a/g=1\,\%$ unter Idealannahmen. Gemeinsame Informationsmatrix für
Nuisance-Parameter; **singulär wird als singulär gemeldet**, keine
Pseudoinverse. Budgets werden benannt: bei festem *einfallendem* Budget
$T_{\rm opt}=2\tau$, bei festen *detektierten* Ereignissen gibt es keine
Zerfallskosten. Vorab festgelegte Abdeckungsstudie (Seed 11): korrektes
Modell ≈ 95 % im Rahmen der Binomialunsicherheit; weggelassener Offset →
Abdeckung bricht ein (dokumentiertes Negativergebnis); nicht
identifizierbarer gemeinsamer Fit → jedes Intervall reicht an die
Suchgrenzen. 3,84 ist nur eine asymptotische Referenz.

## MU6 — Evidenz und Realdaten (`evidence.py`)

Übersetzung in die bestehenden Vokabulare (synthetisch →
`numerical_sample`/`synthetic_only`, analytisch → `analytic_argument`,
endlich → `exhaustive_finite`) und ein Feld `record_kind`, das reale
Quelle, synthetische Messung und Zukunftsprognose trennt. Eine
Quellen-Metadaten-Angabe kann keinen Gravitationswert tragen.
Standard-JSON (nicht endliche Werte als Statusmarker). Der
Realdatenzweig ist `deferred`: Die Datenreferenz der Quellenarbeit ist
InC-NC lizenziert (nicht einchecken), ihr Schema ungeprüft; der Check
erscheint als `skipped`, nie als `passed`.

## MU7 — CLI

`python scripts/run_muonium_pilot.py --scenario ideal|offset|reversal|velocity_mixture|aliases [--seed] [--a-min --a-max] [--output]`
gibt Annahmen, Identifizierbarkeit, Moden, Intervallmethode, Suchbereich,
Unsicherheitsart und Grenzen als Standard-JSON aus. Die Überschrift sagt
immer, dass es sich um ein synthetisches Szenario eines idealisierten
Modells handelt.

## Was nicht behauptet wird

Keine LEMING-Simulation, keine Wellenoptik/Beugung, keine
Gerätemodelle für magnetische Gradienten, Polarisation, Coriolis usw.
(nur als parametrisierte Störphase/Parität), keine Realdatenauswertung,
keine Bestätigung von CREP/UTAC/AFET, keine Aussage über die Gravitation
des Antimyons allein.
