# Explorador do Orçamento do Estado

Base reprodutível para adquirir, validar e apresentar o Orçamento do Estado. A versão atual trabalha sobre o OE 2026 aprovado e mantém publicação e validação como decisões separadas.

## Aplicação web

A Parte 5 usa Vite, React e TypeScript numa aplicação multipágina estática, com CSS nativo:

- `/` apresenta o total de referência e os programas;
- `/explorar/` permite navegar na árvore e pesquisar códigos/designações, quando existir pacote publicado;
- `/simulador/` permite criar um cenário local de exclusões quando a vista publicada for selecionável;
- `/metodologia/` explica âmbito, processo, limitações e fontes;
- o navegador pede apenas `/data/current.json`, criado pelo empacotador depois do gate;
- o build normal da interface não copia `dados/normalizados/` nem consulta fontes oficiais.

Esta stack mantém o alojamento estático e o processo de manutenção simples, dá contratos de tipos ao pacote publicado e permite reutilizar componentes nas partes seguintes sem exigir um servidor de aplicação.

### Preparação local

```bash
npm install
npm run dev
```

Sem um pacote aprovado, a interface mostra deliberadamente o estado recuperável “Os dados não estão disponíveis”. Para validar código e UI:

```bash
npm test
npm run typecheck
npm run build:ui
```

`build:ui` gera as quatro páginas, mas nunca inclui dados orçamentais. O build publicável é diferente:

```bash
npm run build:release
```

Esse comando só chama o Vite depois de `ferramentas/preparar_publicacao_web.py` aceitar conjunto, relatório, catálogo e aprovação humana. O OE 2026 atual continua bloqueado porque os termos de reutilização não estão resolvidos, `publication_eligible` não é verdadeiro e não existe aprovação humana vinculada ao SHA.

### Demonstração local com dados reais

Para uma demonstração estritamente local, sem deploy nem redistribuição, use:

```bash
npm run dev:demo
```

`dev:demo` prepara e serve localmente o pacote de demonstração. `build:demo` cria uma compilação equivalente em `dist/`. Ambos usam o conjunto OE 2026 já reconciliado, não alteram o catálogo de licenças, não criam uma release pública, não removem bloqueios e identificam a interface como demonstração pessoal. Usa os dados oficiais apenas no teu computador; não publiques a pasta `dist/` produzida por estes comandos.

O portal da Entidade Orçamental aponta para o Dados.gov.pt para conjuntos reutilizáveis, mas os recursos diretos usados nesta candidata não trazem uma licença específica no respetivo URL e a página do OE apresenta “todos os direitos reservados”. Os termos gerais do portal não substituem a licença do recurso concreto. Antes de qualquer redistribuição, é obrigatório registar no catálogo a licença, URL da evidência e data de verificação; veja o [gate de publicação](documentacao/oe2026/gate-de-publicacao.md).

O simulador não grava nem envia o cenário: a seleção existe apenas no estado React e é perdida ao recarregar. Calcula montantes exclusivamente a partir das folhas e bloqueia se a árvore não reconciliar ao cêntimo. O conjunto OE 2026 atual declara `selectable: false`, pelo que a página explica a salvaguarda em vez de disponibilizar controlos, mesmo quando for usado num teste local com pacote.

## Pipeline de dados

Os passos existentes continuam disponíveis separadamente:

```bash
python3 ferramentas/aquirir_fontes.py --dry-run
python3 ferramentas/normalizar_mapa1.py
python3 ferramentas/validar_conjunto_normalizado.py
```

Consulte [a documentação do OE 2026](documentacao/oe2026/README.md) para o contrato, proveniência, reconciliação e publicação web.
