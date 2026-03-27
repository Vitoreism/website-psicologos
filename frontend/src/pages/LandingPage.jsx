import { Header } from '../components/landing/Header';
import { Hero } from '../components/landing/Hero';
import { Journey } from '../components/landing/Journey';
import { Presence } from '../components/landing/Presence';
import { Footer } from '../components/landing/Footer';

export function LandingPage() {
  return (
    <div className="bg-cream font-sans text-deep-moss">
      <Header />
      <main>
        <Hero />
        <Journey />
        <Presence />
      </main>
      <Footer />
    </div>
  );
}

export default LandingPage;
