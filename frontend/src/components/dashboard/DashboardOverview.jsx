import { Calendar, Users, Bell, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Skeleton } from '../ui/Skeleton';
import { authService, psicologoService } from '../../services/api';

export function DashboardOverview() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [metrics, setMetrics] = useState({ total_pacientes: 0 });
  const [userName, setUserName] = useState('');

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

          const dadosRelatorio = await psicologoService.getDashboardMetrics();
          setMetrics({
              total_pacientes: dadosRelatorio.total_pacientes || 0
          });
      } catch (error) {
          console.error("Erro ao carregar dashboard", error);
      } finally {
          setIsLoading(false);
      }
  };

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto animate-[fade-in_0.5s_ease-out]">
        <div className="mb-8 space-y-3">
          <Skeleton className="h-10 w-64 bg-sage-200/60 rounded-lg" />
          <Skeleton className="h-5 w-96 bg-sage-200/40 rounded-md" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-[104px] rounded-2xl bg-sage-100/50" />)}
        </div>
        <div className="mt-8">
          <Skeleton className="h-[400px] rounded-2xl bg-white border border-sage-100/50 shadow-sm" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-[fade-in_0.3s_ease-out]">
      <div className="mb-8">
        <h2 className="font-serif text-3xl font-medium mb-2">Olá{userName ? `, ${userName}` : ', Profissional'}</h2>
        <p className="text-sage-600">Seu resumo de hoje, {new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-sage-100 shadow-sm flex items-center gap-4">
          <div className="bg-sage-100 p-4 rounded-full text-sage-600">
            <Calendar size={28} />
          </div>
          <div>
             <p className="text-sage-600 text-sm font-semibold uppercase tracking-wider">Consultas Hoje</p>
             <h3 className="text-3xl font-serif text-deep-moss mt-1">4</h3>
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
        <div className="bg-white rounded-2xl p-6 border border-sage-100 shadow-sm flex items-center gap-4">
          <div className="bg-sage-100 p-4 rounded-full text-sage-600">
            <Bell size={28} />
          </div>
          <div>
             <p className="text-sage-600 text-sm font-semibold uppercase tracking-wider">Lembretes</p>
             <h3 className="text-3xl font-serif text-deep-moss mt-1">1</h3>
          </div>
        </div>
      </div>

      {/* Upcoming Appointments */}
      <div className="bg-white rounded-2xl border border-sage-100 shadow-sm overflow-hidden mt-8">
        <div className="p-6 border-b border-sage-100 flex justify-between items-center">
          <h3 className="font-serif text-xl font-medium text-deep-moss">Próximas Consultas</h3>
          <button onClick={() => navigate('/dashboard/agenda')} className="text-terracotta-500 hover:text-terracotta-600 text-sm font-semibold flex items-center gap-1">
            Ver Agenda <ArrowRight size={16} />
          </button>
        </div>
        <div className="divide-y divide-sage-50">
          {[
            { time: '14:00', name: 'Ana Silva', type: 'Primeira Sessão' },
            { time: '15:30', name: 'Carlos Santos', type: 'Acompanhamento' },
            { time: '17:00', name: 'Mariana Costa', type: 'Acompanhamento' }
          ].map((apt, i) => (
            <div key={i} className="p-6 flex items-center justify-between hover:bg-sage-50/50 transition-colors">
              <div className="flex items-center gap-6">
                 <div className="text-xl font-semibold text-deep-moss min-w-16">{apt.time}</div>
                 <div>
                    <h4 className="font-semibold text-deep-moss">{apt.name}</h4>
                    <p className="text-sm text-sage-500">{apt.type}</p>
                 </div>
              </div>
              <button 
                onClick={() => navigate('/dashboard/pacientes')}
                className="text-sage-600 bg-sage-100 hover:bg-sage-200 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
               >
                 Ver Prontuário
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default DashboardOverview;
