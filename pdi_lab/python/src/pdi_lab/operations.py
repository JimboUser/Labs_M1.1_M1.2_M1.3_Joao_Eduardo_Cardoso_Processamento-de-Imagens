from __future__ import annotations

import sys
import cv2
import numpy as np
from pathlib import Path
import json

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
    write_matrix_csv,
    write_components_csv,
    write_json_object,
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
    # M2.2 —
    "analyze",
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


def analyze_components(
    mask: np.ndarray,
    connectivity: int = 8,
) -> tuple[np.ndarray, list[dict[str, int | float]]]:
    """Identifica e mede os componentes conexos de uma mascara binaria."""

    if mask.ndim != 2:
        raise ValueError(
            "A analise exige uma mascara em escala de cinza."
        )

    if not np.isin(mask, [0, 255]).all():
        raise ValueError(
            "A mascara deve conter somente pixels 0 e 255."
        )

    if connectivity not in {4, 8}:
        raise ValueError(
            "A conectividade deve ser 4 ou 8."
        )

    # OpenCV trabalha com uma imagem binaria de 8 bits.
    binary = (mask == 255).astype(np.uint8)

    num_labels, labels, stats, centroids = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=connectivity,
        )
    )

    components = []

    # O rotulo 0 representa o fundo e nao deve ser contabilizado.
    for label in range(1, num_labels):
        x = int(stats[label, cv2.CC_STAT_LEFT])
        y = int(stats[label, cv2.CC_STAT_TOP])
        width = int(stats[label, cv2.CC_STAT_WIDTH])
        height = int(stats[label, cv2.CC_STAT_HEIGHT])
        area = int(stats[label, cv2.CC_STAT_AREA])

        cx = float(centroids[label, 0])
        cy = float(centroids[label, 1])

        components.append({
            "label": label,
            "area": area,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "cx": cx,
            "cy": cy,
        })

    return labels, components



def load_morphology_config(path: str | Path) -> dict:
    """Carrega e valida a configuração das operações morfológicas."""
    try:
        with Path(path).open("r", encoding="utf-8") as file:
            config = json.load(file)
    except FileNotFoundError as error:
        raise ValueError(
            f"Arquivo de configuração não encontrado: {path}"
        ) from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"JSON inválido: {error.msg}"
        ) from error
    except OSError as error:
        raise ValueError(
            f"Não foi possível ler a configuração: {error}"
        ) from error

    if not isinstance(config, dict):
        raise ValueError("A configuração deve ser um objeto JSON.")

    shape = config.get("kernel_shape")
    if shape not in {"rect", "ellipse", "cross"}:
        raise ValueError(
            "kernel_shape deve ser 'rect', 'ellipse' ou 'cross'."
        )

    size = config.get("kernel_size")
    if (
        isinstance(size, bool)
        or not isinstance(size, int)
        or size <= 0
        or size % 2 == 0
    ):
        raise ValueError(
            "kernel_size deve ser um inteiro positivo e ímpar."
        )

    iterations = config.get("iterations")
    if (
        isinstance(iterations, bool)
        or not isinstance(iterations, int)
        or iterations <= 0
    ):
        raise ValueError("iterations deve ser um inteiro positivo.")

    sequence = config.get("sequence")
    if not isinstance(sequence, list) or len(sequence) < 2:
        raise ValueError(
            "sequence deve conter pelo menos duas operações."
        )

    allowed_operations = {"open", "close", "erode", "dilate"}
    has_open_or_close = False

    for index, step in enumerate(sequence, start=1):
        if not isinstance(step, dict):
            raise ValueError(
                f"A etapa {index} deve ser um objeto JSON."
            )

        operation = step.get("operation")
        if operation not in allowed_operations:
            raise ValueError(
                f"Operação inválida na etapa {index}: {operation!r}."
            )

        if operation in {"open", "close"}:
            has_open_or_close = True

        purpose = step.get("purpose")
        if not isinstance(purpose, str) or not purpose.strip():
            raise ValueError(
                f"A etapa {index} precisa informar sua finalidade em 'purpose'."
            )

    if not has_open_or_close:
        raise ValueError(
            "A sequência deve incluir pelo menos uma operação "
            "'open' ou 'close'."
        )

    return config



