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
    {"protocol": "udp", "use_session": None, "write_to_file": True, "print_output": False},
    {"protocol": "udp", "use_session": None, "write_to_file": False, "print_output": True},
    {"protocol": "udp", "use_session": None, "write_to_file": False, "print_output": False},
]

# funcao que roda uma configuracao especifica
def run_configuration(protocol, use_session, write_to_file, print_output):
    print(f"Executando configuração: protocolo={protocol}, sessão={use_session}, escrever={write_to_file}, imprimir={print_output}")
    
    # define as variáveis de ambiente específicas para a execução
    env = os.environ.copy()
    env.update({
        "SERVER_HOST": "localhost",
        "USE_SESSION": str(use_session).lower() if use_session is not None else "false",
        "PRINT_OUTPUT": str(print_output).lower(),
        "WRITE_TO_FILE": str(write_to_file).lower(),
        "IS_DOCKER": "false",
        "OUTPUT_FILENAME": os.path.join(
            OUTPUT_DIR,
            f"{protocol}_results_{'session' if use_session else 'nosession'}_{'print' if print_output else 'noprint'}_{'write' if write_to_file else 'nowrite'}.csv"
        )
    })

    # monta os argumentos para rodar o cliente
    script_path = f"{protocol}/client/client_{protocol}.py"
    args = ["python3", script_path]

    # executa o cliente com as variáveis de ambiente configuradas
    subprocess.run(args, env=env)

if __name__ == "__main__":
    for config in CONFIGURATIONS:
        # executa cada configuração uma vez
        run_configuration(
            protocol=config["protocol"],
            use_session=config.get("use_session"),
            write_to_file=config["write_to_file"],
            print_output=config["print_output"]
        )
