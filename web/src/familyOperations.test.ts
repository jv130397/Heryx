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
});
