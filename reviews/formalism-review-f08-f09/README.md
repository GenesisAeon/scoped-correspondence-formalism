# Review-Paket: F08/F09 und nächste Erweiterungen

16. September 2026.

- [Review mit Quellen und Befunden](REVIEW_F08_F09_UND_GEMINI.md)
- [Konkrete Erweiterung: ausführbare Transformationen und offene Systeme](NEXT_EXTENSIONS_ACTION_AND_OPEN_SYSTEMS.md)
- [Unabhängige mathematische Prüfungen](verification/verify_review_examples.py)
- [Dokumentierter Lauf: 11/11](verification/review_results.json)

Die hochgeladenen Originale werden durch dieses Paket nicht ersetzt. Die tatsächlichen F08/F09-Moduldateien fehlen im verfügbaren Bestand. Die beigefügten Prüfungen sind unabhängig und bestätigen nicht deren Code oder die berichteten Projektläufe.

## Ausführen

~~~bash
python -m pip install -r verification/requirements_review.txt
python verification/verify_review_examples.py
~~~

Python 3.12.14, NumPy 2.3.5 und SciPy 1.17.0 wurden für den gespeicherten Lauf verwendet. Das Skript schreibt review_results.json in seinen eigenen Ordner. Der Zeitstempel ändert sich bei erneuter Ausführung.

manifest_review.json nennt die Eingangsdateien mit SHA-256 und die Dateien dieses Pakets. Es ist ein Inhaltsverzeichnis mit Prüfsummen, kein Installations- oder Apply-Manifest. Die Eingangsdateien werden nicht in dieses Paket kopiert.
