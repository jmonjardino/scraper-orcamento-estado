import { useEffect, useMemo, useRef, useState } from "react";
import { ErrorState, LoadingState } from "./components/DataStates";
import { Shell } from "./components/Shell";
import { formatEurosExact, formatPercentage } from "./format";
import {
  buildScenarioModel,
  calculateScenario,
  nodeSelectionState,
  resetScenario,
  setNodeExcluded,
  type NodeSelectionState,
  type ScenarioModel,
} from "./scenario";
import type { BudgetNode, PublicationData } from "./types";
import { usePublicationData } from "./usePublicationData";

const EMPTY_SELECTION = new Set<string>();

function ResponsibleNotice() {
  return (
    <aside className="scenario-warning" aria-labelledby="scenario-warning-title">
      <span className="notice-icon" aria-hidden="true">!</span>
      <div>
        <p className="section-label">Uso responsável</p>
        <h2 id="scenario-warning-title">Este é um cenário de montantes</h2>
        <p>
          Excluir uma rubrica neste simulador não significa que o montante seja uma poupança garantida ou realizável.
          Obrigações legais, compromissos, efeitos indiretos e custos de transição podem impedir ou alterar o resultado.
        </p>
      </div>
    </aside>
  );
}

function coverageLabel(value: string, labels: Record<string, string>): string {
  return labels[value] ?? value.replaceAll("_", " ");
}

function ContextPanel({ data }: { data: PublicationData }) {
  const taggedNodes = data.nodes.filter((node) => node.factual_tags.length > 0);
  return (
    <section className="scenario-context" aria-labelledby="scenario-context-title">
      <p className="section-label">Contexto factual</p>
      <h2 id="scenario-context-title">O que está a ser simulado</h2>
      <dl className="scenario-context-grid">
        <div><dt>Fase</dt><dd>OE aprovado — {data.release.publication}</dd></div>
        <div><dt>Universo</dt><dd>{coverageLabel(data.view.coverage.institutional_universe, { administracao_central: "Administração Central" })}</dd></div>
        <div><dt>Segurança Social</dt><dd>{coverageLabel(data.view.coverage.social_security, { excluded: "Excluída enquanto subsistema autónomo" })}</dd></div>
        <div><dt>Consolidação</dt><dd>{coverageLabel(data.view.coverage.consolidation, { non_consolidated: "Não consolidado" })}</dd></div>
        <div><dt>Medida</dt><dd>{coverageLabel(data.view.coverage.measure, { budgeted_expenditure: "Despesa orçamentada, não execução" })}</dd></div>
        <div><dt>Classificação</dt><dd>Programática — {data.view.official_name}</dd></div>
      </dl>
      <div className="factual-restrictions">
        <h3>Restrições factuais declaradas</h3>
        {taggedNodes.length > 0 ? (
          <ul>
            {taggedNodes.flatMap((node) => node.factual_tags.map((tag) => (
              <li key={`${node.node_id}:${tag}`}><strong>{node.official_label}:</strong> {tag}</li>
            )))}
          </ul>
        ) : (
          <p role="note">
            O pacote não declara etiquetas factuais adicionais. Esta ausência não significa que uma rubrica seja
            eliminável ou que o respetivo montante possa ser poupado.
          </p>
        )}
      </div>
      <p className="perspective-note" role="note">
        Este cenário usa apenas a perspetiva programática do Mapa 1. Não mistura classificações funcional,
        económica ou orgânica e não existe outra perspetiva selecionável neste pacote.
      </p>
    </section>
  );
}

function ExclusionCheckbox({ node, state, onChange }: {
  node: BudgetNode;
  state: NodeSelectionState;
  onChange: (excluded: boolean) => void;
}) {
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (input.current) input.current.indeterminate = state === "partial";
  }, [state]);
  return (
    <label className="scenario-checkbox">
      <input
        ref={input}
        type="checkbox"
        checked={state === "excluded"}
        onChange={(event) => onChange(event.target.checked)}
      />
      <span>Excluir {node.official_label}</span>
    </label>
  );
}

