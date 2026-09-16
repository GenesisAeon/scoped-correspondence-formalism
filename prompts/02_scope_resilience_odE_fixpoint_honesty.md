# Phase-2-Prompt 2/N: scope-resilience -- ODE/Fixpunkt-Dokumentation korrigieren

**Repo:** `D:\mandala\scope-resilience` (GenesisAeon Package 41, PyPI `scope-resilience`)
**Ziel dieses Tickets:** eine numerisch verifizierte Diskrepanz zwischen
einer behaupteten "Fixpunkt"-Formel und der Differentialgleichung, aus
der sie angeblich folgt, in der Dokumentation korrigieren. **Keine
Verhaltensaenderung im Code, kein Versions-relevanter Logikwechsel, kein
Versions-Bump** (folgt separat nach Review).

## Kontext (numerisch verifiziert, 2026-09-15)

`src/scope_resilience/semantic_utac.py`, Modul-Docstring, behauptet:

```
H_sem(t) = semantic coherence density on path P
K_sem    = maximum coherence capacity (normalised to 1.0)
H*_sem   = coherence attractor = tanh(σ · Γ_sem(P))

dH_sem/dt = r·H_sem·(1 − H_sem/K_sem)·tanh(σ·Γ_sem)

Fixpunkt: H*_sem = K_sem · tanh(σ · Γ_sem)
```

**Das stimmt nicht.** Fuer die angegebene Differentialgleichung
`dH/dt = r·H·(1-H/K)·tanh(σΓ)` sind die einzigen Nullstellen `H=0`,
`H=K` (unabhaengig von Γ), oder `tanh(σΓ)=0`. Der behauptete Fixpunkt
`H*=K·tanh(σΓ)` loest diese Gleichung NICHT, ausser in Sonderfaellen.

Numerisch bestaetigt (r=1, K=1, σ=2.2, Γ=0.5):
```python
H_star_claimed = K * tanh(sigma*gamma)  # = 0.8005
dH/dt bei H_star_claimed                # = 0.128  (!= 0, sollte bei einem echten Fixpunkt exakt 0 sein)
dH/dt bei H=K (der tatsaechliche Fixpunkt der angegebenen ODE)  # = 0.0 (korrekt)
```

**Wichtig -- Laufzeitverhalten ist NICHT betroffen:** `attractor()`
berechnet `K_sem * tanh(σ*Γ_sem)` direkt algebraisch; die ODE wird im
Code an keiner Stelle tatsaechlich integriert. Der Fehler betrifft nur
die Docstring-Herleitung/Motivation, nicht das tatsaechliche
Programmverhalten. `is_hallucination_regime()`/`state_dict()`
funktionieren unveraendert korrekt.

## Aufgabe

In `semantic_utac.py`, Modul- und Klassen-Docstring, den Fixpunkt-
Anspruch **ehrlich korrigieren, ohne die Laufzeit-Formel `attractor()`
zu aendern**. Vorschlag fuer die korrigierte Formulierung (bitte diesen
Wortlaut sinngemaess uebernehmen, nicht neu erfinden):

> "H*_sem = K_sem · tanh(σ · Γ_sem) is used here as the coherence
> **reference/threshold** for hallucination-vs-coherence regime
> classification -- it is NOT a rigorously derived fixpoint of the
> stated logistic ODE `dH/dt = r·H·(1-H/K)·tanh(σΓ)` (whose actual
> nonzero fixpoint is H=K, independent of Γ; verified numerically
> 2026-09-15). The ODE above is presented as motivating/illustrative
> context for the logistic-growth intuition behind H_sem, not as the
> literal equation `attractor()` implements -- `attractor()` computes
> K_sem·tanh(σΓ_sem) directly and algebraically, without integrating
> any ODE. Treat H*_sem as an independently defined regime-boundary
> reference value."

Bitte:
1. Den Docstring-Abschnitt oben in `semantic_utac.py` entsprechend
   umschreiben (Modul-Docstring UND `SemanticUTAC`-Klassen-Docstring,
   beide enthalten aehnliche Aussagen -- pruefen ob beide betroffen sind).
2. Keine Funktions-Logik in `attractor()`, `is_hallucination_regime()`,
   oder `state_dict()` aendern.
3. Falls Tests existieren, die den Docstring-Wortlaut pruefen (z.B. per
   Doctest), diese entsprechend anpassen -- aber keine neuen
   Verhaltens-Assertions hinzufuegen, die vorher nicht da waren.

## Akzeptanzkriterien

- `pytest` laeuft weiterhin komplett gruen, exakt dieselbe Anzahl Tests
  wie vorher (reine Doku-Aenderung, keine neuen/entfernten Tests noetig
  fuer dieses Ticket).
- `attractor()`, `is_hallucination_regime()`, `state_dict()` liefern
  bitwei­se identische Ergebnisse wie vorher (`git diff` sollte in
  `semantic_utac.py` NUR Docstring-Zeilen zeigen, keine Code-Zeilen
  ausserhalb von Kommentaren/Docstrings).
- Kein Versions-Bump, kein CHANGELOG-Eintrag, kein Zenodo-Release --
  das macht Claude nach Review in einem separaten Schritt.

## Bitte NICHT tun

- Keine Aenderung an der tatsaechlichen `attractor()`-Formel oder der
  ODE selbst -- nur an der Beschreibung/Herleitung im Docstring.
- Keine Aenderung an `semantic_crep.py`, `path_monitor.py`, `system.py`
  oder sonstigen Dateien -- nicht Teil dieses Tickets.
- Keine neuen Abhaengigkeiten.
