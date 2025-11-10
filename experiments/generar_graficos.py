"""
Generador de gráficos a partir de los resultados experimentales.

Uso:
    cd NutSort
    python -m experiments.generar_graficos

Salida:
    experiments/plots/promedios_por_algoritmo.png
    experiments/plots/tiempo_por_categoria.png
    experiments/plots/podas_por_categoria.png
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover - ayuda interactiva
    missing = "pandas" if "pandas" in str(exc) else "matplotlib"
    raise SystemExit(
        f"Falta instalar dependencias ({missing}). Ejecuta: pip install pandas matplotlib"
    ) from exc


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "resultados_batch.csv"
PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)


def cargar_datos() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    df["pruned"] = df["pruned"].fillna(0)
    return df


def plot_promedios_por_algoritmo(df: pd.DataFrame) -> None:
    resumen = (
        df.groupby("algoritmo")
        .agg(
            movimientos=("movimientos", "mean"),
            tiempo=("time", "mean"),
            expandidos=("expanded", "mean"),
            podados=("pruned", "mean"),
        )
        .reset_index()
    )

    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    fig.suptitle("Promedios por algoritmo (50 casos)")

    resumen.plot(x="algoritmo", y="movimientos", kind="bar", ax=axes[0, 0], legend=False)
    axes[0, 0].set_ylabel("Movimientos promedio")

    resumen.assign(tiempo_ms=resumen["tiempo"] * 1000).plot(
        x="algoritmo", y="tiempo_ms", kind="bar", ax=axes[0, 1], legend=False
    )
    axes[0, 1].set_ylabel("Tiempo promedio (ms)")

    resumen.plot(x="algoritmo", y="expandidos", kind="bar", ax=axes[1, 0], legend=False)
    axes[1, 0].set_ylabel("Nodos expandidos promedio")

    resumen.plot(x="algoritmo", y="podados", kind="bar", ax=axes[1, 1], legend=False, color="#ff7f0e")
    axes[1, 1].set_ylabel("Nodos podados promedio")

    for ax in axes.flat:
        ax.set_xlabel("")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.grid(axis="y", linestyle="--", alpha=0.3)

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(PLOTS_DIR / "promedios_por_algoritmo.png", dpi=180)
    plt.close(fig)


def plot_tiempo_por_categoria(df: pd.DataFrame) -> None:
    resumen = (
        df.groupby(["categoria", "algoritmo"])
        .agg(tiempo=("time", "mean"))
        .reset_index()
    )
    resumen["tiempo_ms"] = resumen["tiempo"] * 1000
    pivot = resumen.pivot(index="categoria", columns="algoritmo", values="tiempo_ms").fillna(0)

    ax = pivot.plot(kind="bar", figsize=(8, 5))
    ax.set_title("Tiempo promedio por categoría")
    ax.set_ylabel("Tiempo medio (ms)")
    ax.set_xlabel("Categoría")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "tiempo_por_categoria.png", dpi=180)
    plt.close()


def plot_podas_por_categoria(df: pd.DataFrame) -> None:
    resumen = (
        df[df["algoritmo"] == "branch_and_bound"]
        .groupby("categoria")
        .agg(podas=("pruned", "mean"))
        .reset_index()
    )

    ax = resumen.plot(x="categoria", y="podas", kind="bar", legend=False, figsize=(7, 4), color="#ff7f0e")
    ax.set_title("Podas promedio por categoría (Branch & Bound)")
    ax.set_ylabel("Podas promedio")
    ax.set_xlabel("Categoría")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "podas_por_categoria.png", dpi=180)
    plt.close()


def main() -> None:
    df = cargar_datos()
    plot_promedios_por_algoritmo(df)
    plot_tiempo_por_categoria(df)
    plot_podas_por_categoria(df)
    print(f"[OK] Gráficos guardados en {PLOTS_DIR}")


if __name__ == "__main__":
    main()

