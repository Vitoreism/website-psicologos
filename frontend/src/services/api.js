const API_URL = 'http://127.0.0.1:8000/api';

// Helper: monta os headers com o token JWT automaticamente
function authHeaders(extra = {}) {
  const token = localStorage.getItem('@elo-token');
  const headers = { 'Content-Type': 'application/json', ...extra };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

function getApiErrorMessage(error, fallbackMessage) {
  const detail = error?.detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : null;
        return field ? `${field}: ${item.msg}` : item.msg;
      })
      .join(' | ');
  }

  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  return fallbackMessage;
}

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
    // Salva o objeto do psicólogo e o token JWT
    localStorage.setItem('@elo-psicologo', JSON.stringify(data.psicologo));
    if (data.access_token) {
      localStorage.setItem('@elo-token', data.access_token);
    }
    return data;
  },

  logout() {
    localStorage.removeItem('@elo-psicologo');
    localStorage.removeItem('@elo-token');
    window.location.href = '/auth';
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('@elo-psicologo');
    return userStr ? JSON.parse(userStr) : null;
  },

  getToken() {
    return localStorage.getItem('@elo-token');
  }
};

export const psicologoService = {
    async getProfile(crp) {
        const response = await fetch(`${API_URL}/psicologos/${crp}`, {
            headers: authHeaders()
        });
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
            headers: authHeaders(),
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error('Erro ao atualizar perfil');
        return response.json();
    },

    async getDashboardMetrics() {
        const response = await fetch(`${API_URL}/psicologos/painel/relatorio`, {
            headers: authHeaders()
        });
        if (!response.ok) throw new Error('Erro ao buscar métricas');
        return response.json();
    }
}

export const pacienteService = {
    async getAll() {
        const response = await fetch(`${API_URL}/pacientes/`, {
            headers: authHeaders()
        });
        if (!response.ok) throw new Error('Erro ao buscar pacientes');
        return response.json();
    },

    async create(pacienteData) {
        const response = await fetch(`${API_URL}/pacientes/`, {
            method: 'POST',
            headers: authHeaders(),
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
            method: 'DELETE',
            headers: authHeaders()
        });
        if (!response.ok) throw new Error('Erro ao deletar paciente');
        return response.json();
    }
}

export const consultaService = {
    async listar({ id_paciente, data_inicio, data_fim } = {}) {
        const params = new URLSearchParams();
        if (id_paciente) params.set('id_paciente', id_paciente);
        if (data_inicio) params.set('data_inicio', data_inicio);
        if (data_fim) params.set('data_fim', data_fim);

        const response = await fetch(`${API_URL}/consultas/?${params.toString()}`, {
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao listar consultas');
        }
        return response.json();
    },

    async buscarPorId(id) {
        const response = await fetch(`${API_URL}/consultas/${id}`, {
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao buscar consulta');
        }
        return response.json();
    }
}

export const financeiroService = {
    async getResumo(inicio, fim) {
        const params = new URLSearchParams({ inicio, fim });
        const response = await fetch(`${API_URL}/consultas/financeiro/resumo?${params}`, {
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao buscar resumo financeiro');
        }
        return response.json();
    },

    async getPorDia(inicio, fim) {
        const params = new URLSearchParams({ inicio, fim });
        const response = await fetch(`${API_URL}/consultas/financeiro/por-dia?${params}`, {
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao buscar faturamento diário');
        }
        return response.json();
    },

    async getPorMes(ano) {
        const params = new URLSearchParams({ ano });
        const response = await fetch(`${API_URL}/consultas/financeiro/por-mes?${params}`, {
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao buscar faturamento mensal');
        }
        return response.json();
    },

    async getPorMetodo(inicio, fim) {
        const params = new URLSearchParams({ inicio, fim });
        const response = await fetch(`${API_URL}/consultas/financeiro/por-metodo?${params}`, {
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao buscar faturamento por método');
        }
        return response.json();
    }
}

export const agendamentoService = {
    // Busca a URL de autorização do Google (requer token JWT)
    async getGoogleLoginUrl() {
        const response = await fetch(`${API_URL}/agendamentos/google-login`, {
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao gerar URL do Google');
        }
        return response.json();
    },

    // Cria um novo agendamento no Google Calendar (requer token JWT)
    async criarAgendamento(eventData) {
        const response = await fetch(`${API_URL}/agendamentos/criar-agendamento`, {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify(eventData)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(getApiErrorMessage(error, 'Erro ao criar agendamento'));
        }
        return response.json();
    },

    // Verifica se o psicólogo já conectou o Google Calendar
    async checkGoogleStatus() {
        const response = await fetch(`${API_URL}/agendamentos/google-status`, {
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao verificar status do Google');
        }
        return response.json();
    },

    // Desconecta o Google Calendar (limpa o token)
    async disconnectGoogle() {
        const response = await fetch(`${API_URL}/agendamentos/google-disconnect`, {
            method: 'POST',
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao desconectar Google');
        }
        return response.json();
    },

    // Lista eventos do Google Calendar para um período
    async listarEventos(inicio, fim) {
        const params = new URLSearchParams({ inicio, fim });
        const response = await fetch(`${API_URL}/agendamentos/listar-eventos?${params}`, {
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao listar eventos');
        }
        return response.json();
    },

    // Deleta um evento do Google Calendar pelo ID
    async deletarEvento(eventId) {
        const response = await fetch(`${API_URL}/agendamentos/deletar-evento/${eventId}`, {
            method: 'DELETE',
            headers: authHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao remover evento');
        }
        return response.json();
    }
}