def apply_morphology_sequence(
    mask: np.ndarray,
    config: dict,
    output_prefix: str,
) -> tuple[np.ndarray, list[dict[str, int | str]]]:
    """Aplica a sequência morfológica e salva cada etapa."""
    shape_map = {
        "rect": cv2.MORPH_RECT,
        "ellipse": cv2.MORPH_ELLIPSE,
        "cross": cv2.MORPH_CROSS,
    }

    kernel = cv2.getStructuringElement(
        shape_map[config["kernel_shape"]],
        (config["kernel_size"], config["kernel_size"]),
    )

    iterations = config["iterations"]
    current_mask = mask.copy()
    stage_statistics = []

    # Preserva a máscara inicial, sem modificá-la.
    write_image(f"{output_prefix}_initial.png", current_mask)

    for index, step in enumerate(config["sequence"], start=1):
        operation = step["operation"]

        if operation == "open":
            current_mask = cv2.morphologyEx(
                current_mask,
                cv2.MORPH_OPEN,
                kernel,
                iterations=iterations,
            )
        elif operation == "close":
            current_mask = cv2.morphologyEx(
                current_mask,
                cv2.MORPH_CLOSE,
                kernel,
                iterations=iterations,
            )
        elif operation == "erode":
            current_mask = cv2.erode(
                current_mask,
                kernel,
                iterations=iterations,
            )
        elif operation == "dilate":
            current_mask = cv2.dilate(
                current_mask,
                kernel,
                iterations=iterations,
            )

        stage_path = (
            f"{output_prefix}_stage_{index:02d}_{operation}.png"
        )
        write_image(stage_path, current_mask)

        _, stage_components = analyze_components(
            current_mask,
            connectivity=8,
        )

        stage_statistics.append({
            "stage": index,
            "operation": operation,
            "components": len(stage_components),
            "foreground_area": int(
                np.count_nonzero(current_mask == 255)
            ),
        })

        print(f"Etapa {index}: {operation} — {stage_path}")

    write_image(f"{output_prefix}_final.png", current_mask)

    return current_mask, stage_statistics


