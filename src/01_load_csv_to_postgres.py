import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

file_path = Path(r"C:\Users\SEU_USUARIO\SUA_PASTA\fpa_variance_data_monthly.csv")

if not file_path.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

df = pd.read_csv(file_path)

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
    .str.replace("/", "_")
)

print(df.head())
print(df.info())
print(df.columns)

usuario = "postgres"
senha = "sua_senha"
host = "localhost"
porta = "sua_porta"
banco = "fpa_variance_project"

engine = create_engine(
    f"postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco}"
)

df.to_sql(
    "stg_fpa_variance",
    engine,
    if_exists="replace",
    index=False
)

print("Tabela carregada com sucesso no PostgreSQL.")