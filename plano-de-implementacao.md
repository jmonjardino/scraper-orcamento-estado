# Plano de implementação — Explorador do Orçamento do Estado

## Objetivo do primeiro produto

Disponibilizar uma aplicação pública que permita explorar **um único Orçamento do Estado aprovado** — inicialmente OE 2026 — e construir cenários de exclusão de despesa de forma transparente e auditável.

O produto não deve afirmar que uma exclusão corresponde a uma poupança real. Deve comunicar o respetivo **montante orçamentado excluído do cenário**, as limitações conhecidas e a fonte oficial de cada valor.

## Limites do MVP

Incluído no MVP:

- OE aprovado de 2026;
- despesas previstas, com âmbito contabilístico explicitamente identificado;
- exploração por uma árvore orçamental validada;
- pesquisa, filtros definidos pela fonte e seleção/desseleção de rubricas;
- cálculo local do montante incluído, excluído e percentagem;
- fontes e metodologia visíveis.

Fora do MVP:

- comparação entre anos;
- execução mensal ou anual;
- contas de administrações regionais e locais, salvo se fizerem parte explícita do conjunto escolhido;
- cálculo automático de impacto no défice, dívida ou impostos;
- cenários guardados, partilhados ou exportados;
- autenticação e contas de utilizador;
- interpretação política, recomendações ou classificação subjetiva de despesas.

## Princípios não negociáveis

- Os dados originais oficiais são preservados, versionados e atribuídos.
- Um número apresentado pode ser rastreado até à sua fonte.
- Perspetivas orçamentais diferentes não são somadas entre si.
- Nenhuma simulação é apresentada como poupança garantida.
- A interface declara sempre ano, fase do ciclo, universo e ótica contabilística.
- Um erro de importação impede a publicação dos dados afetados.

## Sequência e pontos de decisão

Cada parte termina num ponto de aceitação. Não se inicia a parte seguinte sem os critérios de sucesso da anterior.

| Parte | Resultado verificável | Decisão de passagem |
|---|---|---|
| 1. Contrato de dados | Âmbito, fontes e reconciliações definidos | Há uma fonte granular e um total de referência compatível |
| 2. Aquisição | Cópia imutável dos ficheiros oficiais e manifesto | Os ficheiros podem ser descarregados e identificados de forma repetível |
| 3. Normalização | Dados estruturados e árvore navegável | Cada nó tem código, valor, hierarquia e proveniência |
| 4. Qualidade | Validações automáticas e relatório de reconciliação | Não há diferenças não explicadas nos totais publicados |
| 5. Fundação web | Aplicação acessível com dados de teste | O produto abre e comunica corretamente o seu âmbito |
| 6. Exploração | Navegação, pesquisa e filtros sobre dados validados | Qualquer rubrica pode ser encontrada e auditada |
| 7. Simulador | Cenário de exclusão semanticamente correto | Não permite dupla contagem nem comunica poupança como facto |
| 8. Prontidão pública | Revisão final, monitorização e documentação | O MVP é seguro de publicar e fácil de corrigir |

---

## Parte 1 — Contrato de dados e mapa de fontes

### Objetivo final

Transformar “o Orçamento do Estado” num âmbito técnico inequívoco antes de escrever um scraper ou desenhar uma base de dados.

### O que deve ser feito

1. Escolher formalmente a versão inicial: **OE 2026 aprovado**, e não proposta ou execução.
2. Inventariar os ficheiros oficiais da DGO: Lei, Mapas Contabilísticos, desenvolvimentos da orçamentação por programas e ficheiros em formato de dados/XML.
3. Descarregar e inspecionar uma amostra real de cada formato, sem ainda construir o importador definitivo.
4. Comparar as leituras possíveis: missão/programa/ação, funcional, orgânica, económica e Segurança Social.
5. Escolher a árvore canónica do simulador. A hipótese preferida é **missão → programa → ação**, desde que a cobertura e os totais possam ser reconciliados.
6. Definir o total de referência, universo institucional, ótica contabilística, unidade monetária e regras de arredondamento.
7. Definir as relações permitidas entre vistas: uma pessoa pode alternar de perspetiva, mas nunca combinar nós de árvores sobrepostas no mesmo cálculo.
8. Registar rubricas ou campos indisponíveis, ambíguos ou não comparáveis.

