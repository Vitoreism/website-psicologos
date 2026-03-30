import { useState, useEffect } from 'react';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import format from 'date-fns/format';
import parse from 'date-fns/parse';
import startOfWeek from 'date-fns/startOfWeek';
import getDay from 'date-fns/getDay';
import ptBR from 'date-fns/locale/pt-BR';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { Plus, X } from 'lucide-react';
import { Skeleton } from '../ui/Skeleton';

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

  // Mock events similar to Google Calendar API structure
  const [events, setEvents] = useState([
    {
      id: 'gcal_event_1',
      title: 'Terapia com Ana Silva',
      start: new Date(new Date().setHours(14, 0, 0, 0)),
      end: new Date(new Date().setHours(14, 50, 0, 0)),
      summary: 'Primeira Sessão', // Google Calendar typically uses 'summary' for title too
    },
    {
      id: 'gcal_event_2',
      title: 'Acompanhamento Carlos Santos',
      start: new Date(new Date().setHours(15, 30, 0, 0)),
      end: new Date(new Date().setHours(16, 20, 0, 0)),
    },
  ]);

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
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.title || !formData.date || !formData.startTime || !formData.endTime) {
      alert('Preencha os campos obrigatórios (Título, Data, Horário Início, Horário Fim).');
      return;
    }
    
    const startDateTime = new Date(`${formData.date}T${formData.startTime}:00`);
    const endDateTime = new Date(`${formData.date}T${formData.endTime}:00`);

    const newEvent = {
      id: `local_event_${Date.now()}`,
      title: formData.title,
      start: startDateTime,
      end: endDateTime,
      summary: formData.title,
      email: formData.email,
      valor: formData.value,
      metodo_pagamento: formData.paymentMethod
    };

    setEvents([...events, newEvent]);
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
  };

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto space-y-6 flex flex-col h-full animate-[fade-in_0.5s_ease-out]">
         <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-4 gap-4 w-full">
           <div className="space-y-3">
             <Skeleton className="h-10 w-48 bg-sage-200/60 rounded-lg" />
             <Skeleton className="h-5 w-80 bg-sage-200/40 rounded-md" />
           </div>
           <div className="flex gap-3">
             <Skeleton className="h-10 w-56 rounded-full bg-sage-200/40" />
             <Skeleton className="h-10 w-36 rounded-full bg-sage-200/60" />
           </div>
         </div>
         <Skeleton className="flex-1 min-h-[600px] w-full rounded-3xl bg-white border border-sage-100/50 shadow-sm" />
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
        <div className="flex flex-wrap gap-3">
           <button className="bg-white border border-sage-200 text-deep-moss rounded-full px-6 py-2.5 text-sm font-semibold hover:bg-sage-50 transition-all shadow-sm flex items-center gap-2">
              <span className="material-symbols-outlined text-lg">sync</span> Conectar Google Calendar
           </button>
           <button 
              onClick={() => setIsModalOpen(true)}
              className="bg-sage-600 text-white rounded-full px-6 py-2.5 text-sm font-semibold hover:bg-sage-700 transition-all shadow-md flex items-center gap-2">
              <Plus size={18} /> Novo Evento
           </button>
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
        />
      </div>

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

              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-5 py-2.5 text-sage-600 font-semibold hover:bg-sage-50 rounded-full transition-colors">
                  Cancelar
                </button>
                <button type="submit" className="bg-sage-600 text-white px-5 py-2.5 rounded-full font-semibold hover:bg-sage-700 transition-colors shadow-sm">
                  Salvar Evento
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
