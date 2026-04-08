import streamlit as st
import requests
from geopy.geocoders import Nominatim
from urllib.parse import quote

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Via Angel App", page_icon="🚚")

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
    # --- BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        st.header("Menú Principal")
        
        # Botón de cerrar sesión primero
        if st.button("Cerrar Sesión"):
            st.session_state["password_correct"] = False
            st.rerun()
        
        st.write("---")
        
        # AQUÍ APARECERÁ EN EL CÍRCULO VERDE QUE MARCASTE
        st.subheader("Configuración de Peajes")
        peaje_unitario = st.number_input(
            "Valor Peaje Unitario ($):", 
            min_value=0, 
            step=100, 
            value=0, 
            help="Se multiplicará por 2 (ida y vuelta)"
        )
        st.info("💡 Este valor se sumará al total como reembolso.")

    # --- INTERFAZ PRINCIPAL ---
    try:
        st.image("logoVA.jpeg", width=220)
    except:
        pass

    st.title("Calculadora de Fletes Inteligente")
    st.markdown("---")

    # Variables de cobro
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    TARIFA_MINIMA = 15000
    VALOR_KM = 950
    VALOR_PESO_KG = 50
    PRECIO_BENCINA = 1600 
    RENDIMIENTO_N400 = 12 

    destino = st.text_input("📍 Destino de entrega:", placeholder="Ej: San Diego 100, Santiago")
    peso = st.number_input("📦 Peso de la carga (kg):", min_value=0.0, step=1.0)

    def obtener_distancia(destino_texto):
        try:
            geolocator = Nominatim(user_agent="via_angel_pro")
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
            with st.spinner('Calculando...'):
                km = obtener_distancia(destino)
            
            if km:
                total_peajes = peaje_unitario * 2
                neto_servicio = TARIFA_MINIMA + (km * VALOR_KM) + (peso * VALOR_PESO_KG)
                iva = neto_servicio * 0.19
                total_final = neto_servicio + iva + total_peajes

                st.success(f"Distancia: {km} km")
                
                # Resumen
                st.markdown(f"""
                ### 💰 Resumen de Cotización
                * **Valor Neto:** ${neto_servicio:,.0f}
                * **IVA (19%):** ${iva:,.0f}
                * **Peajes (I/V):** ${total_peajes:,.0f}
                * **Total Final:** **${total_final:,.0f}**
                """)

                # --- SECCIÓN DE NAVEGACIÓN (LOS BOTONES GRANDES ABAJO) ---
                st.write("---")
                st.subheader("🚀 Iniciar Navegación")
                dest_url = quote(f"{destino}, Chile")
                
                # Botones uno debajo del otro para que ocupen el ancho y sean fáciles de tocar
                st.link_button("📍 Abrir en Google Maps", 
                               f"https://www.google.com/maps/dir/?api=1&origin={quote(DIRECCION_BASE)}&destination={dest_url}", 
                               use_container_width=True)
                
                st.link_button("🚙 Abrir en Waze", 
                               f"https://waze.com/ul?q={dest_url}&navigate=yes", 
                               use_container_width=True)
            else:
                st.error("No encontré la dirección.")
