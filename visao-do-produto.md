# Explorador do Orçamento do Estado

## Visão

Transformar o Orçamento do Estado numa experiência simples, clara e interativa, acessível a qualquer pessoa.

A aplicação deverá permitir perceber quanto dinheiro público é destinado a cada área, entidade ou programa e explorar as escolhas que compõem o orçamento.

> Uma ferramenta pública para explorar, compreender e simular o Orçamento do Estado com base em dados oficiais.

## O que a aplicação deverá fazer

### Dados

- Recolher documentos oficiais do Orçamento do Estado.
- Extrair despesas, receitas, ministérios, programas, entidades e classificações.
- Normalizar os valores para permitir comparações entre anos.
- Manter a ligação para a fonte original.
- Indicar a data da última atualização dos dados.

### Exploração

- Mostrar o orçamento total e a sua distribuição por grandes áreas.
- Permitir navegar de valores agregados para categorias mais detalhadas.
- Pesquisar por termos, entidades ou programas.
- Filtrar por ano, ministério e tipo de despesa.
- Comparar diferentes anos e mostrar variações.

### Simulação

As pessoas poderão selecionar ou desselecionar rubricas para observar:

- o valor total selecionado;
- o valor potencialmente excluído;
- a percentagem do orçamento correspondente;
- uma estimativa do impacto na despesa total e no défice;
- opcionalmente, o valor equivalente por habitante ou contribuinte.

## Uma distinção importante: poupança teórica não é necessariamente poupança real

A aplicação não deve sugerir que qualquer despesa pode ser eliminada automaticamente. Algumas despesas são obrigatórias por lei, plurianuais, resultantes de contratos já assinados, parcialmente financiadas por fundos europeus ou simplesmente transferidas para outra rubrica quando alteradas.

Por isso, convém distinguir claramente:

- valor orçamentado;
- valor efetivamente executado;
- poupança teórica;
- poupança potencial;
- despesa fixa ou difícil de alterar;
- despesa discricionária.

Também será necessário distinguir despesa prevista de despesa paga, despesa anual de encargos plurianuais, despesa bruta de despesa líquida, investimento de despesa corrente e dinheiro nacional de dinheiro europeu.

As transferências entre organismos merecem atenção especial, pois podem fazer com que o mesmo dinheiro apareça em mais do que uma parte da estrutura e seja contado duas vezes.

## Experiência inicial desejada

Uma primeira versão conceptual poderia incluir:

- um resumo do orçamento total;
- cartões para as grandes áreas, como saúde, educação, defesa, pensões, transportes e juros da dívida;
- uma árvore hierárquica ou gráfico explorável;
- filtros por ano, ministério e tipo de despesa;
- seleção e desseleção de rubricas;
- um painel com total incluído, total excluído e percentagem do orçamento;
- explicações em linguagem simples;
- links para os documentos oficiais.

## Possíveis evoluções

- Comparar dois orçamentos.
- Criar e partilhar cenários.
- Exportar uma simulação.
- Mostrar o impacto por habitante.
- Relacionar despesas com indicadores públicos.
- Indicar o grau de confiança da extração e das transformações dos dados.
- Permitir que especialistas assinalem erros ou ambiguidades.

## Principais desafios

O desafio central não será apenas construir a interface, mas garantir a qualidade e a interpretação dos dados. Os documentos oficiais podem estar em PDFs complexos, as tabelas podem mudar entre anos e a mesma despesa pode aparecer com classificações diferentes.

O sistema deverá ter validações fortes e explicar quando um valor foi transformado, agregado ou inferido. É preferível apresentar menos categorias com números confiáveis e bem explicados do que milhares de linhas cuja interpretação seja duvidosa.

## Princípios de confiança e neutralidade

A aplicação deverá ser explicitamente apartidária na forma como apresenta a informação:

- fontes oficiais visíveis;
- metodologia publicada;
- valores reproduzíveis;
- linguagem descritiva, não editorial;
- separação clara entre dados e opinião;
- limitações das simulações apresentadas ao utilizador;
- possibilidade de verificar cada valor na fonte original.

## Direção recomendada

Começar por um único ano e por um nível de detalhe controlado. O produto ganha mais valor através da clareza, da transparência e da confiança do que através da quantidade bruta de linhas importadas.

O objetivo não é apenas criar um scraper. É tornar as escolhas orçamentais legíveis e permitir que qualquer pessoa formule perguntas informadas sobre o dinheiro público.
