import streamlit as st
import matplotlib.pyplot as plt

# -------- CONFIG --------
st.set_page_config(page_title="Gerenciador PRO", layout="centered")

# -------- ESTADO --------
if "gastos" not in st.session_state:
    st.session_state.gastos = []

# -------- CATEGORIAS --------
categorias = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Lazer",
    "Compras",
    "Saúde",
    "Outros"
]

# -------- TÍTULO --------
st.title("💸 Gerenciador de Gastos PRO")

# -------- FORMULÁRIO --------
with st.form("form_gasto"):
    nome = st.text_input("Nome do gasto")
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    categoria = st.selectbox("Categoria", categorias)

    submitted = st.form_submit_button("Adicionar / Atualizar")

# -------- LÓGICA ADD --------
if submitted:
    if not nome.strip():
        st.error("Preencha o nome!")
    elif valor <= 0:
        st.error("Valor deve ser positivo!")
    else:
        st.session_state.gastos.append({
            "nome": nome,
            "valor": valor,
            "categoria": categoria
        })
        st.success("Gasto adicionado!")

# -------- LISTA --------
st.subheader("📋 Lista de Gastos")

if st.session_state.gastos:
    for i, g in enumerate(st.session_state.gastos):
        col1, col2, col3, col4 = st.columns([3,2,2,2])

        col1.write(g["nome"])
        col2.write(g["categoria"])
        col3.write(f"R${g['valor']:.2f}")

        # BOTÃO EDITAR
        if col4.button("Editar", key=f"edit_{i}"):
            st.session_state.edit_index = i

        # BOTÃO REMOVER
        if col4.button("❌", key=f"del_{i}"):
            st.session_state.gastos.pop(i)
            st.rerun()

# -------- EDITAR --------
if "edit_index" in st.session_state:
    st.subheader("✏️ Editando gasto")

    idx = st.session_state.edit_index
    gasto = st.session_state.gastos[idx]

    novo_nome = st.text_input("Nome", gasto["nome"], key="edit_nome")
    novo_valor = st.number_input("Valor", value=gasto["valor"], key="edit_valor")
    nova_categoria = st.selectbox("Categoria", categorias, index=categorias.index(gasto["categoria"]), key="edit_cat")

    if st.button("Salvar edição"):
        st.session_state.gastos[idx] = {
            "nome": novo_nome,
            "valor": novo_valor,
            "categoria": nova_categoria
        }
        del st.session_state.edit_index
        st.success("Atualizado!")
        st.rerun()

# -------- TOTAL --------
total = sum(g["valor"] for g in st.session_state.gastos)
st.markdown(f"## 💰 Total: R${total:.2f}")

# -------- GRÁFICO --------
st.subheader("📊 Gráfico por Categoria")

if st.session_state.gastos:
    categorias_dict = {}

    for g in st.session_state.gastos:
        categorias_dict[g["categoria"]] = categorias_dict.get(g["categoria"], 0) + g["valor"]

    fig, ax = plt.subplots()
    ax.pie(categorias_dict.values(), labels=categorias_dict.keys(), autopct='%1.1f%%')
    ax.set_title("Gastos por Categoria")

    st.pyplot(fig)
else:
    st.info("Sem dados para exibir gráfico.")