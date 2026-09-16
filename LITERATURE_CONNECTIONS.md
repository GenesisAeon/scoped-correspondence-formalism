# Literaturanschlüsse — Revision 3

Recherche und Einordnung: 16. September 2026. Leitfrage: Welche Ergebnisse verbessern konkrete Teile des CREP–UTAC–AFET-Rahmens? Die folgenden Übertragungen sind begrenzte methodische Vorschläge. Sie belegen keine Priorität oder empirische Bestätigung der Gesamtidee.

## 1. Drei vorgeschlagene Anschlüsse, präzisiert

### Takens: Rekonstruktion unter Voraussetzungen

Für eine kompakte d-dimensionale glatte Mannigfaltigkeit, einen C²-Diffeomorphismus F und eine C²-Beobachtung h ist die Verzögerungsabbildung

\[
D_m(z)=(h(z),h(Fz),\ldots,h(F^{m-1}z))
\]

bei m=2d+1 für generische Paare (F,h) eine Einbettung. Das ist eine **hinreichende generische Garantie**, keine notwendige Mindestdimension für jeden Einzelfall. Sie betrifft einen vorhandenen Zustandsraum. Endliche, verrauschte Messungen erhalten dadurch noch keine robuste Rekonstruktionsgarantie. [Takens, Originalbeitrag 1981](https://doi.org/10.1007/BFb0091924); [Gutman, präzise Theoremfassung und eigene Erweiterung](https://arxiv.org/pdf/1510.05843).

**Übernahme:** Typ 2 wird als Bedarf einer erweiterten Darstellung geprüft. Die Zahl 2d+1 ersetzt weder einen Frame-Schwellenwert noch eine Messung von d. Das [Kreisbeispiel](worked_example_reconstruction.md) zeigt ausdrücklich, dass zwei geeignete Koordinaten bei d=1 genügen können und eine ungünstige Abtastung scheitert.

Sauer–Yorke–Casdagli erweitern den Zugang auf kompakte Mengen mit Boxdimension: Die Schranke m>2d_box gehört zu einem Prävalenzresultat; für Verzögerungsabbildungen treten zusätzliche Bedingungen an periodische Orbits hinzu. **Keine pauschale Anwendung auf jede stochastische oder getriebene Zeitreihe.** [Embedology, 1991](https://doi.org/10.1007/BF01053745).

### Causal Emergence: mehrere konkrete, unterschiedliche Ziele

Yang et al. entwickeln NIS+, einen lernenden Ansatz für Makrodynamiken mit Effective Information als Optimierungsziel. Veröffentlichung online am **12. August 2024**, Heftzuordnung **Januar 2025**. Das ist ein möglicher Suchalgorithmus für Darstellungen, kein universeller Satz darüber, wann ein Individuum existiert. Vor einer Übernahme müssen Interventionsannahmen, Schätzung und unabhängige Prognoseprüfung spezifiziert werden. [Verlagsfassung](https://academic.oup.com/nsr/article/doi/10.1093/nsr/nwae279/7732052); [Autorencode](https://github.com/Matthew-ymz/Code-for-Finding-emergence-in-data-5.2).

Zhang et al. definieren Emergenz über das Singularwertspektrum einer Übergangsmatrix. Das liefert eine zusätzliche spektrale Diagnose. Im Artikel sind EI und die SVD-Größe durch Schranken bzw. angenäherte Beziehungen verbunden; sie werden hier nicht identifiziert. Die Verlagsseite vermerkt eine Korrektur der Supplementdatei vom 29. Mai 2025 und keinen öffentlich bereitgestellten Originalcode. Die Revision implementiert nur ausdrücklich angegebene kleine Prüfrechnungen. [npj Complexity, 25. Januar 2025, Gleichungen 7, 11 und 12](https://www.nature.com/articles/s44260-025-00028-0).

**Eigener Grenzfall:** Für P_ij=1/4 ist EI=0, während die Rangformel bei α=1 den Wert 3/4 liefert. Das ist kein Widerspruch innerhalb ihrer Definition; es widerlegt aber die Verwendung dieses positiven Werts als hinreichenden Nachweis informativer Makrokausalität. Vollständige Rechnung im [Makrobeispiel](worked_example_causal_emergence.md).

Rosas et al. operationalisieren Emergenz über Informationszerlegung und kollektive Vorhersagebeiträge. Hoels **CE 2.0** entwickelt nochmals andere Kriterien; die hier eingesehene Fassung ist ein Preprint. Diese Ansätze sind Alternativen mit unterschiedlichen Fragestellungen, keine austauschbaren Bestätigungen. [Rosas et al., 2020](https://doi.org/10.1371/journal.pcbi.1008289); [Hoel, CE 2.0, v3, 2025](https://arxiv.org/html/2503.13395v3).

**Übernahme:** EI, spektrale Redundanz und Synergie erhalten getrennte Metrikkennungen. Für eine Makroeinheit werden zusätzlich dynamische Geschlossenheit und interventionsabhängige Robustheit geprüft.

### Konjugation und RG: zwei unterschiedliche Strukturbeziehungen

Bei invertierbarem stetigem T mit stetiger Umkehrung und exakter Gleichung ist die Beziehung aus Revision 2 eine topologische Konjugation nach konstanter Zeitskalierung. Eine allgemeine Orbitäquivalenz erlaubt flexiblere, orientierungserhaltende Zeitänderungen. Eine verlustbehaftete Projektion ist keine Konjugation; bei exakter Verträglichkeit kann sie eine Semikonjugation sein. [Begrifflicher und mathematischer Anschluss: Colonius–Santana, 2011](https://doi.org/10.3934/cpaa.2011.10.847).

RG-Universalität betrifft das Verhalten unter wiederholter Vergröberung und Reskalierung, insbesondere nahe geeigneten Fixpunkten. Kritische Exponenten und bestimmte Amplitudenverhältnisse können universell sein, während einzelne Amplituden und metrische Faktoren systemspezifisch bleiben. Auch logarithmische Korrekturen und besondere Normalformen sind möglich. [Mussardo, universelle Verhältnisse](https://arxiv.org/abs/hep-th/0010164); [Raju et al., RG-Normalformen, 2019](https://doi.org/10.1103/PhysRevX.9.021014).

**Übernahme:** σ=2,2 ist ohne festgelegte Koordinaten, Normierung und Ableitung keine Universalitätsaussage. Daraus folgt nicht, dass jeder dimensionslose Steilheitsparameter grundsätzlich nichtuniversell sein müsste. Eine begründete normierte Grenzfunktion könnte solche Beziehungen besitzen; sie wäre gesondert nachzuweisen. Die einfache Umparametrisierung von tanh wird im Prüfskript getestet.

## 2. Zusätzliche Anschlüsse, die konkrete Lücken schließen

| Ansatz | Beitrag zum Rahmen | Konkrete Übernahme |
|---|---|---|
| Markov-Lumpability | Wann folgt aus Mikrodynamik eine autonome Makrodynamik? | Kommutationsprüfung PC=CQ und Fehlerbericht |
| Mori–Zwanzig | Was passiert mit ausgelassenen Zuständen? | Gedächtnis und Abhängigkeit vom verborgenen Anfangszustand ausdrücklich zulassen |
| Computational Mechanics | Welche Vergangenheit ist für Prognosen relevant? | prädiktiv äquivalente Historien als Kandidaten für Zustände |
| GENERIC | Wie werden reversible und dissipative Dynamik konsistent verbunden? | Energie-, Entropie- und Degenerationsbedingungen für den thermodynamischen Spezialfall |
| Viabilität und Barrieren | Wie wird Pufferfähigkeit unter fortlaufenden Störungen untersucht? | zulässiger Zustandsbereich, Eingriffe, Störungsbudget und Zeithorizont |
| Informationsgeometrie | Welche Parameter bleiben nach Vergröberung unterscheidbar? | Identifizierbarkeit und Koordinatenabhängigkeit prüfen |

### Geschlossenheit und Gedächtnis

Buchholz behandelt exakte Aggregationsbedingungen für Markov-Ketten. Neuere Arbeiten von Michel–Siegle liefern Fehlerabschätzungen für reduzierte Verteilungen. Damit lässt sich die bislang intuitive Forderung einer „eigenen Dynamik“ direkt an einem Modell prüfen. Die Terminologie ordinary/strong und exact lumpability ist literaturabhängig; hier ist stets die ausgeschriebene Zeilenbedingung maßgeblich. [Buchholz, 1994](https://doi.org/10.2307/3215235); [Michel–Siegle, 2024/aktuelle arXiv-Fassung](https://arxiv.org/abs/2403.07618).

Mori–Zwanzig erklärt, warum Projektionen im Allgemeinen Gedächtnisterme und Beiträge ungelöster Anfangsdaten erzeugen. Die exakte Identität beseitigt den Rechenaufwand nicht automatisch; praktische Schließungen benötigen Approximationen. [Gouasmi–Parish–Duraisamy](https://arxiv.org/abs/1611.06277).

**Übernahme:** Fehlende Markov-Geschlossenheit kann durch einen zusätzlichen Zustand, Historie, andere Beobachtung oder einen expliziten Restterm bearbeitet werden. Das ist eine konkrete Alternative zum voreiligen Postulat neuer physikalischer Dimensionen. Formeln und Beispiele: [Emergenz und Geschlossenheit](emergence_and_closure.md).

### Prädiktive Zustände

Computational Mechanics fasst Vergangenheiten zusammen, wenn sie dieselbe bedingte Zukunftsverteilung besitzen. Unter den Voraussetzungen des Ansatzes liefern diese „causal states“ minimale hinreichende prädiktive Darstellungen. Der Name bedeutet nicht, dass aus Beobachtungsdaten automatisch interventionelle Ursachen identifiziert sind. [Shalizi–Crutchfield, Journalfassung 2001 / Autorenpreprint](https://arxiv.org/abs/cond-mat/9907176).

**Übernahme:** Eine intern gespeicherte Variable muss ihre Prognoserelevanz zeigen. Für CREP und einen Reflexions-/Gedächtnisbaustein ist das ein konkreterer Ausgangspunkt als ein frei gewichteter Gesamtscore. Stationarität, Beobachtungsalphabet und Prognosehorizont bleiben zu begründen.

### Thermodynamik als Strukturforderung

GENERIC verbindet einen Poisson-Anteil mit einem symmetrisch positiv-semidefiniten dissipativen Operator und passenden Energie-/Entropiebedingungen. Es ist ein etablierter Rahmen für geeignete thermodynamische Modelle, keine automatische Thermodynamisierung semantischer Graphen. [Grmela–Öttinger, 1997](https://doi.org/10.1103/PhysRevE.56.6620); [Öttinger, Überblick aus erster Hand](https://arxiv.org/abs/1810.08470).

Die jüngere geometrische Arbeit zu stochastischem GENERIC zeigt eine weitere Ausbaurichtung. Sie wird als **Preprintanschluss** geführt; die Revision leitet keine allgemeine Rauschformel daraus ab. [Peletier et al., 2025](https://arxiv.org/abs/2509.09566).

**Übernahme:** Im [Wärmebeispiel](worked_example_heat_exchange.md) lässt sich die dissipative Struktur vollständig ausrechnen. Das ist ein überprüfbarer AFET-Anschluss mit definierten Einheiten.

### Pufferfähigkeit und Identifizierbarkeit

Control Barrier Functions geben unter Regularitäts- und Zulässigkeitsvoraussetzungen hinreichende Bedingungen dafür, einen sicheren Bereich invariant zu halten. Das ergänzt Rückkehrraten um eine auf Störungen und Eingriffe bezogene Frage. [Ames et al., 2019](https://arxiv.org/abs/1903.11199). Die Revision verwendet einen ausdrücklich gerechneten skalaren Fall sowie (Revision 3.2) zwei gekoppelte Bestände mit gemeinsamem Ressourcenbudget, siehe [Viabilitätsbeispiel](worked_example_viability.md).

Raju–Machta–Sethna untersuchen den Verlust unterscheidbarer Parameterinformation unter Vergröberung mit der Fisher-Metrik. Das liefert einen Anschluss zwischen Informationsbeschreibung und Skalenwechsel, ohne Informations- und Transportgrößen gleichzusetzen. [Physical Review E, 2018](https://doi.org/10.1103/PhysRevE.98.052112).

**Übernahme:** Ein Parameter muss im gewählten Messmodell identifizierbar sein. Beispielsweise bestimmt eine reine Beobachtung von tanh(σΓ) bei unbekannter Skalierung von Γ zunächst nur das Produkt; gleiche Fitwerte beweisen dann keine gemeinsame Naturkonstante.

## 3. Was jetzt zum Formalismus gehört

Verbindlich werden: Art der Abbildung, Rekonstruktionsannahmen, Makro-Geschlossenheit, Interventionsensemble und getrennte Emergenzmetriken. GENERIC ist ein optionales, streng spezifiziertes thermodynamisches Modul. RG, NIS+, PID und prädiktive Zustandsrekonstruktion sind konkrete Forschungsverfahren mit jeweils eigenen Voraussetzungen.

**Nachtrag (F09, 16. September 2026):** PID ist jetzt operationalisiert — Williams–Beer-`I_min`-Atome plus Kolchinsky-Redundancy-Bottleneck, nicht die O-Information als Hauptmetrik. Zur Klarstellung: die O-Information ([Rosas et al., 2019](https://arxiv.org/abs/1902.11239)) und „Reconciling emergences" ([Rosas et al., 2020](https://doi.org/10.1371/journal.pcbi.1008289), oben zitiert) sind zwei verschiedene Arbeiten derselben Erstautorin, keine austauschbaren Referenzen. Siehe [pid_redundancy_bottleneck.md](pid_redundancy_bottleneck.md) mit sieben Prüfungen im Skript. Beide Rosas-Arbeiten bleiben als benannte, nicht operationale Alternativen zitiert. Eine analoge Operationalisierung für Sheaf-Kontextualität (Abramsky–Brandenburger, hier nicht ursprünglich gelistet) steht in [sheaf_contextuality.md](sheaf_contextuality.md) (F08).

Ein universelles Individuationskriterium folgt auch aus dieser Literaturauswahl nicht. Die Revision ersetzt diese offene Frage durch einen dokumentierten, aufgabenspezifischen Prüfvertrag: Was soll als eigenständige Beschreibung gelten, welche Fehler sind zulässig und an welchen unabhängigen Daten kann die Behauptung scheitern?
