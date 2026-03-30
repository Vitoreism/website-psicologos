import { Search, FileText, MoreVertical, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Skeleton } from '../ui/Skeleton';
import { pacienteService } from '../../services/api';

export function DashboardPatients() {
  const [isLoading, setIsLoading] = useState(true);
  const [patients, setPatients] = useState([]);
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ primeiro_nome: '', ultimo_nome: '', email: '' });
  const [submitError, setSubmitError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
        setIsLoading(true);
        const data = await pacienteService.getAll();
        setPatients(data);
    } catch (error) {
        console.error("Erro ao carregar pacientes:", error);
    } finally {
        setIsLoading(false);
    }
  };

  const handleCreatePatient = async (e) => {
      e.preventDefault();
      setIsSubmitting(true);
      setSubmitError('');
      
      try {
          await pacienteService.create(formData);
          setIsModalOpen(false);
          setFormData({ primeiro_nome: '', ultimo_nome: '', email: '' });
          await fetchPatients();
      } catch (err) {
          setSubmitError(err.message);
      } finally {
          setIsSubmitting(false);
      }
  };

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
        <button 
          onClick={() => setIsModalOpen(true)}
          className="bg-sage-600 text-white rounded-full px-6 py-2.5 text-sm font-semibold hover:bg-sage-700 transition-all shadow-md shrink-0"
        >
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
                <th className="p-4 font-semibold">Contato</th>
                <th className="p-4 font-semibold text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-sage-50">
              {patients.map((p) => (
                <tr key={p.id} className="hover:bg-sage-50/30 transition-colors">
                  <td className="p-4 font-medium text-deep-moss">{p.primeiro_nome} {p.ultimo_nome}</td>
                  <td className="p-4 text-sage-600 text-sm">{p.email}</td>
                  <td className="p-4 flex justify-end gap-2">
                    <button className="text-sage-500 hover:text-sage-700 bg-sage-100 hover:bg-sage-200 p-2 rounded-lg transition-colors" title="Ver Prontuário">
                      <FileText size={18} />
                    </button>
                    <button className="text-sage-500 hover:text-sage-700 bg-sage-100 hover:bg-sage-200 p-2 rounded-lg transition-colors" title="Deletar paciente" onClick={async () => {
                        if(confirm('Certeza que deseja deletar este paciente?')) {
                            await pacienteService.delete(p.id);
                            fetchPatients();
                        }
                    }}>
                      <MoreVertical size={18} />
                    </button>
                  </td>
                </tr>
              ))}
              {patients.length === 0 && (
                  <tr>
                      <td colSpan="3" className="p-8 text-center text-sage-500">Nenhum paciente castrado ainda.</td>
                  </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-deep-moss/40 backdrop-blur-sm p-4 animate-[fade-in_0.2s_ease-out]">
            <div className="bg-white rounded-3xl w-full max-w-md shadow-2xl overflow-hidden animate-[scale-in_0.2s_ease-out]">
                <div className="p-6 border-b border-sage-100 flex justify-between items-center bg-sage-50/50">
                    <h3 className="font-serif text-xl text-deep-moss font-semibold">Novo Paciente</h3>
                    <button onClick={() => setIsModalOpen(false)} className="text-sage-400 hover:text-sage-700 transition">
                        <X size={20} />
                    </button>
                </div>
                <div className="p-6">
                    {submitError && <div className="mb-4 p-3 bg-terracotta-50 text-terracotta-600 text-sm rounded-lg">{submitError}</div>}
                    <form onSubmit={handleCreatePatient} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                                <label className="text-xs font-bold text-deep-moss uppercase tracking-wider ml-1">Nome</label>
                                <input required type="text" value={formData.primeiro_nome} onChange={e => setFormData({...formData, primeiro_nome: e.target.value})} className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-sage-500 outline-none" />
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs font-bold text-deep-moss uppercase tracking-wider ml-1">Sobrenome</label>
                                <input required type="text" value={formData.ultimo_nome} onChange={e => setFormData({...formData, ultimo_nome: e.target.value})} className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-sage-500 outline-none" />
                            </div>
                        </div>
                        <div className="space-y-1.5">
                                <label className="text-xs font-bold text-deep-moss uppercase tracking-wider ml-1">E-mail</label>
                                <input required type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-sage-500 outline-none" />
                        </div>
                        <button disabled={isSubmitting} type="submit" className="w-full mt-4 bg-sage-600 hover:bg-sage-700 text-white font-bold h-12 rounded-xl transition cursor-pointer disabled:opacity-50">
                            {isSubmitting ? 'Salvando...' : 'Cadastrar Paciente'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
      )}
    </div>
  );
}

export default DashboardPatients;
