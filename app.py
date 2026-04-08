import streamlit as st
import requests
from geopy.geocoders import Nominatim
from urllib.parse import quote

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Via Angel App", page_icon="🚚")

# 2. SISTEMA DE SEGURIDAD
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.title("🔐 Acceso Via Angel")
        password_input = st.text_input("Ingresa la clave", type="password")
        if st.button("Entrar"):
            if password_input == "fletesmi": 
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta")
        return False
    return True

if check_password():
    # --- BARRA LATERAL (Donde marcaste el círculo verde) ---
    with st.sidebar:
        st.header("Menú y Configuración")
        
        if st.button("Cerrar Sesión"):
            st.session_state["password_correct"] = False
            st.rerun()
        
        st.write("---")
        
        # AQUÍ ESTÁ LO QUE FALTABA:
        st.subheader("Gastos de Carretera")
        activar_peajes = st.checkbox("¿Ruta con Peajes?", value=False)
        
        monto_peaje = 0
        if activar_peajes:
            monto_peaje = st.number_input(
                "Monto de UN peaje ($):", 
                min_value=0, 
                step=100,
                help="La app calculará Ida y Vuelta automáticamente."
            )
            st.info("💡 Se sumará el doble al total final.")

    # --- INTERFAZ PRINCIPAL ---
    try:
        st.image("logoVA.jpeg", width=220)
    except:
        pass

    st.title("Calculadora de Fletes Inteligente")
    st.markdown("---")

    # Variables de Negocio (Ajustadas)
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    TARIFA_MINIMA = 15000
    VALOR_KM = 950
    VALOR_PESO_KG = 50
    PRECIO_BENCINA = 1600 
    RENDIMIENTO_N400 = 12 

    destino = st.text_input("📍 Destino de entrega:", placeholder="Ej: Quintero, Chile")
    peso = st.number_input("📦 Peso de la carga (kg):", min_value=0.0, step=1.0, value=10.0)

    def obtener_distancia(destino_texto):
        try:
            geolocator = Nominatim(user_agent="via_angel_pro_v2")
            location = geolocator.geocode(destino_texto + ", Chile")
            if location:
                url = f"http://router.project-osrm.org/route/v1/driving/-70.7937,-33.3930;{location.longitude},{location.latitude}?overview=false"
                r = requests.get(url).json()
                return round(r['routes'][0]['distance'] / 1000, 1)
            return None
        except:
            return None

    if st.button("CALCULAR AHORA"):
        if destino:
            with st.spinner('Calculando costos para ViAngel...'):
                km = obtener_distancia(destino)
            
            if km:
                # 1. Lógica de Peajes
                total_peajes = monto_peaje * 2 if activar_peajes else 0
                
                # 2. Lógica de Servicio
                neto_servicio = TARIFA_MINIMA + (km * VALOR_KM) + (peso * VALOR_PESO_KG)
                iva = neto_servicio * 0.19
                
                # 3. TOTAL FINAL
                total_final = neto_servicio + iva + total_peajes

                st.success(f"Distancia detectada: {km} km")
                
                # Resumen Estilo Tarjeta
                st.markdown(f"""
                ### 💰 Resumen de Cotización
                * **Valor Neto:** ${neto_servicio:,.0f}
                * **IVA (19%):** ${iva:,.0f}
                * **Peajes (I/V):** ${total_peajes:,.0f}
                * **Total a pagar:** **${total_final:,.0f}**
                
                ---
                **Dile al cliente:** 'El flete sale ${neto_servicio:,.0f} + IVA + ${total_peajes:,.0f} de peajes.'
                """)

                # --- NAVEGACIÓN (Botones Grandes abajo) ---
                st.write("---")
                st.subheader("🚀 Iniciar Navegación")
                dest_url = quote(f"{destino}, Chile")
                
                st.link_button("📍 Abrir en Google Maps", 
                               f"https://www.google.com/maps/dir/?api=1&origin={quote(DIRECCION_BASE)}&destination={dest_url}", 
                               use_container_width=True)
                
                st.link_button("🚙 Abrir en Waze", 
                               f"https://waze.com/ul?q={dest_url}&navigate=yes", 
                               use_container_width=True)
            else:
                st.error("No pude encontrar esa dirección. Intenta ser más específica.")
        else:
            st.warning("Por favor, ingresa un destino.")
