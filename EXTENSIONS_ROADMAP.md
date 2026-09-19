# Extensions Roadmap — natürliche mathematische Erweiterungen

Konsolidiert zwei unabhängige DeepResearch-Antworten auf
[prompts/16_deepresearch_natural_extensions.md](prompts/16_deepresearch_natural_extensions.md):
[ChatGPTAstra3.md](prompts/Answers/ChatGPTAstra3.md) (10 Vorschläge) und
["Mathematische Erweiterungen Scoped Correspondence.docx"](prompts/Answers/Mathematische%20Erweiterungen%20Scoped%20Correspondence.docx)
(7 Vorschläge, vermutlich Gemini). Beide unabhängig von Claude verifiziert
(Zahlenbeispiele von Hand nachgerechnet, alle Zitate per Fork gegen
DOI/arXiv geprüft — siehe F26/F28 in `FOLLOWUP_TICKETS.md`). Eine dritte
Einreichung (`ChatGPTAstra4.md`) wurde als erkennbar halluziniert
**verworfen** (F28) — kein Bezug zum echten Repo, erfundene Dateistruktur.

**Harte Regel für jeden Eintrag (aus dem DeepResearch-Auftrag selbst):**
jede Erweiterung hängt an GENAU EINEM bestehenden Baustein, keine
Cross-Layer-Identität, keine Universalitätsbehauptung, echte
DOI/arXiv-Quelle, nach Möglichkeit von Hand nachrechenbares Beispiel.

## Status je Baustein

| Baustein | Kandidat | Quelle | Status |
|---|---|---|---|
| `correspondence` | Approximation Certificates (fixed-map-Spezialfall) | Girard & Pappas 2007, DOI 10.1109/TAC.2007.895849 | ✅ **M10, gemergt** |
| `observation` | Directed Information (Rückkopplungskapazität) | Massey 1990; Permuter, Weissman, Goldsmith 2009 | ✅ **M22, gemergt** |
| `dynamics` | Fenichels Theorem / GSPT (langsame invariante Mannigfaltigkeit) | Fenichel 1979, DOI 10.1016/0022-0396(79)90152-9; Kuehn 2015, DOI 10.1007/978-3-319-12316-5 | offen |
| `dynamics` | Contraction Analysis | Lohmiller & Slotine 1998, DOI 10.1016/S0005-1098(98)00019-3 | ✅ **M14, gemergt** |
| `coupling` | Dirac-Struktur-Komposition | Cervera, van der Schaft & Baños 2007, DOI 10.1016/j.automatica.2006.08.014 | ✅ **M12, gemergt** |
| `coupling` | Dissipativity / Supply Rates | Willems 1972, DOI 10.1007/BF00276493 | ✅ **M15, gemergt** |
| `closure` | CTMC-Generator-Lumpability (`QC=CQ_macro`) | Buchholz 1994, DOI 10.1017/S0021900200107338; Michel & Siegle, DOI 10.1016/j.peva.2024.102464 | ✅ **M11, gemergt** |
| `closure` | Formal Reduction Error Bounds (allgemeine Fehlerschranken) | Michel & Siegle 2025 (dieselbe Quelle, andere Aussage) | ✅ **M21, gemergt** |
| `viability` | Control Barrier Functions | Ames et al. 2017, DOI 10.1109/TAC.2016.2638961; Ames et al. 2019, DOI 10.23919/ECC.2019.8796030 — **von beiden Recherchen unabhängig vorgeschlagen** | ✅ **M16, gemergt** |
| `membership` | — | (gewichtete/kontinuierliche Zugehörigkeit bewusst zurückgestellt, Semantik unklar) | kein Kandidat |
| `identifiability` | Profile Likelihood | Raue et al. 2009, DOI 10.1093/bioinformatics/btp358 | ✅ **M20, gemergt** |
| `identifiability` | Fisher-Information-Sloppiness | Transtrum, Machta & Sethna 2011, DOI 10.1103/PhysRevE.83.036701; Raju et al. 2018 | ✅ **M23, gemergt** |
| `validation` | Split Conformal Prediction | Lei, G'Sell, Rinaldo, Tibshirani, Wasserman 2018, DOI 10.1080/01621459.2017.1307116 | ✅ **M13, gemergt** |
| `contextuality` | Čech-Cohomology-Witness | Abramsky, Mansfield & Barbosa 2012, arXiv 1111.3620 | ✅ **M24, gemergt** |
| `contextuality` | CSW-Grapheninvarianten | Cabello, Severini & Winter 2014, DOI-bestätigt (PRL 112, 040401) | ✅ **M19, gemergt** |
| `information_decomposition` | BROJA bivariate Unique Information | Bertschinger, Rauh, Olbrich, Jost & Ay 2014, DOI 10.3390/e16042161 | ✅ **M17, gemergt** |
| `thermo` | Schnakenberg Network Thermodynamics | Schnakenberg 1976, DOI 10.1103/RevModPhys.48.571 | ✅ **M18, gemergt** |
| `metarules` (kein Originalbaustein, F25) | — | context_transformations.md §6 | ✅ **M9, gemergt** |

