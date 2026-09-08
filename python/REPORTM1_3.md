# Mini relatório - Laboratório M1.3

## Identificação

* Estudante: João Eduardo
* Matrícula: 7937857
* Laboratório: M1.3 — Operações de vizinhança
* Linguagem: Python

## 1. Objetivo

O objetivo do laboratório foi implementar operações de processamento de imagens baseadas em vizinhança, utilizando kernels para modificar cada pixel a partir dos valores dos pixels ao seu redor. Foram trabalhados filtros de média, média ponderada, Laplaciano e Sobel, além do tratamento das bordas e da conversão dos resultados para visualização.

## 2. Operações implementadas

Foram implementadas as seguintes operações:

* **Convolução:** percorre os pixels da imagem e aplica os coeficientes de um kernel sobre sua vizinhança.
* **Filtro de média:** utiliza kernels de tamanho 3×3 ou 5×5, com todos os coeficientes iguais.
* **Média ponderada:** permite utilizar um kernel com diferentes pesos para cada posição da vizinhança.
* **Laplaciano:** utiliza um kernel com valores positivos e negativos para destacar regiões de transição na imagem.
* **Sharpen com Laplaciano:** utiliza a resposta do Laplaciano para aumentar a nitidez da imagem.
* **Sobel:** utiliza os kernels `Gx` e `Gy` para detectar variações principalmente nas direções vertical e horizontal, respectivamente.

A convolução foi implementada com percurso explícito dos pixels e dos elementos do kernel. Foram utilizadas duas estratégias de tratamento das bordas: **COPY**, que mantém o valor original quando a vizinhança completa não cabe na imagem, e **REPLICATE**, que utiliza o valor do pixel mais próximo quando a vizinhança ultrapassa os limites.

Os cálculos são mantidos em `float64`, permitindo valores negativos ou superiores a 255 durante o processamento. A saturação para o intervalo de 0 a 255 é realizada somente no momento da conversão para a imagem de saída.

## 3. Testes realizados

Foram utilizados casos sintéticos pequenos, permitindo prever o comportamento esperado antes da execução.

| Teste                        | Entrada                                                | Operação        | Parâmetros                    | Resultado esperado ou critério de verificação                                                                           |
| ---------------------------- | ------------------------------------------------------ | --------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Kernel identidade            | Imagem 3×3                                             | Convolução      | Kernel identidade 3×3, `copy` | A saída deve ser igual à entrada.                                                                                       |
| Imagem 1..9                  | Imagem 3×3                                             | Convolução      | Média 3×3, `replicate`        | A saída deve corresponder às médias calculadas manualmente considerando a replicação das bordas.                        |
| Impulso central              | Imagem 3×3                                             | Média           | Kernel 3×3                    | O valor central deve ser distribuído pela vizinhança.                                                                   |
| Impulso central              | Imagem 5×5                                             | Média           | Kernel 5×5                    | O valor do impulso deve ser distribuído entre os pixels considerados pela operação.                                     |
| Imagem constante             | Imagem 5×5 com valor 100                               | Média           | Kernel 3×3, `replicate`       | A imagem deve permanecer constante, com valor 100.                                                                      |
| Média ponderada              | Imagem com impulso central                             | Média ponderada | Kernel ponderado 3×3          | O valor central deve receber o peso correspondente ao centro do kernel.                                                 |
| Impulso central              | Imagem 3×3                                             | Laplaciano      | Kernel Laplaciano 3×3         | A resposta central deve ser negativa, enquanto os demais pixels devem permanecer zerados neste caso.                    |
| Impulso central              | Imagem 3×3                                             | Sharpen         | Laplaciano, `copy`            | A operação deve utilizar a resposta do Laplaciano para reforçar o pixel central.                                        |
| Degrau vertical              | Imagem 3×3 com colunas 0, 0 e 255                      | Sobel           | `copy`                        | `Gx` deve apresentar resposta forte na transição vertical, enquanto `Gy` deve apresentar resposta menor nessa região.   |
| Degrau horizontal            | Imagem 3×3 com linhas 0, 0 e 255                       | Sobel           | `copy`                        | `Gy` deve apresentar resposta forte na transição horizontal e `Gx` deve ser zero no centro.                             |
| Imagem com conteúdo na borda | Imagem 3×3 com pixels de 255 nas posições de interesse | Média           | Kernel 3×3, `copy`            | Os pixels de borda devem ser preservados, enquanto os pixels internos podem ser influenciados pelo conteúdo das bordas. |
| Kernel 5×5                   | Imagem sintética                                       | Média           | Kernel 5×5                    | A operação deve considerar uma vizinhança maior que a utilizada pelo kernel 3×3.                                        |

Os testes foram automatizados com `pytest` e utilizam `numpy` para construir as imagens e verificar os resultados esperados.

## 4. Resultados

Os resultados foram gerados utilizando as imagens e parâmetros previstos pelo laboratório, além dos casos sintéticos utilizados nos testes automatizados.

