import type { WebProject } from "./WebPedigree";

const safeName = (value: string) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-zA-Z0-9_-]+/g, "-").replace(/^-|-$/g, "").toLowerCase() || "rare-pedigree";

export function prepareProjectDownload(project: WebProject) {
  const saved = { ...project, updated_at: new Date().toISOString() };
  return { filename: `${safeName(project.title ?? "rare-pedigree")}.rps.json`, content: JSON.stringify(saved, null, 2), project: saved };
}
