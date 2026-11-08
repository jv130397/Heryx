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

type TutorialKind = "man"|"woman"|"unspecified"|"affected"|"conditions"|"deceased"|"proband"|"presymptomatic"|"carrier"|"partners"|"separated"|"consanguinity"|"descent"|"twinsDz"|"twinsMz"|"adoption"|"pregnancy"|"pregnancyKnown"|"sab"|"top"|"noChildren"|"infertility"|"multiple"|"unknownHistory"|"donor"|"surrogate"|"assignedSex";
type TutorialItem = { kind: TutorialKind; name: string; detail: string };
const tutorialGroups: { id: string; label: string; description: string; items: TutorialItem[] }[] = [
  { id:"individuals", label:"Indivíduos e estado", description:"Forma externa, condição clínica e papel da pessoa no heredograma.", items:[
    {kind:"man",name:"Quadrado",detail:"Homem ou menino"},{kind:"woman",name:"Círculo",detail:"Mulher ou menina"},{kind:"unspecified",name:"Losango",detail:"Gênero desconhecido, diverso ou não relevante"},{kind:"affected",name:"Preenchimento",detail:"Característica ou condição presente"},{kind:"conditions",name:"Preenchimento dividido",detail:"Mais de uma condição, definida na legenda"},{kind:"deceased",name:"Linha diagonal",detail:"Pessoa falecida"},{kind:"proband",name:"Seta com P",detail:"Probando ou caso índice"},{kind:"presymptomatic",name:"Linha vertical",detail:"Portador pré-sintomático de condição dominante"},{kind:"carrier",name:"Setor preenchido",detail:"Portador de variante recessiva; definir na legenda"},
  ]},
  { id:"relationships", label:"Vínculos e descendência", description:"Como representar relações, filhos, gemelaridade e adoção.", items:[
    {kind:"partners",name:"Linha de relacionamento",detail:"Une parceiros ou cônjuges"},{kind:"separated",name:"Linha interrompida",detail:"Relacionamento encerrado"},{kind:"consanguinity",name:"Linha dupla",detail:"Consanguinidade; informar o grau quando necessário"},{kind:"descent",name:"Linha de descendência",detail:"Conecta pais, irmãos e descendentes"},{kind:"twinsDz",name:"Gêmeos dizigóticos",detail:"Duas linhas partem do mesmo ponto"},{kind:"twinsMz",name:"Gêmeos monozigóticos",detail:"Linha horizontal adicional indica monozigosidade"},{kind:"adoption",name:"Adoção",detail:"Colchetes; linha tracejada adotiva e sólida biológica"},
  ]},
  { id:"reproductive", label:"História reprodutiva", description:"Gestações atuais, perdas, interrupções e ausência de descendência.", items:[
    {kind:"pregnancy",name:"Gestação",detail:"Losango com P quando o gênero fetal é desconhecido"},{kind:"pregnancyKnown",name:"Gestação com gênero conhecido",detail:"Usar a forma correspondente e registrar a idade gestacional"},{kind:"sab",name:"Perda gestacional espontânea",detail:"Triângulo; anotar SAB e idade gestacional"},{kind:"top",name:"Interrupção da gestação",detail:"Triângulo com traço diagonal; anotar TOP"},{kind:"noChildren",name:"Sem filhos",detail:"Linha terminal; motivo desconhecido ou por escolha"},{kind:"infertility",name:"Infertilidade",detail:"Linha terminal com anotação INF"},
  ]},
  { id:"annotations", label:"Anotações especiais", description:"Recursos complementares para manter o desenho legível e clinicamente preciso.", items:[
    {kind:"multiple",name:"Vários indivíduos",detail:"Número dentro do símbolo resume pessoas equivalentes"},{kind:"unknownHistory",name:"História indisponível",detail:"Interrogação indica histórico familiar desconhecido"},{kind:"donor",name:"Doador de gameta",detail:"Anotação D; detalhar óvulo ou espermatozoide"},{kind:"surrogate",name:"Gestação de substituição",detail:"Anotação S para gestante substituta"},{kind:"assignedSex",name:"Sexo atribuído ao nascer",detail:"AFAB, AMAB ou UAAB abaixo da forma de gênero"},
  ]},
];

