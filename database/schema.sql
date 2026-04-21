-- Quiz schema v2: preguntas + opciones; jugadores únicos por nombre (mejor puntaje).
-- Migración desde v1: ver database/db.py (preserva datos).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS preguntas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enunciado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS opciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pregunta_id INTEGER NOT NULL,
    letra TEXT NOT NULL,
    texto TEXT NOT NULL,
    es_correcta INTEGER NOT NULL,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
    CHECK (letra IN ('A', 'B', 'C', 'D')),
    CHECK (es_correcta IN (0, 1)),
    UNIQUE (pregunta_id, letra)
);

CREATE INDEX IF NOT EXISTS idx_opciones_pregunta_id ON opciones(pregunta_id);

CREATE TABLE IF NOT EXISTS jugadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL COLLATE NOCASE UNIQUE,
    puntaje INTEGER NOT NULL DEFAULT 0 CHECK (puntaje >= 0)
);

<<<<<<< HEAD
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
=======
CREATE INDEX IF NOT EXISTS idx_jugadores_puntaje ON jugadores(puntaje);

CREATE TABLE IF NOT EXISTS partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jugador_id INTEGER NOT NULL,
    fecha TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    puntaje INTEGER NOT NULL DEFAULT 0 CHECK (puntaje >= 0),
    FOREIGN KEY (jugador_id) REFERENCES jugadores(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_partidas_jugador_id ON partidas(jugador_id);

CREATE TABLE IF NOT EXISTS respuestas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id INTEGER NOT NULL,
    pregunta_id INTEGER NOT NULL,
    opcion_id INTEGER NOT NULL,
    es_correcta INTEGER NOT NULL CHECK (es_correcta IN (0, 1)),
    FOREIGN KEY (partida_id) REFERENCES partidas(id) ON DELETE CASCADE,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
    FOREIGN KEY (opcion_id) REFERENCES opciones(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_respuestas_partida_id ON respuestas(partida_id);
CREATE INDEX IF NOT EXISTS idx_respuestas_pregunta_id ON respuestas(pregunta_id);

PRAGMA user_version = 3;
>>>>>>> 8f6f8f0b41e56e91cd86d4b5e2a808d3a8b5adea
