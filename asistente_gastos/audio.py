#Importamos souddevice para grabar audio desde el microfono del pc
import sounddevice as sd
#Importamos WhisperModel de faster_whisper para convertir la voz a texto 100% offline
from faster_whisper import WhisperModel
# Importamos 'Any' de 'typing' para anotar parámetros internos del flujo de audio.
from typing import Any
# Importamos 'numpy' (ya instalado en tu entorno) para unir los trocitos de audio grabados.
import numpy as np

#Creamos la clase OidoWhisper
class OidoWhisper:
    #Inicializamos el constructor
    def __init__(self, tamano_modelo : str = "medium", frecuencia : int = 16000)-> None:
        #Guardamos la frecuencia
        self.frecuencia : int = frecuencia
        #Cargamos el modelo al crear el objeto
        self.modelo = WhisperModel(tamano_modelo, device = "cpu", compute_type = "int8")

    #Creamos el metodo de escuchar
    def escuchar(self, segundos : int = 5)-> str:
        #Se imprime un aviso de que se esta grabando
        print(f"Se esta grabando {segundos} segundos")
        #Se graba el audio
        grabacion = sd.rec(int(segundos * self.frecuencia), samplerate=self.frecuencia, channels=1, dtype="float32")
        sd.wait()
        #Se transcribe los segmentos
        segmentos, _ = self.modelo.transcribe(grabacion.flatten(),language = "es")
        #Retorna el texto limpio
        return " ".join(seg.text.strip() for seg in segmentos)

    # Método público que graba sin límite fijo de tiempo hasta que tú presiones Enter en la consola.
    def escuchar_libre(self) -> str:
        # Lista vacía donde iremos acumulando los trocitos de audio mientras hablas.
        fragmentos: list[np.ndarray] = []

        # Función interna que 'sounddevice' llama automáticamente cada fracción de segundo con audio nuevo ('indata').
        def guardar_pedazo(indata: np.ndarray, frames: int, tiempo: Any, estado: Any) -> None:
            # Copiamos ese pedacito de audio y lo guardamos al final de nuestra lista 'fragmentos'.
            fragmentos.append(indata.copy())

        # Avisamos en pantalla que el micrófono ya está abierto y cómo detenerlo.
        print("\n[Grabando... Habla tranquilo y presiona ENTER cuando termines]")
        # Abrimos el micrófono en flujo continuo ('InputStream') llamando a 'guardar_pedazo' en segundo plano.
        with sd.InputStream(samplerate=self.frecuencia, channels=1, dtype="float32", callback=guardar_pedazo):
            # 'input()' simplemente pausa aquí hasta que presiones la tecla Enter; al salir del 'with', cierra el micrófono.
            input()

        # Si presionaste Enter muy rápido y no se alcanzó a grabar nada, devolvemos texto vacío.
        if not fragmentos:
            # Retornamos cadena vacía.
            return ""

        # Pegamos todos los trocitos en un solo audio continuo ('axis=0') y lo aplastamos a 1D ('.flatten()').
        audio_completo = np.concatenate(fragmentos, axis=0).flatten()
        # Avisamos que empezó la transcripción.
        print("[Transcribiendo...]")
        # Transcribimos el audio completo con Whisper en español.
        segmentos, _ = self.modelo.transcribe(audio_completo, language="es")
        # Unimos los textos de todos los segmentos y limpiamos espacios sobrantes.
        return " ".join(seg.text.strip() for seg in segmentos).strip()