# Aktuelle Verifikation — Revision 3

Im Hauptverzeichnis dieses Dokumentbestands ausführen:

```bash
python -m pip install -r verification/requirements.txt
python verification/verify_extensions.py
python verification/verify_formalism.py
```

`verify_formalism.py` ist der unveränderte mathematische Prüfkern aus Revision 2 mit 19 Prüfungen. `verify_extensions.py` ergänzt 16 Prüfungen und benötigt NumPy; die ausgeführte Version steht im Ergebnisbericht. Zuerst die Erweiterungen ausführen, damit deren neu erzeugter Bericht beim übergreifenden Linktest bereits existiert.

- [Basis-Laufbericht](verification_results.json)
- [Erweiterungs-Laufbericht](extension_results.json)
- [Aussagekraft und Details](../VERIFICATION.md)

Die Skripte prüfen synthetische Modellrechnungen und Dokumentverweise. Sie reproduzieren keine vollständige Literaturstudie und führen keine Produktionspaket-Tests aus.

Johann meldete, dass ein älteres `cusp_model_numerical_check.py` samt README beim lokalen Anwenden nach `archive/2026-09-15/verification/` verschoben wurde. Dieser ältere Code wurde hier nicht bereitgestellt und ist nicht Bestandteil der aktuellen Tests. Seine überlieferte Bestätigung von `a=-S(Theta)` wird nicht als gültiger Nachweis übernommen. Die unveränderte Revision-2-Suite steht zusätzlich im Archiv dieser Revision.
