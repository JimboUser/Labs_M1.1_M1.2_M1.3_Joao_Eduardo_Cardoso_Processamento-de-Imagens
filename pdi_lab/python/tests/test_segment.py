
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

from pdi_lab.operations import segment_fixed, segment_hsv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "images" / "input"


def assert_binary_mask(mask):
    """Confirma que a máscara é 2D e contém apenas 0 e 255."""
    assert mask.ndim == 2
    assert set(np.unique(mask)).issubset({0, 255})


def read_image(path):
    """Lê imagens mesmo quando o caminho contém caracteres Unicode."""
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def test_fixed_threshold_below_equal_above():
    image = np.array([[159, 160, 161]], dtype=np.uint8)

    mask = segment_fixed(image, threshold=160)

    np.testing.assert_array_equal(
        mask,
        np.array([[0, 255, 255]], dtype=np.uint8),
    )
    assert_binary_mask(mask)


def test_fixed_threshold_inverted():
    image = np.array([[159, 160, 161]], dtype=np.uint8)

    mask = segment_fixed(image, threshold=160, invert=True)

    np.testing.assert_array_equal(
        mask,
        np.array([[255, 0, 0]], dtype=np.uint8),
    )
    assert_binary_mask(mask)


def test_hsv_selects_colors_inside_range():
    # BGR: vermelho, verde, preto e branco.
    image = np.array(
        [[
            [0, 0, 255],
            [0, 255, 0],
            [0, 0, 0],
            [255, 255, 255],
        ]],
        dtype=np.uint8,
    )

    mask = segment_hsv(
        image,
        lower=[0, 100, 100],
        upper=[10, 255, 255],
    )

    np.testing.assert_array_equal(
        mask,
        np.array([[255, 0, 0, 0]], dtype=np.uint8),
    )
    assert_binary_mask(mask)


def test_hsv_rejects_grayscale_image():
    image = np.array([[0, 100, 200]], dtype=np.uint8)

    with pytest.raises(ValueError):
        segment_hsv(image, lower=[0, 100, 100], upper=[10, 255, 255])


def run_cli(*args):
    """Executa a aplicação como o usuário faria pelo terminal."""
    return subprocess.run(
        [sys.executable, "-m", "pdi_lab", *map(str, args)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("image_name", "method", "extra_args"),
    [
        ("limoes.png", "fixed", ["--threshold", "160"]),
        ("limoes.png", "hsv", [
            "--h_min", "5", "--s_min", "60", "--v_min", "40",
            "--h_max", "30", "--s_max", "255", "--v_max", "255",
        ]),
        ("laranjas.png", "fixed", ["--threshold", "160"]),
        ("laranjas.png", "fixed", ["--threshold", "160", "--invert"]),
        ("laranjas.png", "hsv", [
            "--h_min", "5", "--s_min", "60", "--v_min", "40",
            "--h_max", "30", "--s_max", "255", "--v_max", "255",
        ]),
    ],
)
def test_real_images_produce_binary_masks(
    tmp_path, image_name, method, extra_args
):
    input_path = INPUT_DIR / image_name
    output_path = tmp_path / f"{Path(image_name).stem}_{method}.png"

    original = read_image(input_path)
    assert original is not None, f"Não foi possível ler {input_path}"

    result = run_cli(
        "--input", input_path,
        "--output", output_path,
        "--operation", "segment",
        "--method", method,
        *extra_args,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert output_path.exists()

    mask = cv2.imread(str(output_path), cv2.IMREAD_UNCHANGED)
    assert mask is not None
    assert mask.ndim == 2
    assert mask.shape == original.shape[:2]
    assert_binary_mask(mask)


def test_unknown_method_fails(tmp_path):
    input_path = INPUT_DIR / "limoes.png"
    output_path = tmp_path / "unknown.png"

    result = run_cli(
        "--input", input_path,
        "--output", output_path,
        "--operation", "segment",
        "--method", "unknown",
    )

    assert result.returncode != 0


def test_missing_input_fails(tmp_path):
    output_path = tmp_path / "missing.png"

    result = run_cli(
        "--input", tmp_path / "arquivo_inexistente.png",
        "--output", output_path,
        "--operation", "segment",
        "--method", "fixed",
        "--threshold", "160",
    )

    assert result.returncode != 0


def test_invalid_fixed_threshold_fails(tmp_path):
    input_path = INPUT_DIR / "limoes.png"
    output_path = tmp_path / "invalid_threshold.png"

    result = run_cli(
        "--input", input_path,
        "--output", output_path,
        "--operation", "segment",
        "--method", "fixed",
        "--threshold", "300",
    )

    assert result.returncode != 0
