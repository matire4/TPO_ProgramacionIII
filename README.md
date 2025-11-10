# 🔩 Nut Sort – Backtracking & Branch and Bound

Implementación minimalista del problema Nut Sort con dos enfoques de búsqueda:

- **Backtracking** (`algorithms/backtracking/core.py`)
- **Branch and Bound** (`algorithms/branch_and_bound/core.py`)

Ambos algoritmos se exponen mediante un único backend Flask y una interfaz web ligera.

## 📁 Contenido Relevante

```
NutSort/
├── server.py             # API Flask con selector de algoritmos
├── requirements.txt      # Dependencias mínimas
├── algorithms/
│   ├── backtracking/
│   │   ├── core.py       # Algoritmo puro + heurísticas
│   │   └── utils.py      # Validaciones y generación de instancias
│   └── branch_and_bound/
│       ├── core.py       # Algoritmo Branch and Bound con podas
│       └── utils.py      # Utilidades compartidas
├── experiments/
│   └── run_backtracking_cases.py  # Casos de prueba medibles para BT
├── web/
│   ├── index.html        # Interfaz web (selector + visualización)
│   └── styles.css        # Estilos básicos
└── data/
    └── estados_usados.json  # Persistencia de estados aleatorios
```

## 🚀 Cómo Ejecutarlo (local)

```bash
cd NutSort
pip install -r requirements.txt
python server.py
```

Luego abre `http://localhost:5000` en tu navegador.

### Medir casos de Backtracking (Parte 1)

```bash
cd NutSort
python -m experiments.run_backtracking_cases
```

El script imprime tiempos, nodos expandidos y profundidad para cinco instancias representativas (incluye un caso insoluble).

### Comparaciones masivas y gráficos

```bash
cd NutSort
python -m experiments.run_batch_comparison          # Genera CSV (50 casos)
python -m experiments.generar_graficos              # Requiere pandas/matplotlib
```

> Dependencias opcionales para gráficos: `pip install -r experiments/requirements-analytics.txt`

Gráficos exportados en `experiments/plots/`. Resumen textual sugerido: `docs/informe_borrador.txt`.

## 🌐 Despliegue rápido en Vercel (estático + API)

El repositorio ya incluye la configuración necesaria (`vercel.json`, `api/server.py`).

```bash
cd NutSort
pip install vercel
vercel login
vercel            # primer despliegue (elige tu cuenta/proyecto)
vercel --prod     # despliegue a producción
```

- Los archivos en `web/` se publican como sitio estático.
- Las rutas `/api/*` sirven la API Flask empaquetada con `vercel-python-wsgi`.
- El frontend detecta automáticamente el backend en el mismo dominio; si prefieres otro dominio, define `window.API_URL_OVERRIDE` antes de cargar `web/index.html`.

## 📌 Notas

- Los algoritmos comparten el mismo formato de estado (`Tuple[Tuple[str, ...], ...]`).
- `utils.py` de cada algoritmo expone validaciones y generación aleatoria reutilizando `core.py`.
- El backend carga dinámicamente cada algoritmo y ofrece endpoints comunes:
  - `GET /api/algoritmos`
  - `POST /api/generar-aleatorio`
  - `POST /api/validar-estado`
  - `POST /api/resolver`
- `data/estados_usados.json` evita repetir casos aleatorios ya servidos.

## 🧪 Probar los algoritmos desde Python

```python
from algorithms.backtracking.core import solve_backtracking, State

estado: State = (
    ("G","Y","Y","O","G"),
    ("R","B","B","Y","R"),
    ("G","R","R","G","G"),
    ("O","B","Y","B","O"),
    ("O","Y","R","G","B"),
    tuple(),
)

solucion, stats = solve_backtracking(estado, max_expansions=500000)

print(solucion)
print(stats.expanded, stats.max_depth)
```

Repite el mismo esquema importando `solve_branch_and_bound` para comparar resultados.

## ✅ Checklist

- [x] Algoritmos de búsqueda auto-contenidos.
- [x] Servidor Flask listo para producción ligera.
- [x] Frontend HTML/CSS sin dependencias externas.
- [x] Persistencia opcional de estados generados.

