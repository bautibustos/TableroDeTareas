TABLERO DE TAREAS (FASTAPI + TELEGRAM BOT)
=========================================

Un sistema de gestion de tareas en formato de pizarra web interactiva (estilo Post-its) sincronizado en tiempo real con un Bot de Telegram. Las tareas se registran y cierran desde Telegram y se visualizan de manera dinamica en la interfaz web. Ideal para ser plasmado en pantallas grandes para su facil visualziacion.


# 1. INSTALACION Y CONFIGURACION
------------------------------

Sigue estos pasos para clonar, configurar y ejecutar el proyecto en tu entorno local:

Paso 1: Clonar el repositorio e ingresar al directorio
`git clone <URL_DEL_REPOSITORIO>$ cd TableroDeTareas`

Paso 2: Configurar el Entorno Virtual
Crea y activa un entorno virtual de Python. Los scripts del proyecto apuntan al directorio "recursos" el cual ya esta configurado en el archivo .gitignore.
Este mismo directorio de entorno, no es necesario utilizar el nombre recursos, se utiliza el nombre de ejemplo durante todo el readme.

En Linux
`python3 -m venv recursos$ source recursos/bin/activate`

Paso 3: Instalar Dependencias
Instalar todos los paquetes necesarios listados en el archivo de requerimientos:
`pip install -r requeriments.txt`

Paso 4: Configurar la Base de Datos
El proyecto utiliza PostgreSQL como motor de persistencia.
1. Ejecuta las sentencias del archivo "create_db.sql" en tu servidor de base de datos.
2. Esto creara el esquema "batata" junto con las tablas "USERS" y "TASKS", ademas de establecer las restricciones de llaves foraneas por "id_telegram".

Paso 5: Archivo de Variables de Entorno (.env)
Crea un archivo llamado ".env" en la raiz del proyecto con la configuracion de acceso a tu base de datos y el Token provisto por el BotFather de Telegram:

```
db_host=localhost
db_name=tu_base_datos
db_user=tu_usuario
db_pass=tu_contrasena
db_port=5432
TOKEN_BOT_TELEGRAM=tu_token_de_telegram_bot
```


# 2. EJECUCION DEL PROYECTO
-------------------------

Para levantar la API de FastAPI (la cual incluye el ciclo de vida asincrono del Bot de Telegram) y la interfaz web simultaneamente en modo de desarrollo, ejecuta el siguiente bloque de comandos:

En Linux:
`set -a; source .env; set +a$ uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

Una vez iniciado, podras acceder a la pizarra de tareas desde tu navegador ingresando a: http://localhost:8000


# 3. FUNCIONAMIENTO Y FLUJO DE TRABAJO
------------------------------------

El sistema integra el backend asincrono en FastAPI, persistencia en PostgreSQL, renderizado frontend mediante JavaScript nativo, y control remoto mediante python-telegram-bot.

A. Interaccion con el Bot de Telegram:
Los usuarios interactuan con el sistema mediante comandos especificos en el chat del Bot:
- /registro <Nombre>: Comprueba si el ID de Telegram del usuario ya existe. Si no es asi, lo da de alta en la tabla "USERS" vinculando su ID numerico con el nombre especificado.
- /task: Inicia un flujo de conversacion interactivo (ConversationHandler) gestionado en dos etapas:
  1. Muestra una botonera en linea para seleccionar el nivel de Prioridad (1 para Alta, 2 para Media, 3 para Baja).
  2. Espera el contenido de texto de la tarea. Al recibirlo, inserta el registro de forma asincrona en la tabla "TASKS" guardando el autor (user_open), la descripcion (context_task), la fecha de apertura (datetime_open) y la prioridad elegida.
- /close <id_tarea>: Realiza una sentencia UPDATE en la tabla "TASKS" colocando el ID de Telegram del usuario en "user_closed" y la fecha actual en "datetime_closed" para la tarea especificada.

B. Pizarra Web Visual:
- Renderizado Dinamico: Al ingresar a la raiz ("/"), se sirve el archivo "index.html". El script "main.js" realiza peticiones GET asincronas mediante fetch hacia el endpoint "/api/tasks".
- Filtro de Activas: El backend solo retorna las tareas cuyo campo "datetime_closed" sea NULL, ordenadas de manera ascendente por su fecha de creacion.
- Formato Visual: Las tareas se inyectan en un contenedor grid que adapta las tarjetas. El script evalua el valor numerico de la prioridad (1, 2 o 3) para asignar las clases CSS correspondientes ("priority-high", "priority-medium" o "priority-low"), alterando los colores del texto y del indicador visual de la tarjeta.
- Auto-refresco: La interfaz web cuenta con una rutina setInterval configurada a 30000 milisegundos (30 segundos), garantizando que la pizarra se mantenga sincronizada con los cambios realizados desde Telegram de forma automatica y en segundo plano.
