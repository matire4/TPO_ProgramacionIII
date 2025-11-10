# ============================================================
# NUT SORT - CORE DEL ALGORITMO DE BACKTRACKING
# ============================================================
# Este archivo contiene ÚNICAMENTE la lógica del algoritmo de
# backtracking para resolver el problema de ordenamiento de tuercas.
# 
# No incluye:
# - Frontend/Interfaz de usuario
# - Generación de casos aleatorios
# - Utilidades de visualización
# - Validaciones de entrada/salida
# ============================================================

from collections import Counter
from dataclasses import dataclass
from typing import Tuple, List, Optional, Set

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

def top(p: Pile) -> Optional[Color]:
    """
    Devuelve el color del tope (parte superior) de la pila.
    Si la pila está vacía, devuelve None.
    
    Ejemplo:
        top(("R", "G", "Y")) -> "Y"
        top(()) -> None
    """
    return p[-1] if p else None


def free_slots(p: Pile) -> int:
    """
    Calcula cuántos espacios libres hay en la pila.
    La capacidad máxima es MAX_CAP (5 tuercas).
    
    Ejemplo:
        free_slots(("R", "G")) -> 3  (puede agregar 3 más hasta llegar a 5)
    """
    return MAX_CAP - len(p)


def run_len_superior(p: Pile) -> int:
    """
    Cuenta cuántas tuercas del mismo color hay en la parte superior
    de la pila (desde el tope hacia abajo).
    
    Esto es útil para las heurísticas: las rachas largas son buenas
    porque indican que ya hay tuercas ordenadas.
    
    Ejemplo:
        run_len_superior(("R", "R", "R", "G")) -> 3  (3 rojas arriba)
        run_len_superior(("R", "G", "Y")) -> 1  (solo una arriba)
    """
    if not p:
        return 0
    
    # Color del tope
    c = p[-1]
    k = 0
    
    # Contar desde el tope hacia abajo cuántas son iguales
    for x in reversed(p):
        if x == c:
            k += 1
        else:
            break  # Si encontramos uno diferente, terminamos
    
    return k


def pila_es_monocolor(p: Pile) -> bool:
    """
    Verifica si una pila está resuelta: todas las tuercas son del
    mismo color (o la pila está vacía).
    
    Esta es la condición de éxito para cada pila.
    
    Ejemplo:
        pila_es_monocolor(("R", "R", "R")) -> True
        pila_es_monocolor(("R", "G")) -> False
        pila_es_monocolor(()) -> True  (pila vacía cuenta como válida)
    """
    # Si tiene 1 o menos elementos, automáticamente es monocolor
    if len(p) <= 1:
        return True
    
    # Verificar que todos sean iguales al primero
    return all(x == p[0] for x in p)


def pila_terminada(p: Pile) -> bool:
    """
    Verifica si un PERNO/TORNILLO está terminado y no debe usarse más.
    
    Un perno está terminado SOLO si tiene exactamente 5 tuercas
    del mismo color (lleno y monocolor).
    
    IMPORTANTE: 
    - Un perno VACÍO NO está terminado (puede usarse como destino para recibir tuercas)
    - Una vez que un perno está terminado (5 tuercas del mismo color),
      NO se pueden mover tuercas DESDE ese perno NI HACIA ese perno.
      El perno queda "congelado" y no participa más en el juego.
    
    Ejemplo:
        pila_terminada(()) -> False  (perno vacío, puede recibir tuercas)
        pila_terminada(("R", "R", "R", "R", "R")) -> True  (perno terminado: 5 tuercas rojas)
        pila_terminada(("R", "R", "R")) -> False  (monocolor pero no lleno)
        pila_terminada(("R", "G")) -> False  (no monocolor)
    """
    # Solo los pernos con 5 tuercas del mismo color están terminados
    if len(p) == MAX_CAP:
        return all(x == p[0] for x in p)
    
    # Cualquier otro caso (incluyendo vacíos) no está terminado
    return False


