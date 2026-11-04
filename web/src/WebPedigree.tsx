export type WebIndividual = { id: string; label?: string; gender_identity?: string; phenotype_status?: string; proband?: boolean; consultand?: boolean; deceased?: boolean; layout?: { x?: number; y?: number } };
export type WebRelationship = { member_a?: string; member_b?: string; kind?: string };
export type WebParentage = { parent_id?: string; child_id?: string; kind?: string };
export type WebProject = { schema_version: string; title?: string; individuals: WebIndividual[]; relationships?: WebRelationship[]; parentages?: WebParentage[]; study_code?: string; created_at?: string; updated_at?: string };

type Point = { x: number; y: number };

export function WebPedigree({ project, selectedId, onSelect }: { project: WebProject; selectedId?: string | null; onSelect?: (id: string) => void }) {
  const source = project.individuals;
  if (!source.length) return <div className="loaded-empty">Projeto válido, ainda sem indivíduos.</div>;
  const xs = source.map((person) => Number(person.layout?.x ?? 0));
  const ys = source.map((person) => Number(person.layout?.y ?? 0));
  const minX = Math.min(...xs); const maxX = Math.max(...xs); const minY = Math.min(...ys); const maxY = Math.max(...ys);
  const scaleX = (value: number) => 100 + ((value - minX) / Math.max(maxX - minX, 1)) * 760;
  const scaleY = (value: number) => 85 + ((value - minY) / Math.max(maxY - minY, 1)) * 430;
  const points = new Map<string, Point>(source.map((person) => [person.id, { x: scaleX(Number(person.layout?.x ?? 0)), y: scaleY(Number(person.layout?.y ?? 0)) }]));
  const parentages = project.parentages ?? [];
  const children = new Map<string, string[]>();
  for (const edge of parentages) if (edge.parent_id && edge.child_id) children.set(edge.child_id, [...(children.get(edge.child_id) ?? []), edge.parent_id]);

  return <svg className="loaded-pedigree" viewBox="0 0 960 600" role="img" aria-label={`Heredograma carregado: ${project.title ?? "sem título"}`}>
    <g className="loaded-connections">
      {(project.relationships ?? []).filter((edge) => edge.member_a && edge.member_b).map((edge, index) => { const a = points.get(edge.member_a!); const b = points.get(edge.member_b!); return a && b ? <path key={`r-${index}`} d={`M${a.x} ${a.y}H${b.x}`} /> : null; })}
      {[...children.entries()].map(([childId, parentIds]) => { const child = points.get(childId); const parents = parentIds.map((id) => points.get(id)).filter(Boolean) as Point[]; if (!child || !parents.length) return null; if (parents.length >= 2) { const left = parents[0]; const right = parents[1]; const middleX = (left.x + right.x) / 2; const branchY = child.y - Math.max(35, (child.y - Math.max(left.y, right.y)) / 2); return <path key={childId} d={`M${left.x} ${left.y}H${right.x} M${middleX} ${left.y}V${branchY}H${child.x}V${child.y}`} />; } const parent = parents[0]; const branchY = (parent.y + child.y) / 2; return <path key={childId} d={`M${parent.x} ${parent.y}V${branchY}H${child.x}V${child.y}`} />; })}
    </g>
    <g className="loaded-people">{source.map((person) => { const point = points.get(person.id)!; const affected = person.phenotype_status === "affected" || person.phenotype_status === "present"; const shape = person.gender_identity === "man" ? "square" : person.gender_identity === "woman" ? "circle" : "diamond"; return <g key={person.id} role={onSelect ? "button" : undefined} aria-label={onSelect ? `Selecionar indivíduo ${person.label ?? person.id}` : undefined} tabIndex={onSelect ? 0 : undefined} onClick={() => onSelect?.(person.id)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") onSelect?.(person.id); }} transform={`translate(${point.x} ${point.y})`} className={`${affected ? "affected " : ""}${selectedId === person.id ? "selected" : ""}`}>{shape === "square" && <rect x="-22" y="-22" width="44" height="44"/>}{shape === "circle" && <circle r="22"/>}{shape === "diamond" && <rect x="-17" y="-17" width="34" height="34" transform="rotate(45)"/>}{person.deceased && <path className="deceased-mark" d="M-27 27L27 -27"/>}{person.proband && <path className="proband-arrow" d="M-42 38L-25 21M-42 38L-36 26M-42 38L-30 36"/>}<text y="43">{person.label ?? person.id.slice(0, 6)}</text></g>; })}</g>
  </svg>;
}
