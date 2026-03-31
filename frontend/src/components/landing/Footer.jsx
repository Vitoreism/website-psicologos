export function Footer() {
  return (
    <footer className="bg-white border-t border-sage-100 pt-24 pb-12">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="grid md:grid-cols-4 gap-16 mb-20">
          <div className="col-span-2">
            <div className="flex items-center gap-3 mb-8">
              <div className="size-8 text-sage-600">
                <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                  <path d="M24 4C22 18 6 22 4 24C6 26 22 30 24 44C26 30 42 26 44 24C42 22 26 18 24 4Z" fill="currentColor"></path>
                </svg>
              </div>
              <h2 className="font-serif text-xl font-semibold text-deep-moss">Elo Terapêutico</h2>
            </div>
            <p className="text-sage-600 text-lg max-w-sm font-light leading-relaxed">
              Nutrindo a relação entre terapeuta e tecnologia através de uma experiência humanizada e segura.
            </p>
          </div>
          <div>
            <h5 className="text-deep-moss font-bold text-xs uppercase tracking-[0.2em] mb-8">Navegação</h5>
            <ul className="space-y-4 text-sage-600 text-sm font-medium">
              <li><a className="hover:text-terracotta-500 transition-colors" href="#">Sobre Nós</a></li>
              <li><a className="hover:text-terracotta-500 transition-colors" href="#">Manifesto</a></li>
              <li><a className="hover:text-terracotta-500 transition-colors" href="#">Segurança</a></li>
            </ul>
          </div>
          <div>
            <h5 className="text-deep-moss font-bold text-xs uppercase tracking-[0.2em] mb-8">Suporte</h5>
            <ul className="space-y-4 text-sage-600 text-sm font-medium">
              <li><a className="hover:text-terracotta-500 transition-colors" href="#">Central de Ajuda</a></li>
              <li><a className="hover:text-terracotta-500 transition-colors" href="#">Privacidade</a></li>
              <li><a className="hover:text-terracotta-500 transition-colors" href="#">Termos</a></li>
            </ul>
          </div>
        </div>
        <div className="flex flex-col md:flex-row justify-between items-center pt-10 border-t border-sage-50 gap-6">
          <p className="text-sage-400 text-xs tracking-wide">© 2026 Elo Terapêutico. Cultivando conexões humanas, de humanos para humanos.</p>
          <div className="flex gap-8">
            <a className="text-sage-400 hover:text-sage-600 transition-colors" href="#">
              <span className="material-symbols-outlined text-xl">spa</span>
            </a>
            <a className="text-sage-400 hover:text-sage-600 transition-colors" href="#">
              <span className="material-symbols-outlined text-xl">psychology</span>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
