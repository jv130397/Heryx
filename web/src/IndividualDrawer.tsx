import { motion } from "framer-motion";
import { Activity, Check, Dna, UserRound, X } from "lucide-react";
import { useEffect, useState } from "react";
import type { WebIndividual } from "./WebPedigree";
import "./IndividualDrawer.css";

type Props = { person: WebIndividual; onClose: () => void; onSave: (person: WebIndividual) => void };

export function IndividualDrawer({ person, onClose, onSave }: Props) {
  const [draft, setDraft] = useState(person);
  useEffect(() => setDraft(person), [person]);
  const update = <K extends keyof WebIndividual>(key: K, value: WebIndividual[K]) => setDraft(current => ({ ...current, [key]: value }));
  return <motion.aside className="individual-drawer" role="dialog" aria-label={`Editar indivíduo ${person.label ?? person.id}`} initial={{x:"105%",opacity:0}} animate={{x:0,opacity:1}} exit={{x:"105%",opacity:0}} transition={{duration:.38,ease:[.2,.7,.2,1]}}>
    <header><span><UserRound size={17}/><b>{draft.label ?? draft.id}</b><small>PERFIL DO INDIVÍDUO</small></span><button onClick={onClose} aria-label="Fechar edição"><X size={17}/></button></header>
    <div className="drawer-body"><div className="drawer-status"><i/><span><small>REGISTRO ATIVO</small><strong>Dados locais do heredograma</strong></span></div>
      <section><h3><Dna size={15}/>Identificação</h3><label>Identificador exibido<input value={draft.label ?? ""} onChange={event => update("label", event.target.value)}/></label><fieldset><legend>Símbolo biológico</legend><div className="drawer-symbols">{[["man","Masculino"],["woman","Feminino"],["unknown","Não especificado"]].map(([value,label])=><button type="button" className={draft.gender_identity===value?"selected":""} aria-pressed={draft.gender_identity===value} onClick={()=>update("gender_identity",value)} key={value}><i className={value}/>{label}</button>)}</div></fieldset></section>
      <section><h3><Activity size={15}/>Representação clínica</h3><label className="drawer-check"><input type="checkbox" checked={draft.phenotype_status==="affected"} onChange={event=>update("phenotype_status",event.target.checked?"affected":"unknown")}/><span><i><Check size={11}/></i>Fenótipo investigado presente</span></label><label className="drawer-check"><input type="checkbox" checked={Boolean(draft.proband)} onChange={event=>update("proband",event.target.checked)}/><span><i><Check size={11}/></i>Probando</span></label><label className="drawer-check"><input type="checkbox" checked={Boolean(draft.consultand)} onChange={event=>update("consultand",event.target.checked)}/><span><i><Check size={11}/></i>Consultante</span></label><label className="drawer-check"><input type="checkbox" checked={Boolean(draft.deceased)} onChange={event=>update("deceased",event.target.checked)}/><span><i><Check size={11}/></i>Falecido</span></label></section>
    </div><footer><button className="drawer-cancel" onClick={onClose}>Cancelar</button><button className="drawer-save" onClick={()=>onSave(draft)}><Check size={15}/>Aplicar alterações</button></footer>
  </motion.aside>;
}
