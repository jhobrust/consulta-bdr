import streamlit as st
import pandas as pd

ARQ = "Consulta_Executivos.xlsx"

def carregar_com_cabecalho(arquivo, aba, coluna_ancora="REGIONAL"):
    # Lê sem header para procurar onde está o cabeçalho verdadeiro
    bruto = pd.read_excel(arquivo, sheet_name=aba, header=None)

    # acha a linha onde aparece "REGIONAL"
    idx = None
    for i in range(len(bruto)):
        linha = bruto.iloc[i].astype(str).str.strip()
        if (linha == coluna_ancora).any():
            idx = i
            break

    if idx is None:
        raise ValueError(f'Não achei a coluna "{coluna_ancora}" na aba {aba}.')

    # Lê de novo usando a linha encontrada como header
    df = pd.read_excel(arquivo, sheet_name=aba, header=idx)

    # limpa nomes das colunas
    df.columns = [str(c).strip() for c in df.columns]
    return df

st.title("Consulta de Executivo - BDR")

df_exec = carregar_com_cabecalho(ARQ, "EXECUTIVOS", "REGIONAL")

# (opcional) mostrar colunas para debug
# st.write(df_exec.columns)

regiao = st.selectbox("Selecione a Regional", sorted(df_exec["REGIONAL"].dropna().unique()))
vertical = st.selectbox("Selecione a Vertical", sorted(df_exec["VERTICAL"].dropna().unique()))

resultado = df_exec[
    (df_exec["REGIONAL"] == regiao) &
    (df_exec["VERTICAL"] == vertical)
]

st.subheader("Executivo responsável")
st.dataframe(resultado)
