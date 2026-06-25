import streamlit as st
import requests
from geopy.geocoders import Nominatim
from urllib.parse import quote

# 1. CONFIGURACIÓN DE LA APP (Optimizada para celular)
st.set_page_config(page_title="Via Angel App", page_icon="🚚", layout="centered")

# Estilos CSS sutiles para mejorar la tipografía y los botones en móviles
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. SISTEMA DE SEGURIDAD
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        st.title("🔐 Acceso Via Angel")
        password_input = st.text_input("Ingresa la clave para entrar", type="password")
        if st.button("Entrar"):
            if password_input == "fletesmi":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta")
        return False
    return True

if check_password():
    # --- BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        st.header("Menú ViAngel")
        if st.button("Cerrar Sesión"):
            st.session_state["password_correct"] = False
            st.rerun()
        st.write("---")
        
        st.subheader("⚙️ Configuración de Peajes")
        activar_peajes = st.checkbox("¿Ruta con Peajes?", value=False)
        monto_peaje = 0
        if activar_peajes:
            monto_peaje = st.number_input(
                "Valor de 1 Peaje ($):", min_value=0, step=100, value=0
            )
            st.info(f"💡 Se cobrará Ida y Vuelta (${monto_peaje * 2:,.0f})")

    # --- CUERPO PRINCIPAL ---
    # Fila superior de marca: Logo a la izquierda y Título alineado
    col_logo, col_title = st.columns([1, 2])
    with col_logo:
        try:
            st.image("logoVA.jpeg", width=110)
        except:
            pass
    with col_title:
        st.subheader("ViAngel Logistics")
        st.caption("Panel de Control e Internet Móvil")

    st.markdown("## 📊 Calculadora de Fletes Inteligente")
    
    # VARIABLES DE NEGOCIO (Valores fijos)
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    TARIFA_MINIMA = 20000
    VALOR_KM = 1000
    VALOR_PESO_KG = 100
    PRECIO_BENCINA = 1600 
    RENDIMIENTO_N400 = 12 

    # Contenedor visual para el formulario (Tipo Tarjeta)
    with st.container(border=True):
        st.markdown("**Datos del Servicio**")
        destino = st.text_input("📍 Destino de entrega:", placeholder="Ej: Quintero, Chile")
        peso = st.number_input("📦 Peso de la carga (kg):", min_value=0.0, step=1.0, value=10.0)

    # Función de cálculo de distancia (OSRM)
    def obtener_distancia(destino_texto):
        try:
            geolocator = Nominatim(user_agent="via_angel_final_v1")
            location = geolocator.geocode(destino_texto + ", Chile")
            if location:
                url = f"http://router.project-osrm.org/route/v1/driving/-70.7937,-33.3930;{location.longitude},{location.latitude}?overview=false"
                r = requests.get(url).json()
                return round(r['routes'][0]['distance'] / 1000, 1)
            return None
        except:
            return None

    # BOTÓN DE CÁLCULO GENERAL
    if st.button("🚀 CALCULAR AHORA", type="primary"):
        if destino:
            with st.spinner('Procesando ruta satelital...'):
                km = obtener_distancia(destino)
                if km:
                    # Cálculos Matemáticos Internos
                    total_peajes = monto_peaje * 2 if activar_peajes else 0
                    neto_servicio = TARIFA_MINIMA + (km * VALOR_KM) + (peso * VALOR_PESO_KG)
                    iva = neto_servicio * 0.19
                    costo_bencina = ((km * 2) / RENDIMIENTO_N400) * PRECIO_BENCINA
                    total_final = neto_servicio + iva + total_peajes
                    ganancia_real = total_final - costo_bencina - total_peajes

                    st.toast("¡Ruta trazada con éxito!", icon="✅")
                    
                    # --- PANEL DE RESULTADOS ---
                    st.markdown("### 📋 Resultados de la Operación")
                    
                    # Tarjeta destacada con el cobro total para decírselo rápido al cliente
                    with st.container(border=True):
                        st.markdown(f"<h3 style='text-align: center; margin:0;'>Cobro Total: <span style='color:#2563eb;'>${total_final:,.0f}</span></h3>", unsafe_allow_html=True)
                        st.caption(f"<p style='text-align: center; margin:0;'>Distancia de viaje: {km} km (Solo ida)</p>", unsafe_allow_html=True)

                    # Desglose en métricas ordenadas
                    st.markdown("**Control Interno y Costos:**")
                    c1, c2 = st.columns(2)
                    c1.metric("⛽ Combustible (Gasto)", f"${costo_bencina:,.0f}")
                    c2.metric("📈 Ganancia Real Limpia", f"${ganancia_real:,.0f}")

                    # Bloque de resumen estructurado
                    with st.expander("🔍 Ver Desglose Detallado del Neto e IVA", expanded=True):
                        st.markdown(f"""
                        *   **Valor Neto del Viaje:** ${neto_servicio:,.0f}
                        *   **IVA Requerido (19%):** ${iva:,.0f}
                        *   **Fondo para Peajes:** ${total_peajes:,.0f}
                        """)
                        
                    # Cuadro de diálogo comercial para copiar y pegar o leer directamente
                    st.info(f"🗣️ **Texto para el cliente:**\n\n\"El servicio es de ${neto_servicio:,.0f} + IVA. Adicionalmente se consideran ${total_peajes:,.0f} de peajes por ida y vuelta.\"")

                    # --- NAVEGACIÓN DIRECTA ---
                    st.markdown("### 🗺️ Iniciar Ruta en Terreno")
                    dest_url = quote(f"{destino}, Chile")
                    origin_url = quote(DIRECCION_BASE)
                    
                    col_maps, col_waze = st.columns(2)
                    with col_maps:
                        st.link_button("🗺️ Abrir Google Maps", f"https://www.google.com/maps/dir/?api=1&origin={origin_url}&destination={dest_url}", use_container_width=True)
                    with col_waze:
                        st.link_button("🚙 Abrir en Waze", f"https://waze.com/ul?q={dest_url}&navigate=yes", use_container_width=True)

                    # Mostrar furgón decorativo al final para dar el cierre premium
                    st.markdown("---")
                    try:
                        st.image("furgon.png", use_container_width=True, caption="Flota ViAngel Chevrolet N400")
                    except:
                        pass
                else:
                    st.error("❌ No se encontró la dirección geográfica. Intenta escribirla más detallada.")
        else:
            st.warning("⚠️ Por favor, ingresa una dirección de destino primero.")
