# Padrão comum das três linguagens

As versões C++, Java e Python devem oferecer a mesma experiência externa, embora cada ecossistema utilize suas próprias ferramentas, dependências e convenções internas.

## Mesmo contrato

As três variantes devem preservar:

- os mesmos nomes de operações;
- os mesmos nomes de parâmetros;
- as mesmas regras de obrigatoriedade;
- os mesmos valores aceitos para os parâmetros comuns;
- os mesmos códigos de saída;
- mensagens de erro equivalentes;
- os mesmos formatos de kernel, CSV e JSON;
- a mesma organização de `images/`, `kernels/` e `results/`;
- o mesmo conjunto de imagens-base;
- testes públicos equivalentes quanto à infraestrutura verificada.

A implementação interna pode seguir os recursos naturais de cada linguagem. Isso significa, por exemplo, que as versões das bibliotecas, o sistema de build e a organização interna das classes ou módulos não precisam ser idênticos para que o contrato didático seja equivalente.

## Fronteira pedagógica

A infraestrutura fica pronta. O estudante implementa os algoritmos de Processamento de Imagens.

```mermaid
flowchart LR
    A[CLI e parâmetros] --> B[Validação]
    B --> C[Leitura de arquivos]
    C --> D[Algoritmo do estudante]
    D --> E[Escrita de resultados]
```

## Parâmetros comuns

`--operation`, `--input`, `--output`, `--value`, `--levels`, `--threshold`, `--alpha`, `--kernel`, `--border` e `--size`.

## Operações comuns

`inspect`, `copy`, `channel_b`, `channel_g`, `channel_r`, `grayscale_average`, `grayscale_weighted`, `quantize`, `brightness`, `contrast`, `negative`, `threshold`, `histogram`, `convolution`, `mean_filter`, `weighted_mean`, `laplacian` e `sobel`.

## Versão do contrato

O projeto-base 0.2.0 utiliza o contrato externo de versão 2. A saída de `--version` deve permitir conferir esses dois valores na variante escolhida.