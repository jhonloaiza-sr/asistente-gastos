# Asistente Financiero Multimodal Local (LangChain + SQLite + Voz + Visión)

Asistente financiero personal 100% offline construido en Python con **Programación Orientada a Objetos (POO)**, **`uv`**, **SQLite relacional**, **LangChain v1**, **Ollama (`qwen3.5:9b`)** y **`faster-whisper`**.

## Arquitectura Modular

```text
asistente-gastos/
├── main.py                      # Chat en consola (texto, tecla 'v' para voz, y rutas de recibos)
└── asistente_gastos/
    ├── configuracion.py         # Clase Configuracion (modelo, ruta SQLite, categorías y prompt)
    ├── base_datos.py            # Clase GestorGastos (tabla 'gastos' con ALTER TABLE, LIKE, GROUP BY y DELETE)
    ├── ingresos.py              # Clase GestorIngresos (tabla 'ingresos' y balance entre 2 tablas)
    ├── tarjetas.py              # Clase GestorTarjetas (tabla 'tarjetas', fechas de pago, deuda pendiente y pagos)
    ├── audio.py                 # Clase OidoWhisper (faster-whisper en CPU con grabación libre hasta Enter)
    ├── vision.py                # Clase OjoRecibos (lectura multimodal de recibos con qwen3.5:9b)
    └── agente.py                # Clase AgenteGastos (LangChain: ChatOllama, 11 @tool, create_agent e InMemorySaver)
```

## Capacidades (11 herramientas `@tool`)

* **Gastos y Tarjetas Relacionales:** Registra gastos de contado o cargados a una tarjeta de crédito (`LIKE`), calcula días restantes y deuda pendiente por tarjeta, agrupa por categoría (`GROUP BY`) y salda tarjetas (`pagar_tarjeta`).
* **Ingresos y Balance:** Registra ingresos por fuente y calcula `Saldo disponible = Ingresos - Gastos`.
* **Entrada por Voz (`v`):** Dicta gastos o listas largas sin límite fijo de tiempo usando `faster-whisper` (`medium`, CPU `int8`).
* **Lectura Visual de Facturas:** Pasa la ruta o foto de un recibo/factura para que `qwen3.5:9b` extraiga comercio, fecha, categoría y total, y lo guarde automáticamente en SQLite.

## Cómo ejecutarlo

```powershell
uv sync
uv run main.py
```

*(Requiere [Ollama](https://ollama.com/) activo con `qwen3.5:9b`. Bases de datos `*.db`, notebooks e imágenes quedan excluidos por `.gitignore`).*
