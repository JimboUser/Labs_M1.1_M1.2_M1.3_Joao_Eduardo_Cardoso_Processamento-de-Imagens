# Laboratórios M2.1 e M2.2 — Processamento Digital de Imagens

## 1. Visão geral

Este documento descreve as atividades M2.1 e M2.2 do projeto de Processamento Digital de Imagens (PDI), desenvolvido em Python.

A atividade M2.1 aborda a segmentação de imagens por limiarização fixa e pelo espaço de cores HSV, com o objetivo de gerar máscaras binárias que destaquem regiões de interesse.

A atividade M2.2 utiliza essas máscaras como entrada para analisar componentes conexos, aplicar filtragem por área mínima e avaliar os efeitos de operações morfológicas sobre a conectividade e a área das regiões segmentadas.

As implementações são disponibilizadas por meio de uma interface de linha de comando (CLI), permitindo executar as operações com diferentes imagens e parâmetros.

## 2. Tecnologias utilizadas

- Python 3.10 ou superior.
- OpenCV (`opencv-python-headless`).
- NumPy.
- pytest.
- Ambiente virtual Python (`venv`).

O ambiente utilizado durante os experimentos foi o Python 3.12.5.

## 3. Estrutura do projeto

A estrutura relevante para as atividades M2 é apresentada a seguir:

```text
python/
├── configs/
│   └── morphology.json
├── images/
│   ├── input/
│   ├── output/
│   └── reference/
├── kernels/
├── results/
├── src/
│   └── pdi_lab/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── contract.py
│       ├── errors.py
│       ├── exit_code.py
│       ├── image_io.py
│       ├── kernel.py
│       ├── operations.py
│       ├── parameters.py
│       └── result_io.py
├── tests/
│   ├── sobreposicao.py
│   ├── test_analyze.py
│   ├── test_cli.py
│   ├── test_infrastructure.py
│   ├── test_m1_1.py
│   ├── test_m1_2.py
│   ├── test_m1_3.py
│   └── test_segment.py
├── AI_USAGE.md
├── lab.json
├── pyproject.toml
├── README.md
├── README_M2.md
├── REPORTM1.md
├── REPORTM1_2.md
├── REPORTM1_3.md
├── REPORTM2.md
└── requirements.txt
```

### Diretórios principais

- `src/pdi_lab/`: implementação do pacote, das operações de processamento de imagens e da CLI.
- `tests/`: testes automatizados das operações e da infraestrutura.
- `images/input/`: imagens utilizadas como entrada nos experimentos.
- `images/output/`: máscaras e imagens produzidas pelas operações.
- `images/reference/`: diretório destinado a imagens de referência.
- `configs/`: arquivos de configuração, incluindo os parâmetros morfológicos.
- `kernels/`: diretório destinado aos arquivos relacionados a núcleos de convolução.
- `results/`: resultados da análise de componentes conexos, incluindo imagens, arquivos CSV e resumos JSON.

## 4. Instalação e configuração

### 4.1. Requisitos

É necessário ter uma instalação compatível do Python 3.10 ou superior.

No Windows, recomenda-se utilizar uma distribuição oficial do CPython para Windows, conforme as observações presentes em `requirements.txt`.

### 4.2. Criar e ativar o ambiente virtual

Execute os comandos abaixo no PowerShell, a partir do diretório `python/`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4.3. Instalar as dependências

