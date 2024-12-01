#!/bin/bash

# Define as configurações a serem testadas
CONFIGURATIONS=(
    "tcp true true false"
    "tcp true false true"
    "tcp true false false"
    "tcp false true false"
    "tcp false false true"
    "tcp false false false"
    "udp true false false"
    "udp false true true"
    "udp false false false"
)

# Diretório de saída
OUTPUT_DIR="./outputs"
mkdir -p $OUTPUT_DIR

# Itera sobre cada configuração
for config in "${CONFIGURATIONS[@]}"; do
    IFS=' ' read -r protocol use_session write_to_file print_output <<< "$config"

    # Define as variáveis de ambiente
    export USE_SESSION=$use_session
    export PRINT_OUTPUT=$print_output
    export WRITE_TO_FILE=$write_to_file
    export OUTPUT_FILENAME="${protocol}_results_${use_session}_${print_output}_${write_to_file}.csv"

    echo "Executando configuração: protocolo=$protocol, sessão=$use_session, escrever=$write_to_file, imprimir=$print_output"
    
    # Executa o cliente correspondente
    docker-compose run --rm client_$protocol
done
