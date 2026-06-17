# Nutzen eines offiziellen Python-Images.
FROM python:3.12

# Arbeitsverzeichnis im Container wechseln 
WORKDIR /app

# Abhängigkeiten zuerst kopieren und installieren (nutzt Docker-Layer-Cache)
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Kopiere lokale Datei in den Container
COPY app.py /app

# Flask läuft standardmäßig auf Port 5000. Zeige Docker, dass dieser Port genutzt wird.
EXPOSE 5000

# Der Befehl, der ausgeführt wird, wenn der Container startet
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]