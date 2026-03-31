import { useState, useEffect } from 'react';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import format from 'date-fns/format';
import parse from 'date-fns/parse';
import startOfWeek from 'date-fns/startOfWeek';
import getDay from 'date-fns/getDay';
import ptBR from 'date-fns/locale/pt-BR';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { Plus, X, Check, Unlink, Trash2 } from 'lucide-react';
import { Skeleton } from '../ui/Skeleton';
import { agendamentoService } from '../../services/api';

const locales = {
  'pt-BR': ptBR,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

export function DashboardCalendar() {
  const [isLoading, setIsLoading] = useState(true);
  const [googleConnected, setGoogleConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isDisconnecting, setIsDisconnecting] = useState(false);

  const [events, setEvents] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(''); // erro do formulário de agendamento
  const [selectedEvent, setSelectedEvent] = useState(null); // evento clicado no calendário
  const [isDeletingEvent, setIsDeletingEvent] = useState(false);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    date: '',
    startTime: '',
    endTime: '',
    email: '',
    value: '',
    paymentMethod: 'PIX'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (formError) setFormError(''); // limpa erro ao editar
  };

  // Busca eventos do Google Calendar para o mês atual
  const fetchGoogleEvents = async () => {
    try {
      const now = new Date();
      const inicio = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const fim = new Date(now.getFullYear(), now.getMonth() + 2, 0);
      
      const data = await agendamentoService.listarEventos(
        inicio.toISOString().slice(0, 19),
        fim.toISOString().slice(0, 19)
      );

      const eventosFormatados = data.eventos.map(ev => ({
        id: ev.id,
        title: ev.title,
        start: new Date(ev.start),
        end: new Date(ev.end),
      }));

      setEvents(eventosFormatados);
    } catch (err) {
      console.error('Erro ao buscar eventos do Google:', err);
    }
  };

  // Cria evento no Google Calendar via API
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title || !formData.date || !formData.startTime || !formData.endTime) {
      alert('Preencha os campos obrigatórios (Título, Data, Horário Início, Horário Fim).');
      return;
    }
    
    setIsSubmitting(true);
    try {
      const startDateTime = `${formData.date}T${formData.startTime}:00`;
      const endDateTime = `${formData.date}T${formData.endTime}:00`;

      await agendamentoService.criarAgendamento({
        titulo: formData.title,
        inicio: startDateTime,
        fim: endDateTime,
        descricao: formData.email ? `Paciente: ${formData.email}` : null,
        fuso_horario: 'America/Sao_Paulo'
      });

      setIsModalOpen(false);
      setFormData({
        title: '',
        date: '',
        startTime: '',
        endTime: '',
        email: '',
        value: '',
        paymentMethod: 'PIX'
      });

      // Recarrega os eventos do Google para mostrar o novo
      await fetchGoogleEvents();
    } catch (err) {
      // Verifica se é conflito de horário (409)
      if (err.message.includes('Já existe') || err.message.includes('409') || err.message.includes('compromisso')) {
        setFormError('Já existe um compromisso neste horário. Escolha outro horário.');
      } else {
        setFormError('Erro ao criar evento: ' + err.message);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Deletar evento do Google Calendar
  const handleDeleteEvent = async () => {
    if (!selectedEvent) return;
    setIsDeletingEvent(true);
    try {
      await agendamentoService.deletarEvento(selectedEvent.id);
      setSelectedEvent(null);
      await fetchGoogleEvents();
    } catch (err) {
      alert('Erro ao remover evento: ' + err.message);
    } finally {
      setIsDeletingEvent(false);
    }
  };

  // Task 1: Ao montar o componente, checar status do Google
  useEffect(() => {
    const initialize = async () => {
      try {
        // Verifica se voltou do fluxo OAuth do Google
        const params = new URLSearchParams(window.location.search);
        const googleResult = params.get('google');
        if (googleResult) {
          // Limpa o parâmetro da URL sem recarregar a página
          window.history.replaceState({}, '', window.location.pathname);
          if (googleResult === 'success') {
            setGoogleConnected(true);
            await fetchGoogleEvents();
            setIsLoading(false);
            return;
          }
        }

        const status = await agendamentoService.checkGoogleStatus();
        setGoogleConnected(status.google_connected);
        
        // Se Google está conectado, busca os eventos reais
        if (status.google_connected) {
          await fetchGoogleEvents();
        }
      } catch (err) {
        console.error('Erro ao verificar status do Google:', err);
        setGoogleConnected(false);
      } finally {
        setIsLoading(false);
      }
    };
    initialize();
  }, []);

  // Task 1: Conectar ao Google Calendar
  const handleGoogleConnect = async () => {
    setIsConnecting(true);
    try {
      const data = await agendamentoService.getGoogleLoginUrl();
      // Redireciona o navegador para o Google OAuth
      window.location.href = data.url;
    } catch (err) {
      alert('Erro ao conectar com o Google: ' + err.message);
      setIsConnecting(false);
    }
  };

  // Task 6: Desconectar do Google Calendar
  const handleGoogleDisconnect = async () => {
    if (!confirm('Deseja realmente desconectar o Google Calendar? Você não poderá criar eventos até reconectar.')) return;
    setIsDisconnecting(true);
    try {
      await agendamentoService.disconnectGoogle();
      setGoogleConnected(false);
    } catch (err) {
      alert('Erro ao desconectar: ' + err.message);
    } finally {
      setIsDisconnecting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 min-h-[600px] gap-4 animate-[fade-in_0.4s_ease-out]">
        {/* Logo girando como estrela */}
        <div style={{ animation: 'logo-spin 1.6s ease-in-out infinite' }} className="text-sage-500 drop-shadow-sm">
          <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" width="72" height="72">
            <path d="M24 4C22 18 6 22 4 24C6 26 22 30 24 44C26 30 42 26 44 24C42 22 26 18 24 4Z" fill="currentColor" opacity="0.85"/>
            <circle cx="24" cy="24" fill="currentColor" opacity="0.35" r="6"/>
          </svg>
        </div>
        <p className="text-sage-500 text-sm font-medium tracking-wide">Carregando sua agenda...</p>
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
    <div className="max-w-7xl mx-auto space-y-6 flex flex-col h-full animate-[fade-in_0.3s_ease-out]">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-4 gap-4">
        <div>
          <h2 className="font-serif text-3xl font-medium mb-2">Agenda</h2>
          <p className="text-sage-600">Seus compromissos sincronizados e prontos para o fluxo do dia.</p>
        </div>
        <div className="flex flex-wrap gap-3 items-center">

           {/* Task 1 + 6: Botão dinâmico de Google */}
           {googleConnected ? (
             <>
               {/* Badge "Google Conectado" */}
               <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-full px-5 py-2.5 text-sm font-semibold flex items-center gap-2 shadow-sm">
                 <Check size={16} strokeWidth={3} /> Google Conectado
               </div>
               {/* Botão Desconectar */}
               <button
                 onClick={handleGoogleDisconnect}
                 disabled={isDisconnecting}
                 className="bg-white border border-red-200 text-red-500 rounded-full px-5 py-2.5 text-sm font-semibold hover:bg-red-50 hover:border-red-300 transition-all shadow-sm flex items-center gap-2 disabled:opacity-50"
               >
                 <Unlink size={16} /> {isDisconnecting ? 'Desconectando...' : 'Desconectar'}
               </button>
             </>
           ) : (
             <button
               onClick={handleGoogleConnect}
               disabled={isConnecting}
               className="bg-white border border-sage-200 text-deep-moss rounded-full px-6 py-2.5 text-sm font-semibold hover:bg-sage-50 transition-all shadow-sm flex items-center gap-2 disabled:opacity-50"
             >
               <span className="material-symbols-outlined text-lg">sync</span>
               {isConnecting ? 'Conectando...' : 'Conectar Google Calendar'}
             </button>
           )}

           {/* Task 2: Bloquear Novo Evento se Google não conectado */}
           <div className="relative group">
             <button 
               onClick={() => { setIsModalOpen(true); setFormError(''); }}
               disabled={!googleConnected}
               className={`rounded-full px-6 py-2.5 text-sm font-semibold transition-all shadow-md flex items-center gap-2 ${
                 googleConnected 
                   ? 'bg-sage-600 text-white hover:bg-sage-700 cursor-pointer' 
                   : 'bg-sage-300 text-white cursor-not-allowed opacity-60'
               }`}>
               <Plus size={18} /> Novo Evento
             </button>
             {/* Tooltip quando desabilitado */}
             {!googleConnected && (
               <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 bg-deep-moss text-white text-xs rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-lg">
                 Conecte o Google Calendar primeiro
                 <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-deep-moss"></div>
               </div>
             )}
           </div>

        </div>
      </div>

      <div className="bg-white p-6 rounded-3xl border border-sage-100 shadow-sm flex-1 min-h-[600px] flex flex-col">
        <style>
          {`
            .rbc-calendar { font-family: 'Plus Jakarta Sans', sans-serif; min-height: 600px;}
            .rbc-event { background-color: #5a7a5a !important; border-radius: 8px; border: none; padding: 4px 8px; font-weight: 500;}
            .rbc-today { background-color: #f4f7f4 !important; }
            .rbc-toolbar button { border-radius: 8px; color: #4a634a; border-color: #d1ded1; }
            .rbc-toolbar button.rbc-active { background-color: #e6ede6; color: #2c3e2c; font-weight: 600; box-shadow: none;}
            .rbc-toolbar button:hover { background-color: #fdf8f6; border-color: #d68c6e; color: #d68c6e; }
          `}
        </style>
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          culture="pt-BR"
          defaultView="week"
          messages={{
             next: "Próximo",
             previous: "Anterior",
             today: "Hoje",
             month: "Mês",
             week: "Semana",
             day: "Dia"
          }}
          onSelectEvent={(event) => setSelectedEvent(event)}
        />
      </div>

      {/* Popup de detalhes do evento selecionado */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4 animate-[fade-in_0.15s_ease-out]" onClick={() => setSelectedEvent(null)}>
          <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl relative" onClick={e => e.stopPropagation()}>
            <button onClick={() => setSelectedEvent(null)} className="absolute top-4 right-4 text-sage-400 hover:text-sage-700 transition-colors">
              <X size={20} />
            </button>
            <div className="mb-4">
              <div className="bg-sage-100 rounded-xl p-3 mb-3">
                <h3 className="font-serif text-xl font-semibold text-deep-moss">{selectedEvent.title}</h3>
              </div>
              <p className="text-sm text-sage-600">
                <span className="font-semibold">Início:</span> {selectedEvent.start.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}
              </p>
              <p className="text-sm text-sage-600">
                <span className="font-semibold">Fim:</span> {selectedEvent.end.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}
              </p>
            </div>
            <button
              onClick={handleDeleteEvent}
              disabled={isDeletingEvent}
              className="w-full flex items-center justify-center gap-2 bg-red-50 border border-red-200 text-red-600 hover:bg-red-100 transition-colors rounded-xl py-2.5 font-semibold text-sm disabled:opacity-50"
            >
              <Trash2 size={16} />
              {isDeletingEvent ? 'Removendo...' : 'Remover da Agenda'}
            </button>
          </div>
        </div>
      )}

      {/* Modal Novo Evento */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4 animate-[fade-in_0.2s_ease-out]">
          <div className="bg-white rounded-3xl p-6 w-full max-w-md shadow-2xl relative">
            <button 
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-sage-500 hover:text-sage-800 transition-colors"
            >
              <X size={24} />
            </button>
            <h3 className="font-serif text-2xl font-medium text-deep-moss mb-6">Novo Evento</h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-sage-700 mb-1">Título da Consulta</label>
                <input required type="text" name="title" value={formData.title} onChange={handleInputChange} className="w-full border border-sage-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sage-400" placeholder="Ex: Terapia com João" />
              </div>

              <div>
                <label className="block text-sm font-semibold text-sage-700 mb-1">Data</label>
                <input required type="date" name="date" value={formData.date} onChange={handleInputChange} className="w-full border border-sage-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sage-400" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-sage-700 mb-1">Horário Início</label>
                  <input required type="time" name="startTime" value={formData.startTime} onChange={handleInputChange} className="w-full border border-sage-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sage-400" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-sage-700 mb-1">Horário Fim</label>
                  <input required type="time" name="endTime" value={formData.endTime} onChange={handleInputChange} className="w-full border border-sage-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sage-400" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-sage-700 mb-1">E-mail do Paciente</label>
                <input type="email" name="email" value={formData.email} onChange={handleInputChange} className="w-full border border-sage-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sage-400" placeholder="email@exemplo.com" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-sage-700 mb-1">Valor (R$)</label>
                  <input type="number" step="0.01" name="value" value={formData.value} onChange={handleInputChange} className="w-full border border-sage-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sage-400" placeholder="150.00" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-sage-700 mb-1">Método de Pgto</label>
                  <select name="paymentMethod" value={formData.paymentMethod} onChange={handleInputChange} className="w-full border border-sage-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sage-400 bg-white">
                    <option value="PIX">PIX</option>
                    <option value="Cartão de Crédito">Cartão de Crédito</option>
                    <option value="Transferência">Transferência</option>
                    <option value="Dinheiro">Dinheiro</option>
                    <option value="Plano de Saúde">Plano de Saúde</option>
                  </select>
                </div>
              </div>

              {/* Mensagem de erro de conflito */}
              {formError && (
                <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-700 font-medium">
                  {formError}
                </div>
              )}

              <div className="pt-2 flex justify-end gap-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-5 py-2.5 text-sage-600 font-semibold hover:bg-sage-50 rounded-full transition-colors">
                  Cancelar
                </button>
                <button disabled={isSubmitting} type="submit" className="bg-sage-600 text-white px-5 py-2.5 rounded-full font-semibold hover:bg-sage-700 transition-colors shadow-sm disabled:opacity-50">
                  {isSubmitting ? 'Salvando...' : 'Salvar Evento'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default DashboardCalendar;
