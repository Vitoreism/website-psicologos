export function Header() {
  return (
    <header className="sticky top-0 z-50 glass-nav border-b border-sage-200/30 px-6 lg:px-16 py-5 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="size-9 text-sage-600">
          <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
            <path d="M24 4C22 18 6 22 4 24C6 26 22 30 24 44C26 30 42 26 44 24C42 22 26 18 24 4Z" fill="currentColor" opacity="0.8"></path>
            <circle cx="24" cy="24" fill="currentColor" opacity="0.4" r="6"></circle>
          </svg>
        </div>
        <h1 className="font-serif text-2xl font-semibold tracking-tight text-deep-moss">Elo Terapêutico</h1>
      </div>
      <nav className="hidden lg:flex items-center gap-10">
        <a className="text-sage-700/80 text-sm font-medium hover:text-sage-600 transition-colors" href="#essence">Essência</a>
        <a className="text-sage-700/80 text-sm font-medium hover:text-sage-600 transition-colors" href="#journey">Jornada</a>
        <a className="text-sage-700/80 text-sm font-medium hover:text-sage-600 transition-colors" href="#presence">Presença</a>
      </nav>
      <button className="bg-sage-600 text-white rounded-full px-8 py-3 text-sm font-semibold hover:bg-sage-700 transition-all hover:shadow-lg hover:shadow-sage-600/20 active:scale-95">
        Área do Profissional
      </button>
    </header>
  );
}

export default Header;
