# Explorador do Orçamento do Estado

Base reprodutível para adquirir, validar e apresentar o Orçamento do Estado. A versão atual trabalha sobre o OE 2026 aprovado e mantém publicação e validação como decisões separadas.

## Aplicação web

A Parte 5 usa Vite, React e TypeScript numa aplicação multipágina estática, com CSS nativo:

- `/` apresenta o total de referência e os programas;
- `/explorar/` permite navegar na árvore e pesquisar códigos/designações, quando existir pacote publicado;
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

`build:ui` gera as duas páginas, mas nunca inclui dados orçamentais. O build publicável é diferente:

```bash
npm run build:release
```

Esse comando só chama o Vite depois de `ferramentas/preparar_publicacao_web.py` aceitar conjunto, relatório, catálogo e aprovação humana. O OE 2026 atual continua bloqueado porque os termos de reutilização não estão resolvidos, `publication_eligible` não é verdadeiro e não existe aprovação humana vinculada ao SHA.

## Pipeline de dados

Os passos existentes continuam disponíveis separadamente:

```bash
python3 ferramentas/aquirir_fontes.py --dry-run
python3 ferramentas/normalizar_mapa1.py
python3 ferramentas/validar_conjunto_normalizado.py
```

Consulte [a documentação do OE 2026](documentacao/oe2026/README.md) para o contrato, proveniência, reconciliação e publicação web.