### Entregáveis

- Inventário de fontes com URL, entidade publicadora, formato, cobertura e frequência.
- Amostras originais guardadas apenas para análise.
- Dicionário de dados inicial.
- Documento de contrato de dados, com o âmbito exato da versão 1.
- Decisão escrita sobre a árvore canónica e a regra de não dupla contagem.

### Métricas de sucesso

- 100% dos valores do futuro MVP têm uma fonte oficial identificada.
- Existe um ficheiro estruturado e granular que suporta a árvore escolhida, ou uma decisão explícita de usar outra fonte.
- O total da árvore candidata reconcilia com um total oficial definido, com diferença de arredondamento máxima de 1 € ou uma explicação formal da diferença.
- Qualquer pessoa da equipa consegue responder: “que universo estou a ver?” sem interpretar o código.

### Sinais de não sucesso / bloqueio

- Só é possível obter detalhe através de leitura manual de PDF sem método robusto de validação.
- A árvore de programa/ação não cobre o mesmo universo que o total apresentado.
- Existem totais incompatíveis e não é possível explicar a diferença com metadados oficiais.
- Não se consegue distinguir previsão, execução, Administração Central e Segurança Social.

### Decisão ao terminar

Se a fonte granular não for suficientemente completa, reduzir o MVP para uma vista funcional ou económica de menor detalhe, em vez de inventar uma granularidade inexistente.

---

## Parte 2 — Aquisição reprodutível e arquivo da fonte

### Objetivo final

Conseguir recolher os dados oficiais selecionados de forma repetível, respeitosa e auditável.

### O que deve ser feito

1. Criar um processo de aquisição exclusivamente para domínios e URLs oficiais aprovados na Parte 1.
2. Preferir XML, XLSX ou outros dados abertos; utilizar PDF apenas como referência ou fallback identificado.
3. Guardar sem alteração cada ficheiro original.
4. Criar um manifesto por recolha: URL, data/hora, nome, tamanho, tipo MIME, hash criptográfico, ano, estado do OE e licença/condições conhecidas.
5. Aplicar limites de frequência, timeout, tentativas limitadas e identificação clara do processo, se a fonte assim o exigir.
6. Tornar a aquisição idempotente: repetir o processo não cria cópias ambíguas nem altera dados históricos.
7. Definir falha segura: uma recolha incompleta nunca substitui o último conjunto validado.

### Entregáveis

- Processo de aquisição executável localmente.
- Arquivo de fontes originais e manifestos.
- Relatório de recolha com sucessos, falhas e hashes.
- Instruções para atualizar o OE de um novo ano.

### Métricas de sucesso

- Duas execuções consecutivas sobre as mesmas fontes produzem o mesmo manifesto e os mesmos hashes, quando a fonte não mudou.
- 100% dos ficheiros utilizados pela app constam do manifesto.
- Nenhuma página pública é consultada com frequência excessiva; a app serve dados próprios, não faz pedidos à DGO a cada visita.
- Um ficheiro alterado na origem é detetado antes de substituir o conjunto publicado.

### Sinais de não sucesso / bloqueio

- A aquisição depende de URLs temporários, sessão autenticada ou interação humana frequente.
- Não existe forma de saber qual a versão exata que originou um valor publicado.
- Uma falha parcial pode apagar ou substituir dados válidos.

### Decisão ao terminar

Só avançar se os dados puderem ser reconstruídos a partir do manifesto e dos ficheiros guardados.

---

## Parte 3 — Normalização, modelo interno e árvore navegável

### Objetivo final

Converter os ficheiros originais num conjunto de dados interno que preserve significado, hierarquia e proveniência.

### O que deve ser feito

1. Definir o modelo mínimo de rubrica: identificador estável, código oficial, designação oficial, valor em cêntimos, ano, dimensão, nível, pai, ordem, fonte e localização na fonte.
2. Modelar separadamente as perspetivas funcionais, económicas, orgânicas e programáticas; não criar uma falsa árvore universal.
3. Construir o importador da árvore canónica e das vistas necessárias à interface.
4. Preservar designações e códigos oficiais; criar apenas rótulos de linguagem simples separados do original e revistos manualmente.
5. Representar valores monetários em cêntimos ou decimal exato, nunca em vírgula flutuante.
6. Guardar metadados de cobertura: Administração Central, Segurança Social, consolidado/não consolidado, previsão/executado e classificação contabilística.
7. Preparar marcações factuais existentes na fonte, como despesas obrigatórias ou vinculações externas, sem inferir restrições que a fonte não confirme.

