import { describe, expect, it } from "vitest";
import { publicationFixture } from "./test/fixtures";
import {
  buildScenarioModel,
  calculateScenario,
  nodeSelectionState,
  reconcileScenarioContext,
  resetScenario,
  scenarioContextKey,
  setNodeExcluded,
} from "./scenario";

function validModel() {
  const result = buildScenarioModel(publicationFixture());
  if (!result.valid) throw new Error(result.errors.join("\n"));
  return result.model;
}

describe("scenario engine", () => {
  it("calcula exclusivamente pelas folhas e mantém a igualdade ao cêntimo", () => {
    const model = validModel();
    const excluded = setNodeExcluded(model, new Set(), "release:view:area:acao-1", true);
    expect(calculateScenario(model, excluded)).toEqual({
      totalCents: 1_000,
      includedCents: 800,
      excludedCents: 200,
      excludedPercentage: 0.2,
      affectedLeafCount: 1,
    });
  });

  it("selecionar pai e filho não duplica montante", () => {
    const model = validModel();
    let excluded = setNodeExcluded(model, new Set(), "release:view:area", true);
    excluded = setNodeExcluded(model, excluded, "release:view:area:acao-1", true);
    expect([...excluded].sort()).toEqual(["release:view:area:acao-1", "release:view:area:acao-2"]);
    expect(calculateScenario(model, excluded).excludedCents).toBe(600);
  });

  it("marca pais parciais e repõe um ramo inteiro", () => {
    const model = validModel();
    let excluded = setNodeExcluded(model, new Set(), "release:view:area:acao-1", true);
    expect(nodeSelectionState(model, excluded, "release:view:area")).toBe("partial");
    expect(nodeSelectionState(model, excluded, model.root.node_id)).toBe("partial");
    excluded = setNodeExcluded(model, excluded, "release:view:area", false);
    expect(excluded.size).toBe(0);
    expect(nodeSelectionState(model, excluded, "release:view:area")).toBe("included");
  });

  it("conta folhas de valor zero como rubricas afetadas", () => {
    const data = publicationFixture();
    data.nodes.find((node) => node.node_id.endsWith("acao-1"))!.amount_cents = 0;
    data.nodes.find((node) => node.node_id === "release:view:area")!.amount_cents = 400;
    data.nodes.find((node) => node.node_id === data.view.root_node_id)!.amount_cents = 800;
    const result = buildScenarioModel(data);
    expect(result.valid).toBe(true);
    if (!result.valid) return;
    const excluded = setNodeExcluded(result.model, new Set(), "release:view:area:acao-1", true);
    expect(calculateScenario(result.model, excluded)).toMatchObject({ excludedCents: 0, affectedLeafCount: 1 });
  });

  it("preserva as invariantes em sequências de seleções hierárquicas", () => {
    const model = validModel();
    const nodes = [...model.nodesById.keys()];
    let excluded = new Set<string>();
    for (let index = 0; index < 60; index += 1) {
      const nodeId = nodes[index % nodes.length];
      excluded = setNodeExcluded(model, excluded, nodeId, index % 3 !== 0);
      const totals = calculateScenario(model, excluded);
      expect(totals.includedCents + totals.excludedCents).toBe(totals.totalCents);
      expect(totals.affectedLeafCount).toBe(excluded.size);
      expect([...excluded].every((leafId) => model.leafIds.has(leafId))).toBe(true);
    }
    excluded = resetScenario();
    expect(calculateScenario(model, excluded)).toMatchObject({ excludedCents: 0, includedCents: 1_000 });
  });

  it("repõe o cenário sem conservar folhas excluídas", () => {
    const model = validModel();
    const excluded = setNodeExcluded(model, new Set(), model.root.node_id, true);
    expect(excluded.size).toBe(3);
    expect(calculateScenario(model, resetScenario())).toMatchObject({
      includedCents: 1_000,
      excludedCents: 0,
      affectedLeafCount: 0,
    });
  });

  it("rejeita um pai intermédio que não reconcilia mesmo quando as folhas ainda somam a raiz", () => {
    const data = publicationFixture();
    data.nodes.find((node) => node.node_id === "release:view:area")!.amount_cents = 700;
    const result = buildScenarioModel(data);
    expect(result.valid).toBe(false);
    if (result.valid) return;
    expect(result.errors).toContain(
      "O montante da rubrica release:view:area não coincide com a soma dos filhos.",
    );
    expect(data.nodes.filter((node) => node.is_terminal).reduce((sum, node) => sum + node.amount_cents, 0)).toBe(1_000);
  });

  it("limpa seleção quando muda qualquer parte da chave de contexto", () => {
    const data = publicationFixture();
    const previous = scenarioContextKey(data);
    const excluded = new Set(["release:view:P-002"]);
    expect(reconcileScenarioContext(previous, previous, excluded)).toEqual({ excludedLeafIds: excluded, cleared: false });
    data.view.view_id = "outra-vista";
    expect(reconcileScenarioContext(previous, scenarioContextKey(data), excluded)).toEqual({
      excludedLeafIds: new Set(),
      cleared: true,
    });
  });

  it.each([
    ["IDs repetidos", (data: ReturnType<typeof publicationFixture>) => { data.nodes[1].node_id = data.nodes[0].node_id; }],
    ["pai inexistente", (data: ReturnType<typeof publicationFixture>) => { data.nodes[1].parent_node_id = "ausente"; }],
    ["rubrica inacessível", (data: ReturnType<typeof publicationFixture>) => { data.nodes[1].parent_node_id = null; }],
    ["ciclo", (data: ReturnType<typeof publicationFixture>) => { data.nodes[1].parent_node_id = data.nodes[2].node_id; }],
    ["terminação incoerente", (data: ReturnType<typeof publicationFixture>) => { data.nodes[1].is_terminal = true; }],
    ["nível da raiz", (data: ReturnType<typeof publicationFixture>) => { data.nodes[0].level = 1; }],
    ["montante inseguro", (data: ReturnType<typeof publicationFixture>) => { data.nodes[2].amount_cents = Number.MAX_SAFE_INTEGER + 1; }],
    ["soma divergente", (data: ReturnType<typeof publicationFixture>) => { data.nodes[2].amount_cents = 201; }],
  ])("bloqueia dados inválidos: %s", (_name, mutate) => {
    const data = publicationFixture();
    mutate(data);
    expect(buildScenarioModel(data).valid).toBe(false);
  });
});
