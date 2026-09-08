# Processamento de Imagens — Laboratórios M1

Implementação dos Laboratórios M1.1, M1.2 e M1.3 da disciplina de Processamento de Imagens (PDI), desenvolvida em Python a partir da infraestrutura do projeto-base fornecido pelo professor.

O projeto reúne operações de representação de imagens, transformações de intensidade e filtragem espacial, além dos respectivos testes e resultados.

---

# 1. Laboratórios implementados

## M1.1 — Representação, canais e níveis de cinza

Operações implementadas:

* inspeção de imagens;
* cópia manual;
* separação manual dos canais B, G e R;
* conversão para níveis de cinza por média simples;
* conversão para níveis de cinza por média ponderada;
* quantização para 16, 8, 4 e 2 níveis.

## M1.2 — Transformações de intensidade

Operações implementadas:

* ajuste de brilho;
* ajuste de contraste;
* negativo;
* limiarização binária;
* histograma manual.

## M1.3 — Convolução e filtragem espacial

Operações implementadas:

* convolução genérica;
* filtro de média `3 × 3`;
* filtro de média `5 × 5`;
* média ponderada;
* Laplaciano;
* realce utilizando o Laplaciano;
* Sobel;
* tratamento de bordas `copy`;
* tratamento de bordas `replicate`.

---

# 2. Objetivo

O projeto tem como objetivo implementar operações fundamentais de Processamento de Imagens utilizando acesso e manipulação explícita dos pixels.

As operações dos laboratórios foram implementadas manualmente, respeitando as restrições estabelecidas nos respectivos roteiros.

Bibliotecas são utilizadas como suporte para tarefas de infraestrutura, como:

* leitura e escrita de imagens;
* representação das imagens como matrizes;
* acesso aos valores dos pixels;
* execução da aplicação;
* testes automatizados.

As operações avaliadas não são substituídas por funções prontas que executem diretamente os algoritmos solicitados.

---

# 3. Ambiente

## Requisitos

* Python 3.10 ou superior;
* NumPy;
* OpenCV;
* pytest.

O desenvolvimento e os testes foram realizados utilizando **Python 3.12**.

---

# 4. Instalação

É recomendado utilizar um ambiente virtual.

## Windows — PowerShell

Na pasta `python/`:

