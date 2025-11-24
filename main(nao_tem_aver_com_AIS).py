import serial
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from time import sleep
import threading
import json
import queue
import sys


# Configuração da porta serial
while True:
    try:
        ser = serial.Serial('/dev/ttyS0', 9600, timeout=0)
        break
    except:
        pass

  nome_id = 1
# Variável para indicar quando o código de processamento está em execução
processing_running = False

# Fila para armazenar comandos desconhecidos
data_receiver_queue= queue.Queue()


# Função para ativar a câmera e gravar missão 1 
def start1():
    picam.start_recording(encoder, output)

# Função para parar a gravação missão 1
def stop1():
    picam.stop_recording()
  
# Função para ativar a câmera e gravar missão 2 
def start2():
    picam.start_recording(encoder, output)

# Função para parar a gravação missão 2
def stop2():
    picam.stop_recording()
