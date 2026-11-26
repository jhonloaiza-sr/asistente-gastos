#Importamos Path de pathlib
from pathlib import Path
#Importamos ollama
import ollama

#Creamos la clase OjoRecibos:
class OjoRecibos:
    #Definimos el constructor
    def __init__(self, modelo : str = "qwen3.5:9b")-> None:
        #Guardamos el modelo 
        self.modelo : str = modelo

    #Definimos el metodo de leer recibos
    def leer_recibo(self, ruta_imagen : str)-> str:
        #Definimos la ruta de la imagen, realizando la limpieza correspondiente
        ruta : Path  = Path(ruta_imagen.strip().strip('"').strip("'"))
        #Verificamos si ruta existe
        if not ruta.is_file():
            #Retornamos un mensaje
            return f"No se encontro ninguna imagen {ruta}"
        try:
            #Definimos los parametros de ollama
            respuesta = ollama.chat(
                model = self.modelo, 
                think = False,
                messages = [{
                    # Rol de usuario que envía la consulta.
                    "role": "user",
                    # Instrucción clara para extraer los datos contables del recibo.
                    "content": "Lee este recibo o factura y extrae: Comercio, Fecha, Categoría sugerida (Comida, Transporte, Servicios, Tarjetas, Ocio u Otros) y Total en número entero en pesos sin puntos ni símbolos (ej. 11401). ",
                    # Clave 'images': Ollama lee automáticamente la ruta de tu archivo local en Windows.
                    "images": [str(ruta)],
                # Cerramos el diccionario del mensaje.
                }]
                )
            # Devolvemos el contenido extraído (o un aviso si vino vacío).
            return respuesta.message.content or "No pude leer la información de la imagen."
        #Si cacha un error
        except Exception as error:
            #Retorna un mensaje
            return f"Error al analiza la imagen {error}"
