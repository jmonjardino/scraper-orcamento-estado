# Simulador de cenários — Parte 7

Data da implementação e validação técnica: 2026-08-19.

## Resultado

A página `/simulador/` implementa cenários de exclusão numa única árvore programática. O cenário permanece apenas na memória do browser: não existe persistência, exportação, backend ou pedido de rede adicional. Recarregar a página repõe a seleção.

Esta implementação está tecnicamente preparada, mas **não aprova a publicação do OE 2026 nem conclui o gate humano da Parte 7**. O pacote atual declara `selectable: false`; nesse estado, a página apresenta a salvaguarda e não disponibiliza ações.

## Regras de cálculo

- O estado contém exclusivamente um conjunto de IDs de folhas excluídas.
- Excluir um pai adiciona as folhas descendentes; voltar a incluí-lo remove essas folhas.
- Um pai parcialmente selecionado usa o estado nativo `indeterminate` da checkbox.
- Montantes de pais nunca entram na soma, evitando dupla contagem.
- Em cada transição, `incluído + excluído = total da raiz`, em cêntimos inteiros.
- “Rubricas terminais afetadas” conta folhas, incluindo uma folha de montante zero.
- A chave de contexto é `dataset_sha256 + release_id + view_id + root_node_id`; qualquer alteração limpa a seleção e é anunciada.

Antes de calcular, o motor verifica IDs únicos, raiz única e declarada, referências a pais, níveis, ciclos, acessibilidade, terminação, montantes inteiros seguros não negativos, reconciliação de cada pai com os filhos e igualdade entre soma das folhas e raiz. Uma falha apresenta um bloqueio de integridade; não é criada uma rubrica de ajuste.

## Linguagem, contexto e acessibilidade

O aviso permanente diz que excluir uma rubrica cria um cenário de montantes e não uma poupança garantida ou necessariamente realizável. Está presente em carregamento, erro, vista bloqueada, integridade bloqueada e cenário pronto.

Antes da árvore, a página mostra fase, publicação, universo, Segurança Social, consolidação, medida e classificação vindos do `coverage`. Mostra as `factual_tags` declaradas; quando não existem, explica que a ausência não significa que a rubrica seja eliminável. Não oferece um seletor fictício: declara que só existe a perspetiva programática e que não mistura outras classificações.

A árvore usa listas, botões e checkboxes nativas, sem `role="tree"`. Expandir/colapsar é um controlo separado com `aria-expanded`. O painel contém montantes, percentagem, contagem, igualdade explícita, reset desativado no cenário inicial e uma única região `status` live/polite/atomic para alterações. Em ecrãs até 850 px, árvore e resumo passam para uma coluna e o resumo deixa de ser sticky; até 620 px, linhas e resultados empilham. Os controlos têm pelo menos 44 px de altura.

## Evidência automatizada

As fixtures web têm uma árvore profunda reconciliada: raiz 1000, pai 600 com folhas 200 e 400, e uma folha irmã 400. Os testes cobrem cálculo granular, seleção pai/filho sem duplicação, estado parcial, reset, folha zero, invariantes em sequências, mudança de contexto e árvores inválidas. A interface cobre aviso em todos os estados, âmbito/tags, seleção parcial, estatísticas, reconciliação, reset/anúncios, `selectable: false`, integridade, erro e retry.

Os comandos de validação são:

```bash
npm test
npm run typecheck
npm run build:ui
npm run build:release
git diff --check
```

`build:release` deve continuar a falhar antes do Vite apenas pelos bloqueios de publicação já documentados; essa falha é esperada enquanto não existir um pacote aprovado.

## Gate humano pendente

Antes de publicar o simulador, uma pessoa com experiência em contabilidade pública e uma pessoa não especialista em linguagem clara devem rever, com o mesmo SHA candidato:

1. se “incluído”, “excluído” e “rubricas terminais afetadas” são compreendidos sem serem interpretados como poupança;
2. se âmbito, não consolidação, exclusão da Segurança Social e perspetiva programática são percebidos antes da primeira ação;
3. se as restrições factuais são suficientes, verificáveis e apresentadas antes de cada exclusão;
4. se seleção parcial, expansão, reset e anúncio de mudança de contexto funcionam por rato e teclado;
5. se a igualdade ao cêntimo é compreendida como reconciliação matemática, não como viabilidade política, legal ou operacional.

Registar participantes, data, SHA, tarefas, respostas e alterações pedidas. Só depois dessa revisão e dos gates gerais de fontes, elegibilidade e aprovação humana se pode alterar `selectable` ou considerar o release publicável.
