# ============================================================
# NUT SORT - CORE DEL ALGORITMO DE BRANCH AND BOUND
# ============================================================
# Este archivo contiene ÚNICAMENTE la lógica del algoritmo de
# Branch and Bound para resolver el problema de ordenamiento de tuercas.
# 
# Estrategia:
# - Asignación de colores destino por tuerca base (Opción 1)
# - Resolución de empates con puntaje híbrido (Opción 6)
# - Podas agresivas basadas en lower bounds
# - Best-First Search con cola de prioridad
# ============================================================

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Set, Dict
from heapq import heappush, heappop
import math

# ============================================================
# DEFINICIONES BÁSICAS DEL PROBLEMA
# ============================================================

# Capacidad máxima de cada pila (5 tuercas por perno)
MAX_CAP = 5

# Tipos de datos básicos
Color = str               # Representa un color (ej: "R", "G", "Y", "B", "O")
Pile  = Tuple[Color, ...] # Una pila = tupla de colores (de abajo hacia arriba)
State = Tuple[Pile, ...]  # Estado completo = tupla de todas las pilas

# ============================================================
# FUNCIONES PRIMITIVAS: Operaciones básicas sobre pilas
# ============================================================
# Reutilizamos las funciones básicas de backtracking

def top(p: Pile) -> Optional[Color]:
    """Devuelve el color del tope (parte superior) de la pila."""
    return p[-1] if p else None


def free_slots(p: Pile) -> int:
    """Calcula cuántos espacios libres hay en la pila."""
    return MAX_CAP - len(p)


def run_len_superior(p: Pile) -> int:
    """Cuenta cuántas tuercas del mismo color hay en la parte superior."""
    if not p:
        return 0
    c = p[-1]
    k = 0
    for x in reversed(p):
        if x == c:
            k += 1
        else:
            break
    return k


def pila_es_monocolor(p: Pile) -> bool:
    """Verifica si una pila está resuelta: todas las tuercas son del mismo color."""
    if len(p) <= 1:
        return True
    return all(x == p[0] for x in p)


def pila_terminada(p: Pile) -> bool:
    """Verifica si un PERNO está terminado (5 tuercas del mismo color)."""
    if len(p) == MAX_CAP:
        return all(x == p[0] for x in p)
    return False


def is_goal(s: State) -> bool:
    """Verifica si el estado actual es el objetivo (resuelto)."""
    for p in s:
        if len(p) == 0:
            continue  # Vacío está bien
        elif len(p) == MAX_CAP and all(x == p[0] for x in p):
            continue  # 5 tuercas del mismo color está bien
        else:
            return False
    return True


def puede_mover(p_src: Pile, p_dst: Pile) -> bool:
    """Verifica si es legal mover una tuerca desde la pila origen a la pila destino."""
    if not p_src:
        return False
    if len(p_dst) >= MAX_CAP:
        return False
    return (not p_dst) or (top(p_src) == top(p_dst))


def aplicar_movimiento(s: State, i: int, j: int) -> State:
    """Aplica un movimiento: mueve el tope de la pila i hacia la pila j."""
    if not puede_mover(s[i], s[j]):
        raise ValueError(f"Movimiento invalido: P{i} -> P{j}")
    
    if i < 0 or i >= len(s) or j < 0 or j >= len(s):
        raise IndexError(f"Índices inválidos: i={i}, j={j}")
    
    src = list(s[i])
    dst = list(s[j])
    
    tuerca_movida = src.pop()
    dst.append(tuerca_movida)
    
    nuevo = list(s)
    nuevo[i] = tuple(src)
    nuevo[j] = tuple(dst)
    
    return tuple(nuevo)


# ============================================================
# ASIGNACIÓN DE COLORES DESTINO (Opción 1 + Resolución Empates)
# ============================================================

def obtener_color_base(p: Pile) -> Optional[Color]:
    """Obtiene el color de la tuerca en la base de la pila."""
    return p[0] if p else None


def calcular_racha_mas_larga(p: Pile, color: Color) -> int:
    """Calcula la racha más larga del color dado en la pila (consecutivas)."""
    if not p:
        return 0
    
    max_racha = 0
    racha_actual = 0
    
    for c in p:
        if c == color:
            racha_actual += 1
            max_racha = max(max_racha, racha_actual)
        else:
            racha_actual = 0
    
    return max_racha


def contar_otros_colores(p: Pile, color: Color) -> int:
    """Cuenta cuántas tuercas de otros colores hay en la pila."""
    return sum(1 for c in p if c != color)


