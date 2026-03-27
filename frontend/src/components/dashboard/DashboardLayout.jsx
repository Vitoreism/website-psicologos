import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { Home, Calendar, Users, User, LogOut } from 'lucide-react';

export function DashboardLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // #TODO: Desconectar o usuario na API real
    navigate('/');
  };

  const navItems = [
    { name: 'Resumo', path: '/dashboard', icon: Home, end: true },
    { name: 'Agenda', path: '/dashboard/agenda', icon: Calendar },
    { name: 'Pacientes', path: '/dashboard/pacientes', icon: Users },
    { name: 'Meu Perfil', path: '/dashboard/perfil', icon: User },
  ];

  return (
    <div className="h-screen bg-sage-50 font-sans text-deep-moss flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-sage-200/50 flex-col hidden lg:flex">
        <div className="p-6 border-b border-sage-100 flex items-center gap-3">
          <div className="size-8 text-sage-600">
            <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
              <path d="M24 4C22 18 6 22 4 24C6 26 22 30 24 44C26 30 42 26 44 24C42 22 26 18 24 4Z" fill="currentColor" opacity="0.8"></path>
              <circle cx="24" cy="24" fill="currentColor" opacity="0.4" r="6"></circle>
            </svg>
          </div>
          <h1 className="font-serif text-xl font-semibold tracking-tight">Elo Terapêutico</h1>
        </div>
        
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-sage-100 text-deep-moss shadow-sm'
                    : 'text-sage-600 hover:bg-sage-50 hover:text-deep-moss'
                }`
              }
            >
              <item.icon size={20} className="shrink-0" />
              {item.name}
            </NavLink>
          ))}
        </nav>
        
        <div className="p-4 border-t border-sage-100">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-medium text-terracotta-500 hover:bg-terracotta-50 transition-colors"
          >
            <LogOut size={20} />
            Sair
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
