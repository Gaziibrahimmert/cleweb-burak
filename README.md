# praxis-arkan.de

Website der Praxis für Soziotherapie Burak Arkan, Gelsenkirchen (DE / TR / EN).

- Statisches HTML in `de/`, `tr/`, `en/` – keine Abhängigkeiten, kein Framework.
- Texte: `_build/content_de.py`, `content_tr.py`, `content_en.py`
- Layout: `_build/build.py` → nach Änderungen `python _build/build.py` ausführen und die generierten Dateien committen.
- Hosting: Vercel (Framework Preset „Other“, kein Build Command, Output Directory = Projektwurzel). Domain bei IONOS, DNS auf Vercel zeigen lassen.
- Gelb markierte Stellen (`class="todo"`) sind noch fehlende Angaben.

## Kontaktformular

Das Formular auf der Kontaktseite sendet an die Vercel-Funktion `api/contact.js`, die die Nachricht per SMTP als E-Mail weiterleitet (Antwort-an = Absender).
In Vercel unter *Settings → Environment Variables* setzen:

| Variable | Beispiel (Gmail) |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | `arkanburak@gmail.com` |
| `SMTP_PASS` | App-Passwort des Kontos (nicht das normale Passwort) |
| `MAIL_TO` | `arkanburak@gmail.com` (optional, Standard) |

Danach einmal neu deployen. Ohne diese Variablen zeigt das Formular eine Fehlermeldung mit Telefonnummer.
