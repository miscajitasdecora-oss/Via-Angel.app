import streamlit as st
import requests
from geopy.geocoders import Nominatim
from urllib.parse import quote

# 1. CONFIGURACIÓN DE LA APP (Especial para ver en el celular)
st.set_page_config(page_title="Via Angel App", page_icon="🚚")

# 2. SISTEMA DE SEGURIDAD SIMPLE
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 Acceso Via Angel")
        password_input = st.text_input("Ingresa la clave para entrar", type="password")
        if st.button("Entrar"):
            if password_input == "fletesmi": # Tu nueva clave única
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta")
        return False
    return True

if check_password():
    # --- INTERFAZ PRINCIPAL ---
    
    # Mostrar el Logo
    try:
        st.image("logoVA.jpeg", width=220)
    except:
        st.info("💡 Sube 'logoVA.jpeg' a GitHub para ver tu logo.")

    st.title("Calculadora de Fletes Inteligente")
    st.markdown("---")

    # Variables de cobro (Cámbialas aquí si suben los precios)
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    TARIFA_MINIMA = 15000
    VALOR_KM = 950
    VALOR_PESO_KG = 50

    # Entradas de texto
    destino = st.text_input("📍 Destino de entrega:", placeholder="Ej: Calle San Diego 100, Santiago")
    peso = st.number_input("📦 Peso de la carga (kg):", min_value=0.0, step=1.0)

    # Función para calcular los KM automáticamente
    def obtener_distancia(destino_texto):
        try:
            geolocator = Nominatim(user_agent="via_angel_pro")
            location = geolocator.geocode(destino_texto + ", Chile")
            if location:
                # Consultamos al servidor de mapas (OSRM)
                url = f"http://router.project-osrm.org/route/v1/driving/-70.7937,-33.3930;{location.longitude},{location.latitude}?overview=false"
                r = requests.get(url).json()
                return round(r['routes'][0]['distance'] / 1000, 1)
            return None
        except:
            return None

    if st.button("CALCULAR AHORA"):
        if destino:
            with st.spinner('Calculando ruta...'):
                km = obtener_distancia(destino)
            
            if km:
                # Lógica de dinero
                neto = TARIFA_MINIMA + (km * VALOR_KM) + (peso * VALOR_PESO_KG)
                iva = neto * 0.19
                total_final = neto + iva

                # Mostrar resultados estilo "Tarjeta"
                st.success(f"Distancia detectada: {km} km")
                
                st.markdown(f"""
                ### 💰 Resumen de Cotización
                * **Valor Neto:** ${neto:,.0f}
                * **IVA (19%):** ${iva:,.0f}
                * **Total a pagar:** **${total_final:,.0f}**
                """)
                
                st.info(f"Dile al cliente: 'El flete sale ${neto:,.0f} + IVA'")

                # Botones para el GPS del celular
                st.write("---")
                st.subheader("🚀 Iniciar Navegación")
                dest_url = quote(f"{destino}, Chile")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.link_button("📍 Google Maps", f"https://www.google.com/maps/dir/?api=1&origin={quote(DIRECCION_BASE)}&destination={dest_url}&travelmode=driving")
                with c2:
                    st.link_button("🚙 Waze", f"https://waze.com/ul?q={dest_url}&navigate=yes")
            else:
                st.error("No encontré la dirección. Prueba escribiéndola más completa.")
        else:
            st.warning("Escribe una dirección de destino.")

    # Botón para cerrar sesión si lo necesitas
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["password_correct"] = False
        st.rerun()