def is_goal(s: State) -> bool:
    """
    Verifica si el estado actual es el objetivo (resuelto).
    
    El problema está resuelto cuando TODOS los pernos están terminados:
    - Vacíos (sin tuercas), O
    - Con 5 tuercas del mismo color (perno completado)
    
    Ejemplo:
        Estado resuelto: (("R","R","R","R","R"), ("G","G","G","G","G"), (), ("B","B","B","B","B"))
        - Perno 0: terminado con 5 tuercas rojas
        - Perno 1: terminado con 5 tuercas verdes
        - Perno 2: vacío (terminado)
        - Perno 3: terminado con 5 tuercas azules
    """
    for p in s:
        # Un perno está en objetivo si está vacío O tiene 5 tuercas del mismo color
        if len(p) == 0:
            continue  # Vacío está bien (perno terminado sin tuercas)
        elif len(p) == MAX_CAP and all(x == p[0] for x in p):
            continue  # 5 tuercas del mismo color está bien (perno terminado completo)
        else:
            return False  # Si no cumple ninguna condición, no es objetivo
    return True


# ============================================================
# REGLAS DE MOVIMIENTO: Qué movimientos son válidos
# ============================================================

def puede_mover(p_src: Pile, p_dst: Pile) -> bool:
    """
    Verifica si es legal mover una tuerca desde la pila origen
    a la pila destino.
    
    Reglas:
    1. La pila origen NO debe estar vacía
    2. La pila destino NO debe estar llena (MAX_CAP)
    3. Si el destino NO está vacío, el color del tope debe coincidir
       con el color de la tuerca que queremos mover
    
    Ejemplo:
        puede_mover(("R", "G"), ("R")) -> True  (mismo color arriba)
        puede_mover(("R", "G"), ()) -> True     (destino vacío)
        puede_mover(("R", "G"), ("G")) -> False (colores diferentes)
    """
    # Regla 1: Origen no puede estar vacío
    if not p_src:
        return False
    
    # Regla 2: Destino no puede estar lleno
    if len(p_dst) >= MAX_CAP:
        return False
    
    # Regla 3: Si destino no está vacío, colores deben coincidir
    # (Si está vacío, también es válido)
    return (not p_dst) or (top(p_src) == top(p_dst))


def aplicar_movimiento(s: State, i: int, j: int) -> State:
    """
    Aplica un movimiento: mueve el tope de la pila i hacia la pila j.
    
    IMPORTANTE: Esta función VALIDA que el movimiento sea legal antes
    de aplicarlo. Si no es válido, lanza una excepción.
    
    Retorna un NUEVO estado (los estados son inmutables).
    
    Ejemplo:
        estado = (("R", "G"), ("Y",))
        aplicar_movimiento(estado, 0, 1) -> (("R",), ("Y", "G"))
    """
    # VALIDACIÓN DEFENSIVA: Verificar que el movimiento sea legal
    if not puede_mover(s[i], s[j]):
        raise ValueError(
            f"Movimiento invalido: P{i} -> P{j}. "
            f"Origen={s[i]}, Destino={s[j]}. "
            f"Tope origen={top(s[i])}, Tope destino={top(s[j]) if s[j] else None}"
        )
    
    # Verificar índices válidos
    if i < 0 or i >= len(s) or j < 0 or j >= len(s):
        raise IndexError(f"Índices inválidos: i={i}, j={j}, len(estado)={len(s)}")
    
    # Convertir a listas para poder modificar
    src = list(s[i])
    dst = list(s[j])
    
    # Guardar el color que vamos a mover y el tope del destino ANTES del movimiento
    color_origen = src[-1] if src else None
    color_destino_tope = dst[-1] if dst else None
    
    # VALIDACIÓN CRÍTICA: Si el destino no está vacío, los colores DEBEN coincidir
    # Esta validación ya se hizo en puede_mover, pero la hacemos de nuevo por seguridad
    if color_destino_tope is not None and color_origen != color_destino_tope:
        raise ValueError(
            f"Movimiento invalido: Intentando poner {color_origen} sobre {color_destino_tope} "
            f"en P{j}. Origen={s[i]}, Destino={s[j]}"
        )
    
    # Mover el tope: quitar de origen, agregar a destino
    tuerca_movida = src.pop()
    dst.append(tuerca_movida)
    
    # VALIDACIÓN POST-MOVIMIENTO: Verificar que todo quedó bien
    if len(dst) > 1:
        # Verificar que los dos últimos elementos (los que están juntos ahora) tengan el mismo color
        if dst[-1] != dst[-2]:
            raise ValueError(
                f"Error post-movimiento: Colores diferentes juntos en P{j}. "
                f"Estado: {dst}"
            )
    
    # Crear nuevo estado
    nuevo = list(s)
    nuevo[i] = tuple(src)  # Nueva pila origen
    nuevo[j] = tuple(dst)  # Nueva pila destino
    
    # VALIDACIÓN FINAL: Verificar que el nuevo estado es válido
    if len(dst) > MAX_CAP:
        raise ValueError(f"Error: Pila P{j} excede capacidad máxima {MAX_CAP}")
    
    return tuple(nuevo)  # Retornar como tupla (inmutable)


