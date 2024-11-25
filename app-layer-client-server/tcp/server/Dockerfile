# Usar uma imagem base Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o código do servidor para o container
COPY server_tcp.py /app/server_tcp.py

# Expor a porta (escolhida como padrão para o servidor TCP)
EXPOSE 587

# Rodar o servidor TCP quando o container iniciar
CMD ["python", "server_tcp.py"]
