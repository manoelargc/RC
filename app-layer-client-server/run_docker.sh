#!/bin/bash

# cria o diretorio de resultados se nao existir
OUTPUT_DIR="./outputs"
mkdir -p $OUTPUT_DIR

# lista de configuracoes
CONFIGURATIONS=(
  "tcp true true false"
  "tcp true false true"
  "tcp true false false"
  "tcp false true false"
  "tcp false false true"
  "tcp false false false"
  "udp false true false"
  "udp false false true"
  "udp false false false"
)

# executa cada configuracao
for CONFIG in "${CONFIGURATIONS[@]}"; do
  read -r PROTOCOL USE_SESSION WRITE_TO_FILE PRINT_OUTPUT <<< "$CONFIG"
  
  for ((i=1; i<=10; i++)); do
    echo "executando configuracao: protocolo=$PROTOCOL, sessao=$USE_SESSION, escrever=$WRITE_TO_FILE, imprimir=$PRINT_OUTPUT (execucao $i/10)"
    docker-compose run \
      -e USE_SESSION=$USE_SESSION \
      -e WRITE_TO_FILE=$WRITE_TO_FILE \
      -e PRINT_OUTPUT=$PRINT_OUTPUT \
      client_$PROTOCOL
  done
done

echo "todas as configuracoes foram executadas. verifique os resultados no diretorio $OUTPUT_DIR"
