# Serpino_OE_TPI_Chatbot
Trabajo Practico Integrador Gonzalo Serpino

A continuacion, se incluiran 2 guias para ejecutar la aplicacion.

## GUÍA 1: Cómo probar el Chatbot en Vivo

Esta guía está destinada a aquellos usuarios que desean interactuar con el chatbot directamente desde su dispositivo móvil personal a través de **WhatsApp**, utilizando el servidor central actualmente desplegado por el desarrollador.

### Paso 1: Vinculación al Entorno de Pruebas (Sandbox de Twilio)
Dado que se trata de un entorno de desarrollo académico, se requiere conectar tu número de WhatsApp al canal de pruebas seguro del proyecto:
1. Agrega a los contactos de tu teléfono celular el número oficial del Sandbox de Twilio: **+1 415 523 8886**.
2. Abre una conversación de WhatsApp con ese contacto y envía el siguiente código de activación: join lovely-desert

### Paso 2: Iniciar la Interacción y Validar Identidad
Envía cualquier mensaje de saludo (ej. "Hola", "Buenas" o "Inicio") para iniciar la conversacion con el bot.

El bot responderá reconociéndote como un nuevo hilo y te solicitará tu Número de Legajo.

### Paso 3: Perfiles de Prueba Precargados (Simulación de Datos Reales)
Para validar todas las aristas del proceso administrativo, puedes utilizar cualquiera de los siguientes dos perfiles cargados en el archivo relacional:

Perfil de Simulación A:

Número de Legajo: 1001

Nombre Completo: Gonzalo Serpino

Saldo Inicial: 14 días corridos de vacaciones disponibles.

Perfil de Simulación B:

Número de Legajo: 1002

Nombre Completo: Melina Villar

Saldo Inicial: 7 días corridos de vacaciones disponibles.

### Paso 4: Ejecucion del Programa.
Una vez validado el legajo, el bot te presentará un menú interactivo. Te sugerimos forzar las validaciones del sistema para evaluar su resiliencia ante errores del usuario:

Flujo 1: Nueva Solicitud de Vacaciones (Opción 1)

El bot te informará tu saldo de días y te pedirá el rango en formato DD/MM/YYYY - DD/MM/YYYY.

Introduce un rango válido y menor o igual a tu saldo (ej. para el legajo 1001: 01/06/2026 - 10/06/2026). El sistema guardará la solicitud como PENDIENTE_APROBACION y descontará automáticamente los 10 días, actualizando tu registro en la base de datos a 4 días restantes.

Flujo 2: Consulta de Solicitud (Opción 2)

Al presionar 2, el bot realizará un SELECT ordenado cronológicamente sobre tu legajo y te devolverá el estado actual de tu trámite administrativo en la organización (ej. "Tu última solicitud está en estado: PENDIENTE_APROBACION").

## GUÍA 2: Despliegue Local y Configuración de Servidor.

Si deseas clonar este repositorio para ejecutar el servidor en tu propia computadora local, auditar el código o realizar pruebas de arquitectura, sigue el instructivo a continuación:

### Paso 1: Requisitos Previos
Asegúrate de tener instalado Python 3.x en tu sistema operativo.

### Paso 2: Clonar el Repositorio e Instalar Dependencias
Abre tu terminal, clona el proyecto y posicionate en la carpeta raíz. Luego, ejecuta el siguiente comando para instalar las librerías necesarias (Flask para el servidor web y Twilio para la API de mensajería):

git clone <url-del-repositorio>
cd <nombre-de-la-carpeta>
pip install flask twilio

### Paso 3: Ejecutar el Servidor Local
Ejecuta el script principal de Python:

python main.py

Al realizar la primera ejecución, el programa llamará automáticamente a la función inicializar_bd(), creando localmente el archivo de base de datos relacional vacaciones.db e insertando los registros de prueba. El servidor Flask comenzará a escuchar peticiones en el puerto local 5000.

### Paso 4: Configurar el Túnel de Internet (Ngrok)
Dado que el servidor local está aislado, se requiere un túnel seguro para recibir las notificaciones (webhooks) de WhatsApp:

Descarga y arranca Ngrok.

Abre una nueva terminal y levanta el puente HTTP hacia el puerto 5000:

ngrok http 5000

Copia la URL pública con protocolo seguro provista por Ngrok en la sección Forwarding.

### Paso 5: Configurar el Webhook en Twilio Console
Inicia sesión en tu consola de Twilio y dirígete a Messaging > Try it out > Send a WhatsApp message > Sandbox settings.

En el campo "WHEN A MESSAGE COMES IN", pega tu URL de Ngrok agregando obligatoriamente el endpoint /whatsapp al final.

Ejemplo: https://xxxx-xxxx.ngrok-free.app/whatsapp

Configura el método en HTTP POST y presiona Save.

A partir de este momento, tu entorno local estará completamente integrado con la API de WhatsApp, permitiendo auditar la consola de comandos de Flask en tiempo real ante cada interacción.