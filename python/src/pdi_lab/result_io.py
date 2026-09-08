from __future__ import annotations

import csv
import json
import numpy as np
from pathlib import Path
from typing import Mapping, Sequence

from . import exit_code
from .errors import PdiError


def ensure_parent_directory(path: str | Path) -> Path:
    output = Path(path)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise PdiError(
            exit_code.WRITE_ERROR,
            f"Nao foi possivel criar o diretorio de saida: {output.parent}",
        ) from error
    return output


def write_histogram_csv(path: str | Path, histogram: Sequence[int]) -> None:
    """Salva 256 contadores já calculados pelo estudante."""

    if len(histogram) != 256:
        raise ValueError("O histograma deve possuir 256 posicoes.")

    output = ensure_parent_directory(path)
    try:
        with output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["intensity", "count"])
            for intensity, count in enumerate(histogram):
                writer.writerow([intensity, int(count)])
    except OSError as error:
        raise PdiError(
            exit_code.WRITE_ERROR,
            f"Nao foi possivel criar o CSV: {output}",
        ) from error

# Função auxiliar para gravar o resultado do algoritmo laplaciano em csv, similar à função do histograma
def write_matrix_csv(path: str | Path, matrix: np.ndarray) -> None:
    """Salva uma matriz numerica preservando os valores calculados."""


    if matrix is None or matrix.size == 0:
        raise ValueError("A matriz de saida esta vazia.")

    if matrix.ndim != 2:
        raise ValueError("A matriz deve possuir duas dimensoes.")

    output = Path(path)
    output = output.with_name(f"{output.stem}_raw.csv")
    output = ensure_parent_directory(output)

    try:
        with output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            for row in matrix:
                writer.writerow([float(value) for value in row])

    except OSError as error:
        raise PdiError(
            exit_code.WRITE_ERROR,
            f"Nao foi possivel criar o CSV: {output}",
        ) from error


# Função para auxiliar no salvamento de diferentes arquivos gerados pelo Sobel
def derived_output_path(path: str | Path, suffix: str) -> Path:
    """Cria um caminho de saída derivado do arquivo informado."""

    output = Path(path)

    return output.with_name(
        f"{output.stem}_{suffix}{output.suffix}"
    )


def write_json_object(path: str | Path, values: Mapping[str, str]) -> None:
    """Serializa pares texto->texto, como nas variantes C++ e Java."""

    output = ensure_parent_directory(path)
    normalized = {str(key): str(value) for key, value in values.items()}
    try:
        with output.open("w", encoding="utf-8") as file:
            json.dump(normalized, file, ensure_ascii=False, indent=2)
            file.write("\n")
    except OSError as error:
        raise PdiError(
            exit_code.WRITE_ERROR,
            f"Nao foi possivel criar o JSON: {output}",
        ) from error