### Entregáveis

- Esquema de dados documentado.
- Importador versionado.
- Conjunto de dados normalizado para o OE 2026.
- Árvore navegável e índice de pesquisa.
- Tabela de proveniência que liga cada nó ao ficheiro e à referência original.

### Métricas de sucesso

- 100% dos nós publicados têm código/designação/valor/fonte.
- Cada nó filho tem exatamente um pai dentro da sua vista ou é explicitamente uma raiz.
- Os valores preservam precisão até ao cêntimo.
- O importador é determinista: os mesmos originais produzem o mesmo conjunto normalizado.
- Pesquisa por código oficial e por designação devolve a rubrica correta.

### Sinais de não sucesso / bloqueio

- Um valor precisa de ser “adivinhado” a partir do layout de um PDF.
- Existem nós sem fonte ou sem dimensão contabilística.
- A mesma rubrica aparece em duas posições da mesma árvore sem uma regra oficial que explique a repetição.

### Decisão ao terminar

Publicar apenas a dimensão cuja hierarquia e proveniência estejam completas. As restantes podem ficar como dados internos até validação.

---

## Parte 4 — Qualidade, reconciliação e governação do dado

### Objetivo final

Garantir que os números apresentados são corretos no âmbito declarado e que erros são detetados antes de chegarem ao público.

### O que deve ser feito

1. Criar validações estruturais: campos obrigatórios, formatos de código, valores não negativos quando aplicável, pais válidos e ausência de ciclos.
2. Criar validações financeiras: soma dos filhos versus subtotal, subtotal versus raiz e totais versus mapas oficiais.
3. Definir tolerâncias apenas para arredondamento publicado; qualquer diferença material falha a importação.
4. Comparar pontos de controlo com os documentos da DGO e, quando o âmbito coincidir, com o Portal Mais Transparência.
5. Produzir um relatório legível de reconciliação por importação.
6. Definir estados do conjunto: recolhido, normalizado, validado, publicado e rejeitado.
7. Preparar uma correção versionada: nunca editar silenciosamente um valor já publicado.

### Entregáveis

- Suite automática de validação.
- Relatório de reconciliação do OE 2026.
- Página ou ficheiro de metodologia e limitações.
- Política de correção e histórico de versões.

### Métricas de sucesso

- 0 diferenças materiais não explicadas entre os totais publicados e a fonte de referência.
- 100% das regras críticas passam antes da publicação.
- Um erro deliberado num valor, código ou pai faz a validação falhar.
- O relatório identifica fonte, total esperado, total calculado e diferença.

### Sinais de não sucesso / bloqueio

- O conjunto só parece correto porque alguém o inspecionou visualmente.
- Uma diferença financeira é escondida por arredondamento excessivo.
- Não existe modo de saber que versão dos dados a interface está a servir.

### Decisão ao terminar

O OE 2026 só fica disponível à interface depois de obter o estado “validado”.

---

## Parte 5 — Fundação da aplicação e linguagem de confiança

### Objetivo final

Criar a aplicação web mínima, responsiva e acessível, preparada para receber dados validados — sem ainda depender do simulador.

### O que deve ser feito

1. Escolher a stack depois de inspecionar requisitos de alojamento, manutenção e equipa; não escolher tecnologia por hábito.
2. Criar uma interface inicial que declare sempre o ano, o estado “OE aprovado”, o universo e a ótica contabilística.
3. Implementar uma página de resumo com o total de referência e explicação simples do que está incluído e excluído.
4. Criar cartões das grandes áreas com números, percentagem e ligação à origem.
5. Criar uma área de “metodologia e fontes” compreensível sem conhecimentos de contabilidade pública.
6. Garantir semântica HTML, navegação por teclado, contraste adequado, estados de carregamento/erro/vazio e adaptação a telemóvel.
7. Integrar apenas o conjunto de dados validado da Parte 4.

### Entregáveis

- Aplicação navegável com dados do OE 2026.
- Página de metodologia e fontes.
- Estados de erro e indisponibilidade de dados.
- Base visual reutilizável para exploração e simulador.

