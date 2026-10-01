# Myonium-Gravitation — Quellenaudit (MU0)

Teil von [`MUONIUM_GRAVITY_ROADMAP.md`](../MUONIUM_GRAVITY_ROADMAP.md).
Abrufdatum: 2026-10-01. Lizenz: CC BY 4.0.

Getrennt werden drei Arten von Angaben (Plan §2, §10/MU0):

1. **heutige Quelle** — was die geprüfte Originalarbeit tatsächlich
   berichtet;
2. **historischer Vorschlag** — frühere Konzepte, keine aktuellen Messwerte;
3. **eigene Designwerte** — illustrative Zahlen der Kontrollfälle.

## 1. Heutige Quelle

**MU-S1** J. Zhang et al., *Generation of a high-intensity, superthermal
muonium beam for gravity and laser spectroscopy experiments*, Nature
Physics, DOI `10.1038/s41567-026-03433-x`. Geprüft: Verlagsseite
erreichbar, Titel und Veröffentlichungsdatum (14.09.2026) aus den
Seitenmetadaten. Inhaltlich laut Plan: Demonstration und
Charakterisierung einer Strahlquelle; eine Gravitationsmessung wird
**vorbereitet**. Ein Volltextaudit der Zahlen wird hier nicht behauptet.
Der Plan nennt eine Geschwindigkeit um 2180 m/s; eine schmale
Geschwindigkeitsverteilung ist kein nahezu ruhender Strahl.

**MU-S2** arXiv:2512.19923v1 (Vorabfassung vom 22.12.2025, Titel beginnt
mit „Synthesis“) — erreichbar. Zahlen, Unsicherheiten und Formeln der
Vorab- und der Verlagsfassung werden nicht unbemerkt gemischt.

**MU-S4** ETH-Mitteilung vom 15.09.2026 — erreichbar (HTTP 200);
institutionelle Statusmeldung, Zukunftsaussagen sind Planungen. Nicht als
Datenquelle verwendet.

**MU-S5** Datenreferenz `10.3929/ethz-c-000802445` — DOI-Auflösung und
ETH Research Collection antworteten mit HTTP 429 bzw. 500; **über die
DataCite-API geprüft** (alternativer Zugang): Titel „Data for: Generation
of a high-intensity, superthermal muonium beam for gravity and laser
spectroscopy experiments“, Jahr 2026, Format `text/csv`, Lizenz
**„In Copyright – Non-Commercial Use Permitted“ (rightsstatements.org
InC-NC/1.0)**. Folge: Die Daten dürfen **nicht** in dieses Repository
(Code GPLv3+, Doku CC BY 4.0) eingecheckt werden. Ein MU6-Realdatenzweig
kann sie höchstens lokal, hashgeprüft und uneingecheckt lesen (wie der
bestehende SPARC-Weg) — und nur zur Kalibrierung von Strahl- oder
Nachweisparametern, nie als Gravitationsmessung. Inhalt und Spalten-
schema sind noch nicht geprüft.

## 2. Historischer Vorschlag

**MU-S3** Antognini et al. (2018), *Studying Antimatter Gravity with
Muonium*, arXiv:1802.01438 (erreichbar), DOI `10.3390/atoms6020017`
(Verlagsseite: HTTP 403, vermutlich Bot-Sperre; **bibliografisch über die
Crossref-API bestätigt**: *Atoms*, 09.04.2018, Antognini, Kaplan, Kirch, …).
Interferometrie-Kontext; historische Strahlannahmen sind keine aktuellen
Messwerte.

Offene Punkte für eine spätere Volltextrecherche stehen gesammelt in
[`DEEP_RESEARCH_BACKLOG.md`](../DEEP_RESEARCH_BACKLOG.md).

## 3. Eigene Designwerte (nur Kontrollfälle)

$g=9{,}81$ m/s² (kein vor Ort gemessener Präzisionswert), $\tau=2{,}2$ µs
(gerundet), $T=2\tau$, $d=100$ nm, $v=2180$ m/s, $C=0{,}35$ für die
Ereignisabschätzung. Alle daraus abgeleiteten Größen (Plan §5.2, MU-C03,
MU-C13) sind **Modellkontrollwerte**, keine LEMING-Ergebnisse und keine
Anforderungsspezifikation des Experiments.

## 4. Begriffliche Festlegungen aus der Quellenlage

- Myonium ist das neutrale gebundene System aus positivem Myon und
  Elektron, **kein** reines Antimaterieatom. Aus einer Myonium-Messung
  folgt die Gravitation des Antimyons allein erst mit zusätzlichen
  Annahmen über Elektron, Bindungsenergie und Zusammensetzung.
- Einzelbahnabsenkung ($aT^2/2$), relative Verschiebung am dritten
  Gitter ($aT^2$) und Interferometerphase ($2\pi aT^2/d$) sind
  verschiedene Größen; abweichende Faktoren in einer Veröffentlichung
  sind zuerst ein Anlass zur Prüfung von Geometrie und Konventionen,
  kein automatisch nachgewiesener Fehler.

## 5. Fehlendes Begleitskript

Der Plan nennt ein Begleitskript `independent_controls.py` mit „29/29“
bestandenen Kontrollgruppen. Es war nicht unter den gelieferten Dateien.
Die MU-Kontrollen wurden daher ausschließlich selbst hergeleitet
(`verification/plan_controls/mu_series_independent_controls.py`, 17/17);
„29/29“ ist nicht reproduziert.
