CREATE TABLE IF NOT EXISTS psicologos (
    id SERIAL PRIMARY KEY,
    primeiro_nome VARCHAR(100) NOT NULL,
    ultimo_nome VARCHAR(100) NOT NULL,
    crp VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    google_refresh_token TEXT 
);

CREATE TABLE IF NOT EXISTS pacientes (
    id_paciente SERIAL PRIMARY KEY, 
    id_psicologo INTEGER NOT NULL REFERENCES psicologos(id) ON DELETE CASCADE,
    primeiro_nome VARCHAR(50) NOT NULL,
    ultimo_nome VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    is_ativo BOOLEAN DEFAULT TRUE,
    UNIQUE (id_psicologo, email)
);

CREATE TABLE IF NOT EXISTS pagamentos (
    id_pagamento SERIAL PRIMARY KEY,
    id_psicologo INTEGER REFERENCES psicologos(id) ON DELETE CASCADE,
    id_paciente INTEGER REFERENCES pacientes(id_paciente) ON DELETE CASCADE,
    valor DECIMAL(10, 2) NOT NULL,
    metodo_pagamento VARCHAR(30) NOT NULL,
    data_pagamento TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consultas (
    id_consulta SERIAL PRIMARY KEY,
    id_psicologo INTEGER NOT NULL REFERENCES psicologos(id) ON DELETE CASCADE,
    id_paciente INTEGER NOT NULL REFERENCES pacientes(id_paciente) ON DELETE CASCADE,
    id_pagamento INTEGER REFERENCES pagamentos(id_pagamento) ON DELETE SET NULL,
    dia DATE NOT NULL,
    horario_inicio TIMESTAMPTZ NOT NULL,
    horario_fim TIMESTAMPTZ NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);