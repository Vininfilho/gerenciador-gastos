import streamlit as st
import matplotlib.pyplot as plt
from supabase import create_client

# -------- CONFIG --------
st.set_page_config(page_title="Finance App", layout="centered")

# -------- SUPABASE --------
url = "https://zwmudbquylkilddwjabg.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3bXVkYnF1eWxraWxkZHdqYWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2Mzc2MzIsImV4cCI6MjA5NDIxMzYzMn0.5xIXAUBkFIG9n8env3dvi-odRuVs1GMaSM7wzdb5O0I"

supabase = create_client(url, key)


# =========================================================
# SESSION FIX (REAL PERSISTENCE)
# =========================================================
if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None


# 🔥 RESTAURA SESSÃO SEM DESLOGAR
if st.session_state.access_token and st.session_state.refresh_token:
    try:
        supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

        # garante usuário restaurado
        if st.session_state.user is None:
            st.session_state.user = supabase.auth.get_user().user

    except:
        st.session_state.user = None


if "edit_id" not in st.session_state:
    st.session_state.edit_id = None


# =========================================================
# LOGIN
# =========================================================
if st.session_state.user is None:
    st.markdown("""
        <h1 style='text-align:center;color:#6C2DC7;'>💜 Finance App</h1>
    """, unsafe_allow_html=True)

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)

    if col1.button("Entrar"):
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha
        })

        if res and res.user:

            st.session_state.user = res.user
            st.session_state.access_token = res.session.access_token
            st.session_state.refresh_token = res.session.refresh_token

            supabase.auth.set_session(
                res.session.access_token,
                res.session.refresh_token
            )

            st.rerun()

    if col2.button("Criar conta"):
        supabase.auth.sign_up({
            "email": email,
            "password": senha
        })
        st.success("Conta criada!")

    st.stop()


# =========================================================
# USER
# =========================================================
user = st.session_state.user
user_id = user.id


# =========================================================
# HEADER NUBANK STYLE (FIX VISIBILIDADE)
# =========================================================
st.markdown("""
<div style="
    background-color:#6C2DC7;
    padding:20px;
    border-radius:15px;
    color:white;
    text-align:center;
    font-size:24px;
    font-weight:bold;
">
💜 Meu Financeiro
</div>
""", unsafe_allow_html=True)


# =========================================================
# BUSCA
# =========================================================
try:
    res = supabase.table("gastos") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("id", desc=True) \
        .execute()

    gastos = res.data or []

except:
    gastos = []


total = sum(g["valor"] for g in gastos)


# =========================================================
# CARDS (FIX VISUAL)
# =========================================================
col1, col2 = st.columns(2)

col1.markdown(f"""
<div style="
    background:#F3F0FF;
    padding:15px;
    border-radius:12px;
    color:#000;
    box-shadow:0px 2px 6px rgba(0,0,0,0.1);
">
<h4 style="margin:0;">Total</h4>
<h2 style="margin:0;">R$ {total:.2f}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style="
    background:#F3F0FF;
    padding:15px;
    border-radius:12px;
    color:#000;
    box-shadow:0px 2px 6px rgba(0,0,0,0.1);
">
<h4 style="margin:0;">Transações</h4>
<h2 style="margin:0;">{len(gastos)}</h2>
</div>
""", unsafe_allow_html=True)


# =========================================================
# ADD GASTO
# =========================================================
st.markdown("### ➕ Nova transação")

with st.form("form_gasto", clear_on_submit=True):
    nome = st.text_input("Descrição")
    valor_str = st.text_input("Valor")
    categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Moradia", "Lazer", "Outros"])

    submitted = st.form_submit_button("Adicionar")

if submitted:
    try:
        valor = float(valor_str.replace(",", "."))
    except:
        valor = 0

    if nome and valor > 0:
        supabase.table("gastos").insert({
            "user_id": user_id,
            "nome": nome,
            "valor": valor,
            "categoria": categoria
        }).execute()

        st.rerun()


# =========================================================
# LISTA
# =========================================================
st.markdown("### 📋 Extrato")

for g in gastos:
    st.markdown(f"""
    <div style="
        background:#FAFAFA;
        padding:12px;
        border-radius:12px;
        margin-bottom:10px;
        border-left:5px solid #6C2DC7;
        color:#000;
    ">
    <b>{g['nome']}</b><br>
    <small>{g['categoria']}</small><br>
    <b>R$ {g['valor']:.2f}</b>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    if col1.button("🗑️ Deletar", key=f"del_{g['id']}"):
        supabase.table("gastos").delete().eq("id", g["id"]).execute()
        st.rerun()

    if col2.button("✏️ Editar", key=f"edit_{g['id']}"):
        st.session_state.edit_id = g["id"]


# =========================================================
# EDIT
# =========================================================
if st.session_state.edit_id:
    gasto = next((x for x in gastos if x["id"] == st.session_state.edit_id), None)

    if gasto:
        novo_nome = st.text_input("Descrição", gasto["nome"])
        novo_valor = st.text_input("Valor", str(gasto["valor"]))

        nova_categoria = st.selectbox(
            "Categoria",
            ["Alimentação", "Transporte", "Moradia", "Lazer", "Outros"],
            index=["Alimentação", "Transporte", "Moradia", "Lazer", "Outros"].index(gasto["categoria"])
        )

        if st.button("Salvar"):
            supabase.table("gastos").update({
                "nome": novo_nome,
                "valor": float(novo_valor.replace(",", ".")),
                "categoria": nova_categoria
            }).eq("id", gasto["id"]).execute()

            st.session_state.edit_id = None
            st.rerun()


# =========================================================
# GRÁFICO
# =========================================================
st.markdown("### 📊 Gastos por categoria")

if gastos:
    dados = {}

    for g in gastos:
        cat = g.get("categoria", "Outros")
        dados[cat] = dados.get(cat, 0) + g["valor"]

    fig, ax = plt.subplots()
    ax.pie(dados.values(), labels=dados.keys(), autopct='%1.1f%%')
    st.pyplot(fig)