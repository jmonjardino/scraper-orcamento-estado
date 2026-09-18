import { describe, expect, it } from "vitest";
import { parsePublicationData } from "./data";
import { publicationFixture } from "./test/fixtures";

describe("parsePublicationData", () => {
  it("aceita o contrato público v2", () => {
    expect(parsePublicationData(publicationFixture()).schema_version).toBe(2);
  });

  it.each([
    ["schema", (data: Record<string, unknown>) => { data.schema_version = 1; }],
    ["selectable", (data: Record<string, unknown>) => { (data.view as Record<string, unknown>).selectable = "true"; }],
    ["is_terminal", (data: Record<string, unknown>) => { (data.nodes as Record<string, unknown>[])[0].is_terminal = 0; }],
    ["factual_tags", (data: Record<string, unknown>) => { (data.nodes as Record<string, unknown>[])[0].factual_tags = [7]; }],
  ])("rejeita %s com tipo incompatível", (_name, mutate) => {
    const data = publicationFixture() as unknown as Record<string, unknown>;
    mutate(data);
    expect(() => parsePublicationData(data)).toThrow();
  });
});
