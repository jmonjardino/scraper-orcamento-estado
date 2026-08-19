# Relatório de validação da fundação web — OE 2026

Data da validação técnica: 2026-08-19.

## Resultado

**Tecnicamente aprovada para desenvolvimento da exploração.** A fundação pode receber um pacote publicado quando esse pacote existir; não foi aprovada para publicação do OE 2026, porque esse gate continua bloqueado fora da interface.

## Evidência executada

| Verificação | Resultado |
| --- | --- |
| Pipeline de aquisição, normalização, validação e gate | 33 testes Python passaram |
| Componentes web | 8 testes Vitest passaram |
| Tipos TypeScript | passou sem erros |
| Build do shell sem dados | passou; gerou resumo, metodologia e exploração |
| Separação de dados | o modo `ui` não inclui `data/current.json` nem o conjunto normalizado |
| Gate de release | mantém falha antes do Vite por `reuse_terms_unresolved`, inelegibilidade e aprovação humana ausente |

Os testes exercitam carregamento, erro recuperável, vazio, ligação à fonte, árvore, pesquisa por código/designação e ficha de rubrica. A navegação usa elementos nativos, link para saltar conteúdo, foco visível e movimento reduzido. A página de exploração reorganiza a árvore e a ficha numa coluna em ecrãs estreitos.

## Limites desta validação

Não foi possível executar a validação com pessoas não especialistas: não há um pacote publicado autorizado para apresentar no navegador. O `404` de `/data/current.json` continua correto no modo local, pois evita mostrar dados bloqueados.

Antes de considerar a Parte 5 aceite por utilizadores, realizar sessões curtas com pelo menos duas pessoas não especialistas e pedir-lhes que expliquem, sem ajuda:

1. ano, fase e universo mostrado;
2. significado e exclusões do total;
3. diferença entre uma área/programa e uma rubrica de detalhe;
4. como chegam à fonte de uma rubrica.

Registar respostas e obstáculos. A aprovação humana e a resolução dos termos de reutilização continuam necessárias antes de gerar `data/current.json`.
