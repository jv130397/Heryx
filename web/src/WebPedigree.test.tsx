import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { WebPedigree, type WebProject } from "./WebPedigree";
import { applyFamilyAction } from "./familyOperations";

afterEach(cleanup);

describe("WebPedigree", () => {
  it("reconstructs individuals from stored layout coordinates", () => {
    const project: WebProject = { schema_version: "0.4.0", title: "Família carregada", individuals: [
      { id: "father", label: "I-1", gender_identity: "man", layout: { x: 0, y: 0 } },
      { id: "mother", label: "I-2", gender_identity: "woman", layout: { x: 100, y: 0 } },
      { id: "child", label: "II-1", gender_identity: "unknown", proband: true, phenotype_status: "affected", layout: { x: 50, y: 100 } }
    ], parentages: [{ parent_id: "father", child_id: "child" }, { parent_id: "mother", child_id: "child" }] };
    render(<WebPedigree project={project} />);
    expect(screen.getByRole("img", { name: "Heredograma carregado: Família carregada" })).toBeVisible();
    expect(screen.getByText("II-1")).toBeVisible();
    expect(screen.getByText("I", { selector: ".loaded-generations text" })).toBeVisible();
    expect(screen.getByText("II", { selector: ".loaded-generations text" })).toBeVisible();
  });

  it("divides one symbol between multiple phenotype colors", () => {
    const project: WebProject = { schema_version: "0.5.0", individuals: [{ id: "p1", gender_identity: "woman", phenotype_status: "affected", phenotype_markers: [{ id: "neurologic", label: "Neurológico", color: "#8b70e7" }, { id: "cardiac", label: "Cardíaco", color: "#ef705c" }], layout: { x: 0, y: 0 } }] };
    const { container } = render(<WebPedigree project={project}/>);
    expect(container.querySelectorAll("[data-phenotype-segment]")).toHaveLength(2);
    expect(container.querySelector('[data-phenotype-segment="neurologic"]')).toHaveStyle({ fill: "#8b70e7" });
    expect(container.querySelector('[data-phenotype-segment="cardiac"]')).toHaveStyle({ fill: "#ef705c" });
  });

  it("renders special clinical conventions and relationship states", () => {
    const project: WebProject = { schema_version:"0.5.0", individuals:[{id:"a",clinical_symbol:"carrier",adopted:true,assigned_sex:"AFAB",layout:{x:0,y:0}},{id:"b",clinical_symbol:"pregnancy_loss",layout:{x:100,y:0}}], relationships:[{member_a:"a",member_b:"b",kind:"divorced"}] };
    const {container}=render(<WebPedigree project={project}/>);
    expect(container.querySelector(".carrier-dot")).toBeInTheDocument();
    expect(container.querySelector(".adoption-brackets")).toBeInTheDocument();
    expect(container.querySelector(".relationship-divorced")).toBeInTheDocument();
    expect(container.querySelectorAll(".relationship-slash")).toHaveLength(2);
  });

  it("lets the editor select an individual from the diagram", () => {
    const onSelect = vi.fn();
    const project: WebProject = { schema_version: "0.4.0", individuals: [{ id: "proband", label: "I-1", proband: true, layout: { x: 0, y: 0 } }] };
    render(<WebPedigree project={project} onSelect={onSelect}/>);
    fireEvent.click(screen.getByRole("button", { name: "Selecionar indivíduo I-1" }));
    expect(onSelect).toHaveBeenCalledWith("proband");
  });

  it("keeps small family nuclei compact instead of stretching them across the canvas", () => {
    const project: WebProject = { schema_version: "0.4.0", individuals: [{ id: "a", layout: { x: 0, y: 0 } }, { id: "b", layout: { x: 100, y: 0 } }], relationships: [{ member_a: "a", member_b: "b", kind: "partner" }] };
    const { container } = render(<WebPedigree project={project}/>);
    expect(container.querySelector(".loaded-connections path")).toHaveAttribute("d", "M407.5 285H552.5");
  });

  it("separates coincident stored positions and points the proband arrow toward the symbol", () => {
    const project: WebProject = { schema_version: "0.4.0", individuals: [{ id: "a", label: "P-1", proband: true, layout: { x: 10, y: 10 } }, { id: "b", label: "P-2", layout: { x: 10, y: 10 } }] };
    const { container } = render(<WebPedigree project={project}/>);
    const transforms = [...container.querySelectorAll(".loaded-people>g")].map(node => node.getAttribute("transform"));
    expect(new Set(transforms).size).toBe(2);
    expect(container.querySelector(".proband-arrow")).toHaveAttribute("d", "M-46 42L-27 23M-27 23L-29 34M-27 23L-38 25");
  });

  it("separates legacy members that are stored too close together", () => {
    const project: WebProject = { schema_version: "0.4.0", individuals: [{ id: "a", layout: { x: 100, y: 100 } }, { id: "b", layout: { x: 125, y: 100 } }] };
    const { container } = render(<WebPedigree project={project}/>);
    const transforms = [...container.querySelectorAll(".loaded-people>g")].map(node => node.getAttribute("transform"));
    expect(new Set(transforms).size).toBe(2);
  });

  it("applies the requested canvas zoom without changing pedigree coordinates", () => {
    const project: WebProject = { schema_version: "0.4.0", individuals: [{ id: "a", layout: { x: 0, y: 0 } }] };
    render(<WebPedigree project={project} zoom={130}/>);
    expect(screen.getByRole("img")).toHaveStyle({ transform: "translate(-50%,-50%) scale(1.3)" });
  });

  it("marks a newly created relative for its arrival animation", () => {
    const project: WebProject = { schema_version: "0.4.0", individuals: [{ id: "child", label: "II-1", layout: { x: 0, y: 0 } }] };
    render(<WebPedigree project={project} newlyAddedIds={["child"]} onSelect={() => undefined} />);
    expect(screen.getByRole("button", { name: "Selecionar indivíduo II-1" })).toHaveClass("newly-added");
  });

  it("animates connections that belong to the arriving family nucleus", () => {
    const project: WebProject = { schema_version: "0.4.0", individuals: [{ id: "a", layout: { x: 0, y: 0 } }, { id: "b", layout: { x: 100, y: 0 } }], relationships: [{ member_a: "a", member_b: "b", kind: "partner" }] };
    const { container } = render(<WebPedigree project={project} newlyAddedIds={["b"]} />);
    expect(container.querySelector(".loaded-connections path")).toHaveClass("new-connection");
  });

  it("keeps generation markers ordered at the left edge for extended pedigrees", () => {
    const project: WebProject = { schema_version: "0.4.0", individuals: [0,1,2,3].map(index => ({ id: `p-${index}`, layout: { x: index * 100, y: index * 170 } })) };
    const { container } = render(<WebPedigree project={project} />);
    const markers = [...container.querySelectorAll(".loaded-generations text")];
    expect(markers.map(marker => marker.textContent)).toEqual(["I","II","III","IV"]);
    expect(markers.every(marker => marker.getAttribute("x") === "52")).toBe(true);
  });

  it("draws siblings from one shared parental nucleus without duplicating the union line", () => {
    const project: WebProject = { schema_version: "0.4.0", individuals: [
      { id: "father", layout: { x: 0, y: 0 } }, { id: "mother", layout: { x: 100, y: 0 } },
      { id: "child-a", layout: { x: 0, y: 170 } }, { id: "child-b", layout: { x: 150, y: 170 } }
    ], relationships: [{ member_a: "father", member_b: "mother", kind: "partner" }], parentages: [
      { parent_id: "father", child_id: "child-a" }, { parent_id: "mother", child_id: "child-a" },
      { parent_id: "father", child_id: "child-b" }, { parent_id: "mother", child_id: "child-b" }
    ] };
    const { container } = render(<WebPedigree project={project} />);
    const paths = [...container.querySelectorAll(".loaded-connections path")];
    expect(paths).toHaveLength(2);
    const siblingPath = container.querySelector('[data-parental-nucleus="father|mother"]');
    expect(siblingPath).toHaveAttribute("d", expect.stringContaining("M371.25 285H588.75"));
    expect(siblingPath?.getAttribute("d")).not.toContain("M371.25 170.25H516.25");
  });

  it("connects a displaced only child to the parental nucleus", () => {
    const project: WebProject = { schema_version: "0.4.0", individuals: [
      { id: "partner-father", layout: { x: 600, y: 0 } },
      { id: "partner-mother", layout: { x: 700, y: 0 } },
      { id: "partner", layout: { x: 200, y: 170 } }
    ], relationships: [{ member_a: "partner-father", member_b: "partner-mother", kind: "partner" }], parentages: [
      { parent_id: "partner-father", child_id: "partner" },
      { parent_id: "partner-mother", child_id: "partner" }
    ] };
    const { container } = render(<WebPedigree project={project} />);
    const nucleus = container.querySelector('[data-parental-nucleus="partner-father|partner-mother"]');
    const path = nucleus?.getAttribute("d") ?? "";

    expect(path).toMatch(/V[\d.]+ M[\d.]+ [\d.]+H[\d.]+ M[\d.]+ [\d.]+V/);
  });

  it("renders two deep ancestral branches with straight centered descents", () => {
    let sequence = 0;
    const nextId = (role: string) => `${role}-${++sequence}`;
    let family: WebProject = { schema_version:"0.4.0", individuals:[{ id:"proband", proband:true, gender_identity:"man", layout:{x:480,y:300} }], relationships:[], parentages:[] };
    family = applyFamilyAction(family,"proband","parents",nextId).project;
    const [probandFather,probandMother] = family.parentages!.filter(edge=>edge.child_id==="proband").map(edge=>edge.parent_id!);
    family = applyFamilyAction(family,probandFather,"parents",nextId).project;
    family = applyFamilyAction(family,probandMother,"parents",nextId).project;
    family = applyFamilyAction(family,"proband","partner",nextId).project;
    const partner = family.relationships!.find(edge=>edge.member_a==="proband" || edge.member_b==="proband")!;
    const partnerId = partner.member_a === "proband" ? partner.member_b! : partner.member_a!;
    family = applyFamilyAction(family,partnerId,"parents",nextId).project;
    const [partnerFather,partnerMother] = family.parentages!.filter(edge=>edge.child_id===partnerId).map(edge=>edge.parent_id!);
    family = applyFamilyAction(family,partnerFather,"parents",nextId).project;
    family = applyFamilyAction(family,partnerMother,"parents",nextId).project;
    const { container } = render(<WebPedigree project={family} />);
    const ancestralPaths = [...container.querySelectorAll("[data-parental-nucleus]")].map(path=>path.getAttribute("d") ?? "");

    expect(ancestralPaths).toHaveLength(6);
    expect(ancestralPaths.every(path=>!path.includes("H")),JSON.stringify(ancestralPaths)).toBe(true);
  });
});
