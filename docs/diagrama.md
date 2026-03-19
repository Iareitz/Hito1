# Diagrama de Estrategia: Greedy LPT

## Objetivo del programa

Dado un conjunto de tareas (cada una con duracion y categoria) y un conjunto
de recursos (cada uno con categorias que soporta), el programa debe:

1.⁠ ⁠Asignar cada tarea a un recurso compatible con su categoria
2.⁠ ⁠Decidir cuando empieza y termina cada tarea en ese recurso
3.⁠ ⁠Garantizar que un recurso no haga dos cosas al mismo tiempo
4.⁠ ⁠Minimizar el makespan: el instante en que termina la ultima tarea

---

## Algoritmo Greedy LPT (Longest Processing Time)

Un algoritmo Greedy toma la mejor decision posible en cada paso sin mirar
hacia el futuro. LPT es la variante que ordena las tareas de mayor a menor
duracion antes de asignarlas.

*Por que funciona:* Las tareas largas son las que mas desbalancean los
recursos si se agrupan. Asignandolas primero, se distribuyen mejor.
Las tareas cortas al final rellenan los huecos.

### Pasos del Greedy LPT:

1.⁠ ⁠Ordenar tareas de MAYOR a MENOR duracion
2.⁠ ⁠Para cada tarea:
   - Filtrar recursos compatibles con su categoria
   - Elegir el recurso compatible con menor carga acumulada
   - Asignar la tarea y actualizar la carga del recurso

---

## Flujo completo

ENTRADA: tareas.txt, recursos.txt, makespan_objetivo
         |
         v
[1] Leer tareas y recursos
    -> Crear objetos Tarea(id, duracion, categoria)
    -> Crear objetos Recurso(id, categorias, tiempo_libre=0)
         |
         v
[2] GREEDY LPT
    |  Ordenar tareas por duracion (MAYOR -> MENOR)
    |  Para cada tarea:
    |    a) Filtrar recursos compatibles con la categoria
    |    b) Elegir el compatible con menor tiempo_libre
    |    c) Asignar: inicio = recurso.tiempo_libre
    |                fin    = inicio + tarea.duracion
    |    d) Actualizar: recurso.tiempo_libre = fin
         |
         v
[3] Escribir output.txt
    Formato: id_tarea, id_recurso, tiempo_inicio, tiempo_fin
         |
         v
SALIDA: cronograma valido con makespan minimizado

---

## Ejemplo con datos de la EP

*Entrada:*

tareas.txt:          recursos.txt:
T1,4,CAT_A           R1,CAT_A
T2,7,CAT_A           R2,CAT_A
T3,3,CAT_A           R3,CAT_A
T4,6,CAT_A
T5,2,CAT_A
T6,5,CAT_A
T7,8,CAT_A
T8,4,CAT_A

### Paso 1 - Ordenar por duracion (LPT):

| Posicion | Tarea | Duracion |
|----------|-------|----------|
| 1        | T7    | 8        |
| 2        | T2    | 7        |
| 3        | T4    | 6        |
| 4        | T6    | 5        |
| 5        | T1    | 4        |
| 6        | T8    | 4        |
| 7        | T3    | 3        |
| 8        | T5    | 2        |

### Paso 2 - Asignacion Greedy:

| Paso | Tarea   | R1.libre | R2.libre | R3.libre | Elegido | Inicio | Fin |
|------|---------|----------|----------|----------|---------|--------|-----|
| 1    | T7(8)   | 0        | 0        | 0        | R1      | 0      | 8   |
| 2    | T2(7)   | 8        | 0        | 0        | R2      | 0      | 7   |
| 3    | T4(6)   | 8        | 7        | 0        | R3      | 0      | 6   |
| 4    | T6(5)   | 8        | 7        | 6        | R3      | 6      | 11  |
| 5    | T1(4)   | 8        | 7        | 11       | R2      | 7      | 11  |
| 6    | T8(4)   | 8        | 11       | 11       | R1      | 8      | 12  |
| 7    | T3(3)   | 12       | 11       | 11       | R2      | 11     | 14  |
| 8    | T5(2)   | 12       | 14       | 11       | R3      | 11     | 13  |

*Resultado: Makespan = 14*

### Cronograma visual:

R1: [  T7(0-8)  ][T8(8-12)]
R2: [ T2(0-7) ][T1(7-11)][T3(11-14)]
R3: [T4(0-6)][T6(6-11)][T5(11-13)]

    |----|----|----|----|----|----|----|----|
    0    2    4    6    8   10   12   14
                                      ^
                                 Makespan = 14

---

## Complejidad

| Fase         | Complejidad  |
|--------------|-------------|
| Ordenar LPT  | O(n log n)  |
| Greedy       | O(n x m)    |
| *Total*    | *O(n log n + n x m)* |

Donde n = tareas, m = recursos.
Guarda con Cmd+S. En la terminal:


git add docs/diagrama.md
git commit -m "agregar diagrama de estrategia"
git push