# ============================================================
# HEURÍSTICA H1: Selección de Color Foco
# ============================================================
# Idea: Priorizar movimientos que involucren el color más frecuente
# en los topes. Esto ayuda a consolidar colores más rápido.

def freq_topes(s: State) -> Counter:
    """
    Cuenta cuántas veces aparece cada color en los topes de las pilas.
    
    Esto nos ayuda a identificar qué color debería ser nuestra prioridad.
    Si un color aparece muchas veces arriba, tiene más potencial para
    consolidarse.
    
    Ejemplo:
        Estado: (("R", "G"), ("R", "Y"), ("G",))
        freq_topes -> Counter({"R": 2, "G": 1, "Y": 1})
    """
    cnt = Counter()
    for p in s:
        if p:  # Solo si la pila no está vacía
            cnt[top(p)] += 1
    return cnt


def max_run_por_color(s: State) -> dict:
    """
    Para cada color, encuentra la racha más larga que existe en
    alguna pila.
    
    Esto se usa como desempate: si dos colores tienen la misma
    frecuencia, preferimos el que tenga una racha más larga.
    
    Ejemplo:
        Si "R" tiene racha de 3 y "G" tiene racha de 1,
        preferimos trabajar con "R" primero.
    """
    best = {}
    for p in s:
        if not p:
            continue
        c = top(p)
        r = run_len_superior(p)
        # Guardar la racha más larga encontrada para este color
        best[c] = max(best.get(c, 0), r)
    return best


def elegir_color_foco(s: State) -> Optional[Color]:
    """
    Selecciona el "color foco": el color en el que deberíamos
    concentrarnos en este momento.
    
    Criterios (en orden de importancia):
    1. Mayor frecuencia en los topes (más oportunidades de consolidar)
    2. Mayor racha existente (desempate)
    
    Retorna None si no hay ningún tope (todas las pilas vacías).
    """
    ft = freq_topes(s)
    if not ft:
        return None
    
    br = max_run_por_color(s)
    
    # Elegir el color con mayor frecuencia, y si hay empate,
    # el que tenga la racha más larga
    return max(ft.keys(), key=lambda c: (ft[c], br.get(c, 0)))


# ============================================================
# HEURÍSTICA H2: Priorización de Movimientos
# ============================================================
# Idea: No todos los movimientos son iguales. Algunos son mejores
# que otros. Ordenamos los movimientos por calidad.