```powershell
py -3.12 -m venv .venv

.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Instale o projeto em modo editável:

```powershell
python -m pip install -e .
```

Depois da instalação, a aplicação pode ser executada com:

```powershell
python -m pdi_lab --help
```

---

# 5. Estrutura do projeto

```text
python/
├── src/
│   └── pdi_lab/
│       ├── cli.py
│       ├── contract.py
│       ├── errors.py
│       ├── exit_code.py
│       ├── image_io.py
│       ├── kernel.py
│       ├── operations.py
│       ├── parameters.py
│       ├── result_io.py
│       ├── __init__.py
│       └── __main__.py
├── tests/
│   ├── test_cli.py
│   ├── test_infrastructure.py
│   ├── test_m1_1.py
│   ├── test_m1_2.py
│   └── test_m1_3.py
├── images/
│   ├── input/
│   └── output/
├── AI_USAGE.md
├── lab.json
├── pyproject.toml
├── README.md
├── REPORT.md
└── requirements.txt
```

O código-fonte da aplicação está organizado em `src/pdi_lab/`.

Entre os principais módulos estão:

* `operations.py` — implementação das operações dos laboratórios;
* `image_io.py` — leitura e escrita de imagens;
* `kernel.py` — representação, leitura e validação estrutural de kernels;
* `parameters.py` — tratamento dos parâmetros da linha de comando;
* `cli.py` — interface de execução da aplicação;
* `result_io.py` — tratamento dos resultados;
* `errors.py` e `exit_code.py` — tratamento padronizado de erros.

Os testes automatizados estão organizados no diretório `tests/`.

O diretório `images/input/` contém as imagens utilizadas como entrada e `images/output/` contém os resultados gerados pelas operações.

---

# 6. Interface de execução

A aplicação utiliza linha de comando.

Formato geral:

```powershell
python -m pdi_lab --operation <operacao> --input <entrada> --output <saida> [parametros]
```

A operação `inspect` não necessita de arquivo de saída.

Para consultar as operações e parâmetros disponíveis:

```powershell
python -m pdi_lab --help
```

---

# 7. Operações da M1.1

## 7.1 Inspeção

A operação `inspect` apresenta informações da imagem, incluindo:

* largura;
* altura;
* número de canais;
* tipo;
* quantidade de pixels;
* valores mínimo e máximo;
* média das intensidades.

Em imagens coloridas, os valores estatísticos são obtidos separadamente para cada canal.

Exemplo:

```powershell
python -m pdi_lab --operation inspect --input images/input/imagem.png
```

---

## 7.2 Cópia

A operação `copy` cria uma nova imagem e copia os pixels individualmente.

O resultado deve ser numericamente idêntico à imagem de entrada.

```powershell
python -m pdi_lab --operation copy --input images/input/imagem.png --output images/output/copy.png
```

---

## 7.3 Separação de canais

Foram implementadas operações para os canais:

```text
channel_b
channel_g
channel_r
```

Cada operação preserva o canal correspondente e zera os demais.

Exemplo:

```powershell
python -m pdi_lab --operation channel_r --input images/input/imagem.png --output images/output/channel_r.png
```

---

## 7.4 Níveis de cinza

Foram implementadas duas formas de conversão.

### Média simples

```text
g = (R + G + B) / 3
```

### Média ponderada

```text
g = 0,299R + 0,587G + 0,114B
```

Operações:

```text
grayscale_average
grayscale_weighted
```

Exemplo:

```powershell
python -m pdi_lab --operation grayscale_weighted --input images/input/imagem.png --output images/output/gray_weighted.png
```

---

## 7.5 Quantização

A operação `quantize` reduz a quantidade de níveis de intensidade da imagem.

São aceitos:

```text
2
4
8
16
```

níveis.

Exemplo:

```powershell
python -m pdi_lab --operation quantize --input images/input/gray.png --output images/output/quant_8.png --levels 8
```

---

# 8. Operações da M1.2

## 8.1 Brilho

A transformação utilizada é:

```text
g(x,y) = f(x,y) + b
```

O parâmetro `--value` define o valor de `b`.

Exemplo:

```powershell
python -m pdi_lab --operation brightness --input images/input/gray.png --output images/output/brightness.png --value 30
```

Valores positivos aumentam a intensidade e valores negativos diminuem a intensidade.

Os resultados são limitados ao intervalo válido da imagem.

---

## 8.2 Contraste

A transformação utilizada é:

```text
g(x,y) = α(f(x,y) - 128) + 128
```

O parâmetro `--alpha` define o fator de contraste.

Exemplo:

```powershell
python -m pdi_lab --operation contrast --input images/input/gray.png --output images/output/contrast.png --alpha 1.5
```

Foram considerados, entre outros, os valores:

```text
α = 0,5
α = 1,0
α = 1,5
```

---

## 8.3 Negativo

A transformação utilizada é:

```text
g(x,y) = 255 - f(x,y)
```

Exemplo:

```powershell
python -m pdi_lab --operation negative --input images/input/gray.png --output images/output/negative.png
```

---

## 8.4 Limiarização

A limiarização binária utiliza:

```text
g(x,y) = 0,   se f(x,y) < T
g(x,y) = 255, se f(x,y) >= T
```

O parâmetro `--threshold` define o limiar.

Exemplo:

```powershell
python -m pdi_lab --operation threshold --input images/input/gray.png --output images/output/threshold.png --threshold 128
```

---

## 8.5 Histograma

O histograma é calculado manualmente utilizando uma estrutura com 256 posições.

Cada posição representa uma intensidade de `0` a `255` e armazena a quantidade de pixels daquela intensidade.

Exemplo:

```text
intensidade,quantidade

