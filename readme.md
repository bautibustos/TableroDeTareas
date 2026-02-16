# ejecutar app
uvicorn main:app --reload --log-level debug

# error de no encuentra el token
set -a; source .env; set +a