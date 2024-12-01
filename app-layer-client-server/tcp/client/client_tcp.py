import socket
import time
import statistics
import csv
import os

# Configurações de ambiente
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
OUTPUT_DIR = os.path.abspath("./outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Garante que o diretório existe
IS_DOCKER = os.getenv("IS_DOCKER", "false").lower() == "true"
SERVER_PORT = 587
NUM_REQUESTS = 10  # Número de sequências de comandos SMTP
USE_SESSION = os.getenv("USE_SESSION", "true").lower() == "true"
PRINT_OUTPUT = os.getenv("PRINT_OUTPUT", "false").lower() == "true"
WRITE_TO_FILE = os.getenv("WRITE_TO_FILE", "true").lower() == "true"  # Mantido para o nome e cabeçalho
filepath = OUTPUT_DIR  # Diretório base para saída


# Função para gerar nomes de arquivos baseados na configuração
def generate_output_filename(protocol, use_session, print_output, write_to_file):
    session_status = "session" if use_session else "nosession"
    print_status = "print" if print_output else "noprint"
    write_status = "write" if write_to_file else "nowrite"
    return os.path.join(OUTPUT_DIR, f"{protocol}_results_{session_status}_{print_status}_{write_status}.csv")


# Funções principais do cliente
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
        time.sleep(0.01)  # Latência adicional
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


# Função para salvar métricas no CSV
def save_all_metrics_to_csv(all_metrics, config, filename):
    dir_path = os.path.dirname(filename)
    os.makedirs(dir_path, exist_ok=True)  # Garante que o diretório existe

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Escreve as configurações no cabeçalho do arquivo
        writer.writerow([f"# Configurações: PROTOCOLO={config['protocol']}, "
                         f"SESSÃO={config.get('use_session', 'n/a')}, "
                         f"PRINT_OUTPUT={config['print_output']}, "
                         f"WRITE_TO_FILE={config['write_to_file']}"])

        # Escreve o cabeçalho das métricas
        writer.writerow(["Execução", "Média (µs)", "Mediana (µs)", "Desvio Padrão (µs)", "Mínimo (µs)", "Máximo (µs)"])

        # Escreve as métricas de cada execução
        for i, metrics in enumerate(all_metrics, start=1):
            writer.writerow([i] + [f"{value:.2f}" for value in metrics])

    print(f"Métricas salvas em: {filename}")


# Função principal para executar o cliente TCP
def tcp_client():
    config = {
        "protocol": "tcp",
        "print_output": PRINT_OUTPUT,
        "write_to_file": WRITE_TO_FILE,
        "use_session": USE_SESSION
    }

    all_metrics = []
    for i in range(10):  # Executa 10 vezes
        print(f"Executando {i + 1}/10...")
        times = run_requests()
        metrics = calculate_metrics(times)
        all_metrics.append(metrics)

        avg_time, median_time, std_dev_time, min_time, max_time = metrics
        print(f"Execução {i + 1}:")
        print(f"  Tempo médio: {avg_time:.2f} µs")
        print(f"  Mediana: {median_time:.2f} µs")
        print(f"  Desvio padrão: {std_dev_time:.2f} µs")
        print(f"  Tempo mínimo: {min_time:.2f} µs")
        print(f"  Tempo máximo: {max_time:.2f} µs")

    # Salva os resultados sempre
    filename = generate_output_filename(
        config["protocol"],
        config.get("use_session", False),
        config["print_output"],
        config["write_to_file"]
    )
    save_all_metrics_to_csv(all_metrics, config, filename)


if __name__ == "__main__":
    tcp_client()
