# Asistente Financiero Local (LangChain + SQLite + Ollama)

Agente financiero personal 100% local construido en Python con **Programación Orientada a Objetos (POO)**, **`uv`**, **SQLite** y **LangChain v1** conectado a **Ollama** (`qwen3.5:9b`).

Permite registrar gastos en lenguaje natural, consultar totales globales o por categoría, obtener resúmenes agrupados (`GROUP BY`) y eliminar registros por ID de forma persistente.

## Arquitectura Modular

```text
asistente-gastos/
├── main.py                      # Bucle conversacional en consola
└── asistente_gastos/
    ├── configuracion.py         # Clase Configuracion (modelo, ruta SQLite, categorías e instrucciones)
    ├── base_datos.py            # Clase GestorGastos (CRUD y consultas GROUP BY en SQLite)
    └── agente.py                # Clase AgenteGastos (LangChain: ChatOllama, @tool, create_agent e InMemorySaver)
```

## Herramientas del Agente (`@tool`)

* `registrar_gasto`: Guarda un gasto validado con fecha, categoría, descripción y monto en COP.
* `obtener_total`: Suma el total gastado global o filtrado por categoría.
* `listar_ultimos`: Muestra los registros más recientes con su ID.
* `resumen_por_categoria`: Agrupa gastos y montos ordenados de mayor a menor (`GROUP BY`).
* `eliminar_gasto`: Elimina un registro por su ID único verificando `rowcount`.

## Cómo ejecutarlo

```powershell
# Instalar dependencias con uv
uv sync

# Ejecutar el asistente en consola
uv run main.py
```

*(Requiere [Ollama](https://ollama.com/) activo en local con el modelo `qwen3.5:9b` descargado. Tu base `gastos.db` se mantiene privada fuera de Git gracias a `.gitignore`).*
