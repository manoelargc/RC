# Usar uma imagem base Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o código do servidor para o container
COPY server_udp.py /app/server_udp.py

# Expor a porta (escolhida como padrão para o servidor UDP)
EXPOSE 25

# Rodar o servidor UDP quando o container iniciar
CMD ["python", "server_udp.py"]
