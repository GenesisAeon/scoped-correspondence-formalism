Auftrag: Teil 2, Milestone 9 ("Metaregeln") — natürliche Erweiterung von
`membership`/`closure`, formal bereits in `context_transformations.md`
§6 spezifiziert, bisher nirgends implementiert.

## Kontext

§6 definiert den Regelzustand `m` und seine mögliche Eigendynamik
`m′=H(m,z,c,u,t)` (diskretes Update oder Ereignis), sowie die
gemeinsame Eingriffsmenge **mit** `m` als Argument:

\[
\mathcal U_{joint}(z,c,m,t)=\mathcal U_{physical}\cap\bigcap_\alpha\mathcal U_\alpha.
\tag{T5}
\]

`membership.joint_control_set(U_physical, U_alphas)` (M4, gemergt) hat
KEIN `m`-Argument — die Metaregel-Dimension von T5 ist bisher nicht
umgesetzt. §6 nennt außerdem zwei konkrete, bisher unimplementierte
Aussagen:

1. "Eine Prioritätsregel kann eine Anforderung ausdrücklich aufgeben;
   sie erfüllt dadurch nicht beide Anforderungen zugleich."
2. "Unbeobachtetes m kann eine sonst geschlossene Beschreibung
   ungeschlossen machen."

Beide sind mit bereits gemergten Modulen (`membership`, `closure`)
konkret durchrechenbar, ohne neue Theorie zu erfinden.

## Umfang dieses Auftrags

### 1. `metarules.MetaRuleUpdate` (diskrete Regel-Eigendynamik)

Typisierter Wrapper für `m′=H(m,z,c,u,t)` als diskretes Update oder
Ereignis (§6, zweiter Absatz). Kein kontinuierliches/stochastisches
Regel-Update in diesem Auftrag — nur die diskrete Form. Muss
dokumentieren: eine rein beschreibende Änderung von `m` verändert
zunächst nur `π` (Beobachtung); eine tatsächlich durchgesetzte Regel
kann Eingriffe und den physischen Verlauf verändern (§6, letzter Satz)
— beide Fälle als unterscheidbare, benannte Varianten im Rückgabewert.

### 2. `metarules.priority_joint_control_set(...)` (Prioritätsregel für T5)

Erweitert `membership.joint_control_set` um eine Metaregel-Ebene, OHNE
`membership/core.py` zu ändern — nur Aufruf:
1. Ruft zuerst `membership.joint_control_set(U_physical, U_alphas)`
   unverändert auf.
2. Nur wenn `conflict=True` (leerer Schnitt): wendet eine
   Prioritätsregel `m` an, die EXPLIZIT eine der beiden
   Anforderungen `U_α` aufgibt (per Index/Namen aus `m` bestimmt) und
   den Schnitt mit der verbleibenden Menge neu bildet.
3. Bericht muss explizit ausweisen, WELCHE Anforderung aufgegeben
   wurde, und dass dadurch nicht beide Anforderungen gleichzeitig
   erfüllt sind (§6, letzter Satz — wörtlich referenzieren).

Konkretes Beispiel: mindestens ein Fall mit leerem Rohschnitt (analog
`joint_control_set`s bereits getestetem `t5_empty_conflict`-Fall aus
`verify_membership_core.py`), bei dem die Prioritätsregel eine
konkrete, im Bericht sichtbare Eingriffsmenge liefert.

### 3. `metarules.unobserved_metarule_breaks_closure()` (§6 Satz 3, NEU)

Konkretes, von Hand nachrechenbares Gegenbeispielpaar über ein
gemeinsames `(z,m)`-System mit `z,m ∈ {0,1}` (4 Gelenkzustände),
projiziert auf `z` allein via `closure.partition_matrix` (nur Aufruf,
keine Änderung an `closure/core.py`):

- **Fall A (m aus z ableitbar):** `m` ist deterministisch durch `z`
  bestimmt (z.B. `m=z`) — die `z`-Randverteilung allein ist exakt
  geschlossen: `closure.is_exact_closure(P, C, Q)` liefert `True`,
  `closure.closure_error(P, C, Q) == 0`.
- **Fall B (m unabhängige verdeckte Münze):** `m` entwickelt sich
  unabhängig von `z` (z.B. fairer Münzwurf pro Schritt) und moduliert
  gleichzeitig die `z`-Übergänge (die Metaregel beeinflusst `F`, §6
  Satz 2: "Dann hängt F gegebenenfalls von m ab") — die `z`-Rand-
  verteilung allein ist NICHT exakt geschlossen:
  `closure.is_exact_closure(...)` liefert `False`,
  `closure.closure_error(...) > 0` (konkrete Zahl aus dem Skriptlauf).

Beide Fälle müssen mit denselben `closure`-Funktionen geprüft werden,
die bereits für e04 (exakte Lumpability)/e05 (nicht geschlossene
Aggregation) verwendet werden — hier explizit als "unbeobachtetes m"
gerahmt, nicht als generisches Lumping-Beispiel.

### 4. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `membership/core.py` oder `closure/core.py` — nur
  Aufruf der bestehenden `joint_control_set`, `is_exact_closure`,
  `closure_error`, `partition_matrix`.
- Kein kontinuierliches/stochastisches Metaregel-Update — nur die
  diskrete Form aus §6.
- Keine allgemeine Theorie verdeckter Markov-Aggregation — nur das
  eine konkrete Gegenbeispielpaar oben.
- Keine Mutation von `context_transformations.md` oder einem der
  anderen sieben Kerndokumente.

## Verifikation

`verify_metarules_core.py`: keine bestehende Legacy-Prüfung für
Metaregeln (wie schon bei `membership`, M4) — frische, von Hand
nachrechenbare Beispiele. Mindestens: (1) Prioritätsregel bei leerem
Rohschnitt liefert nichtleere Eingriffsmenge und benennt die
aufgegebene Anforderung, (2) Fall A `closure_error==0`, (3) Fall B
`closure_error>0` mit konkreter Zahl, (4) Kreuzprobe, dass
`priority_joint_control_set` bei NICHT-leerem Rohschnitt identisch zu
`membership.joint_control_set` bleibt (Metaregel greift nur im
Konfliktfall).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_metarules_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf `context_transformations.md` §6 — jede neue
   Funktion referenziert ihre Herkunftsstelle (Satz-genau, wo möglich).
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m9-metarules` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Claude
reviewed (Diff, Skript selbst nachrechnen, mindestens einen Fall von
Hand gegenprüfen) und merged erst nach Johanns OK.
