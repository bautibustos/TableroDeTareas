from fastapi import APIRouter
from bd.manage_bd import execute_query

router = APIRouter()

@router.get("/tasks")
async def get_active_tasks():
    # Solo traemos tareas sin fecha de cierre
    query = """
        SELECT user_open, context_task, datetime_open 
        FROM "TASKS" 
        WHERE datetime_closed IS NULL
    """
    
    results = await execute_query(query, fetch=True)
    print(results)
    # Formateamos la salida
    tasks = [
        {
            "creador": row[0],
            "descripcion": row[1],
            "fecha_creacion": row[2]
        } 
        for row in results
    ]
    
    return tasks