0,12
1,7
2,19
...
255,3
```

A operação também foi utilizada para analisar imagens originais e imagens após transformações de intensidade.

---

# 9. Operações da M1.3

## 9.1 Convolução

A convolução aplica um kernel sobre uma imagem em tons de cinza.

O cálculo é realizado percorrendo explicitamente os pixels da imagem e os elementos da vizinhança correspondente.

Exemplo:

```powershell
python -m pdi_lab --operation convolution --input images/input/gray.png --output images/output/convolution.png --kernel <kernel> --border replicate
```

A implementação utiliza acumuladores em `float64` para preservar os resultados intermediários.

---

## 9.2 Filtro de média

Foram implementados filtros de média com kernels:

```text
3 × 3
5 × 5
```

O tamanho da janela pode ser definido pelo parâmetro `--size`.

Exemplo:

```powershell
python -m pdi_lab --operation mean_filter --input images/input/gray.png --output images/output/mean_3.png --size 3 --border replicate
```

---

## 9.3 Média ponderada

A média ponderada utiliza coeficientes diferentes para as posições da vizinhança.

Um dos kernels utilizados nos testes foi:

```text
1/16  2/16  1/16
2/16  4/16  2/16
1/16  2/16  1/16
```

O pixel central possui maior peso no cálculo.

---

## 9.4 Laplaciano

O Laplaciano é utilizado para destacar transições de intensidade.

O kernel utilizado nos testes foi:

```text
 1  1  1
 1 -8  1
 1  1  1
```

A resposta do filtro é preservada antes da conversão para `uint8`, pois o resultado pode conter valores negativos.

---

## 9.5 Realce com Laplaciano

Além da resposta do Laplaciano, é produzida uma imagem realçada combinando a imagem original com a resposta obtida pelo filtro.

A combinação ocorre antes da conversão final para `uint8`.

Isso permite preservar os valores intermediários durante o cálculo e evitar saturação prematura.

---

## 9.6 Sobel

O operador Sobel foi implementado nas direções `Gx` e `Gy`.

### Gx

```text
-1  0  1
-2  0  2
-1  0  1
```

### Gy

```text
-1 -2 -1
 0  0  0
 1  2  1
