import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, ArrowRight } from 'lucide-react';
import { authService } from '../services/api';

export function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  
  const [formData, setFormData] = useState({
    email: '',
    senha: '',
    crp: '',
    primeiro_nome: '',
    ultimo_nome: ''
  });
  const [errorMsg, setErrorMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setIsLoading(true);

    try {
        if (isLogin) {
            await authService.login(formData.email, formData.senha);
            navigate('/dashboard');
        } else {
            await authService.register({
                crp: formData.crp,
                primeiro_nome: formData.primeiro_nome,
                ultimo_nome: formData.ultimo_nome,
                email: formData.email,
                senha: formData.senha
            });
            await authService.login(formData.email, formData.senha);
            navigate('/dashboard');
        }
    } catch (err) {
        setErrorMsg(err.message);
    } finally {
        setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-sage-50 flex items-center justify-center p-6 font-sans">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-xl overflow-hidden p-8 border border-sage-100 relative">
        {/* Blob background decoration */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-terracotta-100 rounded-full blur-3xl opacity-50 -z-10 transform translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-sage-200 rounded-full blur-3xl opacity-50 -z-10 transform -translate-x-1/2 translate-y-1/2"></div>
        
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="size-10 text-sage-600">
              <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <path d="M24 4C22 18 6 22 4 24C6 26 22 30 24 44C26 30 42 26 44 24C42 22 26 18 24 4Z" fill="currentColor" opacity="0.8"></path>
                <circle cx="24" cy="24" fill="currentColor" opacity="0.4" r="6"></circle>
              </svg>
            </div>
          </div>
          <h2 className="font-serif text-3xl font-semibold text-deep-moss mb-2">
            {isLogin ? 'Bem-vindo de volta' : 'Crie seu Espaço'}
          </h2>
          <p className="text-sage-600 text-sm">
            {isLogin 
              ? 'Acesse sua área profissional no Elo Terapêutico.' 
              : 'Junte-se à comunidade de terapeutas que escolheram o equilíbrio.'}
          </p>
        </div>

        {/* Toggle Login/Sign Up */}
        <div className="flex bg-sage-100/50 p-1 rounded-full mb-8">
          <button
            type="button"
            className={`flex-1 py-2 text-sm font-semibold rounded-full transition-all ${isLogin ? 'bg-white text-deep-moss shadow-sm' : 'text-sage-600 hover:text-deep-moss'}`}
            onClick={() => { setIsLogin(true); setErrorMsg(''); }}
          >
            Entrar
          </button>
          <button
            type="button"
            className={`flex-1 py-2 text-sm font-semibold rounded-full transition-all ${!isLogin ? 'bg-white text-deep-moss shadow-sm' : 'text-sage-600 hover:text-deep-moss'}`}
            onClick={() => { setIsLogin(false); setErrorMsg(''); }}
          >
            Cadastrar
          </button>
        </div>

        {errorMsg && (
            <div className="mb-4 p-3 rounded-xl bg-terracotta-50 text-terracotta-600 text-sm font-medium border border-terracotta-100 animate-[fade-in_0.3s_ease]">
                {errorMsg}
            </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          
          {!isLogin && (
            <>
              <div className="space-y-1.5">
                <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">CRP</label>
                <input required minLength={4} name="crp" value={formData.crp} onChange={handleChange} type="text" className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 focus:border-terracotta-500 transition-all text-deep-moss placeholder:text-sage-400" placeholder="Ex: 00/0000" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">Nome</label>
                  <input required minLength={2} name="primeiro_nome" value={formData.primeiro_nome} onChange={handleChange} type="text" className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 focus:border-terracotta-500 transition-all text-deep-moss placeholder:text-sage-400" placeholder="Primeiro nome" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">Sobrenome</label>
                  <input required minLength={2} name="ultimo_nome" value={formData.ultimo_nome} onChange={handleChange} type="text" className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 focus:border-terracotta-500 transition-all text-deep-moss placeholder:text-sage-400" placeholder="Último nome" />
                </div>
              </div>
            </>
          )}

          <div className="space-y-1.5">
            <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">E-mail</label>
            <input required name="email" value={formData.email} onChange={handleChange} type="email" className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 focus:ring-2 focus:ring-terracotta-500 focus:border-terracotta-500 transition-all text-deep-moss placeholder:text-sage-400" placeholder="seuemail@exemplo.com" />
          </div>

          <div className="space-y-1.5 relative">
            <div className="flex justify-between">
              <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">Senha</label>
              {isLogin && (
                <a href="#" className="text-terracotta-500 hover:text-terracotta-600 text-xs font-medium">Esqueceu a senha?</a>
              )}
            </div>
            <div className="relative">
              <input 
                required 
                minLength={8}
                name="senha"
                value={formData.senha}
                onChange={handleChange}
                type={showPassword ? "text" : "password"} 
                className="w-full bg-sage-50/50 border border-sage-200 rounded-xl h-12 px-4 pr-10 focus:ring-2 focus:ring-terracotta-500 focus:border-terracotta-500 transition-all text-deep-moss placeholder:text-sage-400" 
                placeholder="••••••••" 
              />
              <button 
                type="button" 
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sage-400 hover:text-sage-600"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {!isLogin && <p className="text-xs text-sage-500 mt-1 ml-1">A senha precisa ter de 8 a 32 caracteres, incluindo letras (maiúsculas e minúsculas) e números.</p>}
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full bg-sage-600 text-white rounded-xl h-12 mt-6 text-sm font-bold shadow-lg shadow-sage-600/20 hover:bg-sage-700 disabled:opacity-50 transition-all flex items-center justify-center gap-2 transform hover:-translate-y-0.5 active:scale-95"
          >
            {isLoading ? 'Aguarde...' : (isLogin ? 'Entrar' : 'Finalizar Cadastro')}
            {!isLoading && <ArrowRight size={18} />}
          </button>
        </form>
        
      </div>
    </div>
  );
}

export default AuthPage;

