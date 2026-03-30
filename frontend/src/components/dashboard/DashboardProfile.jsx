import { Save } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Skeleton } from '../ui/Skeleton';
import { authService, psicologoService } from '../../services/api';

export function DashboardProfile() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [originalProfile, setOriginalProfile] = useState(null);
  
  const [profile, setProfile] = useState({ primeiro_nome: '', ultimo_nome: '', crp: '', email: '' });

  const handleCancel = () => {
    setIsEditing(false);
    if(originalProfile) setProfile(originalProfile);
    setSuccessMsg('');
    setErrorMsg('');
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
      try {
          setIsLoading(true);
          const currentUser = authService.getCurrentUser();
          if (currentUser && currentUser.crp) {
              const data = await psicologoService.getProfile(currentUser.crp);
              const fetchedProfile = {
                 primeiro_nome: data.primeiro_nome,
                 ultimo_nome: data.ultimo_nome,
                 crp: data.crp,
                 email: data.email
              };
              setProfile(fetchedProfile);
              setOriginalProfile(fetchedProfile);
          }
      } catch (err) {
          console.error("Erro ao carregar perfil", err);
          setErrorMsg("Erro ao carregar os dados de perfil.");
      } finally {
          setIsLoading(false);
      }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccessMsg('');
    setErrorMsg('');
    setIsSaving(true);
    try {
        await psicologoService.updateProfile(profile.crp, {
            primeiro_nome: profile.primeiro_nome,
            ultimo_nome: profile.ultimo_nome,
            email: profile.email
        });
        setSuccessMsg('Perfil atualizado com sucesso!');
        setIsEditing(false);
        setOriginalProfile(profile);
        
        // Atualiza o local storage também
        const currentUser = authService.getCurrentUser();
        localStorage.setItem('@elo-psicologo', JSON.stringify({
            ...currentUser,
            primeiro_nome: profile.primeiro_nome,
            ultimo_nome: profile.ultimo_nome,
            email: profile.email
        }));
    } catch(err) {
        setErrorMsg(err.message || 'Erro ao atualizar perfil.');
    } finally {
        setIsSaving(false);
    }
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
        {successMsg && <div className="mb-6 p-4 bg-sage-100 text-sage-800 font-semibold rounded-xl border border-sage-200">{successMsg}</div>}
        {errorMsg && <div className="mb-6 p-4 bg-terracotta-50 text-terracotta-600 font-semibold rounded-xl border border-terracotta-100">{errorMsg}</div>}

        <form onSubmit={handleSubmit} className="space-y-8">
          
          <div className="flex flex-col sm:flex-row gap-8 items-start">
            <div className="flex flex-col items-center gap-4 shrink-0">
               <div className="size-32 rounded-full bg-sage-100 overflow-hidden border-4 border-white shadow-lg flex items-center justify-center text-sage-400">
                  <span className="text-4xl font-serif text-sage-600 uppercase">{profile.primeiro_nome?.charAt(0) || 'P'}</span>
               </div>
            </div>
            
            <div className="flex-1 space-y-4 w-full">
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">Primeiro Nome</label>
                    <input type="text" disabled={!isEditing} value={profile.primeiro_nome} onChange={e => setProfile({...profile, primeiro_nome: e.target.value})} className={`w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss outline-none ${!isEditing ? 'opacity-70 cursor-not-allowed bg-sage-100/30' : ''}`} />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">Sobrenome</label>
                    <input type="text" disabled={!isEditing} value={profile.ultimo_nome} onChange={e => setProfile({...profile, ultimo_nome: e.target.value})} className={`w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss outline-none ${!isEditing ? 'opacity-70 cursor-not-allowed bg-sage-100/30' : ''}`} />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">CRP</label>
                    <input type="text" value={profile.crp} disabled className="w-full bg-sage-100/50 border border-sage-200 rounded-xl h-12 px-4 text-sage-500 cursor-not-allowed outline-none" />
                  </div>
               </div>
            </div>
          </div>

          <hr className="border-sage-100" />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
             <div className="space-y-1.5">
                <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">E-mail de Contato (Login)</label>
                <input type="email" disabled={!isEditing} value={profile.email} onChange={e => setProfile({...profile, email: e.target.value})} className={`w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss outline-none ${!isEditing ? 'opacity-70 cursor-not-allowed bg-sage-100/30' : ''}`} />
             </div>
          </div>

          <div className="pt-4 flex justify-end gap-3">
            {!isEditing ? (
               <button type="button" onClick={(e) => { e.preventDefault(); setIsEditing(true); }} className="bg-sage-600 text-white rounded-xl px-8 py-3 text-sm font-bold shadow-md hover:bg-sage-700 transition-all">
                 Editar Perfil
               </button>
            ) : (
               <>
                 <button type="button" onClick={handleCancel} className="px-6 py-3 text-sm font-bold text-sage-600 hover:bg-sage-50 rounded-xl transition-all border border-sage-200">
                   Cancelar
                 </button>
                 <button disabled={isSaving} type="submit" className="bg-terracotta-500 text-white rounded-xl px-8 py-3 text-sm font-bold shadow-lg shadow-terracotta-500/20 hover:bg-terracotta-600 disabled:opacity-50 transition-all flex items-center gap-2">
                   <Save size={18} />
                   {isSaving ? 'Salvando...' : 'Salvar Alterações'}
                 </button>
               </>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

export default DashboardProfile;
