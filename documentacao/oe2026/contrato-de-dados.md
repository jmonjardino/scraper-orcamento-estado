# Contrato de dados — OE 2026

## Contrato v0 — bloqueado para publicação

| Campo | Valor |
|---|---|
| `year` | `2026` |
| `phase` | `approved_initial` |
| `publication` | Lei n.º 73-A/2025, de 30 de dezembro |
| `measure` | `budgeted_expenditure` |
| `currency` | `EUR` |
| `release_status` | `blocked_pending_reuse_terms_and_full_gate_review` |
| `canonical_view_id` | `administracao_central_nao_consolidada_por_programa` (candidata validada tecnicamente) |

Ficam fora deste MVP: receitas, execução, alterações posteriores, comparação anual, cálculo de défice/dívida/impostos, regiões e autarquias (salvo perímetro oficialmente inseparável e explicitamente aprovado).

Uma corrigenda ou substituição oficial cria uma nova `release_id`; nunca altera silenciosamente um conjunto já publicado.

## Campos ainda não resolvidos

Não podem ter valor `unknown` num release validado: universo institucional, tratamento da Segurança Social, consolidação, ótica contabilística, natureza bruta/líquida, total de referência compatível, árvore canónica e termos de reutilização. A ausência de qualquer um bloqueia publicação e seleção. A candidata atual resolve tecnicamente a vista e o total, mas os termos de reutilização continuam por confirmar.

## Candidata tecnicamente reconciliada

- Vista: programas da Administração Central, não consolidada.
- Raiz oficial: `Total da Administração Central` = **352 472 389 960 €**.
- Filhos: 20 programas do `Mapa1-2026.xml`; total das folhas = **352 472 389 960 €**; delta = **0 €**.
- Proveniência das folhas: XML, `Mapa1/Registos/Registo`, com código, designação, ministério e `TotalEmEuros`.
- Proveniência da raiz: `oe2026-mapa1-pdf`, página 1, `Total da Administração Central`.

Esta vista não representa o total Administração Central + Segurança Social, nem o total consolidado. O campo Ministério é uma propriedade de cada programa, não uma relação pai inferida.

## Regras de cálculo

- Perspetivas `programmatic`, `functional`, `economic` e `organic` são vistas independentes; a Segurança Social é um perímetro/subsistema, não uma dimensão automaticamente equivalente.
- Um cálculo futuro exige `release_id + view_id + root_node_id`.
- Trocar de vista limpa a seleção após aviso.
- Só folhas elegíveis participam em somas; um pai e os seus descendentes nunca são somados em duplicado.
- O total oficial, soma de folhas e delta são campos separados. Nunca criar uma rubrica artificial de ajuste.
- Valores internos futuros usam cêntimos inteiros (ou decimal exato antes da conversão); arredondar apenas na apresentação.

## Dicionário lógico mínimo

| Registo | Campos essenciais |
|---|---|
| `budget_release` | `release_id`, versão do contrato, ano, fase, publicação, âmbitos, moeda, vista canónica, estado |
| `source_artifact` | editor, título, URL, formato, data, recolha, hash, tamanho, MIME, unidade, cobertura, termos de reutilização |
| `budget_view` | release, dimensão, nome oficial, raiz, cobertura, total de referência, selecionável |
| `budget_node` | vista, código e designação oficiais, pai, nível, ordem, cêntimos, origem, unidade, terminal |
| `provenance` | artefacto com hash, locator, valor/unidade brutos, transformação, `reported`/`derived` e entradas derivadas |
| `reference_total` | total oficial, soma das folhas, delta, locator e estado |
| `ambiguity` | âmbito afetado, evidência, impacto, resolução e se bloqueia release |

Proveniência por formato: XML usa XPath/identificador e campo; XLSX usa folha/range/chave/coluna; CSV usa chave/coluna; PDF usa página/tabela/linha/coluna e excerto curto de controlo.
