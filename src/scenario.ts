import type { BudgetNode, PublicationData } from "./types";

export type NodeSelectionState = "included" | "partial" | "excluded";

export interface ScenarioModel {
  contextKey: string;
  root: BudgetNode;
  nodesById: Map<string, BudgetNode>;
  childrenByParent: Map<string, BudgetNode[]>;
  descendantLeafIds: Map<string, string[]>;
  leafIds: Set<string>;
}

export type ScenarioModelResult =
  | { valid: true; model: ScenarioModel }
  | { valid: false; errors: string[] };

export interface ScenarioTotals {
  totalCents: number;
  includedCents: number;
  excludedCents: number;
  excludedPercentage: number;
  affectedLeafCount: number;
}

export function scenarioContextKey(data: PublicationData): string {
  return JSON.stringify([
    data.dataset_sha256,
    data.release.release_id,
    data.view.view_id,
    data.view.root_node_id,
  ]);
}

function addSafe(left: number, right: number): number | null {
  const result = left + right;
  return Number.isSafeInteger(result) ? result : null;
}

export function buildScenarioModel(data: PublicationData): ScenarioModelResult {
  const errors: string[] = [];
  const nodesById = new Map<string, BudgetNode>();
  for (const node of data.nodes) {
    if (nodesById.has(node.node_id)) {
      errors.push(`O identificador ${node.node_id} está repetido.`);
    } else {
      nodesById.set(node.node_id, node);
    }
    if (!Number.isSafeInteger(node.amount_cents) || node.amount_cents < 0) {
      errors.push(`A rubrica ${node.node_id} não tem um montante inteiro seguro e não negativo.`);
    }
  }

  const root = nodesById.get(data.view.root_node_id);
  const rootNodes = data.nodes.filter((node) => node.parent_node_id === null);
  if (!root) errors.push("A raiz declarada não existe na árvore.");
  if (root && root.level !== 0) errors.push("A raiz declarada tem de estar no nível zero.");
  if (rootNodes.length !== 1 || rootNodes[0]?.node_id !== data.view.root_node_id) {
    errors.push("A árvore tem de conter exatamente uma raiz, igual à raiz declarada.");
  }

  const childrenByParent = new Map<string, BudgetNode[]>();
  for (const node of data.nodes) {
    if (node.parent_node_id === null) continue;
    const parent = nodesById.get(node.parent_node_id);
    if (!parent) {
      errors.push(`A rubrica ${node.node_id} referencia um pai inexistente.`);
      continue;
    }
    if (node.level !== parent.level + 1) {
      errors.push(`O nível da rubrica ${node.node_id} não é coerente com o pai.`);
    }
    const children = childrenByParent.get(parent.node_id) ?? [];
    children.push(node);
    childrenByParent.set(parent.node_id, children);
  }
  for (const children of childrenByParent.values()) {
    children.sort((left, right) => left.sort_order - right.sort_order || left.node_id.localeCompare(right.node_id));
  }

  for (const [parentId, children] of childrenByParent) {
    let childrenSum = 0;
    let sumIsSafe = true;
    for (const child of children) {
      const next = addSafe(childrenSum, child.amount_cents);
      if (next === null) {
        sumIsSafe = false;
        errors.push(`A soma dos filhos da rubrica ${parentId} excede o intervalo inteiro seguro.`);
        break;
      }
      childrenSum = next;
    }
    const parent = nodesById.get(parentId);
    if (sumIsSafe && parent && childrenSum !== parent.amount_cents) {
      errors.push(`O montante da rubrica ${parentId} não coincide com a soma dos filhos.`);
    }
  }

  for (const node of nodesById.values()) {
    const hasChildren = (childrenByParent.get(node.node_id)?.length ?? 0) > 0;
    if (node.is_terminal === hasChildren) {
      errors.push(`A terminação declarada da rubrica ${node.node_id} não coincide com a estrutura.`);
    }
  }

  const colours = new Map<string, "visiting" | "visited">();
  let cycleFound = false;
  const visit = (nodeId: string) => {
    const colour = colours.get(nodeId);
    if (colour === "visiting") {
      cycleFound = true;
      return;
    }
    if (colour === "visited") return;
    colours.set(nodeId, "visiting");
    for (const child of childrenByParent.get(nodeId) ?? []) visit(child.node_id);
    colours.set(nodeId, "visited");
  };
  for (const nodeId of nodesById.keys()) visit(nodeId);
  if (cycleFound) errors.push("A árvore contém um ciclo.");

  const reachable = new Set<string>();
  const markReachable = (nodeId: string) => {
    if (reachable.has(nodeId)) return;
    reachable.add(nodeId);
    for (const child of childrenByParent.get(nodeId) ?? []) markReachable(child.node_id);
  };
  if (root) markReachable(root.node_id);
  if (reachable.size !== nodesById.size) errors.push("A árvore contém rubricas inacessíveis a partir da raiz.");

  const descendantLeafIds = new Map<string, string[]>();
  const collectLeaves = (nodeId: string, path: Set<string>): string[] => {
    const cached = descendantLeafIds.get(nodeId);
    if (cached) return cached;
    if (path.has(nodeId)) return [];
    const children = childrenByParent.get(nodeId) ?? [];
    if (children.length === 0) {
      const leaves = [nodeId];
      descendantLeafIds.set(nodeId, leaves);
      return leaves;
    }
    const nextPath = new Set(path).add(nodeId);
    const leaves = children.flatMap((child) => collectLeaves(child.node_id, nextPath));
    descendantLeafIds.set(nodeId, leaves);
    return leaves;
  };
  for (const nodeId of nodesById.keys()) collectLeaves(nodeId, new Set());
  const leafIds = new Set(root ? descendantLeafIds.get(root.node_id) ?? [] : []);

  let leafSum = 0;
  for (const leafId of leafIds) {
    const next = addSafe(leafSum, nodesById.get(leafId)!.amount_cents);
    if (next === null) {
      errors.push("A soma das folhas excede o intervalo inteiro seguro.");
      break;
    }
    leafSum = next;
  }
  if (root && leafSum !== root.amount_cents) {
    errors.push("A soma das folhas não coincide com o total da raiz.");
  }

  if (errors.length || !root) return { valid: false, errors: [...new Set(errors)] };
  return {
    valid: true,
    model: {
      contextKey: scenarioContextKey(data),
      root,
      nodesById,
      childrenByParent,
      descendantLeafIds,
      leafIds,
    },
  };
}

