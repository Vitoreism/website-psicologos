import { Search, FileText, MoreVertical } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Skeleton } from '../ui/Skeleton';

export function DashboardPatients() {
  const [isLoading, setIsLoading] = useState(true);

  const patients = [
    { id: 1, name: 'Ana Silva', lastVisit: '10/10/2023', status: 'Ativo' },
    { id: 2, name: 'Carlos Santos', lastVisit: '05/10/2023', status: 'Ativo' },
    { id: 3, name: 'Mariana Costa', lastVisit: '12/10/2023', status: 'Inativo' },
    { id: 4, name: 'João Oliveira', lastVisit: '14/10/2023', status: 'Ativo' },
  ];

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto space-y-6 animate-[fade-in_0.5s_ease-out]">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-8 gap-4 w-full">
           <div className="space-y-3">
             <Skeleton className="h-10 w-48 bg-sage-200/60 rounded-lg" />
             <Skeleton className="h-5 w-80 bg-sage-200/40 rounded-md" />
           </div>
           <Skeleton className="h-10 w-40 rounded-full bg-sage-200/60" />
        </div>
        <Skeleton className="h-[500px] w-full rounded-2xl bg-white border border-sage-100/50 shadow-sm" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-[fade-in_0.3s_ease-out]">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-8 gap-4">
        <div>
          <h2 className="font-serif text-3xl font-medium mb-2">Pacientes</h2>
          <p className="text-sage-600">Gerencie todos os prontuários e anotações clínicas.</p>
        </div>
        <button className="bg-sage-600 text-white rounded-full px-6 py-2.5 text-sm font-semibold hover:bg-sage-700 transition-all shadow-md shrink-0">
           + Novo Paciente
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-sage-100 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-sage-100 bg-sage-50/30">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-sage-400" size={18} />
            <input 
              type="text" 
              placeholder="Buscar paciente por nome..." 
              className="w-full bg-white border border-sage-200 rounded-xl h-10 pl-10 pr-4 focus:ring-2 focus:ring-sage-500 focus:border-sage-500 text-sm outline-none transition-all"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[600px]">
            <thead>
              <tr className="bg-sage-50 text-sage-600 text-xs uppercase tracking-wider">
                <th className="p-4 font-semibold">Nome do Paciente</th>
                <th className="p-4 font-semibold">Status</th>
                <th className="p-4 font-semibold">Última Consulta</th>
                <th className="p-4 font-semibold text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-sage-50">
              {patients.map((p) => (
                <tr key={p.id} className="hover:bg-sage-50/30 transition-colors">
                  <td className="p-4 font-medium text-deep-moss">{p.name}</td>
                  <td className="p-4">
                    <span className={`px-3 py-1 text-xs font-semibold rounded-full ${p.status === 'Ativo' ? 'bg-sage-100 text-sage-700' : 'bg-terracotta-100 text-terracotta-600'}`}>
                      {p.status}
                    </span>
                  </td>
                  <td className="p-4 text-sage-600 text-sm">{p.lastVisit}</td>
                  <td className="p-4 flex justify-end gap-2">
                    <button className="text-sage-500 hover:text-sage-700 bg-sage-100 hover:bg-sage-200 p-2 rounded-lg transition-colors" title="Ver Prontuário">
                      <FileText size={18} />
                    </button>
                    <button className="text-sage-500 hover:text-sage-700 bg-sage-100 hover:bg-sage-200 p-2 rounded-lg transition-colors" title="Mais opções">
                      <MoreVertical size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default DashboardPatients;
