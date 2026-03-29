import sys
import csv
import time
import random
import math
from dataclasses import dataclass
from typing import List, Set, Dict, Tuple


Schedule = Dict[str, List[str]]


@dataclass
class Tarea:
    id: str
    duracion: int
    categoria: str


@dataclass
class Recurso:
    id: str
    categorias: Set[str]


@dataclass
class Asignacion:
    id_tarea: str
    id_recurso: str
    tiempo_inicio: int
    tiempo_fin: int


def leer_tareas(path: str) -> List[Tarea]:
    tareas: List[Tarea] = []
    with open(path) as f:
        reader = csv.reader(f)
        for fila in reader:
            if not fila:
                continue
            tareas.append(Tarea(
                id=fila[0].strip(),
                duracion=int(fila[1].strip()),
                categoria=fila[2].strip()
            ))
    return tareas


def leer_recursos(path: str) -> List[Recurso]:
    recursos: List[Recurso] = []
    with open(path) as f:
        reader = csv.reader(f)
        for fila in reader:
            if not fila:
                continue
            recursos.append(Recurso(
                id=fila[0].strip(),
                categorias=set(c.strip() for c in fila[1:])
            ))
    return recursos


def escribir_output(asignaciones: List[Asignacion], path: str) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        for a in asignaciones:
            writer.writerow([a.id_tarea, a.id_recurso, a.tiempo_inicio, a.tiempo_fin])


def schedule_a_asignaciones(
    schedule: Schedule, tareas_dict: Dict[str, Tarea]
) -> List[Asignacion]:
    asignaciones: List[Asignacion] = []
    for recurso_id in sorted(schedule.keys()):
        tiempo_actual = 0
        for task_id in schedule[recurso_id]:
            duracion = tareas_dict[task_id].duracion
            asignaciones.append(Asignacion(
                id_tarea=task_id,
                id_recurso=recurso_id,
                tiempo_inicio=tiempo_actual,
                tiempo_fin=tiempo_actual + duracion
            ))
            tiempo_actual += duracion
    return asignaciones


def greedy_lpt(
    tareas: List[Tarea],
    compatibilidad: Dict[str, List[str]],
    resource_ids: List[str],
) -> Tuple[Dict[str, Set[str]], Dict[str, int], Dict[str, str]]:
    schedule: Dict[str, Set[str]] = {rid: set() for rid in resource_ids}
    cargas: Dict[str, int] = {rid: 0 for rid in resource_ids}
    tarea_a_recurso: Dict[str, str] = {}
    tareas_ord = sorted(tareas, key=lambda t: t.duracion, reverse=True)
    for t in tareas_ord:
        recursos_comp = compatibilidad.get(t.categoria, [])
        if not recursos_comp:
            raise ValueError(f"Tarea {t.id} (categoria {t.categoria}) no tiene recurso compatible")
        mejor = min(recursos_comp, key=lambda rid: cargas[rid])
        schedule[mejor].add(t.id)
        cargas[mejor] += t.duracion
        tarea_a_recurso[t.id] = mejor
    return schedule, cargas, tarea_a_recurso


