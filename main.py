from fastapi import FastAPI, HTTPException
import mysql.connector
from models import Proizvod, Kategorija
import os
import redis
import json

app = FastAPI()

def dohvati_konekciju():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "mysql"),
        user=os.environ.get("MYSQL_USER", "slasticarnicauser"),
        password=os.environ.get("MYSQL_PASSWORD", "pass"),
        database=os.environ.get("MYSQL_DATABASE", "slasticarnica")
    )

# Inicijalizacija Redis konekcije
redis_host = os.environ.get("REDIS_HOST", "redis")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Endpoint za dohvat svih proizvoda (s Redis cache-om)
@app.get("/proizvodi")
def dohvati_proizvode():
    cache_key = "proizvodi_all"
    cached_proizvodi = redis_client.get(cache_key)
    if cached_proizvodi:
        return json.loads(cached_proizvodi)

    veza = dohvati_konekciju()
    cursor = veza.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proizvodi")
    proizvodi = cursor.fetchall()
    cursor.close()
    veza.close()

    # Spremi rezultat u Redis cache
    redis_client.set(cache_key, json.dumps(proizvodi))
    return proizvodi

# Dohvati jedan proizvod po id-u
@app.get("/proizvodi/{id}")
def dohvati_proizvod(id: int):
    veza = dohvati_konekciju()
    cursor = veza.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proizvodi WHERE id = %s", (id,))
    proizvod = cursor.fetchone()
    cursor.close()
    veza.close()
    if proizvod:
        return proizvod
    raise HTTPException(status_code=404, detail="Proizvod nije pronađen")

# Kreiraj novi proizvod
@app.post("/proizvodi", status_code=201)
def kreiraj_proizvod(proizvod: Proizvod):
    veza = dohvati_konekciju()
    cursor = veza.cursor()
    query = "INSERT INTO proizvodi (naziv, opis, cijena, kategorija_id) VALUES (%s, %s, %s, %s)"
    values = (proizvod.naziv, proizvod.opis, proizvod.cijena, proizvod.kategorija_id)
    cursor.execute(query, values)
    veza.commit()
    novi_id = cursor.lastrowid
    cursor.close()
    veza.close()

    # Invalidate cache
    redis_client.delete("proizvodi_all")
    return {"id": novi_id, **proizvod.dict()}

@app.post("/kategorije", status_code=201)
def kreiraj_kategoriju(kategorija: Kategorija):
    veza = dohvati_konekciju()
    cursor = veza.cursor()
    query = "INSERT INTO kategorije (naziv) VALUES (%s)"
    values = (kategorija.naziv,)
    cursor.execute(query, values)
    veza.commit()
    novi_id = cursor.lastrowid
    cursor.close()
    veza.close()

    # Invalidate cache
    redis_client.delete("kategorije_all")
    return {"id": novi_id, **kategorija.dict()}

# Ažuriraj postojeći proizvod
@app.put("/proizvodi/{id}")
def azuriraj_proizvod(id: int, proizvod: Proizvod):
    veza = dohvati_konekciju()
    cursor = veza.cursor()
    query = "UPDATE proizvodi SET naziv = %s, opis = %s, cijena = %s, kategorija_id = %s WHERE id = %s"
    values = (proizvod.naziv, proizvod.opis, proizvod.cijena, proizvod.kategorija_id, id)
    cursor.execute(query, values)
    veza.commit()
    if cursor.rowcount == 0:
        cursor.close()
        veza.close()
        raise HTTPException(status_code=404, detail="Proizvod nije pronađen")
    cursor.close()
    veza.close()

    # Invalidate cache
    redis_client.delete("proizvodi_all")
    return {"id": id, **proizvod.dict()}

# Obriši proizvod
@app.delete("/proizvodi/{id}")
def obrisi_proizvod(id: int):
    veza = dohvati_konekciju()
    cursor = veza.cursor()
    cursor.execute("DELETE FROM proizvodi WHERE id = %s", (id,))
    veza.commit()
    if cursor.rowcount == 0:
        cursor.close()
        veza.close()
        raise HTTPException(status_code=404, detail="Proizvod nije pronađen")
    cursor.close()
    veza.close()

    # Invalidate cache
    redis_client.delete("proizvodi_all")
    return {"poruka": "Proizvod uspješno obrisan"}
