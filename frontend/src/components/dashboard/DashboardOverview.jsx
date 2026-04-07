import { Calendar, Users, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Skeleton } from '../ui/Skeleton';
import { authService, pacienteService, agendamentoService, consultaService } from '../../services/api';

const hasLinkedPatient = (description = '') =>
  description.startsWith('Paciente vinculado:') || description.startsWith('Paciente:');

const sanitizePatientDescription = (description = '') =>
  description.replace(/\s*\|\s*ID:\s*\d+\s*$/i, '').trim();

export function DashboardOverview() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [metrics, setMetrics] = useState({ total_pacientes: 0, consultas_hoje: 0 });
  const [userName, setUserName] = useState('');
  const [upcomingConsultations, setUpcomingConsultations] = useState([]);
  const [googleConnected, setGoogleConnected] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);

      const user = authService.getCurrentUser();
      if (user && user.primeiro_nome) {
        setUserName(user.primeiro_nome);
      }

      const pacientes = await pacienteService.getAll();
      const consultasHoje = await consultaService.getQuantidadeHoje();

      setMetrics({
        total_pacientes: pacientes.length,
        consultas_hoje: consultasHoje
      });

      const statusGoogle = await agendamentoService.checkGoogleStatus();
      setGoogleConnected(statusGoogle.google_connected);

      const now = new Date();
      const nextWeek = new Date();
      nextWeek.setDate(now.getDate() + 7);

      const strHoje = now.toISOString().split('T')[0];
      const strNextWeek = nextWeek.toISOString().split('T')[0];

      const proximas = await consultaService.listar({
        data_inicio: strHoje,
        data_fim: strNextWeek
      });

      const formatada = proximas.map((ev) => {
        const date = new Date(ev.horario_inicio);
        return {
          id: ev.id_consulta,
          time: date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
          dateStr: date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
          name: ev.nome_paciente,
          type: ev.email_paciente ? `Paciente vinculado | E-mail: ${ev.email_paciente}` : 'Consulta agendada'
        };
      });

      setUpcomingConsultations(formatada);
    } catch (error) {
      console.error('Erro ao carregar dashboard', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 min-h-[500px] gap-4 animate-[fade-in_0.4s_ease-out]">
        <div style={{ animation: 'logo-spin 1.6s ease-in-out infinite' }} className="text-sage-500 drop-shadow-sm">
          <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" width="72" height="72">
            <path d="M24 4C22 18 6 22 4 24C6 26 22 30 24 44C26 30 42 26 44 24C42 22 26 18 24 4Z" fill="currentColor" opacity="0.85" />
            <circle cx="24" cy="24" fill="currentColor" opacity="0.35" r="6" />
          </svg>
        </div>
        <p className="text-sage-500 text-sm font-medium tracking-wide">Carregando seu resumo...</p>
        <style>{`
          @keyframes logo-spin {
            0%   { transform: rotate(0deg) scale(1); }
            25%  { transform: rotate(90deg) scale(1.08); }
            50%  { transform: rotate(180deg) scale(1); }
            75%  { transform: rotate(270deg) scale(1.08); }
            100% { transform: rotate(360deg) scale(1); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-[fade-in_0.3s_ease-out]">
      <div className="mb-8">
        <h2 className="font-serif text-3xl font-medium mb-2">Olá{userName ? `, ${userName}` : ', Profissional'}</h2>
        <p className="text-sage-600">Seu resumo de hoje, {new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-sage-100 shadow-sm flex items-center gap-4">
          <div className="bg-sage-100 p-4 rounded-full text-sage-600">
            <Calendar size={28} />
          </div>
          <div>
            <p className="text-sage-600 text-sm font-semibold uppercase tracking-wider">Consultas Hoje</p>
            <h3 className="text-3xl font-serif text-deep-moss mt-1">
              {metrics.consultas_hoje}
            </h3>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-6 border border-sage-100 shadow-sm flex items-center gap-4">
          <div className="bg-terracotta-100 p-4 rounded-full text-terracotta-500">
            <Users size={28} />
          </div>
          <div>
            <p className="text-sage-600 text-sm font-semibold uppercase tracking-wider">Total de Pacientes</p>
            <h3 className="text-3xl font-serif text-deep-moss mt-1">{metrics.total_pacientes}</h3>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-sage-100 shadow-sm overflow-hidden mt-8">
        <div className="p-6 border-b border-sage-100 flex justify-between items-center">
          <h3 className="font-serif text-xl font-medium text-deep-moss">Próximas Consultas</h3>
          <div className="flex items-center gap-4">
            {!googleConnected && (
              <span className="text-xs font-semibold px-3 py-1 bg-terracotta-50 text-terracotta-500 rounded-full">
                Google Agenda desconectado
              </span>
            )}
            <button onClick={() => navigate('/dashboard/agenda')} className="text-terracotta-500 hover:text-terracotta-600 text-sm font-semibold flex items-center gap-1">
              Ver Agenda <ArrowRight size={16} />
            </button>
          </div>
        </div>
        <div className="divide-y divide-sage-50">
          {upcomingConsultations.length > 0 ? (
            upcomingConsultations.map((apt) => (
              <div key={apt.id} className="p-6 flex items-center justify-between hover:bg-sage-50/50 transition-colors">
                <div className="flex items-center gap-6">
                  <div className="flex flex-col items-center min-w-16">
                    <div className="text-xl font-bold text-deep-moss">{apt.time}</div>
                    <div className="text-[10px] uppercase font-bold text-sage-400">{apt.dateStr}</div>
                  </div>
                  <div>
                    <h4 className="font-semibold text-deep-moss">{apt.name}</h4>
                    <p className="text-sm text-sage-500 line-clamp-1">{apt.type}</p>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="p-12 text-center text-sage-500">
              Nenhuma consulta agendada para os próximos 7 dias.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DashboardOverview;
