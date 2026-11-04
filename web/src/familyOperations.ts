import type { WebIndividual, WebProject } from "./WebPedigree";

export type FamilyAction = "partner" | "parents" | "child" | "sibling";
export type FamilyResult = { project: WebProject; createdId: string };
type IdFactory = (role: string) => string;

const oppositeGender = (gender?: string) => gender === "man" ? "woman" : gender === "woman" ? "man" : "unknown";
const position = (person: WebIndividual) => ({ x: Number(person.layout?.x ?? 480), y: Number(person.layout?.y ?? 300) });
const label = (project: WebProject) => `P-${project.individuals.length + 1}`;
const person = (project: WebProject, id: string, gender: string, x: number, y: number): WebIndividual => ({ id, label: label(project), gender_identity: gender, phenotype_status: "unknown", layout: { x, y } });
const collides = (individuals: WebIndividual[], x: number, y: number, radius = 70) => individuals.some(item => { const point = position(item); return Math.abs(point.x - x) < radius && Math.abs(point.y - y) < radius; });
const availablePair = (individuals: WebIndividual[], centerX: number, y: number) => {
  for (const shift of [0, 220, -220, 440, -440]) if (!collides(individuals, centerX - 85 + shift, y) && !collides(individuals, centerX + 85 + shift, y)) return [centerX - 85 + shift, centerX + 85 + shift] as const;
  return [centerX - 85 + individuals.length * 55, centerX + 85 + individuals.length * 55] as const;
};

export function applyFamilyAction(project: WebProject, sourceId: string, action: FamilyAction, idFactory: IdFactory = role => `${role}-${crypto.randomUUID()}`): FamilyResult {
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
    individuals.push(person({ ...project, individuals }, id, oppositeGender(source.gender_identity), sourcePoint.x + 170, sourcePoint.y));
    relationships.push({ member_a: sourceId, member_b: id, kind: "partner" });
    return { project: { ...project, individuals, relationships, parentages }, createdId: id };
  }

  if (action === "parents") {
    if (parents.length) return { project, createdId: parents[0] };
    const fatherId = idFactory("father"); const motherId = idFactory("mother"); const parentY = sourcePoint.y - 170; const [fatherX, motherX] = availablePair(individuals, sourcePoint.x, parentY);
    individuals.push(person({ ...project, individuals }, fatherId, "man", fatherX, parentY));
    individuals.push(person({ ...project, individuals }, motherId, "woman", motherX, parentY));
    relationships.push({ member_a: fatherId, member_b: motherId, kind: "partner" });
    parentages.push({ parent_id: fatherId, child_id: sourceId, kind: "biological" }, { parent_id: motherId, child_id: sourceId, kind: "biological" });
    return { project: { ...project, individuals, relationships, parentages }, createdId: fatherId };
  }

  if (action === "child") {
    let partnerId = partners[0];
    if (!partnerId) {
      partnerId = idFactory("partner");
      individuals.push(person({ ...project, individuals }, partnerId, oppositeGender(source.gender_identity), sourcePoint.x + 170, sourcePoint.y));
      relationships.push({ member_a: sourceId, member_b: partnerId, kind: "partner" });
    }
    const partner = individuals.find(item => item.id === partnerId)!; const partnerPoint = position(partner); const childId = idFactory("child");
    individuals.push(person({ ...project, individuals }, childId, "unknown", (sourcePoint.x + partnerPoint.x) / 2, Math.max(sourcePoint.y, partnerPoint.y) + 175));
    parentages.push({ parent_id: sourceId, child_id: childId, kind: "biological" }, { parent_id: partnerId, child_id: childId, kind: "biological" });
    return { project: { ...project, individuals, relationships, parentages }, createdId: childId };
  }

  let siblingParents = parents;
  if (!siblingParents.length) {
    const withParents = applyFamilyAction({ ...project, individuals, relationships, parentages }, sourceId, "parents", idFactory).project;
    individuals.splice(0, individuals.length, ...withParents.individuals); relationships.splice(0, relationships.length, ...(withParents.relationships ?? [])); parentages.splice(0, parentages.length, ...(withParents.parentages ?? []));
    siblingParents = parentages.filter(edge => edge.child_id === sourceId).map(edge => edge.parent_id).filter(Boolean) as string[];
  }
  const siblingId = idFactory("sibling");
  individuals.push(person({ ...project, individuals }, siblingId, "unknown", sourcePoint.x + 155, sourcePoint.y));
  for (const parentId of siblingParents) parentages.push({ parent_id: parentId, child_id: siblingId, kind: "biological" });
  return { project: { ...project, individuals, relationships, parentages }, createdId: siblingId };
}
