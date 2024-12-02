import os
import pandas as pd

# Caminhos para as pastas
docker_folder = 'outputs/docker'
local_folder = 'outputs/local'

# Listar todos os arquivos CSV nas pastas
docker_files = [os.path.join(docker_folder, f) for f in os.listdir(docker_folder) if f.endswith('.csv')]
local_files = [os.path.join(local_folder, f) for f in os.listdir(local_folder) if f.endswith('.csv')]

# Carregar todos os arquivos CSV em um único DataFrame, tratando corretamente o cabeçalho
docker_df = pd.concat([pd.read_csv(file, header=1) for file in docker_files], ignore_index=True)
local_df = pd.concat([pd.read_csv(file, header=1) for file in local_files], ignore_index=True)

# Adicionar uma coluna para identificar de qual pasta os dados vêm (docker ou local)
docker_df['source'] = 'docker'
local_df['source'] = 'local'

# Combinar os dois DataFrames
df = pd.concat([docker_df, local_df], ignore_index=True)

# Exibir as primeiras linhas para verificar a estrutura
print(df.head())
