import type { PublicationData } from "./types";

export const DATA_URL = `${import.meta.env.BASE_URL}data/current.json`;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isSafeNonNegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isSafeInteger(value) && value >= 0;
}

function hasStringFields(value: Record<string, unknown>, fields: string[]): boolean {
  return fields.every((field) => isNonEmptyString(value[field]));
}

export function parsePublicationData(value: unknown): PublicationData {
  if (!isRecord(value) || !isRecord(value.release) || !isRecord(value.view)) {
    throw new Error("O pacote publicado não tem a estrutura esperada.");
  }
  if (value.schema_version !== 2) {
    throw new Error("A versão do pacote publicado não é suportada.");
  }
  if (!Array.isArray(value.nodes) || !Array.isArray(value.sources)) {
    throw new Error("O pacote publicado não contém nós e fontes válidos.");
  }
  if (typeof value.dataset_sha256 !== "string" || value.dataset_sha256.length !== 64) {
    throw new Error("O pacote publicado não identifica a versão dos dados.");
  }
  if (
    !isSafeNonNegativeInteger(value.release.year)
    || value.release.phase !== "approved_initial"
    || !hasStringFields(value.release, ["release_id", "publication"])
    || !hasStringFields(value.view, ["view_id", "official_name", "root_node_id"])
    || value.view.dimension !== "programmatic"
    || typeof value.view.selectable !== "boolean"
    || !isRecord(value.view.coverage)
  ) {
    throw new Error("O pacote publicado não declara o ano ou o total de referência.");
  }
  const coverageFields = [
    "institutional_universe", "social_security", "consolidation", "measure",
    "accounting_classification", "gross_net", "currency", "unit",
  ];
  if (!hasStringFields(value.view.coverage, coverageFields) || value.view.coverage.currency !== "EUR" || value.view.coverage.unit !== "cents") {
    throw new Error("O pacote publicado não declara um âmbito válido.");
  }
  for (const node of value.nodes) {
    if (
      !isRecord(node)
      || !hasStringFields(node, ["node_id", "official_label"])
      || (node.official_code !== null && typeof node.official_code !== "string")
      || !isSafeNonNegativeInteger(node.amount_cents)
      || !isSafeNonNegativeInteger(node.level)
      || (node.parent_node_id !== null && !isNonEmptyString(node.parent_node_id))
      || !isSafeNonNegativeInteger(node.sort_order)
      || typeof node.is_terminal !== "boolean"
      || !Array.isArray(node.factual_tags)
      || node.factual_tags.some((tag) => !isNonEmptyString(tag))
      || !isRecord(node.source)
      || !hasStringFields(node.source, ["source_id", "locator"])
    ) {
      throw new Error("O pacote publicado contém uma rubrica inválida.");
    }
  }
  for (const source of value.sources) {
    if (!isRecord(source) || !hasStringFields(source, ["source_id", "publisher", "title", "url", "coverage", "reuse_terms"])) {
      throw new Error("O pacote publicado contém uma fonte inválida.");
    }
  }
  if (
    value.demo !== undefined
    && (!isRecord(value.demo) || value.demo.mode !== "personal_local" || !isNonEmptyString(value.demo.notice))
  ) {
    throw new Error("O pacote de demonstração não declara as suas limitações.");
  }
  return value as unknown as PublicationData;
}

export async function loadPublicationData(signal?: AbortSignal): Promise<PublicationData> {
  const response = await fetch(DATA_URL, {
    signal,
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Não foi possível carregar os dados publicados (HTTP ${response.status}).`);
  }
  return parsePublicationData(await response.json());
}
