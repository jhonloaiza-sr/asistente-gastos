# Asistente Financiero Local v2 (LangChain + SQLite Relacional + Ollama)

Agente financiero personal 100% local construido en Python con **Programación Orientada a Objetos (POO)**, **`uv`**, **SQLite multi-tabla relacional** y **LangChain v1** conectado a **Ollama** (`qwen3.5:9b`).

## Arquitectura Modular (3 Tablas en `gastos.db`)

```text
asistente-gastos/
├── main.py                      # Bucle conversacional y alertas iniciales de tarjetas
└── asistente_gastos/
    ├── configuracion.py         # Clase Configuracion (modelo, ruta SQLite, categorías y prompt)
    ├── base_datos.py            # Clase GestorGastos (tabla 'gastos' con ALTER TABLE, LIKE, GROUP BY y DELETE)
    ├── ingresos.py              # Clase GestorIngresos (tabla 'ingresos' y balance entre 2 tablas)
    ├── tarjetas.py              # Clase GestorTarjetas (tabla 'tarjetas', cálculo de fechas, deuda pendiente y pagos)
    └── agente.py                # Clase AgenteGastos (LangChain: ChatOllama, 10 @tool, create_agent e InMemorySaver)
```

## Capacidades del Agente (10 herramientas `@tool`)

* **Gastos:** Registrar gastos de contado o asociados a tarjeta (`tarjeta_id`, `pagado=0`), sumar totales globales o por categoría, listar últimos, agrupar con `GROUP BY` y eliminar por ID.
* **Ingresos y Balance:** Registrar ingresos por fuente y calcular `Ingresos - Gastos = Saldo disponible`.
* **Tarjetas de Crédito:** Registrar fechas de corte y pago, calcular días restantes con alertas de urgencia + saldo pendiente real, y saldar compras pendientes (`pagar_tarjeta`).

## Cómo ejecutarlo

```powershell
uv sync
uv run main.py
```

*(Requiere [Ollama](https://ollama.com/) activo en local con `qwen3.5:9b`. `gastos.db` y `laboratorio.ipynb` quedan excluidos por `.gitignore`).*
