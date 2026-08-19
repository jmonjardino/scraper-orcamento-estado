# Exploração detalhada — OE 2026

A página `/explorar/` prepara a exploração da única vista publicável candidata: programas do Mapa 1 da Administração Central não consolidada.

## Comportamento

- apresenta uma árvore expansível baseada apenas na relação pai-filho do pacote publicado;
- permite procurar por código oficial ou designação oficial, sem inventar rótulos simples;
- mostra, na ficha selecionada, montante, percentagem do total, percentagem do pai, caminho, classificação, âmbito, limitações e fonte;
- não oferece filtros que combinem perspetivas: as classificações económica, funcional e orgânica não estão disponíveis neste pacote e nunca são somadas à programática.

O componente não carrega fontes oficiais diretamente; usa apenas `/data/current.json`. A ligação à fonte é uma ação iniciada pela pessoa.

## Limitação atual

O OE 2026 continua sem pacote publicado. Por isso a página apresenta o estado de indisponibilidade até o gate de publicação receber termos de reutilização resolvidos e aprovação humana válida. Os testes usam uma fixture isolada para verificar a interação sem expor o conjunto bloqueado.
