import type { WebIndividual, WebProject } from "./WebPedigree";

export type FamilyAction = "partner" | "parents" | "child" | "sibling";
export type FamilyResult = { project: WebProject; createdId: string; blockedReason?: "partner-required" };
type IdFactory = (role: string) => string;

const oppositeGender = (gender?: string) => gender === "man" ? "woman" : gender === "woman" ? "man" : "unknown";
const position = (person: WebIndividual) => ({ x: Number(person.layout?.x ?? 480), y: Number(person.layout?.y ?? 300) });
const label = (project: WebProject) => { const used = new Set(project.individuals.map(individual => individual.label).filter(Boolean)); let sequence = project.individuals.length+1; while (used.has(`P-${sequence}`)) sequence += 1; return `P-${sequence}`; };
const person = (project: WebProject, id: string, gender: string, x: number, y: number): WebIndividual => ({ id, label: label(project), gender_identity: gender, phenotype_status: "unknown", layout: { x, y } });
const collides = (individuals: WebIndividual[], x: number, y: number, radius = 70) => individuals.some(item => { const point = position(item); return Math.abs(point.x - x) < radius && Math.abs(point.y - y) < radius; });
const availablePair = (individuals: WebIndividual[], centerX: number, y: number) => {
  for (const shift of [0, 220, -220, 440, -440]) if (!collides(individuals, centerX - 85 + shift, y) && !collides(individuals, centerX + 85 + shift, y)) return [centerX - 85 + shift, centerX + 85 + shift] as const;
  return [centerX - 85 + individuals.length * 55, centerX + 85 + individuals.length * 55] as const;
};
const availableSingle = (individuals: WebIndividual[], preferredX: number, y: number, step = 155) => {
  for (const offset of [0, -step, step, -step * 2, step * 2, -step * 3, step * 3]) if (!collides(individuals, preferredX + offset, y)) return preferredX + offset;
  return preferredX + individuals.length * step;
};
const availablePartner = (individuals: WebIndividual[], sourceX: number, y: number) => {
  for (const offset of [170,-170,340,-340,510,-510]) if (!collides(individuals,sourceX+offset,y)) return sourceX+offset;
  return sourceX+(individuals.length+1)*170;
};

const ANCESTRY_SLOT = 140;
const COUPLE_GAP = 30;
const GENERATION_GAP = 170;

export function centerAncestralBranches(project: WebProject): WebProject {
  const focus = project.individuals.find(individual => individual.proband) ?? project.individuals[0];
  if (!focus) return project;
  const parentages = project.parentages ?? [];
  const relationships = project.relationships ?? [];
  const parentsByChild = new Map<string,string[]>();
  for (const edge of parentages) {
    if (!edge.parent_id || !edge.child_id) continue;
    parentsByChild.set(edge.child_id,[...(parentsByChild.get(edge.child_id) ?? []),edge.parent_id]);
  }
  const directPartners = relationships
    .filter(edge => edge.member_a === focus.id || edge.member_b === focus.id)
    .map(edge => edge.member_a === focus.id ? edge.member_b : edge.member_a)
    .filter((id): id is string => Boolean(id));
  const ancestrySize = new Map<string,number>();
  const measure = (id: string, visiting = new Set<string>()): number => {
    if (ancestrySize.has(id)) return ancestrySize.get(id)!;
    if (visiting.has(id)) return ANCESTRY_SLOT;
    const nextVisiting = new Set(visiting).add(id);
    const parents = [...new Set(parentsByChild.get(id) ?? [])].slice(0,2);
    if (!parents.length) { ancestrySize.set(id,ANCESTRY_SLOT); return ANCESTRY_SLOT; }
    if (parents.length === 1) { const width = Math.max(ANCESTRY_SLOT,measure(parents[0],nextVisiting)); ancestrySize.set(id,width); return width; }
    const leftWidth = measure(parents[0],nextVisiting); const rightWidth = measure(parents[1],nextVisiting);
    const offset = (leftWidth + rightWidth) / 4 + COUPLE_GAP / 2;
    const width = 2 * (offset + Math.max(leftWidth,rightWidth) / 2);
    ancestrySize.set(id,width); return width;
  };
  const coordinates = new Map<string,{x:number;y:number}>();
  const place = (id: string, x: number, generation: number, visiting = new Set<string>()) => {
    if (visiting.has(id)) return;
    coordinates.set(id,{x,y:300 + generation * GENERATION_GAP});
    const parents = [...new Set(parentsByChild.get(id) ?? [])].slice(0,2);
    if (!parents.length) return;
    const nextVisiting = new Set(visiting).add(id);
    if (parents.length === 1) { place(parents[0],x,generation-1,nextVisiting); return; }
    const leftWidth = measure(parents[0]); const rightWidth = measure(parents[1]);
    const offset = (leftWidth + rightWidth) / 4 + COUPLE_GAP / 2;
    place(parents[0],x-offset,generation-1,nextVisiting);
    place(parents[1],x+offset,generation-1,nextVisiting);
  };
  const primaryPartner = directPartners[0];
  if (primaryPartner) {
    const focusWidth = measure(focus.id); const partnerWidth = measure(primaryPartner);
    const offset = (focusWidth + partnerWidth) / 4 + COUPLE_GAP / 2;
    place(focus.id,480-offset,0);
    place(primaryPartner,480+offset,0);
  } else place(focus.id,480,0);
  return { ...project, individuals: project.individuals.map(individual => coordinates.has(individual.id) ? { ...individual, layout: coordinates.get(individual.id) } : individual) };
}