**Status (2026-09-19): alle 17 ursprünglich identifizierten Erweiterungskandidaten
(M9–M24) sind gemergt.** Jeder einzeln unabhängig geprüft (Zitate gegen
DOI/arXiv, mindestens eine Zahl von Hand nachgerechnet, Diff-Scope
kontrolliert). Nächste Runde: eine zweite DeepResearch-Anfrage für weitere
Kandidaten, siehe `prompts/33_deepresearch_structural_and_mathematical_extensions.md`.

**Bewusst kein Kandidat identifiziert (mit Begründung):** `validation`
(neue Theoreme würden den empirischen Testcharakter verfälschen —
`validation` bleibt Protokoll, nicht Theorie); `thermo` als Ganzes
(bestehende Abdeckung durch M8 bereits vollständig, Schnakenberg oben
ist die einzige verbleibende offene Vertiefung); `information_decomposition`
über BROJA hinaus (N-Quellen-PID bleibt bewusst offenes Forschungsfeld,
nicht spekulativ vorwegnehmen).

## Reihenfolge / Priorisierung

Kein festes Ranking — die drei aktuell in Arbeit befindlichen (M11–M13)
wurden nach Astra3s eigener Einschätzung "geringster Aufwand" bzw.
bereits vollständig durchgerechnetem Beispiel gewählt. Für die
verbleibenden zwölf Kandidaten gilt dieselbe Logik: kleinere,
gut belegte Fälle zuerst, größere (Čech-Kohomologie, BROJA, Schnakenberg)
später. Reihenfolge wird bei Bedarf mit Johann abgestimmt, nicht
automatisch abgearbeitet.

## Runde 2 (2026-09-19): zwei unabhängige Claude-Agenten-Recherchen

Vier menschliche DeepResearch-Antworten auf `prompts/33_deepresearch_structural_and_mathematical_extensions.md`
erfüllten den Spur-A/B-Auftrag nicht zuverlässig (siehe F43 in
`FOLLOWUP_TICKETS.md` für Details — eine verworfen als stale/halluziniert,
eine erwies sich als Wiederholung von Runde 1, eine enthielt ein per
WebSearch als falsch verifiziertes Zitat). Deshalb wurden zusätzlich zwei
unabhängige, frische general-purpose-Agenten mit vollem Repo-Kontext
beauftragt — ohne Einsicht ineinander oder in die menschlichen Antworten,
mit Pflicht zur Live-Verifikation jedes Zitats per WebSearch/WebFetch/
Crossref-API. Fünf Kandidaten mit klarer Formel-zu-Formel-Anknüpfung und
kleinem/mittlerem Aufwand wurden als M25–M29 an Aeon gesendet. Drei
weitere Punkte sind zurückgestellt, weil sie eine Grundsatzentscheidung
(Baustein-Klassifizierung bzw. ein komplett neues Modul) statt einer
reinen additiven Erweiterung sind.