function ScenarioTreeNode({ node, model, excludedLeafIds, expanded, onToggle, onExclude }: {
  node: BudgetNode;
  model: ScenarioModel;
  excludedLeafIds: ReadonlySet<string>;
  expanded: ReadonlySet<string>;
  onToggle: (nodeId: string) => void;
  onExclude: (nodeId: string, excluded: boolean) => void;
}) {
  const children = model.childrenByParent.get(node.node_id) ?? [];
  const hasChildren = children.length > 0;
  const isExpanded = expanded.has(node.node_id);
  const selection = nodeSelectionState(model, excludedLeafIds, node.node_id);
  return (
    <li>
      <div className="scenario-tree-row">
        {hasChildren ? (
          <button
            className="tree-toggle"
            type="button"
            aria-expanded={isExpanded}
            aria-label={`${isExpanded ? "Colapsar" : "Expandir"} ${node.official_label}`}
            onClick={() => onToggle(node.node_id)}
          >{isExpanded ? "−" : "+"}</button>
        ) : <span className="tree-spacer" aria-hidden="true" />}
        <div className="scenario-node-summary">
          <span className="scenario-node-name">{node.official_code ? `${node.official_code} — ` : ""}{node.official_label}</span>
          <strong>{formatEurosExact(node.amount_cents)}</strong>
          {node.factual_tags.length > 0 ? <ul className="node-tags">{node.factual_tags.map((tag) => <li key={tag}>{tag}</li>)}</ul> : null}
        </div>
        <ExclusionCheckbox node={node} state={selection} onChange={(excluded) => onExclude(node.node_id, excluded)} />
      </div>
      {hasChildren && isExpanded ? (
        <ul>
          {children.map((child) => (
            <ScenarioTreeNode
              key={child.node_id}
              node={child}
              model={model}
              excludedLeafIds={excludedLeafIds}
              expanded={expanded}
              onToggle={onToggle}
              onExclude={onExclude}
            />
          ))}
        </ul>
      ) : null}
    </li>
  );
}

function IntegrityBlocked({ errors }: { errors: string[] }) {
  return (
    <section className="state-card state-error scenario-blocked" role="alert">
      <span className="state-icon" aria-hidden="true">!</span>
      <div>
        <h2>Simulador bloqueado por integridade</h2>
        <p>Não é feito qualquer ajuste nem cálculo com uma árvore que não reconcilia.</p>
        <ul>{errors.map((error) => <li key={error}>{error}</li>)}</ul>
      </div>
    </section>
  );
}

function SelectionBlocked() {
  return (
    <section className="state-card state-empty scenario-blocked" role="status">
      <span className="state-icon" aria-hidden="true">i</span>
      <div>
        <h2>Simulador indisponível para esta vista</h2>
        <p>
          Esta vista ainda não está autorizada para criar cenários. Esta salvaguarda mantém as ações indisponíveis
          até as rubricas serem revistas e aprovadas para seleção.
        </p>
      </div>
    </section>
  );
}

export function Simulator({ data }: { data: PublicationData }) {
  const result = useMemo(() => buildScenarioModel(data), [data]);
  if (!result.valid) return <IntegrityBlocked errors={result.errors} />;
  if (!data.view.selectable) return <SelectionBlocked />;
  return <ReadySimulator data={data} model={result.model} />;
}

