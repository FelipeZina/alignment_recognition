from ultralytics import YOLO
from google.colab.patches import cv2_imshow
import cv2
import numpy as np
import math
from google.colab import drive


def calcular_angulo_3_pontos(pontos):
    """
    Calcula o ângulo de vértice, com base na ordem de anotação:
    [0: Braço Pivô (Vértice), 1: Canto do Suporte, 2: Ponta do Braço]
    """
    try:
        p_pivo = pontos[0]
        p_canto_suporte = pontos[1]
        p_ponta_braco = pontos[2]

        vetor_A = (p_canto_suporte[0] - p_pivo[0], p_canto_suporte[1] - p_pivo[1])
        vetor_B = (p_ponta_braco[0] - p_pivo[0], p_ponta_braco[1] - p_pivo[1])

        angulo_A = math.atan2(vetor_A[1], vetor_A[0])
        angulo_B = math.atan2(vetor_B[1], vetor_B[0])

        angulo_relativo_rad = angulo_B - angulo_A
        angulo_relativo_graus = math.degrees(angulo_relativo_rad)
        angulo_relativo_graus = (angulo_relativo_graus + 180) % 360 - 180

        ANGULO_IDEAL = 65.0
        TOLERANCIA = 7.0

        status = "ALINHADO" if abs(angulo_relativo_graus - ANGULO_IDEAL) <= TOLERANCIA else "DESALINHADO"
        return status, angulo_relativo_graus
    except Exception as e:
        print(f"Erro no cálculo do ângulo: {e}")
        return "ERRO", 0.0


print("Conectando ao Google Drive...")

model_path = "/content/drive/MyDrive/Modelo_final.pt"
print(f"Carregando modelo de: {model_path}")
model = YOLO(model_path)
print("Modelo carregado com sucesso!")

imagens_para_testar = [
    "muito_errada.png",
    "certa.png",
    "certa2.png",
    "pouco_errada.png"
]

print(f"\nIniciando análise de {len(imagens_para_testar)} imagens...")

for i, nome_imagem in enumerate(imagens_para_testar):

    print(f"\nanalise imagem {i+1}")

    img = cv2.imread(nome_imagem)

    if img is None:
        print(f"ERRO: Não foi possível carregar a imagem '{nome_imagem}'. Pulando.")
        continue

    results = model(img, conf=0.7, verbose=False)

    if results[0].names:
        results[0].names[0] = "kit"

    annotated_frame = results[0].plot(kpt_radius=10)
    if results[0].keypoints is not None and len(results[0].keypoints.xy) > 0 and len(results[0].keypoints.xy[0]) == 3:
        keypoints = results[0].keypoints.xy[0].cpu().numpy()

        status, valor = calcular_angulo_3_pontos(keypoints)
        texto_valor = f"ANGULO: {valor:.1f} GRAUS"

        cor = (0, 255, 0) if status == "ALINHADO" else (0, 0, 255)

        cv2.putText(annotated_frame, f"STATUS: {status}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 2, cor, 4)
        cv2.putText(annotated_frame, texto_valor, (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, cor, 3)
    else:
        cv2.putText(annotated_frame, "FALHA: 3 PONTOS NAO DETECTADOS", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 165, 255), 3)

    cv2_imshow(annotated_frame)
