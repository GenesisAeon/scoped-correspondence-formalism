# Geprüfte Standardisierungsregel und endliche Gegenmodelle (J10)

Paket J10 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §16. Code: `src/scoped_correspondence/causal/selection_diagrams.py`,
`.../transport.py`. Prüfung: `verification/verify_scoped_transportability.py`
(math). Lizenz der Dokumentation: CC BY 4.0.

**Dies ist eine geprüfte Standardisierungsregel mit endlichen
Gegenmodellen — kein allgemeiner Pearl-Transportabilitätssolver.**

## 1. Graphprüfung

`DAG` (azyklisch, explizite latente Knoten möglich) und `d_separated`
über den moralisierten Vorfahrengraphen. Der do-Graph $G_{\bar X}$
entfernt alle Kanten **in** $X$. `s_admissible` prüft
$(Y\perp S\mid X,Z)$ in $G_{\bar X}$ — eine **deklarierte** kausale
Annahme, nicht aus Daten gelernt. Allgemeine ADMG-/sID-Unterstützung ist
nicht enthalten.

**J-C23:** Collider $A\to C\leftarrow B$, $C\to D$: ohne Konditionierung
getrennt, mit $C$ oder $D$ verbunden. In $S\to Z\to Y\leftarrow X$ ist
$S$ von $Y$ gegeben $X,Z$ getrennt, gegeben nur $X$ nicht. Die falsche
Richtung (Kanten **aus** $X$ entfernen) würde in
$S\to X\leftarrow U\to Y$, $X\to Y$ den Pfad über den Collider $X$
öffnen — im Test nachgewiesen.

## 2. Die Regel

$$Q(Y\mid do(X=x))=\sum_z P(Y\mid do(X=x),Z=z)\,Q(Z=z)$$

Geprüfte Voraussetzungen, jede mit eigenem Feld: Quellgrößen sind
**interventionell** (`source_provenance="source_experiment"`;
beobachtete $P(Y\mid X,Z)$ werden nicht ersatzweise angenommen), $Z$ ist
beobachtet und kein Nachfahre von $X$, $Z$ ist S-admissibel, Support für
jedes $z$ mit $Q(z)>0$. Tabellen müssen vollständig sein.

## 3. Drei getrennte Ergebnisse

| Ergebnis | Bedeutung |
|---|---|
| `certified_applicable` | die Formel folgt unter den geprüften Voraussetzungen des deklarierten Diagramms |
| `not_certified_by_this_rule` | eine Voraussetzung fehlt oder ist unbewiesen — **kein** Nichttransportabilitätsbeweis |
| `non_identified_by_counter_models` | zwei zugelassene vollständige Quelle-Ziel-Familien stimmen in **allen** verfügbaren Größen überein und unterscheiden sich im Zielwert |

## 4. Kontrollen

- **J-C20:** Quelle $Z\sim{\rm Bern}(1/2)$, Ziel $Z\sim{\rm Bern}(3/4)$,
  $Y=X\oplus Z$; Quelltabellen aus den **Interventionsverteilungen** des
  endlichen Quell-SCM (J9). Ergebnis $3/4$ und $1/4$, Effekt $-1/2$;
  direkte Rechnung im Ziel-SCM stimmt überein; der ungewichtete
  Quelleffekt $0$ wäre falsch. Ohne $Z=1$ in der Quelle: nicht
  zertifiziert (Support).
- **J-C21:** In beiden Familien Quelle $X=U$, $Y=X$; Ziel einmal $Y=X$,
  einmal $Y=U$. Quellbeobachtung, beide Quellexperimente und
  Zielbeobachtung identisch; $Q(Y=1\mid do(X=1))$: $1$ vs. $1/2$. Weicht
  **eine** verfügbare Größe ab, ist das Paar kein Zeuge.

Weitere Pflichtprüfungen: $Z$ als Nachfahre von $X$, Verletzung der
S-Admissibilität ($S\to Y$), unvollständige Tabellen, Budgetgrenze beim
Aufbau der Quelltabellen.

## 5. Quelle

S15 Pearl & Bareinboim (2014), *External Validity* — Definition 8 /
Korollar 1; Volltextabgleich im [`DEEP_RESEARCH_BACKLOG.md`](../DEEP_RESEARCH_BACKLOG.md).
