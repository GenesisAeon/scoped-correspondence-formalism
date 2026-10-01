# Organoid-Netzwerke — Quellenaudit (ON0)

Teil von [`ORGANOID_NETWORK_ROADMAP.md`](../ORGANOID_NETWORK_ROADMAP.md).
Abrufdatum 2026-10-01. Lizenz: CC BY 4.0. Quellenstatus, Datenverfügbarkeit
und rechtliche Wiederverwendbarkeit sind getrennte Felder.

| ID | Quelle | Geprüft am 2026-10-01 | Rolle |
|---|---|---|---|
| ON-S1 | Chow et al., *Modular organoid networks acquire source-signal discrimination through input-driven network refinement*, Communications Biology, DOI 10.1038/s42003-026-11036-8 | DOI löst auf; Titel und Veröffentlichungsdatum **28.09.2026** aus den Seitenmetadaten bestätigt. Kein Volltextaudit; Supplement und Rohsignale nicht geprüft | biologisches Motiv, Scope, Datenanforderungen |
| ON-S2 | Duenki & Ikeuchi 2026, DOI 10.1038/s42003-026-09589-9 | Verlagsseite erreichbar | Vergleich mehrgliedriger Netzwerke; keine Kritikalitätsbehauptung übernommen |
| ON-S3 | Bertschinger et al. 2014, DOI 10.3390/e16042161, arXiv:1311.2852 | arXiv erreichbar; die SCF-Implementierung (`broja.py`) gelesen | BROJA-Definition |
| ON-S4 | Lazic 2010, DOI 10.1186/1471-2202-11-5 (PMC2817684) | PMC-Seite erreichbar | Replikationseinheit, verschachtelte Messungen |
| ON-S5 | Varoquaux 2018, DOI 10.1016/j.neuroimage.2017.06.061, arXiv:1706.07581 | arXiv erreichbar | Unsicherheit bei kleinen Stichproben / Cross-Validation |
| ON-S6/S7 | SCF-Dokumentation zu Arimoto–Blahut und Directed Information | Code am aktuellen Stand gelesen (siehe Roadmap, API-Tabelle) | bestehende Implementierungen |

## Was aus ON-S1 übernommen wird — und was nicht

Laut Plan (nicht hier im Volltext nachgeprüft): wiederholt stimulierte
Trios zeigten konsistent verbesserte Dekodierbarkeit; zentraler Vergleich
fünf Solo-, vier Duo-, fünf Trio-Präparate; beim Duo lagen beide Eingänge
im selben Organoid, beim Trio in getrennten — die Konfigurationen ändern
also **mehr als die Modulzahl**; Eingangspaare wurden bei etwa 50 %
SVM-Leistung gewählt; 80 von 100 Wiederholungen je Eingang zum Training,
20 zur Bewertung; funktionelle Konnektivität u. a. aus Kofeuer-Beziehungen.

Daraus folgen die Grenzen des Piloten: keine universelle
Drei-Modul-Schwelle; Korrelation ist keine Synapse; biologische
Replikation (Präparat) und Reizwiederholung (Versuch) bleiben getrennt.
Die SCF-Modelle sind eigene methodische Vorschläge, keine Rekonstruktion
der biologischen Mechanismen.

## Offen für eine spätere Volltextrecherche

Siehe [`DEEP_RESEARCH_BACKLOG.md`](../DEEP_RESEARCH_BACKLOG.md): Volltext
und Methoden von ON-S1 (Zahlen der Präparate, Auswahlregel, Splits),
Verfügbarkeit, Format und Lizenz der verlinkten Diagrammquelldaten und
Rohsignale (Voraussetzung für ON6b).
