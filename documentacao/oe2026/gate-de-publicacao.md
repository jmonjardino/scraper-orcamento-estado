# Gate de publicação e revisão humana — OE 2026

## Estado em 2026-09-18

O conjunto candidato está tecnicamente reconciliado, mas continua bloqueado para redistribuição e seleção pública. A página oficial da Entidade Orçamental identifica os documentos do OE 2026 e remete para o portal Dados.gov.pt para conjuntos reutilizáveis. Contudo, a página também apresenta “todos os direitos reservados” e não foi localizado um registo OE 2026 específico que associe uma licença aos cinco recursos usados por este conjunto.

Consequentemente, `reuse_terms` mantém-se `unresolved`. Os termos gerais do Dados.gov.pt não são evidência suficiente para alterar este estado: a licença tem de ser atribuível ao recurso exato.

## Evidência obrigatória de reutilização

Para cada artefacto que deixe de estar `unresolved`, adicionar em `config/fontes-oe2026.json`:

```json
"reuse_terms": "CC-BY-4.0",
"reuse_evidence": {
  "resource_url": "https://url-exata-do-recurso-usado",
  "license_url": "https://pagina-oficial-que-declara-a-licenca",
  "checked_at": "2026-09-18T14:00:00Z",
  "statement": "Resumo factual da licença declarada para este recurso."
}
```

O gate verifica HTTPS, data ISO 8601, declaração não vazia e que `resource_url` coincide exatamente com `artifact.url`. Uma licença geral, uma página de pesquisa ou uma inferência a partir da entidade publicadora não passa este controlo.

## Revisão humana do simulador

Depois de todos os termos estarem resolvidos, realizar duas sessões no mesmo SHA do conjunto: uma com uma pessoa de contabilidade pública e outra com uma pessoa não especialista. Registar nome/função, data, SHA, ambiente, tarefas, resultado e alterações pedidas.

As tarefas mínimas são:

1. Explicar, antes de selecionar, ano, fase, universo, não consolidação e exclusão da Segurança Social.
2. Excluir uma rubrica e explicar a diferença entre montante excluído e poupança realizável.
3. Identificar as limitações e restrições factuais sem concluir que ausência de etiqueta torna a rubrica eliminável.
4. Usar expansão, seleção parcial e reposição apenas com teclado.
5. Confirmar que a igualdade ao cêntimo é uma reconciliação matemática, não uma aprovação legal, política ou operacional.

Uma aprovação só pode ser criada depois desta revisão e deve identificar o SHA, `release_id`, `view_id`, revisor e data. Não criar nem preencher `config/aprovacoes/oe-2026-approved-initial.json` até existir uma decisão humana real.

## Ordem de passagem

1. Resolver a licença de cada fonte usada e registar a evidência acima.
2. Reexecutar normalização e validação, gerando/confirmando o SHA e o relatório.
3. Remover apenas blockers efetivamente resolvidos, rever `publication_eligible` e decidir `selectable`.
4. Fazer a revisão humana no SHA final e criar a aprovação vinculada.
5. Executar `npm run build:release`; só um resultado bem-sucedido autoriza preparar uma publicação. Deploy continua uma decisão separada.
