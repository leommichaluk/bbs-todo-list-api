# Nutzen eines offiziellen Python-Images.
FROM python:3.12

# Installiere die Python-Abhängigkeiten
RUN pip install flask

# Arbeitsverzeichnis im Container wechseln 
WORKDIR /app

# Kopiere lokale Datei in den Container
COPY app.py /app

# Flask läuft standardmäßig auf Port 5000. Zeige Docker, dass dieser Port genutzt wird.
EXPOSE 5000

# Der Befehl, der ausgeführt wird, wenn der Container startet
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]