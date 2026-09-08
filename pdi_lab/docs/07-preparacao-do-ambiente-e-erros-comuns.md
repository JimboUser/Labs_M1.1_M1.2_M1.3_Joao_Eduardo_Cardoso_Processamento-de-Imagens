# Preparação do ambiente e solução de problemas

Este guia reúne os principais cuidados de instalação, configuração, `PATH`, ambientes virtuais, dependências e diagnóstico para o projeto-base dos laboratórios de Processamento de Imagens.

O projeto oferece três variantes equivalentes:

- C++ com CMake e OpenCV;
- Java com Maven e OpenCV;
- Python com `venv`, `pip`, OpenCV headless e `pytest`.

A escolha da linguagem não altera o contrato do laboratório. Antes de começar a implementar algoritmos, confirme que a infraestrutura da linguagem escolhida funciona corretamente.

---

## 1. Antes de instalar qualquer coisa

Confira o que já existe na máquina:

```bash
git --version
cmake --version
gcc --version
g++ --version
java -version
javac -version
mvn -version
python --version
py --version
```

Nem todos esses comandos precisam existir: use apenas os relacionados à linguagem escolhida.

Uma regra importante de diagnóstico é conferir **qual executável está sendo usado de fato**.

Em terminais Unix-like:

```bash
which cmake
which gcc
which g++
which java
which javac
which mvn
which python
```

No PowerShell:

```powershell
Get-Command cmake
Get-Command java
Get-Command mvn
Get-Command python
```

Isso é especialmente importante quando existem duas ou mais instalações da mesma ferramenta.

---

## 2. Windows, MSYS2 e UCRT64

Para a variante C++, o ambiente de referência no Windows é o **MSYS2 UCRT64**.

Confirme:

```bash
echo $MSYSTEM
```

Esperado:

```text
UCRT64
```

Também confira:

```bash
which gcc
which g++
```

Os compiladores devem apontar para caminhos relacionados a `/ucrt64/bin`.

Pacotes específicos desse ambiente normalmente usam o prefixo:

```text
mingw-w64-ucrt-x86_64-
```

Nem toda ferramenta do projeto precisa ser instalada pelo `pacman`. Java e Python merecem atenção especial nesse ponto.

---

## 3. C++: configuração recomendada

A variante C++ utiliza MSYS2 UCRT64, GCC/G++, CMake, Ninja, OpenCV e CTest.

Na pasta `cpp/`:

```bash
cmake --list-presets
cmake --preset ucrt64-debug
cmake --build --preset ucrt64-debug
ctest --preset ucrt64-debug
```

Depois:

```bash
./build/ucrt64-debug/pdi_lab.exe --version
./build/ucrt64-debug/pdi_lab.exe --help
```

As etapas são diferentes:

- `cmake --preset ...`: configura o projeto;
- `cmake --build ...`: compila;
- `ctest --preset ...`: executa os testes.

Se houver comportamento estranho depois de alterar configuração, recrie o diretório de build:

```bash
rm -rf build/ucrt64-debug
cmake --preset ucrt64-debug
cmake --build --preset ucrt64-debug
```

### Erros comuns no C++

**Terminal MSYS2 errado.** Verifique `echo $MSYSTEM`. Evite misturar UCRT64, MINGW64, CLANG64 e bibliotecas construídas para toolchains incompatíveis.

**OpenCV encontrado em instalação incorreta.** Durante o CMake, observe o caminho informado para o OpenCV. No ambiente recomendado, ele deve ser coerente com UCRT64.

**Build antigo.** Limpe apenas o diretório de build e configure novamente; não apague o código-fonte.

---

## 4. Java: JDK e Maven no Windows

No Windows, Java e Maven **não precisam ser instalados pelo `pacman` do UCRT64**.

A estratégia recomendada é usar:

- JDK para Windows;
- Maven para Windows;
- ambos disponíveis no `PATH`.

Eles podem ser usados a partir do UCRT64, PowerShell ou CMD.

Verifique:

```bash
java -version
javac -version
mvn -version
```

E, no UCRT64:

```bash
which java
which javac
which mvn
```

Para desenvolver, é necessário um **JDK**, não apenas um runtime. Se `java` funcionar e `javac` não, revise a instalação.

`JAVA_HOME` pode apontar para a raiz do JDK, por exemplo:

```text
C:\Program Files\Java\jdk-21
```

Depois de alterar `PATH` ou `JAVA_HOME`, feche e abra novamente o terminal.

Na pasta `java/`:

```bash
mvn clean test
mvn package
java -jar target/pdi-lab.jar --version
java -jar target/pdi-lab.jar --help
```

