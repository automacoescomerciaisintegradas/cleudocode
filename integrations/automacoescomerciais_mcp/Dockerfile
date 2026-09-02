FROM python:3.11-slim

WORKDIR /app

# Cria diretório de dados para persistência de leads
RUN mkdir -p /app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expõe a porta do Health Check
EXPOSE 65000

CMD ["python", "server.py"]
