CREATE SCHEMA IF NOT EXISTS test_batata;

SET search_path TO test_batata, public;

CREATE TABLE "USERS"(
    id_user SERIAL PRIMARY KEY,
    id_telegram BIGINT NOT NULL UNIQUE, -- Debe ser UNIQUE para ser referenciado
    name_user VARCHAR(64),
    --Revserva a futuro
    extra_info_1 TEXT,
    extra_info_2 TEXT
);

CREATE TABLE "TASKS"(
    id_task SERIAL PRIMARY KEY,
    context_task VARCHAR(500) NOT NULL,
    
    -- Relaciones
    user_open BIGINT NOT NULL,
    user_closed BIGINT,
    
    -- Fechas
    datetime_open TIMESTAMP,
    datetime_closed TIMESTAMP,

    -- Campos reservados
    extra_info_1 TEXT,
    extra_info_2 TEXT,
    
    -- Prioridad de la tarea
    priority INT,
    
    -- Usuario Asignado
    user_assigned BIGINT,

    -- Definición de llaves foráneas
    CONSTRAINT fk_user_open 
        FOREIGN KEY (user_open) 
        REFERENCES "USERS"(id_telegram),
        
    CONSTRAINT fk_user_closed 
        FOREIGN KEY (user_closed) 
        REFERENCES "USERS"(id_telegram),
    
    CONSTRAINT fk_user_assigned 
        FOREIGN KEY (user_assigned) 
        REFERENCES "USERS"(id_telegram)
);

select * from test_batata."USERS";
ALTER TABLE test_batata."TASKS" 
ADD COLUMN user_assigned bigint,
ADD CONSTRAINT fk_user_assigned 
    FOREIGN KEY (user_assigned) 
    REFERENCES test_batata."USERS"(id_telegram);


SET search_path TO test_batata;
SELECT "TASKS".id_task, "USERS".name_user, "TASKS".context_task, "TASKS".datetime_open, "TASKS".priority, assigned_user.name_user 
        FROM "TASKS"
        JOIN "USERS" ON "TASKS".user_open = "USERS".id_telegram
        JOIN "USERS" AS assigned_user ON "TASKS".user_assigned = assigned_user.id_telegram
        WHERE "TASKS".datetime_closed IS NULL
        ORDER BY "TASKS".datetime_open ASC;
