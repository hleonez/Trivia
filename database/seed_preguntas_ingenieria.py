"""One-off seed: 30 preguntas de ingeniería de software. Run from project root: python database/seed_preguntas_ingenieria.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database.db import DatabaseManager  # noqa: E402

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "¿Qué es la ingeniería de software?",
        "El estudio del hardware de los computadores",
        "La aplicación de métodos sistemáticos al desarrollo de software",
        "La programación sin planificación",
        "El diseño de redes informáticas",
        "B",
    ),
    (
        "¿Cuál es el objetivo principal del modelo en cascada?",
        "Iterar continuamente",
        "Minimizar costos de hardware",
        "Seguir fases secuenciales definidas",
        "Evitar documentación",
        "C",
    ),
    (
        "¿Qué significa UML?",
        "Unified Modeling Language",
        "Universal Machine Language",
        "User Modeling Logic",
        "Unified Machine Logic",
        "A",
    ),
    (
        "¿Qué representa un diagrama de casos de uso?",
        "Estructura de clases",
        "Interacción entre usuarios y sistema",
        "Flujo de datos",
        "Código fuente",
        "B",
    ),
    (
        "¿Qué es un requisito funcional?",
        "Restricción técnica",
        "Característica del sistema",
        "Lenguaje de programación",
        "Tipo de base de datos",
        "B",
    ),
    (
        "¿Qué es un requisito no funcional?",
        "Funcionalidad principal",
        "Comportamiento del usuario",
        "Restricción de calidad del sistema",
        "Algoritmo",
        "C",
    ),
    (
        "¿Qué es Scrum?",
        "Un lenguaje de programación",
        "Un framework ágil",
        "Un sistema operativo",
        "Un tipo de base de datos",
        "B",
    ),
    (
        "¿Qué es un sprint en Scrum?",
        "Un error del sistema",
        "Un ciclo corto de desarrollo",
        "Un diagrama UML",
        "Un tipo de prueba",
        "B",
    ),
    (
        "¿Qué es la deuda técnica?",
        "Dinero invertido en software",
        "Problemas financieros del proyecto",
        "Costos futuros por malas decisiones técnicas",
        "Salario de desarrolladores",
        "C",
    ),
    (
        "¿Qué es Git?",
        "Sistema operativo",
        "Lenguaje de programación",
        "Sistema de control de versiones",
        "Base de datos",
        "C",
    ),
    (
        "¿Qué es integración continua?",
        "Probar al final del proyecto",
        "Integrar cambios frecuentemente",
        "Evitar pruebas",
        "Solo programar",
        "B",
    ),
    (
        "¿Qué es un bug?",
        "Nueva funcionalidad",
        "Error en el software",
        "Mejora del sistema",
        "Documento técnico",
        "B",
    ),
    (
        "¿Qué es testing?",
        "Programar",
        "Documentar",
        "Probar el software",
        "Diseñar hardware",
        "C",
    ),
    (
        "¿Qué es TDD?",
        "Test Driven Development",
        "Technical Design Document",
        "Total Data Design",
        "Test Data Deployment",
        "A",
    ),
    (
        "¿Qué es refactorización?",
        "Añadir nuevas funciones",
        "Cambiar código sin alterar su comportamiento",
        "Eliminar código",
        "Crear documentación",
        "B",
    ),
    (
        "¿Qué es un framework?",
        "Lenguaje de programación",
        "Herramienta que facilita el desarrollo",
        "Sistema operativo",
        "Hardware",
        "B",
    ),
    (
        "¿Qué es MVC?",
        "Modelo de base de datos",
        "Patrón de arquitectura",
        "Lenguaje de programación",
        "Protocolo de red",
        "B",
    ),
    (
        "¿Qué significa API?",
        "Application Programming Interface",
        "Advanced Programming Input",
        "Application Process Integration",
        "Automated Program Interface",
        "A",
    ),
    (
        "¿Qué es un backlog?",
        "Lista de errores",
        "Lista de tareas pendientes",
        "Código fuente",
        "Base de datos",
        "B",
    ),
    (
        "¿Qué es la documentación técnica?",
        "Código del sistema",
        "Manual para usuarios",
        "Información sobre el sistema y su desarrollo",
        "Pruebas del sistema",
        "C",
    ),
    (
        "¿Qué es DevOps?",
        "Lenguaje de programación",
        "Integración entre desarrollo y operaciones",
        "Base de datos",
        "Sistema operativo",
        "B",
    ),
    (
        "¿Qué es un diagrama de clases?",
        "Representa usuarios",
        "Representa estructura del sistema",
        "Representa red",
        "Representa pruebas",
        "B",
    ),
    (
        "¿Qué es un algoritmo?",
        "Programa completo",
        "Secuencia de pasos para resolver un problema",
        "Lenguaje de programación",
        "Hardware",
        "B",
    ),
    (
        "¿Qué es la mantenibilidad?",
        "Capacidad de ejecutar rápido",
        "Facilidad de modificar el software",
        "Seguridad del sistema",
        "Uso de memoria",
        "B",
    ),
    (
        "¿Qué es escalabilidad?",
        "Reducir errores",
        "Capacidad de crecer en rendimiento",
        "Mejorar interfaz",
        "Reducir código",
        "B",
    ),
    (
        "¿Qué es un repositorio?",
        "Lugar físico",
        "Almacenamiento de código",
        "Servidor web",
        "Base de datos relacional",
        "B",
    ),
    (
        "¿Qué es una historia de usuario?",
        "Código del sistema",
        "Requisito desde la perspectiva del usuario",
        "Documento técnico",
        "Error del sistema",
        "B",
    ),
    (
        "¿Qué es una prueba unitaria?",
        "Prueba del sistema completo",
        "Prueba de una pequeña parte del código",
        "Prueba de usuario",
        "Prueba de hardware",
        "B",
    ),
    (
        "¿Qué es un patrón de diseño?",
        "Lenguaje de programación",
        "Solución reutilizable a un problema común",
        "Error del sistema",
        "Tipo de hardware",
        "B",
    ),
    (
        "¿Qué es la calidad del software?",
        "Cantidad de código",
        "Nivel de cumplimiento de requisitos y estándares",
        "Velocidad del computador",
        "Número de usuarios",
        "B",
    ),
]


def main() -> None:
    db = DatabaseManager()
    db.connect()
    db.create_tables()
    for enunciado, oa, ob, oc, od, rc in ROWS:
        db.insert_pregunta(enunciado, oa, ob, oc, od, rc)
    print(f"Insertadas {len(ROWS)} preguntas en {db.db_path}")


if __name__ == "__main__":
    main()
