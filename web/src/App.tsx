import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, FolderOpen, Github, Moon, Play, Sun } from "lucide-react";
import { lazy, Suspense, useEffect, useState } from "react";

const PedigreeScene = lazy(() => import("./PedigreeScene").then((module) => ({ default: module.PedigreeScene })));
const repositoryUrl = "https://github.com/jv130397/RarePedigree-Studio";

const copy = {
  pt: { nav: ["O projeto", "Ciência", "Documentação"], chapter: "CAPÍTULO 01 · O OBSERVATÓRIO", title: "Toda família guarda uma história.", description: "Entre no laboratório de João Vitor e transforme vínculos, fenótipos e gerações em conhecimento clínico.", enter: "Entrar no laboratório", open: "Continuar projeto", github: "Ver no GitHub", guide: "JOÃO VITOR · GUIA DO OBSERVATÓRIO", hint: "Mova o cursor para explorar o ambiente", status: "SISTEMA ONLINE", mission: "MISSÃO ATUAL", missionText: "Criar um novo heredograma" },
  en: { nav: ["The project", "Science", "Documentation"], chapter: "CHAPTER 01 · THE OBSERVATORY", title: "Every family holds a story.", description: "Enter João Vitor's laboratory and turn relationships, phenotypes and generations into clinical knowledge.", enter: "Enter the laboratory", open: "Continue project", github: "View on GitHub", guide: "JOÃO VITOR · OBSERVATORY GUIDE", hint: "Move the cursor to explore the environment", status: "SYSTEM ONLINE", mission: "CURRENT MISSION", missionText: "Create a new pedigree" }
};

function BrandMark() { return <span className="brand-mark" aria-hidden="true"><span /></span>; }

export function App() {
  const [language, setLanguage] = useState<keyof typeof copy>("pt");
  const [light, setLight] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [entered, setEntered] = useState(false);
  const text = copy[language];

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(media.matches);
    update(); media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  return <main className={`${light ? "app light" : "app"}${entered ? " entered" : ""}`}>
    <header className="topbar">
      <a className="brand" href="#inicio" aria-label="RarePedigree Studio"><BrandMark /><span><strong>RarePedigree</strong><small>STUDIO</small></span></a>
      <nav aria-label="Navegação principal">{text.nav.map((item, index) => <a className={index === 0 ? "active" : ""} href={`#section-${index}`} key={item}>{item}</a>)}</nav>
      <div className="utilities"><a className="github-compact" href={repositoryUrl} target="_blank" rel="noreferrer" aria-label={text.github}><Github size={17} /><span>GitHub</span></a><button className="language" onClick={() => setLanguage(language === "pt" ? "en" : "pt")} aria-label="Alternar idioma">{language.toUpperCase()}</button><button onClick={() => setLight(!light)} aria-label="Alternar aparência">{light ? <Moon size={17} /> : <Sun size={17} />}</button></div>
    </header>

    <section className="hero" id="inicio">
      <div className="visual-stage"><Suspense fallback={<div className="scene-fallback">Carregando observatório…</div>}><PedigreeScene reducedMotion={reducedMotion} entered={entered} /></Suspense></div>
      <div className="screen-vignette" aria-hidden="true" /><div className="hud-corners" aria-hidden="true"><i /><i /><i /><i /></div>
      <motion.div className="system-status" initial={reducedMotion ? false : { opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1 }}><span className="status-dot" />{text.status}<b>RP–01</b></motion.div>
      <motion.div className="guide-tag" initial={reducedMotion ? false : { opacity: 0, x: -18 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: .9, duration: .7 }}><span>JV</span><div><small>{text.guide}</small><strong>Genética · Família · Descoberta</strong></div></motion.div>
      <motion.div className="content" initial={reducedMotion ? false : { opacity: 0, y: 26 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .9, delay: .2, ease: [0.2, 0.7, 0.2, 1] }}>
        <span className="eyebrow"><i />{text.chapter}</span>
        <AnimatePresence mode="wait"><motion.div key={language} initial={reducedMotion ? false : { opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: .25 }}><h1>{text.title}</h1><p className="description">{text.description}</p></motion.div></AnimatePresence>
        <div className="actions"><button className="primary" onClick={() => setEntered(true)}><Play size={17} fill="currentColor" />{text.enter}<ArrowRight size={17} /></button><button className="secondary"><FolderOpen size={18} />{text.open}</button></div>
        <a className="github-link" href={repositoryUrl} target="_blank" rel="noreferrer"><Github size={16} />{text.github}<span>↗</span></a>
      </motion.div>
      <div className="mission-card"><span>01</span><div><small>{text.mission}</small><strong>{text.missionText}</strong></div><i /></div><div className="explore-hint"><span className="mouse-icon" />{text.hint}</div>
    </section>
  </main>;
}
