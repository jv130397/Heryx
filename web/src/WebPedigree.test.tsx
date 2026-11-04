import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { WebPedigree, type WebProject } from "./WebPedigree";

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
});
