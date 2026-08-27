# TableroDeTareas

FastAPI (pizarra web) + bot de Telegram, un solo proceso (`main.py`, lifespan arranca ambos), pool async a Postgres (`bd/manage_bd.py`).

## Variables de entorno requeridas (no hardcodear valores, solo nombres)

- `TOKEN_BOT_TELEGRAM`
- `db_host`, `db_name`, `db_user`, `db_pass`, `db_port`, `db_schema`

`bd/manage_bd.py` no tiene defaults: si falta alguna, la conexión falla al abrir el pool (falla recién en el lifespan de `main.py`, no al importar). `db_schema` en particular no tiene default a propósito — sin valor explícito, `sql.Identifier(None)` rompe al armar el `SET search_path`, para forzar que cada entorno lo elija a mano en vez de heredar uno por accidente.

## Schema de Postgres

**Hay dos schemas reales en la misma base**: `batata` es producción (datos y usuarios reales) y `test_batata` es de prueba (data descartable). `bd/manage_bd.py` arma `SET search_path TO <db_schema>, public;` a partir de la env var `db_schema` — el `.env` local apunta a `test_batata`; el `.env` de producción tiene que apuntar a `batata`. Antes de correr algo, confirmar cuál `.env` estás usando.

**Nunca corras un contenedor de prueba con el `TOKEN_BOT_TELEGRAM` real mientras la instancia de producción esté viva**: ambas hacen polling del mismo bot de Telegram, y Telegram le reparte los updates a la que gane la carrera — un usuario real puede terminar interactuando con tu contenedor de test (schema equivocado) sin que nadie lo note hasta que algo como una FK violation lo delate. Para probar el bot en sí (no solo la web), conseguir un token de bot separado vía @BotFather y usarlo en el `.env` local.

`create_db.sql` es la definición del schema, pero **no correrlo entero contra una base con datos reales**: al final del archivo (últimas ~20 líneas) hay SQL de scratch/debug que no es DDL del schema y en el pasado pisó datos de una tabla real por apuntar al schema equivocado. Extraer y correr solo los `CREATE SCHEMA` / `CREATE TABLE` / `ALTER TABLE` que definen la estructura.

## Docker

- `Dockerfile` copia `requeriments.txt` (typo real en el nombre del archivo, no es error) — no renombrar sin actualizar el Dockerfile.
- Si el Postgres corre en el host (no en otro contenedor) y el daemon es **Docker Desktop**: `--network host` NO sirve para llegar al host (Docker Desktop corre en una VM, `localhost` ahí no es el host real). Usar red bridge normal (`-p 8000:8000`) y setear `db_host=host.docker.internal`.
- Si el daemon es Docker nativo de Linux (no Desktop), `--network host` sí comparte la red real y `db_host=localhost` funciona directo.
- `.env` pasado con `docker run --env-file` se toma literal, sin parsear comillas (a diferencia de `python-dotenv`, que sí las saca corriendo local). Si el `.env` tiene valores entre comillas simples/dobles, van a llegar con las comillas incluidas al contenedor y van a romper lo que las use (ej. token de Telegram).

## Bot de Telegram

- Comandos registrados en `bot_telegram/run_bot.py` vía `set_my_commands` en `configurar_menu` (hook `post_init`). El nombre en `BotCommand(...)` tiene que coincidir exactamente con el `CommandHandler` real — ya hubo un desajuste (`register` vs `registro`).
- `/close` es un `ConversationHandler` (`bot_telegram/commands/close_task.py`): solo lo puede cerrar `user_assigned`, pide una observación y si no llega en `OBSERVATION_TIMEOUT` (constante al principio del archivo) cierra la tarea igual sin observación.
