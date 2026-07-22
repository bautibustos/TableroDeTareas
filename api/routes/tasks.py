from fastapi import APIRouter
from bd.manage_bd import execute_query

router = APIRouter()

@router.get("/tasks")
async def get_active_tasks():
    # Solo traemos tareas sin fecha de cierre
    query = """
        SELECT "TASKS".id_task, "USERS".name_user, "TASKS".context_task, "TASKS".datetime_open, "TASKS".priority, assigned_user.name_user 
        FROM "TASKS"
        JOIN "USERS" ON "TASKS".user_open = "USERS".id_telegram
        JOIN "USERS" AS assigned_user ON "TASKS".user_assigned = assigned_user.id_telegram
        WHERE "TASKS".datetime_closed IS NULL
        ORDER BY "TASKS".datetime_open ASC;
    """
    
    results = await execute_query(query, fetch=True)
    
    # Formateamos la salida
    tasks = [
        {
            "id_task": row[0],
            "creador": row[1],      # Ahora es name_user
            "descripcion": row[2],
            "fecha_creacion": row[3],
            "prioridad": row[4],
            "assign": row[5]
        } 
        for row in results
    ]
    
    return tasks    