def contar_color_total(p: Pile, color: Color) -> int:
    """Cuenta cuántas tuercas del color dado hay en la pila."""
    return sum(1 for c in p if c == color)


def asignar_colores_destino(estado: State) -> Dict[int, Color]:
    """
    Asigna un color destino a cada perno basándose en la tuerca base.
    
    Estrategia:
    1. Para cada color, encontrar todos los pernos que lo tienen en la base
    2. Calcular puntaje híbrido: (cantidad_R * 3) + (racha_mas_larga * 2) - (otros_colores)
    3. Asignar el color al perno con mayor puntaje
    4. Si hay empate exacto, usar el primer perno encontrado
    
    Retorna un diccionario {indice_perno: color_destino}
    """
    asignaciones: Dict[int, Color] = {}
    colores_asignados: Set[Color] = set()
    
    # Encontrar todos los colores únicos que aparecen en las bases
    colores_base: Dict[Color, List[int]] = defaultdict(list)
    
    for i, pila in enumerate(estado):
        color_base = obtener_color_base(pila)
        if color_base is not None:
            colores_base[color_base].append(i)
    
    # Para cada color que aparece en alguna base, asignar al mejor perno
    for color, indices_pernos in colores_base.items():
        if color in colores_asignados:
            continue  # Este color ya fue asignado
        
        mejor_perno = None
        mejor_puntaje = -math.inf
        
        for idx in indices_pernos:
            pila = estado[idx]
            
            # Calcular componentes del puntaje híbrido (Opción 6)
            cantidad_color = contar_color_total(pila, color)
            racha_mas_larga = calcular_racha_mas_larga(pila, color)
            otros_colores = contar_otros_colores(pila, color)
            
            # Puntaje híbrido: (cantidad * 3) + (racha * 2) - (otros)
            puntaje = (cantidad_color * 3) + (racha_mas_larga * 2) - otros_colores
            
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_perno = idx
        
        # Asignar el color al mejor perno encontrado
        if mejor_perno is not None:
            asignaciones[mejor_perno] = color
            colores_asignados.add(color)
    
    return asignaciones


# ============================================================
# HEURÍSTICA: CÁLCULO DE LOWER BOUND (COTA INFERIOR)
# ============================================================

def calcular_lower_bound(estado: State, asignaciones: Dict[int, Color]) -> int:
    """
    Calcula una cota inferior (lower bound) del número de movimientos
    necesarios para resolver el estado.
    
    Estrategia agresiva:
    1. Para cada color, contar cuántas tuercas están fuera de lugar
    2. Estimar movimientos mínimos necesarios para consolidarlas
    3. Considerar tuercas atrapadas bajo otros colores
    4. Sumar estimaciones optimistas pero realistas
    
    Retorna un entero >= 0 representando el mínimo estimado de movimientos.
    """
    if is_goal(estado):
        return 0
    
    movimientos_estimados = 0
    
    # Para cada color asignado a un perno destino
    for perno_destino, color_destino in asignaciones.items():
        pila_destino = estado[perno_destino]
        
        # Contar cuántas tuercas del color destino hay en esta pila
        tuercas_en_destino = contar_color_total(pila_destino, color_destino)
        
        # Si faltan tuercas, necesitamos moverlas desde otros pernos
        tuercas_faltantes = MAX_CAP - tuercas_en_destino
        
        if tuercas_faltantes > 0:
            # Estimar movimientos para traer las tuercas faltantes
            # Optimista: al menos 1 movimiento por tuerca faltante (si no están atrapadas)
            movimientos_estimados += tuercas_faltantes
        
        # Contar tuercas de otros colores que están en el perno destino
        # Estas deben moverse fuera (mínimo 1 movimiento por tuerca diferente)
        tuercas_otras = contar_otros_colores(pila_destino, color_destino)
        movimientos_estimados += tuercas_otras
        
        # Detectar tuercas atrapadas: si hay tuercas del color destino
        # pero están bajo otro color, necesitamos más movimientos
        if len(pila_destino) > 0:
            # Verificar si la base es del color destino
            if obtener_color_base(pila_destino) != color_destino:
                # Si no, todas las tuercas del color destino están atrapadas
                movimientos_estimados += tuercas_en_destino
    
    # Buscar tuercas del color destino en otros pernos
    for color_destino in asignaciones.values():
        tuercas_en_otros_pernos = 0
        
        for i, pila in enumerate(estado):
            if i not in asignaciones or asignaciones[i] != color_destino:
                # Este perno no es el destino de este color
                tuercas_en_otros_pernos += contar_color_total(pila, color_destino)
        
        # Estimar movimientos para traer estas tuercas
        # Optimista: al menos 1 movimiento por tuerca
        if tuercas_en_otros_pernos > 0:
            movimientos_estimados += tuercas_en_otros_pernos
    
    # Para pilas sin color destino asignado (vacías o con color no asignado)
    # Considerar que pueden servir como buffer, pero penalizar si tienen mezclas
    for i, pila in enumerate(estado):
        if i not in asignaciones:
            if len(pila) > 0:
                # Esta pila tiene tuercas pero no tiene destino asignado
                # Puede ser un buffer, pero si está mezclada necesita movimientos
                if not pila_es_monocolor(pila):
                    # Pila mezclada: estimar movimientos para limpiarla
                    # Contar bloques de colores diferentes
                    bloques = 1
                    for j in range(1, len(pila)):
                        if pila[j] != pila[j-1]:
                            bloques += 1
                    movimientos_estimados += bloques - 1  # Al menos bloques-1 movimientos
    
    return movimientos_estimados


