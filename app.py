import streamlit as st
import requests
from geopy.geocoders import Nominatim
from urllib.parse import quote

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(page_title="Via Angel App", page_icon="🚚")

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
        st.header("Configuración de Ruta")
        # Opción 3: Entrada manual de Peaje (Unitario)
        peaje_unitario = st.number_input("Valor Peaje Unitario ($):", min_value=0, step=100, value=0, help="Escribe el valor de un peaje. La app lo multiplicará por 2 (ida y vuelta).")
        
        st.write("---")
        if st.button("Cerrar Sesión"):
            st.session_state["password_correct"] = False
            st.rerun()

    # --- INTERFAZ PRINCIPAL ---
    try:
        st.image("logoVA.jpeg", width=220)
    except:
        st.info("💡 Sube 'logoVA.jpeg' a GitHub para ver tu logo.")

    st.title("Calculadora de Fletes Inteligente")
    st.markdown("---")

    # Variables de cobro
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    TARIFA_MINIMA = 15000
    VALOR_KM = 950
    VALOR_PESO_KG = 50
    PRECIO_BENCINA = 1600 
    RENDIMIENTO_N400 = 12 

    # Entradas de texto principales
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
            with st.spinner('Calculando ruta y costos...'):
                km = obtener_distancia(destino)
            
            if km:
                # 1. Cálculo de Bencina (Costo operativo para ti)
                litros_viaje = (km * 2) / RENDIMIENTO_N400
                costo_bencina = litros_viaje * PRECIO_BENCINA
                
                # 2. Cálculo de Peajes (Reembolso de ida y vuelta)
                total_peajes = peaje_unitario * 2
                
                # 3. Lógica de Cobro al Cliente
                neto_servicio = TARIFA_MINIMA + (km * VALOR_KM) + (peso * VALOR_PESO_KG)
                iva = neto_servicio * 0.19
                
                # TOTAL FINAL: (Neto + IVA) + Peajes Exentos
                total_final = neto_servicio + iva + total_peajes

                # --- MOSTRAR RESULTADOS ---
                st.success(f"Distancia detectada: {km} km")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Gasto Bencina", f"${costo_bencina:,.0f}")
                c2.metric("Peajes (I/V)", f"${total_peajes:,.0f}")
                c3.metric("Total a Cobrar", f"${total_final:,.0f}")

                st.markdown(f"""
                ### 💰 Resumen de Cotización
                * **Valor Neto Servicio:** ${neto_servicio:,.0f}
                * **IVA (19%):** ${iva:,.0f}
                * **Peajes (Reembolso Exento):** ${total_peajes:,.0f}
                * **Total Final a Pagar:** **${total_final:,.0f}**
                ---
                **💡 Mensaje para el cliente:**
                'El flete sale **${neto_servicio:,.0f} + IVA**, más **${total_peajes:,.0f}** de peajes de carretera.'
                """)

                # Botones de Navegación
                st.subheader("🚀 Iniciar Navegación")
                dest_url = quote(f"{destino}, Chile")
                col1, col2 = st.columns(2)
                with col1:
                    st.link_button("📍 Google Maps", f"https://www.google.com/maps/dir/?api=1&origin={quote(DIRECCION_BASE)}&destination={dest_url}")
                with col2:
                    st.link_button("🚙 Waze", f"https://waze.com/ul?q={dest_url}&navigate=yes")
            else:
                st.error("No encontré la dirección.")
        else:
            st.warning("Escribe un destino.")