### Métricas de sucesso

- Uma pessoa consegue identificar, em menos de 30 segundos, ano, âmbito e significado do total mostrado.
- 100% dos cartões principais têm fonte acessível.
- Os fluxos principais funcionam por teclado e em ecrãs móveis comuns.
- Não é feita qualquer chamada direta do navegador para fontes oficiais durante a utilização normal.

### Sinais de não sucesso / bloqueio

- O total surge sem âmbito contabilístico ou sem fonte.
- A interface usa apenas cor para comunicar estados ou seleção.
- O carregamento de dados falha sem mensagem recuperável.

### Decisão ao terminar

Validar com utilizadores não especialistas se conseguem explicar o que estão a ver antes de acrescentar mais detalhe.

---

## Parte 6 — Exploração detalhada, pesquisa e filtros

### Objetivo final

Permitir que qualquer pessoa passe de uma grande área a uma rubrica detalhada sem perder contexto nem criar dupla contagem.

### O que deve ser feito

1. Implementar a árvore da perspetiva canónica, com expansão e colapso de níveis.
2. Mostrar em cada nó valor, percentagem do pai, percentagem do total e caminho hierárquico.
3. Adicionar pesquisa por designação simples, designação oficial e código.
4. Adicionar apenas filtros cuja semântica esteja garantida pelos dados; por exemplo, ministério ou tipo económico só quando a relação com a árvore for inequívoca.
5. Criar vistas alternativas funcionais, orgânicas ou económicas apenas como navegações independentes, claramente rotuladas.
6. Criar uma ficha de rubrica com descrição, classificação, âmbito, fonte, data de atualização e limitações.
7. Desativar ou assinalar claramente rubricas indisponíveis, agregadas ou sem detalhe suficiente.

### Entregáveis

- Árvore orçamental interativa.
- Pesquisa e filtros validados.
- Ficha auditável de cada rubrica publicada.
- Navegação entre resumo, detalhe e fonte.

### Métricas de sucesso

- Uma pesquisa por termo ou código devolve resultados relevantes em menos de 1 segundo sobre o conjunto inicial.
- Um utilizador consegue chegar de uma área grande a uma rubrica folha sem perder o total de referência.
- 100% das fichas de rubrica mostram fonte e caminho hierárquico.
- A soma dos elementos exibidos em qualquer vista coincide com o subtotal mostrado ou explica explicitamente o que ficou oculto.

### Sinais de não sucesso / bloqueio

- Filtros escondem valores sem atualizar totais ou sem explicação.
- Uma mesma rubrica pode ser vista e somada em mais de uma perspetiva simultaneamente.
- A pesquisa apresenta uma rubrica sem contexto, valor ou fonte.

### Decisão ao terminar

Fazer uma revisão de compreensão com pessoas não especialistas; só avançar se estas reconhecerem claramente a diferença entre área, programa, ação e tipo de despesa.

---

## Parte 7 — Simulador de cenário de exclusão

### Objetivo final

Permitir selecionar e desselecionar rubricas na árvore canónica, com cálculo rigoroso e comunicação responsável.

### O que deve ser feito

1. Definir o modelo de seleção por árvore: selecionar um nó inclui todos os descendentes; desselecionar um descendente coloca o ancestral em estado parcial.
2. Calcular sempre a seleção a partir das folhas, para evitar contar um pai e um filho duas vezes.
3. Mostrar montante incluído, montante excluído, percentagem do total de referência e número de rubricas afetadas.
4. Manter o cenário no browser na primeira versão; não criar contas nem persistência remota.
5. Mostrar um aviso permanente: “montante orçamentado excluído do cenário; não representa necessariamente poupança realizável”.
6. Mostrar etiquetas factuais disponíveis — obrigação, vinculação externa, transferência ou outra limitação — antes de uma exclusão.
7. Permitir repor o cenário e fornecer um resumo textual acessível da seleção atual.
8. Impedir a mistura de perspetivas e tornar a troca de vista explicitamente destrutiva para a seleção, após aviso.

### Entregáveis

- Controlo de seleção hierárquica.
- Painel de cenário com totais e avisos.
- Resumo acessível e reset do cenário.
- Testes para cálculo, seleção parcial e prevenção de dupla contagem.

### Métricas de sucesso

