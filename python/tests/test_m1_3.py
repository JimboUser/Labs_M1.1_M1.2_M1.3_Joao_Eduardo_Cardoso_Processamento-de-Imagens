import numpy as np

from pdi_lab.parameters import BorderStrategy
from pdi_lab.kernel import Kernel
from pdi_lab.operations import convolution, mean_filter, weighted_mean, laplacian, sharpen_with_laplacian, sobel


def test_convolution_identity_copy():
    image = np.array(
        [
            [10, 20, 30],
            [40, 50, 60],
            [70, 80, 90],
        ],
        dtype=np.uint8,
    )

    kernel = Kernel(
        size=3,
        values=(
            0.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 0.0,
        ),
    )

    resultado = convolution(
        image,
        kernel,
        BorderStrategy.COPY,
    )

    esperado = image.astype(np.float64)

    np.testing.assert_array_equal(resultado, esperado)


def test_convolution_mean_replicate():
    image = np.array(
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ],
        dtype=np.uint8,
    )

    kernel = Kernel(
        size=3,
        values=(
            1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0,
            1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0,
            1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0,
        ),
    )

    resultado = convolution(
        image,
        kernel,
        BorderStrategy.REPLICATE,
    )

    esperado = np.array(
        [
            [2.33333333, 3.0, 3.66666667],
            [4.33333333, 5.0, 5.66666667],
            [6.33333333, 7.0, 7.66666667],
        ],
        dtype=np.float64,
    )

    np.testing.assert_allclose(
        resultado,
        esperado,
        rtol=1e-7,
        atol=1e-7,
    )


def test_mean_filter_3_copy():
    image = np.array(
        [
            [0, 0, 0],
            [0, 255, 0],
            [0, 0, 0],
        ],
        dtype=np.uint8,
    )

    resultado = mean_filter(
        image,
        3,
        BorderStrategy.COPY,
    )

    esperado = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 255.0 / 9.0, 0.0],
            [0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )

    np.testing.assert_allclose(
        resultado,
        esperado,
        rtol=1e-7,
        atol=1e-7,
    )


def test_mean_filter_3_replicate():
    image = np.array(
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ],
        dtype=np.uint8,
    )

    resultado = mean_filter(
        image,
        3,
        BorderStrategy.REPLICATE,
    )

    esperado = np.array(
        [
            [2.33333333, 3.0, 3.66666667],
            [4.33333333, 5.0, 5.66666667],
            [6.33333333, 7.0, 7.66666667],
        ],
        dtype=np.float64,
    )

    np.testing.assert_allclose(
        resultado,
        esperado,
        rtol=1e-7,
        atol=1e-7,
    )


def test_mean_filter_5_copy():
    image = np.zeros((5, 5), dtype=np.uint8)
    image[2, 2] = 255

    resultado = mean_filter(
        image,
        5,
        BorderStrategy.COPY,
    )

    esperado = np.zeros((5, 5), dtype=np.float64)
    esperado[2, 2] = 255.0 / 25.0

    np.testing.assert_allclose(
        resultado,
        esperado,
        rtol=1e-7,
        atol=1e-7,
    )


def test_mean_filter_5_replicate():
    image = np.array(
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ],
        dtype=np.uint8,
    )

    resultado = mean_filter(
        image,
        5,
        BorderStrategy.REPLICATE,
    )

    esperado = np.array(
        [
            [3.4, 3.8, 4.2],
            [4.6, 5.0, 5.4],
            [5.8, 6.2, 6.6],
        ],
        dtype=np.float64,
    )

    np.testing.assert_allclose(
        resultado,
        esperado,
        rtol=1e-7,
        atol=1e-7,
    )