function ReadySimulator({ data, model }: { data: PublicationData; model: ScenarioModel }) {
  const [excludedLeafIds, setExcludedLeafIds] = useState<Set<string>>(() => new Set());
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set([model.root.node_id]));
  const [announcement, setAnnouncement] = useState("Cenário inicial: nenhuma rubrica excluída.");
  const contextRef = useRef(model.contextKey);
  const contextChanged = contextRef.current !== model.contextKey;
  const activeExcludedLeafIds = contextChanged ? EMPTY_SELECTION : excludedLeafIds;

  useEffect(() => {
    if (contextRef.current === model.contextKey) return;
    contextRef.current = model.contextKey;
    setExcludedLeafIds(new Set());
    setExpanded(new Set([model.root.node_id]));
    setAnnouncement("O contexto dos dados mudou. A seleção anterior foi limpa e o cenário foi reiniciado.");
  }, [model.contextKey, model.root.node_id]);

  const totals = calculateScenario(model, activeExcludedLeafIds);
  const updateNode = (nodeId: string, excluded: boolean) => {
    const next = setNodeExcluded(model, activeExcludedLeafIds, nodeId, excluded);
    const nextTotals = calculateScenario(model, next);
    setExcludedLeafIds(next);
    setAnnouncement(
      `${nextTotals.affectedLeafCount} rubricas terminais afetadas; montante excluído ${formatEurosExact(nextTotals.excludedCents)}.`,
    );
  };
  const reset = () => {
    setExcludedLeafIds(resetScenario());
    setAnnouncement("Cenário reposto: nenhuma rubrica excluída.");
  };
  return (
    <>
      <ContextPanel data={data} />
      <div className="scenario-layout">
        <section className="scenario-tree-card" aria-labelledby="scenario-tree-title">
          <p className="section-label">Seleção hierárquica</p>
          <h2 id="scenario-tree-title">Rubricas do cenário</h2>
          <p>Excluir um pai exclui todas as folhas descendentes. Um estado parcial indica que apenas algumas estão excluídas.</p>
          <ul className="scenario-tree" aria-label="Árvore de rubricas para o cenário">
            <ScenarioTreeNode
              node={model.root}
              model={model}
              excludedLeafIds={activeExcludedLeafIds}
              expanded={expanded}
              onToggle={(nodeId) => setExpanded((current) => {
                const next = new Set(current);
                if (next.has(nodeId)) next.delete(nodeId); else next.add(nodeId);
                return next;
              })}
              onExclude={updateNode}
            />
          </ul>
        </section>
        <aside className="scenario-results" aria-labelledby="scenario-results-title">
          <p className="section-label">Resultado do cenário</p>
          <h2 id="scenario-results-title">Resumo</h2>
          <dl>
            <div><dt>Montante incluído</dt><dd>{formatEurosExact(totals.includedCents)}</dd></div>
            <div><dt>Montante excluído</dt><dd>{formatEurosExact(totals.excludedCents)}</dd></div>
            <div><dt>Percentagem excluída</dt><dd>{formatPercentage(totals.excludedCents, totals.totalCents)}</dd></div>
            <div><dt>Rubricas terminais afetadas</dt><dd>{totals.affectedLeafCount}</dd></div>
          </dl>
          <p className="scenario-equation">
            <strong>Reconciliação exata</strong><br />
            {formatEurosExact(totals.includedCents)} + {formatEurosExact(totals.excludedCents)} = {formatEurosExact(totals.totalCents)}
          </p>
          <button type="button" disabled={activeExcludedLeafIds.size === 0} onClick={reset}>Repor cenário</button>
          <p className="visually-hidden" role="status" aria-live="polite" aria-atomic="true">{announcement}</p>
        </aside>
      </div>
    </>
  );
}

export function SimulatorPage() {
  const state = usePublicationData();
  const data = state.status === "ready" ? state.data : undefined;
  return (
    <Shell
      currentPage="simulate"
      data={data}
      title="Simular exclusões com responsabilidade"
      intro={<p>Crie um cenário reversível numa única perspetiva, sempre reconciliado com o total publicado.</p>}
    >
      <div className="content-width page-content simulator-page">
        <ResponsibleNotice />
        {state.status === "loading" ? <LoadingState /> : null}
        {state.status === "error" ? <ErrorState message={state.error} onRetry={state.retry} /> : null}
        {state.status === "ready" && data ? <Simulator data={data} /> : null}
      </div>
    </Shell>
  );
}
