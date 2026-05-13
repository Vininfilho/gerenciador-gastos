import streamlit as st
import matplotlib.pyplot as plt
from supabase import create_client

# -------- CONFIG --------
st.set_page_config(page_title="Gerenciador PRO", layout="centered")

# -------- SUPABASE --------
url = "https://zwmudbquylkilddwjabg.supabase.co"
key = "sb_publishable_pWPdvTuV05pSo2RF4tCDGQ_qwp_10cz"
supabase = create_client(url, key)

# -------- SESSION --------
if "user" not in st.session_state:
    st.session_state.user = None

# -------- LOGIN --------
if not st.session_state.user:
    st.title("🔐 Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)

    if col1.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": senha
            })
            st.session_state.user = res.user
            st.success("Login realizado!")
            st.rerun()
        except Exception as e:
            st.error("Login inválido")

    if col2.button("Criar conta"):
        try:
            supabase.auth.sign_up({
                "email": email,
                "password": senha
            })
            st.success("Conta criada! Faça login.")
        except:
            st.error("Erro ao criar conta")

    st.stop()

user_id = st.session_state.user.id

# -------- HEADER --------
col1, col2 = st.columns([3,1])
col1.title("💸 Gerenciador PRO")

if col2.button("Sair"):
    st.session_state.user = None
    st.rerun()

# -------- CATEGORIAS --------
categorias = [
    "Alimentação", "Transporte", "Moradia",
    "Lazer", "Compras", "Saúde", "Outros"
]

# -------- FORM --------
with st.form("form_gasto", clear_on_submit=True):
    nome = st.text_input("Nome do gasto")
    valor_str = st.text_input("Valor (ex: 12.50)")
    categoria = st.selectbox("Categoria", categorias)

    submitted = st.form_submit_button("Adicionar")

# -------- ADICIONAR --------
if submitted:
    try:
        valor = float(valor_str.replace(",", "."))
    except:
        valor = 0

    if not nome.strip():
        st.error("Preencha o nome!")
    elif valor <= 0:
        st.error("Valor inválido!")
    else:
        try:
            supabase.table("gastos").insert({
                "user_id": user_id,
                "nome": nome,  # ✅ corrigido
                "valor": valor,
                "categoria": categoria
            }).execute()

            st.success("Gasto adicionado!")
            st.rerun()
        except Exception as e:
            st.error("Erro ao salvar no banco")

# -------- BUSCAR --------
try:
    res = supabase.table("gastos") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("id", desc=True) \
        .execute()

    gastos = res.data if res.data else []
except:
    gastos = []
    st.error("Erro ao buscar dados")

# -------- LISTA --------
st.subheader("📋 Seus Gastos")

for g in gastos:
    col1, col2, col3, col4 = st.columns([3,2,2,2])

    col1.write(g["nome"])
    col2.write(g["categoria"])
    col3.write(f"R${g['valor']:.2f}")

    # EDITAR
    if col4.button("✏️", key=f"edit_{g['id']}"):
        st.session_state.edit_id = g["id"]

    # REMOVER
    if col4.button("❌", key=f"del_{g['id']}"):
        supabase.table("gastos").delete().eq("id", g["id"]).execute()
        st.rerun()

# -------- EDITAR --------
if "edit_id" in st.session_state:
    st.subheader("✏️ Editar gasto")

    gasto = next((g for g in gastos if g["id"] == st.session_state.edit_id), None)

    if gasto:
        novo_nome = st.text_input("Nome", gasto["nome"])
        novo_valor = st.text_input("Valor", str(gasto["valor"]))
        nova_categoria = st.selectbox(
            "Categoria",
            categorias,
            index=categorias.index(gasto["categoria"])
        )

        if st.button("Salvar edição"):
            try:
                valor_convertido = float(novo_valor.replace(",", "."))
            except:
                valor_convertido = 0

            supabase.table("gastos").update({
                "nome": novo_nome,
                "valor": valor_convertido,
                "categoria": nova_categoria
            }).eq("id", gasto["id"]).execute()

            del st.session_state.edit_id
            st.success("Atualizado!")
            st.rerun()

# -------- TOTAL --------
total = sum(g["valor"] for g in gastos)
st.markdown(f"## 💰 Total: R${total:.2f}")

# -------- GRÁFICO --------
st.subheader("📊 Gastos por Categoria")

if gastos:
    categorias_dict = {}

    for g in gastos:
        categorias_dict[g["categoria"]] = categorias_dict.get(g["categoria"], 0) + g["valor"]

    fig, ax = plt.subplots()
    ax.pie(
        categorias_dict.values(),
        labels=categorias_dict.keys(),
        autopct='%1.1f%%'
    )
    ax.set_title("Distribuição de gastos")

    st.pyplot(fig)
else:
    st.info("Sem dados ainda.")