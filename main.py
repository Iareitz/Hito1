import sys
import csv
import time
from dataclasses import dataclass, field
from typing import List, Set


# -- Estructuras de datos --

@dataclass
class Tarea:
    """Representa una tarea: tiene un id, cuanto dura y de que categoria es."""
    id: str
    duracion: int
    categoria: str
    
