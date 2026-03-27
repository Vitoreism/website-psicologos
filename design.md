# Design System Oficial: Elo Terapêutico

Este documento serve como a **Bandeira de Design** para o "Elo Terapêutico". A aplicação gerada deve seguir estas diretrizes para manter consistência, acessibilidade e transmitir a sensação correta (acolhimento, seriedade e tranquilidade).

---

## 🎨 1. Personalidade & Moodboard
*   **Sensação Desejada:** Profissional, acolhedor, transparente, calmo e seguro.
*   **Inspiração:** Clínicas modernas, unindo tecnologia à empatia humana.
*   **Abordagem Visual:** Minimalista, com amplo uso de espaços em branco (Negative Space) para evitar sobrecarga cognitiva. Cantos arredondados para transmitir suavidade.

---

## 🖌️ 2. Paleta de Cores (Tailwind CSS)

A psicologia das cores aqui foca no azul e no verde-água (Teal), que transmitem calma, além de tons quentes suaves para chamadas à ação (CTAs).

*   **Cor Primária (Identidade & Trust):** Teal (Verde-água)
    *   Base: `bg-teal-600` (`#0d9488`) - Botões primários, ícones de destaque.
    *   Hover: `hover:bg-teal-700` (`#0f766e`)
    *   Light (Fundos suaves): `bg-teal-50` (`#f0fdfa`) - Excelente para backgrounds de cards de pacientes.
*   **Cor Secundária (Acolhimento & Destaque Alternativo):** Coral/Laranja Suave (Opcional, usado com parcimônia)
    *   Exemplo: `text-orange-600` ou botões secundários para agendamento.
*   **Cores Neutras (Textos & Backgrounds):** Slate (Cinza azulado)
    *   Background Principal da Página: `bg-slate-50` (`#f8fafc`) - Fundo off-white, mais confortável que o branco puro.
    *   Background de Cards/Painéis: `bg-white` (`#ffffff`) - Cria contraste limpo com o fundo Slate.
    *   Texto Principal (Títulos): `text-slate-900` (`#0f172a`)
    *   Texto Secundário (Parágrafos e Labels): `text-slate-500` (`#64748b`)
*   **Feedback & Estados (Essencial para UX de saúde):**
    *   Erro/Cancelar: `text-red-600` (`#dc2626`) / `bg-red-50`
    *   Sucesso (Consulta confirmada): `text-green-600` (`#16a34a`) / `bg-green-50`

---

## 🔤 3. Tipografia

Devemos utilizar fontes limpas (Sans-Serif), com excelente legibilidade tanto em dispositivos móveis quanto em Web.

*   **Fonte Principal:** **Inter** ou **Plus Jakarta Sans** (Se houver importação via Google Fonts).
*   **Hierarquia:**
    *   **H1 (Títulos de Página):** `text-3xl` ou `text-4xl`, fonte `font-bold`, cor `text-slate-900`, tracking levemente mais justo (`tracking-tight`).
    *   **H2/H3 (Subtítulos de Seções):** `text-xl` ou `text-2xl`, fonte `font-semibold`, `text-slate-800`.
    *   **Body (Texto Corrido/Bios):** `text-base` (16px), fonte `font-normal`, `text-slate-600`, entrelinha confortável (`leading-relaxed`).
    *   **Microcopy (Legendas, labels de form):** `text-sm`, fonte `font-medium`, `text-slate-500`.

---

## 📐 4. Layout & Espaçamento

O Tailwind será usado para criar layouts expansivos e focados e mobile-first.

*   **Container Principal:**
    *   No Portal do Psicólogo/Admin: Layout de **Dashboard Clássico** (Sidebar fixa à esquerda com largura `w-64`, Header no topo com `h-16`, e o conteúdo da página no restante).
    *   Na Área Pública/Paciente: Layout de **Landing Page** (Max-width centrado `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`).
*   **Grid e Gaps:** Utilizar o sistema de grids de 12 colunas ou Flexbox, mantendo respiros generosos (`gap-6` ou `gap-8` entre seções).

---

## 🧩 5. Componentização Base da UI (Shadcn/UI Vibe)

Se gerar com base em componentes (como Shadcn UI), as propriedades primordiais são:

1.  **Cards:**  
    *   Características: `bg-white rounded-xl shadow-sm border border-slate-100 p-6`.
    *   *Uso:* Listagem de psicólogos, Resumo de faturamento, Detalhes da próxima consulta.
2.  **Botões:**
    *   *Primário:* `bg-teal-600 text-white rounded-lg px-4 py-2 font-medium hover:bg-teal-700 transition-colors`.
    *   *Secundário/Outline:* `border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 rounded-lg px-4 py-2 font-medium transition-colors`.
3.  **Formulários (Inputs & Selects):**
    *   Clean: Borda cinza clara (`border-slate-300`), fundo branco (`bg-white`), cantos arredondados (`rounded-lg`).
    *   Focus State (Crítico para acessibilidade): Ao clicar, a borda vira primária e ganha um ring suave (`focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 outline-none`).
4.  **Tabelas e Listas de Dados:**
    *   Cabeçalhos discretos: Fundo de tabela cinza claríssimo (`bg-slate-50`), linha de borda inferior em cada item (`border-b border-slate-200`).
5.  **Alertas / Toast Notifications:**
    *   Erros de API (ex: Status 409 Email em uso): Card flutuante com borda esquerda vermelha grossa, fundo quase branco.
    *   Sucesso de Cadastro (ex: Status 201): Card flutuante verde suave.

---

## 📌 6. Regras de Ouro Geradas para a IA

Ao alimentar o **Stich** ou cursor com esse arquivo, instrua explicitamente o seguinte:
*   *"Sempre obedeça à paleta especificada neste design.md."*
*   *"Faça todos os formulários implementarem o 'Focus Ring' da cor Teal."*
*   *"Nas listagens (seja pacientes ou psicólogos), sempre exiba dados em Cards `rounded-xl`."*
*   *"As páginas de Login e Cadastro devem ter um layout com tela dividida (50% formulário limpo, 50% imagem inspiracional ou padrão geométrico de tom Teal), para passar credibilidade imediata."*