- Para qualquer cenário, `incluído + excluído = total de referência`, com diferença máxima de 0 cêntimos.
- Um pai e um descendente selecionados nunca aumentam o total duas vezes.
- Trocar de perspetiva não preserva silenciosamente uma seleção incompatível.
- 100% dos ecrãs do simulador incluem a limitação de “não é poupança garantida”.
- Os cálculos ocorrem em tempo percebido como imediato para o conjunto inicial.

### Sinais de não sucesso / bloqueio

- A interface diz “poupança” sem qualificação.
- Uma exclusão altera o valor de uma rubrica fora da árvore sem explicar porquê.
- O total do cenário deixa de coincidir com a raiz validada.
- É possível selecionar simultaneamente uma vista funcional e uma programática no mesmo cálculo.

### Decisão ao terminar

Submeter o simulador a revisão de contabilidade pública e de linguagem antes de disponibilizá-lo ao público.

---

## Parte 8 — Qualidade final, operação e publicação controlada

### Objetivo final

Colocar o MVP online com uma operação simples, observável e reversível.

### O que deve ser feito

1. Executar testes de dados, interface, cálculo, acessibilidade e desempenho.
2. Rever conteúdo e linguagem com alguém conhecedor de orçamento público.
3. Validar em telemóvel, tablet e computador, com teclado e leitor de ecrã nos fluxos principais.
4. Configurar registo de erros técnicos sem recolher dados pessoais desnecessários.
5. Monitorizar disponibilidade, falhas de importação, versão de dados publicada e erros de interface.
6. Preparar uma página de estado e um canal para reporte de erros nos dados.
7. Definir rollback: publicar a versão anterior dos dados ou aplicação se uma validação posterior encontrar erro.
8. Lançar inicialmente em acesso limitado e recolher feedback de cidadãos e especialistas antes de comunicação ampla.

### Entregáveis

- Checklist de aceitação preenchida.
- Plano de rollback testado.
- Monitorização mínima e procedimento de incidentes.
- Política de privacidade proporcional ao MVP.
- Versão pública controlada do MVP.

### Métricas de sucesso

- 0 falhas críticas nos fluxos de explorar, procurar, selecionar, desselecionar e consultar fonte.
- 0 erros materiais de reconciliação conhecidos no conjunto publicado.
- Todos os incidentes de dados podem ser associados à versão e fonte de origem.
- É possível restaurar a versão anterior da aplicação e dos dados de forma documentada.
- O feedback de utilizadores confirma que o simulador é entendido como cenário, não como promessa de poupança.

### Sinais de não sucesso / bloqueio

- Não é possível saber que versão está online.
- Não existe forma segura de corrigir um número errado.
- A monitorização revela falhas recorrentes sem informação suficiente para as diagnosticar.
- Utilizadores interpretam sistematicamente o simulador como uma recomendação política ou uma poupança assegurada.

---

## Critérios de aceitação do MVP completo

O MVP está concluído quando uma pessoa consegue:

1. Abrir a aplicação e perceber imediatamente o que o total representa.
2. Explorar uma grande área até ao detalhe suportado pelos dados.
3. Pesquisar uma rubrica pelo nome ou código.
4. Consultar a fonte oficial e a metodologia de qualquer valor apresentado.
5. Desselecionar rubricas numa única árvore e ver o montante excluído do cenário.
6. Compreender que esse montante não equivale automaticamente a poupança real.

E quando a equipa consegue provar que:

1. Os dados publicados derivam de fontes oficiais arquivadas.
2. Os totais são reconciliados e as exceções são documentadas.
3. Não existe dupla contagem no simulador.
4. Um erro de importação ou publicação pode ser detetado e revertido.

## Pressupostos que têm de ser confirmados na Parte 1

- O ficheiro de dados da DGO para OE 2026 contém a granularidade necessária para a árvore canónica.
- A cobertura da árvore de missão/programa/ação pode ser reconciliada com um total oficial claramente identificado.
- Os metadados disponíveis permitem marcar, sem inferência, pelo menos parte das despesas obrigatórias ou vinculadas.
- A licença e condições de reutilização dos dados oficiais permitem a sua republicação com atribuição.

Se algum pressuposto falhar, o plano continua válido, mas o âmbito do MVP deve ser reduzido antes de construir a interface: menos detalhe, uma única perspetiva e comunicação explícita da cobertura.