def busqueda_local(
    schedule: Dict[str, Set[str]],
    cargas: Dict[str, int],
    tarea_a_recurso: Dict[str, str],
    tareas_dict: Dict[str, Tarea],
    compatibilidad: Dict[str, List[str]],
    recursos_categorias: Dict[str, Set[str]],
    makespan_objetivo: int,
    tiempo_limite: float,
) -> int:
    mejor_makespan = max(cargas.values())
    while time.monotonic() < tiempo_limite and mejor_makespan > makespan_objetivo:
        mejorado = False
        bottleneck = max(cargas, key=lambda r: cargas[r])
        for task_id in sorted(schedule[bottleneck],
                              key=lambda tid: tareas_dict[tid].duracion, reverse=True):
            dur = tareas_dict[task_id].duracion
            cat = tareas_dict[task_id].categoria
            for destino in compatibilidad.get(cat, []):
                if destino == bottleneck:
                    continue
                nueva_carga_bot = cargas[bottleneck] - dur
                nueva_carga_dest = cargas[destino] + dur
                nuevo_ms = max(nueva_carga_bot, nueva_carga_dest,
                    max((c for r, c in cargas.items() if r != bottleneck and r != destino), default=0))
                if nuevo_ms < mejor_makespan:
                    schedule[bottleneck].discard(task_id)
                    schedule[destino].add(task_id)
                    cargas[bottleneck] = nueva_carga_bot
                    cargas[destino] = nueva_carga_dest
                    tarea_a_recurso[task_id] = destino
                    mejor_makespan = nuevo_ms
                    mejorado = True
                    break
            if mejorado:
                break
        if mejorado:
            continue
        for t1_id in list(schedule[bottleneck]):
            cat1 = tareas_dict[t1_id].categoria
            dur1 = tareas_dict[t1_id].duracion
            for otro in cargas:
                if otro == bottleneck:
                    continue
                if cat1 not in recursos_categorias[otro]:
                    continue
                for t2_id in list(schedule[otro]):
                    cat2 = tareas_dict[t2_id].categoria
                    if cat2 not in recursos_categorias[bottleneck]:
                        continue
                    dur2 = tareas_dict[t2_id].duracion
                    if dur1 <= dur2:
                        continue
                    nueva_carga_bot = cargas[bottleneck] - dur1 + dur2
                    nueva_carga_otro = cargas[otro] - dur2 + dur1
                    nuevo_ms = max(nueva_carga_bot, nueva_carga_otro,
                        max((c for r, c in cargas.items() if r != bottleneck and r != otro), default=0))
                    if nuevo_ms < mejor_makespan:
                        schedule[bottleneck].discard(t1_id)
                        schedule[otro].discard(t2_id)
                        schedule[bottleneck].add(t2_id)
                        schedule[otro].add(t1_id)
                        cargas[bottleneck] = nueva_carga_bot
                        cargas[otro] = nueva_carga_otro
                        tarea_a_recurso[t1_id] = otro
                        tarea_a_recurso[t2_id] = bottleneck
                        mejor_makespan = nuevo_ms
                        mejorado = True
                        break
                if mejorado:
                    break
            if mejorado:
                break
        if not mejorado:
            break
    return mejor_makespan


def simulated_annealing(
    schedule: Dict[str, Set[str]],
    cargas: Dict[str, int],
    tarea_a_recurso: Dict[str, str],
    tareas_movibles: List[str],
    tareas_dict: Dict[str, Tarea],
    compatibilidad: Dict[str, List[str]],
    makespan_objetivo: int,
    tiempo_limite: float,
) -> Tuple[Dict[str, Set[str]], Dict[str, int], Dict[str, str], int]:
    sa_makespan = max(cargas.values())
    mejor_makespan = sa_makespan
    mejor_schedule = {k: set(v) for k, v in schedule.items()}
    mejor_cargas = dict(cargas)
    mejor_tar = dict(tarea_a_recurso)
    temp = float(sa_makespan) * 0.2
    enfriamiento = 0.99995
    n_movibles = len(tareas_movibles)
    while time.monotonic() < tiempo_limite and mejor_makespan > makespan_objetivo:
        task_id = tareas_movibles[random.randint(0, n_movibles - 1)]
        cat = tareas_dict[task_id].categoria
        dur = tareas_dict[task_id].duracion
        origen = tarea_a_recurso[task_id]
        recursos_comp = compatibilidad[cat]
        destino = recursos_comp[random.randint(0, len(recursos_comp) - 1)]
        if destino == origen:
            continue
        nueva_carga_orig = cargas[origen] - dur
        nueva_carga_dest = cargas[destino] + dur
        viejo_max_orig = cargas[origen]
        viejo_max_dest = cargas[destino]
        nuevo_max = max(nueva_carga_orig, nueva_carga_dest)
        if nuevo_max <= sa_makespan:
            nuevo_ms = sa_makespan
            if viejo_max_orig == sa_makespan or viejo_max_dest == sa_makespan:
                nuevo_ms = max(nueva_carga_orig, nueva_carga_dest,
                    max((c for r, c in cargas.items() if r != origen and r != destino), default=0))
        else:
            nuevo_ms = nuevo_max
        delta = nuevo_ms - sa_makespan
        if delta <= 0 or random.random() < math.exp(-delta / max(temp, 0.001)):
            schedule[origen].discard(task_id)
            schedule[destino].add(task_id)
            cargas[origen] = nueva_carga_orig
            cargas[destino] = nueva_carga_dest
            tarea_a_recurso[task_id] = destino
            sa_makespan = nuevo_ms
            if sa_makespan < mejor_makespan:
                mejor_makespan = sa_makespan
                mejor_schedule = {k: set(v) for k, v in schedule.items()}
                mejor_cargas = dict(cargas)
                mejor_tar = dict(tarea_a_recurso)
        temp *= enfriamiento
        if temp < 0.01:
            temp = float(mejor_makespan) * 0.1
    return mejor_schedule, mejor_cargas, mejor_tar, mejor_makespan


