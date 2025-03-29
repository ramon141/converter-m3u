import pyautogui
import time

def mover_mouse():
    # Obtém o tamanho da tela
    largura, altura = pyautogui.size()
    
    # Define as posições de destino
    posicao_esquerda = (10, altura // 2)          # Perto do lado esquerdo
    posicao_direita = (largura - 10, altura // 2) # Perto do lado direito
    
    while True:
        try:
            # Move para a posição esquerda
            pyautogui.moveTo(posicao_esquerda[0], posicao_esquerda[1], duration=1)
            
            # Espera por 30 segundos
            time.sleep(30)
            
            # Move para a posição direita
            pyautogui.moveTo(posicao_direita[0], posicao_direita[1], duration=1)
            
            # Espera por 30 segundos
            time.sleep(30)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            break

if __name__ == "__main__":
    mover_mouse()
