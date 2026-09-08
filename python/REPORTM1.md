# Mini relatorio - Laboratorio M1

## Identificacao

* Estudante: Joao Eduardo Cardoso
* Matricula: 7937857
* Laboratorio: M1.1: Representacao, canais e niveis de cinza
* Linguagem: Python

## 1. Objetivo

Implementar operacoes basicas de processamento de imagens por meio do acesso direto aos pixels, trabalhando com dimensoes, canais de cor, conversao para niveis de cinza e reducao da quantidade de niveis de intensidade.

## 2. Operacoes implementadas

Foram implementadas as seguintes operacoes:

* **Inspecao da imagem:** obtencao de largura, altura, quantidade de canais, tipo, quantidade de pixels e estatisticas de intensidade. Para imagens coloridas, as estatisticas sao calculadas separadamente para os canais B, G e R.
* **Copia manual:** criacao de uma nova imagem e copia individual de cada pixel, sem utilizar uma funcao pronta de copia.
* **Separacao de canais:** criacao de imagens contendo individualmente os canais azul, verde e vermelho, mantendo os demais canais zerados.
* **Conversao para tons de cinza:** implementacao da media simples e da media ponderada dos canais R, G e B.
* **Quantizacao:** reducao da imagem em tons de cinza para 2, 4, 8 ou 16 niveis, agrupando as intensidades em faixas e utilizando um valor representativo para cada faixa.

As operacoes que exigem processamento manual foram implementadas com percurso explicito dos pixels. A leitura e escrita das imagens foram realizadas utilizando OpenCV.

## 3. Testes realizados

| Teste                       | Entrada                      | Operacao             | Parametros          | Resultado esperado ou criterio de verificacao                                                   |
| --------------------------- | ---------------------------- | -------------------- | ------------------- | ----------------------------------------------------------------------------------------------- |
| Inspecao de imagem colorida | `m1_color_2x2.png`           | `inspect`            |                     | Largura 2, altura 2, 3 canais e estatisticas calculadas corretamente                            |
| Copia manual                | `m1_color_2x2.png`           | `copy`               |                     | Imagem de saida numericamente identica a entrada                                                |
| Separacao do azul           | `m1_color_2x2.png`           | `channel_b`          |                     | Canal B preservado e canais G e R zerados                                                       |
| Separacao do verde          | `m1_color_2x2.png`           | `channel_g`          |                     | Canal G preservado e canais B e R zerados                                                       |
| Separacao do vermelho       | `m1_color_2x2.png`           | `channel_r`          |                     | Canal R preservado e canais B e G zerados                                                       |
| Media simples               | `m1_color_2x2.png`           | `grayscale_average`  |                     | Resultado previsto manualmente: `[[85, 85], [85, 255]]`                                         |
| Media ponderada             | `m1_color_2x2.png`           | `grayscale_weighted` |                     | Resultado previsto manualmente: `[[76, 150], [29, 255]]`                                        |
| Quantizacao                 | `m1_gray_steps_16levels.png` | `quantize`           | 2, 4, 8 e 16 niveis | Quantidade de niveis igual ao parametro e valores entre 0 e 255                                 |
| Caso sintetico de fronteira | `m1_quant_boundary.png`      | `quantize`           | 4 niveis            | Valores proximos as fronteiras devem resultar em `[[0, 0, 0, 85, 85, 170, 170, 255, 255, 255]]` |

Os testes automatizados das operacoes do laboratorio foram executados com sucesso, totalizando **5 testes aprovados**.

## 4. Resultados

