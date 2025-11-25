import subprocess
import threading
import json
from time import sleep
import queue

# Variável para indicar quando o código de processamento está em execução
processing_running = False

nome_id = 1
# Fila para armazenar comandos desconhecidos
data_receiver_queue= queue.Queue()

# Função para ativar a câmera e começar a gravar vídeo
def start_recording():
    try:
        print("Gravação iniciada.")
    except Exception as e:
        print("Erro ao iniciar a gravação:", str(e))

# Função para parar a gravação e salvar o vídeo
def stop_recording():
    try:
        print("Gravação interrompida.")
    except Exception as e:
        print("Erro ao parar a gravação:", str(e))

# Função para executar o código de processamento 1
def run_processing_code_1():
    nome = "cena01.mp4"
    print(nome)
    global processing_running
    processing_running = True
    print("Executando o código de processamento 1")
    result = subprocess.run(['python3', 'cena_01.py', nome], capture_output=True, text=True)
    result_list = json.loads(result.stdout)
    
    chunk_size = 4
    result_chunks = [result_list[i:i + chunk_size] for i in range(0, len(result_list), chunk_size)]

    for chunk in result_chunks:
        dado  = ""
        size = len(chunk)
        for l in range(0,size):
            coordenadas = chunk[l]
            if l != size-1:
                dado += str(coordenadas[0]) + ',' + str(coordenadas[1]) + ','
            else:
                dado += str(coordenadas[0]) + ',' + str(coordenadas[1])
        print(dado)
        sleep(2)

    print("Código de processamento 1 concluído")
    processing_running = False

# Função para executar o código de processamento 2
def run_processing_code_2():
    nome = "raios_4.mp4"
    global processing_running
    processing_running = True
    print("Executando o código de processamento 2")
    result_cena2 = subprocess.run(['python3', 'cena_02.py', nome], capture_output=True, text=True)
    result = round(float(result_cena2.stdout),5)
    resultado = str(result)
    print(resultado)
    print("Código de processamento 2 concluído")
    processing_running = False


def save_data():
    while True:
        if not data_receiver_queue.empty():
            command = data_receiver_queue.get()
            try:
                with open('unknown_commands.txt', 'a') as file:
                    file.write(command + '\n')
            except Exception as e:
                print("Erro ao salvar comando desconhecido:", str(e))
        else:
            sleep(0.1)

# Inicialização da thread para salvar comandos desconhecidos em um arquivo
save_thread = threading.Thread(target=save_data)
save_thread.daemon = True
save_thread.start()

# Thread para monitorar a porta serial e executar comandos

while True: 
    command = input('Insira o comando:')
    command = str(command)      
    if command == '1':
        nome = "video_%d" % nome_id
        nome_id += 1
        start_recording()
    elif command == '2':
        stop_recording()
    elif command == '3':
        if not processing_running:
            threading.Thread(target=run_processing_code_1).start()
        else:
            print("O código de processamento já está em execução.")
    elif command == '4':
        if not processing_running:
            threading.Thread(target=run_processing_code_2).start()
        else:
            print("O código de processamento já está em execução.")
    else:
        data_receiver_queue.put(command)
