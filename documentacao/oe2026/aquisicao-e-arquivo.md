# Aquisição e arquivo — OE 2026

## Estado

O processo está pronto para adquirir e arquivar os três documentos oficiais definidos no catálogo. A recolha não altera o contrato de dados nem desbloqueia uma árvore selecionável: os mapas PDF são guardados como evidência e fallback de auditoria.

## Executar

Na raiz do repositório:

```bash
python3 ferramentas/aquirir_fontes.py
```

Para validar apenas as restrições do catálogo, sem rede:

```bash
python3 ferramentas/aquirir_fontes.py --dry-run
```

Por omissão, o arquivo local é criado em `arquivo/oe-2026-approved-initial/` e não é versionado pelo Git. Pode ser escolhido outro destino:

```bash
python3 ferramentas/aquirir_fontes.py --archive-root /caminho/para/arquivo
```

## Garantias do processo

- Só aceita HTTPS e os domínios constantes em `config/fontes-oe2026.json`.
- Usa identificação, timeout de 30 segundos, no máximo três tentativas e dois segundos entre pedidos.
- Confirma o tipo PDF pelo conteúdo e guarda tamanho, MIME, URL, estado HTTP e SHA-256.
- Guarda cada original em `originais/sha256/<prefixo>/<sha256>`; um conteúdo igual não é duplicado.
- Publica `manifesto.json` apenas se **todos** os ficheiros forem adquiridos e validados. Uma falha mantém intacto o último manifesto válido.
- Guarda um relatório por execução em `relatorios/`. O manifesto não inclui timestamps, portanto é estável se as fontes não se alterarem.

## Atualização anual ou de release

1. Concluir a Parte 1 para o novo ano/fase e aprovar explicitamente as URLs e os domínios.
2. Criar um catálogo em `config/` com novo `release_id`; não editar o catálogo que originou um arquivo já publicado.
3. Executar primeiro com `--dry-run`, depois com um `--archive-root` isolado.
4. Rever manifesto e relatório: hashes, MIME, cobertura, fase e termos de reutilização.
5. Só entregar o manifesto à normalização depois de passarem os gates da Parte 1 e as validações da Parte 4.

Não colocar PDFs, manifestos ou relatórios num bundle de frontend. A aplicação futura lerá apenas um conjunto normalizado e validado, nunca fará pedidos diretos às fontes oficiais durante a navegação.

## Inspeção do Mapa 1 estruturado

Depois de adquirir o XML `Mapa1-2026`, executar:

```bash
python3 ferramentas/inspecionar_mapa1.py --report arquivo/oe-2026-approved-initial/inspecoes/mapa1.json
```

O relatório descreve o cabeçalho, campos, número de registos, códigos distintos, soma dos montantes e se a origem declara campos de missão ou de pai. Não normaliza nem aprova dados: essa decisão continua dependente dos gates da Parte 1.

## Incidente TLS da DGO

Em 2026-08-18, `www.dgo.gov.pt` apresentou um certificado que não correspondia ao respetivo hostname. Os dois PDFs passaram para os URLs diretos oficiais da Entidade Orçamental em `www.eo.gov.pt`, ligados pela página do OE aprovado. O adquiridor não tem, nem terá, uma opção para ignorar erros de certificado.
