export interface SourceReference {
  source_id: string;
  locator: string;
}

export interface BudgetNode {
  node_id: string;
  official_code: string | null;
  official_label: string;
  amount_cents: number;
  level: number;
  parent_node_id: string | null;
  sort_order: number;
  source: SourceReference;
}

export interface PublishedSource {
  source_id: string;
  publisher: string;
  title: string;
  url: string;
  coverage: string;
  reuse_terms: string;
}

export interface PublicationData {
  schema_version: number;
  dataset_sha256: string;
  release: {
    release_id: string;
    year: number;
    phase: "approved_initial";
    publication: string;
  };
  view: {
    view_id: string;
    official_name: string;
    dimension: "programmatic";
    root_node_id: string;
    coverage: {
      institutional_universe: string;
      social_security: string;
      consolidation: string;
      measure: string;
      accounting_classification: string;
      gross_net: string;
      currency: "EUR";
      unit: "cents";
    };
  };
  nodes: BudgetNode[];
  sources: PublishedSource[];
}
