# ejecutar app
uvicorn main:app --reload --log-level debug

# ejecucion limpia
uvicorn main:app --host 0.0.0.0 --port 8000 --reload


# error de no encuentra el token
set -a; source .env; set +a