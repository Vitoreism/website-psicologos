import { AnimatedSection } from './AnimatedSection';

export function Presence() {
  return (
    <section className="py-32 bg-cream overflow-hidden" id="presence">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="bg-sage-600 rounded-[3rem] p-8 lg:p-20 overflow-hidden relative shadow-3xl">
          <div className="absolute top-0 right-0 w-1/2 h-full opacity-10 pointer-events-none">
            <svg className="w-full h-full scale-150" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
              <path d="M150,200 C150,100 250,100 250,200 C250,300 150,300 150,200" fill="none" stroke="white" strokeWidth="0.5"></path>
            </svg>
          </div>
          <div className="grid lg:grid-cols-2 gap-20 items-center relative z-10">
            <AnimatedSection>
              <h2 className="font-serif text-4xl lg:text-5xl text-white mb-8 leading-tight">Sua prática merece essa <span className="italic opacity-80">leveza</span>.</h2>
              <p className="text-sage-50 text-lg font-light leading-relaxed mb-10 opacity-90">
                Junte-se a uma comunidade de terapeutas que escolheram o equilíbrio. Experimente o Elo Terapêutico gratuitamente por 14 dias.
              </p>
              <div className="grid grid-cols-2 gap-8 mb-10 border-t border-white/20 pt-10">
                <div>
                  <div className="text-white text-3xl font-serif mb-1">500+</div>
                  <div className="text-sage-100 text-xs uppercase tracking-widest font-bold">Psicólogos</div>
                </div>
                <div>
                  <div className="text-white text-3xl font-serif mb-1">98%</div>
                  <div className="text-sage-100 text-xs uppercase tracking-widest font-bold">Satisfação</div>
                </div>
              </div>
            </AnimatedSection>
            <AnimatedSection delay={300} className="bg-white/95 backdrop-blur-xl rounded-[2rem] p-8 lg:p-12 shadow-2xl">
              <form className="space-y-6">
                <div className="grid grid-cols-2 gap-5">
                  <div className="space-y-2">
                    <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">Nome Completo</label>
                    <input className="w-full bg-sage-50 border-none rounded-2xl h-14 px-5 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss placeholder:text-sage-600/30" placeholder="Como te chamamos?" type="text"/>
                  </div>
                  <div className="space-y-2">
                    <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">CRP</label>
                    <input className="w-full bg-sage-50 border-none rounded-2xl h-14 px-5 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss placeholder:text-sage-600/30" placeholder="00/0000" type="text"/>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-deep-moss text-xs font-bold uppercase tracking-wider ml-1">E-mail Profissional</label>
                  <input className="w-full bg-sage-50 border-none rounded-2xl h-14 px-5 focus:ring-2 focus:ring-terracotta-500 transition-all text-deep-moss placeholder:text-sage-600/30" placeholder="seuemail@exemplo.com" type="email"/>
                </div>
                <button className="w-full bg-terracotta-500 text-white rounded-2xl h-16 text-lg font-bold shadow-lg shadow-terracotta-500/30 hover:bg-terracotta-600 transition-all flex items-center justify-center gap-3 transform hover:-translate-y-1 active:scale-95" type="submit">
                  Criar meu Espaço
                  <span className="material-symbols-outlined">arrow_forward</span>
                </button>
                <p className="text-sage-600/70 text-[10px] text-center uppercase tracking-widest leading-relaxed">Sua privacidade e sigilo são nossa prioridade máxima.</p>
              </form>
            </AnimatedSection>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Presence;
