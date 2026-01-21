CREATE SCHEMA IF NOT EXISTS batata;

SET search_path TO batata, public;

CREATE TABLE "USERS"(
    id_user SERIAL PRIMARY KEY,
    id_telegram BIGINT NOT NULL UNIQUE, -- Debe ser UNIQUE para ser referenciado
    name_user VARCHAR(64)
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

    -- Definición de llaves foráneas
    CONSTRAINT fk_user_open 
        FOREIGN KEY (user_open) 
        REFERENCES "USERS"(id_telegram),
        
    CONSTRAINT fk_user_closed 
        FOREIGN KEY (user_closed) 
        REFERENCES "USERS"(id_telegram)
);

select * from USERS where id_telegram = ;