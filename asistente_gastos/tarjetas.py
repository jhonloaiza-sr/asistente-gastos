#Importamos SQL
import sqlite3
#Importamos date de datetime
from datetime import date
#Importamos Path de pathlib
from pathlib import Path
#Importamos calendar
import calendar

#Creamos la clase GestorTarjetas
class GestorTarjetas:
    #Definimos el constructor:
    def __init__(self, ruta_db : Path)-> None:
        #Se guarda la ruta de la db
        self.ruta_db : Path = ruta_db
        #Se crea la tabla de DB
        self._crear_tabla()

    #Metodo de crear tabla
    def _crear_tabla(self)-> None:
        #Realizamos la conexion con la DB
        with sqlite3.connect(self.ruta_db) as conexion:
            #Instrucciones de crear tabla
            conexion.execute("CREATE TABLE IF NOT EXISTS tarjetas (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, dia_corte INTEGER, dia_pago INTEGER)")

    #Registrar tarjetas credito o debito
    def registrar_tarjeta(self, nombre : str, dia_corte : int, dia_pago : int)-> str:
        #Se valida que dia corte y dia pago sea mayor 1 y menor a 31
        if not (1 <= dia_corte <= 31 and 1 <= dia_pago <= 31):
            #Error si no cumple
            return "Error. los días no cuadran con el calendario."
        #Se limpia 
        nombre_limpio : str = nombre.strip()
        #abrimos conexio con la DB
        with sqlite3.connect(self.ruta_db) as conexion:
            #Insertamos los datos
            conexion.execute("INSERT INTO tarjetas (nombre, dia_corte, dia_pago) VALUES(?,?,?)", (nombre_limpio, dia_corte, dia_pago))
        #Retornamos la confirmacion
        return f"Los datos registrados son: {nombre_limpio}, {dia_corte}, {dia_pago}"

    # Método privado que calcula cuántos días reales faltan desde hoy hasta la próxima fecha de pago.
    def _dias_hasta_pago(self, dia_pago: int) -> int:
        # Obtenemos la fecha de hoy según el reloj del computador.
        hoy: date = date.today()
        # Si el día de pago todavía no ha pasado este mes (o es hoy mismo)...
        if dia_pago >= hoy.day:
            # Calculamos cuántos días tiene este mes actual para no pasarnos (ej. 28 en febrero).
            ultimo_dia_mes: int = calendar.monthrange(hoy.year, hoy.month)[1]
            # Construimos la fecha de pago de este mes usando el menor entre 'dia_pago' y 'ultimo_dia_mes'.
            fecha_pago: date = date(hoy.year, hoy.month, min(dia_pago, ultimo_dia_mes))
        # Si el día de pago ya pasó este mes, toca el próximo mes.
        else:
            # Si estamos en diciembre (mes 12), el próximo mes es enero (1) del siguiente año.
            mes_sig: int = 1 if hoy.month == 12 else hoy.month + 1
            # Calculamos el año correspondiente al próximo mes.
            anio_sig: int = hoy.year + 1 if hoy.month == 12 else hoy.year
            # Obtenemos cuántos días tiene ese próximo mes.
            ultimo_dia_sig: int = calendar.monthrange(anio_sig, mes_sig)[1]
            # Construimos la fecha exacta del próximo pago.
            fecha_pago = date(anio_sig, mes_sig, min(dia_pago, ultimo_dia_sig))
        # Restamos ambas fechas 'date' y devolvemos el número entero de días restantes.
        return (fecha_pago - hoy).days

    #Metodo para consultar las tarjetas
    def consultar_tarjetas(self)-> str:
        #Abrimos conexion con DB
        with sqlite3.connect(self.ruta_db) as conexion:
            #Se recorre los datos y se almacenan en la lista
            filas = conexion.execute("SELECT id, nombre, dia_corte, dia_pago FROM tarjetas ORDER BY nombre").fetchall()
            #Se verifica la existencia de tarjetas
            if not filas:
                #Mensaje de que no hay tarjetas registradas
                return "No hay tarjetas registradas"

            #Lista para construir las lineas de texto formateadas
            lineas : list[str] = []
            #Extraemos los datos de cada columna
            for id_t, nombre, corte, pago in filas:
                try:
                    deuda: float = conexion.execute("SELECT COALESCE(SUM(monto),0) FROM gastos WHERE tarjeta_id = ? AND pagado = 0", (id_t,)).fetchone()[0]
                except sqlite3.OperationalError:
                    deuda = 0.0
                dias : int = self._dias_hasta_pago(pago)
                if dias == 0:
                    aviso :str = "PAGO HOY"
                elif dias <= 5:
                    aviso = f"URGENTE. fatan {dias} días"
                else:
                    aviso = f"faltan {dias} días"
                lineas.append(f"#{id_t} | {nombre} | Corte dia {corte} | Pago dia {pago} -> {aviso} | Saldo a pagar: ${deuda:,.0f} COP")
            return "\n".join(lineas)

    #Metodo de pagar tarjeta
    def pagar_tarjeta(self, nombre_tarjeta: str)-> str:
        #Abrimos la conexion con la DB
        with sqlite3.connect(self.ruta_db) as conexion:
            fila = conexion.execute("SELECT id, nombre FROM tarjetas WHERE LOWER(nombre) LIKE LOWER(?) LIMIT 1", (f"%{nombre_tarjeta.strip()}%",)).fetchone()
            if not fila:
                return f"No encotre ninguna tarjeta llamada {nombre_tarjeta}"
            
            id_t, nombre_real = fila
            try:
                # Ejecutamos UPDATE y guardamos el cursor para saber cuántas filas cambió.
                cursor = conexion.execute("UPDATE gastos SET pagado = 1 WHERE tarjeta_id = ? AND pagado = 0", (id_t,))
            # Si aún no existe la tabla 'gastos', avisamos sin que el programa explote.
            except sqlite3.OperationalError:
                # Retornamos aviso cuando no hay gastos creados todavía.
                return "No hay gastos registrados todavía."
        # Si 'rowcount' fue 0, la tarjeta no tenía compras pendientes por pagar.
        if cursor.rowcount == 0:
            # Confirmamos que la tarjeta ya estaba al día.
            return f"La tarjeta '{nombre_real}' ya estaba al día ($0 COP pendiente)."
        # Confirmamos cuántos gastos pendientes quedaron saldados.
        return f"Pago aplicado a '{nombre_real}': se saldaron {cursor.rowcount} gasto(s) pendiente(s)."

            
                
