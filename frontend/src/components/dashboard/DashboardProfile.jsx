import { Save } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Skeleton } from '../ui/Skeleton';

export function DashboardProfile() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Perfil atualizado com sucesso! (Integraçao conectada em breve)');
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-[fade-in_0.5s_ease-out]">
        <div className="mb-8 space-y-3">
          <Skeleton className="h-10 w-48 bg-sage-200/60 rounded-lg" />
          <Skeleton className="h-5 w-96 bg-sage-200/40 rounded-md" />
        </div>
        <div className="bg-white rounded-3xl border border-sage-100 shadow-sm p-8 space-y-8">
          <div className="flex flex-col sm:flex-row gap-8 items-start">
             <div className="flex flex-col items-center gap-4 shrink-0">
               <Skeleton className="size-32 rounded-full bg-sage-100/80" />
               <Skeleton className="h-8 w-24 rounded-full bg-sage-100/80" />
             </div>
             <div className="flex-1 space-y-4 w-full">
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <div className="space-y-2"><Skeleton className="h-4 w-24 bg-sage-200/40 rounded" /><Skeleton className="h-12 w-full rounded-xl bg-sage-50/50" /></div>
                 <div className="space-y-2"><Skeleton className="h-4 w-12 bg-sage-200/40 rounded" /><Skeleton className="h-12 w-full rounded-xl bg-sage-100/50" /></div>
               </div>
               <div className="space-y-2"><Skeleton className="h-4 w-36 bg-sage-200/40 rounded" /><Skeleton className="h-24 w-full rounded-xl bg-sage-50/50" /></div>
             </div>
          </div>
          <hr className="border-sage-100" />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
             <div className="space-y-2"><Skeleton className="h-4 w-32 bg-sage-200/40 rounded" /><Skeleton className="h-12 w-full rounded-xl bg-sage-50/50" /></div>
             <div className="space-y-2"><Skeleton className="h-4 w-40 bg-sage-200/40 rounded" /><Skeleton className="h-12 w-full rounded-xl bg-sage-50/50" /></div>
             <div className="space-y-2"><Skeleton className="h-4 w-40 bg-sage-200/40 rounded" /><Skeleton className="h-12 w-full rounded-xl bg-sage-50/50" /></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-[fade-in_0.3s_ease-out]">
      <div className="mb-8">
        <h2 className="font-serif text-3xl font-medium mb-2">Meu Perfil</h2>
        <p className="text-sage-600">Atualize suas informações públicas e configurações da clínica.</p>
      </div>

      <div className="bg-white rounded-3xl border border-sage-100 shadow-sm p-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          
          <div className="flex flex-col sm:flex-row gap-8 items-start">
            <div className="flex flex-col items-center gap-4 shrink-0">
               <div className="size-32 rounded-full bg-sage-100 overflow-hidden border-4 border-white shadow-lg flex items-center justify-center text-sage-400">
                  <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
                     <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"></path>
                  </svg>
               </div>
               <button type="button" className="text-xs font-semibold uppercase tracking-wider text-sage-600 hover:text-sage-800 bg-sage-100 px-4 py-2 rounded-full transition-colors">
                 Mudar Foto
               </button>
            </div>
            
            <div className="flex-1 space-y-4 w-full">
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">Nome Completo</label>
                    <input type="text" defaultValue="Dra. Helena Souza" className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss outline-none" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">CRP</label>
                    <input type="text" defaultValue="04/12345" disabled className="w-full bg-sage-100/50 border border-sage-200 rounded-xl h-12 px-4 text-sage-500 cursor-not-allowed outline-none" />
                  </div>
               </div>
               
               <div className="space-y-1.5">
                  <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">Biografia Resumida</label>
                  <textarea rows="4" className="w-full bg-sage-50/50 border border-sage-200 rounded-xl p-4 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss outline-none resize-none" defaultValue="Especialista em Terapia Cognitivo-Comportamental (TCC) com foco em ansiedade e desenvolvimento pessoal. Acredito no poder transformador da escuta ativa."></textarea>
               </div>
            </div>
          </div>

          <hr className="border-sage-100" />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
             <div className="space-y-1.5">
                <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">E-mail de Contato</label>
                <input type="email" defaultValue="contato@helenasouza.com" className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss outline-none" />
             </div>
             <div className="space-y-1.5">
                <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">Telefone / WhatsApp</label>
                <input type="text" defaultValue="(11) 98765-4321" className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss outline-none" />
             </div>
             <div className="space-y-1.5">
                <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">Valor da Consulta (R$)</label>
                <input type="number" defaultValue="250" className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss outline-none" />
             </div>
          </div>

          <div className="pt-4 flex justify-end">
            <button type="submit" className="bg-terracotta-500 text-white rounded-xl px-8 py-3 text-sm font-bold shadow-lg shadow-terracotta-500/20 hover:bg-terracotta-600 transition-all flex items-center gap-2">
              <Save size={18} />
              Salvar Alterações
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default DashboardProfile;
