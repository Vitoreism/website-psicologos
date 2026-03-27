import { useNavigate } from 'react-router-dom';

export function DashboardPage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // #TODO: Desconectar o usuario na API real
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-cream font-sans text-deep-moss flex flex-col">
      <header className="sticky top-0 z-50 bg-white border-b border-sage-200/50 px-6 lg:px-16 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="size-8 text-sage-600">
            <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
              <path d="M24 4C22 18 6 22 4 24C6 26 22 30 24 44C26 30 42 26 44 24C42 22 26 18 24 4Z" fill="currentColor" opacity="0.8"></path>
              <circle cx="24" cy="24" fill="currentColor" opacity="0.4" r="6"></circle>
            </svg>
          </div>
          <h1 className="font-serif text-xl font-semibold tracking-tight">Elo Terapêutico <span className="text-sage-500">| Painel</span></h1>
        </div>
        <button 
          onClick={handleLogout}
          className="text-terracotta-500 hover:text-terracotta-600 text-sm font-semibold transition-colors flex items-center gap-2"
        >
          Sair do Sistema
        </button>
      </header>
      
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 lg:px-16 py-12">
        <div className="mb-10">
          <h2 className="font-serif text-3xl font-medium mb-2">Olá, Profissional</h2>
          <p className="text-sage-600">Bem-vindo(a) ao seu novo espaço de conexão e fluidez.</p>
        </div>
        
        <div className="bg-white rounded-3xl p-10 border border-sage-100 shadow-xl shadow-sage-200/10 text-center">
          <div className="mx-auto size-24 bg-sage-50 rounded-full flex items-center justify-center mb-6">
            <span className="material-symbols-outlined text-4xl text-sage-600">home_repair_service</span>
          </div>
          <h3 className="font-serif text-2xl font-medium text-deep-moss mb-4">Seu painel está em construção</h3>
          <p className="max-w-md mx-auto text-sage-600 font-light leading-relaxed">
            Nossa equipe de engenheiros terapêuticos está preparando as melhores ferramentas para facilitar suas sessões e gerenciamento de prontuários.
          </p>
        </div>
      </main>
    </div>
  );
}

export default DashboardPage;