Com o ambiente virtual ativado:

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
```

O arquivo `requirements.txt` especifica as dependências utilizadas pelo projeto e pelos testes automatizados. O comando `pip install -e .` instala o pacote em modo editável.

### 4.4. Verificar a instalação

Para conferir os comandos disponíveis na interface de linha de comando:

```powershell
python -m pdi_lab --help
```

Para executar os testes automatizados:

```powershell
python -m pytest -v
```

## 5. Atividade M2.1 — Segmentação de imagens

### 5.1. Objetivo

A atividade M2.1 consiste em implementar e comparar métodos de segmentação capazes de separar regiões de interesse do fundo da imagem por meio da geração de máscaras binárias.

Foram utilizados dois métodos principais:

- **Limiarização fixa:** aplica um valor de limiar à intensidade dos pixels.
- **Segmentação HSV:** seleciona pixels com base em intervalos de matiz, saturação e valor.

Os experimentos utilizaram imagens de limões e laranjas para avaliar o comportamento dos métodos em diferentes condições de cor e contraste.

### 5.2. Segmentação por limiarização fixa

A limiarização fixa classifica os pixels de acordo com sua intensidade e um valor de limiar previamente definido.

Para executar a segmentação com limiar fixo, utilize:

```powershell
python -m pdi_lab --input images/input/limoes.png --output images/output/limoes_fixed.png --operation segment --method fixed --threshold 160
```

O parâmetro `--threshold` define o limiar utilizado na classificação.

Com a configuração binária convencional do OpenCV, pixels com intensidade superior ao limiar recebem valor 255, enquanto pixels com intensidade igual ou inferior recebem valor 0. Com a opção `--invert`, a classificação é invertida.

Exemplo com inversão:

```powershell
python -m pdi_lab --input images/input/laranjas.png --output images/output/laranjas_fixed_invert.png --operation segment --method fixed --threshold 160 --invert
```

### 5.3. Segmentação pelo espaço de cores HSV

O espaço HSV representa as cores por matiz (*Hue*), saturação (*Saturation*) e valor (*Value*). Essa representação permite selecionar intervalos de cores sem depender exclusivamente da intensidade dos pixels.

Para executar a segmentação HSV:

```powershell
python -m pdi_lab --input images/input/limoes.png --output images/output/limoes_hsv.png --operation segment --method hsv
```

Os parâmetros de seleção de cores podem ser definidos por meio dos seguintes argumentos:

- `--h_min` e `--h_max`: limites da matiz.
- `--s_min` e `--s_max`: limites da saturação.
- `--v_min` e `--v_max`: limites do valor.

Nos experimentos com as laranjas, foram utilizados os intervalos de referência H = 5–30, S = 60–255 e V = 40–255.

Esses valores constituem uma configuração experimental, não uma regra universal para a segmentação de frutas. Os resultados podem variar conforme a iluminação, as cores do fundo e as características da imagem.

### 5.4. Resultados experimentais

A comparação entre os métodos demonstrou diferenças significativas na quantidade de pixels classificados como primeiro plano.

| Imagem | Método | Pixels brancos | Proporção |
|---|---|---:|---:|
| Limões | Limiar fixo, 160 | 642.379 | 96,31% |
| Limões | HSV | 374.549 | 56,15% |
| Laranjas | Limiar fixo, 160 | 666.846 | 99,98% |
| Laranjas | HSV | 91.407 | 13,70% |
| Laranjas | Limiar fixo, 160, invertido | 154 | 0,02% |

Os valores correspondem aos resultados obtidos nos experimentos registrados no relatório M2.

A limiarização fixa com valor 160 classificou praticamente toda a imagem como primeiro plano em ambas as imagens. Já a segmentação HSV produziu máscaras mais seletivas, preservando regiões de interesse de forma mais adequada para a etapa seguinte.

A segmentação HSV também apresentou limitações: regiões do fundo com cores semelhantes às dos objetos podem ser incorporadas à máscara, enquanto partes dos objetos podem deixar de ser selecionadas.

### 5.5. Conclusão da M2.1

A segmentação HSV foi selecionada como ponto de partida para a atividade M2.2 por apresentar resultados mais promissores do que o limiar fixo com valor 160 nos experimentos realizados.

Embora a segmentação ainda apresente limitações, as máscaras geradas permitem investigar a detecção de componentes conexos, a aplicação de filtros por área e os efeitos das operações morfológicas.

## 6. Atividade M2.2 — Análise de componentes conexos e morfologia

### 6.1. Objetivo

A atividade M2.2 investiga a análise de componentes conexos em máscaras binárias e avalia como operações morfológicas podem modificar a conectividade e a área das regiões classificadas como primeiro plano.

Os experimentos utilizam as máscaras HSV geradas na atividade M2.1 para as imagens de limões e laranjas.

As principais etapas são:

1. Identificação dos componentes conexos.
2. Filtragem dos componentes pela área mínima.
3. Aplicação de operações morfológicas.
4. Comparação das áreas e quantidades de componentes antes e depois do processamento.
5. Geração de imagens, arquivos CSV e resumos JSON.

### 6.2. Executar a análise

Os comandos abaixo executam a análise das máscaras previamente geradas:

```powershell
python -m pdi_lab --input images/output/limoes_hsv.png --output results/limoes_hsv --operation analyze --connectivity 8 --min-area 20 --config configs/morphology.json
```

```powershell
python -m pdi_lab --input images/output/laranjas_hsv.png --output results/laranjas_hsv --operation analyze --connectivity 8 --min-area 20 --config configs/morphology.json
```

Os parâmetros utilizados são:

- `--operation analyze`: executa a análise de componentes conexos e o processamento associado.
- `--connectivity 8`: considera vizinhos horizontais, verticais e diagonais na identificação dos componentes.
- `--min-area 20`: define a área mínima utilizada na filtragem dos componentes.
- `--config configs/morphology.json`: carrega a configuração das operações morfológicas.

A sequência configurada utiliza um elemento estruturante elíptico de tamanho 3, com uma iteração por operação, aplicando abertura (*opening*) seguida de fechamento (*closing*).

### 6.3. Conectividade

A conectividade determina quais pixels são considerados vizinhos durante a identificação dos componentes conexos.

Na conectividade 4, são considerados os vizinhos horizontais e verticais. Na conectividade 8, também são considerados os vizinhos diagonais.

Consequentemente, dois pixels que se tocam apenas diagonalmente podem pertencer a componentes diferentes com conectividade 4 e ao mesmo componente com conectividade 8.

Essa diferença influencia a contagem de componentes, especialmente quando os objetos estão próximos ou apresentam regiões de contato.

### 6.4. Filtragem por área mínima

A filtragem por área mínima permite desconsiderar componentes menores que o valor definido em `--min-area`.

No experimento, foi utilizado o valor 20. O objetivo é reduzir a influência de pequenas regiões isoladas que podem corresponder a ruídos na máscara.

A filtragem dos componentes não deve ser confundida com uma operação morfológica: ela seleciona quais componentes serão considerados na análise, enquanto a morfologia modifica a máscara binária.

### 6.5. Operações morfológicas

As operações morfológicas utilizam um elemento estruturante para modificar a forma das regiões de primeiro plano.

**Abertura (*opening*)**

Consiste em uma erosão seguida de uma dilatação. Pode remover pequenas regiões de primeiro plano e reduzir conexões estreitas, dependendo da geometria dos objetos e do elemento estruturante.

**Fechamento (*closing*)**

Consiste em uma dilatação seguida de uma erosão. Pode preencher pequenas lacunas e conectar regiões próximas, dependendo da configuração utilizada.

Os efeitos não são necessariamente benéficos em todos os casos. Uma operação pode remover pixels relevantes, unir objetos distintos ou modificar contornos.

### 6.6. Resultados experimentais

Os resultados foram obtidos a partir dos arquivos JSON gerados pela execução da análise, utilizando conectividade 8 e área mínima de 20 pixels.

| Métrica | Limões | Laranjas |
|---|---:|---:|
| Componentes iniciais brutos | 21 | 1 |
| Componentes após filtragem inicial | 2 | 1 |
| Área inicial do primeiro plano | 374.549 px | 91.407 px |
| Componentes após abertura | 3 | 2 |
| Área após abertura | 374.443 px | 91.272 px |
| Componentes após fechamento | 2 | 1 |
| Área final do primeiro plano | 374.485 px | 91.485 px |
| Componentes finais após filtragem | 2 | 1 |

A contagem inicial dos limões foi de 26 componentes com conectividade 4 e 21 com conectividade 8. Essa diferença demonstra a influência da conectividade na identificação de regiões que se tocam diagonalmente.

Para os limões, a abertura reduziu a área do primeiro plano de 374.549 para 374.443 pixels. O fechamento elevou a área para 374.485 pixels. Ao final, permaneceram dois componentes.

Para as laranjas, a máscara inicial apresentou um único componente com conectividade 8, apesar de a imagem conter três frutas. Após a abertura, foram identificados dois componentes; depois do fechamento, a máscara voltou a apresentar um único componente.

Esses resultados indicam que as regiões das frutas podem estar conectadas na máscara binária, impedindo que cada fruta seja representada por um componente independente.

### 6.7. Arquivos de saída

A execução da análise gera arquivos associados ao prefixo especificado em `--output`.

Para cada conjunto de resultados, são produzidos arquivos com as seguintes finalidades:

| Arquivo ou sufixo | Finalidade |
|---|---|
| `_initial.png` | Representa a máscara inicial utilizada na análise. |
| `_stage_01_open.png` | Representa a máscara após a abertura morfológica. |
| `_stage_02_close.png` | Representa a máscara após o fechamento morfológico. |
| `_final.png` | Representa a máscara final do processamento. |
| `_initial_labels.png` | Visualiza os componentes identificados na etapa inicial. |
| `_labels.png` | Visualiza os componentes da etapa final. |
| `_initial.csv` | Registra os dados dos componentes iniciais. |
| `_final.csv` | Registra os dados dos componentes finais. |
| `_summary.json` | Reúne os parâmetros e as estatísticas da execução. |

Os arquivos CSV e JSON permitem comparar os resultados quantitativamente, enquanto as imagens possibilitam a inspeção visual das mudanças na máscara.

### 6.8. Conclusão da M2.2

Os experimentos demonstraram que a análise de componentes conexos depende tanto da qualidade da máscara binária inicial quanto da conectividade adotada. Na imagem dos limões, a contagem passou de 21 componentes com conectividade 8 para dois após a sequência morfológica. Na imagem das laranjas, permaneceu um único componente, evidenciando que regiões pertencentes a frutas distintas podem estar conectadas na máscara.

A filtragem por área mínima permitiu distinguir componentes relevantes de pequenas regiões, sem modificar diretamente a máscara. As operações de abertura e fechamento também alteraram a área e a conectividade do primeiro plano, mas essas mudanças não representam necessariamente uma melhoria da segmentação.

Conclui-se que a morfologia pode auxiliar na redução de ruídos e na modificação de pequenas lacunas e conexões, porém seus efeitos dependem da máscara inicial e dos parâmetros utilizados. A contagem de componentes, isoladamente, não garante a identificação correta de cada objeto físico. A separação de frutas em contato e a correção de regiões do fundo incorporadas à máscara podem exigir técnicas complementares.

## 7. Testes automatizados

Os testes são executados por meio do pytest:

```powershell
python -m pytest -v
```

Para executar somente os testes de análise de componentes conexos:

```powershell
python -m pytest -v tests/test_analyze.py
```

Para executar somente os testes de segmentação:

```powershell
python -m pytest -v tests/test_segment.py
```

Na execução registrada durante o desenvolvimento, a suíte completa apresentou **62 testes aprovados**, sem falhas.

Esse resultado indica que os testes automatizados passaram no ambiente utilizado durante a validação. A quantidade de testes poderá variar caso a suíte seja modificada posteriormente.

## 8. Observações e limitações

Os resultados dependem das imagens de entrada, dos parâmetros de segmentação, da conectividade e da configuração morfológica.

Em particular:

- A limiarização fixa pode classificar grandes regiões do fundo como primeiro plano.
- A segmentação HSV depende dos intervalos de cor selecionados e das condições de iluminação.
- A conectividade 4 ou 8 pode produzir contagens diferentes para a mesma máscara.
- A filtragem por área mínima pode remover componentes pequenos que sejam relevantes para outras imagens.
- As operações morfológicas podem modificar a área, os contornos e a conectividade dos objetos.
- Um componente conexo não corresponde necessariamente a um único objeto físico.

Por esses motivos, a avaliação deve considerar tanto as métricas numéricas quanto a inspeção visual das imagens geradas.

## 9. Relatório técnico

O relatório técnico das atividades M2.1 e M2.2 está disponível em [REPORTM2.md](REPORTM2.md).

O documento apresenta a metodologia, os experimentos realizados, os resultados observados e as conclusões obtidas durante o desenvolvimento.

## 10. Referências

- [OpenCV — Structural Analysis and Shape Descriptors](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html)
- [OpenCV — Morphological Transformations](https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html)
- [pytest — Documentação oficial](https://docs.pytest.org/)