import socket
import time
import statistics
import csv
import os

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
OUTPUT_DIR = os.path.abspath("./outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Garante que o diretório existe
IS_DOCKER = os.getenv("IS_DOCKER", "false").lower() == "true"  # Verifica se está sendo executado no Docker


# Configurações
# SERVER_HOST = 'server_tcp'
# SERVER_HOST = 'localhost'  # Certifique-se de usar 'localhost' ou o IP correto
SERVER_PORT = 587
NUM_REQUESTS = 1000      # número de sequências de comandos SMTP
USE_SESSION = os.getenv("USE_SESSION", "false").lower() == "true"
PRINT_OUTPUT = os.getenv("PRINT_OUTPUT", "true").lower() == "true"
WRITE_TO_FILE = os.getenv("WRITE_TO_FILE", "true").lower() == "true"



def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    return client_socket

def communicate_with_server(client_socket, command):
    client_socket.sendall(command.encode())
    response = client_socket.recv(1024)
    if PRINT_OUTPUT:
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
        time.sleep(0.01)  #PARA DOCKER

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

def save_all_metrics_to_csv(all_metrics, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Execução", "Média (µs)", "Mediana (µs)", "Desvio Padrão (µs)", "Mínimo (µs)", "Máximo (µs)"])
        for i, metrics in enumerate(all_metrics, start=1):
            writer.writerow([i] + [f"{value:.2f}" for value in metrics])
    print(f"Métricas de todas as execuções salvas em: {filepath}")

def tcp_client():
    all_metrics = []
    for i in range(10):  # Executa 10 vezes
        print(f"Executando {i+1}/10...")
        times = run_requests()
        metrics = calculate_metrics(times)
        all_metrics.append(metrics)

        avg_time, median_time, std_dev_time, min_time, max_time = metrics
        print(f"Execução {i+1}:")
        print(f"  Tempo médio: {avg_time:.2f} µs")
        print(f"  Mediana: {median_time:.2f} µs")
        print(f"  Desvio padrão: {std_dev_time:.2f} µs")
        print(f"  Tempo mínimo: {min_time:.2f} µs")
        print(f"  Tempo máximo: {max_time:.2f} µs")

    if WRITE_TO_FILE:
        option = input("Deseja especificar o nome do arquivo para salvar os resultados? (y/n): ").strip().lower()
        if option == 'y':
            filename = input("Digite o nome do arquivo (com extensão .csv): ").strip()
            if not filename.endswith(".csv"):
                filename += ".csv"
        else:
            filename = "tcp_all_metrics.csv" if not IS_DOCKER else "docker_tcp_all_metrics.csv"

        save_all_metrics_to_csv(all_metrics, filename)

if __name__ == "__main__":
    tcp_client()