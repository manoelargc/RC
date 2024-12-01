import os
import subprocess

# define o diretorio para salvar os resultados
OUTPUT_DIR = "./outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# lista com as configuracoes que serao testadas
CONFIGURATIONS = [
    {"protocol": "tcp", "use_session": True, "write_to_file": True, "print_output": False},
    {"protocol": "tcp", "use_session": True, "write_to_file": False, "print_output": True},
    {"protocol": "tcp", "use_session": True, "write_to_file": False, "print_output": False},
    {"protocol": "tcp", "use_session": False, "write_to_file": True, "print_output": False},
    {"protocol": "tcp", "use_session": False, "write_to_file": False, "print_output": True},
    {"protocol": "tcp", "use_session": False, "write_to_file": False, "print_output": False},
    {"protocol": "udp", "use_session": False, "write_to_file": True, "print_output": False},
    {"protocol": "udp", "use_session": False, "write_to_file": False, "print_output": True},
    {"protocol": "udp", "use_session": False, "write_to_file": False, "print_output": False},
]

# funcao que roda uma configuracao especifica no docker
def run_configuration(protocol, use_session, write_to_file, print_output, num_executions=10):
    for execution in range(1, num_executions + 1):
        print(f"executando configuracao no docker: {protocol}, sessao: {use_session}, escrever: {write_to_file}, imprimir: {print_output} (execucao {execution}/10)")
        args = [
            "docker-compose",
            "run",
            f"client_{protocol}",  # define o servico do cliente
            "--use_session", str(use_session),  # passa se usa sessao
            "--write_to_file", str(write_to_file),  # passa se escreve no arquivo
            "--print_output", str(print_output)  # passa se imprime no terminal
        ]
        subprocess.run(args)  # executa o comando para rodar no docker

if __name__ == "__main__":
    for config in CONFIGURATIONS:
        # roda cada configuracao da lista
        run_configuration(
            protocol=config["protocol"],
            use_session=config["use_session"],
            write_to_file=config["write_to_file"],
            print_output=config["print_output"]
        )
