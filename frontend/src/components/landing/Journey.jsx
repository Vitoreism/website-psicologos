import { AnimatedSection } from './AnimatedSection';

export function Journey() {
  return (
    <section className="py-32 bg-white relative" id="journey">
      <div className="max-w-7xl mx-auto px-6 lg:px-16">
        <div className="flex flex-col lg:flex-row justify-between items-end mb-24 gap-8">
          <AnimatedSection className="max-w-2xl">
            <h3 className="font-serif text-4xl lg:text-5xl text-deep-moss mb-6 leading-tight">Facilitando o <span className="italic font-light">cuidado profundo</span></h3>
            <p className="text-sage-700 text-lg leading-relaxed">
              Desenvolvemos ferramentas que respeitam o ritmo da terapia. Menos cliques, mais presença.
            </p>
          </AnimatedSection>
        </div>
        <div className="grid md:grid-cols-3 gap-12 lg:gap-16">
          <AnimatedSection className="group">
            <div className="mb-8 relative inline-block">
              <div className="absolute inset-0 bg-sage-100 organic-shape group-hover:scale-110 transition-transform duration-500"></div>
              <div className="relative p-6 text-sage-600">
                <span className="material-symbols-outlined text-4xl">calendar_month</span>
              </div>
            </div>
            <h4 className="font-serif text-2xl mb-4 text-deep-moss group-hover:text-terracotta-500 transition-colors">Presença Consciente</h4>
            <p className="text-sage-600 leading-relaxed font-light">Uma agenda que entende seus intervalos e organiza seu tempo de forma acolhedora, reduzindo o ruído administrativo.</p>
          </AnimatedSection>
          
          <AnimatedSection delay={200} className="group md:mt-12">
            <div className="mb-8 relative inline-block">
              <div className="absolute inset-0 bg-terracotta-100 group-hover:scale-110 transition-transform duration-500" style={{ borderRadius: '40% 60% 30% 70% / 50% 40% 60% 50%' }}></div>
              <div className="relative p-6 text-terracotta-500">
                <span className="material-symbols-outlined text-4xl">favorite</span>
              </div>
            </div>
            <h4 className="font-serif text-2xl mb-4 text-deep-moss group-hover:text-terracotta-500 transition-colors">Escuta Protegida</h4>
            <p className="text-sage-600 leading-relaxed font-light">Prontuários que são extensões do seu cuidado. Segurança absoluta para que cada palavra e história fiquem em solo fértil.</p>
          </AnimatedSection>
          
          <AnimatedSection delay={400} className="group">
            <div className="mb-8 relative inline-block">
              <div className="absolute inset-0 bg-sage-100 group-hover:scale-110 transition-transform duration-500" style={{ borderRadius: '70% 30% 50% 50% / 30% 30% 70% 70%' }}></div>
              <div className="relative p-6 text-sage-600">
                <span className="material-symbols-outlined text-4xl">self_improvement</span>
              </div>
            </div>
            <h4 className="font-serif text-2xl mb-4 text-deep-moss group-hover:text-terracotta-500 transition-colors">Vínculos que Crescem</h4>
            <p className="text-sage-600 leading-relaxed font-light">Conecte-se com pessoas que buscam exatamente o seu olhar terapêutico. Uma vitrine de alma para sua prática profissional.</p>
          </AnimatedSection>
        </div>
      </div>
    </section>
  );
}

export default Journey;
