#Se importa Any
from typing import Any
#Se importa langchain agents
from langchain.agents import create_agent
#Se importa langchain tools
from langchain.tools import tool
#Se importa langchain Ollama
from langchain_ollama import ChatOllama
#Se importa langgraph con memoria persistente
from langgraph.checkpoint.memory import InMemorySaver
#Se importa el objeto Configuracion
from asistente_gastos.configuracion import Configuracion
#Se importa el objeto de GestorGastos
from asistente_gastos.base_datos import GestorGastos

#Se crea la clase AgenteGastos
class AgenteGastos:
    #Se crea el constructor
    def __init__(self, config: Configuracion, gestor: GestorGastos)-> None:
        #Se guarda config
        self.config = config
        #Se guarda gestor
        self.gestor = gestor
        #Se crea el modelo
        modelo = ChatOllama(model = self.config.modelo, reasoning = False, temperature = 0)
        #Se llama a un metodo interno _crear_herramientas()
        herramientas = self._crear_herramientas()
        #Se crea el agente
        self.agente = create_agent(model = modelo, tools = herramientas, system_prompt = self.config.instrucciones, checkpointer = InMemorySaver())

    # Método privado que fabrica las 3 herramientas '@tool' conectadas a 'self.gestor'.
    def _crear_herramientas(self) -> list[Any]:
        # Calculamos las categorías como texto para darle la pista exacta al modelo en el docstring.
        categorias_texto: str = ", ".join(self.config.categorias_validas)

        # Decorador '@tool': convierte esta función en una herramienta legible por LangChain.
        @tool
        # Definimos la herramienta 1 (sin 'self' porque está dentro del método).
        def registrar_gasto(categoria: str, descripcion: str, monto: float) -> str:
            # Docstring claro para que el modelo clasifique cada gasto dentro de nuestras categorías válidas.
            """Registra un gasto nuevo en SQLite. Categorías: Comida, Transporte, Servicios, Tarjetas, Ocio, Otros. Monto en pesos."""
            # Delegamos el guardado real a nuestro objeto 'self.gestor'.
            return self.gestor.registrar_gasto(categoria, descripcion, monto)

        # Decorador '@tool' para la herramienta 2.
        @tool
        # Definimos la herramienta 2 con parámetro opcional 'categoria'.
        def obtener_total(categoria: str = "") -> str:
            """Consulta el total gastado en pesos. Si pasas una categoría (ej. 'Comida'), filtra solo esa; si la dejas vacía, suma todo."""
            # Delegamos la consulta SQL a 'self.gestor'.
            return self.gestor.obtener_total(categoria)

        #Se crea el tool de la funcion obtener_total
        @tool
        #Se define la funcion listar_ultimos
        def listar_ultimos(limite: int = 10)-> str:
            #Docstring
            """
            Muestra la lista de los últimos gastos registrados en la base de datos SQLite.
            """
            #Retorna
            return self.gestor.listar_ultimos(limite)

        #Se crea el metodo de resumen por categoria
        @tool
        #Se define la funcion resumen_por_categoria
        def resumen_por_categoria()-> str:
            #Docstring
            """
            Muestra el resumen de categoria, cantidad total por categoria, y monto total por categoria.
            """
            #Retorna
            return self.gestor.resumen_por_categoria()

        #Se define la tool
        @tool
        #Se define la tool de eliminar_gasto
        def eliminar_gasto(id_gasto : int)-> str:
            #Docstring
            """
            Elimina el dato especificando el id de interes.
            """
            #Retorna
            return self.gestor.eliminar_gasto(id_gasto)
        

        return [registrar_gasto, obtener_total, listar_ultimos, resumen_por_categoria, eliminar_gasto]
        


    # Método público principal que envía la pregunta del usuario a LangChain y devuelve la respuesta final.
    def responder(self, pregunta: str) -> str:
        # Protegemos la llamada con try/except por si Ollama está cerrado.
        try:
            # Ejecutamos el agente pasando el mensaje del usuario y un 'thread_id' fijo para mantener la memoria.
            resultado = self.agente.invoke(
                # Diccionario con el mensaje nuevo del usuario.
                {"messages": [{"role": "user", "content": pregunta}]},
                # Configuración del hilo de conversación en InMemorySaver.
                {"configurable": {"thread_id": "sesion-1"}},
            # Cerramos la llamada a '.invoke()'.
            )
            # 'resultado["messages"][-1]' es el último mensaje de la conversación (la respuesta final de la IA).
            return str(resultado["messages"][-1].content)
        # Capturamos cualquier fallo de conexión o ejecución.
        except Exception as error:
            # Devolvemos un aviso legible sin romper la aplicación.
            return f"Error al comunicarse con el agente LangChain: {error}"