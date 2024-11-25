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
# SERVER_HOST = 'server_udp'
# SERVER_HOST = 'localhost' 
SERVER_PORT = 25
NUM_REQUESTS = 1000      # número de sequências de comandos SMTP
PRINT_OUTPUT = True       # imprime resultados no console
WRITE_TO_FILE = True      # grava resultados em arquivo
PRINT_REQUESTS = False     # imprime cada requisição no console

def communicate_with_server(client_socket, command):
    client_socket.sendto(command.encode(), (SERVER_HOST, SERVER_PORT))
    response, _ = client_socket.recvfrom(1024)  # Recebe a resposta rapidamente
    return response.decode()

def measure_execution_time(func, *args):
    start_time = time.perf_counter()
    func(*args)  # Executa a função com os argumentos fornecidos
    end_time = time.perf_counter()
    return (end_time - start_time) * 1e6  # Converte de segundos para microssegundos


def execute_command_sequence(client_socket, commands):
    times = []
    for command in commands:
        time_elapsed = measure_execution_time(communicate_with_server, client_socket, command)
        times.append(time_elapsed)
    return times

def run_requests():
    commands = ["HELO", "MAIL FROM:<teste@cliente.com>", "RCPT TO:<destino@servidor.com>", "QUIT"]
    times = []

    # Usa um único socket para enviar todas as mensagens, já que UDP não estabelece conexão
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        for _ in range(NUM_REQUESTS):
            times.extend(execute_command_sequence(client_socket, commands))
                
    return times


def calculate_metrics(times):
    avg_time = statistics.mean(times)
    median_time = statistics.median(times)
    std_dev_time = statistics.stdev(times)
    min_time = min(times)
    max_time = max(times)
    return avg_time, median_time, std_dev_time, min_time, max_time


def save_metrics(metrics, filename):
    avg_time, median_time, std_dev_time, min_time, max_time = metrics
    with open(filename, "w") as file:
        file.write(f"Resultados para {NUM_REQUESTS} sequências de comandos SMTP no servidor UDP:\n")
        file.write(f"Tempo médio: {avg_time:.2f} µs\n")
        file.write(f"Mediana: {median_time:.2f} µs\n")
        file.write(f"Desvio padrão: {std_dev_time:.2f} µs\n")
        file.write(f"Tempo mínimo: {min_time:.2f} µs\n")
        file.write(f"Tempo máximo: {max_time:.2f} µs\n")


def save_metrics_to_csv(metrics, filename=None):
    if filename is None:
        filename = OUTPUT_FILENAME
    filepath = os.path.join(OUTPUT_DIR, filename)
    avg_time, median_time, std_dev_time, min_time, max_time = metrics
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Escreve o cabeçalho
        writer.writerow(["Tipo", "Tempo (µs)"])
        # Escreve os tempos individuais
        # Escreve as métricas
        writer.writerow(["Média", avg_time])
        writer.writerow(["Mediana", median_time])
        writer.writerow(["Desvio Padrão", std_dev_time])
        writer.writerow(["Mínimo", min_time])
        writer.writerow(["Máximo", max_time])


def udp_client():
    times = run_requests()
    metrics = calculate_metrics(times)

    avg_time, median_time, std_dev_time, min_time, max_time = metrics

    if PRINT_OUTPUT:
        print(f"Resultados para {NUM_REQUESTS} sequências de comandos SMTP no servidor UDP:")
        print(f"Tempo médio: {avg_time:.2f} µs")
        print(f"Mediana: {median_time:.2f} µs")
        print(f"Desvio padrão: {std_dev_time:.2f} µs")
        print(f"Tempo mínimo: {min_time:.2f} µs")
        print(f"Tempo máximo: {max_time:.2f} µs")

    # Salvar resultados em arquivos
    if WRITE_TO_FILE:
        # Salvar métricas em arquivo de texto
        filename = "udp_metrics.txt"
        save_metrics(metrics, filename)
        
        option = input("Deseja especificar o nome do arquivo para salvar os resultados? (y/n): ").strip().lower()
        if option == 'y':
            filename = input("Digite o nome do arquivo (com extensão .csv): ").strip()
            if not filename.endswith(".csv"):
                filename += ".csv"
        else:
            if IS_DOCKER:
                filename = OUTPUT_FILENAME  # Nome definido no Docker
            else:
                filename = "udp_results.csv"  # Nome padrão fora do Docker


        save_metrics_to_csv(metrics, filename)
        print(f"Métricas salvas em: {filename}")




if __name__ == "__main__":
    udp_client()