def create_component_visualization(
    mask: np.ndarray,
    labels: np.ndarray,
    components: list[dict[str, int | float]],
    output_path: str,
) -> None:
    """Gera uma imagem colorida com rótulos e caixas delimitadoras."""
    if mask.ndim != 2 or labels.ndim != 2:
        raise ValueError(
            "A visualizacao exige mascara e rotulos em escala de cinza."
        )

    if mask.shape != labels.shape:
        raise ValueError(
            "A mascara e a matriz de rotulos devem ter o mesmo tamanho."
        )

    # Converte os rótulos em uma imagem colorida.
    labels_uint8 = (labels.astype(np.int64) % 256).astype(np.uint8)
    visualization = cv2.applyColorMap(
        labels_uint8,
        cv2.COLORMAP_JET,
    )

    # Mantém o fundo preto.
    visualization[mask == 0] = (0, 0, 0)

    for component in components:
        label = int(component["label"])
        x = int(component["x"])
        y = int(component["y"])
        width = int(component["width"])
        height = int(component["height"])

        # Desenha a caixa delimitadora.
        cv2.rectangle(
            visualization,
            (x, y),
            (x + width - 1, y + height - 1),
            (255, 255, 255),
            2,
        )

        # Identifica o componente próximo ao canto superior esquerdo.
        cv2.putText(
            visualization,
            str(label),
            (x, max(y - 5, 15)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    write_image(output_path, visualization)


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

    if options.operation == "analyze":
        config_path = (
                options.parameters.get("config")
                or "configs/morphology.json"
        )

        try:
            morphology_config = load_morphology_config(config_path)
        except ValueError as error:
            print(
                f"Erro na configuração morfológica: {error}",
                file=sys.stderr,
            )
            return exit_code.INVALID_PARAMETER

        connectivity = (
            parameter_as_int(options, "connectivity")
            if options.parameters.get("connectivity") is not None
            else 8
        )

        min_area = (
            parameter_as_int(options, "min_area")
            if options.parameters.get("min_area") is not None
            else 0
        )

        output_prefix = options.output

        # Preserva e valida a mascara original.
        initial_mask = image.copy()

        try:
            _, components_4 = analyze_components(
                initial_mask, connectivity=4
            )
            _, components_8 = analyze_components(
                initial_mask, connectivity=8
            )
            initial_labels, components = analyze_components(
                initial_mask, connectivity=connectivity
            )
        except ValueError as error:
            print(
                f"Erro na mascara inicial: {error}",
                file=sys.stderr,
            )
            return exit_code.INVALID_PARAMETER

        create_component_visualization(
            initial_mask,
            initial_labels,
            components,
            f"{output_prefix}_initial_labels.png",
        )

        # Registra quais componentes atendem ao filtro de area.
        for component in components:
            component["kept"] = component["area"] >= min_area

        filtered_components = [
            component
            for component in components
            if component["kept"]
        ]

        total_foreground = int(
            np.count_nonzero(initial_mask == 255)
        )

        initial_component_area = sum(
            component["area"] for component in components
        )

        if initial_component_area != total_foreground:
            print(
                "Erro: a soma das áreas dos componentes iniciais "
                "não corresponde à área total do primeiro plano.",
                file=sys.stderr,
            )
            return exit_code.INVALID_PARAMETER

        # Aplica a sequencia morfologica e salva cada etapa.
        try:
            final_mask, stage_statistics = apply_morphology_sequence(
                initial_mask,
                morphology_config,
                output_prefix,
            )
        except (ValueError, OSError) as error:
            print(
                f"Erro ao aplicar morfologia: {error}",
                file=sys.stderr,
            )
            return exit_code.INVALID_PARAMETER

        # Analisa os componentes da mascara final.
        try:
            final_labels, final_components = analyze_components(
                final_mask,
                connectivity=connectivity,
            )

            create_component_visualization(
                final_mask,
                final_labels,
                final_components,
                f"{output_prefix}_labels.png",
            )
        except ValueError as error:
            print(
                f"Erro na mascara final: {error}",
                file=sys.stderr,
            )
            return exit_code.INVALID_PARAMETER

        for component in final_components:
            component["kept"] = component["area"] >= min_area

        final_filtered_components = [
            component
            for component in final_components
            if component["kept"]
        ]

        final_foreground = int(
            np.count_nonzero(final_mask == 255)
        )

        final_component_area = sum(
            component["area"] for component in final_components
        )

        if final_component_area != final_foreground:
            print(
                "Erro: a soma das áreas dos componentes finais "
                "não corresponde à área total do primeiro plano.",
                file=sys.stderr,
            )
            return exit_code.INVALID_PARAMETER

        # Salva os dados dos componentes iniciais e finais.
        write_components_csv(
            f"{output_prefix}_initial.csv",
            components,
        )
        write_components_csv(
            f"{output_prefix}_final.csv",
            final_components,
        )

        # Salva o resumo para comparacao antes/depois.
        write_json_object(
            f"{output_prefix}_summary.json",
            {
                "connectivity": connectivity,
                "min_area": min_area,
                "morphology": morphology_config,
                "stage_statistics": stage_statistics,
                "initial_components_connectivity_4": len(components_4),
                "initial_components_connectivity_8": len(components_8),
                "initial_components_raw": len(components),
                "initial_components_filtered": len(filtered_components),
                "initial_foreground_area": total_foreground,
                "initial_filtered_area": sum(
                    component["area"]
                    for component in filtered_components
                ),
                "final_components_raw": len(final_components),
                "final_components_filtered": len(final_filtered_components),
                "final_foreground_area": final_foreground,
                "final_filtered_area": sum(
                    component["area"]
                    for component in final_filtered_components
                ),
            },
        )

        print(f"Conectividade selecionada: {connectivity}")
        print(f"Componentes iniciais: {len(components)}")
        print(f"Componentes iniciais mantidos: {len(filtered_components)}")
        print(f"Componentes finais: {len(final_components)}")
        print(
            f"Componentes finais mantidos: "
            f"{len(final_filtered_components)}"
        )
        print(f"Area inicial: {total_foreground}")
        print(f"Area final: {final_foreground}")
        print(f"CSV inicial: {output_prefix}_initial.csv")
        print(f"CSV final: {output_prefix}_final.csv")
        print(f"Resumo: {output_prefix}_summary.json")

        return exit_code.SUCCESS


    print(
        f"Operacao '{options.operation}' reconhecida, "
        "mas ainda nao implementada no projeto-base.",
        file=sys.stderr,
    )

    return exit_code.GENERAL_ERROR