| # | Baustein | Kandidat | Quelle | Konvergenz | Status |
|---|---|---|---|---|---|
| M25 | `observation` | Arimoto–Blahut-Algorithmus (Kanalkapazität für beliebige DMC) | Arimoto 1972, DOI 10.1109/TIT.1972.1054753; Blahut 1972, DOI 10.1109/TIT.1972.1054855 | ✅ beide Agenten unabhängig, identisches Zahlenbeispiel (Z-Kanal ε=0,5 → C=0,321928 bit, optimale Eingabe (0,6; 0,4)) | ✅ **gemergt** |
| M26 | `coupling` | Lie-Poisson-Struktur / Casimir-Invarianten (formalisiert die bereits verlangte GENERIC-Degeneriertheitsbedingung `J∇S=0`) | Arnold 1966, DOI 10.5802/aif.233; Marsden & Ratiu 1999, DOI 10.1007/978-0-387-21792-5 | nur Agent B | ✅ **gemergt** |
| M27 | `membership` | Formal Concept Analysis (Galois-Verbindung auf der bestehenden binären `MembershipMatrix`) — schließt die bisherige "kein Kandidat"-Lücke OHNE gewichtete Semantik | Ganter & Wille 1999, DOI 10.1007/978-3-642-59830-2 | nur Agent B | ✅ **gemergt** |
| M28 | `viability` | Nagumos Tangentialkegel-Bedingung (verallgemeinert M16/CBF auf nicht-glatte/polyedrische Mengen) | Nagumo 1942, DOI 10.11429/ppmsj1919.24.0_551 (Übersetzung: arXiv:2406.18614) | beide (Agent A: Saint-Pierre-Kernel-Approximation; Agent B: Nagumo direkt — Agent B gewählt, kleinerer Aufwand) | ✅ **gemergt** |
| M29 | `dynamics` | Landau-Entwicklung der bestehenden kubischen Normalform als Selbst-Falsifizierungs-Instrument gegen Universalitätsansprüche (β=1/2 modellintern vs. β=1/8 beim exakten 2D-Ising-Modell) | Onsager 1944, DOI 10.1103/PhysRev.65.117; Yang 1952, DOI 10.1103/PhysRev.85.808; Guckenheimer & Holmes 1983, DOI 10.1007/978-1-4612-1140-2 | nur Agent B | ✅ **gemergt** |
| — | neuer Baustein `pattern_formation` (Johanns Entscheidung 2026-09-19: eigenständig, nicht (a)) | Turing-Instabilität (Diffusions-getriebene Musterbildung) | Turing 1952, DOI 10.1098/rstb.1952.0012; Schnakenberg 1979, DOI 10.1016/0022-5193(79)90042-0 — **ACHTUNG:** anderer Schnakenberg-Aufsatz als M18 (1976)!; Murray 2003, DOI 10.1007/b98869 | ✅ beide Agenten, aber UNEINIG in der a/b-Klassifizierung — Agent A hätte eine formal mögliche (a)-Anbindung an `dynamics` gesehen (gleiche Jacobi-Eigenwert-Rechnung, parametrisiert über Wellenzahl k); Johann entscheidet sich bewusst für (b), Anbindung bleibt als offener, unbewiesener `correspondence`-Kandidat dokumentiert (siehe unten) | 🔄 Prompt gesendet (`prompts/39_...md`) |
| — | neuer Baustein `free_boundary` (Johanns Entscheidung 2026-09-19) | Stefan-Problem / freie Randbedingung (bewegliche Phasengrenze als eigene dynamische Variable, kein Unterfall von `viability`) | Kot 2017, DOI 10.1007/s10891-017-1638-2; Bollati, Natale, Semitiel & Tarzia, arXiv:1906.08601 (Rubinstein 1971 bewusst NICHT verwendet — keine verlässlich verifizierte DOI in dieser Runde) | ✅ beide Agenten, fast identisches Rechenbeispiel (λ≈0,6201 bei St=1) | 🔄 Prompt gesendet (`prompts/40_...md`) |
| — | neuer Baustein `percolation` (Johanns Entscheidung 2026-09-19) | Perkolation (Kesten-Theorem / Bethe-Gitter-Verzweigungsprozess) | Kesten 1980, DOI 10.1007/BF01197577; Fisher & Essam 1961, DOI 10.1063/1.1703745 | ✅ beide Agenten, beide warnen unabhängig vor Zahlenkoinzidenzen mit bereits verworfenen Werten (u.a. Bethe-Gitter-Zwischenwert 1/16) | 🔄 Prompt gesendet (`prompts/41_...md`) |

**Offener, unbewiesener `correspondence`-Kandidat (bewusst nicht gebaut):**
eine mögliche zukünftige Konjugation zwischen dem neuen Turing-Baustein und
`dynamics` über die gemeinsame Jacobi-Eigenwert-Struktur — Turings
`S_rec(k)` würde `dynamics.recovery_rate_at_equilibrium` (=`S_rec(0)`) auf
eine Wellenzahl `k` verallgemeinern. Das ist eine strukturelle Beobachtung,
KEINE Gleichsetzung der beiden Bausteine. Sollte das je verfolgt werden,
läuft es über den normalen `correspondence`-Vertrag mit eigenem Beweis und
eigener Prüfung, nicht als stillschweigende Abkürzung.

## Arbeitsweise (unverändert für jeden Eintrag)

1. Prompt für Aeon schreiben (Referenzen gegen echten Code/Doku-Stand
   verifizieren, bevor gesendet wird).
2. Aeon liefert auf eigenem Branch (`aeon/m<n>-<name>`).
3. Claude reviewed unabhängig: Diff-Scope prüfen (nur additive Module,
   keine Kernmutation), Skript selbst nachrechnen, mindestens eine Zahl
   von Hand gegenprüfen.
4. Merge erst nach Johanns explizitem OK.
5. `FOLLOWUP_TICKETS.md` und diese Datei aktualisieren.

Mehrere Einträge können parallel an Aeon gehen, wenn sie unterschiedliche
Module betreffen (kein Merge-Konflikt-Risiko) — aktuell M11/M12/M13
gleichzeitig in Arbeit.