| Operação        | Entrada         | Parâmetros                | Arquivo de saída    | Observação                                                              |
| --------------- | --------------- | ------------------------- | ------------------- | ----------------------------------------------------------------------- |
| Convolução      | Imagem de teste | Kernel identidade, `copy` | Saída da convolução | A saída reproduziu a imagem de entrada.                                 |
| Filtro de média | Imagem de teste | 3×3                       | Saída do filtro     | Houve suavização das variações locais.                                  |
| Filtro de média | Imagem de teste | 5×5                       | Saída do filtro     | A suavização foi maior devido à vizinhança ampliada.                    |
| Média ponderada | Imagem de teste | Kernel ponderado 3×3      | Saída do filtro     | O peso maior no centro influencia mais o pixel central.                 |
| Laplaciano      | Imagem de teste | Kernel Laplaciano 3×3     | Saída do Laplaciano | Foram obtidas respostas positivas e negativas nas regiões de transição. |
| Sharpen         | Imagem de teste | Laplaciano                | Saída sharpen       | A resposta do Laplaciano foi utilizada para reforçar detalhes.          |
| Sobel           | Imagem de teste | `Gx` e `Gy`, `copy`       | Saídas Sobel        | `Gx` e `Gy` permitiram observar as respostas direcionais das bordas.    |

Nos testes sintéticos, os resultados foram comparados diretamente com valores esperados calculados previamente. Também foram comparadas as duas formas de magnitude do Sobel: `|Gx| + |Gy|` e `sqrt(Gx² + Gy²)`.

## 5. Análise técnica

### 1. Qual é a diferença entre uma operação pontual e uma operação de vizinhança?

Uma operação pontual utiliza somente o valor do próprio pixel para calcular o resultado. Já uma operação de vizinhança utiliza o pixel e outros pixels ao seu redor. As operações implementadas neste laboratório, como média, Laplaciano e Sobel, são operações de vizinhança porque dependem dos valores presentes no kernel e na região ao redor de cada pixel.

### 2. Por que kernels normalmente possuem dimensões ímpares?

Dimensões ímpares permitem definir uma posição central para o kernel. Assim, em um kernel 3×3, por exemplo, existe um pixel central e a vizinhança possui a mesma quantidade de posições em cada direção.

### 3. Qual é o efeito de aumentar o tamanho do kernel de média?

Aumentar o kernel faz com que uma região maior da imagem participe do cálculo da média. Como consequência, ocorre maior suavização das variações locais e dos detalhes. Nos testes realizados, o kernel 5×5 considera uma vizinhança maior que o kernel 3×3 e tende a produzir um efeito de suavização mais forte.

### 4. Como a estratégia de tratamento de bordas interfere no resultado?

A estratégia define como a operação deve agir quando a vizinhança ultrapassa os limites da imagem. Na estratégia `COPY`, o pixel original é mantido quando o kernel não cabe completamente naquela posição. Na estratégia `REPLICATE`, os pixels que ficariam fora da imagem são substituídos pelo valor do pixel mais próximo da borda.

Por isso, as diferenças entre as estratégias aparecem principalmente nas regiões periféricas da imagem.

### 5. Por que a resposta bruta do Laplaciano pode conter valores negativos?

O kernel do Laplaciano possui coeficientes positivos e negativos. Durante a soma ponderada, os valores negativos podem fazer com que o resultado final também seja negativo. Esses valores são válidos durante o processamento e não devem ser descartados antes da visualização.

### 6. Qual é a diferença entre `Gx` e `Gy` no Sobel?

`Gx` mede principalmente variações na direção horizontal do cálculo do gradiente, sendo utilizado para destacar bordas verticais. `Gy` mede principalmente variações na direção vertical do cálculo do gradiente, destacando bordas horizontais.

Nos testes com degraus vertical e horizontal, foi possível verificar essa diferença nas respostas dos dois kernels.

### 7. Que diferenças são observadas entre `|Gx| + |Gy|` e `sqrt(Gx² + Gy²)`?

`|Gx| + |Gy|` é uma aproximação mais simples da magnitude do gradiente e corresponde à soma das magnitudes das duas componentes. Já `sqrt(Gx² + Gy²)` calcula a magnitude euclidiana do vetor gradiente.

Os valores da primeira abordagem geralmente são maiores ou iguais aos da magnitude euclidiana para as mesmas componentes, enquanto a segunda representa diretamente o comprimento do vetor formado por `Gx` e `Gy`.

## 6. Limitações

A implementação possui algumas limitações definidas pelas regras do laboratório. O filtro de média aceita somente kernels de tamanho 3×3 e 5×5. Além disso, as estratégias de borda disponíveis são somente `copy` e `replicate`.

A estratégia `COPY` não realiza preenchimento da imagem; quando a vizinhança não cabe completamente, o pixel original é preservado. Dessa forma, a região de borda possui comportamento diferente da região interna.

Outra decisão da implementação é manter os resultados das operações em `float64` durante o processamento. A conversão para valores de 8 bits e a saturação entre 0 e 255 são realizadas posteriormente, no momento apropriado para geração da imagem de saída.

## 7. Referências

* Material e roteiro disponibilizados na disciplina de Processamento de Imagens.
* Documentacao da biblioteca OpenCV.
* Documentacao da biblioteca NumPy.
* Documentacao do framework pytest.

