from __future__ import annotations

import argparse
from dataclasses import dataclass, field


@dataclass
class CliOptions:
    """Representação comum dos argumentos recebidos pela aplicação."""

    operation: str | None = None
    input: str | None = None
    output: str | None = None
    version: bool = False
    parameters: dict[str, str] = field(default_factory=dict)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description="Projeto-base dos laboratorios M1 de Processamento de Imagens",
    )
    parser.add_argument("--version", action="store_true")
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Inverte a máscara de segmentação.",
    )

    # As três linguagens expõem os mesmos nomes de parâmetros.
    for name in [
        "operation",
        "input",
        "output",
        "value",
        "levels",
        "threshold",
        "alpha",
        "kernel",
        "border",
        "size",
        "method",
        "h_min",
        "s_min",
        "v_min",
        "h_max",
        "s_max",
        "v_max",
    ]:
        parser.add_argument(f"--{name}")

    return parser


def parse_cli(argv=None) -> CliOptions:
    values = vars(build_parser().parse_args(argv))
    version = bool(values.pop("version"))
    operation = values.pop("operation")
    input_path = values.pop("input")
    output_path = values.pop("output")
    invert = bool(values.pop("invert"))

    parameters = {
        name: value
        for name, value in values.items()
        if value is not None
    }

    if invert:
        parameters["invert"] = True

    return CliOptions(
        operation=operation,
        input=input_path,
        output=output_path,
        version=version,
        parameters=parameters,
    )



def version_requested(options: CliOptions) -> bool:
    return options.version
