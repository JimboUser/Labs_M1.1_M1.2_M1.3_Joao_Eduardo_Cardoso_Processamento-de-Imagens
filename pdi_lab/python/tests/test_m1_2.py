from pathlib import Path

import cv2
import numpy as np

from pdi_lab.operations import (
    adjust_brightness,
    adjust_contrast,
    calculate_histogram,
    negative_image,
    threshold_image,
)

INPUT_DIR = Path("images/input")


def test_brightness_positive():
    image = np.array(
        [[0, 50, 100, 128, 200, 250, 255]],
        dtype=np.uint8,
    )

    resultado = adjust_brightness(image, 20)

    esperado = np.array(
        [[20, 70, 120, 148, 220, 255, 255]],
        dtype=np.uint8,
    )

    assert np.array_equal(resultado, esperado)


def test_brightness_negative():
    image = np.array(
        [[0, 50, 100, 128, 200, 250, 255]],
        dtype=np.uint8,
    )

    resultado = adjust_brightness(image, -30)

    esperado = np.array(
        [[0, 20, 70, 98, 170, 220, 225]],
        dtype=np.uint8,
    )

    assert np.array_equal(resultado, esperado)


def test_brightness_saturation():
    image = np.array(
        [[0, 250, 255]],
        dtype=np.uint8,
    )

    resultado = adjust_brightness(image, 20)

    esperado = np.array(
        [[20, 255, 255]],
        dtype=np.uint8,
    )

    assert np.array_equal(resultado, esperado)


def test_contrast_reduced():
    image = np.array(
        [[0, 50, 100, 128, 200, 255]],
        dtype=np.uint8,
    )

    resultado = adjust_contrast(image, 0.5)

    esperado = np.array(
        [[64, 89, 114, 128, 164, 192]],
        dtype=np.uint8,
    )

    assert np.array_equal(resultado, esperado)


def test_contrast_identity():
    image = np.array(
        [[0, 50, 100, 128, 200, 255]],
        dtype=np.uint8,
    )

    resultado = adjust_contrast(image, 1.0)

    assert np.array_equal(resultado, image)


def test_contrast_increased():
    image = np.array(
        [[0, 50, 100, 128, 200, 255]],
        dtype=np.uint8,
    )

    resultado = adjust_contrast(image, 1.5)

    esperado = np.array(
        [[0, 11, 86, 128, 236, 255]],
        dtype=np.uint8,
    )

    assert np.array_equal(resultado, esperado)


def test_negative():
    image = np.array(
        [[0, 50, 100, 128, 200, 255]],
        dtype=np.uint8,
    )

    resultado = negative_image(image)

    esperado = np.array(
        [[255, 205, 155, 127, 55, 0]],
        dtype=np.uint8,
    )

    assert np.array_equal(resultado, esperado)


def test_threshold_low():
    image = np.array(
        [[0, 50, 100, 128, 200, 255]],
        dtype=np.uint8,
    )

    resultado = threshold_image(image, 100)

    esperado = np.array(
        [[0, 0, 255, 255, 255, 255]],
        dtype=np.uint8,
    )

    assert np.array_equal(resultado, esperado)


def test_threshold_high():
    image = np.array(
        [[0, 50, 100, 128, 200, 255]],
        dtype=np.uint8,
    )

    resultado = threshold_image(image, 200)

    esperado = np.array(
        [[0, 0, 0, 0, 255, 255]],
        dtype=np.uint8,
    )

    assert np.array_equal(resultado, esperado)


def test_histogram():
    image = np.array(
        [[0, 0, 50, 100, 100, 100, 255]],
        dtype=np.uint8,
    )

    resultado = calculate_histogram(image)

    assert len(resultado) == 256
    assert resultado[0] == 2
    assert resultado[50] == 1
    assert resultado[100] == 3
    assert resultado[255] == 1
    assert sum(resultado) == 7


def test_m1_2_input_image():
    image = cv2.imread(
        str(INPUT_DIR / "m1_gray_steps_16levels.png"),
        cv2.IMREAD_GRAYSCALE,
    )

    assert image is not None
    assert image.ndim == 2
    assert image.dtype == np.uint8