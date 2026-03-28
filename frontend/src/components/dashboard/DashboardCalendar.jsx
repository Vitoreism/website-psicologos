import { useState, useEffect } from 'react';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import format from 'date-fns/format';
import parse from 'date-fns/parse';
import startOfWeek from 'date-fns/startOfWeek';
import getDay from 'date-fns/getDay';
import ptBR from 'date-fns/locale/pt-BR';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { Plus } from 'lucide-react';
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
           <button className="bg-sage-600 text-white rounded-full px-6 py-2.5 text-sm font-semibold hover:bg-sage-700 transition-all shadow-md flex items-center gap-2">
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
    </div>
  );
}

export default DashboardCalendar;
