import sys
import csv
import time
from dataclasses import dataclass, field
from typing import List, Set, Dict


# ── Estructuras de datos ──────────────────────────────────────────────────────

@dataclass
class Tarea:
    """Representa una tarea: tiene un id, cuánto dura y de qué categoría es."""
    id: str
    duracion: int
    categoria: str


@dataclass
class Recurso:
    """Representa un recurso: tiene un id y las categorías que puede ejecutar."""
    id: str
    categorias: Set[str]
    tiempo_libre: int = field(default=0)


@dataclass
class Asignacion:
    """Representa una línea del output: qué tarea, en qué recurso, cuándo."""
    id_tarea: str
    id_recurso: str
    tiempo_inicio: int
    tiempo_fin: int

