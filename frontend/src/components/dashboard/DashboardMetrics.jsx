import { TrendingUp, CreditCard, DollarSign } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Skeleton } from '../ui/Skeleton';
import { financeiroService } from '../../services/api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';

const COLORS = ['#5a7a5a', '#d68c6e', '#d1ded1', '#a7bca7', '#e8c9bb'];

const getCurrentMonthValue = () => {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
};

const toApiDateTime = (date) => {
  const pad = (value) => String(value).padStart(2, '0');

  return [
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`,
    `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`,
  ].join('T');
};

const getMonthRange = (monthValue) => {
  const [year, month] = monthValue.split('-').map(Number);
  const start = new Date(year, month - 1, 1, 0, 0, 0);
  const end = new Date(year, month, 0, 23, 59, 59);

  return {
    inicio: toApiDateTime(start),
    fim: toApiDateTime(end),
  };
};

const formatCurrency = (value) =>
  new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(Number(value || 0));

const formatPaymentMethod = (method) => {
  const labels = {
    pix: 'PIX',
    cartao_credito: 'Cartão de Crédito',
    cartao_debito: 'Cartão de Débito',
    dinheiro: 'Dinheiro',
    transferencia: 'Transferência',
    plano_de_saude: 'Plano de Saúde',
  };

  return labels[method] || method.replaceAll('_', ' ');
};

const formatMonthLabel = (monthValue) => {
  const [year, month] = monthValue.split('-').map(Number);
  return new Date(year, month - 1, 1).toLocaleDateString('pt-BR', {
    month: 'long',
    year: 'numeric',
  });
};

export function DashboardMetrics() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedMonth, setSelectedMonth] = useState(getCurrentMonthValue());
  const [financialSummary, setFinancialSummary] = useState({
    total_faturado: 0,
    total_consultas: 0,
    por_metodo: [],
  });
  const [revenueData, setRevenueData] = useState([]);

  useEffect(() => {
    loadFinancialData();
  }, [selectedMonth]);

  const loadFinancialData = async () => {
    const { inicio, fim } = getMonthRange(selectedMonth);

    try {
      setIsLoading(true);
      setError('');

      const [summaryData, dailyData] = await Promise.all([
        financeiroService.getResumo(inicio, fim),
        financeiroService.getPorDia(inicio, fim),
      ]);

      setFinancialSummary(summaryData);
      setRevenueData(
        dailyData.map((entry) => ({
          name: entry.dia.slice(8, 10),
          dia: entry.dia,
          total: Number(entry.total || 0),
          quantidade_consultas: entry.quantidade_consultas,
        }))
      );
    } catch (err) {
      setError(err.message || 'Erro ao carregar o faturamento.');
    } finally {
      setIsLoading(false);
    }
  };

  const totalFaturado = Number(financialSummary.total_faturado || 0);
  const totalConsultas = Number(financialSummary.total_consultas || 0);
  const ticketMedio = totalConsultas > 0 ? totalFaturado / totalConsultas : 0;
  const sourceData = (financialSummary.por_metodo || []).map((entry) => ({
    name: formatPaymentMethod(entry.metodo_pagamento),
    value: Number(entry.total || 0),
    quantidade_consultas: entry.quantidade_consultas,
  }));

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto space-y-6 animate-[fade-in_0.5s_ease-out]">
        <div className="mb-8 space-y-3">
          <Skeleton className="h-10 w-56 bg-sage-200/60 rounded-lg" />
          <Skeleton className="h-5 w-96 bg-sage-200/40 rounded-md" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-[104px] rounded-2xl bg-sage-100/50" />)}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          <Skeleton className="lg:col-span-2 h-[400px] rounded-2xl bg-white border border-sage-100/50 shadow-sm" />
          <Skeleton className="h-[400px] rounded-2xl bg-white border border-sage-100/50 shadow-sm" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-[fade-in_0.3s_ease-out]">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-8">
        <div>
          <h2 className="font-serif text-3xl font-medium mb-2">Métricas e Faturamento</h2>
          <p className="text-sage-600">Acompanhe o faturamento das consultas registradas no período selecionado.</p>
        </div>
        <div className="w-full sm:w-auto">
          <label className="block text-xs font-semibold uppercase tracking-wider text-sage-600 mb-2">Mês de referência</label>
          <input
            type="month"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="w-full sm:w-auto bg-white border border-sage-200 rounded-xl h-11 px-4 focus:ring-2 focus:ring-sage-500 focus:border-sage-500 outline-none"
          />
        </div>
      </div>

      {error && (
        <div className="bg-terracotta-50 border border-terracotta-200 text-terracotta-700 rounded-2xl px-4 py-3 text-sm font-medium">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-sage-100 shadow-sm flex items-center gap-4">
          <div className="bg-sage-100 p-4 rounded-full text-sage-600">
            <DollarSign size={28} />
          </div>
          <div>
            <p className="text-sage-600 text-sm font-semibold uppercase tracking-wider">Faturamento no mês</p>
            <h3 className="text-3xl font-serif text-deep-moss mt-1">{formatCurrency(totalFaturado)}</h3>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-sage-100 shadow-sm flex items-center gap-4">
          <div className="bg-terracotta-100 p-4 rounded-full text-terracotta-500">
            <TrendingUp size={28} />
          </div>
          <div>
            <p className="text-sage-600 text-sm font-semibold uppercase tracking-wider">Consultas realizadas</p>
            <h3 className="text-3xl font-serif text-deep-moss mt-1">{totalConsultas}</h3>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-sage-100 shadow-sm flex items-center gap-4">
          <div className="bg-sage-100 p-4 rounded-full text-sage-600">
            <CreditCard size={28} />
          </div>
          <div>
            <p className="text-sage-600 text-sm font-semibold uppercase tracking-wider">Ticket médio</p>
            <h3 className="text-3xl font-serif text-deep-moss mt-1">{formatCurrency(ticketMedio)}</h3>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        <div className="bg-white p-6 rounded-3xl border border-sage-100 shadow-sm lg:col-span-2">
          <div className="mb-6">
            <h3 className="font-serif text-xl font-medium text-deep-moss">Evolução do Faturamento</h3>
            <p className="text-sm text-sage-500 mt-1">Visão diária de {formatMonthLabel(selectedMonth)}.</p>
          </div>

          <div className="h-72 w-full">
            {revenueData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={revenueData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e6ede6" vertical={false} />
                  <XAxis dataKey="name" stroke="#5a7a5a" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#5a7a5a" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => formatCurrency(value)} />
                  <RechartsTooltip
                    contentStyle={{ borderRadius: '12px', border: '1px solid #d1ded1', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    labelFormatter={(label, payload) => {
                      if (!payload?.length) return label;
                      const dia = payload[0].payload.dia;
                      return new Date(`${dia}T12:00:00`).toLocaleDateString('pt-BR', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                      });
                    }}
                    formatter={(value) => [formatCurrency(value), 'Faturamento']}
                  />
                  <Line type="monotone" dataKey="total" stroke="#5a7a5a" strokeWidth={3} dot={{ r: 4, fill: '#5a7a5a' }} activeDot={{ r: 6, fill: '#d68c6e', stroke: '#fff', strokeWidth: 2 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-center text-sage-500 text-sm px-6">
                Nenhum pagamento encontrado em {formatMonthLabel(selectedMonth)}.
              </div>
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-sage-100 shadow-sm">
          <div className="mb-6">
            <h3 className="font-serif text-xl font-medium text-deep-moss">Fontes de Pagamento</h3>
            <p className="text-sm text-sage-500 mt-1">Distribuição do faturamento no período.</p>
          </div>

          <div className="h-72 w-full flex items-center justify-center">
            {sourceData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sourceData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                    nameKey="name"
                  >
                    {sourceData.map((entry, index) => (
                      <Cell key={`cell-${entry.name}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip
                    contentStyle={{ borderRadius: '12px', border: '1px solid #d1ded1' }}
                    formatter={(value, name, item) => [
                      formatCurrency(value),
                      `${name} • ${item?.payload?.quantidade_consultas ?? 0} consultas`,
                    ]}
                  />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#4a634a' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-sage-500 text-sm px-6">
                Ainda não há formas de pagamento registradas neste período.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardMetrics;
