#Importamos la clase de configuracion
from asistente_gastos.configuracion import Configuracion
#Importamos la clase de gestorgastos
from asistente_gastos.base_datos import GestorGastos
#Importamos la clase de agentegastos
from asistente_gastos.agente import AgenteGastos

#Dedinimos la funcion main
def main()-> None:
    #Creamos el objeto de configuracion
    config = Configuracion()
    #Creamos el objeto de gestorgastos
    gestor = GestorGastos(config.ruta_db)
    #Creamos el objeto de agente
    agente = AgenteGastos(config, gestor)

    #Mostramos el resumen de la configuracion
    print(config.mostrar_resumen())

    #Se inicia el bucle iterativo
    while True:
        #Se ingresa la pregunta
        pregunta = input("\nTú: ").strip()
        #Validacion de terminar conversacion
        if pregunta.lower() in ("salir", "exit"):
            #Mensaje de salida
            print("Estare atento a cualquier inquietud o registro.")
            break
        #Validacion si no coloco nada
        if not pregunta:
            #Volvemos al inicio del while
            continue
        #Se realiza la pregunta al agente
        respuesta = agente.responder(pregunta)
        #Se imprime la respuesta
        print(respuesta)

if __name__ == "__main__":
    main()
