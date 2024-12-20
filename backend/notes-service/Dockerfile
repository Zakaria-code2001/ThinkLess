FROM python:3.10-slim

# Installa Node.js per supportare pacchetti Azure (ma senza Tools completi)
RUN apt-get update && apt-get install -y nodejs npm curl

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file del progetto
COPY . /app

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Esponi la porta 7071
EXPOSE 7071

# Comando placeholder per il backend
CMD ["python", "function_app.py"]

