# Validação inicial do projeto-base

Antes de implementar qualquer algoritmo do laboratório, valide a variante escolhida **sem modificar o código-fonte**. O objetivo é separar problemas de ambiente, dependências e construção de problemas que possam surgir posteriormente na implementação dos algoritmos.

## C++ — Windows com MSYS2 UCRT64

Na pasta `cpp/`:

```bash
cmake --preset ucrt64-debug
cmake --build --preset ucrt64-debug
ctest --preset ucrt64-debug
./build/ucrt64-debug/pdi_lab.exe --help
./build/ucrt64-debug/pdi_lab.exe --version
```

Se configuração, compilação e testes terminarem sem erro, a infraestrutura C++ está pronta para uso.

## Java

Na pasta `java/`:

```bash
mvn clean test
mvn package
java -jar target/pdi-lab.jar --help
java -jar target/pdi-lab.jar --version
```

Confirme antes que `java`, `javac` e `mvn` estão disponíveis no `PATH`.

## Python

Na pasta `python/`, crie um ambiente virtual. No Windows, prefira o CPython para Windows em vez do Python fornecido pelo MSYS2/UCRT64.

Exemplo com o launcher do Python para Windows:

```bash
py -3.13 -m venv .venv
source .venv/Scripts/activate
```

Em sistemas Unix-like:

```bash
python -m venv .venv
source .venv/bin/activate
```

Depois:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest
python -m pdi_lab --help
python -m pdi_lab --version
```

## O que conferir

Ao final, a variante escolhida deve:

- construir ou instalar sem erro;
- passar nos testes públicos da infraestrutura;
- responder a `--help`;
- responder a `--version`;
- reconhecer as operações previstas;
- rejeitar parâmetros inválidos com mensagens e códigos de saída coerentes;
- manter as operações avaliadas ainda sem implementação pronta.

Se a base original falhar antes de qualquer alteração sua, investigue primeiro o ambiente e as dependências. Não tente corrigir um problema de instalação alterando o algoritmo.