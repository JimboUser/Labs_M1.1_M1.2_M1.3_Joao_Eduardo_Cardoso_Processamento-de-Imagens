from pathlib import Path

import cv2
import numpy as np

from pdi_lab.operations import (
    copy_image_manual,
    extract_channel,
    grayscale_average,
    grayscale_weighted,
    quantize_image,
)


INPUT_DIR = Path("images/input")


def test_copy_image_manual():
    image = cv2.imread(
        str(INPUT_DIR / "m1_color_2x2.png"),
        cv2.IMREAD_UNCHANGED,
    )

    copia = copy_image_manual(image)

    assert np.array_equal(image, copia)


def test_extract_channels():
    image = cv2.imread(
        str(INPUT_DIR / "m1_color_2x2.png"),
        cv2.IMREAD_UNCHANGED,
    )

    azul = extract_channel(image, 0)
    verde = extract_channel(image, 1)
    vermelho = extract_channel(image, 2)

    assert np.array_equal(azul[:, :, 0], image[:, :, 0])
    assert np.all(azul[:, :, 1] == 0)
    assert np.all(azul[:, :, 2] == 0)

    assert np.all(verde[:, :, 0] == 0)
    assert np.array_equal(verde[:, :, 1], image[:, :, 1])
    assert np.all(verde[:, :, 2] == 0)

    assert np.all(vermelho[:, :, 0] == 0)
    assert np.all(vermelho[:, :, 1] == 0)
    assert np.array_equal(vermelho[:, :, 2], image[:, :, 2])


def test_grayscale_operations():
    image = cv2.imread(
        str(INPUT_DIR / "m1_color_2x2.png"),
        cv2.IMREAD_UNCHANGED,
    )

    media = grayscale_average(image)
    ponderada = grayscale_weighted(image)

    esperado_media = np.array(
        [
            [85, 85],
            [85, 255],
        ],
        dtype=np.uint8,
    )

    esperado_ponderada = np.array(
        [
            [76, 150],
            [29, 255],
        ],
        dtype=np.uint8,
    )

    assert np.array_equal(media, esperado_media)
    assert np.array_equal(ponderada, esperado_ponderada)


def test_quantization_levels():
    image = cv2.imread(
        str(INPUT_DIR / "m1_gray_steps_16levels.png"),
        cv2.IMREAD_GRAYSCALE,
    )

    esperados = {
        2: 2,
        4: 4,
        8: 8,
        16: 16,
    }

    for levels, quantidade_esperada in esperados.items():
        resultado = quantize_image(image, levels)

        valores = np.unique(resultado)

        assert len(valores) == quantidade_esperada
        assert valores.min() >= 0
        assert valores.max() <= 255


def test_quantization_boundaries():
    image = cv2.imread(
        str(INPUT_DIR / "m1_quant_boundary.png"),
        cv2.IMREAD_GRAYSCALE,
    )

    resultado = quantize_image(image, 4)

    esperado = np.array(
        [[0, 0, 0, 85, 85, 170, 170, 255, 255, 255]],
        dtype=np.uint8,
    )

    assert np.array_equal(resultado, esperado)