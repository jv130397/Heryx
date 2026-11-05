import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, ArrowRight, FileJson, FolderOpen, Github, Maximize2, Minus, Moon, Play, Plus, Redo2, Save, Sun, Undo2, Upload, X } from "lucide-react";
import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { WebPedigree, type WebProject } from "./WebPedigree";
import { NewProjectMission } from "./NewProjectMission";
import { IndividualDrawer } from "./IndividualDrawer";
import { applyFamilyAction, type FamilyAction } from "./familyOperations";
import { prepareProjectDownload } from "./projectIO";

const PedigreeScene = lazy(() => import("./PedigreeScene").then((module) => ({ default: module.PedigreeScene })));
const repositoryUrl = "https://github.com/jv130397/RarePedigree-Studio";
type AvatarPose = "neutral" | "pointing" | "laptop" | "thinking" | "celebrating";
type ProjectSummary = { fileName: string; title: string; schema: string; individuals: number; relationships: number; updatedAt?: string };
const readLocalFile = (file: File) => new Promise<string>((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(String(reader.result)); reader.onerror = () => reject(reader.error); reader.readAsText(file); });

const copy = {
  pt: { nav: ["O projeto", "Ciência", "Documentação"], chapter: "CAPÍTULO 01 · O OBSERVATÓRIO", title: "Toda família guarda uma história.", description: "Entre no laboratório de João Vitor e transforme vínculos, fenótipos e gerações em conhecimento clínico.", enter: "Entrar no laboratório", open: "Continuar projeto", github: "Ver no GitHub", guide: "JOÃO VITOR · GUIA DO OBSERVATÓRIO", hint: "Mova o cursor para explorar o ambiente", status: "SISTEMA ONLINE", mission: "MISSÃO ATUAL", missionText: "Criar um novo heredograma", skip: "Pular introdução", sequence: ["INICIALIZANDO OBSERVATÓRIO", "JOÃO VITOR CONECTADO", "RECONSTRUINDO HISTÓRIA FAMILIAR", "ACESSO LIBERADO"], workspace: "Editor de heredograma", back: "Voltar ao observatório", add: "Adicionar indivíduo", relationship: "Relacionamento", inspector: "Inspetor", archive: "Arquivo de famílias", chooseFile: "Selecionar projeto local", localOnly: "O arquivo permanece neste dispositivo.", invalidFile: "Este arquivo não parece ser um projeto RarePedigree válido.", reactions: { neutral: "Genética · Família · Descoberta", pointing: "Vamos construir uma história familiar?", laptop: "Pronto para retomar seu projeto.", thinking: "Código aberto, ciência compartilhada.", celebrating: "Acesso ao laboratório autorizado!" } },
  en: { nav: ["The project", "Science", "Documentation"], chapter: "CHAPTER 01 · THE OBSERVATORY", title: "Every family holds a story.", description: "Enter João Vitor's laboratory and turn relationships, phenotypes and generations into clinical knowledge.", enter: "Enter the laboratory", open: "Continue project", github: "View on GitHub", guide: "JOÃO VITOR · OBSERVATORY GUIDE", hint: "Move the cursor to explore the environment", status: "SYSTEM ONLINE", mission: "CURRENT MISSION", missionText: "Create a new pedigree", skip: "Skip intro", sequence: ["INITIALIZING OBSERVATORY", "JOÃO VITOR CONNECTED", "REBUILDING FAMILY HISTORY", "ACCESS GRANTED"], workspace: "Pedigree editor", back: "Back to observatory", add: "Add individual", relationship: "Relationship", inspector: "Inspector", archive: "Family archive", chooseFile: "Select local project", localOnly: "The file remains on this device.", invalidFile: "This file does not appear to be a valid RarePedigree project.", reactions: { neutral: "Genetics · Family · Discovery", pointing: "Shall we build a family story?", laptop: "Ready to resume your project.", thinking: "Open code, shared science.", celebrating: "Laboratory access authorized!" } }
};

function BrandMark() { return <span className="brand-mark" aria-hidden="true"><span /></span>; }

