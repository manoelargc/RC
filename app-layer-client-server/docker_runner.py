import os
import subprocess

# Diretório para salvar os resultados
OUTPUT_DIR = "./outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Lista de configurações para testar
CONFIGURATIONS = [
    {"protocol": "tcp", "use_session": True, "write_to_file": True, "print_output": False},
    {"protocol": "tcp", "use_session": True, "write_to_file": False, "print_output": True},
    {"protocol": "tcp", "use_session": True, "write_to_file": False, "print_output": False},
    {"protocol": "tcp", "use_session": False, "write_to_file": True, "print_output": False},
    {"protocol": "tcp", "use_session": False, "write_to_file": False, "print_output": True},
    {"protocol": "tcp", "use_session": False, "write_to_file": False, "print_output": False},
    {"protocol": "udp", "write_to_file": True, "print_output": False},
    {"protocol": "udp", "write_to_file": False, "print_output": True},
    {"protocol": "udp", "write_to_file": False, "print_output": False},
]

# Função que executa uma configuração no Docker
def run_docker_configuration(protocol, use_session, write_to_file, print_output):
    """
    Executa uma configuração específica no Docker.
    """
    print(f"Executando configuração: protocolo={protocol}, sessão={use_session}, escrever={write_to_file}, imprimir={print_output}")
    
    # Define as variáveis de ambiente para o contêiner
    output_filename = f"{protocol}_results_" \
                      f"{'session' if protocol == 'tcp' and use_session else 'nosession'}_" \
                      f"{'print' if print_output else 'noprint'}_" \
                      f"{'write' if write_to_file else 'nowrite'}.csv"

    env = os.environ.copy()
    env.update({
        "SERVER_HOST": "localhost",
        "USE_SESSION": str(use_session).lower() if protocol == "tcp" else "false",
        "PRINT_OUTPUT": str(print_output).lower(),
        "WRITE_TO_FILE": str(write_to_file).lower(),
        "IS_DOCKER": "true",
        "OUTPUT_FILENAME": output_filename,
    })

    # Monta o comando para executar o cliente
    service_name = f"client_{protocol}"  # Nome do serviço no docker-compose.yml
    cmd = ["docker-compose", "run", "--rm", service_name]

    # Executa o cliente dentro do contêiner
    subprocess.run(cmd, env=env)

if __name__ == "__main__":
    # Itera sobre as configurações
    for config in CONFIGURATIONS:
        run_docker_configuration(
            protocol=config["protocol"],
            use_session=config.get("use_session", False),
            write_to_file=config["write_to_file"],
            print_output=config["print_output"]
        )
