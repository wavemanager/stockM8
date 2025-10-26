# 1. Start mit einem offiziellen, schlanken Python-Image
FROM python:3.10-slim

# 2. Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# 3. Kopiere die Abhängigkeitsliste in den Container
COPY requirements.txt .

# 4. Installiere alle benötigten Pakete
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kopiere den gesamten restlichen Code in den Container
COPY . .

# 6. Der Befehl, der beim Starten des Containers ausgeführt wird
CMD ["python", "agent_1.py"]