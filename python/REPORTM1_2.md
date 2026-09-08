# Mini relatorio - Laboratorio M1.2

## Identificacao

* Estudante: Joao Eduardo Cardoso
* Matricula: 7937857
* Laboratorio: M1.2 - Transformacoes de intensidade e histograma
* Linguagem: Python

## 1. Objetivo

Implementar transformacoes de intensidade em imagens em tons de cinza e analisar como essas transformacoes alteram os valores dos pixels e a distribuicao das intensidades. Foram trabalhadas alteracoes de brilho e contraste, negativo, limiarizacao binaria e calculo manual do histograma.

## 2. Operacoes implementadas

Foram implementadas as seguintes operacoes:

* **Brilho:** cada pixel recebe um valor `b`, seguindo `g = f + b`. Valores abaixo de 0 sao limitados a 0 e valores acima de 255 sao limitados a 255.
* **Contraste:** aplicacao da formula `g = alpha(f - 128) + 128`, utilizando o valor 128 como ponto central.
* **Negativo:** inversao da intensidade utilizando `g = 255 - f`.
* **Threshold:** valores menores que o limiar recebem 0 e valores maiores ou iguais recebem 255.
* **Histograma:** contagem manual das ocorrencias de cada intensidade entre 0 e 255, armazenada em uma estrutura com 256 posicoes e posteriormente exportada para CSV.

Todas as operacoes de transformacao percorrem explicitamente os pixels da imagem em tons de cinza. O OpenCV foi utilizado para leitura e escrita das imagens.

## 3. Testes realizados

Foram utilizados casos sinteticos pequenos, imagens fornecidas no projeto e resultados gerados a partir de uma imagem de cena em tons de cinza.

| Teste               | Entrada                      | Operacao     | Parametros    | Resultado esperado ou criterio de verificacao                                               |
| ------------------- | ---------------------------- | ------------ | ------------- | ------------------------------------------------------------------------------------------- |
| Brilho positivo     | Caso sintetico               | `brightness` | `b = 20`      | Cada intensidade deve aumentar 20 unidades, respeitando o limite 255.                       |
| Brilho negativo     | Caso sintetico               | `brightness` | `b = -30`     | Cada intensidade deve diminuir 30 unidades, respeitando o limite 0.                         |
| Saturacao do brilho | Caso sintetico               | `brightness` | `b = 20`      | Valores que ultrapassariam 255 devem permanecer em 255.                                     |
| Contraste reduzido  | Caso sintetico               | `contrast`   | `alpha = 0.5` | Intensidades devem se aproximar de 128.                                                     |
| Contraste neutro    | Caso sintetico               | `contrast`   | `alpha = 1.0` | A imagem resultante deve ser identica a entrada.                                            |
| Contraste aumentado | Caso sintetico               | `contrast`   | `alpha = 1.5` | Intensidades devem se afastar de 128, respeitando os limites.                               |
| Negativo            | Caso sintetico               | `negative`   |               | Cada pixel deve resultar em `255 - f`.                                                      |
| Threshold 1         | Caso sintetico               | `threshold`  | `T = 100`     | Valores menores que 100 devem resultar em 0; valores a partir de 100 devem resultar em 255. |
| Threshold 2         | Caso sintetico               | `threshold`  | `T = 200`     | Verificar a mudanca da classificacao dos pixels com a alteracao do limiar.                  |
| Histograma          | Caso sintetico               | `histogram`  |               | Deve possuir 256 posicoes e a soma dos contadores deve corresponder ao numero de pixels.    |
| Imagem fornecida    | `m1_gray_steps_16levels.png` | Leitura      |               | A imagem deve ser carregada como imagem em tons de cinza de 8 bits.                         |

Os testes automatizados da M1.2 foram executados com `pytest`, totalizando **11 testes aprovados**.

Alem dos testes unitarios, foram gerados resultados praticos utilizando a imagem `m1_gray_scene_256.png`.

## 4. Resultados

