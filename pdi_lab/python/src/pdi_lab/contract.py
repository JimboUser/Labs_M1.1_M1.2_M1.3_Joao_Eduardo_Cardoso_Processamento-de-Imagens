from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import exit_code
from .cli import CliOptions
from .operations import is_known_operation
from .parameters import (
    has_parameter,
    parameter_as_border,
    parameter_as_float,
    parameter_as_int,
    parameter_as_path,
)


@dataclass(frozen=True)
class ValidationResult:
    code: int = exit_code.SUCCESS
    message: str = ""

    @property
    def ok(self) -> bool:
        return self.code == exit_code.SUCCESS


def _require(options: CliOptions, name: str) -> ValidationResult:
    if not has_parameter(options, name):
        return ValidationResult(
            exit_code.INVALID_ARGUMENTS,
            f"A operacao '{options.operation}' exige --{name}.",
        )
    return ValidationResult()


def _validate_parameters(options: CliOptions) -> ValidationResult:
    try:
        if options.operation == "quantize":
            required = _require(options, "levels")
            if not required.ok:
                return required
            levels = parameter_as_int(options, "levels")
            if levels not in {2, 4, 8, 16}:
                return ValidationResult(
                    exit_code.INVALID_PARAMETER,
                    "--levels deve ser 2, 4, 8 ou 16.",
                )

        elif options.operation == "brightness":
            required = _require(options, "value")
            if not required.ok:
                return required
            parameter_as_int(options, "value")

        elif options.operation == "contrast":
            required = _require(options, "alpha")
            if not required.ok:
                return required
            if parameter_as_float(options, "alpha") <= 0.0:
                return ValidationResult(
                    exit_code.INVALID_PARAMETER,
                    "--alpha deve ser maior que zero.",
                )

        elif options.operation == "threshold":
            required = _require(options, "threshold")
            if not required.ok:
                return required
            threshold = parameter_as_int(options, "threshold")
            if not 0 <= threshold <= 255:
                return ValidationResult(
                    exit_code.INVALID_PARAMETER,
                    "--threshold deve estar entre 0 e 255.",
                )

        elif options.operation == "segment":
            required = _require(options, "method")
            if not required.ok:
                return required

            method = options.parameters.get("method")

            if method not in {"fixed", "hsv"}:
                return ValidationResult(
                    exit_code.INVALID_PARAMETER,
                    "--method deve ser fixed ou hsv.",
                )

            if method == "fixed":
                required = _require(options, "threshold")
                if not required.ok:
                    return required

                threshold = parameter_as_int(options, "threshold")
                if not 0 <= threshold <= 255:
                    return ValidationResult(
                        exit_code.INVALID_PARAMETER,
                        "--threshold deve estar entre 0 e 255.",
                    )

            elif method == "hsv":
                ranges = {
                    "h": (0, 179),
                    "s": (0, 255),
                    "v": (0, 255),
                }

                for channel, (minimum, maximum) in ranges.items():
                    for suffix in ("min", "max"):
                        name = f"{channel}_{suffix}"

                        required = _require(options, name)
                        if not required.ok:
                            return required

                        value = parameter_as_int(options, name)
                        if not minimum <= value <= maximum:
                            return ValidationResult(
                                exit_code.INVALID_PARAMETER,
                                f"--{name} deve estar entre "
                                f"{minimum} e {maximum}.",
                            )

                    lower_value = parameter_as_int(
                        options, f"{channel}_min"
                    )
                    upper_value = parameter_as_int(
                        options, f"{channel}_max"
                    )

                    if lower_value > upper_value:
                        return ValidationResult(
                            exit_code.INVALID_PARAMETER,
                            f"O limite mínimo de {channel.upper()} "
                            "não pode exceder o máximo.",
                        )

        elif options.operation == "analyze":
            # Conectividade: padrao 8 quando nao informada.
            if has_parameter(options, "connectivity"):
                connectivity = parameter_as_int(
                    options, "connectivity"
                )
            else:
                connectivity = 8

            if connectivity not in {4, 8}:
                return ValidationResult(
                    exit_code.INVALID_PARAMETER,
                    "--connectivity deve ser 4 ou 8.",
                )

            # Area minima: opcional, com padrao 0.
            if has_parameter(options, "min_area"):
                min_area = parameter_as_int(
                    options, "min_area"
                )
            else:
                min_area = 0

            if min_area < 0:
                return ValidationResult(
                    exit_code.INVALID_PARAMETER,
                    "--min-area deve ser um inteiro nao negativo.",
                )

        elif options.operation == "convolution":
            required = _require(options, "kernel")
            if not required.ok:
                return required
            required = _require(options, "border")
            if not required.ok:
                return required

            kernel_path = parameter_as_path(options, "kernel")
            if not Path(kernel_path).is_file():
                return ValidationResult(
                    exit_code.READ_ERROR,
                    f"Nao foi possivel abrir o kernel: {kernel_path}",
                )
            parameter_as_border(options)

        elif options.operation == "mean_filter":
            required = _require(options, "size")
            if not required.ok:
                return required
            required = _require(options, "border")
            if not required.ok:
                return required
            size = parameter_as_int(options, "size")
            if size not in {3, 5}:
                return ValidationResult(
                    exit_code.INVALID_PARAMETER,
                    "--size deve ser 3 ou 5 para mean_filter.",
                )
            parameter_as_border(options)

        elif options.operation in {"weighted_mean", "laplacian", "sobel"}:
            required = _require(options, "border")
            if not required.ok:
                return required
            parameter_as_border(options)

    except ValueError as error:
        return ValidationResult(exit_code.INVALID_PARAMETER, str(error))

    return ValidationResult()


def validate_contract(options: CliOptions) -> ValidationResult:
    if not options.operation:
        return ValidationResult(exit_code.INVALID_ARGUMENTS, "Informe --operation.")
    if not is_known_operation(options.operation):
        return ValidationResult(
            exit_code.UNKNOWN_OPERATION,
            f"Operacao desconhecida: {options.operation}",
        )
    if not options.input:
        return ValidationResult(exit_code.INVALID_ARGUMENTS, "Informe --input.")
    if not Path(options.input).is_file():
        return ValidationResult(
            exit_code.READ_ERROR,
            f"Nao foi possivel abrir a imagem: {options.input}",
        )
    if options.operation != "inspect" and not options.output:
        return ValidationResult(exit_code.INVALID_ARGUMENTS, "Informe --output.")

    return _validate_parameters(options)
