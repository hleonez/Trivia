"""SQLite access layer (no ORM). Schema v2 with opciones + jugadores únicos."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class DatabaseManager:
    """Thin wrapper around sqlite3 for preguntas, opciones, jugadores y partidas."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        base = Path(__file__).resolve().parent
        self.db_path = Path(db_path) if db_path else base / "quiz.db"
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    @property
    def connection(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._conn

    def _table_exists(self, name: str) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (name,),
        ).fetchone()
        return row is not None

    def _table_has_column(self, table: str, column: str) -> bool:
        if not self._table_exists(table):
            return False
        cur = self.connection.execute(f"PRAGMA table_info({table})")
        return any(str(r[1]) == column for r in cur.fetchall())

    def _run_new_schema_sql(self) -> None:
        schema_file = Path(__file__).resolve().parent / "schema.sql"
        sql = schema_file.read_text(encoding="utf-8")
        self.connection.executescript(sql)
        self.connection.commit()
        
        # Initialize default admin if no users exist
        cur = self.connection.execute("SELECT COUNT(*) FROM usuarios")
        if cur.fetchone()[0] == 0:
            import hashlib
            default_pass_hash = hashlib.sha256(b"admin").hexdigest()
            self.insert_usuario("admin", default_pass_hash)

    def _migrate_legacy_v1(self) -> None:
        """Convierte preguntas planas + jugadores duplicados al esquema v2 sin borrar datos."""
        c = self.connection
        c.execute("BEGIN")
        try:
            c.execute("DROP TABLE IF EXISTS opciones")
            c.execute("ALTER TABLE preguntas RENAME TO preguntas_legacy")
            c.execute(
                """
                CREATE TABLE preguntas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    enunciado TEXT NOT NULL
                )
                """
            )
            c.execute(
                "INSERT INTO preguntas (id, enunciado) SELECT id, enunciado FROM preguntas_legacy"
            )
            c.execute(
                """
                CREATE TABLE opciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pregunta_id INTEGER NOT NULL,
                    letra TEXT NOT NULL,
                    texto TEXT NOT NULL,
                    es_correcta INTEGER NOT NULL,
                    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
                    CHECK (letra IN ('A', 'B', 'C', 'D')),
                    CHECK (es_correcta IN (0, 1)),
                    UNIQUE (pregunta_id, letra)
                )
                """
            )
            for letter, col in (
                ("A", "opcion_a"),
                ("B", "opcion_b"),
                ("C", "opcion_c"),
                ("D", "opcion_d"),
            ):
                c.execute(
                    f"""
                    INSERT INTO opciones (pregunta_id, letra, texto, es_correcta)
                    SELECT id, ?, {col},
                        CASE WHEN UPPER(TRIM(COALESCE(respuesta_correcta, ''))) = ? THEN 1 ELSE 0 END
                    FROM preguntas_legacy
                    """,
                    (letter, letter),
                )
            c.execute("DROP TABLE preguntas_legacy")

            if self._table_exists("jugadores"):
                c.execute("ALTER TABLE jugadores RENAME TO jugadores_legacy")
            c.execute(
                """
                CREATE TABLE jugadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    puntaje INTEGER NOT NULL DEFAULT 0 CHECK (puntaje >= 0)
                )
                """
            )
            if self._table_exists("jugadores_legacy"):
                merged: dict[str, tuple[str, int]] = {}
                for row in c.execute(
                    "SELECT nombre, puntaje FROM jugadores_legacy ORDER BY id ASC"
                ):
                    nombre_raw = row["nombre"]
                    puntaje = int(row["puntaje"])
                    key = str(nombre_raw).strip().lower()
                    disp = str(nombre_raw).strip()
                    if not key:
                        continue
                    if key not in merged or puntaje > merged[key][1]:
                        merged[key] = (disp, puntaje)
                c.executemany(
                    "INSERT INTO jugadores (nombre, puntaje) VALUES (?, ?)",
                    list(merged.values()),
                )
                c.execute("DROP TABLE jugadores_legacy")

            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_opciones_pregunta_id ON opciones(pregunta_id)"
            )
            c.execute("CREATE INDEX IF NOT EXISTS idx_jugadores_puntaje ON jugadores(puntaje)")
            c.execute("PRAGMA user_version = 2")
            c.commit()
        except Exception:
            c.rollback()
            raise

    def _ensure_modern_indexes(self) -> None:
        c = self.connection
        c.execute("CREATE INDEX IF NOT EXISTS idx_opciones_pregunta_id ON opciones(pregunta_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_jugadores_puntaje ON jugadores(puntaje)")
        c.commit()

    def _ensure_extended_schema(self) -> None:
        c = self.connection
        if not self._table_exists("partidas"):
            c.execute(
                """
                CREATE TABLE partidas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jugador_id INTEGER NOT NULL,
                    fecha TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                    puntaje INTEGER NOT NULL DEFAULT 0 CHECK (puntaje >= 0),
                    FOREIGN KEY (jugador_id) REFERENCES jugadores(id) ON DELETE CASCADE
                )
                """
            )
        if not self._table_exists("respuestas"):
            c.execute(
                """
                CREATE TABLE respuestas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    partida_id INTEGER NOT NULL,
                    pregunta_id INTEGER NOT NULL,
                    opcion_id INTEGER NOT NULL,
                    es_correcta INTEGER NOT NULL CHECK (es_correcta IN (0, 1)),
                    FOREIGN KEY (partida_id) REFERENCES partidas(id) ON DELETE CASCADE,
                    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
                    FOREIGN KEY (opcion_id) REFERENCES opciones(id) ON DELETE CASCADE
                )
                """
            )
        c.execute("CREATE INDEX IF NOT EXISTS idx_partidas_jugador_id ON partidas(jugador_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_respuestas_partida_id ON respuestas(partida_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_respuestas_pregunta_id ON respuestas(pregunta_id)")
        c.execute("PRAGMA user_version = 3")
        c.commit()

    def create_tables(self) -> None:
        """Crea esquema v3 en BD vacía o migra desde v1/v2 sin perder datos."""
        c = self.connection
        if not self._table_exists("preguntas"):
            self._run_new_schema_sql()
            return
        if self._table_has_column("preguntas", "opcion_a"):
            self._migrate_legacy_v1()
            return
        self._ensure_modern_indexes()
        self._ensure_extended_schema()

    def insert_pregunta(
        self,
        enunciado: str,
        opcion_a: str,
        opcion_b: str,
        opcion_c: str,
        opcion_d: str,
        respuesta_correcta: str,
    ) -> int:
        letter = respuesta_correcta.strip().upper()
        cur = self.connection.execute(
            "INSERT INTO preguntas (enunciado) VALUES (?)",
            (enunciado,),
        )
        pid = int(cur.lastrowid)
        opts = [
            ("A", opcion_a),
            ("B", opcion_b),
            ("C", opcion_c),
            ("D", opcion_d),
        ]
        for letra, texto in opts:
            es = 1 if letra == letter else 0
            self.connection.execute(
                """
                INSERT INTO opciones (pregunta_id, letra, texto, es_correcta)
                VALUES (?, ?, ?, ?)
                """,
                (pid, letra, texto, es),
            )
        self.connection.commit()
        return pid

    def get_preguntas(self) -> list[sqlite3.Row]:
        cur = self.connection.execute(
            """
            SELECT p.id,
                   p.enunciado,
                   MAX(CASE WHEN o.letra = 'A' THEN o.texto END) AS opcion_a,
                   MAX(CASE WHEN o.letra = 'B' THEN o.texto END) AS opcion_b,
                   MAX(CASE WHEN o.letra = 'C' THEN o.texto END) AS opcion_c,
                   MAX(CASE WHEN o.letra = 'D' THEN o.texto END) AS opcion_d,
                   MAX(CASE WHEN o.es_correcta = 1 THEN o.letra END) AS respuesta_correcta
            FROM preguntas p
            LEFT JOIN opciones o ON o.pregunta_id = p.id
            GROUP BY p.id, p.enunciado
            ORDER BY p.id
            """
        )
        return list(cur.fetchall())

    def update_pregunta(
        self,
        pregunta_id: int,
        enunciado: str,
        opcion_a: str,
        opcion_b: str,
        opcion_c: str,
        opcion_d: str,
        respuesta_correcta: str,
    ) -> None:
        letter = respuesta_correcta.strip().upper()
        self.connection.execute(
            "UPDATE preguntas SET enunciado = ? WHERE id = ?",
            (enunciado, pregunta_id),
        )
        for letra, texto in (
            ("A", opcion_a),
            ("B", opcion_b),
            ("C", opcion_c),
            ("D", opcion_d),
        ):
            es = 1 if letra == letter else 0
            self.connection.execute(
                """
                UPDATE opciones SET texto = ?, es_correcta = ?
                WHERE pregunta_id = ? AND letra = ?
                """,
                (texto, es, pregunta_id, letra),
            )
        self.connection.commit()

    def delete_pregunta(self, pregunta_id: int) -> None:
        self.connection.execute("DELETE FROM preguntas WHERE id = ?", (pregunta_id,))
        self.connection.commit()

    def insert_jugador(self, nombre: str, puntaje: int) -> int:
        nombre_clean = nombre.strip()
        cur = self.connection.execute(
            """
            INSERT INTO jugadores (nombre, puntaje) VALUES (?, ?)
            ON CONFLICT(nombre) DO UPDATE SET
                puntaje = MAX(jugadores.puntaje, excluded.puntaje)
            """,
            (nombre_clean, puntaje),
        )
        self.connection.commit()
        return int(cur.lastrowid)

    def get_record(self) -> dict[str, Any] | None:
        """Best score (MAX puntaje) with a player row; None if no games played."""
        cur = self.connection.execute(
            """
            SELECT nombre, puntaje
            FROM jugadores
            WHERE puntaje = (SELECT MAX(puntaje) FROM jugadores)
            ORDER BY id ASC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        if row is None:
            return None
        return {"nombre": row["nombre"], "puntaje": int(row["puntaje"])}

    def get_top_5_scores(self) -> list[dict[str, Any]]:
        """Returns the top 5 scores from the jugadores table."""
        cur = self.connection.execute(
            """
            SELECT nombre, puntaje
            FROM jugadores
            ORDER BY puntaje DESC, id ASC
            LIMIT 5
            """
        )
        return [{"nombre": row["nombre"], "puntaje": int(row["puntaje"])} for row in cur.fetchall()]

    def insert_usuario(self, username: str, password_hash: str) -> int:
        cur = self.connection.execute(
            "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        self.connection.commit()
        return int(cur.lastrowid)

    def get_usuario_by_username(self, username: str) -> sqlite3.Row | None:
        cur = self.connection.execute(
            "SELECT id, username, password_hash FROM usuarios WHERE username = ?",
            (username,)
        )
        return cur.fetchone()
