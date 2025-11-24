import subprocess
import socket
import time
import csv
import os

# IMPORTA O DECODER (presume que essas funções existem no seu módulo)
from ais_decoder import (
    parse_nmea_sentence,
    ais_payload_to_bits,
    decode_position_report
)

print("Iniciando AIS-catcher...")
ais_process = subprocess.Popen(
    ["AIS-catcher", "-f", "162.0M", "-u", "127.0.0.1", "10110", "-y", "213.66.184.34", "5555", "-v", "10", "-o", "5"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

# espera rápida para o AIS-catcher iniciar
time.sleep(2)

UDP_IP = "127.0.0.1"
UDP_PORT = 10110

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("AIS iniciado. Aguardando mensagens...\n")

# Lista de registros AIS decodificados (opcional, mantém em memória)
ais_log = []  # cada item será: (timestamp_local, dict_dados)

# CSV
CSV_FILE = "ais_log.csv"
# cria CSV com cabeçalho se não existir
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp_local", "timestamp", "mmsi", "latitude", "longitude", "time"])

# inicia o contador de tempo que será registrado na coluna 'time'
start_time = time.time()

try:
    while True:
        data, addr = sock.recvfrom(4096)
        msg = data.decode(errors="ignore").strip()

        # Filtra apenas sentenças AIS
        if not msg.startswith("!AIVDM"):
            continue

        try:
            # 1) Extrai o payload NMEA
            payload = parse_nmea_sentence(msg)

            # 2) Converte para bits
            bits = ais_payload_to_bits(payload)

            # 3) Decodifica mensagem AIS (ex.: position report)
            decoded = decode_position_report(bits)

            # 4) Filtra apenas mensagens tipo 1 (se desejar manter este filtro)
            if decoded.get("message_id") != 1:
                continue

            # 5) Adiciona timestamp da recepção (local, epoch float)
            t_local = time.time()
            ais_log.append((t_local, decoded))

            # Extrai os campos requeridos
            timestamp_utc = decoded.get("timestamp", None)   # timestamp vindo do AIS (se disponível)
            mmsi = decoded.get("mmsi", None)                 # MMSI do navio
            lat = decoded.get("latitude", None)
            lon = decoded.get("longitude", None)

            # tempo decorrido desde o início do programa (em segundos, float)
            elapsed_time = time.time() - start_time

            # Grava no CSV (append)
            with open(CSV_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([t_local, timestamp_utc, mmsi, lat, lon, elapsed_time])

            # Impressão no console para monitoramento
            print("\n=== AIS RECEBIDO ===")
            print("Timestamp local:", t_local)
            for k, v in decoded.items():
                print(f"{k}: {v}")
            print(f"time (elapsed): {elapsed_time:.3f} s")

        except Exception as e:
            # Erro ao decodificar esta mensagem — continua recebendo as próximas
            print("Erro ao decodificar:", e)
            continue

except KeyboardInterrupt:
    print("\nEncerrando...")

finally:
    # encerra o processo AIS-catcher e fecha o socket
    try:
        ais_process.terminate()
        ais_process.wait(timeout=5)
    except Exception:
        pass

    try:
        sock.close()
    except Exception:
        pass

    print("AIS-catcher finalizado. CSV salvo em:", os.path.abspath(CSV_FILE))