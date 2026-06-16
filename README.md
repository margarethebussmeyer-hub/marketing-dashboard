# Marketing-Dashboard

Streamlit-Dashboard fuer die Marketingabteilung auf Basis zweier Exceldateien:

- `data/input/Kennzahlen-Marketing.xlsx`
- `data/input/2026_2025_Marketing_Budget.xlsx`

Das Dashboard priorisiert die wichtigsten Steuerungskennzahlen:

- Budget geplant, verwendet und verfuegbar
- Neukundengewinnung
- Social-Media-Reichweite, Interaktionen und Engagement-Rate
- Gutschein- und Rabattcode-Nutzungen
- Newsletter-, App- und Google-Bewertungsdaten

## Python-Version

Empfohlen: Python 3.11 oder neuer.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Start

```powershell
streamlit run src/app.py
```

Beim Start verwendet das Dashboard die Dateien aus `data/input/`. In der linken Navigation koennen alternativ aktuelle Exceldateien hochgeladen werden:

- Woechentliche Kennzahlen
- Budgetbericht

Nach dem Upload aktualisiert Streamlit das Dashboard automatisch mit den hochgeladenen Daten.

## Erwartete Tabellenblaetter

`Kennzahlen-Marketing.xlsx`:

- `Neukundengewinnung`
- `Kundenbindung`
- `App`
- `Newsletter`
- `Kundenzufriedenheit`
- `Social Media-GG`
- `Social Media-WH`

`2026_2025_Marketing_Budget.xlsx`:

- `GGBE_2026_Jahresbudget`
- `WH_2026_Jahresbudget`
- `2025_Jahresbudget`
- optional: `GGBE_Buchungsliste`
- optional: `WH_Buchungsliste`

## Annahmen

- `WH` bedeutet `Weidenhof`.
- `GG` und `GGBE` bedeuten `Gemüsegärtner`.
- Leere Werte, `/` und vergleichbare Platzhalter werden bei numerischen Kennzahlen nicht mitgerechnet.
- Das Blatt `Kundenzufriedenheit` enthaelt keine Unternehmensspalte. Aktuell wird anhand der Gesamtanzahl Bewertungen unterschieden: kleinere Bewertungsbasis = Weidenhof, groessere Bewertungsbasis = Gemüsegärtner.
- Budgetwerte werden aus den Jahresbudget-Blaettern gelesen; Buchungslisten dienen fuer Detailauswertungen wie groesste Lieferanten.

## Tests

```powershell
pytest
```

## Passwortschutz

Das Dashboard ist passwortgeschuetzt, sobald die Umgebungsvariable `DASHBOARD_PASSWORD` gesetzt ist.
Das Passwort wird nicht in den Code geschrieben.

Lokal in PowerShell:

```powershell
$env:DASHBOARD_PASSWORD="ein-sicheres-passwort"
streamlit run src/app.py
```

In einem Hosting-Dienst wird `DASHBOARD_PASSWORD` als Secret bzw. Environment Variable hinterlegt.

## Hosting-Hinweis

Dieses Projekt ist eine Streamlit-App. Streamlit benoetigt einen dauerhaft laufenden Python-Webserver und ist daher nicht sinnvoll als Vercel Serverless Function deploybar. Vercel eignet sich fuer statische Frontends, Next.js und Python APIs, aber nicht als direkter Host fuer diese Streamlit-Oberflaeche.

Empfohlene Hosting-Ziele fuer diese App:

- Streamlit Community Cloud
- Render
- Railway
- Google Cloud Run

Wenn Vercel zwingend verwendet werden soll, ist die stabile Architektur:

- Streamlit-Dashboard auf Render/Railway/Cloud Run hosten
- optional eine Vercel-Seite als passwortgeschuetzten Einstieg oder Weiterleitung verwenden
- produktiven Zugriff ueber `DASHBOARD_PASSWORD` oder Hosting-Provider-Auth absichern

## Struktur

```text
data/input/                 Excel-Eingabedateien
data/output/                Ausgaben, nicht versioniert
src/app.py                  Streamlit-Oberflaeche
src/config.py               Pfade, Marken-Mapping und Konstanten
src/data_loader.py          Excel-Import und Normalisierung
src/data_processing.py      Filter, Rabattcode- und Detailaufbereitung
src/metrics.py              KPI- und Aggregationslogik
src/charts.py               Plotly-Diagramme
src/styles.py               Dashboard-CSS
tests/                      pytest-Tests
```
