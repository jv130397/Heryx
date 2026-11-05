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
});