### Erro de XML no `pom.xml`

Um erro como:

```text
Non-parseable POM
```

acontece antes da compilação Java. Durante a validação do template encontramos um caso causado por comentário XML contendo a sequência inválida `--`. A versão distribuída já contém a correção, mas a lição de diagnóstico permanece: um `Non-parseable POM` aponta primeiro para o `pom.xml`, não para o algoritmo.

---

## 5. Python: escolha correta do interpretador no Windows

No Windows podem coexistir vários Python:

- CPython para Windows;
- Python do MSYS2/UCRT64;
- Python instalado por IDEs ou outras ferramentas;
- Python de um ambiente virtual.

Para este projeto, use **CPython para Windows**.

Antes de criar o ambiente virtual:

```bash
python --version
which python
py --version
py -0p
```

Durante a validação, um `.venv` criado com Python/MSYS2 fez o `pip` tentar compilar o OpenCV localmente. Isso puxou uma cadeia desnecessária de CMake, Visual Studio, compiladores, OpenBLAS, Fortran e outras dependências.

Queremos um wheel pré-compilado para Windows. Um bom sinal é aparecer algo terminado em:

```text
win_amd64.whl
```

Um sinal de alerta é:

```text
Building wheel for opencv-python-headless
```

Nesse caso, confira imediatamente qual Python está em uso.

---

## 6. Python: criando o `.venv`

Na pasta `python/`:

```bash
py -3.13 -m venv .venv
```

Use outra versão compatível se necessário.

No MSYS2/Git Bash:

```bash
source .venv/Scripts/activate
```

No PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Depois confira:

```bash
python --version
python -c "import sys; print(sys.executable)"
```

No Windows, o esperado é um caminho semelhante a:

```text
...\python\.venv\Scripts\python.exe
```

Se aparecer `.venv/bin/` em uma instalação Windows, verifique se o ambiente não foi criado com Python/MSYS2.

Instale:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

E teste:

```bash
python -m pytest
python -m pdi_lab --version
python -m pdi_lab --help
```

### Erro `No module named pdi_lab`

Se as dependências foram instaladas, mas ocorrer:

```text
No module named pdi_lab
```

execute:

```bash
python -m pip install -e .
```

O papel de cada comando é diferente:

```text
requirements.txt -> dependências externas
pip install -e . -> registra o próprio projeto local
```

Se o ambiente virtual foi criado com o Python errado, não tente migrá-lo alterando apenas o `PATH`. Remova `.venv`, recrie-o com o interpretador correto e reinstale as dependências.

---

## 7. OpenCV headless no Python

O projeto utiliza `opencv-python-headless` porque a interface gráfica do OpenCV não é necessária para o contrato dos laboratórios.

A estratégia é ler imagens de arquivo, processar os dados e gravar os resultados. Isso favorece terminal, reprodutibilidade, correção automatizada e máquinas sem ambiente gráfico.

Evite instalar simultaneamente `opencv-python` e `opencv-python-headless` no mesmo ambiente sem uma necessidade específica.

---

## 8. `PATH`: causa frequente de erros

Quando uma ferramenta parece instalada, mas o terminal não a encontra, verifique:

1. se o diretório está no `PATH`;
2. se o terminal foi aberto antes da alteração do `PATH`;
3. se outra instalação está sendo encontrada primeiro;
4. se o ambiente virtual está ativado;
5. se o terminal MSYS2 correto está sendo usado.

Use:

```bash
which python
which java
which mvn
which cmake
```

ou no PowerShell:

```powershell
Get-Command python
Get-Command java
Get-Command mvn
Get-Command cmake
```

---

## 9. Caminhos e pasta atual

No MSYS2, um caminho Windows como:

```text
C:\Users\aluno\projeto
```

pode aparecer como:

```text
/c/Users/aluno/projeto
```

Isso é normal.

Muitos comandos pressupõem que você está dentro da pasta da linguagem escolhida. Se um arquivo existe, mas o programa não o encontra, confira:

```bash
pwd
ls
```

No PowerShell:

```powershell
Get-Location
Get-ChildItem
```

Os caminhos como `images/input/...` são relativos ao diretório de trabalho atual.

---

## 10. Códigos de saída

As três variantes usam os mesmos códigos:

| Código | Significado |
|---:|---|
| `0` | sucesso |
| `1` | erro geral |
| `2` | argumentos inválidos ou obrigatórios ausentes |
| `3` | erro de leitura |
| `4` | erro de escrita |
| `5` | parâmetro presente, mas inválido |
| `6` | operação desconhecida |

Em MSYS2/Git Bash, consulte o último código com:

