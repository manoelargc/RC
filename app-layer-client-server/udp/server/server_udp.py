import socket

# Configurações do servidor
HOST = '0.0.0.0'  # Aceita conexões de qualquer interface de rede
PORT = 25       # Porta do servidor

def handle_command(data):
    """
    Processa comandos SMTP enviados pelo cliente e retorna a resposta apropriada.

    Args:
        data (bytes): O comando recebido do cliente em formato de bytes.

    Retorna:
        str: A resposta apropriada para o comando.

    Comandos implementados:
    - HELO: Responde com "250 Hello".
    - MAIL FROM: Responde com "250 OK".
    - RCPT TO: Responde com "250 OK".
    - QUIT: Responde com "221 Bye" e encerra a conexão.
    - Outros comandos: Responde com "500 Comando nao reconhecido".
    """
    command = data.decode().strip().upper()
    if command == "HELO":
        return "250 Hello"
    elif command.startswith("MAIL FROM"):
        return "250 OK"
    elif command.startswith("RCPT TO"):
        return "250 OK"
    elif command == "QUIT":
        return "221 Bye"
    else:
        return "500 Comando nao reconhecido"

def start_server():
    """
    Inicia o servidor UDP, escutando por mensagens de clientes e respondendo com a resposta apropriada.

    - Cria um socket para escutar conexões UDP.
    - Recebe mensagens de clientes e utiliza handle_command() para processar e enviar uma resposta.

    O servidor é executado continuamente, escutando em HOST:PORT e respondendo a cada comando recebido.
    
    
    No servidor UDP, o comando recvfrom() recebe a mensagem e o endereço do cliente diretamente, e o servidor responde com sendto() sem precisar abrir ou fechar uma conexão.
    o código executa recvfrom() e sendto() no mesmo loop, sem criar threads, já que cada datagrama é independente.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))
        print(f"Servidor UDP escutando em {HOST}:{PORT}")
        
        while True:
            # Recebe uma mensagem do cliente e responde com o comando apropriado
            data, addr = server_socket.recvfrom(1024)
            response = handle_command(data)
            server_socket.sendto(response.encode(), addr) # envia o datagrama, mas o servidor não sabe se o cliente o recebeu

if __name__ == "__main__":
    start_server()
