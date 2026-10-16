
from pathlib import Path

import cv2
import numpy as np


def criar_sobreposicao(
    imagem: np.ndarray,
    mascara: np.ndarray,
    alpha: float = 0.4,
) -> np.ndarray:
    """Destaca em vermelho os pixels classificados como objeto."""

    if imagem is None or imagem.size == 0:
        raise ValueError("A imagem original está vazia.")

    if mascara is None or mascara.size == 0:
        raise ValueError("A máscara está vazia.")

    if imagem.ndim != 3 or imagem.shape[2] != 3:
        raise ValueError("A imagem original deve ter três canais.")

    if mascara.ndim != 2:
        raise ValueError("A máscara deve ter um único canal.")

    if imagem.shape[:2] != mascara.shape:
        raise ValueError(
            "A imagem e a máscara devem ter as mesmas dimensões."
        )

    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha deve estar entre 0 e 1.")

    if not np.isin(mascara, [0, 255]).all():
        raise ValueError("A máscara deve conter apenas 0 e 255.")

    resultado = imagem.copy()
    selecionados = mascara == 255

    vermelho = np.zeros_like(imagem)
    vermelho[:] = (0, 0, 255)  # BGR

    resultado[selecionados] = cv2.addWeighted(
        imagem[selecionados],
        1.0 - alpha,
        vermelho[selecionados],
        alpha,
        0,
    )

    return resultado


def main():
    raiz = Path(__file__).resolve().parents[1]
    pasta_entrada = raiz / "images" / "input"
    pasta_saida = raiz / "images" / "output"

    casos = [
        ("laranjas.png", "laranjas_hsv.png",
         "laranjas_hsv_overlay.png"),
        ("laranjas.png", "laranjas_fixed.png",
         "laranjas_fixed_overlay.png"),
        ("limoes.png", "limoes_hsv.png",
         "limoes_hsv_overlay.png"),
        ("limoes.png", "limoes_fixed.png",
         "limoes_fixed_overlay.png"),
    ]

    pasta_saida.mkdir(parents=True, exist_ok=True)

    for nome_imagem, nome_mascara, nome_saida in casos:
        imagem = cv2.imread(
            str(pasta_entrada / nome_imagem),
            cv2.IMREAD_COLOR,
        )
        mascara = cv2.imread(
            str(pasta_saida / nome_mascara),
            cv2.IMREAD_GRAYSCALE,
        )

        if imagem is None:
            raise FileNotFoundError(
                f"Imagem não encontrada: {nome_imagem}"
            )

        if mascara is None:
            raise FileNotFoundError(
                f"Máscara não encontrada: {nome_mascara}"
            )

        sobreposicao = criar_sobreposicao(imagem, mascara)
        caminho_saida = pasta_saida / nome_saida

        if not cv2.imwrite(str(caminho_saida), sobreposicao):
            raise OSError(
                f"Não foi possível salvar: {caminho_saida}"
            )

        print(f"Sobreposição salva: {caminho_saida}")


if __name__ == "__main__":
    main()
