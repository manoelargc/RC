import socket
import time
import statistics
import csv
import os

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
OUTPUT_DIR = "/app/outputs"  # Diretório para salvar os resultados no contêiner
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Garante que o diretório existe
IS_DOCKER = os.getenv("IS_DOCKER", "false").lower() == "true"  # Verifica se está sendo executado no Docker


# Configurações
# SERVER_HOST = 'server_tcp'
# SERVER_HOST = 'localhost'  # Certifique-se de usar 'localhost' ou o IP correto
SERVER_PORT = 587
NUM_REQUESTS = 1000      # número de sequências de comandos SMTP
USE_SESSION = False       # usa uma única conexão (True) ou uma nova conexão para cada requisição (False)
PRINT_OUTPUT = True      # imprime resultados no console
WRITE_TO_FILE = True     # grava resultados em arquivo
PRINT_REQUESTS = False   # imprime cada requisição no console


def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    return client_socket

def communicate_with_server(client_socket, command):
    client_socket.sendall(command.encode())
    response = client_socket.recv(1024)
    if PRINT_REQUESTS:
        print(f"Enviado: {command}")
    return response.decode()

def measure_execution_time(func, *args):
    start_time = time.perf_counter()
    func(*args)
    end_time = time.perf_counter()
    return (end_time - start_time) * 1e6

def execute_command_sequence(client_socket, commands):
    times = []
    for command in commands:
        time_elapsed = measure_execution_time(communicate_with_server, client_socket, command)
        times.append(time_elapsed)
        # time.sleep(0.001)  #PARA DOCKER

    return times

def run_requests():
    commands = ["HELO", "MAIL FROM:<teste@cliente.com>", "RCPT TO:<destino@servidor.com>", "QUIT"]
    times = []
    client_socket = None

    if USE_SESSION:
        client_socket = connect_to_server()

    for _ in range(NUM_REQUESTS):
        if USE_SESSION:
            times.extend(execute_command_sequence(client_socket, commands))
        else:
            with connect_to_server() as client_socket:
                times.extend(execute_command_sequence(client_socket, commands))

    if USE_SESSION and client_socket:
        client_socket.close()

    return times

def calculate_metrics(times):
    avg_time = statistics.mean(times)
    median_time = statistics.median(times)
    std_dev_time = statistics.stdev(times)
    min_time = min(times)
    max_time = max(times)
    return avg_time, median_time, std_dev_time, min_time, max_time

def save_metrics_to_csv(metrics, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    avg_time, median_time, std_dev_time, min_time, max_time = metrics
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Métrica", "Tempo (µs)"])
        writer.writerow(["Média", f"{avg_time:.2f}"])
        writer.writerow(["Mediana", f"{median_time:.2f}"])
        writer.writerow(["Desvio Padrão", f"{std_dev_time:.2f}"])
        writer.writerow(["Mínimo", f"{min_time:.2f}"])
        writer.writerow(["Máximo", f"{max_time:.2f}"])

def tcp_client():
    times = run_requests()
    metrics = calculate_metrics(times)

    avg_time, median_time, std_dev_time, min_time, max_time = metrics

    if PRINT_OUTPUT:
        print(f"Resultados para {NUM_REQUESTS} sequências de comandos SMTP no servidor TCP:")
        print(f"Tempo médio: {avg_time:.2f} µs")
        print(f"Mediana: {median_time:.2f} µs")
        print(f"Desvio padrão: {std_dev_time:.2f} µs")
        print(f"Tempo mínimo: {min_time:.2f} µs")
        print(f"Tempo máximo: {max_time:.2f} µs")

    if WRITE_TO_FILE:
        option = input("Deseja especificar o nome do arquivo para salvar os resultados? (y/n): ").strip().lower()
        if option == 'y':
            filename = input("Digite o nome do arquivo (com extensão .csv): ").strip()
            if not filename.endswith(".csv"):
                filename += ".csv"
        else:
            if IS_DOCKER:
                filename = OUTPUT_FILENAME  # Nome definido no Docker
            else:
                filename = "tcp_results.csv"  # Nome padrão fora do Docker

        save_metrics_to_csv(metrics, filename)
        print(f"Métricas salvas em: {filename}")

if __name__ == "__main__":
    tcp_client()
