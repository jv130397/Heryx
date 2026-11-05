import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { IndividualDrawer } from "./IndividualDrawer";

afterEach(cleanup);

describe("IndividualDrawer", () => {
  it("applies individual edits only after confirmation", () => {
    const onSave = vi.fn();
    render(<IndividualDrawer person={{ id: "p1", label: "I-1", gender_identity: "unknown" }} onClose={vi.fn()} onSave={onSave} onAddRelative={vi.fn()}/>);
    fireEvent.change(screen.getByLabelText("Identificador exibido"), { target: { value: "II-2" } });
    fireEvent.click(screen.getByRole("button", { name: "Feminino" }));
    fireEvent.click(screen.getByLabelText("Fenótipo investigado presente"));
    fireEvent.click(screen.getByRole("button", { name: /Aplicar alterações/ }));
    expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ label: "II-2", gender_identity: "woman", phenotype_status: "affected" }));
  });

  it("routes family creation through the selected individual", () => {
    const onAddRelative = vi.fn();
    render(<IndividualDrawer person={{ id: "p1", label: "I-1" }} onClose={vi.fn()} onSave={vi.fn()} onAddRelative={onAddRelative}/>);
    fireEvent.click(screen.getByRole("button", { name: /Filho/ }));
    expect(onAddRelative).toHaveBeenCalledWith("child", undefined);
  });

  it("requires a parental branch when the individual has multiple partners", () => {
    const onAddRelative = vi.fn();
    render(<IndividualDrawer person={{ id: "p1", label: "I-1" }} partners={[{id:"p2",label:"I-2"},{id:"p3",label:"I-3"}]} onClose={vi.fn()} onSave={vi.fn()} onAddRelative={onAddRelative}/>);
    expect(screen.getByRole("button",{name:/Filho/})).toBeDisabled();
    fireEvent.change(screen.getByLabelText("Outro genitor para o novo filho"),{target:{value:"p3"}});
    fireEvent.click(screen.getByRole("button",{name:/Filho/}));
    expect(onAddRelative).toHaveBeenCalledWith("child","p3");
  });

  it("blocks empty or duplicate displayed identifiers", () => {
    const onSave = vi.fn();
    render(<IndividualDrawer person={{id:"p1",label:"I-1"}} reservedLabels={["II-1"]} onClose={vi.fn()} onSave={onSave} onAddRelative={vi.fn()}/>);
    const identifier = screen.getByLabelText("Identificador exibido");
    fireEvent.change(identifier,{target:{value:"II-1"}});
    expect(screen.getByRole("alert")).toHaveTextContent("já está em uso");
    expect(screen.getByRole("button",{name:/Aplicar alterações/})).toBeDisabled();
    fireEvent.change(identifier,{target:{value:""}});
    expect(screen.getByRole("alert")).toHaveTextContent("Informe um identificador");
    expect(onSave).not.toHaveBeenCalled();
  });
});
