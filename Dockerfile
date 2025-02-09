FROM python:3.10-slim

WORKDIR /app

# Kopiraj i instaliraj potrebne pakete
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiraj ostatak koda
COPY . .

# Pokretanje aplikacije
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