def optimizar(
    tareas: List[Tarea],
    resource_ids: List[str],
    tareas_dict: Dict[str, Tarea],
    compatibilidad: Dict[str, List[str]],
    recursos_categorias: Dict[str, Set[str]],
    makespan_objetivo: int,
    tiempo_limite: float,
) -> Schedule:
    tareas_movibles = [t.id for t in tareas if len(compatibilidad.get(t.categoria, [])) > 1]
    schedule, cargas, tar = greedy_lpt(tareas, compatibilidad, resource_ids)
    mejor_makespan = busqueda_local(
        schedule, cargas, tar, tareas_dict, compatibilidad,
        recursos_categorias, makespan_objetivo, tiempo_limite
    )
    mejor_schedule = {k: set(v) for k, v in schedule.items()}
    mejor_cargas = dict(cargas)
    mejor_tar = dict(tar)
    if mejor_makespan <= makespan_objetivo or not tareas_movibles:
        return {k: list(v) for k, v in mejor_schedule.items()}
    sa_s, sa_c, sa_t, sa_ms = simulated_annealing(
        {k: set(v) for k, v in mejor_schedule.items()},
        dict(mejor_cargas), dict(mejor_tar),
        tareas_movibles, tareas_dict, compatibilidad,
        makespan_objetivo, tiempo_limite
    )
    if sa_ms < mejor_makespan:
        mejor_makespan = sa_ms
        mejor_schedule = sa_s
        mejor_cargas = sa_c
        mejor_tar = sa_t
    if time.monotonic() < tiempo_limite and mejor_makespan > makespan_objetivo:
        busqueda_local(
            mejor_schedule, mejor_cargas, mejor_tar, tareas_dict,
            compatibilidad, recursos_categorias, makespan_objetivo, tiempo_limite
        )
    return {k: list(v) for k, v in mejor_schedule.items()}


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python main.py <makespan_objetivo>")
        sys.exit(1)
    makespan_objetivo = int(sys.argv[1])
    tareas = leer_tareas("tareas.txt")
    recursos = leer_recursos("recursos.txt")
    tareas_dict: Dict[str, Tarea] = {t.id: t for t in tareas}
    resource_ids: List[str] = [r.id for r in recursos]
    compatibilidad: Dict[str, List[str]] = {}
    recursos_categorias: Dict[str, Set[str]] = {}
    for r in recursos:
        recursos_categorias[r.id] = r.categorias
        for cat in r.categorias:
            compatibilidad.setdefault(cat, []).append(r.id)
    inicio = time.monotonic()
    tiempo_limite = inicio + 9.0
    schedule = optimizar(
        tareas, resource_ids, tareas_dict, compatibilidad,
        recursos_categorias, makespan_objetivo, tiempo_limite
    )
    asignaciones = schedule_a_asignaciones(schedule, tareas_dict)
    tiempo_ejecucion = time.monotonic() - inicio
    makespan = max(a.tiempo_fin for a in asignaciones)
    escribir_output(asignaciones, "output.txt")
    print(f"Makespan obtenido: {makespan}")
    print(f"Makespan objetivo: {makespan_objetivo}")
    if makespan <= makespan_objetivo:
        print("Solucion dentro del objetivo")
    else:
        print("Solucion fuera del objetivo")
    print(f"Tiempo de ejecucion: {tiempo_ejecucion:.4f} s")


if __name__ == "__main__":
    main()
    