# Importamos la clase 'Configuracion' desde 'configuracion.py'.
from asistente_gastos.configuracion import Configuracion

# Importamos 'GestorGastos' desde 'base_datos.py'.
from asistente_gastos.base_datos import GestorGastos

# Importamos 'GestorIngresos' desde 'ingresos.py'.
from asistente_gastos.ingresos import GestorIngresos

# Importamos 'GestorTarjetas' desde 'tarjetas.py'.
from asistente_gastos.tarjetas import GestorTarjetas

# Importamos 'AgenteGastos' desde 'agente.py'.
from asistente_gastos.agente import AgenteGastos

#Importamos 'OidoWhisper' desde 'audio.py'
from asistente_gastos.audio import OidoWhisper

# Importamos el lector visual de recibos desde 'vision.py'.
from asistente_gastos.vision import OjoRecibos


# Definimos la función principal que conecta todos los módulos y arranca el chat en consola.
def main() -> None:
    # Creamos la configuración y los 3 gestores apuntando al mismo archivo 'gastos.db'.
    config = Configuracion()
    # Creamos el gestor de gastos (ejecuta ALTER TABLE automático si tu DB ya existía).
    gestor = GestorGastos(config.ruta_db)
    # Creamos el gestor de ingresos y balance.
    ingresos = GestorIngresos(config.ruta_db)
    # Creamos el gestor de tarjetas de crédito.
    tarjetas = GestorTarjetas(config.ruta_db)
    # Conectamos los 3 gestores dentro del agente LangChain con las 10 herramientas.
    # Creamos el lector de recibos por visión usando el modelo local configurado.
    ojo = OjoRecibos(modelo=config.modelo)
    # Conectamos los 3 gestores SQLite y el lector visual dentro del agente LangChain (11 herramientas).
    agente = AgenteGastos(config, gestor, ingresos, tarjetas, ojo)
    # Instanciamos el oido Whisper una sola vez al arrancar para no recargarlo en cada pregunta
    oido = OidoWhisper(tamano_modelo= "medium")

    # Mostramos bienvenida, configuración y el estado actual de tarjetas apenas inicia la app.
    print("ASISTENTE FINANCIERO LOCAL (Escribe 'v' para hablar o 'salir' para terminar)")
    # Imprimimos resumen del modelo y categorías.
    print(config.mostrar_resumen())
    # Imprimimos de una vez las alertas de tarjetas pendientes al arrancar.
    print("\nESTADO DE TARJETAS")
    # Consultamos y mostramos las tarjetas registradas.
    print(tarjetas.consultar_tarjetas())

    # Iniciamos el bucle conversacional infinito.
    while True:
        # Pedimos la pregunta una sola vez limpiando espacios sobrantes.
        pregunta: str = input("\nTú: ").strip()

        # Comprobamos si el usuario quiere cerrar el programa.
        if pregunta.lower() in ("salir", "exit"):
            # Nos despedimos por consola.
            print("Estaré atento a cualquier inquietud o registro.")
            # Salimos del bucle 'while'.
            break

        # Si presionó Enter en blanco, volvemos a pedir entrada.
        if not pregunta:
            # Saltamos a la siguiente vuelta sin molestar al agente.
            continue

        # Si el usuario escribe 'v', activamos el micrófono durante 6 segundos para dictar por voz.
        if pregunta.lower() == "v":
            # Escuchamos por micrófono y guardamos la transcripción dentro de 'pregunta'.
            pregunta = oido.escuchar_libre()
            # Imprimimos lo que entendió Whisper para que veas lo que se enviará al agente.
            print(f"Tú (voz): {pregunta}")
            # Si hubo silencio y no capturó nada, volvemos al inicio del bucle sin molestar al agente.
            if not pregunta:
                # Saltamos a la siguiente vuelta del 'while'.
                continue

        # Enviamos la petición al agente LangChain e imprimimos su respuesta.
        respuesta: str = agente.responder(pregunta)
        # Mostramos la respuesta en pantalla.
        print(f"\nAsistente: {respuesta}")


# Este bloque asegura que 'main()' solo arranque al ejecutar este archivo directamente.
if __name__ == "__main__":
    # Ejecutamos la función principal.
    main()