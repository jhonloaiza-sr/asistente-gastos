#Importamos SQLite
import sqlite3
#Importamos datetime
from datetime import datetime
#Importamos Path de pathlib
from pathlib import Path

#Creamos la clase GestorIngresos
class GestorIngresos:
    #Creamos el constructor
    def __init__(self, ruta_db : Path) -> None:
        #Definimos la ruta de la base de datos
        self.ruta_db : Path = ruta_db
        #Definimos el metodo de crear la tabla de la base de datos
        self._crear_tabla()

    #Creamos el metodo para crear la tabla de la DB
    def _crear_tabla(self)-> None:
        #Se inicia la conexion con la DB
        with sqlite3.connect(self.ruta_db) as conexion:
            #Se crea la base de datos
            conexion.execute("CREATE TABLE IF NOT EXISTS ingresos (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, fuente TEXT, monto REAL)")

    #Se define el metodo de registrar los ingresos
    def registrar_ingreso(self, fuente: str, monto: float)-> str:
        #Validación de monto
        if monto <= 0 :
            #Error si es 0 menos
            return "El monto ingresado debe ser mayor a 0."
        #Se limpia los datos de fuente
        fuente_limpia : str = fuente.strip()
        #Se organiza la fecha
        fecha_limpia : str = datetime.now().strftime("%Y-%m-%d %H:%M")
        #Se abre la conexion con la DB
        with sqlite3.connect(self.ruta_db) as conexion:
            #Se insertan datos
            conexion.execute("INSERT INTO ingresos (fecha, fuente, monto) VALUES (?,?,?)", (fecha_limpia, fuente_limpia, monto))
        #Retorna mensaje de exito
        return f"Se registro exitosamente la fecha {fecha_limpia}, la fuente {fuente_limpia} y el monto ${monto} COP"

    #Se define el metodo para consultar 2 tablas en el mismo archivo.db
    def obtener_balance(self)-> str:
        #Se abre la conexion con la DB
        with sqlite3.connect(self.ruta_db) as conexion:
            #Se extrae los ingresos totales de la base de datos tabla ingresos
            total_ingresos : float = conexion.execute("SELECT COALESCE(SUM(monto), 0) FROM ingresos").fetchone()[0]
            #Se extrae los gastos totales de la base de datos tabla gastos
            try:
                total_gastos : float = conexion.execute("SELECT COALESCE(SUM(monto),0) FROM gastos").fetchone()[0]
            #Atrapa errores
            except sqlite3.OperationalError:
                total_gastos = 0.0
            #Se calcula el saldo a favor
            saldo : float = total_ingresos - total_gastos
            #Retorna Ingresos, Gastos y Saldo
            return f"Los ingresos totales son ${total_ingresos:,.0f} COP, los gatos totales son ${total_gastos:,.0f} COP, quedando de esta forma un saldo a favor de ${saldo:,.0f} COP"

        