def es_estado_imposible(estado: State, asignaciones: Dict[int, Color]) -> bool:
    """
    Detecta si un estado es imposible de resolver (podar agresivamente).
    
    Criterios de imposibilidad:
    1. Algún color tiene más de MAX_CAP tuercas en total
    2. Algún perno destino tiene más tuercas de otro color que del color destino
       y no hay espacio para moverlas
    3. Hay un deadlock evidente
    
    Retorna True si el estado es imposible de resolver.
    """
    # Verificar que ningún color tenga más tuercas de las permitidas
    contador_colores = Counter()
    for pila in estado:
        for color in pila:
            contador_colores[color] += 1
    
    for color, cantidad in contador_colores.items():
        if cantidad > MAX_CAP:
            return True  # Imposible: más tuercas de un color que capacidad
    
    # Verificar deadlocks simples: perno destino completamente bloqueado
    for perno_destino, color_destino in asignaciones.items():
        pila = estado[perno_destino]
        
        # Si la base no es del color destino y la pila está llena
        if len(pila) == MAX_CAP and obtener_color_base(pila) != color_destino:
            # Verificar si hay espacio en otros pernos para mover
            espacios_disponibles = sum(
                free_slots(estado[j]) 
                for j in range(len(estado)) 
                if j != perno_destino and not pila_terminada(estado[j])
            )
            
            # Si no hay espacio suficiente para mover las tuercas bloqueantes
            tuercas_bloqueantes = contar_otros_colores(pila, color_destino)
            if espacios_disponibles < tuercas_bloqueantes:
                return True  # Deadlock: no hay espacio para desbloquear
    
    return False


# ============================================================
# ALGORITMO PRINCIPAL: BRANCH AND BOUND
# ============================================================

@dataclass
class SearchStats:
    """Estadísticas de la búsqueda."""
    expanded: int = 0
    max_depth: int = 0
    pruned: int = 0  # Número de nodos podados
    mejor_cota_encontrada: int = field(default_factory=lambda: math.inf)


@dataclass
class Node:
    """Nodo del árbol de búsqueda para Branch and Bound."""
    estado: State
    g: int  # Costo acumulado (número de movimientos)
    h: int  # Heurística (lower bound)
    path: List[Tuple[int, int]]  # Secuencia de movimientos hasta aquí
    f: int = 0  # f = g + h (se calcula automáticamente)
    
    def __post_init__(self):
        self.f = self.g + self.h
    
    def __lt__(self, other):
        """Comparación para heapq (menor f = mayor prioridad)."""
        if self.f != other.f:
            return self.f < other.f
        # Desempate: preferir menor profundidad (g)
        return self.g < other.g


def generar_movimientos_validos(s: State) -> List[Tuple[int, int]]:
    """
    Genera todos los movimientos válidos desde el estado s.
    
    Similar a backtracking pero sin ordenamiento heurístico especial
    (el ordenamiento lo hace la cola de prioridad).
    """
    N = len(s)
    movimientos = []
    
    for i in range(N):
        if pila_terminada(s[i]):
            continue  # No mover desde pilas terminadas
        
        for j in range(N):
            if i == j:
                continue
            if pila_terminada(s[j]):
                continue  # No mover hacia pilas terminadas
            
            if puede_mover(s[i], s[j]):
                movimientos.append((i, j))
    
    return movimientos