export function App() {
  const [language, setLanguage] = useState<keyof typeof copy>("pt");
  const [light, setLight] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [entered, setEntered] = useState(false);
  const [introPhase, setIntroPhase] = useState(0);
  const [workspaceOpen, setWorkspaceOpen] = useState(false);
  const [avatarPose, setAvatarPose] = useState<AvatarPose>("neutral");
  const [archiveOpen, setArchiveOpen] = useState(false);
  const [newProjectOpen, setNewProjectOpen] = useState(false);
  const [projectSummary, setProjectSummary] = useState<ProjectSummary | null>(null);
  const [loadedProject, setLoadedProject] = useState<WebProject | null>(null);
  const [selectedIndividualId, setSelectedIndividualId] = useState<string | null>(null);
  const [undoStack, setUndoStack] = useState<WebProject[]>([]);
  const [redoStack, setRedoStack] = useState<WebProject[]>([]);
  const [saveState, setSaveState] = useState<"modified" | "saved">("modified");
  const [zoom, setZoom] = useState(100);
  const [newlyAddedIds, setNewlyAddedIds] = useState<string[]>([]);
  const [editorNotice, setEditorNotice] = useState("");
  const [fileError, setFileError] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const text = copy[language];

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(media.matches);
    update(); media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    if (reducedMotion) { setIntroPhase(3); return; }
    const timers = [window.setTimeout(() => setIntroPhase(1), 900), window.setTimeout(() => setIntroPhase(2), 2300), window.setTimeout(() => setIntroPhase(3), 4400)];
    return () => timers.forEach(window.clearTimeout);
  }, [reducedMotion]);

  useEffect(() => {
    if (!entered) return;
    const timer = window.setTimeout(() => setWorkspaceOpen(true), reducedMotion ? 50 : 1450);
    return () => window.clearTimeout(timer);
  }, [entered, reducedMotion]);

  useEffect(() => {
    if (!workspaceOpen) return;
    const handleKeyboard = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const editing = target instanceof Element && target.matches("input,select,textarea,[contenteditable='true']");
      if (event.key === "Escape" && selectedIndividualId) { setSelectedIndividualId(null); return; }
      if (editing || !(event.ctrlKey || event.metaKey)) return;
      if (event.key === "+" || event.key === "=") { event.preventDefault(); setZoom(value=>Math.min(200,value+10)); }
      if (event.key === "-") { event.preventDefault(); setZoom(value=>Math.max(50,value-10)); }
      if (event.key === "0") { event.preventDefault(); setZoom(100); }
    };
    window.addEventListener("keydown",handleKeyboard);
    return () => window.removeEventListener("keydown",handleKeyboard);
  }, [workspaceOpen,selectedIndividualId]);

  useEffect(() => { if (!editorNotice) return; const timer = window.setTimeout(()=>setEditorNotice(""),2600); return () => window.clearTimeout(timer); }, [editorNotice]);

  const leaveWorkspace = () => { setWorkspaceOpen(false); setEntered(false); setSelectedIndividualId(null); setNewlyAddedIds([]); setEditorNotice(""); setZoom(100); setAvatarPose("neutral"); };
  const beginNewProject = () => { setAvatarPose("pointing"); setNewProjectOpen(true); };
  const createProject = (project: WebProject) => { setLoadedProject(project); setProjectSummary(null); setSelectedIndividualId(null); setUndoStack([]); setRedoStack([]); setSaveState("modified"); setNewProjectOpen(false); setAvatarPose("celebrating"); setEntered(true); };
  const selectedIndividual = loadedProject?.individuals.find(person => person.id === selectedIndividualId) ?? null;
  const selectedPartners = selectedIndividualId && loadedProject ? (loadedProject.relationships ?? []).filter(edge=>edge.member_a===selectedIndividualId||edge.member_b===selectedIndividualId).map(edge=>edge.member_a===selectedIndividualId?edge.member_b:edge.member_a).map(id=>loadedProject.individuals.find(person=>person.id===id)).filter((person): person is WebProject["individuals"][number]=>Boolean(person)) : [];
  const reservedLabels = loadedProject?.individuals.filter(person=>person.id!==selectedIndividualId).map(person=>person.label ?? "") ?? [];
  const commitProject = (next: WebProject) => { if (loadedProject) setUndoStack(stack => [...stack, loadedProject]); setRedoStack([]); setLoadedProject({ ...next, updated_at: new Date().toISOString() }); setSaveState("modified"); };
  const saveIndividual = (person: WebProject["individuals"][number]) => { if (loadedProject) commitProject({ ...loadedProject, individuals: loadedProject.individuals.map(current => current.id === person.id ? person : person.proband && current.proband ? {...current,proband:false} : current) }); setEditorNotice("Informações do indivíduo atualizadas."); setSelectedIndividualId(null); };
  const addRelative = (action: FamilyAction, partnerId?: string) => { if (!loadedProject || !selectedIndividualId) return; const result = applyFamilyAction(loadedProject, selectedIndividualId, action, undefined, partnerId); if (result.blockedReason) { setEditorNotice("Selecione o outro genitor antes de adicionar o filho."); return; } const existingIds = new Set(loadedProject.individuals.map(person => person.id)); const createdIds = result.project.individuals.filter(person => !existingIds.has(person.id)).map(person => person.id); if (!createdIds.length) { setEditorNotice("Este vínculo familiar já está registrado."); return; } commitProject(result.project); setNewlyAddedIds(createdIds); setSelectedIndividualId(result.createdId); setEditorNotice(`${createdIds.length>1?"Núcleo familiar criado":"Familiar adicionado"} com sucesso.`); window.setTimeout(() => setNewlyAddedIds(current => current.some(id => createdIds.includes(id)) ? [] : current), 1050); };
  const undo = () => { const previous = undoStack.at(-1); if (!previous || !loadedProject) return; setUndoStack(stack => stack.slice(0,-1)); setRedoStack(stack => [...stack,loadedProject]); setLoadedProject(previous); setSelectedIndividualId(null); setNewlyAddedIds([]); setSaveState("modified"); };
  const redo = () => { const next = redoStack.at(-1); if (!next || !loadedProject) return; setRedoStack(stack => stack.slice(0,-1)); setUndoStack(stack => [...stack,loadedProject]); setLoadedProject(next); setSelectedIndividualId(null); setNewlyAddedIds([]); setSaveState("modified"); };
  const saveProject = () => { if (!loadedProject) return; const prepared = prepareProjectDownload(loadedProject); const url = URL.createObjectURL(new Blob([prepared.content],{type:"application/json"})); const anchor = document.createElement("a"); anchor.href=url; anchor.download=prepared.filename; anchor.click(); URL.revokeObjectURL(url); setLoadedProject(prepared.project); setSaveState("saved"); };
  const inspectProject = async (file?: File) => {
    if (!file) return;
    try {
      const data = JSON.parse(await readLocalFile(file)) as Record<string, unknown>;
      if (typeof data.schema_version !== "string" || !Array.isArray(data.individuals)) throw new Error("invalid");
      setProjectSummary({ fileName: file.name, title: typeof data.title === "string" ? data.title : file.name, schema: data.schema_version, individuals: data.individuals.length, relationships: Array.isArray(data.relationships) ? data.relationships.length : 0, updatedAt: typeof data.updated_at === "string" ? data.updated_at : undefined });
      setFileError(false);
      setLoadedProject(data as unknown as WebProject);
    } catch { setProjectSummary(null); setLoadedProject(null); setFileError(true); }
  };
  const openLoadedProject = () => { if (!loadedProject) return; setUndoStack([]); setRedoStack([]); setSaveState("saved"); setArchiveOpen(false); setAvatarPose("celebrating"); setEntered(true); };

  const ready = introPhase === 3;
  return <main className={`${light ? "app light" : "app"}${entered ? " entered" : ""}${ready ? " intro-ready" : " intro-running"}`}>
    <header className="topbar">
      <a className="brand" href="#inicio" aria-label="RarePedigree Studio"><BrandMark /><span><strong>RarePedigree</strong><small>STUDIO</small></span></a>
      <nav aria-label="Navegação principal">{text.nav.map((item, index) => <a className={index === 0 ? "active" : ""} href={`#section-${index}`} key={item}>{item}</a>)}</nav>
      <div className="utilities"><a className="github-compact" href={repositoryUrl} target="_blank" rel="noreferrer" aria-label={text.github} onMouseEnter={() => setAvatarPose("thinking")} onMouseLeave={() => setAvatarPose("neutral")}><Github size={17} /><span>GitHub</span></a><button className="language" onClick={() => setLanguage(language === "pt" ? "en" : "pt")} aria-label="Alternar idioma">{language.toUpperCase()}</button><button onClick={() => setLight(!light)} aria-label="Alternar aparência">{light ? <Moon size={17} /> : <Sun size={17} />}</button></div>
    </header>

    <section className="hero" id="inicio">
      <div className="visual-stage"><Suspense fallback={<div className="scene-fallback">Carregando observatório…</div>}><PedigreeScene reducedMotion={reducedMotion} entered={entered} introPhase={introPhase} avatarPose={avatarPose} /></Suspense></div>
      <div className="screen-vignette" aria-hidden="true" /><div className="hud-corners" aria-hidden="true"><i /><i /><i /><i /></div>
      <motion.div className="system-status" initial={reducedMotion ? false : { opacity: 0 }} animate={{ opacity: 1 }}><span className="status-dot" />{ready ? text.status : text.sequence[introPhase]}<b>RP–01</b></motion.div>
      {!ready && <button className="skip-intro" onClick={() => setIntroPhase(3)}>{text.skip}<span>››</span></button>}
      <div className="sequence-meter" aria-hidden="true"><span style={{ width: `${(introPhase + 1) * 25}%` }} /></div>
      <motion.div className="guide-tag" initial={false} animate={{ opacity: introPhase >= 1 ? 1 : 0, x: introPhase >= 1 ? 0 : -18 }} transition={{ duration: .65 }}><span>JV</span><div><small>{text.guide}</small><AnimatePresence mode="wait"><motion.strong key={avatarPose} initial={{opacity:0,y:3}} animate={{opacity:1,y:0}} exit={{opacity:0,y:-3}}>{text.reactions[avatarPose]}</motion.strong></AnimatePresence></div></motion.div>
      <motion.div className="content" initial={false} animate={{ opacity: ready ? 1 : 0, y: ready ? 0 : 24 }} transition={{ duration: .8, ease: [0.2, 0.7, 0.2, 1] }}>
        <span className="eyebrow"><i />{text.chapter}</span>
        <AnimatePresence mode="wait"><motion.div key={language} initial={reducedMotion ? false : { opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: .25 }}><h1>{text.title}</h1><p className="description">{text.description}</p></motion.div></AnimatePresence>
        <div className="actions"><button className="primary" onClick={beginNewProject} onMouseEnter={() => setAvatarPose("pointing")} onMouseLeave={() => !entered && !newProjectOpen && setAvatarPose("neutral")}><Play size={17} fill="currentColor" />{text.enter}<ArrowRight size={17} /></button><button className="secondary" onClick={() => { setArchiveOpen(true); setAvatarPose("laptop"); }} onMouseEnter={() => setAvatarPose("laptop")} onMouseLeave={() => !archiveOpen && setAvatarPose("neutral")}><FolderOpen size={18} />{text.open}</button></div>
        <a className="github-link" href={repositoryUrl} target="_blank" rel="noreferrer" onMouseEnter={() => setAvatarPose("thinking")} onMouseLeave={() => setAvatarPose("neutral")}><Github size={16} />{text.github}<span>↗</span></a>
      </motion.div>
      <div className="mission-card"><span>01</span><div><small>{text.mission}</small><strong>{text.missionText}</strong></div><i /></div><div className="explore-hint"><span className="mouse-icon" />{text.hint}</div>
      <AnimatePresence>{archiveOpen && <motion.div className="archive-panel" role="dialog" aria-label={text.archive} initial={{opacity:0,x:40,scale:.97}} animate={{opacity:1,x:0,scale:1}} exit={{opacity:0,x:30}}><header><span><FileJson size={18}/>{text.archive}</span><button aria-label="Fechar arquivo" onClick={() => { setArchiveOpen(false); setAvatarPose("neutral"); }}><X size={17}/></button></header><div className="archive-body"><input ref={fileInput} type="file" accept=".json,.rps.json,application/json" onChange={(event) => inspectProject(event.target.files?.[0])}/><button className="file-picker" onClick={() => fileInput.current?.click()}><Upload size={20}/><span><strong>{text.chooseFile}</strong><small>.rps.json · .json</small></span></button><p className="privacy-note">⌁ {text.localOnly}</p>{fileError && <p className="file-error">{text.invalidFile}</p>}{projectSummary && <section className="project-summary"><small>PROJETO RECONHECIDO</small><h3>{projectSummary.title}</h3><p>{projectSummary.fileName}</p><dl><div><dt>Schema</dt><dd>{projectSummary.schema}</dd></div><div><dt>Indivíduos</dt><dd>{projectSummary.individuals}</dd></div><div><dt>Relações</dt><dd>{projectSummary.relationships}</dd></div></dl><button className="open-project" onClick={openLoadedProject}>Abrir visualização no editor <ArrowRight size={14}/></button></section>}</div></motion.div>}</AnimatePresence>
    </section>
    <AnimatePresence>{newProjectOpen && <NewProjectMission language={language} reducedMotion={reducedMotion} onCancel={() => { setNewProjectOpen(false); setAvatarPose("neutral"); }} onComplete={createProject}/>}</AnimatePresence>
    <AnimatePresence>{workspaceOpen && <motion.section className="workspace" aria-label={text.workspace} initial={{ opacity: 0, scale: 1.06 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }} transition={{ duration: .65, ease: [0.2,.7,.2,1] }}>
      <header className="workspace-bar"><button className="workspace-back" onClick={leaveWorkspace}><ArrowLeft size={17} />{text.back}</button><span className="workspace-title"><BrandMark /><strong>{loadedProject?.title ?? "Família RP–001"}</strong><small>{saveState === "saved" ? "PROJETO SALVO" : "ALTERAÇÕES LOCAIS"}</small></span><div className="workspace-actions"><button aria-label="Desfazer" disabled={!undoStack.length} onClick={undo}><Undo2 size={17} /></button><button aria-label="Refazer" disabled={!redoStack.length} onClick={redo}><Redo2 size={17} /></button><button aria-label="Salvar projeto" onClick={saveProject}><Save size={17} /></button></div></header>
      <div className="pedigree-canvas">{loadedProject ? <WebPedigree project={loadedProject} selectedId={selectedIndividualId} newlyAddedIds={newlyAddedIds} onSelect={setSelectedIndividualId} zoom={zoom}/> : <><div className="generation generation-i">I</div><div className="generation generation-ii">II</div><svg className="pedigree-preview" viewBox="0 0 760 430" role="img" aria-label="Heredograma de demonstração"><g className="pedigree-lines"><path d="M210 100H350M280 100V205M170 205H390M170 205V270M390 205V270M390 270H530M460 270V355" /></g><g className="pedigree-symbols"><rect x="180" y="70" width="60" height="60"/><circle cx="380" cy="100" r="30"/><circle cx="170" cy="300" r="30"/><rect className="affected" x="360" y="270" width="60" height="60"/><circle cx="560" cy="300" r="30"/><rect x="430" y="355" width="60" height="60"/></g><g className="pedigree-labels"><text x="210" y="153">I-1</text><text x="380" y="153">I-2</text><text x="170" y="350">II-1</text><text x="390" y="350">II-2</text><text x="560" y="350">II-3</text></g></svg></>}<div className="canvas-guide"><span>JV</span><p><strong>{loadedProject ? "Projeto carregado em modo de edição." : "Ambiente preparado."}</strong>{loadedProject ? ` ${loadedProject.individuals.length} ${loadedProject.individuals.length===1?"indivíduo disponível":"indivíduos disponíveis"}. Selecione um símbolo para editar.` : " Selecione um indivíduo para começar."}</p></div><AnimatePresence>{editorNotice&&<motion.div className="editor-notice" role="status" aria-live="polite" initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} exit={{opacity:0,y:8}}>{editorNotice}</motion.div>}</AnimatePresence><div className="zoom-control" aria-label="Controles de zoom"><button aria-label="Diminuir zoom" disabled={zoom<=50} onClick={()=>setZoom(value=>Math.max(50,value-10))}><Minus size={15}/></button><output aria-label="Nível de zoom">{zoom}%</output><button aria-label="Aumentar zoom" disabled={zoom>=200} onClick={()=>setZoom(value=>Math.min(200,value+10))}><Plus size={15}/></button><button aria-label="Ajustar à tela" onClick={()=>setZoom(100)}><Maximize2 size={14}/></button></div></div>
      <AnimatePresence>{selectedIndividual && <IndividualDrawer person={selectedIndividual} partners={selectedPartners} reservedLabels={reservedLabels} onClose={()=>setSelectedIndividualId(null)} onSave={saveIndividual} onAddRelative={addRelative}/>}</AnimatePresence>
    </motion.section>}</AnimatePresence>
  </main>;
}
