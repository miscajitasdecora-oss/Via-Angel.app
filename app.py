import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Via Angel - Privado", page_icon="🚚")

# --- SISTEMA DE CONTRASEÑA ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Contraseña de Acceso", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Contraseña de Acceso", type="password", on_change=password_entered, key="password")
        st.error("❌ Contraseña incorrecta")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- LOGO Y CALCULADORA ---
try:
    st.image("Logotipo profesional.png", width=280)
except:
    st.info("Sube el logo a GitHub para que aparezca aquí.")

st.title("Gestión de Fletes Via Angel")

distancia = st.number_input("Kilómetros del viaje:", min_value=0.0, step=0.1)
peso_carga = st.number_input("Peso de la carga (kg):", min_value=0.0, step=1.0)

if st.button("CALCULAR COBRO"):
    # Tu fórmula de siempre
    neto = 15000 + (distancia * 950) + (peso_carga * 50)
    total_final = neto * 1.19
    
    st.success(f"### Total a cobrar: ${total_final:,.0f} CLP")
    st.write(f"*(Incluye IVA y recargos)*")
