# ============================================================
# Servidor Flask común para múltiples algoritmos
# ============================================================
# Este servidor permite que el frontend HTML se comunique con
# diferentes algoritmos (Backtracking, Branch and Bound, etc.)
# ============================================================

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from typing import Tuple
import os
import sys
import importlib.util
import math

# Configurar rutas relativas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALGORITHMS_DIR = os.path.join(BASE_DIR, 'algorithms')
BACKTRACKING_SRC = os.path.join(ALGORITHMS_DIR, 'backtracking')
BRANCH_AND_BOUND_SRC = os.path.join(ALGORITHMS_DIR, 'branch_and_bound')
WEB_DIR = os.path.join(BASE_DIR, 'web')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Agregar las carpetas de algoritmos al path
if BACKTRACKING_SRC not in sys.path:
    sys.path.insert(0, BACKTRACKING_SRC)
if BRANCH_AND_BOUND_SRC not in sys.path:
    sys.path.insert(0, BRANCH_AND_BOUND_SRC)

app = Flask(__name__, static_folder=WEB_DIR)
CORS(app)  # Permitir solicitudes desde el frontend

# Importar módulos de algoritmos dinámicamente
backtracking_module = None
branch_and_bound_module = None

def load_module_from_path(module_name, module_path):
    """Carga un módulo desde una ruta específica usando importlib"""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ImportError(f"No se pudo crear spec para {module_name} desde {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_backtracking():
    """Carga el módulo de backtracking"""
    global backtracking_module
    if backtracking_module is None:
        try:
            # Cargar módulos usando importlib para evitar conflictos
            # IMPORTANTE: Cargar core primero porque utils lo importa
            core_path = os.path.join(BACKTRACKING_SRC, 'core.py')
            utils_path = os.path.join(BACKTRACKING_SRC, 'utils.py')
            
            # Guardar estado original
            original_sys_path = sys.path.copy()
            original_cwd = os.getcwd()
            
            # Agregar el directorio de backtracking al path
            sys.path.insert(0, BACKTRACKING_SRC)
            
            # Cargar core primero
            core_module = load_module_from_path('backtracking_core', core_path)
            
            # Registrar 'core' en el namespace del directorio para que utils pueda importarlo
            # Usar un nombre específico para evitar conflictos
            sys.modules['backtracking.core'] = core_module
            # También registrar como 'core' dentro del contexto del directorio
            sys.modules['core'] = core_module
            
            # Cambiar al directorio de backtracking para que los imports relativos funcionen
            os.chdir(BACKTRACKING_SRC)
            
            # Ahora cargar utils (que importa desde core)
            utils_module = load_module_from_path('backtracking_utils', utils_path)
            
            # Restaurar estado
            sys.path = original_sys_path
            os.chdir(original_cwd)
            
            backtracking_module = {
                'State': core_module.State,
                'solve_backtracking': core_module.solve_backtracking,
                'MAX_CAP': core_module.MAX_CAP,
                'validar_instancia_inicial': utils_module.validar_instancia_inicial,
                'generar_estado_aleatorio_unico': utils_module.generar_estado_aleatorio_unico,
                'dibujar_estado': utils_module.dibujar_estado,
                'reconstruir_y_mostrar': utils_module.reconstruir_y_mostrar,
                'estado_a_string': utils_module.estado_a_string
            }
            print("✓ Módulo de Backtracking cargado correctamente")
        except Exception as e:
            print(f"✗ Error cargando backtracking: {e}")
            import traceback
            traceback.print_exc()
            backtracking_module = None
    return backtracking_module


def load_branch_and_bound():
    """Carga el módulo de Branch and Bound"""
    global branch_and_bound_module
    if branch_and_bound_module is None:
        try:
            # Cargar módulos usando importlib para evitar conflictos
            # IMPORTANTE: Cargar core primero porque utils lo importa
            core_path = os.path.join(BRANCH_AND_BOUND_SRC, 'core.py')
            utils_path = os.path.join(BRANCH_AND_BOUND_SRC, 'utils.py')
            
            # Guardar estado original
            original_sys_path = sys.path.copy()
            original_cwd = os.getcwd()
            
            # Agregar el directorio de branch_and_bound al path
            sys.path.insert(0, BRANCH_AND_BOUND_SRC)
            
            # Cargar core primero
            core_module = load_module_from_path('branch_and_bound_core', core_path)
            
            # Registrar 'core' en el namespace del directorio para que utils pueda importarlo
            # Usar un nombre específico para evitar conflictos
            sys.modules['branch_and_bound.core'] = core_module
            # También registrar como 'core' dentro del contexto del directorio
            sys.modules['core'] = core_module
            
            # Cambiar al directorio de branch_and_bound para que los imports relativos funcionen
            os.chdir(BRANCH_AND_BOUND_SRC)
            
            # Ahora cargar utils (que importa desde core)
            utils_module = load_module_from_path('branch_and_bound_utils', utils_path)
            
            # Restaurar estado
            sys.path = original_sys_path
            os.chdir(original_cwd)
            
            branch_and_bound_module = {
                'State': core_module.State,
                'solve_branch_and_bound': core_module.solve_branch_and_bound,
                'MAX_CAP': core_module.MAX_CAP,
                'validar_instancia_inicial': utils_module.validar_instancia_inicial,
                'generar_estado_aleatorio_unico': utils_module.generar_estado_aleatorio_unico,
                'dibujar_estado': utils_module.dibujar_estado,
                'reconstruir_y_mostrar': utils_module.reconstruir_y_mostrar,
                'estado_a_string': utils_module.estado_a_string
            }
            print("✓ Módulo de Branch and Bound cargado correctamente")
        except Exception as e:
            print(f"✗ Error cargando branch_and_bound: {e}")
            import traceback
            traceback.print_exc()
            branch_and_bound_module = None
    return branch_and_bound_module


@app.route('/')
def index():
    """Servir la página HTML principal."""
    return send_from_directory(WEB_DIR, 'index.html')


@app.route('/styles.css')
def styles():
    """Servir el archivo CSS."""
    return send_from_directory(WEB_DIR, 'styles.css')


@app.route('/api/algoritmos', methods=['GET'])
def listar_algoritmos():
    """Lista los algoritmos disponibles."""
    algoritmos = []
    
    # Backtracking
    if load_backtracking():
        algoritmos.append({
            'id': 'backtracking',
            'nombre': 'Backtracking',
            'descripcion': 'Búsqueda en profundidad con vuelta atrás'
        })
    
    # Branch and Bound
    if load_branch_and_bound():
        algoritmos.append({
            'id': 'branch_and_bound',
            'nombre': 'Branch and Bound',
            'descripcion': 'Búsqueda con poda de ramas y heurísticas agresivas'
        })
    
    return jsonify({
        "success": True,
        "algoritmos": algoritmos
    })


@app.route('/api/generar-aleatorio', methods=['POST'])
def generar_aleatorio():
    """
    Genera un estado aleatorio único.
    
    Body (JSON):
        {
            "algoritmo": "backtracking",
            "colores": ["R", "G", "B", ...],
            "numColores": 5
        }
    """
    try:
        data = request.json
        algoritmo = data.get('algoritmo', 'backtracking')
        colores_str = data.get('colores', [])
        num_colores = data.get('numColores', len(colores_str))
        
        # Convertir a tupla de colores (soporta hasta 15 colores)
        if not colores_str:
            COLORES_STANDARD = ['R', 'G', 'B', 'Y', 'O', 'V', 'P', 'C', 'M', 'S', 'L', 'T', 'D', 'A', 'I']
            colores = tuple(COLORES_STANDARD[:num_colores])
        else:
            colores = tuple(colores_str)
        
        # Seleccionar módulo según algoritmo
        if algoritmo == 'backtracking':
            mod = load_backtracking()
            if not mod:
                return jsonify({
                    "success": False,
                    "error": "Módulo de backtracking no disponible"
                }), 500
        elif algoritmo == 'branch_and_bound':
            mod = load_branch_and_bound()
            if not mod:
                return jsonify({
                    "success": False,
                    "error": "Módulo de Branch and Bound no disponible"
                }), 500
        else:
            return jsonify({
                "success": False,
                "error": f"Algoritmo '{algoritmo}' no disponible"
            }), 400
        
        # Generar estado aleatorio único (ambos algoritmos usan la misma función)
        estado = mod['generar_estado_aleatorio_unico'](colores)
        
        if estado is None:
            return jsonify({
                "success": False,
                "error": "No se pudo generar un estado único. Intenta de nuevo."
            }), 400
        
        # Convertir a lista para JSON
        estado_lista = [list(p) for p in estado]
        
        return jsonify({
            "success": True,
            "estado": estado_lista,
            "colores": list(colores),
            "mensaje": f"Estado aleatorio generado exitosamente"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/resolver', methods=['POST'])
def resolver():
    """
    Resuelve un estado usando el algoritmo especificado.
    
    Body (JSON):
        {
            "algoritmo": "backtracking",
            "estado": [[...], [...], ...],
            "colores": ["R", "G", "B", ...],
            "max_expansions": 500000
        }
    """
    try:
        data = request.json
        algoritmo = data.get('algoritmo', 'backtracking')
        estado_lista = data.get('estado', [])
        colores_str = data.get('colores', [])
        max_expansions = data.get('max_expansions', 500000)
        
        if not estado_lista:
            return jsonify({
                "success": False,
                "error": "No se proporcionó un estado"
            }), 400
        
        # Convertir a State (tupla de tuplas)
        estado = tuple(tuple(p) for p in estado_lista)
        colores = tuple(colores_str) if colores_str else None
        
        # Seleccionar módulo según algoritmo
        if algoritmo == 'backtracking':
            mod = load_backtracking()
            if not mod:
                return jsonify({
                    "success": False,
                    "error": "Módulo de backtracking no disponible"
                }), 500
            
            # Validar estado si tenemos colores
            if colores:
                try:
                    mod['validar_instancia_inicial'](estado, colores)
                except AssertionError as e:
                    return jsonify({
                        "success": False,
                        "error": f"Estado inválido: {str(e)}"
                    }), 400
            
            # Resolver usando backtracking
            solucion, stats = mod['solve_backtracking'](estado, max_expansions=max_expansions)
            
            resuelto = solucion is not None
            
            respuesta = {
                "success": True,
                "resuelto": resuelto,
                "stats": {
                    "expanded": stats.expanded,
                    "max_depth": stats.max_depth
                }
            }
            
            if resuelto:
                respuesta["solucion"] = solucion
                respuesta["num_movimientos"] = len(solucion)
                respuesta["mensaje"] = f"Solución encontrada en {len(solucion)} movimientos"
            else:
                # Distinguir entre límite alcanzado y sin solución
                if max_expansions and stats.expanded >= max_expansions:
                    respuesta["mensaje"] = f"No se encontró solución: se alcanzó el límite de {max_expansions:,} expansiones (expandidas: {stats.expanded:,})"
                    respuesta["limite_alcanzado"] = True
                else:
                    respuesta["mensaje"] = f"No se encontró solución: el estado puede no tener solución (expandidas: {stats.expanded:,})"
                    respuesta["limite_alcanzado"] = False
            
            return jsonify(respuesta)
            
        elif algoritmo == 'branch_and_bound':
            mod = load_branch_and_bound()
            if not mod:
                return jsonify({
                    "success": False,
                    "error": "Módulo de Branch and Bound no disponible"
                }), 500
            
            # Validar estado si tenemos colores
            if colores:
                try:
                    mod['validar_instancia_inicial'](estado, colores)
                except AssertionError as e:
                    return jsonify({
                        "success": False,
                        "error": f"Estado inválido: {str(e)}"
                    }), 400
            
            # Resolver usando Branch and Bound
            try:
                solucion, stats = mod['solve_branch_and_bound'](estado, max_expansions=max_expansions)
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Error ejecutando Branch and Bound: {e}")
                print(error_trace)
                return jsonify({
                    "success": False,
                    "error": f"Error ejecutando Branch and Bound: {str(e)}"
                }), 500
            
            resuelto = solucion is not None
            
            # Convertir math.inf a None para JSON
            mejor_cota = getattr(stats, 'mejor_cota_encontrada', None)
            if mejor_cota is not None and (mejor_cota == float('inf') or mejor_cota == math.inf):
                mejor_cota = None
            
            respuesta = {
                "success": True,
                "resuelto": resuelto,
                "stats": {
                    "expanded": stats.expanded,
                    "max_depth": stats.max_depth,
                    "pruned": getattr(stats, 'pruned', 0),
                    "mejor_cota": mejor_cota
                }
            }
            
            if resuelto:
                respuesta["solucion"] = solucion
                respuesta["num_movimientos"] = len(solucion)
                respuesta["mensaje"] = f"Solución encontrada en {len(solucion)} movimientos"
            else:
                # Distinguir entre límite alcanzado y sin solución
                if max_expansions and stats.expanded >= max_expansions:
                    respuesta["mensaje"] = f"No se encontró solución: se alcanzó el límite de {max_expansions:,} expansiones (expandidas: {stats.expanded:,}, podados: {getattr(stats, 'pruned', 0):,})"
                    respuesta["limite_alcanzado"] = True
                else:
                    respuesta["mensaje"] = f"No se encontró solución: el estado puede no tener solución (expandidas: {stats.expanded:,}, podados: {getattr(stats, 'pruned', 0):,})"
                    respuesta["limite_alcanzado"] = False
            
            return jsonify(respuesta)
        else:
            return jsonify({
                "success": False,
                "error": f"Algoritmo '{algoritmo}' no disponible"
            }), 400
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error general al resolver: {e}")
        print(error_trace)
        return jsonify({
            "success": False,
            "error": f"Error al resolver: {str(e)}"
        }), 500


@app.route('/api/validar-estado', methods=['POST'])
def validar_estado():
    """
    Valida que un estado sea correcto.
    
    Body (JSON):
        {
            "algoritmo": "backtracking",
            "estado": [[...], [...], ...],
            "colores": ["R", "G", "B", ...]
        }
    """
    try:
        data = request.json
        algoritmo = data.get('algoritmo', 'backtracking')
        estado_lista = data.get('estado', [])
        colores_str = data.get('colores', [])
        
        if not estado_lista:
            return jsonify({
                "success": False,
                "valido": False,
                "error": "No se proporcionó un estado"
            }), 400
        
        # Convertir a State
        estado = tuple(tuple(p) for p in estado_lista)
        colores = tuple(colores_str) if colores_str else None
        
        # Seleccionar módulo según algoritmo
        if algoritmo == 'backtracking':
            mod = load_backtracking()
            if not mod:
                return jsonify({
                    "success": False,
                    "valido": False,
                    "error": "Módulo de backtracking no disponible"
                }), 500
        elif algoritmo == 'branch_and_bound':
            mod = load_branch_and_bound()
            if not mod:
                return jsonify({
                    "success": False,
                    "valido": False,
                    "error": "Módulo de Branch and Bound no disponible"
                }), 500
        else:
            return jsonify({
                "success": False,
                "valido": False,
                "error": f"Algoritmo '{algoritmo}' no disponible"
            }), 400
        
        if not colores:
            return jsonify({
                "success": True,
                "valido": True,
                "mensaje": "Estado tiene formato correcto (colores no proporcionados para validación completa)"
            })
        
        try:
            mod['validar_instancia_inicial'](estado, colores)
            return jsonify({
                "success": True,
                "valido": True,
                "mensaje": "Estado válido"
            })
        except AssertionError as e:
            return jsonify({
                "success": True,
                "valido": False,
                "mensaje": str(e)
            })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Servidor Flask iniciado")
    print("Cargando algoritmos disponibles...")
    print("-" * 60)
    
    # Intentar cargar ambos algoritmos al inicio
    bt = load_backtracking()
    bnb = load_branch_and_bound()
    
    print("-" * 60)
    print(f"Backtracking: {'✓ Disponible' if bt else '✗ No disponible'}")
    print(f"Branch and Bound: {'✓ Disponible' if bnb else '✗ No disponible'}")
    print("=" * 60)
    print("Abre tu navegador en: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)