```bash
echo $?
```

Uma imagem ou kernel inexistente deve produzir `read_error` antes de chegar ao algoritmo.

---

## 11. Testes automatizados e testes manuais

C++:

```bash
ctest --preset ucrt64-debug
```

Java:

```bash
mvn test
```

Python:

```bash
python -m pytest
```

Esses testes validam principalmente a infraestrutura. Também execute `--help`, `--version` e alguns casos válidos e inválidos da CLI.

Os testes públicos do template **não substituem os testes dos algoritmos** que serão implementados durante os laboratórios.

---

## 12. Sequência rápida de diagnóstico

Quando algo não funcionar, siga esta ordem:

1. confirme a pasta atual;
2. confirme o ambiente ativo;
3. confirme qual executável está sendo usado;
4. confira as versões;
5. confira o `PATH`;
6. confirme as dependências;
7. execute o teste mínimo do template;
8. somente depois investigue o algoritmo.

Comandos úteis:

```bash
pwd
git status
which python
which java
which mvn
which cmake
python --version
java -version
mvn -version
cmake --version
```

Python:

```bash
python -c "import sys; print(sys.executable)"
python -m pip --version
python -m pip show pdi-lab
```

C++:

```bash
echo $MSYSTEM
cmake --list-presets
```

---

## 13. Classifique o problema antes de alterar o código

**Ambiente:** comando não encontrado, executável errado no `PATH`, Python incorreto, Maven sem Java, CMake sem compilador, dependência ausente.

**Construção:** erro de compilação, linkedição, `pom.xml` inválido ou configuração CMake.

**Execução:** arquivo inexistente, argumento ausente ou parâmetro inválido.

**Algoritmo:** resultado numérico errado, saturação, canais BGR/RGB, tratamento de borda ou transformação incorreta.

Não altere o algoritmo aleatoriamente quando o erro acontece antes dele.

---

## 14. Máquinas com restrição de instalação

JDK e Maven podem ser extraídos para diretórios do usuário e usados ajustando `JAVA_HOME` e `PATH`.

Dependências Python também podem ser baixadas previamente:

```bash
python -m pip download -r requirements.txt -d packages
```

E instaladas sem acesso à Internet:

```bash
python -m pip install --no-index --find-links packages -r requirements.txt
```

Os pacotes precisam ser compatíveis com sistema operacional, arquitetura e versão/ABI do Python da máquina de destino.

---

## 15. Estado mínimo esperado antes de implementar

### C++

```bash
cmake --preset ucrt64-debug
cmake --build --preset ucrt64-debug
ctest --preset ucrt64-debug
./build/ucrt64-debug/pdi_lab.exe --version
./build/ucrt64-debug/pdi_lab.exe --help
```

### Java

```bash
mvn clean test
mvn package
java -jar target/pdi-lab.jar --version
java -jar target/pdi-lab.jar --help
```

### Python

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest
python -m pdi_lab --version
python -m pdi_lab --help
```

Se esse fluxo mínimo não funcionar, resolva primeiro o ambiente antes de começar a implementar os algoritmos.

---

# Referências oficiais

## MSYS2

- https://www.msys2.org/
- https://www.msys2.org/docs/environments/
- https://www.msys2.org/docs/package-management/
- https://www.msys2.org/docs/package-naming/
- https://www.msys2.org/docs/terminals/

## CMake e CTest

- https://cmake.org/
- https://cmake.org/documentation/
- https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html
- https://cmake.org/cmake/help/latest/manual/ctest.1.html

## GCC e Ninja

- https://gcc.gnu.org/
- https://gcc.gnu.org/onlinedocs/
- https://ninja-build.org/

## OpenCV

- https://opencv.org/
- https://docs.opencv.org/

## Java e Maven

- https://docs.oracle.com/en/java/
- https://docs.oracle.com/en/java/javase/21/install/
- https://maven.apache.org/
- https://maven.apache.org/guides/
- https://maven.apache.org/pom.html

## Python, pip e empacotamento

- https://www.python.org/
- https://docs.python.org/3/
- https://docs.python.org/3/library/venv.html
- https://pip.pypa.io/
- https://packaging.python.org/
- https://pypi.org/project/opencv-python-headless/

## pytest

- https://pytest.org/
- https://docs.pytest.org/

## Git

- https://git-scm.com/
- https://git-scm.com/docs

---

## Pergunta de diagnóstico recomendada

Quando ocorrer um problema, pergunte:

> **o erro aconteceu antes da compilação, durante a compilação, durante a inicialização, na leitura dos dados ou dentro do algoritmo?**

Essa classificação geralmente indica onde procurar a causa.