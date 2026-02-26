import streamlit as st

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Via Angel - Acceso Privado", page_icon="🚚")

# --- LA CONTRASEÑA (Aquí la puedes cambiar tú misma) ---
CLAVE_REAL = "fletesmi"

# --- LÓGICA DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("🔐 Acceso Restringido - Via Angel")
    password_input = st.text_input("Ingrese la clave para cotizar:", type="password")
    
    if st.button("Entrar"):
        if password_input == CLAVE_REAL:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("❌ Clave incorrecta. Inténtelo de nuevo.")
    st.stop() # Detiene el resto de la app si no está autenticado

# --- TODO LO QUE SIGUE SOLO SE VE SI LA CLAVE ES CORRECTA ---

# Intentar mostrar el Logo
try:
    st.image("Logotipo profesional.png", width=300)
except:
    st.info("Logística Via Angel")

st.title("Calculadora Corporativa de Fletes")
st.write("Bienvenida Cecilia. Sistema listo para cotizar.")

# Entradas para la fórmula
km = st.number_input("Kilómetros totales:", min_value=0.0, step=1.0)
kg = st.number_input("Peso de la carga (KG):", min_value=0.0, step=1.0)

if st.button("CALCULAR TOTAL"):
    # Tu fórmula exacta:
    subtotal = 15000 + (km * 950) + (kg * 50)
    total_con_iva = subtotal * 1.19
    
    st.success(f"### Total a cobrar: ${total_con_iva:,.0f} CLP")
    
    st.markdown(f"""
    **Desglose del cobro:**
    * Cargo Base: $15.000
    * Distancia ({km} km): ${km * 950:,.0f}
    * Peso ({kg} kg): ${kg * 50:,.0f}
    * **Impuestos:** IVA 19% incluido
    """)

st.write("---")
if st.button("Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()