| Operacao   | Entrada                 | Parametros    | Arquivo de saida                        | Observacao                                                              |
| ---------- | ----------------------- | ------------- | --------------------------------------- | ----------------------------------------------------------------------- |
| Brilho     | `m1_gray_scene_256.png` | `b = 50`      | `images/output/brightness_plus.png`     | Aumento geral das intensidades, com saturacao dos valores acima de 255. |
| Brilho     | `m1_gray_scene_256.png` | `b = -50`     | `images/output/brightness_minus.png`    | Reducao geral das intensidades, com saturacao dos valores abaixo de 0.  |
| Contraste  | `m1_gray_scene_256.png` | `alpha = 0.5` | `images/output/contrast_05.png`         | Reducao do contraste e aproximacao das intensidades de 128.             |
| Contraste  | `m1_gray_scene_256.png` | `alpha = 1.0` | `images/output/contrast_10.png`         | Mantem as intensidades originais.                                       |
| Contraste  | `m1_gray_scene_256.png` | `alpha = 1.5` | `images/output/contrast_15.png`         | Aumento do contraste, com saturacao nas extremidades.                   |
| Negativo   | `m1_gray_scene_256.png` |               | `images/output/negative.png`            | Inversao das intensidades da imagem.                                    |
| Threshold  | `m1_gray_scene_256.png` | `T = 80`      | `images/output/threshold_80.png`        | Conversao da imagem para apenas dois niveis de intensidade.             |
| Threshold  | `m1_gray_scene_256.png` | `T = 180`     | `images/output/threshold_180.png`       | Alteracao da classificacao dos pixels devido ao novo limiar.            |
| Histograma | `m1_gray_scene_256.png` |               | `results/histogram_original.csv`        | Histograma da imagem original.                                          |
| Histograma | `brightness_plus.png`   | `b = 50`      | `results/histogram_brightness_plus.csv` | Deslocamento das intensidades para valores maiores.                     |
| Histograma | `contrast_05.png`       | `alpha = 0.5` | `results/histogram_contrast_05.csv`     | Concentracao das intensidades em torno de 128.                          |
| Histograma | `negative.png`          |               | `results/histogram_negative.csv`        | Inversao da distribuicao das intensidades.                              |

Os quatro histogramas possuem 256 intensidades e a soma de seus contadores resulta em **65.536 pixels**, correspondente a uma imagem de 256 × 256 pixels.

## 5. Analise tecnica

### Brilho

A alteracao de brilho desloca as intensidades da imagem. Com `b = 50`, os pixels sao deslocados para valores maiores. Como a faixa valida de uma imagem de 8 bits termina em 255, valores que ultrapassam esse limite sao saturados.

Com `b = -50`, ocorre o comportamento inverso: as intensidades sao deslocadas para valores menores e aquelas que ficariam abaixo de 0 sao saturadas nesse valor.

Esse comportamento tambem pode ser observado nos histogramas. O histograma da imagem com brilho `+50` apresenta valores a partir de 50, enquanto o limite superior permanece em 255 devido a saturacao.

### Contraste

A transformacao de contraste utiliza 128 como ponto central.

Com `alpha = 0.5`, os valores sao aproximados de 128, reduzindo a diferenca entre regioes claras e escuras. Na imagem analisada, a faixa observada passou de `0–255` para aproximadamente `64–192`.

Com `alpha = 1.0`, a transformacao mantem os valores originais, funcionando como uma transformacao identidade.

Com `alpha = 1.5`, os valores sao afastados de 128, aumentando o contraste. Alguns valores ultrapassam a faixa valida e sao saturados em 0 ou 255.

### Negativo

A transformacao negativa utiliza `g = 255 - f`. Dessa forma, valores escuros tornam-se claros e valores claros tornam-se escuros.

Por exemplo, um pixel de intensidade 0 passa para 255, enquanto um pixel de intensidade 255 passa para 0. No histograma, isso corresponde a uma inversao da distribuicao das intensidades.

### Threshold

A limiarizacao transforma a imagem em uma representacao binaria. Para um limiar `T`, valores menores que `T` recebem 0 e valores maiores ou iguais recebem 255.

A utilizacao de diferentes valores de threshold, como 80 e 180, produz resultados diferentes porque modifica a quantidade de pixels classificados como claros ou escuros.

A principal perda de informacao ocorre porque todos os valores de uma mesma faixa sao convertidos para um unico nivel. Assim, diferentes intensidades presentes na imagem original deixam de ser diferenciadas.

### Histograma

O histograma foi calculado manualmente utilizando 256 posicoes, uma para cada intensidade possivel de uma imagem de 8 bits.

Para cada pixel, sua intensidade e utilizada como indice e o contador correspondente e incrementado. A soma dos contadores permite verificar se todos os pixels foram contabilizados.

Nos resultados obtidos, os quatro histogramas gerados possuem soma igual a 65.536, confirmando a correspondencia com a quantidade de pixels da imagem de 256 × 256.

As transformacoes tambem provocam alteracoes perceptiveis na distribuicao. O aumento de brilho desloca as intensidades, a reducao de contraste concentra os valores em torno de 128 e o negativo inverte a distribuicao.

## 6. Limitacoes

* As operacoes da M1.2 foram desenvolvidas para imagens em tons de cinza de 8 bits, com intensidades entre 0 e 255.
* As transformacoes de brilho, contraste, negativo e threshold exigem uma imagem em tons de cinza.
* O contraste exige `alpha > 0`.
* O threshold e limitado ao intervalo de 0 a 255.
* O histograma implementado possui exatamente 256 posicoes, considerando imagens de 8 bits.
* Valores resultantes das transformacoes sao saturados para permanecer na faixa de 0 a 255.
* A implementacao nao utiliza funcoes prontas de processamento para realizar diretamente as transformacoes exigidas pelo laboratorio.

## 7. Referencias

* Material e roteiro disponibilizados na disciplina de Processamento de Imagens.
* Documentacao da biblioteca OpenCV.
* Documentacao da biblioteca NumPy.
* Documentacao do framework pytest.
