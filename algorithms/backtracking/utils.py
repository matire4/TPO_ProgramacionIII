# ============================================================
# Nut Sort - Complementos y Utilidades
# ============================================================
# Este archivo contiene:
# - Funciones de visualización y utilidades
# - Generación de casos aleatorios
# - Validaciones de entrada
# - Ejemplo de uso del algoritmo de backtracking
#
# El algoritmo de backtracking puro está en: core.py
# ============================================================

from typing import Tuple, List, Optional, Set
import random
import json
import os

# Importar el algoritmo de backtracking desde el módulo core
from core import (
    State, Pile, Color, MAX_CAP,
    solve_backtracking, SearchStats,
    aplicar_movimiento  # Necesaria para reconstruir
)

# ============================================================
# UTILIDADES DE VISUALIZACIÓN
# ============================================================

def dibujar_estado(s: State) -> str:
    """
    Convierte un estado a una representación de texto legible.
    
    Ejemplo:
        dibujar_estado((("R","G"), ("Y",), ())) 
        -> "P0: R G | P1: Y | P2: ∅"
    """
    cols = []
    for k, p in enumerate(s):
        if p:
            cols.append(f"P{k}: " + " ".join(p))
        else:
            cols.append(f"P{k}: ∅")
    return " | ".join(cols)


def reconstruir_y_mostrar(start: State, path: List[tuple]) -> None:
    """
    Reconstruye y muestra la secuencia completa de estados desde
    el inicio hasta la solución.
    
    Útil para ver cómo el algoritmo va resolviendo el problema paso a paso.
    """
    s = start
    print("  S0:", dibujar_estado(s))
    for t, (i, j) in enumerate(path, 1):
        s = aplicar_movimiento(s, i, j)
        print(f"  S{t}:", dibujar_estado(s))


# ============================================================
# VALIDACIONES DE ENTRADA
# ============================================================

def validar_instancia_inicial(s: State, colores: Tuple[Color, ...]) -> None:
    """
    Valida que un estado inicial cumpla con las reglas del problema:
    1. Debe haber (#colores + 1) pilas (una es el buffer)
    2. Las primeras N pilas deben estar llenas (MAX_CAP tuercas)
    3. La última pila (buffer) debe estar vacía
    
    Lanza AssertionError si alguna validación falla.
    """
    assert len(s) == len(colores) + 1, \
        f"Esperaba {len(colores)+1} pernos, hay {len(s)}"
    
    for k, p in enumerate(s[:-1]):
        assert len(p) == MAX_CAP, \
            f"Pila P{k} no está llena (len={len(p)}, esperado {MAX_CAP})"
    
    assert len(s[-1]) == 0, \
        "El último perno debe estar vacío (buffer)"


# ============================================================
# GENERACIÓN DE CASOS ALEATORIOS
# ============================================================

def generar_estado_aleatorio(colores: Tuple[Color, ...], seed: Optional[int] = None) -> State:
    """
    Genera un estado inicial aleatorio válido.
    
    Distribuye aleatoriamente las tuercas en las pilas:
    - N*MAX_CAP tuercas totales (5 de cada color)
    - N pilas llenas (una por color)
    - 1 pila vacía (buffer)
    
    Parámetros:
        colores: Tupla con los colores disponibles
        seed: Semilla para reproducibilidad (opcional)
    
    Retorna:
        Estado válido aleatorio
    """
    if seed is not None:
        random.seed(seed)
    
    N = len(colores)
    # Necesitamos N*MAX_CAP tuercas en total (distribuidas en N pilas)
    tuercas = list(colores) * MAX_CAP
    random.shuffle(tuercas)
    
    pilas = []
    for i in range(N):
        pila = tuple(tuercas[i*MAX_CAP:(i+1)*MAX_CAP])
        pilas.append(pila)
    
    # Última pila es el buffer (vacía)
    pilas.append(tuple())
    
    return tuple(pilas)


def estado_a_string(s: State) -> str:
    """Convierte un estado a string JSON para almacenamiento/hash."""
    return json.dumps(s, sort_keys=True)


def cargar_estados_usados(archivo: str = None) -> Set[str]:
    """
    Carga el conjunto de estados ya generados desde un archivo JSON.
    
    Útil para evitar generar el mismo estado dos veces.
    """
    if archivo is None:
        # Usar ruta relativa a la carpeta data
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        archivo = os.path.join(BASE_DIR, 'data', 'estados_usados.json')
    
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('estados', []))
    return set()


def guardar_estado_usado(s: State, archivo: str = None) -> None:
    """Guarda un estado en la lista de estados usados."""
    if archivo is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        archivo = os.path.join(BASE_DIR, 'data', 'estados_usados.json')
    
    estados = cargar_estados_usados(archivo)
    estados.add(estado_a_string(s))
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump({'estados': list(estados)}, f, indent=2)


def generar_estado_aleatorio_unico(colores: Tuple[Color, ...], max_intentos: int = 1000) -> Optional[State]:
    """
    Genera un estado aleatorio que no haya sido usado antes.
    
    Intenta hasta encontrar uno único o hasta max_intentos.
    Guarda automáticamente los estados generados.
    
    Retorna None si no se pudo generar uno único.
    """
    estados_usados = cargar_estados_usados()
    intentos = 0
    
    while intentos < max_intentos:
        # Usar combinación única como seed para asegurar diferencias
        seed = hash((id(colores), intentos, random.random()))
        estado = generar_estado_aleatorio(colores, seed)
        estado_str = estado_a_string(estado)
        
        if estado_str not in estados_usados:
            guardar_estado_usado(estado)
            return estado
        intentos += 1
    
    return None


def string_a_estado(s: str) -> State:
    """Convierte un string JSON a State."""
    return tuple(tuple(p) for p in json.loads(s))


# ============================================================
# EJEMPLO DE USO
# ============================================================

if __name__ == "__main__":
    # Ejemplo básico: usar el algoritmo con un estado manual
    print("=" * 60)
    print("EJEMPLO DE USO DEL ALGORITMO DE BACKTRACKING")
    print("=" * 60)
    
    # Colores disponibles
    colores = ("G", "Y", "O", "R", "B")
    
    # Estado inicial (del ejemplo original)
    start_img_like: State = (
        ("G","Y","Y","O","G"),  # P0
        ("R","B","B","Y","R"),  # P1
        ("G","R","R","G","G"),  # P2
        ("O","B","Y","B","O"),  # P3
        ("O","Y","R","G","B"),  # P4
        tuple(),                # P5 (buffer)
    )
    
    # Validar que el estado es correcto
    try:
        validar_instancia_inicial(start_img_like, colores)
        print("✓ Estado inicial válido")
    except AssertionError as e:
        print(f"✗ Error en estado inicial: {e}")
        exit(1)
    
    print(f"Estado inicial: {dibujar_estado(start_img_like)}")
    print("\nEjecutando backtracking...")
    
    # Resolver usando el algoritmo del core
    path, stats = solve_backtracking(start_img_like, max_expansions=500000)
    
    print("\n" + "=" * 60)
    print("RESULTADO:")
    print("=" * 60)
    
    if path is None:
        print("✗ No se encontró solución (o se alcanzó el límite de expansiones)")
    else:
        print(f"✓ Solución encontrada en {len(path)} movimientos")
        print(f"\nMovimientos: {path}")
        print("\nSecuencia de estados:")
        reconstruir_y_mostrar(start_img_like, path)
    
    print("\n" + "=" * 60)
    print("MÉTRICAS:")
    print("=" * 60)
    print(f"  Nodos expandidos: {stats.expanded}")
    print(f"  Profundidad máxima: {stats.max_depth}")
