import { TrendingUp, CreditCard, DollarSign } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Skeleton } from '../ui/Skeleton';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';

export function DashboardMetrics() {
  const [isLoading, setIsLoading] = useState(true);

  const revenueData = []; // Aguardando backend

  const sourceData = []; // Aguardando backend

  const COLORS = ['#5a7a5a', '#d68c6e', '#d1ded1'];

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto space-y-6 animate-[fade-in_0.5s_ease-out]">
        <div className="mb-8 space-y-3">
          <Skeleton className="h-10 w-48 bg-sage-200/60 rounded-lg" />
          <Skeleton className="h-5 w-80 bg-sage-200/40 rounded-md" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-[104px] rounded-2xl bg-sage-100/50" />)}
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
      <div className="mb-8">
        <h2 className="font-serif text-3xl font-medium mb-2">Métricas e Faturamento</h2>
        <p className="text-sage-600">Acompanhe a saúde financeira e o desempenho da sua clínica.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-sage-100 shadow-sm flex items-center gap-4">
          <div className="bg-sage-100 p-4 rounded-full text-sage-600">
            <DollarSign size={28} />
          </div>
          <div>
             <p className="text-sage-600 text-sm font-semibold uppercase tracking-wider">Faturamento no Mês</p>
             <h3 className="text-3xl font-serif text-deep-moss mt-1">R$ 0,00</h3>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-6 border border-sage-100 shadow-sm flex items-center gap-4">
          <div className="bg-terracotta-100 p-4 rounded-full text-terracotta-500">
            <TrendingUp size={28} />
          </div>
          <div>
             <p className="text-sage-600 text-sm font-semibold uppercase tracking-wider">Consultas Realizadas</p>
             <h3 className="text-3xl font-serif text-deep-moss mt-1">0</h3>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-6 border border-sage-100 shadow-sm flex items-center gap-4">
          <div className="bg-sage-100 p-4 rounded-full text-sage-600">
            <CreditCard size={28} />
          </div>
          <div>
             <p className="text-sage-600 text-sm font-semibold uppercase tracking-wider">Ticket Médio</p>
             <h3 className="text-3xl font-serif text-deep-moss mt-1">R$ 0,00</h3>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        
        {/* Line Chart */}
        <div className="bg-white p-6 rounded-3xl border border-sage-100 shadow-sm lg:col-span-2">
          <h3 className="font-serif text-xl font-medium text-deep-moss mb-6">Evolução do Faturamento</h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={revenueData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e6ede6" vertical={false} />
                <XAxis dataKey="name" stroke="#5a7a5a" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#5a7a5a" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `R$ ${value}`} />
                <RechartsTooltip 
                  contentStyle={{ borderRadius: '12px', border: '1px solid #d1ded1', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  formatter={(value) => [`R$ ${value}`, 'Faturamento']}
                />
                <Line type="monotone" dataKey="total" stroke="#5a7a5a" strokeWidth={3} dot={{ r: 4, fill: '#5a7a5a' }} activeDot={{ r: 6, fill: '#d68c6e', stroke: '#fff', strokeWidth: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart */}
        <div className="bg-white p-6 rounded-3xl border border-sage-100 shadow-sm">
          <h3 className="font-serif text-xl font-medium text-deep-moss mb-6">Fontes de Pagamento</h3>
          <div className="h-72 w-full flex items-center justify-center">
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
                >
                  {sourceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ borderRadius: '12px', border: '1px solid #d1ded1' }}
                  formatter={(value) => [`${value}%`, 'Porcentagem']}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#4a634a' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardMetrics;