```

`Gx` responde principalmente a bordas verticais, enquanto `Gy` responde principalmente a bordas horizontais.

Também são consideradas as magnitudes:

```text
|Gx| + |Gy|
```

e

```text
sqrt(Gx² + Gy²)
```

---

# 10. Tratamento de bordas

As operações de vizinhança utilizam duas estratégias.

## `copy`

Quando a vizinhança completa não cabe na imagem, o valor original do pixel é preservado.

## `replicate`

Quando uma coordenada ultrapassa os limites da imagem, ela é ajustada para a coordenada válida mais próxima.

As diferenças entre as duas estratégias aparecem principalmente nas regiões periféricas da imagem.

---

# 11. Tratamento numérico

Durante os cálculos, são utilizados tipos numéricos adequados para evitar perda de precisão e saturação prematura.

Nas operações de filtragem espacial, os resultados intermediários podem conter:

* valores negativos;
* valores superiores a `255`;
* valores fracionários.

Por isso, os cálculos são realizados em `float64` quando necessário.

A conversão para `uint8` é realizada somente após os cálculos relevantes, limitando os valores ao intervalo:

```text
0 ≤ valor ≤ 255
```

Esse procedimento é especialmente importante para:

* convolução;
* Laplaciano;
* realce;
* Sobel;
* magnitudes do gradiente.

---

# 12. Kernels

O kernel de identidade utilizado nos testes de convolução foi fornecido pelo professor:

```text
3 3
0 0 0
0 1 0
0 0 0
```

Esse kernel deve reproduzir a imagem de entrada quando aplicado corretamente.

Os kernels específicos de operações como média, média ponderada, Laplaciano e Sobel são definidos de acordo com cada operação.

A leitura e validação estrutural dos kernels utilizam a infraestrutura fornecida no projeto-base.

---

# 13. Testes

Os testes específicos dos laboratórios estão organizados no diretório:

```text
tests/
```

Os testes da M1.3 estão em:

```text
tests/test_m1_3.py
```

Para executar todos os testes:

```powershell
python -m pytest
```

Ou, especificamente para a M1.3:

```powershell
python -m pytest tests/test_m1_3.py
```

Os testes incluem casos sintéticos que permitem prever os resultados antes da execução.

Entre os casos utilizados estão:

### M1.1

* cópia de imagem;
* canais;
* conversões para níveis de cinza;
* quantização;
* valores próximos aos limites.

### M1.2

* brilho positivo e negativo;
* contraste reduzido, identidade e ampliado;
* negativo;
* diferentes limiares;
* saturação;
* histogramas antes e depois das transformações.

### M1.3

* kernel identidade;
* imagem constante;
* imagem impulso;
* degrau vertical;
* degrau horizontal;
* conteúdo tocando as bordas;
* kernels `3 × 3`;
* kernels `5 × 5`;
* estratégias `copy` e `replicate`.

---

# 14. Imagens

As imagens utilizadas como entrada estão armazenadas em:

```text
images/input/
```

Os resultados gerados pelas operações estão armazenados em:

```text
images/output/
```

As imagens utilizadas nos testes podem incluir imagens fornecidas pelo projeto-base e imagens sintéticas criadas especificamente para verificar o comportamento dos algoritmos.

---

# 15. Validações e tratamento de erros

A implementação considera situações de entrada inválida e problemas durante o processamento, incluindo:

* falha na leitura da imagem;
* imagem vazia;
* número incompatível de canais;
* parâmetros inválidos;
* quantidade de níveis de quantização inválida;
* valores de limiar inválidos;
* valores inadequados para `alpha`;
* kernel inexistente;
* kernel vazio;
* kernel não quadrado;
* kernel de dimensão par;
* acesso fora dos limites do kernel;
* estratégia de borda inválida;
* valores negativos durante os cálculos;
* valores superiores a `255`;
* conversões numéricas;
* falha na escrita da imagem.

---

# 16. Reprodutibilidade

As operações são executadas por linha de comando e utilizam caminhos fornecidos pelos argumentos da aplicação.

A mesma operação, executada com:

* a mesma imagem de entrada;
* os mesmos parâmetros;
* o mesmo kernel;
* a mesma estratégia de borda;
* o mesmo código;

deve produzir o mesmo resultado.

Não são utilizadas entradas interativas ou números aleatórios nas operações dos laboratórios.

---

# 17. Relatório

A análise dos laboratórios e dos resultados obtidos está disponível em:

```text
REPORT.md
```

O relatório apresenta os objetivos, operações implementadas, testes realizados, resultados observados e análise técnica das atividades.

---

# 18. Uso de Inteligência Artificial

A declaração sobre a utilização de ferramentas de Inteligência Artificial generativa durante o desenvolvimento do projeto está disponível em:

```text
AI_USAGE.md
```

---

# 19. Projeto-base

Este projeto utiliza a infraestrutura fornecida no projeto-base da disciplina.

Componentes como a interface de linha de comando, leitura e escrita de imagens, validações gerais, leitura estrutural de kernels e infraestrutura de resultados foram aproveitados conforme a organização fornecida.

As implementações específicas dos laboratórios foram desenvolvidas sobre essa infraestrutura.

A documentação original do projeto-base e o contrato técnico geral da M1 permanecem disponíveis na raiz do projeto.

---

# 20. Checklist

Antes da entrega, foram consideradas as seguintes verificações:

* [x] projeto executável pela linha de comando;
* [x] dependências especificadas;
* [x] operações da M1.1 implementadas;
* [x] operações da M1.2 implementadas;
* [x] operações da M1.3 implementadas;
* [x] tratamento de bordas implementado;
* [x] testes específicos realizados;
* [x] imagens de entrada organizadas;
* [x] imagens de saída organizadas;
* [x] relatório preenchido;
* [x] declaração de uso de IA preenchida;
* [x] caminhos absolutos evitados;
* [x] cálculos numéricos realizados com tipos adequados.
