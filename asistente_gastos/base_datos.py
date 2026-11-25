#Importamos la libreria de SQLite
import sqlite3

#Importamos la libreria datetime
from datetime import datetime

#Importamos la libreria de Path
from pathlib import Path

#Creamos la clase GestorGastos
class GestorGastos:
    #Definimos el constructor
    def __init__(self, ruta_db: Path)-> None:
        #Definimos la ruta de la base de datos
        self.ruta_db: Path = ruta_db
        #Definimos el metodo para crear la tabla de la base de datos
        self._crear_tabla()

    #Definimos el método de _crear_tabla
    def _crear_tabla(self)-> None:
        #Realizamos la conexion a la base de datos
        with sqlite3.connect(self.ruta_db) as conexion:
            #Se conecta a la base de datos, y se manda el comando para crear la base de datos
            conexion.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, categoria TEXT, descripcion TEXT, monto REAL)")

    #Metodo para registrar gastos
    def registrar_gasto(self, categoria: str, descripcion: str, monto: float) -> str:
        #Se verifica que monto sea mayor a 0
        if monto <= 0:
            #Devulve una advertencia
            return "el monto debe ser mayor a cero."
        #Se limpian espacios sobrantes de categoria
        categoria_limpia : str = categoria.strip()
        #Se limpian espacios sobrantes de descripcion
        descripcion_limpia : str = descripcion.strip()

        fecha_actual : str = datetime.now().strftime("%Y-%m-%d %H:%M")
        #Realizamos la conexion a la base de datos
        with sqlite3.connect(self.ruta_db) as conexion:
            #Se ingresa los datos
            conexion.execute("INSERT INTO gastos (fecha, categoria, descripcion, monto) VALUES (?, ?, ?, ?)", (fecha_actual, categoria_limpia, descripcion_limpia, monto))
        
        return f"Registro exitoso: {descripcion_limpia}, por ${monto:,.0f} COP en categoria {categoria_limpia}"

    #Metodo para obtener el total de las categorias
    def obtener_total(self, categoria: str = "")-> str:
        #Se limpian espacios del texto recibido
        categoria_limpia : str = categoria.strip()
        #Se conecta a la base de datos
        with sqlite3.connect(self.ruta_db) as conexion:
        #Se verifica la categoria
            if not categoria_limpia:
                #Devuelva una tupla de 1 elemento
                fila = conexion.execute("SELECT COALESCE(SUM(monto), 0) FROM gastos").fetchone()
                #Se saca el número de la posición 0 de la tupla
                suma_total : float = fila[0]
                return f"Total gastado: ${suma_total:,.0f} COP"


    #Metodo de listar ultimo
    def listar_ultimos(self, limite: int = 10)-> str:
        #Se asegura que el limite minimo sea al menos 1
        limite_seguro : int = max(1,limite)
        #Se establece la conexion con la base de datos
        with sqlite3.connect(self.ruta_db) as conexion:
            #.fetchall devuelve una lista de tuplas, una por fila
            filas = conexion.execute("SELECT id, fecha, categoria, descripcion, monto FROM gastos ORDER BY id DESC LIMIT ?", (limite_seguro,)).fetchall()
            #Si la lista esta vacia, se devulve un mensaje
            if not filas:
                return "No hay gastos registrados."
            #Se crea una lista vacia 
            lineas : list[str] = []
            #Se recorre cada tupla de la lista
            for f in filas: 
                lineas.append(f"#{f[0]} | {f[1]} | {f[2]} | {f[3]} | ${f[4]:,.0f}")
            return "\n".join(lineas)

    #Metodo de resumen por categoria
    def resumen_por_categoria(self) -> str:
        #Se abre la conexion con la base de datos
        with sqlite3.connect(self.ruta_db) as conexion:
            #Se agrupa la info
            filas =  conexion.execute("SELECT categoria, COUNT(*), SUM(monto) AS total FROM gastos GROUP BY categoria ORDER BY total DESC").fetchall()
            #Si las filas estan vacias retorna un mensaje
            if not filas:
                return "No hay gastos registrados todavia"
            lineas: list[str] = []
            #Se recorre dato por dato
            for cat, cant, total in filas:
                lineas.append(f"{cat} : {cant} gastos ${total:,.0f} COP")
            return "\n".join(lineas)

    #Metodo para eliminar_gasto
    def eliminar_gasto(self, id_gasto: int) -> str:
        #Se abre la conexion con la base de datos
        with sqlite3.connect(self.ruta_db) as conexion:
            #Se ejecuta eliminar los datos
            cursor = conexion.execute("DELETE FROM gastos WHERE id = ?", (id_gasto,))
            #Se verifica si encontro gasto con el Id
            if cursor.rowcount == 0:
                #Devuelve un mensaje
                return f"No se encontro ningun gasto con ID: {id_gasto}"
            else:
                return f"Gasto {id_gasto} eliminado correctamente"



        
