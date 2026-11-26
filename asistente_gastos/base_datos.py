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

    # Método privado que crea la tabla 'gastos' y agrega las columnas nuevas si la tabla ya existía antes.
    def _crear_tabla(self) -> None:
        # Abrimos conexión segura con SQLite.
        with sqlite3.connect(self.ruta_db) as conexion:
            # Creamos la tabla completa (incluyendo 'tarjeta_id' y 'pagado' para instalaciones nuevas desde cero).
            conexion.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, categoria TEXT, descripcion TEXT, monto REAL, tarjeta_id INTEGER, pagado INTEGER DEFAULT 1)")
            # Intentamos agregar 'tarjeta_id' si el archivo '.db' ya existía de antes sin esa columna.
            try:
                # Añadimos la columna 'tarjeta_id' que conectará cada compra a crédito con la tabla 'tarjetas'.
                conexion.execute("ALTER TABLE gastos ADD COLUMN tarjeta_id INTEGER")
            # Si la columna ya existía, SQLite lanza OperationalError y lo ignoramos sin problema.
            except sqlite3.OperationalError:
                # No hacemos nada porque la columna ya está presente.
                pass
            # Intentamos agregar 'pagado' (1 = pagado/contado, 0 = pendiente en tarjeta) si la tabla ya existía.
            try:
                # Añadimos la columna 'pagado' con valor por defecto 1 para tus gastos viejos.
                conexion.execute("ALTER TABLE gastos ADD COLUMN pagado INTEGER DEFAULT 1")
            # Si ya existía, ignoramos el aviso de columna duplicada.
            except sqlite3.OperationalError:
                # No hacemos nada porque la columna ya está presente.
                pass

# Método público para insertar un gasto; si 'tarjeta' trae texto, lo asocia a esa tarjeta como deuda pendiente.
    def registrar_gasto(self, categoria: str, descripcion: str, monto: float, tarjeta: str = "") -> str:
        # Validamos que el monto sea un número positivo antes de guardar nada.
        if monto <= 0:
            # Retornamos aviso de error si intentan guardar cero o un valor negativo.
            return "Error: el monto debe ser mayor a cero."

        # Limpiamos espacios sobrantes de la categoría, descripción y tarjeta.
        categoria_limpia: str = categoria.strip()
        # Limpiamos espacios de la descripción.
        descripcion_limpia: str = descripcion.strip()
        # Limpiamos espacios del nombre de la tarjeta (quedará "" si no mencionó tarjeta).
        tarjeta_limpia: str = tarjeta.strip()
        # Obtenemos la fecha y hora actual como texto.
        fecha_actual: str = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Aqui se define la llave foranea de la tabla tarjetas, si el gasto fue con tarjeta de credito se le asigna el id de la tarjeta, si no fue con tarjeta se le asigna None.
        tarjeta_id: int | None = None
        # 1 significa que fue pagado de contado; si usa tarjeta de crédito lo cambiaremos a 0 .
        pagado: int = 1
        # Guardará el nombre completo de la tarjeta encontrada en la base de datos.
        nombre_tarjeta: str = ""

        # Abrimos conexión segura con SQLite.
        with sqlite3.connect(self.ruta_db) as conexion:
            # Si el usuario mencionó una tarjeta (ej. "Bancolombia"), la buscamos primero en la tabla 'tarjetas'.
            if tarjeta_limpia:
                # Protegemos la consulta por si la tabla 'tarjetas' todavía no ha sido creada.
                try:
                    # Buscamos con LIKE '%texto%' ignorando mayúsculas para hallar 'Visa Bancolombia' aunque diga solo 'Bancolombia'.
                    fila = conexion.execute("SELECT id, nombre FROM tarjetas WHERE LOWER(nombre) LIKE LOWER(?) LIMIT 1", (f"%{tarjeta_limpia}%",)).fetchone()
                # Si la tabla 'tarjetas' no existe aún, dejamos 'fila' en None sin romper el programa.
                except sqlite3.OperationalError:
                    # Indicamos que no se encontró ninguna tarjeta.
                    fila = None

                # Si no encontramos esa tarjeta, detenemos la función y avisamos al usuario/agente.
                if not fila:
                    # Retornamos el mensaje claro sin guardar el gasto huérfano.
                    return f"Error: no encontré ninguna tarjeta llamada '{tarjeta_limpia}'. Regístrala primero."

                # Si sí la encontramos, sacamos el 'id' y el 'nombre' real de la tupla y marcamos pagado = 0 (pendiente).
                tarjeta_id, nombre_tarjeta = fila
                # Al ser compra con tarjeta de crédito, queda pendiente de pago al banco (0).
                pagado = 0

            # Insertamos las 6 columnas en la tabla 'gastos' (tarjeta_id quedará NULL en SQLite si fue None).
            conexion.execute("INSERT INTO gastos (fecha, categoria, descripcion, monto, tarjeta_id, pagado) VALUES (?, ?, ?, ?, ?, ?)", (fecha_actual, categoria_limpia, descripcion_limpia, monto, tarjeta_id, pagado))

        # Si se asoció a una tarjeta, devolvemos el mensaje aclarando qué tarjeta y que queda saldo pendiente.
        if tarjeta_id is not None:
            # Confirmación específica para compra a crédito.
            return f"Gasto registrado: {descripcion_limpia} por ${monto:,.0f} COP ({categoria_limpia}) cargado a '{nombre_tarjeta}' [Saldo pendiente]."

        # Si no usó tarjeta de crédito, devolvemos la confirmación normal de contado.
        return f"Registro exitoso: {descripcion_limpia} por ${monto:,.0f} COP en categoría {categoria_limpia}."

        
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



        
