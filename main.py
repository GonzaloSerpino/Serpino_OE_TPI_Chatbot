import sqlite3

def inicializar_bd():
    """Crea la base de datos, las tablas y carga datos de prueba."""
    conexion = sqlite3.connect('vacaciones.db')
    cursor = conexion.cursor()

    # Tabla de Empleados, almacena la informacion del empleado y los dias de vacaciones disponibles.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empleados (
            id_legajo INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            dias_disponibles INTEGER NOT NULL
        )
    ''')

    # Tabla de Solicitudes, almacena la informacion de la solicitud de vacacion de los empleados.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes (
            id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
            id_legajo INTEGER,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            estado TEXT NOT NULL,
            fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(id_legajo) REFERENCES empleados(id_legajo)
        )
    ''')

    # Tabla de Sesiones, almacena el estado de cada conversacion iniciada.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sesiones (
            numero_telefono TEXT PRIMARY KEY,
            id_legajo INTEGER,
            estado_conversacion TEXT NOT NULL,
            ultima_interaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insertar empleados de prueba si la tabla está vacía
    cursor.execute('SELECT COUNT(*) FROM empleados')
    if cursor.fetchone()[0] == 0:
        empleados_prueba = [
            (1001, 'Gonzalo', 'Serpino', 14),
            (1002, 'Melina', 'Villar', 7)
        ]
        cursor.executemany('INSERT INTO empleados VALUES (?,?,?,?)', empleados_prueba)
        conexion.commit()

    conexion.close()
    
inicializar_bd()