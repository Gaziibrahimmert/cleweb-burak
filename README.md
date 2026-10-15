# praxis-arkan.de

Website der Praxis für Soziotherapie Burak Arkan, Gelsenkirchen (DE / TR / EN).

- Statisches HTML in `de/`, `tr/`, `en/` – keine Abhängigkeiten, kein Framework.
- Texte: `_build/content_de.py`, `content_tr.py`, `content_en.py`
- Layout: `_build/build.py` → nach Änderungen `python _build/build.py` ausführen und die generierten Dateien committen.
- Hosting: Vercel (Framework Preset „Other“, kein Build Command, Output Directory = Projektwurzel). Domain bei IONOS, DNS auf Vercel zeigen lassen.
- Gelb markierte Stellen (`class="todo"`) sind noch fehlende Angaben.
