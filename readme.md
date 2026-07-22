# ejecutar app
uvicorn main:app --reload --log-level debug

# ejecucion limpia
uvicorn main:app --host 0.0.0.0 --port 8000 --reload


# error de no encuentra el token
set -a; source .env; set +a

# datos
para la ejecucion del programa y compartir en la misma red, crear exepciones dentro del firewall de windows para postgre y fasapi


# doker
docker build -t mi-proyecto:1.0 .
docker run -d --name mi-proyecto-container -p 8000:8000 --env-file .env mi-proyecto:1.0
docker stop mi-proyecto-container && docker rm mi-proyecto-container