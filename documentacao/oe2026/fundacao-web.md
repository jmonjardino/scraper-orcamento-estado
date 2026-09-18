# Fundação web e gate de publicação — OE 2026

## Decisão de stack

A interface é uma aplicação multipágina estática com Vite, React e TypeScript, estilizada com CSS nativo. Há quatro documentos HTML reais: o resumo em `/`, a exploração em `/explorar/`, o simulador em `/simulador/` e a metodologia em `/metodologia/`.

A escolha responde aos requisitos desta fase:

- o alojamento só precisa de servir ficheiros estáticos;
- React permite reutilizar shell, estados e cartões nas fases seguintes;
- TypeScript fixa o contrato consumido pela interface;
- CSS nativo evita uma dependência visual e mantém os tokens explícitos;
- a configuração MPA mantém cada URL navegável sem depender de routing no servidor.

## Separação entre UI e dados

`npm run build:ui` compila apenas a interface. O modo `ui` do Vite não tem `publicDir`, por isso não transporta o conjunto normalizado, o relatório nem um pacote anteriormente gerado. Em execução, a aplicação faz um único pedido de dados para `/data/current.json`; links para documentos oficiais são navegação iniciada pela pessoa, não pedidos automáticos da aplicação.

Enquanto não existir um pacote, a página apresenta uma falha explicada e o botão “Tentar novamente”. Existem também estados distintos de carregamento e de pacote vazio. O resumo, cartões e ligações às fontes só aparecem no estado pronto.

## Demonstração pessoal local

`npm run build:demo` é uma via separada para experimentar localmente a aplicação com o conjunto real tecnicamente validado. Valida a identidade do conjunto, o relatório e todas as reconciliações, mas não substitui o gate de publicação: não aceita termos de reutilização como resolvidos, não requer aprovação humana e não produz uma release destinada a alojamento público. O payload inclui uma marca permanente de demonstração pessoal local.

A EO anunciou a disponibilização dos dados OE 2026 nos formatos abertos do Dados.gov. Os termos gerais desse portal preveem CC BY 4.0 para dados carregados por organismos do Estado salvo indicação em contrário. Esta informação não é aplicada retroativamente aos ficheiros diretos da EO no catálogo: a URL e licença do recurso OE 2026 concreto continuam obrigatórias antes de distribuição pública.

## Gate do pacote publicável

`ferramentas/preparar_publicacao_web.py` recebe quatro entradas:

1. conjunto normalizado;
2. relatório de validação correspondente;
3. catálogo de fontes;
4. aprovação humana correspondente ao mesmo SHA, release e vista.

O comando recusa publicar quando qualquer uma destas condições não se verifica:

- SHA-256, `release_id`, `view_id`, ano, fase ou publicação não coincidem;
- `validation_status` não é `validated` ou as regras críticas não passaram;
- falta uma reconciliação, ou alguma reconciliação não passou;
- há bloqueios no relatório ou no conjunto;
- `publication_eligible` não é exatamente `true`;
- `selectable`, `is_terminal` ou `factual_tags` não têm os tipos exigidos pelo contrato público;
- uma fonte não usa HTTPS num domínio oficial aprovado, falta no catálogo ou tem termos por resolver;
- uma fonte com termos resolvidos não contém evidência do recurso exato, URL da licença, data de verificação e declaração registada;
- a aprovação humana falta, não diz `approved`, não identifica pessoa/data ou aponta para outro SHA/release/vista.

A aprovação tem esta estrutura mínima (o ficheiro real só deve ser criado após a revisão):

```json
{
  "schema_version": 1,
  "decision": "approved",
  "dataset_sha256": "<sha256-do-conjunto-revisto>",
  "release_id": "oe-2026-approved-initial",
  "view_id": "administracao_central_nao_consolidada_por_programa",
  "approved_by": "<identidade da pessoa revisora>",
  "approved_at": "<data/hora ISO 8601>"
}
```

Quando passa, o empacotador escreve JSON canónico e determinista em:

- `.generated/public/data/current.json`;
- `.generated/public/data/releases/<dataset_sha256>.json`.

Os dois ficheiros contêm o mesmo envelope público reduzido, na versão 2: metadados de release/vista, `view.selectable`, nós com `is_terminal` e `factual_tags`, e fontes enriquecidas com URL. Não incluem o relatório, a aprovação, o catálogo completo nem campos internos do normalizador. Só então `build:release` executa typecheck e Vite no modo que copia `.generated/public`.

## Estado do OE 2026

O conjunto está tecnicamente validado e as duas reconciliações têm diferença zero. A publicação continua bloqueada por termos de reutilização não resolvidos, bloqueios declarados no conjunto, `publication_eligible: false` e ausência de aprovação humana. Este é um resultado esperado: `npm run build:release` termina antes do Vite e enumera as razões.

## Acessibilidade e responsividade

O shell tem link para saltar conteúdo, `header`, navegação identificada, `main`, secções tituladas, `aside` e `footer`. A navegação e o retry usam elementos nativos de teclado; o erro recebe foco quando surge; loading usa `aria-busy`; erros e vazio têm texto e símbolos além da cor; `:focus-visible` tem destaque forte; movimento respeita `prefers-reduced-motion`.

Os layouts passam de três para duas e uma coluna, a navegação reorganiza-se em ecrãs estreitos e valores/texto podem quebrar sem scroll horizontal intencional. A validação final com pessoas não especialistas e testes em dispositivos/leitores de ecrã reais continua a ser o gate humano antes de avançar para exploração detalhada.
