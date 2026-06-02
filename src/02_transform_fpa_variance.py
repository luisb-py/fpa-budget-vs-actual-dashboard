import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# configs

USUARIO = "postgres"
SENHA = "sua_senha"
HOST = "localhost"
PORTA = sua_porta
BANCO = "fpa_variance_project"

PASTA_SAIDA = Path(r"C:\Users\SEU_USUARIO\SUA_PASTA")
ARQUIVO_EXCEL = PASTA_SAIDA / "fpa_variance_clean.xlsx"

# conexao sql

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=USUARIO,
    password=SENHA,
    host=HOST,
    port=PORTA,
    database=BANCO,
)

engine = create_engine(connection_url)

# extrair do sqp

query = """
SELECT
    department,
    month,
    budget,
    actual,
    variance,
    variance_pct
FROM stg_fpa_variance;
"""

df = pd.read_sql_query(query, engine)

print("Dados extraídos do PostgreSQL:")
print(df.head())
print(df.info())

# tratamento de dados

df["department"] = df["department"].astype(str).str.strip()
df["month"] = df["month"].astype(str).str.strip()

numeric_cols = ["budget", "actual", "variance", "variance_pct"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Converte mês para data
df["month_date"] = pd.to_datetime(df["month"], errors="coerce")

df["year"] = df["month_date"].dt.year
df["month_number"] = df["month_date"].dt.month
df["month_name"] = df["month_date"].dt.month_name()

# Recalcula as variações para garantir consistência
df["variance_amount"] = df["actual"] - df["budget"]

df["variance_pct_calc"] = np.where(
    df["budget"] == 0,
    np.nan,
    df["variance_amount"] / df["budget"]
)

# Status Budget x Actual
df["budget_status"] = np.where(
    df["variance_amount"] > 0,
    "Over Budget",
    np.where(
        df["variance_amount"] < 0,
        "Under Budget",
        "On Budget"
    )
)

# Criticidade da variação
df["variance_level"] = np.where(
    df["variance_pct_calc"].abs() >= 0.20,
    "High Variance",
    np.where(
        df["variance_pct_calc"].abs() >= 0.10,
        "Medium Variance",
        "Low Variance"
    )
)

# Coluna para facilitar ordenação no Power BI/Excel
df["month_year"] = df["month_date"].dt.strftime("%Y-%m")

# Organiza tabela final
df_final = df[
    [
        "department",
        "month",
        "month_date",
        "month_year",
        "year",
        "month_number",
        "month_name",
        "budget",
        "actual",
        "variance_amount",
        "variance_pct_calc",
        "budget_status",
        "variance_level"
    ]
]

# Salvar tabela sql

df_final.to_sql(
    "fact_fpa_variance_clean",
    engine,
    if_exists="replace",
    index=False
)

# Exportar pro excel

PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

df_final.to_excel(
    ARQUIVO_EXCEL,
    index=False
)

print("\nProcesso finalizado com sucesso!")
print("Tabela criada no PostgreSQL: fact_fpa_variance_clean")
print(f"Arquivo Excel exportado em: {ARQUIVO_EXCEL}")