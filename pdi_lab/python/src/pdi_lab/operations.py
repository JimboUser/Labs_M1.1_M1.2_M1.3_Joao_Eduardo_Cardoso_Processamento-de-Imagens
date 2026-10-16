from __future__ import annotations

import sys
import cv2
import numpy as np

from . import exit_code
from .cli import CliOptions
from .image_io import read_image, write_image
from .kernel import Kernel, read_kernel
from .parameters import (
    BorderStrategy,
    parameter_as_border,
    parameter_as_float,
    parameter_as_int,
    parameter_as_path
)
from .result_io import (
    derived_output_path,
    write_histogram_csv,
    write_matrix_csv
)


# A lista é equivalente às variantes C++ e Java. Atividades complementares
# dos roteiros não são transformadas em requisitos do contrato mínimo.
KNOWN_OPERATIONS = {
    # M1.1 — representação, canais e níveis de cinza
    "inspect",
    "copy",
    "channel_b",
    "channel_g",
    "channel_r",
    "grayscale_average",
    "grayscale_weighted",
    "quantize",

    # M1.2 — transformações de intensidade
    "brightness",
    "contrast",
    "negative",
    "threshold",
    "histogram",

    # M1.3 — convolução e filtragem espacial
    "convolution",
    "mean_filter",
    "weighted_mean",
    "laplacian",
    "sobel",

    # M2.1 —
    "segment",
}


def is_known_operation(operation: str) -> bool:
    """Retorna True somente para as operações previstas no contrato comum."""

    return operation in KNOWN_OPERATIONS


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def _validate_color_image(image: np.ndarray) -> None:
    """Valida se a imagem possui três canais."""

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(
            "A operacao exige uma imagem colorida com 3 canais."
        )


def _validate_grayscale_image(image: np.ndarray) -> None:
    """Valida se a imagem possui apenas um canal."""

    if image.ndim != 2:
        raise ValueError(
            "A operacao exige uma imagem em niveis de cinza."
        )


def _clamp(value: float) -> int:
    if value < 0:
        return 0

    if value > 255:
        return 255

    return int(value + 0.5)


def _neighborhood_fits(
    y: int,
    x: int,
    height: int,
    width: int,
    radius: int,
) -> bool:
    """Verifica se a vizinhanca completa cabe dentro da imagem."""

    return (
        y - radius >= 0
        and y + radius < height
        and x - radius >= 0
        and x + radius < width
    )


def copy_border(
    y: int,
    x: int,
    height: int,
    width: int,
    radius: int,
) -> bool:
    return _neighborhood_fits(y, x, height, width, radius)


def replicate_border(
    y: int,
    x: int,
    height: int,
    width: int,
) -> tuple[int, int]:
    if y < 0:
        y = 0
    elif y >= height:
        y = height - 1

    if x < 0:
        x = 0
    elif x >= width:
        x = width - 1

    return y, x


def to_uint8(image: np.ndarray) -> np.ndarray:
    """Converte uma imagem numerica para uint8 com saturacao."""

    altura, largura = image.shape

    resultado = np.zeros((altura, largura), dtype=np.uint8)

    for y in range(altura):
        for x in range(largura):
            valor = float(image[y, x])

            if valor < 0:
                valor = 0
            elif valor > 255:
                valor = 255

            resultado[y, x] = int(valor + 0.5)

    return resultado

def sobel_gx(
    image: np.ndarray,
    border: BorderStrategy,
    ) -> np.ndarray:
    """Calcula a resposta do Sobel na direcao horizontal."""

    _validate_grayscale_image(image)

    values = (
        -1.0, 0.0, 1.0,
        -2.0, 0.0, 2.0,
        -1.0, 0.0, 1.0,
    )

    kernel = Kernel(
        size=3,
        values=values,
    )

    return convolution(image, kernel, border)


def sobel_gy(
    image: np.ndarray,
    border: BorderStrategy,
    ) -> np.ndarray:
    """Calcula a resposta do Sobel na direcao vertical."""

    _validate_grayscale_image(image)

    values = (
        -1.0, -2.0, -1.0,
        0.0, 0.0, 0.0,
        1.0, 2.0, 1.0,
    )

    kernel = Kernel(
        size=3,
        values=values,
    )

    return convolution(image, kernel, border)


