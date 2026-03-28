import { AnimatedSection } from './AnimatedSection';

export function Hero() {
  return (
    <section className="relative min-h-[921px] flex items-center overflow-hidden pt-12 pb-24 lg:pb-0" id="essence">
      <div className="blob-bg w-96 h-96 bg-sage-200 top-0 -left-20"></div>
      <div className="blob-bg w-[500px] h-[500px] bg-terracotta-200 bottom-0 -right-20"></div>
      <div className="max-w-7xl mx-auto px-6 lg:px-16 grid lg:grid-cols-2 gap-12 items-center">
        
        <AnimatedSection className="flex flex-col gap-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-sage-100 text-sage-700 text-xs font-semibold uppercase tracking-widest">
            <span className="w-1.5 h-1.5 rounded-full bg-sage-600 animate-pulse"></span>
            Um espaço para florescer
          </div>
          <h2 className="font-serif text-5xl lg:text-7xl leading-[1.05] text-deep-moss font-medium">
            Onde o cuidado <br/><span className="italic text-terracotta-500">encontra</span> a fluidez.
          </h2>
          <p className="text-sage-700 text-lg lg:text-xl leading-relaxed max-w-lg font-light">
            Libere-se das complexidades administrativas para se dedicar ao que é essencial: a conexão humana e o processo de cura dos seus pacientes.
          </p>
          <div className="flex flex-col sm:flex-row gap-5">
            <button className="bg-terracotta-500 text-white rounded-full px-10 py-5 text-lg font-semibold shadow-xl shadow-terracotta-500/20 hover:bg-terracotta-600 transition-all hover:-translate-y-1">
              Começar sua jornada
            </button>
            <button className="flex items-center justify-center gap-3 text-sage-700 rounded-full px-8 py-5 text-lg font-medium hover:bg-sage-100/50 transition-all border border-sage-200/50">
              <span className="material-symbols-outlined text-2xl">eco</span>
              Conheça o Elo
            </button>
          </div>
        </AnimatedSection>
        
        <AnimatedSection delay={300} className="relative">
          <div className="organic-shape overflow-hidden shadow-2xl shadow-sage-600/10 bg-sage-100 aspect-square lg:aspect-[5/6] transform hover:rotate-1 transition-transform duration-700">
            <img alt="Atmosphere of peace" className="w-full h-full object-cover mix-blend-multiply opacity-90" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAv_-q41oJJ_2SenJX1GDXCDt-G1eevHjf2_nN1OAQ1Futc0qux-4HNWdjkNJsIGQQCylluFfR5Yog11dmTkr03dvCzfR_RUMursm7G54NdZppQbUMv2PK3GlNLhIYLKpwwx-YD_Hm3YJfWvT3YuKPc4tBM0QKnn6OX3Oz4wyp_x4tA56RJ_Yc6l3Gg5vKtws7O4Me7vI8Xjpxs_4HNuo06k-7CKnF7z_UyOyPCbYA0iZlsTKZ9Oic-rakNYh_ptJ2Weg0TggQjEFg" />
          </div>
          <div className="absolute -bottom-6 -left-6 lg:-left-12 p-8 bg-white/90 backdrop-blur-md rounded-2xl shadow-xl max-w-xs border border-sage-100 animate-[float_6s_ease-in-out_infinite]">
            <p className="font-serif text-terracotta-500 text-lg italic mb-3">"Encontrei a leveza necessária para estar inteira em cada sessão."</p>
            <div className="flex items-center gap-3">
              <div className="w-8 h-px bg-sage-200"></div>
              <span className="text-sage-600 text-xs font-bold uppercase tracking-tighter">Dra. Helena Souza</span>
            </div>
          </div>
        </AnimatedSection>
        
      </div>
    </section>
  );
}

export default Hero;
