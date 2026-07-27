FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Meshtastic Météo Bot"
LABEL description="Bot Meshtastic de diffusion météo et alertes officielles françaises"
LABEL version="1.0.0"

# Répertoire de travail
WORKDIR /app

# Dépendances système (nécessaires pour certains packages Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances en premier (optimisation du cache Docker)
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer le répertoire de logs
RUN mkdir -p logs

# Variables d'environnement par défaut
ENV MESHTASTIC_CONNECTION_TYPE=tcp
ENV MESHTASTIC_TCP_HOST=meshtastic-node
ENV DEFAULT_DEPARTMENT=75
ENV DEFAULT_LATITUDE=48.8566
ENV DEFAULT_LONGITUDE=2.3522
ENV BROADCAST_CHANNEL=0
ENV ALERT_CHANNEL=0
ENV METEO_BROADCAST_INTERVAL=360
ENV ALERT_CHECK_INTERVAL=15
ENV ALERT_REPORT_INTERVAL=60
ENV ALERT_TRIGGER_LEVEL=3
ENV LOG_LEVEL=INFO
ENV LOG_FILE=logs/bot.log

# Exposer un volume pour les logs
VOLUME ["/app/logs"]

# Commande de démarrage
CMD ["python", "main.py"]
