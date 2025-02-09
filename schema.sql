-- Tablica za kategorije proizvoda (npr. torte, kolači, peciva)
CREATE TABLE IF NOT EXISTS kategorije (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(255) NOT NULL
);

-- Tablica za proizvode
CREATE TABLE IF NOT EXISTS proizvodi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(255) NOT NULL,
    opis TEXT,
    cijena DECIMAL(10,2) NOT NULL,
    kategorija_id INT,
    FOREIGN KEY (kategorija_id) REFERENCES kategorije(id) ON DELETE SET NULL
);

-- Tablica za kupce
CREATE TABLE IF NOT EXISTS kupci (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ime VARCHAR(255) NOT NULL,
    prezime VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- Tablica za narudžbe
CREATE TABLE IF NOT EXISTS narudzbe (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kupac_id INT NOT NULL,
    datum_narudzbe DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (kupac_id) REFERENCES kupci(id) ON DELETE CASCADE
);

-- Tablica za stavke narudžbe (poveznica između narudžbi i proizvoda)
CREATE TABLE IF NOT EXISTS narudzba_proizvodi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    narudzba_id INT NOT NULL,
    proizvod_id INT NOT NULL,
    kolicina INT NOT NULL,
    FOREIGN KEY (narudzba_id) REFERENCES narudzbe(id) ON DELETE CASCADE,
    FOREIGN KEY (proizvod_id) REFERENCES proizvodi(id) ON DELETE CASCADE
);
