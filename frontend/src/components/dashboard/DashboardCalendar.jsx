import { useState, useEffect } from 'react';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { useLocation, useNavigate } from 'react-router-dom';
import format from 'date-fns/format';
import parse from 'date-fns/parse';
import startOfWeek from 'date-fns/startOfWeek';
import getDay from 'date-fns/getDay';
import ptBR from 'date-fns/locale/pt-BR';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { Plus, X, Check, Unlink, Trash2 } from 'lucide-react';
import { Skeleton } from '../ui/Skeleton';
import { agendamentoService, pacienteService } from '../../services/api';

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

const initialFormData = {
  title: '',
  date: '',
  startTime: '',
  endTime: '',
  patientId: '',
  email: '',
  value: '',
  paymentMethod: 'pix'
};

const formatPatientDescription = (patient) =>
  `Paciente vinculado: ${patient.primeiro_nome} ${patient.ultimo_nome} | E-mail: ${patient.email}`;

const parseCurrencyValue = (value) => {
  const rawValue = String(value ?? '').trim();

  if (!rawValue) {
    return null;
  }

  const normalizedValue = rawValue.includes(',') && rawValue.includes('.')
    ? rawValue.replace(/\./g, '').replace(',', '.')
    : rawValue.replace(',', '.');

  const parsedValue = Number(normalizedValue);
  return Number.isFinite(parsedValue) ? parsedValue : null;
};

