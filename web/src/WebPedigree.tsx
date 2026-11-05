export type WebIndividual = { id: string; label?: string; gender_identity?: string; phenotype_status?: string; proband?: boolean; consultand?: boolean; deceased?: boolean; layout?: { x?: number; y?: number } };
export type WebRelationship = { member_a?: string; member_b?: string; kind?: string };
export type WebParentage = { parent_id?: string; child_id?: string; kind?: string };
export type WebProject = { schema_version: string; title?: string; individuals: WebIndividual[]; relationships?: WebRelationship[]; parentages?: WebParentage[]; study_code?: string; created_at?: string; updated_at?: string };

type Point = { x: number; y: number };
const romanGeneration = (value: number) => { const numerals: Array<[number,string]> = [[1000,"M"],[900,"CM"],[500,"D"],[400,"CD"],[100,"C"],[90,"XC"],[50,"L"],[40,"XL"],[10,"X"],[9,"IX"],[5,"V"],[4,"IV"],[1,"I"]]; let remaining = value; return numerals.map(([number,symbol]) => { const count = Math.floor(remaining / number); remaining %= number; return symbol.repeat(count); }).join(""); };

export function WebPedigree({ project, selectedId, newlyAddedIds = [], onSelect, zoom = 100 }: { project: WebProject; selectedId?: string | null; newlyAddedIds?: string[]; onSelect?: (id: string) => void; zoom?: number }) {
  const source = project.individuals;
  if (!source.length) return <div className="loaded-empty">Projeto válido, ainda sem indivíduos.</div>;
  const placed: Array<{x:number;y:number}> = [];
  const displaySource = source.map(person => { const originalX = Number(person.layout?.x ?? 0); const y = Number(person.layout?.y ?? 0); const offsets = [0,100,-100,200,-200,300,-300]; const x = originalX + (offsets.find(offset => !placed.some(point => Math.abs(point.x - (originalX + offset)) < 70 && Math.abs(point.y - y) < 70)) ?? placed.length * 100); placed.push({x,y}); return { person, x, y }; });
  const xs = displaySource.map(item => item.x);
  const ys = displaySource.map(item => item.y);
  const minX = Math.min(...xs); const maxX = Math.max(...xs); const minY = Math.min(...ys); const maxY = Math.max(...ys);
  const spanX = maxX - minX; const spanY = maxY - minY; const middleX = (minX + maxX) / 2; const middleY = (minY + maxY) / 2;
  const scaleX = (value: number) => spanX < 500 ? 480 + (value - middleX) * 1.45 : 100 + ((value - minX) / spanX) * 760;
  const scaleY = (value: number) => spanY < 340 ? 285 + (value - middleY) * 1.35 : 85 + ((value - minY) / spanY) * 430;
  const generationRows = [...new Set(displaySource.map(item => item.y))].sort((a,b) => a-b);
  const points = new Map<string, Point>(displaySource.map(({person,x,y}) => [person.id, { x: scaleX(x), y: scaleY(y) }]));
  const parentages = project.parentages ?? [];
  const children = new Map<string, string[]>();
  for (const edge of parentages) if (edge.parent_id && edge.child_id) children.set(edge.child_id, [...(children.get(edge.child_id) ?? []), edge.parent_id]);

  return <svg className="loaded-pedigree" style={{transform:`translate(-50%,-50%) scale(${zoom/100})`}} viewBox="0 0 960 600" role="img" aria-label={`Heredograma carregado: ${project.title ?? "sem título"}`}>
    <g className="loaded-generations" aria-label="Gerações">{generationRows.map((row,index) => <text key={row} x="52" y={scaleY(row)+5}>{romanGeneration(index+1)}</text>)}</g>
    <g className="loaded-connections">
      {(project.relationships ?? []).filter((edge) => edge.member_a && edge.member_b).map((edge, index) => { const a = points.get(edge.member_a!); const b = points.get(edge.member_b!); const arriving = newlyAddedIds.includes(edge.member_a!) || newlyAddedIds.includes(edge.member_b!); return a && b ? <path className={arriving ? "new-connection" : undefined} key={`r-${index}`} d={`M${a.x} ${a.y}H${b.x}`} /> : null; })}
      {[...children.entries()].map(([childId, parentIds]) => { const child = points.get(childId); const parents = parentIds.map((id) => points.get(id)).filter(Boolean) as Point[]; const arriving = newlyAddedIds.includes(childId) || parentIds.some(id => newlyAddedIds.includes(id)); if (!child || !parents.length) return null; if (parents.length >= 2) { const left = parents[0]; const right = parents[1]; const middleX = (left.x + right.x) / 2; const branchY = child.y - Math.max(35, (child.y - Math.max(left.y, right.y)) / 2); return <path className={arriving ? "new-connection" : undefined} key={childId} d={`M${left.x} ${left.y}H${right.x} M${middleX} ${left.y}V${branchY}H${child.x}V${child.y}`} />; } const parent = parents[0]; const branchY = (parent.y + child.y) / 2; return <path className={arriving ? "new-connection" : undefined} key={childId} d={`M${parent.x} ${parent.y}V${branchY}H${child.x}V${child.y}`} />; })}
    </g>
    <g className="loaded-people">{source.map((person) => { const point = points.get(person.id)!; const affected = person.phenotype_status === "affected" || person.phenotype_status === "present"; const shape = person.gender_identity === "man" ? "square" : person.gender_identity === "woman" ? "circle" : "diamond"; return <g key={person.id} role={onSelect ? "button" : undefined} aria-label={onSelect ? `Selecionar indivíduo ${person.label ?? person.id}` : undefined} tabIndex={onSelect ? 0 : undefined} onClick={() => onSelect?.(person.id)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") onSelect?.(person.id); }} transform={`translate(${point.x} ${point.y})`} className={`${affected ? "affected " : ""}${selectedId === person.id ? "selected " : ""}${newlyAddedIds.includes(person.id) ? "newly-added" : ""}`}>{shape === "square" && <rect x="-22" y="-22" width="44" height="44"/>}{shape === "circle" && <circle r="22"/>}{shape === "diamond" && <rect x="-17" y="-17" width="34" height="34" transform="rotate(45)"/>}{person.deceased && <path className="deceased-mark" d="M-27 27L27 -27"/>}{person.proband && <path className="proband-arrow" d="M-46 42L-27 23M-27 23L-29 34M-27 23L-38 25"/>}<text y="43">{person.label ?? person.id.slice(0, 6)}</text></g>; })}</g>
  </svg>;
}
