# Endliche kausale Modelle und interventionelle Abstraktion (J9)

Paket J9 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §15. Code: `src/scoped_correspondence/causal/finite_scm.py`,
`.../abstraction.py`. Prüfungen: `verification/verify_finite_causal_models.py`,
`verification/verify_causal_abstraction.py` (beide math). Lizenz der
Dokumentation: CC BY 4.0.

## 1. Modellklasse

Endliche azyklische SCMs: endogene Variablen mit endlichen Wertebereichen
und **deterministischen** Mechanismen; Zufall nur aus einer expliziten
endlichen **gemeinsamen** Verteilung der exogenen Variablen — gemeinsame
exogene Ursachen sind darstellbar, Unabhängigkeit wird nie still
vorausgesetzt (`independent_exogenous` erzeugt sie nur auf ausdrücklichen
Wunsch). Ein harter Eingriff `do(V = v)` ersetzt die Strukturgleichung.

Validiert werden: DAG (keine Zyklen, Eltern sind deklarierte endogene
Variablen), Mechanismen lesen **nur** ihre deklarierten Eltern und
exogenen Eingänge (durchgesetzt über bewachte Abbildungen), Ausgaben im
deklarierten Wertebereich (bei jeder ausgewerteten Belegung), exogene
Wahrscheinlichkeiten exakt und mit Summe genau 1 (sonst Fehler, **keine**
stille Normalisierung), Eingriffswerte im Wertebereich, Rechenbudget
(Abbruch entscheidet nichts).

**J-C18 — Beobachtung ist nicht Eingriff:** $U$ fair, $X=U$; Modell 1
$Y=X$, Modell 2 $Y=U$. Beide liefern dieselbe Beobachtungsverteilung, aber
$P(Y=1\mid do(X=1))=1$ bzw. $1/2$ (TV $1/2$). Die epistemische Faser über
**genau diese zwei** Kandidaten (bestehende `observation_fiber`) zeigt die
Mehrdeutigkeit, ohne eine Aufzählung aller denkbaren Kausalmodelle zu
behaupten. **MR8:** Umbenennen der Variablen samt Eingriffen ändert
nichts.

## 2. Abstraktionsbedingung

Für jede **deklarierte** Mikrointervention $i$ wird geprüft
$\tau_\#P_{\rm micro}^{do(i)}=P_{\rm macro}^{do(\omega(i))}$ — exakt
(Brüche) oder ausdrücklich als numerischer Vergleich mit Toleranz
gekennzeichnet. Getrennt davon: Surjektivität von $\omega$ auf die
deklarierte Makro-Interventionsmenge und Ordnungserhaltung bezüglich
$i\le j\iff j$ erweitert $i$ (S14, Definition 3). Es geht um Gleichheit
**interventioneller** Verteilungen, nicht um kontrafaktische Kopplungen.
Jedes Ergebnis nennt seinen Interventionsscope.

**J-C19:** Mikro $X_1,X_2$ unabhängig fair, $Y=X_1\oplus X_2$; Makro
$Z$ fair, $\bar Y=Z$; $\tau=(x_1\oplus x_2,y)$. Nichtstun und die vier
vollständigen Eingriffe, abgebildet nach $a\oplus b$: alle fünf exakt,
surjektiv, ordnungserhaltend. Erweiterung $do(X_1=1)\mapsto do(Z=1)$:
TV $1/2$ **und** (J0-Befund B3) Ordnungsverletzung, denn
$do(X_1=1)\le do(X_1=1,X_2=1)\mapsto do(Z=0)$. Die alternative Zuordnung
$do(X_1=1)\mapsto$ Nichtstun besteht beide Prüfungen — ein konkreter
Zeuge dafür, dass nicht jede andere Abbildung scheitert.

Weitere Prüfungen: falsche Variable als Quelle von $Z$ (scheitert), nicht
surjektive Abbildung, Abbildung außerhalb der Makromenge (Eingabefehler),
ein einzelner verletzender Eingriff genügt zur Widerlegung, korrelierte
Exogene im Mikromodell ($U_1=U_2$ ⇒ Nichtstun-Prüfung TV $1/2$),
Budgetabbruch ohne Urteil. **Ehrliche Grenze:** Ein Vertauschen der beiden
Makrokoordinaten ist in diesem Beispiel prinzipiell unsichtbar, weil
$\bar Y=Z$ und $Y=X_1\oplus X_2$ stets gleich sind; das ist im Test
festgehalten statt als Erkennung gezählt.

Kein Graphlernen, kein kausaler Realdatenanspruch, keine kontrafaktische
Abstraktion (Plan §22).

## 3. Quelle

S14 Rubenstein et al. (2017), *Causal Consistency of Structural Equation
Models* — Links siehe Plan §21; die genaue Ordnungsdefinition steht zum
Volltextabgleich im [`DEEP_RESEARCH_BACKLOG.md`](../DEEP_RESEARCH_BACKLOG.md).