# ---------------------------------------------------------------------------
# Funções principais
# ---------------------------------------------------------------------------

def inspect(image: np.ndarray) -> None:
    if image is None or image.size == 0:
        raise ValueError("A imagem esta vazia.")
    """Exibe informações básicas da imagem."""

    altura, largura = image.shape[:2]
    quantidade_pixels = largura * altura

    if image.ndim == 2:
        minimo = int(image[0, 0])
        maximo = int(image[0, 0])
        soma = 0

        for y in range(altura):
            for x in range(largura):
                valor = int(image[y, x])

                if valor < minimo:
                    minimo = valor

                if valor > maximo:
                    maximo = valor

                soma += valor

        media = soma / quantidade_pixels

        print(f"Largura: {largura}")
        print(f"Altura: {altura}")
        print("Canais: 1")
        print(f"Tipo: {image.dtype}")
        print(f"Pixels: {quantidade_pixels}")
        print(f"Minimo: {minimo}")
        print(f"Maximo: {maximo}")
        print(f"Media: {media:.2f}")

    elif image.ndim == 3 and image.shape[2] == 3:
        print(f"Largura: {largura}")
        print(f"Altura: {altura}")
        print("Canais: 3")
        print(f"Tipo: {image.dtype}")
        print(f"Pixels: {quantidade_pixels}")

        for canal, nome in enumerate(("B", "G", "R")):
            minimo = int(image[0, 0, canal])
            maximo = int(image[0, 0, canal])
            soma = 0

            for y in range(altura):
                for x in range(largura):
                    valor = int(image[y, x, canal])

                    if valor < minimo:
                        minimo = valor

                    if valor > maximo:
                        maximo = valor

                    soma += valor

            media = soma / quantidade_pixels

            print(f"Canal {nome}:")
            print(f"  Minimo: {minimo}")
            print(f"  Maximo: {maximo}")
            print(f"  Media: {media:.2f}")

    else:
        raise ValueError(
            "Numero de canais ou dimensoes nao suportado."
        )


def copy(image: np.ndarray) -> np.ndarray:
    """Cria uma cópia da imagem percorrendo todos os pixels manualmente."""

    copia = np.zeros_like(image)

    if image.ndim == 2:
        altura, largura = image.shape

        for y in range(altura):
            for x in range(largura):
                copia[y, x] = image[y, x]

    elif image.ndim == 3:
        altura, largura, canais = image.shape

        for y in range(altura):
            for x in range(largura):
                for canal in range(canais):
                    copia[y, x, canal] = image[y, x, canal]

    else:
        raise ValueError(
            "Numero de canais ou dimensoes nao suportado."
        )

    return copia


def extract_channel(
    image: np.ndarray,
    channel: int,
) -> np.ndarray:
    """Gera uma imagem contendo somente o canal solicitado."""

    _validate_color_image(image)

    altura, largura, canais = image.shape
    resultado = np.zeros_like(image)

    for y in range(altura):
        for x in range(largura):
            resultado[y, x, channel] = image[y, x, channel]

    return resultado


def grayscale_average(image: np.ndarray) -> np.ndarray:
    """Converte uma imagem colorida para tons de cinza usando média simples."""

    _validate_color_image(image)

    altura, largura, _ = image.shape
    resultado = np.zeros((altura, largura), dtype=image.dtype)

    for y in range(altura):
        for x in range(largura):
            B = int(image[y, x, 0])
            G = int(image[y, x, 1])
            R = int(image[y, x, 2])

            valor = (R + G + B) / 3
            resultado[y, x] = int(valor + 0.5)

    return resultado


def grayscale_weighted(image: np.ndarray) -> np.ndarray:
    """Converte uma imagem colorida para tons de cinza usando média ponderada."""

    _validate_color_image(image)

    altura, largura, _ = image.shape
    resultado = np.zeros((altura, largura), dtype=image.dtype)

    for y in range(altura):
        for x in range(largura):
            B = int(image[y, x, 0])
            G = int(image[y, x, 1])
            R = int(image[y, x, 2])

            valor = 0.299 * R + 0.587 * G + 0.114 * B
            resultado[y, x] = int(valor + 0.5)

    return resultado


