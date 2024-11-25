# Usar uma imagem base Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o código do cliente para o container
COPY client_tcp.py /app/client_tcp.py

# Definir o comando que será executado no container
CMD ["python", "client_tcp.py"]
