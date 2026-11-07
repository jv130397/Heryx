export type HpoSuggestion = { id: string; label: string };

type OlsDocument = { obo_id?: string; short_form?: string; label?: string; is_obsolete?: boolean };
type OlsResponse = { response?: { docs?: OlsDocument[] } };

export async function searchHpo(query: string, signal?: AbortSignal): Promise<HpoSuggestion[]> {
  const term=query.trim(); if(term.length<2) return [];
  const url=new URL("https://www.ebi.ac.uk/ols4/api/search");
  url.searchParams.set("q",term); url.searchParams.set("ontology","hp"); url.searchParams.set("queryFields","label,synonym,obo_id"); url.searchParams.set("rows","8");
  const response=await fetch(url,{signal,headers:{Accept:"application/json"}}); if(!response.ok) throw new Error("OLS unavailable");
  const data=await response.json() as OlsResponse; const seen=new Set<string>();
  return (data.response?.docs??[]).flatMap(document=>{const id=document.obo_id??document.short_form?.replace("HP_","HP:"); if(!id||!/^HP:\d{7}$/.test(id)||!document.label||document.is_obsolete||seen.has(id)) return []; seen.add(id); return [{id,label:document.label}];});
}
