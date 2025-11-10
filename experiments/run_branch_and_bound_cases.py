"""
Ejecutor de casos predefinidos para Branch and Bound.

Usa la misma batería que el script de backtracking para facilitar la comparación.
"""

from __future__ import annotations

import importlib
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
BAB_DIR = BASE_DIR / "algorithms" / "branch_and_bound"

if str(BAB_DIR) not in sys.path:
    sys.path.insert(0, str(BAB_DIR))

bab_core = importlib.import_module("core")
bab_utils = importlib.import_module("utils")

State = bab_core.State  # type: ignore[attr-defined]
solve_branch_and_bound = bab_core.solve_branch_and_bound  # type: ignore[attr-defined]
dibujar_estado = bab_utils.dibujar_estado  # type: ignore[attr-defined]
validar_instancia_inicial = bab_utils.validar_instancia_inicial  # type: ignore[attr-defined]


Color = str


@dataclass
class CasoPrueba:
    nombre: str
    colores: Tuple[Color, ...]
    estado: State
    descripcion: str
    max_expansions: int = 1_000_000


CASOS: Tuple[CasoPrueba, ...] = (
    CasoPrueba(
        nombre="bnb_facil_3_colores",
        colores=("R", "G", "B"),
        estado=(
            ("R", "G", "B", "R", "G"),
            ("B", "R", "G", "B", "R"),
            ("G", "B", "R", "G", "B"),
            tuple(),
        ),
        descripcion="Instancia equilibrada de 3 colores totalmente mezclada.",
    ),
    CasoPrueba(
        nombre="bnb_medio_4_colores",
        colores=("R", "G", "B", "Y"),
        estado=(
            ("R", "Y", "G", "B", "R"),
            ("Y", "B", "R", "G", "Y"),
            ("G", "R", "Y", "B", "G"),
            ("B", "G", "B", "Y", "R"),
            tuple(),
        ),
        descripcion="Instancia con 4 colores y buffer vacío, mezcla uniforme.",
    ),
    CasoPrueba(
        nombre="bnb_dificil_5_colores",
        colores=("R", "G", "B", "Y", "O"),
        estado=(
            ("R", "G", "O", "B", "Y"),
            ("Y", "R", "G", "O", "B"),
            ("B", "Y", "R", "G", "O"),
            ("O", "B", "Y", "R", "G"),
            ("G", "O", "B", "Y", "R"),
            tuple(),
        ),
        descripcion="Instancia densa de 5 colores; cada color distribuye una vez por pila.",
    ),
    CasoPrueba(
        nombre="bnb_casi_resuelto",
        colores=("R", "G", "B"),
        estado=(
            ("R", "R", "R", "R", "G"),
            ("G", "G", "G", "G", "B"),
            ("B", "B", "B", "B", "R"),
            tuple(),
        ),
        descripcion="Casi resuelto; sirve para medir tiempos muy cortos.",
    ),
    CasoPrueba(
        nombre="bnb_insoluble_conteo_invalido",
        colores=("R", "G", "B"),
        estado=(
            ("R", "R", "R", "R", "R"),
            ("R", "G", "G", "G", "G"),
            ("B", "B", "B", "B", "B"),
            tuple(),
        ),
        descripcion=(
            "Instancia deliberadamente insoluble (6 rojas y 4 verdes). "
            "El algoritmo debe reportar que no hay solución."
        ),
        max_expansions=500_000,
    ),
)


def formatear_tiempo(segundos: float) -> str:
    return f"{segundos:0.6f} s"


def ejecutar_caso(caso: CasoPrueba) -> dict:
    try:
        validar_instancia_inicial(caso.estado, caso.colores)
    except AssertionError as exc:
        return {
            "nombre": caso.nombre,
            "valido": False,
            "error": f"Validación falló: {exc}",
        }

    inicio = time.perf_counter()
    solucion, stats = solve_branch_and_bound(
        caso.estado,
        max_expansions=caso.max_expansions,
    )
    duracion = time.perf_counter() - inicio

    mejor_cota = stats.mejor_cota_encontrada
    if mejor_cota in {float("inf"), bab_core.math.inf}:  # type: ignore[attr-defined]
        mejor_cota = None

    return {
        "nombre": caso.nombre,
        "descripcion": caso.descripcion,
        "colores": "".join(caso.colores),
        "estado": dibujar_estado(caso.estado),
        "valido": True,
        "resuelto": solucion is not None,
        "movimientos": len(solucion) if solucion else 0,
        "expanded": stats.expanded,
        "pruned": stats.pruned,
        "max_depth": stats.max_depth,
        "mejor_cota": mejor_cota,
        "tiempo": duracion,
        "limite_alcanzado": (
            stats.expanded >= caso.max_expansions if solucion is None else False
        ),
    }


def imprimir_resultados(resultados: Iterable[dict]) -> None:
    ancho = 84
    separador = "-" * ancho
    for resultado in resultados:
        print(separador)
        print(f"Caso: {resultado['nombre']}")
        print(f"Descripción: {resultado.get('descripcion', '')}")
        print(f"Colores: {resultado.get('colores', '-')}")
        print(f"Estado inicial: {resultado.get('estado', '-')}")

        if not resultado["valido"]:
            print(f"❌ Estado inválido: {resultado['error']}")
            continue

        print(f"Resuelto: {'Sí' if resultado['resuelto'] else 'No'}")
        if resultado["resuelto"]:
            print(f"Movimientos: {resultado['movimientos']}")
        if resultado.get("limite_alcanzado"):
            print("⚠️  Se alcanzó el límite de expansiones especificado.")
        print(f"Nodos expandidos: {resultado['expanded']:,}")
        print(f"Nodos podados: {resultado['pruned']:,}")
        print(f"Profundidad máxima: {resultado['max_depth']:,}")
        if resultado.get("mejor_cota") is not None:
            print(f"Mejor cota encontrada: {resultado['mejor_cota']}")
        print(f"Tiempo: {formatear_tiempo(resultado['tiempo'])}")
    print(separador)


def main() -> None:
    resultados = [ejecutar_caso(caso) for caso in CASOS]
    imprimir_resultados(resultados)


if __name__ == "__main__":
    main()