def quantize(
    image: np.ndarray,
    levels: int,
) -> np.ndarray:
    """Reduz a quantidade de níveis de uma imagem em tons de cinza."""

    _validate_grayscale_image(image)

    altura, largura = image.shape
    resultado = np.zeros_like(image)

    for y in range(altura):
        for x in range(largura):
            valor = int(image[y, x])

            faixa = (valor * levels) // 256

            if faixa >= levels:
                faixa = levels - 1

            quantizado = faixa * 255 / (levels - 1)

            resultado[y, x] = int(quantizado + 0.5)

    return resultado


def brightness(
    image: np.ndarray,
    value: int,
) -> np.ndarray:
    """Altera o brilho de uma imagem em tons de cinza."""

    _validate_grayscale_image(image)

    altura, largura = image.shape
    resultado = np.zeros_like(image)

    for y in range(altura):
        for x in range(largura):
            pixel = int(image[y, x])
            novo_valor = pixel + value
            resultado[y, x] = _clamp(novo_valor)

    return resultado


def contrast(
    image: np.ndarray,
    alpha: float,
) -> np.ndarray:
    """Altera o contraste de uma imagem em tons de cinza."""

    _validate_grayscale_image(image)

    altura, largura = image.shape
    resultado = np.zeros_like(image)

    for y in range(altura):
        for x in range(largura):
            pixel = int(image[y, x])
            novo_valor = alpha * (pixel - 128) + 128
            resultado[y, x] = _clamp(novo_valor)

    return resultado


def negative(image: np.ndarray) -> np.ndarray:
    """Gera o negativo de uma imagem em tons de cinza."""

    _validate_grayscale_image(image)

    altura, largura = image.shape
    resultado = np.zeros_like(image)

    for y in range(altura):
        for x in range(largura):
            pixel = int(image[y, x])
            resultado[y, x] = 255 - pixel

    return resultado


def threshold(
    image: np.ndarray,
    threshold: int,
) -> np.ndarray:
    """Converte uma imagem em tons de cinza para uma imagem binaria."""

    _validate_grayscale_image(image)

    altura, largura = image.shape
    resultado = np.zeros_like(image)

    for y in range(altura):
        for x in range(largura):
            pixel = int(image[y, x])

            if pixel < threshold:
                resultado[y, x] = 0
            else:
                resultado[y, x] = 255

    return resultado


def histogram(image: np.ndarray) -> list[int]:
    """Calcula manualmente o histograma de uma imagem em tons de cinza."""

    _validate_grayscale_image(image)

    histograma = [0] * 256

    altura, largura = image.shape

    for y in range(altura):
        for x in range(largura):
            pixel = int(image[y, x])
            histograma[pixel] += 1

    return histograma


def convolution(
    image: np.ndarray,
    kernel: Kernel,
    border: BorderStrategy,
) -> np.ndarray:
    """Aplica manualmente uma convolucao em uma imagem em tons de cinza."""

    _validate_grayscale_image(image)

    height, width = image.shape
    radius = kernel.radius

    resultado = np.zeros((height, width), dtype=np.float64)

    for y in range(height):
        for x in range(width):

            if border == BorderStrategy.COPY:
                if not copy_border(y, x, height, width, radius):
                    resultado[y, x] = float(image[y, x])
                    continue

            acumulador = 0.0

            for ky in range(kernel.size):
                for kx in range(kernel.size):

                    image_y = y + ky - radius
                    image_x = x + kx - radius

                    if border == BorderStrategy.REPLICATE:
                        image_y, image_x = replicate_border(
                            image_y,
                            image_x,
                            height,
                            width,
                        )

                    pixel = float(image[image_y, image_x])
                    coeficiente = kernel.at(ky, kx)

                    acumulador += pixel * coeficiente

            resultado[y, x] = acumulador

    return resultado


