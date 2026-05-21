import sqlite3
from datetime import datetime
#Importo las funciones de Flask 
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

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
    
def obtener_sesion(telefono):
    """Recupera el estado actual del usuario."""
    conexion = sqlite3.connect('vacaciones.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT estado_conversacion, id_legajo FROM sesiones WHERE numero_telefono = ?', (telefono,))
    resultado = cursor.fetchone()
    conexion.close()
    
    #Si el select devuelve un resultado, devuelve el estado de esa conversacion.
    if resultado:
        return resultado[0], resultado[1] # Devuelve estado y legajo
    #Si no encuentra nada, por defecto pone como "NUEVO" el estado y devuelve None en el numero de legajo, indicando que es una conversacion nueva.
    return 'NUEVO', None
    
def guardar_sesion(telefono, estado, legajo=None):
    """Actualiza o crea el estado de la conversación."""
    conexion = sqlite3.connect('vacaciones.db')
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO sesiones (numero_telefono, id_legajo, estado_conversacion, ultima_interaccion)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(numero_telefono) 
        DO UPDATE SET estado_conversacion=excluded.estado_conversacion, 
                      id_legajo=excluded.id_legajo, 
                      ultima_interaccion=CURRENT_TIMESTAMP
    ''', (telefono, legajo, estado))
    conexion.commit()
    conexion.close()
    
def insertar_solicitud(legajo, f_inicio, f_fin, estado):
    """Crea en la base de datos la solicitud de vacaciones."""
    conexion = sqlite3.connect('vacaciones.db')
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO solicitudes (id_legajo, fecha_inicio, fecha_fin, estado, fecha_solicitud)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (legajo, f_inicio, f_fin, estado))
    conexion.commit()
    conexion.close()
    
def conteo_solicitud(legajo):
    """Devuelve si existe una solicitud pendiente."""
    conexion = sqlite3.connect('vacaciones.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT count(*) FROM solicitudes WHERE id_legajo = ?', (legajo,))
    resultado = cursor.fetchone()
    conexion.close()
    
    return resultado[0] #Devuelvo el numero de solicitudes

def actualizar_dias_disponibles(legajo, dias_a_descontar):
    """Resta los días solicitados de los días disponibles del empleado."""
    conexion = sqlite3.connect('vacaciones.db')
    cursor = conexion.cursor()
    cursor.execute('''
        UPDATE empleados 
        SET dias_disponibles = dias_disponibles - ? 
        WHERE id_legajo = ?
    ''', (dias_a_descontar, legajo))
    conexion.commit()
    conexion.close()

def procesar_mensaje(telefono, mensaje):
    """Funcion de decision de mensajes de bot en base al estado del proceso."""
    estado_actual, legajo = obtener_sesion(telefono)
    print(estado_actual)
    mensaje = mensaje.strip().lower()

    # --- ESTADO: NUEVO USUARIO ---
    if estado_actual == 'NUEVO':
        respuesta = "¡Hola! Soy el bot de RRHH. Para comenzar, por favor ingresa tu número de legajo."
        guardar_sesion(telefono, 'ESPERANDO_LEGAJO')
        return respuesta

    # --- ESTADO: VALIDANDO IDENTIDAD ---
    elif estado_actual == 'ESPERANDO_LEGAJO':
        try:
            legajo_ingresado = int(mensaje)
            # Validar en la BD
            conexion = sqlite3.connect('vacaciones.db')
            cursor = conexion.cursor()
            cursor.execute('SELECT nombre, apellido FROM empleados WHERE id_legajo = ?', (legajo_ingresado,))
            empleado = cursor.fetchone()
            conexion.close()

            if empleado:
                nombre_emp = empleado[0]
                respuesta = f"Bienvenido/a {nombre_emp}. ¿Qué deseas hacer?\n1. Nueva Solicitud\n2. Consultar Solicitud"
                guardar_sesion(telefono, 'MENU_PRINCIPAL', legajo_ingresado)
            else:
                respuesta = "Legajo no encontrado. Por favor, verifica e ingresa tu número de legajo nuevamente."
                # Se mantiene en el mismo estado
        except ValueError:
            respuesta = "Por favor, ingresa solo números para tu legajo."
        
        return respuesta

    # --- ESTADO: MENÚ PRINCIPAL ---
    elif estado_actual == 'MENU_PRINCIPAL':
        solicitud_existente = conteo_solicitud(legajo)
        
        if mensaje == '1':
            if solicitud_existente == 0:
                conexion = sqlite3.connect('vacaciones.db')
                cursor = conexion.cursor()
                cursor.execute('SELECT dias_disponibles, nombre FROM empleados WHERE id_legajo = ?', (legajo,))
                datos = cursor.fetchone()
                conexion.close()
                
                dias = datos[0]
                nombre = datos[1]
                
                respuesta = f"Hola {nombre}, tienes {dias} días disponibles. Por favor, ingresa el rango de fechas con el formato DD/MM/YYYY - DD/MM/YYYY"
                guardar_sesion(telefono, 'ESPERANDO_FECHAS', legajo)
            else:
                respuesta = "Ya existe una solicitud pendiente de aprobacion."
                guardar_sesion(telefono, 'NUEVO') #Se reinicia el estado
            
        
        elif mensaje == '2':
            if solicitud_existente != 0:
                conexion = sqlite3.connect('vacaciones.db')
                cursor = conexion.cursor()
                cursor.execute('SELECT estado FROM solicitudes WHERE id_legajo = ?', (legajo,))
                datos = cursor.fetchone()
                respuesta = f"Tu solicitud esta en estado: {datos[0]}"
                guardar_sesion(telefono, 'NUEVO') #Se reinicia el estado
            else: 
                respuesta = f"No se encuentrar solicitudes existentes para el legajo {legajo}"
        else:
            #Si se selecciona otra opcion, indica al usuario que ingrese una opcion valida
            respuesta = "Opción inválida. Por favor responde '1' o '2'."
        
        return respuesta
    
    elif estado_actual == 'ESPERANDO_FECHAS':
        try:
            #Separa el string ingresado por el guion para obtener la diferencia entre fechas
            partes = mensaje.split('-')
            if len(partes) != 2:
                raise ValueError("Formato de Fecha incorrecto. Por favor, ingresa el rango de fechas con el formato DD/MM/YYYY - DD/MM/YYYY")
            
            str_inicio = partes[0].strip()
            str_fin = partes[1].strip()

            #Convertir a objetos datetime (Esto valida que la fecha sea real, ej. no exista el 32/01/2026)
            fecha_inicio = datetime.strptime(str_inicio, "%d/%m/%Y")
            fecha_fin = datetime.strptime(str_fin, "%d/%m/%Y")

            #Validar orden cronologico
            if fecha_fin < fecha_inicio:
                return "La fecha de fin no puede ser anterior a la fecha de inicio. Por favor, inténtalo de nuevo (DD/MM/YYYY - DD/MM/YYYY):"

            #Calcular la cantidad de dias (se suma 1 para que sea inclusivo)
            dias_solicitados = (fecha_fin - fecha_inicio).days + 1

            #Validar cantidad de dias disponibles
            conexion = sqlite3.connect('vacaciones.db')
            cursor = conexion.cursor()
            cursor.execute('SELECT dias_disponibles FROM empleados WHERE id_legajo = ?', (legajo,))
            dias_disponibles = cursor.fetchone()[0]
            conexion.close()

            if dias_solicitados > dias_disponibles:
                return f"Estás solicitando {dias_solicitados} días, pero solo tienes {dias_disponibles} disponibles. Por favor, ingresa un rango menor:"

            # 6. Si todo está correcto: Guardar solicitud y descontar días
            insertar_solicitud(legajo, str_inicio, str_fin, 'PENDIENTE_APROBACION')
            actualizar_dias_disponibles(legajo, dias_solicitados)
            
            respuesta = f"¡Éxito! Tu solicitud por {dias_solicitados} días ha sido registrada y está 'Pendiente de aprobación'. Tus días disponibles han sido actualizados."
            guardar_sesion(telefono, 'NUEVO') # Finaliza el trámite

        except ValueError:
            # Se captura cualquier error de formato o fechas inexistentes
            respuesta = "El formato de la fecha es incorrecto o la fecha no existe. Usa exactamente DD/MM/YYYY - DD/MM/YYYY."
            # Mantenemos el estado en ESPERANDO_FECHAS para que lo vuelva a intentar

        return respuesta

    else:
        # Mecanismo de seguridad frente a estados rotos
        guardar_sesion(telefono, 'NUEVO')
        return "Ocurrió un error y la sesión se reinició. Por favor, envía un mensaje para empezar de nuevo."



# Inicializamos la aplicación Flask
app = Flask(__name__)

# Esta es la ruta (endpoint) que WhatsApp/Twilio va a consultar
@app.route('/whatsapp', methods=['POST'])
def webhook_whatsapp():
    # 1. Twilio nos envía los datos del mensaje recibido mediante un POST request
    mensaje_entrante = request.values.get('Body', '')
    numero_remitente = request.values.get('From', '')

    # 2. Le pasamos el número y el texto a tu máquina de estados
    respuesta_bot = procesar_mensaje(numero_remitente, mensaje_entrante)

    # 3. Formateamos la respuesta usando la librería de Twilio
    respuesta_twilio = MessagingResponse()
    mensaje_twilio = respuesta_twilio.message()
    mensaje_twilio.body(respuesta_bot)

    # 4. Devolvemos el XML que Twilio necesita para mandar el WhatsApp de vuelta
    return str(respuesta_twilio)

if __name__ == '__main__':
    inicializar_bd()
    print("--- SERVIDOR DEL CHATBOT INICIADO ---")
    print("El bot está escuchando en el puerto 5000...")
    # debug=True permite que el servidor se reinicie solo si hacés cambios en el código
    app.run(port=5000, debug=True)