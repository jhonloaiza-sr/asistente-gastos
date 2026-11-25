#importamos Path de pathlib
from pathlib import Path


#Definimos la clase Configuracion
class Configuracion:
    #Se constuye el constructor
    def __init__(self)-> None:
        #Se guarda el modelo de Ollama a utilizar
        self.modelo : str = "qwen3.5:9b"
        #Se establece laruta donde va a estar SQLite
        self.ruta_db : Path = Path("gastos.db")
        #Se crea una lista de las categorias de gastos disponibles
        self.categorias_validas : list[str] = ["Comida", "Transporte", "Servicios", "Tarjetas", "Ocio", "Otros"]
        #Se define el system prompt
        self.instrucciones : str = "Eres un asistente financiero personal en español, que usa sus herramientas para registrar y consultar datos reales en pesos colombianos sin inventar cifras."


    #Funcion de validacion y mostrar resumen
    def mostrar_resumen(self)-> str:
        #Retornamos el modelo, la ruta de la db y las categorias validas
        return f"el modelo usado es: {self.modelo}, la ruta de la base de datos es {self.ruta_db}, y las categorias validas son: {', '.join(self.categorias_validas)}"


