CREATE TABLE IF NOT EXISTS psicologos(
    id SERIAL PRIMARY KEY,
    primeiro_nome VARCHAR(100) NOT NULL,
    ultimo_nome  VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,

);

CREATE TABLE IF NOT EXISTS pacientes(
    id SERIAL PRIMARY KEY,
    primeiro_nome VARCHAR(100) NOT NULL,
    ultimo_nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL.
)