| Operacao        | Entrada                      | Parametros | Arquivo de saida    | Observacao                                                 |
| --------------- | ---------------------------- | ---------- | ------------------- | ---------------------------------------------------------- |
| Copia           | `m1_color_2x2.png`           |            | `copy.png`          | Saida numericamente identica a entrada                     |
| Canal azul      | `m1_color_2x2.png`           |            | `channel_b.png`     | Somente o canal B foi preservado                           |
| Canal verde     | `m1_color_2x2.png`           |            | `channel_g.png`     | Somente o canal G foi preservado                           |
| Canal vermelho  | `m1_color_2x2.png`           |            | `channel_r.png`     | Somente o canal R foi preservado                           |
| Media simples   | `m1_color_2x2.png`           |            | `gray_average.png`  | Conversao utilizando pesos iguais para os tres canais      |
| Media ponderada | `m1_color_2x2.png`           |            | `gray_weighted.png` | Conversao considerando a contribuicao diferente dos canais |
| Quantizacao     | `m1_gray_steps_16levels.png` | 2 niveis   | `quant_2.png`       | 2 niveis distintos                                         |
| Quantizacao     | `m1_gray_steps_16levels.png` | 4 niveis   | `quant_4.png`       | 4 niveis distintos                                         |
| Quantizacao     | `m1_gray_steps_16levels.png` | 8 niveis   | `quant_8.png`       | 8 niveis distintos                                         |
| Quantizacao     | `m1_gray_steps_16levels.png` | 16 niveis  | `quant_16.png`      | 16 niveis distintos                                        |

## 5. Analise tecnica

### 1. Qual e a diferenca entre resolucao espacial e resolucao radiometrica?

A resolucao espacial esta relacionada a quantidade de pixels utilizada para representar uma imagem e, consequentemente, a quantidade de detalhes espaciais que pode ser representada.

A resolucao radiometrica esta relacionada a quantidade de valores de intensidade disponiveis para representar cada pixel. Em uma imagem de 8 bits, por exemplo, existem 256 valores possiveis, de 0 a 255.

### 2. Por que a media ponderada produz resultado diferente da media simples?

A media simples atribui o mesmo peso aos tres canais:

`g = (R + G + B) / 3`

A media ponderada utiliza pesos diferentes:

`g = 0.299R + 0.587G + 0.114B`

Dessa forma, o canal verde possui maior contribuicao e o azul possui menor contribuicao. Por exemplo, no teste com um pixel vermelho puro, a media simples produziu 85, enquanto a media ponderada produziu 76.

### 3. O que ocorre visualmente quando a quantidade de niveis e reduzida?

Quando a quantidade de niveis e reduzida, diferentes intensidades passam a ser representadas pelo mesmo valor. Com isso, a imagem apresenta menos variacoes de tons e transicoes mais abruptas entre regioes de intensidade diferente.

Esse efeito e mais evidente nas quantizacoes com 2 e 4 niveis.

### 4. Em quais regioes da imagem a perda de informacao fica mais evidente?

A perda de informacao fica mais evidente em regioes com variacoes suaves de intensidade, como gradientes, sombras e areas com pequenas diferencas de brilho.

Ao reduzir os niveis, essas diferencas sao agrupadas em uma mesma faixa, diminuindo os detalhes de intensidade.

### 5. Como o tipo e o numero de canais da imagem interferem na forma de acessar um pixel?

Em uma imagem em tons de cinza, cada pixel possui apenas um valor de intensidade, sendo acessado por `image[y, x]`.

Em uma imagem colorida com tres canais, cada pixel possui tres valores. Como o OpenCV utiliza a ordem BGR, um canal especifico pode ser acessado por `image[y, x, canal]`.

Assim, o tipo e a quantidade de canais determinam a estrutura dos dados e a forma de acesso aos valores dos pixels.

## 6. Limitacoes

A implementacao foi desenvolvida considerando as imagens e os tipos previstos pelo laboratorio. As operacoes de conversao para tons de cinza e separacao de canais exigem imagens coloridas com exatamente tres canais, enquanto a quantizacao exige uma imagem em tons de cinza.

A quantizacao foi implementada especificamente para os niveis previstos pelo laboratorio: 2, 4, 8 e 16. Outros valores sao rejeitados pela validacao dos parametros.

A implementacao tambem considera imagens no intervalo de intensidade utilizado pelas imagens de 8 bits, de 0 a 255.

## 7. Referencias

* Documentacao do OpenCV utilizada como referencia para leitura, escrita e acesso aos pixels das imagens.
* Material e roteiro fornecidos na disciplina de Processamento de Imagens - Laboratorio M1.1.
