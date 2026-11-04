import { describe, expect, it, vi } from "vitest";
import { prepareProjectDownload } from "./projectIO";

describe("project download", () => {
  it("creates a compatible, sanitized RarePedigree file", () => {
    vi.useFakeTimers(); vi.setSystemTime(new Date("2026-11-04T12:00:00Z"));
    const result = prepareProjectDownload({ schema_version: "0.4.0", title: "Família João / Caso 01", individuals: [{ id: "p1" }] });
    expect(result.filename).toBe("familia-joao-caso-01.rps.json");
    expect(JSON.parse(result.content)).toMatchObject({ schema_version: "0.4.0", title: "Família João / Caso 01", updated_at: "2026-11-04T12:00:00.000Z" });
    vi.useRealTimers();
  });
});
