import { AnimatePresence, motion } from "framer-motion";
import { FolderOpen, Moon, Plus, Sun } from "lucide-react";
import { lazy, Suspense, useEffect, useState } from "react";

const PedigreeScene = lazy(() =>
  import("./PedigreeScene").then((module) => ({ default: module.PedigreeScene }))
);

const copy = {
  pt: {
    nav: ["Editor", "Recursos", "Documentação"],
    eyebrow: "VISUALIZAÇÃO CLÍNICA · HEREDOGRAMAS",
    title: "Genética clínica em perspectiva.",
    description: "Construa, explore e documente relações familiares com precisão.",
    create: "Nova família",
    open: "Abrir projeto",
    recent: "Projetos recentes",
    edited: "editado",
    projects: ["Família Silva", "Coorte Raras", "Estudo Familiar A"]
  },
  en: {
    nav: ["Editor", "Resources", "Documentation"],
    eyebrow: "CLINICAL VISUALIZATION · PEDIGREES",
    title: "Clinical genetics in perspective.",
    description: "Build, explore, and document family relationships with precision.",
    create: "New family",
    open: "Open project",
    recent: "Recent projects",
    edited: "edited",
    projects: ["Silva Family", "Rare Cohort", "Family Study A"]
  }
};

function BrandMark() {
  return (
    <span className="brand-mark" aria-hidden="true">
      <span />
    </span>
  );
}

export function App() {
  const [language, setLanguage] = useState<keyof typeof copy>("pt");
  const [light, setLight] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const text = copy[language];

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  return (
    <main className={light ? "app light" : "app"}>
      <header className="topbar">
        <a className="brand" href="#" aria-label="RarePedigree Studio">
          <BrandMark />
          <strong>RarePedigree Studio</strong>
        </a>
        <nav aria-label="Navegação principal">
          {text.nav.map((item, index) => (
            <a className={index === 0 ? "active" : ""} href={`#${item}`} key={item}>
              {item}
            </a>
          ))}
        </nav>
        <div className="utilities">
          <button
            className="language"
            onClick={() => setLanguage(language === "pt" ? "en" : "pt")}
            aria-label="Alternar idioma"
          >
            {language.toUpperCase()}
          </button>
          <button onClick={() => setLight(!light)} aria-label="Alternar aparência">
            {light ? <Moon size={18} /> : <Sun size={18} />}
          </button>
        </div>
      </header>

      <section className="hero">
        <div className="visual-stage">
          <Suspense fallback={<div className="scene-fallback">Preparando visualização…</div>}>
            <PedigreeScene reducedMotion={reducedMotion} />
          </Suspense>
          <div className="generation-key" aria-hidden="true">
            <span>I</span><span>II</span><span>III</span>
          </div>
          <div className="scene-caption">
            <span className="status-dot" />
            Cena clínica interativa · arraste o cursor para explorar
          </div>
        </div>

        <motion.div
          className="content"
          initial={reducedMotion ? false : { opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.2, 0.7, 0.2, 1] }}
        >
          <span className="eyebrow">{text.eyebrow}</span>
          <AnimatePresence mode="wait">
            <motion.div
              key={language}
              initial={reducedMotion ? false : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.25 }}
            >
              <h1>{text.title}</h1>
              <p className="description">{text.description}</p>
            </motion.div>
          </AnimatePresence>
          <div className="actions">
            <button className="primary"><Plus size={20} />{text.create}</button>
            <button className="secondary"><FolderOpen size={19} />{text.open}</button>
          </div>

          <section className="recent" aria-labelledby="recent-title">
            <div className="section-heading">
              <h2 id="recent-title">{text.recent}</h2>
              <span />
            </div>
            <ul>
              {text.projects.map((project, index) => (
                <li key={project}>
                  <button>
                    <FolderOpen size={16} />
                    <span>{project}</span>
                    <small>{text.edited} {index === 0 ? "há 2 h" : `há ${index} dia${index > 1 ? "s" : ""}`}</small>
                  </button>
                </li>
              ))}
            </ul>
          </section>
        </motion.div>
      </section>
    </main>
  );
}
