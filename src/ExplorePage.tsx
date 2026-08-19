import { useMemo, useState } from "react";
import { EmptyState, ErrorState, LoadingState } from "./components/DataStates";
import { Shell } from "./components/Shell";
import { SourceLink } from "./components/SourceLink";
import { formatEuros, formatPercentage } from "./format";
import type { BudgetNode, PublicationData } from "./types";
import { usePublicationData } from "./usePublicationData";

function normalize(value: string) {
  return value.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLocaleLowerCase("pt-PT");
}

function nodePath(node: BudgetNode, nodes: Map<string, BudgetNode>) {
  const path: BudgetNode[] = [];
  let current: BudgetNode | undefined = node;
  while (current) {
    path.unshift(current);
    current = current.parent_node_id ? nodes.get(current.parent_node_id) : undefined;
  }
  return path;
}

function TreeNode({ node, childrenByParent, selectedId, expanded, onSelect, onToggle }: {
  node: BudgetNode;
  childrenByParent: Map<string, BudgetNode[]>;
  selectedId: string;
  expanded: Set<string>;
  onSelect: (nodeId: string) => void;
  onToggle: (nodeId: string) => void;
}) {
  const children = childrenByParent.get(node.node_id) ?? [];
  const hasChildren = children.length > 0;
  const isExpanded = expanded.has(node.node_id);
  return (
    <li>
      <div className="tree-row">
        {hasChildren ? <button className="tree-toggle" type="button" onClick={() => onToggle(node.node_id)} aria-label={`${isExpanded ? "Colapsar" : "Expandir"} ${node.official_label}`}>{isExpanded ? "−" : "+"}</button> : <span className="tree-spacer" aria-hidden="true" />}
        <button className="tree-node" type="button" aria-current={selectedId === node.node_id ? "true" : undefined} onClick={() => onSelect(node.node_id)}>
          <span>{node.official_code ? `${node.official_code} — ` : ""}{node.official_label}</span><strong>{formatEuros(node.amount_cents)}</strong>
        </button>
      </div>
      {hasChildren && isExpanded ? <ul>{children.map((child) => <TreeNode key={child.node_id} node={child} childrenByParent={childrenByParent} selectedId={selectedId} expanded={expanded} onSelect={onSelect} onToggle={onToggle} />)}</ul> : null}
    </li>
  );
}

function Explorer({ data }: { data: PublicationData }) {
  const root = data.nodes.find((node) => node.node_id === data.view.root_node_id);
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(data.view.root_node_id);
  const [expanded, setExpanded] = useState(() => new Set([data.view.root_node_id]));
  const nodes = useMemo(() => new Map(data.nodes.map((node) => [node.node_id, node])), [data.nodes]);
  const childrenByParent = useMemo(() => {
    const index = new Map<string, BudgetNode[]>();
    for (const node of data.nodes) {
      if (!node.parent_node_id) continue;
      const children = index.get(node.parent_node_id) ?? [];
      children.push(node);
      index.set(node.parent_node_id, children);
    }
    for (const children of index.values()) children.sort((left, right) => left.sort_order - right.sort_order);
    return index;
  }, [data.nodes]);
  const selected = nodes.get(selectedId) ?? root;
  const matches = useMemo(() => {
    const term = normalize(query.trim());
    return term ? data.nodes.filter((node) => normalize(`${node.official_code ?? ""} ${node.official_label}`).includes(term)) : [];
  }, [data.nodes, query]);
  const source = selected ? data.sources.find((entry) => entry.source_id === selected.source.source_id) : undefined;
  const parent = selected?.parent_node_id ? nodes.get(selected.parent_node_id) : undefined;
  const path = selected ? nodePath(selected, nodes) : [];
  if (!root || !selected) return <EmptyState />;
  return (
    <div className="content-width page-content explorer-layout">
      <section className="explorer-main" aria-labelledby="tree-title">
        <div className="explorer-intro"><div><p className="section-label">Vista canónica</p><h2 id="tree-title">Programas do Mapa 1</h2></div><p>Expanda uma área e escolha uma rubrica para consultar o valor, o caminho e a fonte.</p></div>
        <label className="search-field" htmlFor="pesquisa-rubrica"><span>Procurar por código ou designação oficial</span><input id="pesquisa-rubrica" value={query} onChange={(event) => setQuery(event.target.value)} type="search" placeholder="Ex.: P-001 ou Saúde" /></label>
        {query.trim() ? <section className="search-results" aria-live="polite" aria-label="Resultados da pesquisa"><p><strong>{matches.length}</strong> resultados para “{query.trim()}”.</p>{matches.length ? <ul>{matches.map((node) => <li key={node.node_id}><button type="button" onClick={() => setSelectedId(node.node_id)}>{node.official_code ? `${node.official_code} — ` : ""}{node.official_label}<span>{formatEuros(node.amount_cents)}</span></button></li>)}</ul> : <p>Nenhuma rubrica corresponde à pesquisa. Tente o código oficial ou outra palavra da designação.</p>}</section> : null}
        <p className="filter-note" role="note">Não existem filtros adicionais nesta vista: não misturamos classificações programática, económica, funcional ou orgânica.</p>
        <ul className="budget-tree" aria-label="Árvore orçamental por programas"><TreeNode node={root} childrenByParent={childrenByParent} selectedId={selected.node_id} expanded={expanded} onSelect={setSelectedId} onToggle={(nodeId) => setExpanded((current) => { const next = new Set(current); next.has(nodeId) ? next.delete(nodeId) : next.add(nodeId); return next; })} /></ul>
      </section>
      <aside className="detail-card" aria-labelledby="detail-title">
        <p className="section-label">Ficha da rubrica</p><h2 id="detail-title">{selected.official_label}</h2>
        {selected.official_code ? <p className="detail-code">Código oficial: <code>{selected.official_code}</code></p> : <p className="detail-code">A fonte não declara código oficial para o total.</p>}
        <p className="detail-value">{formatEuros(selected.amount_cents)}</p>
        <dl className="detail-list"><div><dt>Do total</dt><dd>{formatPercentage(selected.amount_cents, root.amount_cents)}</dd></div><div><dt>Do pai</dt><dd>{parent ? formatPercentage(selected.amount_cents, parent.amount_cents) : "—"}</dd></div><div><dt>Classificação</dt><dd>Programática — Mapa 1</dd></div><div><dt>Atualização</dt><dd>{data.release.publication}; não é fornecida uma data de atualização pela fonte.</dd></div></dl>
        <h3>Caminho</h3><ol className="breadcrumb-list">{path.map((node) => <li key={node.node_id}>{node.official_label}</li>)}</ol>
        <h3>Âmbito e limitações</h3><p>Despesa orçamentada da Administração Central não consolidada. Não representa execução, poupança nem o total da Segurança Social.</p>
        {source ? <SourceLink source={source} locator={selected.source.locator} /> : <p className="source-missing">A fonte desta rubrica não está declarada no pacote.</p>}
      </aside>
    </div>
  );
}

export function ExplorePage() {
  const state = usePublicationData();
  const data = state.status === "ready" ? state.data : undefined;
  return <Shell currentPage="explore" data={data} title="Explorar as rubricas sem perder o contexto" intro={<p>Uma árvore programática com pesquisa por designação e código oficiais, valores e fontes rastreáveis.</p>}>
    {state.status === "loading" ? <div className="content-width page-content"><LoadingState /></div> : null}
    {state.status === "error" ? <div className="content-width page-content"><ErrorState message={state.error} onRetry={state.retry} /></div> : null}
    {state.status === "ready" && data ? <Explorer data={data} /> : null}
  </Shell>;
}
