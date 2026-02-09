import streamlit as st
import pandas as pd

ARQ = "Consulta_Executivos.xlsx"

st.set_page_config(page_title="Consulta de Executivo - BDR", layout="wide")

# --- CSS leve pra ficar bonito e evitar “quebra” ---
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; max-width: 1200px; }
.card {
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 18px;
  padding: 18px;
  background: rgba(255,255,255,0.05);
}
.small { opacity: 0.85; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

def carregar_com_cabecalho(arquivo, aba, coluna_ancora):
    bruto = pd.read_excel(arquivo, sheet_name=aba, header=None)

    idx = None
    for i in range(len(bruto)):
        linha = bruto.iloc[i].astype(str).str.strip()
        if (linha == coluna_ancora).any():
            idx = i
            break

    if idx is None:
        raise ValueError(f'Não achei a coluna "{coluna_ancora}" na aba {aba}.')

    df = pd.read_excel(arquivo, sheet_name=aba, header=idx)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def norm_txt(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    return s if s else None

# ---------------------------
# Carregamento dos dados
# ---------------------------
st.title("Consulta de Executivo - BDR")
st.caption("Escolha os filtros e o app indica o executivo mais adequado para agendar a reunião.")

with st.spinner("Carregando base..."):
    df_exec = carregar_com_cabecalho(ARQ, "EXECUTIVOS", "REGIONAL")
    df_icp  = carregar_com_cabecalho(ARQ, "ICP", "Segmento")

# Normaliza textos principais
for c in ["REGIONAL", "VERTICAL", "ICP", "GERENTE DE VENDAS", "EXECUTIVO DE CONTA", "PERFIL"]:
    if c in df_exec.columns:
        df_exec[c] = df_exec[c].map(norm_txt)

for c in ["Segmento", "TM (MRR)", "TM (ARR)", "ICP – Critérios"]:
    if c in df_icp.columns:
        df_icp[c] = df_icp[c].map(norm_txt)

# ---------------------------
# Fluxo do treinamento:
# 1) Região -> 2) Vertical (legenda) -> 3) ICP -> Executivos
# ---------------------------

# 1) Região
regioes = sorted(df_exec["REGIONAL"].dropna().unique().tolist())
regiao = st.selectbox("1) Selecione a Regional", regioes)

df_r = df_exec[df_exec["REGIONAL"] == regiao]

# 2) Vertical
verticais = sorted(df_r["VERTICAL"].dropna().unique().tolist())
vertical = st.selectbox("2) Selecione a Vertical", verticais)

# Legenda / enquadramento baseado na aba ICP (Segmento == Vertical)
df_icp_seg = df_icp[df_icp["Segmento"] == vertical]

with st.expander("📌 Legenda / Enquadramento (baseado no ICP)", expanded=True):
    if df_icp_seg.empty:
        st.warning("Não encontrei critérios na aba ICP para essa Vertical (Segmento).")
    else:
        crit = df_icp_seg.iloc[0].get("ICP – Critérios", None)
        mrr  = df_icp_seg.iloc[0].get("TM (MRR)", None)
        arr  = df_icp_seg.iloc[0].get("TM (ARR)", None)

        if crit:
            st.markdown(f"**Critérios:** {crit}")
        if mrr or arr:
            st.markdown(f"**Ticket médio (ref.):** MRR: {mrr or '—'} | ARR: {arr or '—'}")

df_v = df_r[df_r["VERTICAL"] == vertical]

# 3) ICP
icps_validos = sorted(df_v["ICP"].dropna().unique().tolist())
icp = st.selectbox("3) Selecione o ICP (porte/tipo da empresa)", icps_validos)

resultado = df_v[df_v["ICP"] == icp]

st.subheader("Executivos disponíveis")

if resultado.empty:
    st.warning("Nenhum executivo encontrado para esses filtros.")
else:
    cols_show = [c for c in ["EXECUTIVO DE CONTA", "GERENTE DE VENDAS", "PERFIL"] if c in resultado.columns]
    st.dataframe(resultado[cols_show], use_container_width=True)

    # Se tiver mais de um executivo, deixa escolher
    if len(resultado) > 1:
        escolha = st.selectbox(
            "Selecione o executivo para agendar",
            resultado["EXECUTIVO DE CONTA"].fillna("—").unique().tolist()
        )
        row = resultado[resultado["EXECUTIVO DE CONTA"] == escolha].iloc[0]
    else:
        row = resultado.iloc[0]

    st.markdown("### Resultado final")
    st.write(f"**Executivo:** {row.get('EXECUTIVO DE CONTA','—')}")
    st.write(f"**Gerente:** {row.get('GERENTE DE VENDAS','—')}")
    st.write(f"**Perfil:** {row.get('PERFIL','—')}")

    st.caption("Texto rápido pra colar no agendamento")
    st.code(
        f"Reunião com {row.get('EXECUTIVO DE CONTA','—')} "
        f"(Regional: {regiao} | Vertical: {vertical} | ICP: {icp}).",
        language="text"
    )
