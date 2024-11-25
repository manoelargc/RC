import socket
from threading import Thread

# Configurações do servidor
HOST = '0.0.0.0'  # Aceita conexões de qualquer interface de rede
PORT = 587       # Porta do servidor


# TCP: Exige uma conexão contínua entre o cliente e o servidor. Quando um cliente se conecta, o servidor aceita essa conexão e trata as requisições até que a conexão seja encerrada

def handle_command(data):
    """
    Trata os comandos SMTP enviados pelo cliente e retorna a resposta apropriada.

    Args:
        data (bytes): O comando recebido do cliente em formato de bytes.

    Retorna:
        str: A resposta apropriada para o comando.

    Comandos implementados:
    - HELO: Responde com "250 Hello".
    - MAIL FROM: Responde com "250 OK".
    - RCPT TO: Responde com "250 OK".
    - QUIT: Responde com "221 Bye" e encerra a conexão.
    - Outros comandos: Responde com "500 Command not recognized".
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
        return "500 Command not recognized"

def handle_client(conn):
    """
    Lida com a comunicação com um cliente específico. Recebe e responde a comandos até a conexão ser encerrada.

    Args:
        conn (socket): O objeto socket representando a conexão com o cliente.

    Este loop contínuo:
    - Recebe um comando do cliente.
    - Envia a resposta apropriada.
    - Encerra a conexão quando não há mais dados recebidos.
    """
    while True:
        data = conn.recv(1024)
        if not data:
            break
        response = handle_command(data)
        conn.sendall(response.encode()) # aqui confiorma que o TCP garantirá a entrega
    conn.close()

def start_server():
    """
    Inicia o servidor TCP, escuta em HOST:PORT e cria uma nova thread para cada cliente conectado.

    - Cria um socket para escutar conexões TCP.
    - Para cada cliente que se conecta, cria uma nova thread que chama handle_client().
    
    
    O servidor TCP usa server_socket.accept() para aceitar uma conexão e conn.recv() para receber dados do cliente, indicando uma conexão persistente.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Servidor TCP escutando em {HOST}:{PORT}")
        while True:
            conn, addr = server_socket.accept()
            Thread(target=handle_client, args=(conn,)).start() #inicia uma nova thread

if __name__ == "__main__":
    start_server()
