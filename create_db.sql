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

    -- Definición de llaves foráneas
    CONSTRAINT fk_user_open 
        FOREIGN KEY (user_open) 
        REFERENCES "USERS"(id_telegram),
        
    CONSTRAINT fk_user_closed 
        FOREIGN KEY (user_closed) 
        REFERENCES "USERS"(id_telegram)
);

select * from test_batata."TASKS";


SELECT t.context_task, t.user_open, t.datetime_open, t.priority, u.name_user FROM test_batata."TASKS" t
                LEFT JOIN test_batata."USERS" u ON t.user_open = u.id_telegram
                WHERE t.id_task = 3 AND t.user_closed IS null;
