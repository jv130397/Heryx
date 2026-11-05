import { describe, expect, it } from "vitest";
import { applyFamilyAction } from "./familyOperations";
import type { WebProject } from "./WebPedigree";

const baseProject = (): WebProject => ({ schema_version: "0.4.0", title: "Família", individuals: [{ id: "proband", label: "I-1", gender_identity: "man", proband: true, layout: { x: 480, y: 300 } }], relationships: [], parentages: [] });
const ids = (...values: string[]) => { let index = 0; return () => values[index++]; };

describe("family operations", () => {
  it("creates two parents in the previous generation", () => {
    const result = applyFamilyAction(baseProject(), "proband", "parents", ids("father", "mother"));
    expect(result.project.individuals).toHaveLength(3);
    expect(result.project.parentages).toEqual(expect.arrayContaining([{ parent_id: "father", child_id: "proband", kind: "biological" }, { parent_id: "mother", child_id: "proband", kind: "biological" }]));
    expect(result.project.individuals.find(person => person.id === "father")?.layout?.y).toBe(130);
  });

  it("creates a partner automatically when adding a child", () => {
    const result = applyFamilyAction(baseProject(), "proband", "child", ids("partner", "child"));
    expect(result.project.individuals).toHaveLength(3);
    expect(result.project.relationships).toContainEqual({ member_a: "proband", member_b: "partner", kind: "partner" });
    expect(result.project.parentages?.filter(edge => edge.child_id === "child")).toHaveLength(2);
  });

  it("reuses both parents when adding a sibling", () => {
    const family = applyFamilyAction(baseProject(), "proband", "parents", ids("father", "mother")).project;
    const result = applyFamilyAction(family, "proband", "sibling", ids("sibling"));
    expect(result.project.parentages?.filter(edge => edge.child_id === "sibling").map(edge => edge.parent_id).sort()).toEqual(["father", "mother"]);
  });

  it("allocates separate lanes for the parents of adjacent partners", () => {
    const coupled = applyFamilyAction(baseProject(), "proband", "partner", ids("partner")).project;
    const firstBranch = applyFamilyAction(coupled, "proband", "parents", ids("f1", "m1")).project;
    const secondBranch = applyFamilyAction(firstBranch, "partner", "parents", ids("f2", "m2")).project;
    const coordinates = secondBranch.individuals.filter(person => ["f1","m1","f2","m2"].includes(person.id)).map(person => `${person.layout?.x}:${person.layout?.y}`);
    expect(new Set(coordinates).size).toBe(4);
  });

  it("places a sibling away from an existing partner", () => {
    const coupled = applyFamilyAction(baseProject(), "proband", "partner", ids("partner")).project;
    const result = applyFamilyAction(coupled, "proband", "sibling", ids("father", "mother", "sibling"));
    const partnerX = result.project.individuals.find(person => person.id === "partner")?.layout?.x;
    const siblingX = result.project.individuals.find(person => person.id === "sibling")?.layout?.x;
    expect(siblingX).not.toBe(partnerX);
    expect(Math.abs(Number(siblingX) - Number(partnerX))).toBeGreaterThanOrEqual(70);
  });

  it("alternates multiple partners around the source instead of placing lines through symbols", () => {
    const first = applyFamilyAction(baseProject(), "proband", "partner", ids("partner-a")).project;
    const second = applyFamilyAction(first, "proband", "partner", ids("partner-b")).project;
    const sourceX = Number(second.individuals.find(person => person.id === "proband")?.layout?.x);
    const firstX = Number(second.individuals.find(person => person.id === "partner-a")?.layout?.x);
    const secondX = Number(second.individuals.find(person => person.id === "partner-b")?.layout?.x);
    expect(firstX-sourceX).toBe(170);
    expect(secondX-sourceX).toBe(-170);
  });

  it("never reuses an existing generated label from a legacy project", () => {
    const legacy = baseProject();
    legacy.individuals.push({ id: "legacy", label: "P-3", layout: { x: 820, y: 300 } });
    const result = applyFamilyAction(legacy, "proband", "partner", ids("new-partner"));
    expect(result.project.individuals.find(person => person.id === "new-partner")?.label).toBe("P-4");
    expect(new Set(result.project.individuals.map(person => person.label)).size).toBe(result.project.individuals.length);
  });

  it("requires an explicit branch before adding a child to someone with multiple partners", () => {
    const first = applyFamilyAction(baseProject(), "proband", "partner", ids("partner-a")).project;
    const family = applyFamilyAction(first, "proband", "partner", ids("partner-b")).project;
    const blocked = applyFamilyAction(family, "proband", "child", ids("child"));
    expect(blocked.blockedReason).toBe("partner-required");
    expect(blocked.project).toBe(family);
    const created = applyFamilyAction(family, "proband", "child", ids("child"), "partner-b");
    expect(created.project.parentages?.filter(edge=>edge.child_id==="child").map(edge=>edge.parent_id).sort()).toEqual(["partner-b","proband"]);
  });

  it("keeps the proband and partner ancestry centered in separate branches", () => {
    let family = applyFamilyAction(baseProject(),"proband","parents",ids("proband-father","proband-mother")).project;
    family = applyFamilyAction(family,"proband-father","parents",ids("pf-father","pf-mother")).project;
    family = applyFamilyAction(family,"proband-mother","parents",ids("pm-father","pm-mother")).project;
    family = applyFamilyAction(family,"proband","partner",ids("partner")).project;
    family = applyFamilyAction(family,"partner","parents",ids("partner-father","partner-mother")).project;
    family = applyFamilyAction(family,"partner-father","parents",ids("qf-father","qf-mother")).project;
    family = applyFamilyAction(family,"partner-mother","parents",ids("qm-father","qm-mother")).project;
    const x = (id: string) => Number(family.individuals.find(person => person.id === id)?.layout?.x);
    const midpoint = (left: string,right: string) => (x(left)+x(right))/2;

    expect(family.individuals).toHaveLength(14);
    expect(midpoint("proband-father","proband-mother")).toBe(x("proband"));
    expect(midpoint("partner-father","partner-mother")).toBe(x("partner"));
    expect(midpoint("pf-father","pf-mother")).toBe(x("proband-father"));
    expect(midpoint("pm-father","pm-mother")).toBe(x("proband-mother"));
    expect(midpoint("qf-father","qf-mother")).toBe(x("partner-father"));
    expect(midpoint("qm-father","qm-mother")).toBe(x("partner-mother"));
    expect(Math.max(x("pf-father"),x("pf-mother"),x("pm-father"),x("pm-mother"))).toBeLessThan(Math.min(x("qf-father"),x("qf-mother"),x("qm-father"),x("qm-mother")));
  });

  it("places siblings outside the proband-partner union and keeps their generation aligned", () => {
    let family = applyFamilyAction(baseProject(),"proband","parents",ids("pf","pm")).project;
    family = applyFamilyAction(family,"proband","partner",ids("partner")).project;
    family = applyFamilyAction(family,"partner","parents",ids("qf","qm")).project;
    family = applyFamilyAction(family,"proband","sibling",ids("proband-sibling")).project;
    family = applyFamilyAction(family,"partner","sibling",ids("partner-sibling")).project;
    const point = (id: string) => family.individuals.find(person=>person.id===id)!.layout!;

    expect(Number(point("proband-sibling").x)).toBeLessThan(Number(point("proband").x));
    expect(Number(point("partner-sibling").x)).toBeGreaterThan(Number(point("partner").x));
    expect(point("proband-sibling").y).toBe(point("proband").y);
    expect(point("partner-sibling").y).toBe(point("partner").y);
    expect(new Set(["proband","partner","proband-sibling","partner-sibling"].map(id=>`${point(id).x}:${point(id).y}`)).size).toBe(4);
  });
});
