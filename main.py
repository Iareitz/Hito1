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

def leer_tareas(path: str) -> List[Tarea]:
    """Lee tareas.txt y devuelve una lista de objetos Tarea."""
    tareas: List[Tarea] = []
    with open(path) as f:
        reader = csv.reader(f)
        for fila in reader:
            tareas.append(Tarea(
                id=fila[0].strip(),
                duracion=int(fila[1].strip()),
                categoria=fila[2].strip()
            ))
    return tareas

def leer_recursos(path: str) -> List[Recurso]:
    """Lee recursos.txt y devuelve una lista de objetos Recurso."""
    recursos: List[Recurso] = []
    with open(path) as f:
        reader = csv.reader(f)
        for fila in reader:
            recursos.append(Recurso(
                id=fila[0].strip(),
                categorias=set(c.strip() for c in fila[1:])
            ))
    return recursos

def escribir_output(asignaciones: List[Asignacion], path: str) -> None:
    """Escribe el cronograma en output.txt en formato CSV."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        for a in asignaciones:
            writer.writerow([a.id_tarea, a.id_recurso, a.tiempo_inicio, a.tiempo_fin])


def planificar(tareas: List[Tarea], recursos: List[Recurso]) -> List[Asignacion]:
    tareas_ord = sorted(tareas, key=lambda t: t.duracion, reverse=True)
    asignaciones: List[Asignacion] = []
    for t in tareas_ord:
        compatibles = [r for r in recursos if t.categoria in r.categorias]
        if not compatibles:
            continue
        mejor = min(compatibles, key=lambda r: r.tiempo_libre)
        inicio = mejor.tiempo_libre
        fin = inicio + t.duracion
        asignaciones.append(Asignacion(id_tarea=t.id, id_recurso=mejor.id, tiempo_inicio=inicio, tiempo_fin=fin))
        mejor.tiempo_libre = fin
    return asignaciones