function leavesForNode(model: ScenarioModel, nodeId: string): string[] {
  const leaves = model.descendantLeafIds.get(nodeId);
  if (!leaves) throw new Error(`Rubrica desconhecida: ${nodeId}`);
  return leaves;
}

export function nodeSelectionState(
  model: ScenarioModel,
  excludedLeafIds: ReadonlySet<string>,
  nodeId: string,
): NodeSelectionState {
  const leaves = leavesForNode(model, nodeId);
  const excluded = leaves.reduce((count, leafId) => count + Number(excludedLeafIds.has(leafId)), 0);
  if (excluded === 0) return "included";
  return excluded === leaves.length ? "excluded" : "partial";
}

export function setNodeExcluded(
  model: ScenarioModel,
  excludedLeafIds: ReadonlySet<string>,
  nodeId: string,
  excluded: boolean,
): Set<string> {
  const next = new Set(excludedLeafIds);
  for (const leafId of leavesForNode(model, nodeId)) {
    if (excluded) next.add(leafId);
    else next.delete(leafId);
  }
  return next;
}

export function calculateScenario(model: ScenarioModel, excludedLeafIds: ReadonlySet<string>): ScenarioTotals {
  let excludedCents = 0;
  for (const leafId of excludedLeafIds) {
    if (!model.leafIds.has(leafId)) throw new Error(`A seleção contém uma rubrica não terminal: ${leafId}`);
    const next = addSafe(excludedCents, model.nodesById.get(leafId)!.amount_cents);
    if (next === null) throw new Error("O total excluído excede o intervalo inteiro seguro.");
    excludedCents = next;
  }
  const includedCents = model.root.amount_cents - excludedCents;
  if (includedCents < 0 || includedCents + excludedCents !== model.root.amount_cents) {
    throw new Error("O cenário deixou de reconciliar com o total de referência.");
  }
  return {
    totalCents: model.root.amount_cents,
    includedCents,
    excludedCents,
    excludedPercentage: model.root.amount_cents === 0 ? 0 : excludedCents / model.root.amount_cents,
    affectedLeafCount: excludedLeafIds.size,
  };
}

export function resetScenario(): Set<string> {
  return new Set();
}

export function reconcileScenarioContext(
  previousContextKey: string,
  nextContextKey: string,
  excludedLeafIds: ReadonlySet<string>,
): { excludedLeafIds: Set<string>; cleared: boolean } {
  if (previousContextKey === nextContextKey) {
    return { excludedLeafIds: new Set(excludedLeafIds), cleared: false };
  }
  return { excludedLeafIds: resetScenario(), cleared: excludedLeafIds.size > 0 };
}