def mean_filter(
    image: np.ndarray,
    size: int,
    border: BorderStrategy,
) -> np.ndarray:
    """Aplica um filtro de media na imagem."""

    _validate_grayscale_image(image)

    if size not in (3, 5):
        raise ValueError("O filtro de media deve possuir tamanho 3 ou 5.")

    value = 1.0 / (size * size)

    values = tuple(
        value for _ in range(size * size)
    )

    kernel = Kernel(
        size=size,
        values=values,
    )

    return convolution(image, kernel, border)


def weighted_mean(
    image: np.ndarray,
    border: BorderStrategy,
) -> np.ndarray:
    """Aplica uma media ponderada 3x3."""

    _validate_grayscale_image(image)

    values = (
        1.0 / 16.0, 2.0 / 16.0, 1.0 / 16.0,
        2.0 / 16.0, 4.0 / 16.0, 2.0 / 16.0,
        1.0 / 16.0, 2.0 / 16.0, 1.0 / 16.0,
    )

    kernel = Kernel(
        size=3,
        values=values,
    )

    return convolution(image, kernel, border)


def laplacian(
    image: np.ndarray,
    border: BorderStrategy,
) -> np.ndarray:
    """Aplica o operador Laplaciano."""

    _validate_grayscale_image(image)

    values = (
        1.0, 1.0, 1.0,
        1.0, -8.0, 1.0,
        1.0, 1.0, 1.0,
    )

    kernel = Kernel(
        size=3,
        values=values,
    )

    return convolution(image, kernel, border)



def sharpen_with_laplacian(
    image: np.ndarray,
    border: BorderStrategy,
) -> np.ndarray:
    """Realca a imagem utilizando a resposta do Laplaciano."""

    _validate_grayscale_image(image)

    resposta = laplacian(image, border)

    resultado = image.astype(np.float64) - resposta

    return resultado