const completed = (project: WebProject, createdId: string): FamilyResult => ({ project: centerAncestralBranches(project), createdId });

export function applyFamilyAction(project: WebProject, sourceId: string, action: FamilyAction, idFactory: IdFactory = role => `${role}-${crypto.randomUUID()}`, preferredPartnerId?: string): FamilyResult {
  const source = project.individuals.find(item => item.id === sourceId);
  if (!source) return { project, createdId: sourceId };
  const relationships = [...(project.relationships ?? [])];
  const parentages = [...(project.parentages ?? [])];
  const individuals = [...project.individuals];
  const sourcePoint = position(source);
  const partners = relationships.filter(edge => edge.member_a === sourceId || edge.member_b === sourceId).map(edge => edge.member_a === sourceId ? edge.member_b : edge.member_a).filter(Boolean) as string[];
  const parents = parentages.filter(edge => edge.child_id === sourceId).map(edge => edge.parent_id).filter(Boolean) as string[];

  if (action === "partner") {
    const id = idFactory("partner");
    const partnerX = availablePartner(individuals,sourcePoint.x,sourcePoint.y);
    individuals.push(person({ ...project, individuals }, id, oppositeGender(source.gender_identity), partnerX, sourcePoint.y));
    relationships.push({ member_a: sourceId, member_b: id, kind: "partner" });
    return completed({ ...project, individuals, relationships, parentages },id);
  }

  if (action === "parents") {
    if (parents.length) return { project, createdId: parents[0] };
    const fatherId = idFactory("father"); const motherId = idFactory("mother"); const parentY = sourcePoint.y - 170; const [fatherX, motherX] = availablePair(individuals, sourcePoint.x, parentY);
    individuals.push(person({ ...project, individuals }, fatherId, "man", fatherX, parentY));
    individuals.push(person({ ...project, individuals }, motherId, "woman", motherX, parentY));
    relationships.push({ member_a: fatherId, member_b: motherId, kind: "partner" });
    parentages.push({ parent_id: fatherId, child_id: sourceId, kind: "biological" }, { parent_id: motherId, child_id: sourceId, kind: "biological" });
    return completed({ ...project, individuals, relationships, parentages },fatherId);
  }

  if (action === "child") {
    if (partners.length > 1 && !preferredPartnerId) return { project, createdId: sourceId, blockedReason: "partner-required" };
    let partnerId = preferredPartnerId && partners.includes(preferredPartnerId) ? preferredPartnerId : partners[0];
    if (!partnerId) {
      partnerId = idFactory("partner");
      const partnerX = availablePartner(individuals,sourcePoint.x,sourcePoint.y);
      individuals.push(person({ ...project, individuals }, partnerId, oppositeGender(source.gender_identity), partnerX, sourcePoint.y));
      relationships.push({ member_a: sourceId, member_b: partnerId, kind: "partner" });
    }
    const partner = individuals.find(item => item.id === partnerId)!; const partnerPoint = position(partner); const childId = idFactory("child");
    const childY = Math.max(sourcePoint.y, partnerPoint.y) + 175; const childX = availableSingle(individuals, (sourcePoint.x + partnerPoint.x) / 2, childY);
    individuals.push(person({ ...project, individuals }, childId, "unknown", childX, childY));
    parentages.push({ parent_id: sourceId, child_id: childId, kind: "biological" }, { parent_id: partnerId, child_id: childId, kind: "biological" });
    return completed({ ...project, individuals, relationships, parentages },childId);
  }

  let siblingParents = parents;
  if (!siblingParents.length) {
    const withParents = applyFamilyAction({ ...project, individuals, relationships, parentages }, sourceId, "parents", idFactory).project;
    individuals.splice(0, individuals.length, ...withParents.individuals); relationships.splice(0, relationships.length, ...(withParents.relationships ?? [])); parentages.splice(0, parentages.length, ...(withParents.parentages ?? []));
    siblingParents = parentages.filter(edge => edge.child_id === sourceId).map(edge => edge.parent_id).filter(Boolean) as string[];
  }
  const siblingId = idFactory("sibling");
  const siblingX = availableSingle(individuals, sourcePoint.x + 155, sourcePoint.y);
  individuals.push(person({ ...project, individuals }, siblingId, "unknown", siblingX, sourcePoint.y));
  for (const parentId of siblingParents) parentages.push({ parent_id: parentId, child_id: siblingId, kind: "biological" });
  return completed({ ...project, individuals, relationships, parentages },siblingId);
}
