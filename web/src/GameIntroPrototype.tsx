import { Activity, BookOpen, BrainCircuit, Dna, ExternalLink, FileDown, FolderOpen, Github, Network, Play, ShieldCheck, Sparkles, Users, X } from "lucide-react";
import { motion } from "framer-motion";
import { useState } from "react";

type Props = { onStart?: () => void; onContinue?: () => void };

const features = [
  { icon: Network, label: "Editor intuitivo", detail: "de heredogramas" },
  { icon: Dna, label: "Inferência", detail: "de padrões de herança" },
  { icon: Users, label: "Cálculo", detail: "de risco familiar" },
  { icon: FileDown, label: "Relatórios", detail: "clínicos personalizados" },
  { icon: BrainCircuit, label: "Integração", detail: "fenotípica e HPO" },
];

function HeryxMark() {
  return <span className="heryx-logo-mark" aria-hidden="true"><Dna /></span>;
}

function ClinicalPedigree() {
  return <motion.svg className="hero-pedigree" viewBox="0 0 650 520" role="img" aria-label="Heredograma clínico vetorial">
    <defs>
      <linearGradient id="nodePurple" x1="0" x2="1"><stop stopColor="#7256ea"/><stop offset="1" stopColor="#b98bff"/></linearGradient>
      <filter id="glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>
    <motion.g animate={{ y: [0,-7,0] }} transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}>
    <motion.g className="pedigree-lines" initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ duration: 1.5, ease: "easeInOut" }}>
      <path d="M150 95H430M290 95V210M95 210H555M95 210V365M290 210V365M555 210V365" />
    </motion.g>
    <motion.g className="pedigree-nodes" initial={{ opacity: 0, scale: .78 }} animate={{ opacity: 1, scale: [1,1.018,1] }} transition={{ opacity: { delay: .8, duration: .7 }, scale: { delay: 1.3, duration: 4.2, repeat: Infinity, ease: "easeInOut" } }}>
      <rect x="85" y="30" width="130" height="130" rx="4" />
      <circle cx="495" cy="95" r="65" className="half-node" />
      <path className="half-fill" d="M495 30a65 65 0 0 1 0 130z" />
      <rect x="35" y="305" width="120" height="120" rx="4" className="affected-node" />
      <circle cx="290" cy="365" r="60" />
      <rect x="495" y="305" width="120" height="120" rx="4" />
      <path className="deceased" d="M475 445L635 285" />
    </motion.g>
    </motion.g>
  </motion.svg>;
}

