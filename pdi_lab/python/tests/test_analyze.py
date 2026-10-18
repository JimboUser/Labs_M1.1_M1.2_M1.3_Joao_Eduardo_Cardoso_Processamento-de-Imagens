
import json

import cv2
import numpy as np
import pytest

from pdi_lab.operations import (
    analyze_components,
    apply_morphology_sequence,
    load_morphology_config,
)


def test_connectivity_4_counts_diagonal_pixels_separately():
    """Pixels diagonais formam componentes distintos com conectividade 4."""
    mask = np.zeros((3, 3), dtype=np.uint8)
    mask[0, 0] = 255
    mask[1, 1] = 255

    _, components = analyze_components(mask, connectivity=4)

    assert len(components) == 2
    assert sum(c["area"] for c in components) == 2


def test_connectivity_8_connects_diagonal_pixels():
    """Pixels diagonais pertencem ao mesmo componente com conectividade 8."""
    mask = np.zeros((3, 3), dtype=np.uint8)
    mask[0, 0] = 255
    mask[1, 1] = 255

    _, components = analyze_components(mask, connectivity=8)

    assert len(components) == 1
    assert components[0]["area"] == 2


def test_empty_mask_has_no_components():
    """Uma máscara vazia não deve produzir componentes de primeiro plano."""
    mask = np.zeros((5, 5), dtype=np.uint8)

    labels, components = analyze_components(mask, connectivity=8)

    assert len(components) == 0
    assert np.count_nonzero(labels) == 0


def test_component_touching_border_is_counted():
    """Um objeto encostado na borda deve ser contado normalmente."""
    mask = np.zeros((5, 5), dtype=np.uint8)
    mask[0:2, 0:2] = 255

    _, components = analyze_components(mask, connectivity=8)

    assert len(components) == 1
    assert components[0]["area"] == 4
    assert components[0]["x"] == 0
    assert components[0]["y"] == 0


def test_component_areas_equal_foreground_pixel_count():
    """A soma das áreas deve corresponder aos pixels brancos da máscara."""
    mask = np.zeros((8, 8), dtype=np.uint8)
    mask[1:3, 1:3] = 255
    mask[5:7, 5:8] = 255

    _, components = analyze_components(mask, connectivity=8)

    assert sum(c["area"] for c in components) == np.count_nonzero(
        mask == 255
    )


@pytest.mark.parametrize("connectivity", [0, 5, 6, 9, -1])
def test_invalid_connectivity_is_rejected(connectivity):
    """Somente conectividade 4 ou 8 deve ser aceita."""
    mask = np.zeros((3, 3), dtype=np.uint8)

    with pytest.raises(ValueError, match="conectividade"):
        analyze_components(mask, connectivity=connectivity)


def test_non_binary_mask_is_rejected():
    """A análise deve rejeitar máscaras com valores diferentes de 0 e 255."""
    mask = np.zeros((3, 3), dtype=np.uint8)
    mask[1, 1] = 127

    with pytest.raises(ValueError, match="0 e 255"):
        analyze_components(mask)


def test_opening_removes_small_noise(tmp_path):
    """A abertura deve remover um pixel isolado sem eliminar a região maior."""
    mask = np.zeros((15, 15), dtype=np.uint8)

    # Região principal suficientemente grande para sobreviver à abertura.
    mask[4:11, 4:11] = 255

    # Ruído isolado.
    mask[1, 1] = 255

    config = {
        "kernel_shape": "rect",
        "kernel_size": 3,
        "iterations": 1,
        "sequence": [
            {"operation": "open", "purpose": "Teste de ruído"},
            {"operation": "close", "purpose": "Segunda etapa obrigatória"},
        ],
    }

    result = apply_morphology_sequence(
        mask, config, str(tmp_path / "opening")
    )

    # A função retorna máscara e estatísticas por etapa.
    if isinstance(result, tuple):
        final_mask, stage_statistics = result
    else:
        final_mask = result
        stage_statistics = []

    assert final_mask[1, 1] == 0
    assert np.count_nonzero(final_mask == 255) > 0

    if stage_statistics:
        assert stage_statistics[0]["operation"] == "open"
        assert stage_statistics[0]["foreground_area"] < np.count_nonzero(
            mask == 255
        )


def test_closing_fills_small_hole(tmp_path):
    """O fechamento deve preencher um pequeno buraco dentro de uma região."""
    mask = np.zeros((9, 9), dtype=np.uint8)
    mask[2:7, 2:7] = 255
    mask[4, 4] = 0

    config = {
        "kernel_shape": "rect",
        "kernel_size": 3,
        "iterations": 1,
        "sequence": [
            {"operation": "close", "purpose": "Preencher o buraco"},
            {"operation": "open", "purpose": "Segunda operação"},
        ],
    }

    result = apply_morphology_sequence(
        mask, config, str(tmp_path / "closing")
    )

    if isinstance(result, tuple):
        final_mask, _ = result
    else:
        final_mask = result

    assert final_mask[4, 4] == 255


def test_morphology_stages_are_saved(tmp_path):
    """A sequência deve salvar a máscara inicial, etapas e máscara final."""
    mask = np.zeros((9, 9), dtype=np.uint8)
    mask[2:7, 2:7] = 255

    config = {
        "kernel_shape": "ellipse",
        "kernel_size": 3,
        "iterations": 1,
        "sequence": [
            {"operation": "open", "purpose": "Primeira etapa"},
            {"operation": "close", "purpose": "Segunda etapa"},
        ],
    }

    prefix = str(tmp_path / "sample")
    apply_morphology_sequence(mask, config, prefix)

    assert (tmp_path / "sample_initial.png").exists()
    assert (tmp_path / "sample_stage_01_open.png").exists()
    assert (tmp_path / "sample_stage_02_close.png").exists()
    assert (tmp_path / "sample_final.png").exists()


def test_invalid_morphology_config_is_rejected(tmp_path):
    """A configuração precisa conter uma sequência morfológica válida."""
    config_path = tmp_path / "invalid.json"
    config_path.write_text(
        json.dumps(
            {
                "kernel_shape": "invalid",
                "kernel_size": 3,
                "iterations": 1,
                "sequence": [
                    {"operation": "open", "purpose": "Teste"},
                    {"operation": "close", "purpose": "Teste"},
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_morphology_config(str(config_path))
