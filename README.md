# Todo-Listen REST-API

Eine einfache REST-API zur Verwaltung von Todo-Listen und deren Einträgen. Die API ist mit Flask implementiert und speichert Daten im Arbeitsspeicher (keine persistente Datenbank).

## Funktionen

- Todo-Listen anlegen, abrufen und löschen
- Einträge zu einer Liste hinzufügen, bearbeiten und löschen
- CORS-Unterstützung für Frontend-Anbindung

## Voraussetzungen

- Python 3.x

## Installation & Start

```bash
pip install -r requirements.txt
python app.py
```

Der Server läuft anschließend unter `http://127.0.0.1:5000`.

## Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| `GET` | `/todo-list` | Alle Todo-Listen abrufen |
| `POST` | `/todo-list` | Neue Todo-Liste anlegen |
| `GET` | `/todo-list/{list_id}` | Einträge einer Liste abrufen |
| `POST` | `/todo-list/{list_id}` | Eintrag zu einer Liste hinzufügen |
| `DELETE` | `/todo-list/{list_id}` | Todo-Liste löschen |
| `PATCH` | `/entry/{entry_id}` | Eintrag bearbeiten |
| `DELETE` | `/entry/{entry_id}` | Eintrag löschen |

Die vollständige API-Spezifikation liegt in `Todolistenverwaltung.yaml` (OpenAPI 3.0).
