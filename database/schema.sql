-- Quiz application schema (SQLite)

CREATE TABLE IF NOT EXISTS preguntas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enunciado TEXT NOT NULL,
    opcion_a TEXT NOT NULL,
    opcion_b TEXT NOT NULL,
    opcion_c TEXT NOT NULL,
    opcion_d TEXT NOT NULL,
    respuesta_correcta TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jugadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    puntaje INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
