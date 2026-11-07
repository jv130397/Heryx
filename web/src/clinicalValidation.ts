import type { WebProject } from "./WebPedigree";

export type ValidationIssue = { severity: "error" | "warning"; code: string; message: string; individualId?: string };

export function validateClinicalProject(project: WebProject): ValidationIssue[] {
  const issues: ValidationIssue[]=[];
  if(!project.individuals.length) issues.push({severity:"error",code:"EMPTY",message:"O heredograma não possui indivíduos."});
  const probands=project.individuals.filter(person=>person.proband);
  if(!probands.length) issues.push({severity:"warning",code:"NO_PROBAND",message:"Nenhum probando foi definido."});
  if(probands.length>1) issues.push({severity:"error",code:"MULTIPLE_PROBANDS",message:"Há mais de um probando no heredograma."});
  const labels=new Map<string,string>();
  for(const person of project.individuals) {
    const label=(person.label??"").trim().toLocaleLowerCase();
    if(!label) issues.push({severity:"warning",code:"MISSING_LABEL",message:"Indivíduo sem identificador exibido.",individualId:person.id});
    else if(labels.has(label)) issues.push({severity:"error",code:"DUPLICATE_LABEL",message:`Identificador duplicado: ${person.label}.`,individualId:person.id}); else labels.set(label,person.id);
    if(!person.gender_identity) issues.push({severity:"warning",code:"MISSING_SEX",message:`${person.label??person.id}: símbolo biológico não definido.`,individualId:person.id});
    const hpoIds=new Set<string>();
    for(const term of person.hpo_terms??[]) {
      if(!/^HP:\d{7}$/.test(term.id)) issues.push({severity:"error",code:"INVALID_HPO",message:`${person.label??person.id}: código HPO inválido (${term.id}).`,individualId:person.id});
      if(hpoIds.has(term.id)) issues.push({severity:"warning",code:"DUPLICATE_HPO",message:`${person.label??person.id}: termo HPO repetido (${term.id}).`,individualId:person.id});
      hpoIds.add(term.id);
    }
  }
  const ids=new Set(project.individuals.map(person=>person.id));
  for(const edge of project.parentages??[]) if(!edge.parent_id||!edge.child_id||!ids.has(edge.parent_id)||!ids.has(edge.child_id)) issues.push({severity:"error",code:"BROKEN_PARENTAGE",message:"Existe uma relação parental com indivíduo inexistente."});
  return issues;
}
