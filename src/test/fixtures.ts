import type { PublicationData } from "../types";

export function publicationFixture(): PublicationData {
  const rootId = "release:view:root";
  return {
    schema_version: 1,
    dataset_sha256: "a".repeat(64),
    release: { release_id: "release", year: 2026, phase: "approved_initial", publication: "Lei" },
    view: {
      view_id: "view",
      official_name: "Mapa 1",
      dimension: "programmatic",
      root_node_id: rootId,
      coverage: {
        institutional_universe: "administracao_central",
        social_security: "excluded",
        consolidation: "non_consolidated",
        measure: "budgeted_expenditure",
        accounting_classification: "mapa",
        gross_net: "not_declared_by_source",
        currency: "EUR",
        unit: "cents",
      },
    },
    nodes: [
      {
        node_id: rootId,
        official_code: null,
        official_label: "Total da Administração Central",
        amount_cents: 100_000,
        level: 0,
        parent_node_id: null,
        sort_order: 0,
        source: { source_id: "pdf", locator: "página 1" },
      },
      {
        node_id: "release:view:P-001",
        official_code: "P-001",
        official_label: "Saúde",
        amount_cents: 25_000,
        level: 1,
        parent_node_id: rootId,
        sort_order: 1,
        source: { source_id: "xml", locator: "/Mapa1/Registo[1]" },
      },
    ],
    sources: [
      { source_id: "pdf", publisher: "Entidade oficial", title: "Mapa PDF", url: "https://dados.gov.pt/mapa.pdf", coverage: "Total", reuse_terms: "public_domain" },
      { source_id: "xml", publisher: "Entidade oficial", title: "Mapa XML", url: "https://dados.gov.pt/mapa.xml", coverage: "Programas", reuse_terms: "public_domain" },
    ],
  };
}