def test_mean_filter_content_on_border():
    image = np.zeros((3, 3), dtype=np.uint8)
    image[0, 0] = 255

    resultado = mean_filter(
        image,
        3,
        BorderStrategy.COPY,
    )

    esperado = np.array(
        [
            [255.0, 0.0, 0.0],
            [0.0, 255.0 / 9.0, 0.0],
            [0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )

    np.testing.assert_allclose(
        resultado,
        esperado,
        rtol=1e-7,
        atol=1e-7,
    )



def test_mean_filter_constant_image():
    image = np.full(
        (5, 5),
        100,
        dtype=np.uint8,
    )

    resultado = mean_filter(
        image,
        3,
        BorderStrategy.REPLICATE,
    )

    esperado = np.full(
        (5, 5),
        100.0,
        dtype=np.float64,
    )

    np.testing.assert_allclose(
        resultado,
        esperado,
        rtol=1e-7,
        atol=1e-7,
    )


def test_weighted_mean_copy():
    image = np.zeros((3, 3), dtype=np.uint8)
    image[1, 1] = 255

    resultado = weighted_mean(
        image,
        BorderStrategy.COPY,
    )

    esperado = np.zeros((3, 3), dtype=np.float64)
    esperado[1, 1] = 255.0 * (4.0 / 16.0)

    np.testing.assert_allclose(
        resultado,
        esperado,
        rtol=1e-7,
        atol=1e-7,
    )


def test_laplacian_copy():
    image = np.zeros((3, 3), dtype=np.uint8)
    image[1, 1] = 255

    resultado = laplacian(
        image,
        BorderStrategy.COPY,
    )

    esperado = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, -2040.0, 0.0],
            [0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )

    np.testing.assert_allclose(
        resultado,
        esperado,
        rtol=1e-7,
        atol=1e-7,
    )


def test_sobel_copy():
    image = np.array(
        [
            [0, 0, 255],
            [0, 0, 255],
            [0, 0, 255],
        ],
        dtype=np.uint8,
    )

    gx, gy, magnitude_aproximada, magnitude_euclidiana = sobel(
        image,
        BorderStrategy.COPY,
    )

    esperado_gx = np.array(
        [
            [0.0, 0.0, 255.0],
            [0.0, 1020.0, 255.0],
            [0.0, 0.0, 255.0],
        ],
        dtype=np.float64,
    )

    esperado_gy = np.array(
        [
            [0.0, 0.0, 255.0],
            [0.0, 0.0, 255.0],
            [0.0, 0.0, 255.0],
        ],
        dtype=np.float64,
    )

    esperado_magnitude_aproximada = (
        np.abs(esperado_gx) + np.abs(esperado_gy)
    )

    esperado_magnitude_euclidiana = np.sqrt(
        esperado_gx * esperado_gx
        + esperado_gy * esperado_gy
    )

    np.testing.assert_allclose(
        gx,
        esperado_gx,
        rtol=1e-7,
        atol=1e-7,
    )

    np.testing.assert_allclose(
        gy,
        esperado_gy,
        rtol=1e-7,
        atol=1e-7,
    )

    np.testing.assert_allclose(
        magnitude_aproximada,
        esperado_magnitude_aproximada,
        rtol=1e-7,
        atol=1e-7,
    )

    np.testing.assert_allclose(
        magnitude_euclidiana,
        esperado_magnitude_euclidiana,
        rtol=1e-7,
        atol=1e-7,
    )


def test_sobel_magnitudes():
    image = np.array(
        [
            [0, 0, 255],
            [0, 255, 255],
            [255, 255, 255],
        ],
        dtype=np.uint8,
    )

    gx, gy, magnitude_aproximada, magnitude_euclidiana = sobel(
        image,
        BorderStrategy.COPY,
    )

    esperado_magnitude_aproximada = (
        np.abs(gx) + np.abs(gy)
    )

    esperado_magnitude_euclidiana = np.sqrt(
        gx * gx + gy * gy
    )

    np.testing.assert_allclose(
        magnitude_aproximada,
        esperado_magnitude_aproximada,
        rtol=1e-7,
        atol=1e-7,
    )

    np.testing.assert_allclose(
        magnitude_euclidiana,
        esperado_magnitude_euclidiana,
        rtol=1e-7,
        atol=1e-7,
    )


def test_sobel_horizontal_step():
    image = np.array(
        [
            [0, 0, 0],
            [0, 0, 0],
            [255, 255, 255],
        ],
        dtype=np.uint8,
    )

    gx, gy, _, _ = sobel(
        image,
        BorderStrategy.COPY,
    )

    assert gx[1, 1] == 0.0
    assert gy[1, 1] == 1020.0