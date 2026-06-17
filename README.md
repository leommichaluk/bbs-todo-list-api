# Todo-Listen REST-API

Eine einfache REST-API zur Verwaltung von Todo-Listen und deren Einträgen. Die API ist mit Flask implementiert und speichert Daten im Arbeitsspeicher (keine persistente Datenbank — nach einem Neustart sind die Daten weg).

> Diese README dient zugleich als **Dokumentation des kompletten Deployments** auf einem Raspberry-Pi-Linux-Server: jeder Schritt ist kurz erklärt, nicht nur aufgelistet.

## Inhaltsverzeichnis

- [Funktionen](#funktionen)
- [Endpunkte](#endpunkte)
- [Projektstruktur](#projektstruktur)
- [Lokal ausführen](#lokal-ausführen)
- [Live-Demo (Frontend)](#live-demo-frontend)
- [Deployment auf Raspberry Pi](#deployment-auf-raspberry-pi)
  - [1. Statische IP-Adresse](#1-statische-ip-adresse)
  - [2. Benutzer & SSH](#2-benutzer--ssh)
  - [3. Docker & Anwendung](#3-docker--anwendung)

## Funktionen

- Todo-Listen anlegen, abrufen und löschen
- Einträge zu einer Liste hinzufügen, bearbeiten und löschen
- CORS-Unterstützung für die Frontend-Anbindung

## Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| `GET` | `/todo-list` | Alle Todo-Listen abrufen |
| `POST` | `/todo-list` | Neue Todo-Liste anlegen |
| `GET` | `/todo-list/{list_id}` | Einträge einer Liste abrufen |
| `POST` | `/todo-list/{list_id}` | Eintrag zu einer Liste hinzufügen |
| `DELETE` | `/todo-list/{list_id}` | Todo-Liste (inkl. Einträge) löschen |
| `PATCH` | `/entry/{entry_id}` | Eintrag bearbeiten |
| `DELETE` | `/entry/{entry_id}` | Eintrag löschen |

Die vollständige API-Spezifikation liegt in `Todolistenverwaltung.yaml` (OpenAPI 3.0).

## Projektstruktur

Übersicht der wichtigsten Dateien des Projekts:

| Datei | Beschreibung |
|-------|--------------|
| `app.py` | Kern der Anwendung: die komplette Flask-REST-API (Routen, Logik, CORS, Fehlerbehandlung). Daten liegen im Arbeitsspeicher. |
| `requirements.txt` | Python-Abhängigkeiten (Flask). |
| `Dockerfile` | Bauanleitung für das Container-Image (Python-Basis-Image, Installation, Port 5000, Startbefehl). Wird beim Pi-Deployment verwendet. |
| `Todolistenverwaltung.yaml` | OpenAPI-3.0-Spezifikation der API — beschreibt alle Endpunkte, Parameter und Antwort-Schemata. |
| `.gitignore` | Legt fest, welche Dateien/Ordner (z. B. `venv/`, `__pycache__/`) nicht ins Git-Repository aufgenommen werden. |
| `README.md` | Diese Datei: Projektbeschreibung und Deployment-Dokumentation. |

---

## Lokal ausführen

### Voraussetzungen

- Python 3.x

### Installation & Start

```bash
pip install -r requirements.txt
python app.py
```

Der Server läuft anschließend unter `http://127.0.0.1:5000`.

---

## Live-Demo (Frontend)

Zur API existiert ein passendes Web-Frontend, das auf [Vercel](https://vercel.com) gehostet wird:

**→ Live: [bbs-todo-list-frontend.vercel.app](https://bbs-todo-list-frontend.vercel.app)**
**→ Quellcode: [github.com/leommichaluk/bbs-todo-list-frontend](https://github.com/leommichaluk/bbs-todo-list-frontend)** (Nuxt / Vue)

Über die Oberfläche lassen sich Listen und Einträge anlegen, bearbeiten und löschen — alle Aktionen laufen über die hier beschriebenen Endpunkte. So kann die Funktionstüchtigkeit der API bequem im Browser getestet werden, ohne selbst HTTP-Anfragen (z. B. per `curl`) absetzen zu müssen.

**Voraussetzung:** Das Frontend hat kein eigenes Backend. Die API muss daher beim Nutzer **lokal oder im selben Netzwerk** laufen (siehe [Lokal ausführen](#lokal-ausführen) bzw. [Deployment auf Raspberry Pi](#deployment-auf-raspberry-pi)). Im Frontend muss anschließend die **IP-Adresse angegeben werden, unter der die API vom Client (Browser) aus erreichbar ist** — z. B. `http://127.0.0.1:5000` bei lokalem Betrieb oder `http://192.168.x.x:5000` für eine Instanz im Netzwerk.

> Hinweis: Da die API ihre Daten nur im Arbeitsspeicher hält, sind die im Frontend erstellten Daten nicht dauerhaft gespeichert.

---

## Deployment auf Raspberry Pi

Diese Anleitung beschreibt das Aufsetzen eines Raspberry Pi als Linux-Server und das Deployment der API per Docker. Die Schritte wurden in folgender Reihenfolge ausgeführt.

### Übersicht

1. Statische IP-Adresse konfigurieren
2. Benutzer anlegen und SSH absichern
3. Docker installieren und Anwendung starten

---

### 1. Statische IP-Adresse

Eine feste IP sorgt dafür, dass der Pi im Netzwerk immer unter derselben Adresse erreichbar ist.

Zuerst per SSH verbinden — `192.168.x.x` ist die **aktuelle IP** des Pi:

```bash
ssh pi@192.168.x.x
```

Verbindungsname der Netzwerkschnittstelle ermitteln:

```bash
nmcli con show
```

Den angezeigten Namen (z. B. `Wired connection 1`) in `[name]` einsetzen und statische IP konfigurieren:

- `192.168.x.x/24` — gewünschte feste IP mit Subnetz (`/24` = 255.255.255.0)
- `192.168.x.1` — Router / Standard-Gateway
- `192.168.x.2` — DNS-Server (Router-IP als Fallback möglich)
- `local.domain` — lokale Suchdomäne (optional, anpassen)

```bash
sudo nmcli connection modify [name] \
  ipv4.method manual \
  ipv4.addresses 192.168.x.x/24 \
  ipv4.gateway 192.168.x.1 \
  ipv4.dns "192.168.x.2 192.168.x.1" \
  ipv4.dns-search "local.domain" \
  ipv6.method disabled \
  connection.autoconnect yes

sudo nmcli connection down [name]
sudo nmcli connection up [name]
```

Pi neu starten, danach unter der **neu vergebenen statischen IP** erreichbar:

```bash
ssh pi@192.168.x.x
```

---

### 2. Benutzer & SSH

Ziel: nicht mit dem Standard-Benutzer arbeiten, sondern einen dedizierten Fernzugriffs-Benutzer nutzen und SSH absichern.

#### Benutzer anlegen

Lokalen Benutzer `Willi` und dedizierten SSH-Benutzer `fernzugriff` anlegen — letzterer erhält sudo-Rechte:

```bash
sudo adduser Willi
sudo adduser fernzugriff
sudo usermod -aG sudo fernzugriff
```

Für jeden Benutzer ein Passwort vergeben, wenn danach gefragt wird.

#### SSH-Dienst aktivieren

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

#### SSH absichern

Konfiguration bearbeiten:

```bash
sudo nano /etc/ssh/sshd_config
```

Folgende Werte setzen bzw. anpassen:

```
PermitRootLogin no          # Root-Login per SSH verbieten
PasswordAuthentication yes  # Login per Passwort erlauben
AllowUsers fernzugriff      # nur dieser Benutzer darf sich per SSH verbinden
```

SSH-Dienst neu laden, damit die Änderungen greifen:

```bash
sudo systemctl restart ssh
```

Ab jetzt nur noch mit dem dedizierten Benutzer verbinden — `192.168.x.x` = statische Pi-IP aus Schritt 1:

```bash
ssh fernzugriff@192.168.x.x
```

---

### 3. Docker & Anwendung

Die API wird in einem Docker-Container betrieben. Das hält die Umgebung sauber und macht das Deployment reproduzierbar.

#### Systemzeit setzen

Falls die Uhrzeit nicht stimmt (wichtig für `apt` und Zertifikate):
Format: 'YYYY-MM-DD HH:MM:SS' Zum Beispiel: '2026-06-17 12:58:00'


```bash
sudo date --set='20XX-XX-XX XX:XX:XX' 
```

Datum und Uhrzeit durch den aktuellen Wert ersetzen.

#### Docker installieren

```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker.service
sudo docker run hello-world
```

Wenn `hello-world` erfolgreich läuft, ist Docker einsatzbereit.

#### Repository klonen und Image bauen

Zuerst prüfen, ob Git installiert ist, und es bei Bedarf nachinstallieren:

```bash
# Prüft, ob git vorhanden ist – falls nicht, wird es installiert
git --version || sudo apt install -y git
```

Das Image wird anhand des `Dockerfile` aus dem Repository gebaut:

```bash
sudo git clone https://github.com/leommichaluk/bbs-todo-list-api.git
cd bbs-todo-list-api/
sudo docker image build -t app .
sudo docker images
```

Erwartete Ausgabe von `docker images`:

```
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
app          latest    ...            ...              ...
```

#### Container starten

`-p 5000:5000` mappt Port 5000 des Pi auf den Container, `-d` startet im Hintergrund:

```bash
sudo docker run -p 5000:5000 -d app
```

Die API ist danach im Netzwerk unter `http://192.168.x.x:5000` erreichbar (`192.168.x.x` = Pi-IP).

#### Nützliche Docker-Befehle

```bash
# Laufende Container anzeigen
sudo docker ps

# Logs anzeigen
sudo docker logs <container-id>

# Container stoppen
sudo docker stop <container-id>
```
