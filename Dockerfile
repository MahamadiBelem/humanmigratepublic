# # Utiliser l'image officielle Python 3.11
# FROM python:3.11-slim

# # Définir le répertoire de travail
# WORKDIR /app

# # Mettre à jour pip et setuptools avant d'installer les paquets
# RUN pip install --upgrade pip setuptools

# # Installer les dépendances système nécessaires (pour Pillow, folium, etc.)
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libglib2.0-0 \
#     libsm6 \
#     libxrender1 \
#     libxext6 \
#     && rm -rf /var/lib/apt/lists/* \
#     && echo "System dependencies installed successfully"

# # Copier les fichiers de l'application dans le conteneur
# COPY . /app

# # Copier le fichier requirements.txt dans le conteneur
# COPY requirements.txt /app/requirements.txt

# # Installer les dépendances Python avec des logs détaillés
# RUN pip install -v --no-cache-dir -r requirements.txt \
#     && echo "Python dependencies installed successfully"

# # Exposer le port 8501 pour Streamlit
# EXPOSE 8501

# # Lancer l'application Streamlit
# CMD ["streamlit", "run", "app.py"]

# Start from a minimal Python base image
FROM python:3.11-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    wget \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Download and install OpenJDK 11 from AdoptOpenJDK
RUN wget https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.20+8/OpenJDK11U-jdk_x64_linux_hotspot_11.0.20_8.tar.gz -P /tmp/ \
    && tar -xzf /tmp/OpenJDK11U-jdk_x64_linux_hotspot_11.0.20_8.tar.gz -C /usr/local/ \
    && rm /tmp/OpenJDK11U-jdk_x64_linux_hotspot_11.0.20_8.tar.gz

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/local/jdk-11.0.20+8
ENV PATH=$JAVA_HOME/bin:$PATH

# Set working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for Streamlit
EXPOSE 8501

# Command to run your Streamlit app
CMD ["streamlit", "run", "app.py"]