export function DashboardCalendar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(true);
  const [googleConnected, setGoogleConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isDisconnecting, setIsDisconnecting] = useState(false);

  const [events, setEvents] = useState([]);
  const [patients, setPatients] = useState([]);
  const [isPatientsLoading, setIsPatientsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isDeletingEvent, setIsDeletingEvent] = useState(false);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState(initialFormData);
  const selectedPatient = patients.find((patient) => String(patient.id) === formData.patientId);

  const fetchPatients = async () => {
    try {
      setIsPatientsLoading(true);
      const data = await pacienteService.getAll();
      setPatients(data);
    } catch (err) {
      console.error('Erro ao buscar pacientes:', err);
    } finally {
      setIsPatientsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    if (name === 'patientId') {
      const patient = patients.find((item) => String(item.id) === value);
      setFormData((prev) => ({
        ...prev,
        patientId: value,
        email: patient?.email ?? '',
        title: prev.title || (patient ? `Consulta com ${patient.primeiro_nome}` : prev.title),
      }));

      if (formError) setFormError('');
      return;
    }

    setFormData((prev) => ({ ...prev, [name]: value }));
    if (formError) setFormError('');
  };

  const handleOpenModal = async () => {
    setFormError('');
    setIsModalOpen(true);
    await fetchPatients();
  };

  const handleGoToPatients = () => {
    navigate('/dashboard/pacientes', {
      state: {
        openNewPatient: true,
        returnTo: '/dashboard/agenda',
        draftEvent: formData,
        prefillPatient: {
          email: formData.email,
        },
      },
    });
  };

  const fetchGoogleEvents = async () => {
    try {
      const now = new Date();
      const inicio = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const fim = new Date(now.getFullYear(), now.getMonth() + 2, 0);

      const data = await agendamentoService.listarEventos(
        inicio.toISOString().slice(0, 19),
        fim.toISOString().slice(0, 19)
      );

      const eventosFormatados = data.eventos.map((ev) => ({
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    const now = new Date();
    const parsedValue = parseCurrencyValue(formData.value);
    const startDateTimeStr = `${formData.date}T${formData.startTime}:00`;
    const endDateTimeStr = `${formData.date}T${formData.endTime}:00`;
    const startDate = new Date(startDateTimeStr);
    const endDate = new Date(endDateTimeStr);

    if (startDate < now) {
      setFormError('Não é possível criar consultas em datas ou horários que já passaram.');
      return;
    }

    if (!selectedPatient) {
      setFormError('Selecione um paciente cadastrado para vincular ao evento.');
      return;
    }

    if (!parsedValue || parsedValue <= 0) {
      setFormError('Informe um valor válido para a consulta.');
      return;
    }

    if (endDate <= startDate) {
      setFormError('O horário de término deve ser após o horário de início.');
      return;
    }

    setIsSubmitting(true);
    setFormError('');

    try {
      await agendamentoService.criarAgendamento({
        id_paciente: Number(formData.patientId),
        titulo: formData.title,
        dia: formData.date,
        inicio: startDateTimeStr,
        fim: endDateTimeStr,
        valor: parsedValue.toFixed(2),
        metodo_pagamento: formData.paymentMethod,
        descricao: formatPatientDescription(selectedPatient),
        fuso_horario: 'America/Sao_Paulo'
      });

      setIsModalOpen(false);
      setFormData(initialFormData);
      await fetchGoogleEvents();
    } catch (err) {
      if (err.message.includes('Já existe') || err.message.includes('409') || err.message.includes('compromisso')) {
        setFormError('Já existe um compromisso neste horário. Escolha outro horário.');
      } else {
        setFormError('Erro ao criar evento: ' + err.message);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

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

  useEffect(() => {
    const initialize = async () => {
      try {
        const params = new URLSearchParams(window.location.search);
        const googleResult = params.get('google');
        if (googleResult) {
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

  useEffect(() => {
    const state = location.state;

    if (!state?.selectedPatient && !state?.draftEvent) {
      return;
    }

    const patient = state.selectedPatient;
    const draftEvent = state.draftEvent || {};

    setIsModalOpen(true);
    setFormError('');
    setFormData({
      ...initialFormData,
      ...draftEvent,
      patientId: patient ? String(patient.id) : (draftEvent.patientId || ''),
      email: patient?.email ?? draftEvent.email ?? '',
      title: draftEvent.title || (patient ? `Consulta com ${patient.primeiro_nome}` : ''),
    });

    fetchPatients();
    navigate(location.pathname, { replace: true });
  }, [location.pathname, location.state, navigate]);

  const handleGoogleConnect = async () => {
    setIsConnecting(true);
    try {
      const data = await agendamentoService.getGoogleLoginUrl();
      window.location.href = data.url;
    } catch (err) {
      alert('Erro ao conectar com o Google: ' + err.message);
      setIsConnecting(false);
    }
  };

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
          {googleConnected ? (
            <>
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-full px-5 py-2.5 text-sm font-semibold flex items-center gap-2 shadow-sm">
                <Check size={16} strokeWidth={3} /> Google Conectado
              </div>
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

          <div className="relative group">
            <button
              onClick={handleOpenModal}
              disabled={!googleConnected}
              className={`rounded-full px-6 py-2.5 text-sm font-semibold transition-all shadow-md flex items-center gap-2 ${
                googleConnected
                  ? 'bg-sage-600 text-white hover:bg-sage-700 cursor-pointer'
                  : 'bg-sage-300 text-white cursor-not-allowed opacity-60'
              }`}
            >
              <Plus size={18} /> Novo Evento
            </button>
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
            next: 'Próximo',
            previous: 'Anterior',
            today: 'Hoje',
            month: 'Mês',
            week: 'Semana',
            day: 'Dia'
          }}
          onSelectEvent={(event) => setSelectedEvent(event)}
        />
      </div>

      {selectedEvent && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4 animate-[fade-in_0.15s_ease-out]" onClick={() => setSelectedEvent(null)}>
          <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl relative" onClick={(e) => e.stopPropagation()}>
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
                <div className="mb-1 flex items-center justify-between gap-3">
                  <label className="block text-sm font-semibold text-sage-700">Paciente Vinculado</label>
                  <button
                    type="button"
                    onClick={handleGoToPatients}
                    className="text-sm font-semibold text-sage-700 hover:text-sage-900 transition-colors"
                  >
                    + Novo paciente
                  </button>
                </div>
                <select
                  name="patientId"
                  value={formData.patientId}
                  onChange={handleInputChange}
                  required
                  className="w-full border border-sage-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sage-400 bg-white"
                >
                  <option value="">
                    {isPatientsLoading ? 'Carregando pacientes...' : 'Selecione um paciente cadastrado'}
                  </option>
                  {patients.map((patient) => (
                    <option key={patient.id} value={patient.id}>
                      {patient.primeiro_nome} {patient.ultimo_nome} - {patient.email}
                    </option>
                  ))}
                </select>
                <p className="mt-2 text-xs text-sage-500">
                  Escolha um paciente existente ou abra a aba de pacientes para cadastrar um novo e voltar para este evento.
                </p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-sage-700 mb-1">E-mail do Paciente</label>
                <input type="email" name="email" value={formData.email} readOnly className="w-full border border-sage-200 rounded-xl px-4 py-2 bg-sage-50 text-sage-600 focus:outline-none" placeholder="Selecione um paciente para preencher o e-mail" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-sage-700 mb-1">Valor (R$)</label>
                  <input required type="text" inputMode="decimal" name="value" value={formData.value} onChange={handleInputChange} className="w-full border border-sage-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sage-400" placeholder="150,00" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-sage-700 mb-1">Método de Pgto</label>
                  <select name="paymentMethod" value={formData.paymentMethod} onChange={handleInputChange} className="w-full border border-sage-200 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sage-400 bg-white">
                    <option value="pix">PIX</option>
                    <option value="cartao_credito">Cartão de Crédito</option>
                    <option value="cartao_debito">Cartão de Débito</option>
                    <option value="transferencia">Transferência</option>
                    <option value="dinheiro">Dinheiro</option>
                    <option value="plano_de_saude">Plano de Saúde</option>
                  </select>
                </div>
              </div>

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