def solve_branch_and_bound(
    start: State,
    max_expansions: Optional[int] = None
) -> Tuple[Optional[List[Tuple[int, int]]], SearchStats]:
    """
    Resuelve el problema usando Branch and Bound con Best-First Search.
    
    Estrategia:
    1. Calcular asignaciones de colores destino al inicio
    2. Usar cola de prioridad (heap) ordenada por f(n) = g(n) + h(n)
    3. Podar ramas donde f(n) >= mejor_solucion_encontrada
    4. Podar estados imposibles
    5. Mantener conjunto de estados visitados (pero permitir revisitar si mejor g)
    
    Parámetros:
        start: Estado inicial
        max_expansions: Límite opcional de estados a expandir
    
    Retorna:
        (solucion, stats) donde:
        - solucion: Lista de movimientos (i, j) que llevan a la solución, o None
        - stats: Estadísticas de la búsqueda
    """
    # Calcular asignaciones de colores destino una sola vez
    asignaciones = asignar_colores_destino(start)
    
    stats = SearchStats()
    mejor_solucion: Optional[List[Tuple[int, int]]] = None
    mejor_costo = math.inf
    
    # Cola de prioridad: (f, g, estado, path)
    heap = []
    
    # Calcular heurística inicial
    h_inicial = calcular_lower_bound(start, asignaciones)
    
    # Verificar si el estado inicial es imposible
    if es_estado_imposible(start, asignaciones):
        return None, stats
    
    # Nodo inicial
    nodo_inicial = Node(
        estado=start,
        g=0,
        h=h_inicial,
        path=[]
    )
    heappush(heap, nodo_inicial)
    
    # Diccionario de mejor costo conocido para cada estado
    # {estado_string: mejor_g_conocido}
    mejor_g_por_estado: Dict[str, int] = {}
    # Función auxiliar para convertir estado a string único
    def estado_a_string(s: State) -> str:
        """Convierte un estado a string para usar como clave."""
        return str(s)
    
    # Verificar estado inicial
    estado_str_inicial = estado_a_string(start)
    mejor_g_por_estado[estado_str_inicial] = 0
    
    while heap:
        # Obtener el nodo con menor f(n)
        nodo_actual = heappop(heap)
        
        # Verificar límite de expansiones
        if max_expansions and stats.expanded >= max_expansions:
            break
        
        stats.expanded += 1
        stats.max_depth = max(stats.max_depth, len(nodo_actual.path))
        
        # CASO BASE: ¿Hemos alcanzado el objetivo?
        if is_goal(nodo_actual.estado):
            # Si encontramos una solución mejor que la actual, actualizarla
            if nodo_actual.g < mejor_costo:
                mejor_solucion = nodo_actual.path
                mejor_costo = nodo_actual.g
                stats.mejor_cota_encontrada = mejor_costo
            # No expandir este nodo (ya es solución)
            continue
        
        # PODA 1: Si ya tenemos una solución y este nodo no puede mejorarla
        if mejor_costo < math.inf:
            if nodo_actual.f >= mejor_costo:
                stats.pruned += 1
                continue  # Podar: no puede mejorar la solución actual
        
        # PODA 2: Si el estado es imposible
        if es_estado_imposible(nodo_actual.estado, asignaciones):
            stats.pruned += 1
            continue
        
        # Generar movimientos válidos
        movimientos = generar_movimientos_validos(nodo_actual.estado)
        
        for (i, j) in movimientos:
            try:
                nuevo_estado = aplicar_movimiento(nodo_actual.estado, i, j)
            except (ValueError, IndexError):
                continue  # Movimiento inválido, saltar
            
            nuevo_g = nodo_actual.g + 1
            nuevo_h = calcular_lower_bound(nuevo_estado, asignaciones)
            nuevo_f = nuevo_g + nuevo_h
            
            # PODA 3: Si f(n) >= mejor_costo, podar
            if nuevo_f >= mejor_costo:
                stats.pruned += 1
                continue
            
            # PODA 4: Si el nuevo estado es imposible
            if es_estado_imposible(nuevo_estado, asignaciones):
                stats.pruned += 1
                continue
            
            estado_str = estado_a_string(nuevo_estado)
            
            # PODA 5: Si ya visitamos este estado con mejor o igual costo
            if estado_str in mejor_g_por_estado:
                if mejor_g_por_estado[estado_str] <= nuevo_g:
                    continue  # Ya exploramos este estado con mejor o igual costo
                # Si encontramos mejor camino, actualizar y explorar de nuevo
                mejor_g_por_estado[estado_str] = nuevo_g
            else:
                mejor_g_por_estado[estado_str] = nuevo_g
            
            # Crear nuevo nodo y agregarlo a la cola
            nuevo_nodo = Node(
                estado=nuevo_estado,
                g=nuevo_g,
                h=nuevo_h,
                path=nodo_actual.path + [(i, j)]
            )
            
            heappush(heap, nuevo_nodo)
    
    return mejor_solucion, stats