def priority_tuple(s: State, i: int, j: int) -> tuple:
    """
    Calcula una "tupla de prioridad" para un movimiento (i -> j).
    
    Las tuplas más pequeñas (según orden lexicográfico) representan
    movimientos MEJORES. Esto permite ordenar los movimientos.
    
    Componentes de la tupla (de mayor a menor importancia):
    1. ¿Consolida color? (0 = sí, 1 = no) - Consolidar es mejor
    2. Negativo de racha en destino - Más racha = mejor
    3. Negativo de racha en origen - Sacar de racha larga = mejor
    4. ¿Destino vacío? (0 = no, 1 = sí) - Consolidar > usar buffer
    5. Espacios libres en destino - Más espacio = mejor
    6. ¿Rompe pila pura? (0 = no, 1 = sí) - No romper pilas puras
    
    Ejemplo:
        priority_tuple(estado, 0, 1) -> (0, -3, -2, 0, 2, 0)
        (mejor que uno que retorne (1, -1, -1, 1, 3, 1))
    """
    p_src, p_dst = s[i], s[j]
    c = top(p_src)
    
    # Defensivo: no debería pasar si se verifica con puede_mover primero
    if c is None:
        return (999, 0, 0, 0, 0, 0)  # Prioridad muy baja
    
    # Análisis del movimiento
    same_color = (bool(p_dst) and top(p_dst) == c)  # ¿Consolida?
    run_after = run_len_superior(tuple(list(p_dst) + [c]))  # Ra cha después
    run_before = run_len_superior(p_src)  # Rach a antes
    dest_empty = (len(p_dst) == 0)  # ¿Buffer?
    dest_free = free_slots(p_dst)  # Espacios libres
    break_pure = (len(p_src) > 1 and all(x == p_src[0] for x in p_src))  # ¿Rompe pura?
    
    # Calcular espacios libres DESPUÉS del movimiento
    espacios_despues = dest_free - 1 if not dest_empty else MAX_CAP - 1
    
    # Detectar si el destino es buffer (última pila)
    es_buffer = (j == len(s) - 1)
    
    # REGLA MEJORADA: Preferir buffer cuando consolidamos
    # para no contaminar pilas de trabajo innecesariamente
    preferir_buffer = 1  # Por defecto, no preferir buffer
    if same_color:  # Si estamos consolidando
        if es_buffer:
            preferir_buffer = 0  # Preferir buffer si es buffer (menor = mejor)
        else:
            preferir_buffer = 1  # Penalizar usar pilas de trabajo
    
    return (
        0 if same_color else 1,        # (1) Consolidar es mejor
        preferir_buffer,               # (2) Preferir buffer cuando consolidamos (0=buffer, 1=pila trabajo)
        -run_after,                    # (3) Más racha en destino = mejor (negativo porque queremos minimizar)
        -run_before,                   # (4) Sacar de racha larga = mejor
        0 if not dest_empty else 1,    # (5) Consolidar > usar buffer vacío
        -espacios_despues,             # (6) Más espacios libres después = mejor
        1 if break_pure else 0         # (7) No romper pilas puras
    )


# ============================================================
# GENERACIÓN DE MOVIMIENTOS ORDENADOS
# ============================================================
# Genera todos los movimientos legales, pero ordenados por calidad
# (usando las heurísticas H1 y H2).

def generar_movimientos_ordenados(s: State) -> List[tuple]:
    """
    Genera todos los movimientos legales desde el estado s,
    ordenados por calidad según las heurísticas.
    
    Estrategia:
    1. Excluir pilas terminadas (no pueden ser origen ni destino)
    2. Identificar el "color foco" (H1)
    3. Separar movimientos: los que involucran el color foco vs otros
    4. Ordenar cada grupo por prioridad (H2)
    5. Retornar: primero movimientos del color foco, luego otros
    
    IMPORTANTE: Las pilas terminadas (con 5 tuercas del mismo color)
    se excluyen completamente de los movimientos (ni origen ni destino).
    
    Retorna lista de tuplas (i, j) representando movimientos i -> j.
    """
    N = len(s)
    foco = elegir_color_foco(s)
    
    # Separar movimientos en dos grupos
    grupo_foco = []      # Movimientos que involucran el color foco
    grupo_otros = []     # Otros movimientos
    
    # Generar todos los movimientos posibles
    for i in range(N):
        # EXCLUIR pilas terminadas como origen
        if pila_terminada(s[i]):
            continue
        
        for j in range(N):
            if i == j:  # No podemos mover de una pila a sí misma
                continue
            
            # EXCLUIR pilas terminadas como destino
            if pila_terminada(s[j]):
                continue
            
            if puede_mover(s[i], s[j]):  # Verificar que sea legal
                # Clasificar según si involucra el color foco
                if foco is not None and s[i] and top(s[i]) == foco:
                    grupo_foco.append((i, j))
                else:
                    grupo_otros.append((i, j))
    
    # Ordenar cada grupo por prioridad (tupla más pequeña = mejor)
    grupo_foco.sort(key=lambda mv: priority_tuple(s, *mv))
    grupo_otros.sort(key=lambda mv: priority_tuple(s, *mv))
    
    # Retornar: primero los del color foco (más importantes)
    return grupo_foco + grupo_otros