function TutorialGlyph({kind}:{kind:TutorialKind}) {
  const common={fill:"none",stroke:"currentColor",strokeWidth:2.4} as const;
  if(kind==="man") return <svg viewBox="0 0 64 52"><rect x="19" y="8" width="28" height="28" {...common}/></svg>;
  if(kind==="woman") return <svg viewBox="0 0 64 52"><circle cx="33" cy="22" r="14" {...common}/></svg>;
  if(kind==="unspecified") return <svg viewBox="0 0 64 52"><path d="M33 6l16 16-16 16-16-16z" {...common}/></svg>;
  if(kind==="affected") return <svg viewBox="0 0 64 52"><circle cx="33" cy="22" r="14" fill="currentColor" stroke="currentColor" strokeWidth="2.4"/></svg>;
  if(kind==="conditions") return <svg viewBox="0 0 64 52"><circle cx="33" cy="22" r="14" {...common}/><path d="M33 8a14 14 0 0 1 0 28z" fill="currentColor"/></svg>;
  if(kind==="deceased") return <svg viewBox="0 0 64 52"><circle cx="33" cy="22" r="14" {...common}/><path d="M16 39L49 5" {...common}/></svg>;
  if(kind==="proband") return <svg viewBox="0 0 64 52"><rect x="27" y="8" width="25" height="25" {...common}/><path d="M6 42l22-15M6 42l3-8M6 42l8-1" {...common}/><text x="8" y="14">P</text></svg>;
  if(kind==="presymptomatic") return <svg viewBox="0 0 64 52"><circle cx="33" cy="22" r="14" {...common}/><path d="M33 8v28" {...common}/></svg>;
  if(kind==="carrier") return <svg viewBox="0 0 64 52"><circle cx="33" cy="22" r="14" {...common}/><path d="M33 22V8a14 14 0 0 1 12.1 7z" fill="currentColor"/></svg>;
  if(kind==="partners") return <svg viewBox="0 0 94 52"><rect x="8" y="10" width="24" height="24" {...common}/><circle cx="76" cy="22" r="12" {...common}/><path d="M32 22h32" {...common}/></svg>;
  if(kind==="separated") return <svg viewBox="0 0 94 52"><rect x="8" y="10" width="24" height="24" {...common}/><circle cx="76" cy="22" r="12" {...common}/><path d="M32 22h13m7 0h12M44 28l9-12" {...common}/></svg>;
  if(kind==="consanguinity") return <svg viewBox="0 0 94 52"><rect x="8" y="10" width="24" height="24" {...common}/><circle cx="76" cy="22" r="12" {...common}/><path d="M32 18h32M32 26h32" {...common}/></svg>;
  if(kind==="descent") return <svg viewBox="0 0 94 52"><path d="M14 8h66M47 8v16M25 24h44M25 24v16M69 24v16" {...common}/><circle cx="25" cy="43" r="5" {...common}/><rect x="64" y="38" width="10" height="10" {...common}/></svg>;
  if(kind==="twinsDz"||kind==="twinsMz") return <svg viewBox="0 0 94 52"><path d="M47 6v12M47 18L27 36M47 18l20 18" {...common}/>{kind==="twinsMz"&&<path d="M34 29h26" {...common}/>}<circle cx="25" cy="40" r="7" {...common}/><circle cx="69" cy="40" r="7" {...common}/></svg>;
  if(kind==="adoption") return <svg viewBox="0 0 94 52"><path d="M47 4v18" stroke="currentColor" strokeWidth="2.4" strokeDasharray="5 4"/><path d="M27 12v30h10M67 12v30H57" {...common}/><circle cx="47" cy="37" r="10" {...common}/></svg>;
  if(kind==="pregnancy") return <svg viewBox="0 0 64 52"><path d="M33 4v9M33 13l13 13-13 13-13-13z" {...common}/><text x="29" y="30">P</text></svg>;
  if(kind==="pregnancyKnown") return <svg viewBox="0 0 64 52"><path d="M33 4v9" {...common}/><circle cx="33" cy="27" r="13" {...common}/><text x="29" y="31">P</text></svg>;
  if(kind==="sab"||kind==="top") return <svg viewBox="0 0 64 52"><path d="M33 4v9M18 38h30L33 13z" {...common}/>{kind==="top"&&<path d="M18 40L48 10" {...common}/>}</svg>;
  if(kind==="noChildren"||kind==="infertility") return <svg viewBox="0 0 64 52"><path d="M33 5v28M21 33h24" {...common}/>{kind==="infertility"&&<text x="23" y="49">INF</text>}</svg>;
  if(kind==="multiple") return <svg viewBox="0 0 64 52"><path d="M33 6l16 16-16 16-16-16z" {...common}/><text x="27" y="27">5</text></svg>;
  if(kind==="unknownHistory") return <svg viewBox="0 0 64 52"><path d="M33 6l16 16-16 16-16-16z" {...common}/><text x="28" y="28">?</text></svg>;
  if(kind==="donor"||kind==="surrogate") return <svg viewBox="0 0 64 52"><circle cx="33" cy="20" r="14" {...common}/><text x="27" y="25">{kind==="donor"?"D":"S"}</text></svg>;
  return <svg viewBox="0 0 84 52"><path d="M42 5l14 14-14 14-14-14z" {...common}/><text x="24" y="49">AFAB</text></svg>;
}

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
  const [tutorialGroup, setTutorialGroup] = useState(tutorialGroups[0].id);
  const activeTutorialGroup = tutorialGroups.find(group=>group.id===tutorialGroup) ?? tutorialGroups[0];
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
        <button className="mobile-tutorial" type="button" aria-label="Abrir tutorial" onClick={() => setInformation("tutorial")}><BookOpen/></button>
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
          <span className="panel-kicker">Tutorial clínico · nomenclatura padronizada</span><h2>Como ler um heredograma</h2><p>Consulte símbolos de indivíduos, vínculos familiares, história reprodutiva e anotações especiais. O significado de cores e preenchimentos deve sempre aparecer na legenda do heredograma.</p>
          <nav className="tutorial-tabs" aria-label="Categorias do tutorial">{tutorialGroups.map(group=><button key={group.id} type="button" className={group.id===activeTutorialGroup.id?"active":""} aria-pressed={group.id===activeTutorialGroup.id} onClick={()=>setTutorialGroup(group.id)}>{group.label}<small>{group.items.length}</small></button>)}</nav>
          <div className="tutorial-section-heading"><strong>{activeTutorialGroup.label}</strong><span>{activeTutorialGroup.description}</span></div>
          <div className="symbol-legend expanded">
            {activeTutorialGroup.items.map(item=><article key={item.kind}><i className="tutorial-glyph"><TutorialGlyph kind={item.kind}/></i><span><strong>{item.name}</strong><small>{item.detail}</small></span></article>)}
          </div>
          <footer className="tutorial-note"><ShieldCheck/><span><strong>Nota clínica</strong><small>As convenções seguem Bennett et al. (2008) e a revisão inclusiva da NSGC (2022). Anotações complementares e uma legenda são essenciais quando houver ambiguidade.</small></span></footer>
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
