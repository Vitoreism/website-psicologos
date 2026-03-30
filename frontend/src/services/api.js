const API_URL = 'http://127.0.0.1:8000/api';

export const authService = {
  async register(psicologoData) {
    const response = await fetch(`${API_URL}/psicologos/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(psicologoData)
    });
        if (!response.ok) {
            const error = await response.json();
            if (Array.isArray(error.detail)) {
                throw new Error(error.detail[0].msg);
            }
            throw new Error(error.detail || 'Erro ao registrar');
        }
        return response.json();
  },

  async login(email, senha) {
    const response = await fetch(`${API_URL}/psicologos/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, senha })
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro de autenticação');
    }
    const data = await response.json();
    // Salva o objeto do psicólogo e uma flag de autenticação
    localStorage.setItem('@elo-psicologo', JSON.stringify(data.psicologo));
    return data;
  },

  logout() {
    localStorage.removeItem('@elo-psicologo');
    window.location.href = '/auth';
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('@elo-psicologo');
    return userStr ? JSON.parse(userStr) : null;
  }
};

export const psicologoService = {
    async getProfile(crp) {
        const response = await fetch(`${API_URL}/psicologos/${crp}`);
        if (!response.ok) throw new Error('Erro ao buscar perfil');
        return response.json();
    },
    
    async updateProfile(crp, data) {
        // Enviar apenas os campos presentes
        const payload = Object.keys(data).reduce((acc, current) => {
            if (data[current]) acc[current] = data[current];
            return acc;
        }, {});
        
        const response = await fetch(`${API_URL}/psicologos/${crp}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error('Erro ao atualizar perfil');
        return response.json();
    },

    async getDashboardMetrics() {
        const response = await fetch(`${API_URL}/psicologos/painel/relatorio`);
        if (!response.ok) throw new Error('Erro ao buscar métricas');
        return response.json();
    }
}

export const pacienteService = {
    async getAll() {
        const response = await fetch(`${API_URL}/pacientes/`);
        if (!response.ok) throw new Error('Erro ao buscar pacientes');
        return response.json();
    },

    async create(pacienteData) {
        const response = await fetch(`${API_URL}/pacientes/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pacienteData)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao criar paciente');
        }
        return response.json();
    },

    async delete(id) {
         const response = await fetch(`${API_URL}/pacientes/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Erro ao deletar paciente');
        return response.json();
    }
}