def sobel(
    image: np.ndarray,
    border: BorderStrategy,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Calcula as respostas Gx, Gy e as magnitudes do Sobel."""

    _validate_grayscale_image(image)

    gx = sobel_gx(image, border)
    gy = sobel_gy(image, border)

    magnitude_aproximada = np.abs(gx) + np.abs(gy)
    magnitude_euclidiana = np.sqrt(gx * gx + gy * gy)

    return (
        gx,
        gy,
        magnitude_aproximada,
        magnitude_euclidiana,
    )


# ---------------------------------------------------------------------------
# Operações M2-1
# ---------------------------------------------------------------------------


def segment_fixed(image, threshold, invert=False):
    gray = image

    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if invert:
        mask = np.where(gray < threshold, 255, 0).astype(np.uint8)
    else:
        mask = np.where(gray >= threshold, 255, 0).astype(np.uint8)

    return mask



def segment_hsv(image, lower, upper):
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(
            "A segmentação HSV exige uma imagem colorida BGR."
        )

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array(lower, dtype=np.uint8)
    upper = np.array(upper, dtype=np.uint8)

    return cv2.inRange(hsv, lower, upper)


# ---------------------------------------------------------------------------
# Despacho das operações
# ---------------------------------------------------------------------------

def run_operation(options: CliOptions) -> int:
    """Executa a operação solicitada."""

    image = read_image(options.input)

    if options.operation == "inspect":
        inspect(image)
        return exit_code.SUCCESS

    if options.operation == "copy":
        copia = copy(image)
        write_image(options.output, copia)
        return exit_code.SUCCESS

    if options.operation == "channel_b":
        resultado = extract_channel(image, 0)
        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "channel_g":
        resultado = extract_channel(image, 1)
        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "channel_r":
        resultado = extract_channel(image, 2)
        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "grayscale_average":
        resultado = grayscale_average(image)
        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "grayscale_weighted":
        resultado = grayscale_weighted(image)
        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "quantize":
        levels = parameter_as_int(options, "levels")
        resultado = quantize(image, levels)
        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "brightness":
        value = parameter_as_int(options, "value")
        resultado = brightness(image, value)
        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "contrast":
        alpha = parameter_as_float(options, "alpha")
        resultado = contrast(image, alpha)
        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "negative":
        resultado = negative(image)
        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "threshold":
        threshold = parameter_as_int(options, "threshold")
        resultado = threshold(image, threshold)
        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "histogram":
        histograma = histogram(image)
        write_histogram_csv(options.output, histograma)
        return exit_code.SUCCESS

    if options.operation == "convolution":
        kernel_path = parameter_as_path(options, "kernel")
        border = parameter_as_border(options)

        kernel = read_kernel(kernel_path)
        resultado = convolution(image, kernel, border)

        write_image(options.output, resultado)
        return exit_code.SUCCESS

    if options.operation == "mean_filter":
        size = parameter_as_int(options, "size")
        border = parameter_as_border(options)

        resultado = mean_filter(image, size, border)
        resultado_visual = to_uint8(resultado)

        write_image(options.output, resultado_visual)
        return exit_code.SUCCESS

    if options.operation == "weighted_mean":
        border = parameter_as_border(options)

        resultado = weighted_mean(image, border)
        resultado_visual = to_uint8(resultado)

        write_image(options.output, resultado_visual)
        return exit_code.SUCCESS

    if options.operation == "laplacian":
        border = parameter_as_border(options)

        resultado = laplacian(image, border)

        write_matrix_csv(options.output, resultado)

        resultado_visual = to_uint8(resultado)

        write_image(options.output, resultado_visual)
        return exit_code.SUCCESS

    if options.operation == "sharpen_laplacian":
        border = parameter_as_border(options)

        resultado = sharpen_with_laplacian(image, border)
        resultado_visual = to_uint8(resultado)

        write_image(options.output, resultado_visual)
        return exit_code.SUCCESS

    if options.operation == "sobel":
        border = parameter_as_border(options)

        gx, gy, magnitude_aproximada, magnitude_euclidiana = sobel(
            image,
            border,
        )

        gx_visual = to_uint8(np.abs(gx))
        gy_visual = to_uint8(np.abs(gy))
        aproximada_visual = to_uint8(magnitude_aproximada)
        euclidiana_visual = to_uint8(magnitude_euclidiana)

        gx_path = derived_output_path(options.output, "gx")
        gy_path = derived_output_path(options.output, "gy")
        aproximada_path = derived_output_path(options.output, "approx")
        euclidiana_path = derived_output_path(options.output, "euclidean")

        write_image(gx_path, gx_visual)
        write_image(gy_path, gy_visual)
        write_image(aproximada_path, aproximada_visual)
        write_image(euclidiana_path, euclidiana_visual)

        return exit_code.SUCCESS

    if options.operation == "segment":
        method = options.parameters.get("method")

        if method == "fixed":
            threshold_value = parameter_as_int(options, "threshold")
            invert = options.parameters.get("invert", False)

            resultado = segment_fixed(
                image,
                threshold_value,
                invert=invert,
            )

        elif method == "hsv":
            lower = [
                parameter_as_int(options, "h_min"),
                parameter_as_int(options, "s_min"),
                parameter_as_int(options, "v_min"),
            ]

            upper = [
                parameter_as_int(options, "h_max"),
                parameter_as_int(options, "s_max"),
                parameter_as_int(options, "v_max"),
            ]

            resultado = segment_hsv(image, lower, upper)

        else:
            raise ValueError(
                "Método de segmentação inválido. Use fixed ou hsv."
            )

        if resultado.ndim != 2 or not np.isin(
                resultado, [0, 255]
        ).all():
            raise ValueError(
                "A segmentação não produziu uma máscara binária válida."
            )

        write_image(options.output, resultado)

        pixels_fundo = int(np.count_nonzero(resultado == 0))
        pixels_objeto = int(np.count_nonzero(resultado == 255))
        total_pixels = int(resultado.size)

        print(f"Método: {method}")
        print(f"Pixels classificados como 0: {pixels_fundo}")
        print(f"Pixels classificados como 255: {pixels_objeto}")
        print(
            f"Proporção de pixels 255: "
            f"{100 * pixels_objeto / total_pixels:.2f}%"
        )

        return exit_code.SUCCESS

    print(
        f"Operacao '{options.operation}' reconhecida, "
        "mas ainda nao implementada no projeto-base.",
        file=sys.stderr,
    )

    return exit_code.GENERAL_ERROR