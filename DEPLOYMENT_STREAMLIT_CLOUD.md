# Deployment auf Streamlit Community Cloud

Diese Anleitung beschreibt den empfohlenen Weg, das Marketing-Dashboard auf Streamlit Community Cloud zu veroeffentlichen.

## 1. GitHub-Repository vorbereiten

Streamlit Community Cloud deployt direkt aus GitHub.

Empfohlen:

- privates GitHub-Repository erstellen
- Projektdateien hochladen
- keine Exceldateien ins Repository laden

Die Exceldateien in `data/input/` werden durch `.gitignore` ausgeschlossen. Das ist wichtig, damit interne Kennzahlen und Budgetdaten nicht versehentlich veroeffentlicht werden.

## 2. Dateien, die im Repository vorhanden sein muessen

Pflicht:

- `src/app.py`
- `src/`
- `requirements.txt`
- `.streamlit/config.toml`
- `README.md`

Nicht hochladen:

- `.venv/`
- `.env`
- `.streamlit/secrets.toml`
- Exceldateien mit echten Unternehmensdaten

## 3. Streamlit Cloud App erstellen

1. `https://share.streamlit.io/` oeffnen.
2. Mit GitHub anmelden.
3. `Create app` auswaehlen.
4. Repository auswaehlen.
5. Branch auswaehlen, meist `main`.
6. Main file path setzen:

```text
src/app.py
```

## 4. Passwort als Secret setzen

In den Advanced settings bzw. App settings unter Secrets eintragen:

```toml
DASHBOARD_PASSWORD = "hier-ein-sicheres-passwort-eintragen"
```

Das Passwort nicht in den Code, nicht in `.env` und nicht in GitHub speichern.

## 5. App starten

Nach `Deploy` installiert Streamlit Cloud die Pakete aus `requirements.txt` und startet `src/app.py`.

Beim ersten Oeffnen:

1. Passwort eingeben.
2. Links unter `Datenquellen` die beiden Exceldateien hochladen:
   - woechentliche Kennzahlen
   - Budgetbericht
3. Dashboard pruefen.

## 6. Aktualisieren der Daten

Neue Daten werden nicht automatisch gespeichert. Fuer eine neue Auswertung:

1. App oeffnen.
2. Passwort eingeben.
3. neue Exceldateien hochladen.

Wenn dauerhaft gespeicherte Uploads gewuenscht sind, braucht das Dashboard spaeter einen externen Speicher, zum Beispiel Google Drive, SharePoint, OneDrive API, S3 oder eine Datenbank.

## 7. Typische Fehler

`ModuleNotFoundError`:

- Paket fehlt in `requirements.txt`.

`File not found`:

- Exceldateien wurden nicht hochgeladen.
- Das ist auf Streamlit Cloud normal, wenn keine Beispieldateien im Repository liegen.

Passwortmaske erscheint nicht:

- `DASHBOARD_PASSWORD` ist nicht als Secret gesetzt.

App startet, aber Daten fehlen:

- Beide Exceldateien links hochladen.
- Tabellenblattnamen muessen zur erwarteten Struktur passen.
