import socket
import time
import statistics
import csv
import os

# obtem as configuracoes do ambiente ou usa valores padrao
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
OUTPUT_DIR = os.path.abspath("./outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)  # garante que o diretorio existe
IS_DOCKER = os.getenv("IS_DOCKER", "false").lower() == "true"  # verifica se esta sendo executado no Docker
SERVER_PORT = 25
NUM_REQUESTS = 1000  # numero de sequencias de comandos SMTP
PRINT_OUTPUT = os.getenv("PRINT_OUTPUT", "false").lower() == "true"
WRITE_TO_FILE = os.getenv("WRITE_TO_FILE", "true").lower() == "true"

# funcao para enviar e receber dados via UDP
def communicate_with_server(client_socket, command):
    client_socket.sendto(command.encode(), (SERVER_HOST, SERVER_PORT))
    response, _ = client_socket.recvfrom(1024)  # recebe a resposta do servidor
    if PRINT_OUTPUT:  # verifica se a impressao esta habilitada
        print(f"Enviado: {command}")
    return response.decode()

# mede o tempo de execucao de uma funcao
def measure_execution_time(func, *args):
    start_time = time.perf_counter()
    func(*args)
    end_time = time.perf_counter()
    return (end_time - start_time) * 1e6  # converte de segundos para microssegundos

# executa uma sequencia de comandos e mede os tempos
def execute_command_sequence(client_socket, commands):
    times = []
    for command in commands:
        time_elapsed = measure_execution_time(communicate_with_server, client_socket, command)
        times.append(time_elapsed)
    return times

# executa todas as requisicoes
def run_requests():
    commands = ["HELO", "MAIL FROM:<teste@cliente.com>", "RCPT TO:<destino@servidor.com>", "QUIT"]
    times = []

    # usa um unico socket para enviar todas as mensagens, ja que UDP nao estabelece conexao
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        for _ in range(NUM_REQUESTS):
            times.extend(execute_command_sequence(client_socket, commands))

    return times

# calcula as metricas dos tempos de execucao
def calculate_metrics(times):
    avg_time = statistics.mean(times)
    median_time = statistics.median(times)
    std_dev_time = statistics.stdev(times)
    min_time = min(times)
    max_time = max(times)
    return avg_time, median_time, std_dev_time, min_time, max_time

# salva as metricas no arquivo CSV com configuracoes no topo
def save_all_metrics_to_csv(all_metrics, config):
    """
    Salva métricas no arquivo CSV com informações da configuração no topo.
    """
    filename = f"{config['protocol']}_results_" \
               f"{'print' if config.get('print_output', False) else 'noprint'}_" \
               f"{'write' if config.get('write_to_file', False) else 'nowrite'}.csv"

    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, mode="w", newline="") as file:
        writer = csv.writer(file)
        
        # escreve as configurações como comentário
        writer.writerow([f"# Configurações: SERVER_HOST={SERVER_HOST}, "
                         f"PRINT_OUTPUT={config.get('print_output')}, "
                         f"WRITE_TO_FILE={config.get('write_to_file')}"])
        
        # escreve o cabeçalho das métricas
        writer.writerow(["Execução", "Média (µs)", "Mediana (µs)", "Desvio Padrão (µs)", "Mínimo (µs)", "Máximo (µs)"])
        
        # escreve as métricas
        for i, metrics in enumerate(all_metrics, start=1):
            writer.writerow([i] + [f"{value:.2f}" for value in metrics])
    
    print(f"Métricas salvas em: {filepath}")

# funcao principal para executar o cliente UDP
def udp_client():
    """
    Executa 10 vezes a configuração atual e salva um único arquivo CSV.
    """
    config = {
        "protocol": "udp",
        "print_output": PRINT_OUTPUT,
        "write_to_file": WRITE_TO_FILE,
    }
    all_metrics = []

    # executa 10 vezes e armazena as métricas
    for i in range(10):
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

    # salva as métricas no arquivo
    if WRITE_TO_FILE:
        save_all_metrics_to_csv(all_metrics, config)

if __name__ == "__main__":
    udp_client()