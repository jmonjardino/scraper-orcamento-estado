# Decisão da árvore canónica — OE 2026

## Decisão atual

`canonical_view = administracao_central_nao_consolidada_por_programa` e `status = technically_reconciled_but_not_publishable`.

A estrutura missão → programa → ação continua a ser a candidata ideal, mas não está disponível em dados estruturados. O XML oficial `Mapa1-2026.xml` fornece 20 programas com código, designação, ministério e total. Não declara uma missão nem um pai; por isso a vista aceite tecnicamente é uma raiz oficial da Administração Central não consolidada com programas como folhas, e não uma hierarquia missão → programa.

O XML soma **352 472 389 960 €**, exatamente o `Total da Administração Central` não consolidado no PDF oficial Mapa 1, página 1. O total consolidado da Administração Central (245 121 564 003 €), a Segurança Social e o total AC+SS continuam universos distintos e não entram nesta vista.

## Gates obrigatórios

| Gate | Critério |
|---|---|
| G1 | Fonte oficial estruturada; relações não inferidas de layout PDF. |
| G2 | Árvore acíclica, com um pai por nó dentro da vista. |
| G3 | Cobertura integral do mesmo universo do total de referência. |
| G4 | Folhas sem sobreposição calculável. |
| G5 | 100% dos nós e total com proveniência navegável. |
| G6 | Ano, fase, universo, Segurança Social, consolidação, ótica, bruto/líquido e unidade compatíveis. |
| G7 | Delta até 1 € apenas por arredondamento oficialmente explicado. |
| G8 | Pelo menos uma raiz e um nível oficial navegável abaixo dela. |
| G9 | Mesmos originais e regras produzem o mesmo relatório. |

Para o simulador, o delta tem de ser zero cêntimos ou existir uma rubrica oficial explicativa; a tolerância documental não autoriza criar um ajuste artificial.

## Ordem de escolha

1. Programática: missão → programa → ação, se passar G1–G9.
2. Programas da Administração Central não consolidada: aceite tecnicamente para normalização interna; raiz oficial → programa.
3. Funcional, se as anteriores falharem e esta passar os mesmos gates.
4. Económica, se as anteriores falharem e esta passar os mesmos gates.
5. Nenhuma: reduzir o produto a metodologia/visão, sem simulador.

Os totais de MBO e do Portal Mais Transparência não são tratados como falha de arredondamento: representam leituras com âmbito/ótica diferentes. A Administração Central, a Segurança Social e as classificações alternativas serão sempre mantidas separadas até uma fonte oficial provar a correspondência.
