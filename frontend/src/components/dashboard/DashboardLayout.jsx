import { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Home, Calendar, Users, User, LogOut, BarChart3, ChevronRight, ChevronLeft } from 'lucide-react';

export function DashboardLayout() {
  const navigate = useNavigate();
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(false);

  const handleLogout = () => {
    // #TODO: Desconectar o usuario na API real
    navigate('/');
  };

  const navItems = [
    { name: 'Resumo', path: '/dashboard', icon: Home, end: true },
    { name: 'Agenda', path: '/dashboard/agenda', icon: Calendar },
    { name: 'Pacientes', path: '/dashboard/pacientes', icon: Users },
    { name: 'Faturamento', path: '/dashboard/faturamento', icon: BarChart3 },
    { name: 'Meu Perfil', path: '/dashboard/perfil', icon: User },
  ];

  return (
    <div className="h-screen bg-sage-50 font-sans text-deep-moss flex">
      {/* Sidebar */}
      <aside className={`transition-all duration-300 bg-white border-r border-sage-200/50 flex-col hidden lg:flex relative ${isSidebarExpanded ? 'w-64' : 'w-20 items-center'}`}>
        <button 
          onClick={() => setIsSidebarExpanded(!isSidebarExpanded)}
          className="absolute -right-3 top-8 bg-white border border-sage-400 rounded-full p-1 text-sage-600 hover:text-deep-moss hover:border-sage-600 shadow-md z-10 transition-colors"
        >
          {isSidebarExpanded ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>

        <div className={`p-6 border-b border-sage-100 flex ${isSidebarExpanded ? 'items-center gap-3 w-full' : 'justify-center w-full'}`}>
          <div className="size-8 text-sage-600 shrink-0" title="Elo Terapêutico">
            <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
              <path d="M24 4C22 18 6 22 4 24C6 26 22 30 24 44C26 30 42 26 44 24C42 22 26 18 24 4Z" fill="currentColor" opacity="0.8"></path>
              <circle cx="24" cy="24" fill="currentColor" opacity="0.4" r="6"></circle>
            </svg>
          </div>
          {isSidebarExpanded && <h1 className="font-serif text-xl font-semibold tracking-tight whitespace-nowrap overflow-hidden">Elo Terapêutico</h1>}
        </div>
        
        <nav className={`flex-1 py-6 space-y-2 overflow-y-auto w-full ${isSidebarExpanded ? 'px-4' : 'px-0 flex flex-col items-center'}`}>
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              end={item.end}
              title={!isSidebarExpanded ? item.name : undefined}
              className={({ isActive }) =>
                `rounded-xl transition-all flex items-center ${isSidebarExpanded ? 'px-4 py-3 gap-3 w-full text-sm font-medium' : 'p-3 justify-center'} ${
                  isActive
                    ? 'bg-sage-100 text-deep-moss shadow-sm'
                    : 'text-sage-600 hover:bg-sage-50 hover:text-deep-moss'
                }`
              }
            >
              <item.icon size={22} className="shrink-0" />
              {isSidebarExpanded && <span className="whitespace-nowrap">{item.name}</span>}
            </NavLink>
          ))}
        </nav>
        
        <div className={`p-4 border-t border-sage-100 w-full ${isSidebarExpanded ? '' : 'flex justify-center'}`}>
          <button
            onClick={handleLogout}
            title={!isSidebarExpanded ? 'Sair' : undefined}
            className={`rounded-xl transition-colors text-terracotta-500 hover:bg-terracotta-50 flex items-center ${isSidebarExpanded ? 'px-4 py-3 gap-3 w-full text-sm font-medium' : 'p-3 justify-center'}`}
          >
            <LogOut size={22} className="shrink-0" />
            {isSidebarExpanded && <span>Sair</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden h-screen relative">
        <header className="lg:hidden sticky top-0 z-10 bg-white border-b border-sage-200/50 px-6 py-4 flex items-center justify-between shadow-sm">
           <span className="font-serif font-semibold">Elo Terapêutico</span>
           <button onClick={handleLogout} className="p-2 text-terracotta-500"><LogOut size={20} /></button>
        </header>
        <div className="flex-1 overflow-auto bg-cream px-4 lg:px-10 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default DashboardLayout;
