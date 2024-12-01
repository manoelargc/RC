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

# funcao que roda uma configuracao especifica
def run_configuration(protocol, use_session, write_to_file, print_output, num_executions=10):
    for execution in range(1, num_executions + 1):
        print(f"executando configuracao: protocolo={protocol}, sessao={use_session}, escrever={write_to_file}, imprimir={print_output} (execucao {execution}/10)")
        
        # define o nome do arquivo de saída baseado na configuração
        output_file = os.path.join(OUTPUT_DIR, f"{protocol}_results_{'session' if use_session else 'nosession'}_{'print' if print_output else 'noprint'}.csv")
        
        # monta os argumentos para rodar o cliente
        args = [
            "python3",
            f"client_{protocol}.py",
            "--use_session", str(use_session).lower(),
            "--write_to_file", str(write_to_file).lower(),
            "--print_output", str(print_output).lower(),
            "--output_file", output_file,
        ]
        
        # executa o cliente
        subprocess.run(args)

if __name__ == "__main__":
    for config in CONFIGURATIONS:
        run_configuration(
            protocol=config["protocol"],
            use_session=config.get("use_session", False),
            write_to_file=config["write_to_file"],
            print_output=config["print_output"]
        )