# ============================================================
# ALGORITMO PRINCIPAL: BACKTRACKING DFS
# ============================================================
# Este es el corazón del algoritmo. Usa búsqueda en profundidad
# con backtracking para encontrar una solución.

@dataclass
class SearchStats:
    """
    Estadísticas de la búsqueda.
    - expanded: Número de estados expandidos (visitados)
    - max_depth: Profundidad máxima alcanzada en el árbol de búsqueda
    """
    expanded: int = 0
    max_depth: int = 0


def solve_backtracking(start: State, max_expansions: Optional[int] = None) -> Tuple[Optional[List[tuple]], SearchStats]:
    """
    Resuelve el problema usando backtracking con DFS (búsqueda en profundidad).
    
    Estrategia:
    1. Mantener un conjunto de estados visitados (para evitar ciclos)
    2. Usar recursión para explorar el árbol de estados
    3. En cada estado, generar movimientos ordenados por heurísticas
    4. Probar cada movimiento (backtrack si no lleva a solución)
    5. Evitar movimientos reversos inmediatos (i->j luego j->i)
    
    Parámetros:
        start: Estado inicial
        max_expansions: Límite opcional de estados a expandir (para evitar loops infinitos)
    
    Retorna:
        (solucion, stats) donde:
        - solucion: Lista de movimientos (i, j) que llevan a la solución, o None si no hay
        - stats: Estadísticas de la búsqueda
    """
    # Conjunto de estados ya visitados (evita ciclos)
    visited: Set[State] = {start}
    stats = SearchStats()

    def dfs(s: State, path: List[tuple], last_move: Optional[tuple]) -> Optional[List[tuple]]:
        """
        Función recursiva de búsqueda en profundidad.
        
        Parámetros:
            s: Estado actual
            path: Secuencia de movimientos desde el inicio hasta s
            last_move: Último movimiento realizado (para evitar reversos)
        
        Retorna:
            Lista de movimientos solución, o None si no hay solución desde aquí
        """
        # Incrementar contador de expansiones
        stats.expanded += 1
        stats.max_depth = max(stats.max_depth, len(path))
        
        # Verificar límite de expansiones (safety check)
        if max_expansions and stats.expanded >= max_expansions:
            return None
        
        # CASO BASE: ¿Hemos alcanzado el objetivo?
        if is_goal(s):
            return path  # ¡Solución encontrada!
        
        # Obtener movimientos legales ordenados por heurísticas
        moves = generar_movimientos_ordenados(s)
        
        # Intentar cada movimiento posible
        for (i, j) in moves:
            # Evitar movimientos reversos inmediatos (optimización)
            # Si acabamos de hacer j->i, no hacer i->j inmediatamente
            if last_move and (j, i) == last_move:
                continue
            
            # VALIDACIÓN ADICIONAL: Verificar una vez más antes de aplicar
            # (en caso de que el estado haya cambiado desde que se generaron los movimientos)
            if not puede_mover(s[i], s[j]):
                continue  # Saltar este movimiento si ya no es válido
            
            try:
                # Aplicar el movimiento para obtener nuevo estado
                nuevo_estado = aplicar_movimiento(s, i, j)
            except (ValueError, IndexError) as e:
                # Si hay error al aplicar movimiento, registrarlo y continuar
                # (no debería pasar, pero es defensivo)
                continue
            
            # Evitar ciclos: si ya visitamos este estado, saltarlo
            if nuevo_estado in visited:
                continue
            
            # Marcar como visitado y explorar recursivamente
            visited.add(nuevo_estado)
            solucion = dfs(nuevo_estado, path + [(i, j)], (i, j))
            
            # Si encontramos solución, retornarla inmediatamente
            if solucion is not None:
                return solucion
        
        # Si ningún movimiento llevó a solución, retornar None (backtrack)
        return None

    # Iniciar la búsqueda desde el estado inicial
    solucion = dfs(start, [], None)
    
    return solucion, stats