export function GameIntroPrototype({ onStart, onContinue }: Props = {}) {
  const [information, setInformation] = useState<"tutorial" | "literature" | null>(null);
  return <main className="heryx-landing">
    <div className="science-grid" aria-hidden="true" />
    <div className="science-orb science-orb--one" aria-hidden="true" />
    <div className="science-orb science-orb--two" aria-hidden="true" />

    <header className="heryx-header">
      <a className="heryx-logo" href="./" aria-label="Heryx — Hereditary Analytics">
        <HeryxMark/><span><strong>Heryx</strong><small>HEREDITARY ANALYTICS</small></span>
      </a>
      <nav aria-label="Navegação principal">
        <a className="active" href="#inicio">Início</a>
        <button type="button" onClick={() => setInformation("tutorial")}>Tutorial</button>
        <button type="button" onClick={() => setInformation("literature")}>Literatura</button>
      </nav>
      <div className="header-actions">
        <a className="header-cta" href="https://github.com/jv130397/Heryx" target="_blank" rel="noreferrer"><Github/>GitHub<ExternalLink/></a>
      </div>
    </header>

    <section className="heryx-hero" id="inicio">
      <motion.div className="hero-copy" initial={{ opacity: 0, x: -36 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: .7 }}>
        <div className="hero-eyebrow"><span>Análise de heredogramas</span><i/></div>
        <h1>Heredogramas para <em>Genética Clínica</em></h1>
        <p>Construa, analise e interprete heredogramas de forma rápida e profissional, com suporte à inferência de padrões de herança, risco familiar e documentação clínica.</p>
        <div className="hero-actions">
          <button className="primary-action" type="button" onClick={onStart}><Play/>Iniciar análise</button>
          {onContinue && <button className="secondary-action" type="button" onClick={onContinue}><FolderOpen/>Carregar projeto</button>}
        </div>
        <div className="trust-row"><span><ShieldCheck/>Dados locais</span><span><Activity/>Fluxo clínico</span><span><Sparkles/>Código aberto</span></div>
      </motion.div>

      <motion.div className="hero-science" initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: .8, delay: .15 }}>
        <div className="dna-helix" aria-hidden="true"><Dna/></div>
        <div className="pedigree-aura" aria-hidden="true" />
        <ClinicalPedigree/>
      </motion.div>
    </section>

    <div className="scientific-wave" aria-hidden="true"><i/><i/><i/></div>
    <section className="feature-strip" id="recursos" aria-label="Recursos da plataforma">
      {features.map(({icon:Icon,label,detail}, index)=><motion.article key={label} initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{delay:.55+index*.08}} whileHover={{y:-6,scale:1.025}}><span className="feature-icon"><Icon/></span><span><strong>{label}</strong><small>{detail}</small></span></motion.article>)}
    </section>

    {information && <motion.div className="heryx-info-backdrop" role="presentation" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} onMouseDown={(event) => event.target === event.currentTarget && setInformation(null)}>
      <motion.section className="heryx-info-panel" role="dialog" aria-modal="true" aria-label={information === "tutorial" ? "Tutorial de símbolos do heredograma" : "Literatura científica"} initial={{opacity:0,y:18,scale:.97}} animate={{opacity:1,y:0,scale:1}}>
        <header><span><HeryxMark/><small>HERYX · BASE DE CONHECIMENTO</small></span><button type="button" aria-label="Fechar" onClick={() => setInformation(null)}><X/></button></header>
        {information === "tutorial" ? <div className="tutorial-content">
          <span className="panel-kicker">Tutorial clínico</span><h2>Como ler um heredograma</h2><p>Os símbolos representam pessoas, vínculos e informações clínicas ao longo das gerações.</p>
          <div className="symbol-legend">
            <article><i className="legend-symbol square"/><span><strong>Quadrado</strong><small>Indivíduo masculino</small></span></article>
            <article><i className="legend-symbol circle"/><span><strong>Círculo</strong><small>Indivíduo feminino</small></span></article>
            <article><i className="legend-symbol diamond"/><span><strong>Losango</strong><small>Sexo não especificado</small></span></article>
            <article><i className="legend-symbol affected"/><span><strong>Preenchido</strong><small>Característica presente</small></span></article>
            <article><i className="legend-symbol proband">↗</i><span><strong>Seta</strong><small>Probando da família</small></span></article>
            <article><i className="legend-symbol deceased"/><span><strong>Linha diagonal</strong><small>Indivíduo falecido</small></span></article>
          </div>
        </div> : <div className="literature-content">
          <span className="panel-kicker">Literatura</span><h2>Referências que orientam o Heryx</h2><p>Fontes clínicas e terminológicas usadas como base para documentação, fenótipos e interpretação familiar.</p>
          <div className="reference-list">
            <a href="https://www.acmg.net/" target="_blank" rel="noreferrer"><BookOpen/><span><strong>ACMG</strong><small>Diretrizes de genética médica e genômica</small></span><ExternalLink/></a>
            <a href="https://hpo.jax.org/" target="_blank" rel="noreferrer"><BrainCircuit/><span><strong>Human Phenotype Ontology</strong><small>Terminologia padronizada de fenótipos</small></span><ExternalLink/></a>
            <a href="https://www.ncbi.nlm.nih.gov/books/NBK1116/" target="_blank" rel="noreferrer"><Dna/><span><strong>GeneReviews®</strong><small>Revisões clínicas de condições hereditárias</small></span><ExternalLink/></a>
          </div>
        </div>}
      </motion.section>
    </motion.div>}
  </main>;
}
