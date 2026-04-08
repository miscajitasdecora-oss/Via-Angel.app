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
    try:
        st.image("logoVA.jpeg", width=220)
    except:
        st.info("💡 Sube 'logoVA.jpeg' a GitHub.")

    st.title("Calculadora de Fletes Inteligente")
    st.markdown("---")

    # --- VARIABLES DE NEGOCIO ---
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    TARIFA_MINIMA = 15000
    VALOR_KM = 950
    VALOR_PESO_KG = 50
    
    # AJUSTE DE COMBUSTIBLE (Aquí está la magia)
    PRECIO_BENCINA = 1600 
    RENDIMIENTO_N400 = 12 # Km por litro (promedio cargada)

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
                # 1. Cálculo base (Servicio + Distancia + Peso)
                costo_servicio = TARIFA_MINIMA + (km * VALOR_KM) + (peso * VALOR_PESO_KG)
                
                # 2. Cargo por Combustible (Lo que gasta la N400 en ir y volver)
                # Multiplicamos por 2 porque la camioneta tiene que volver a base
                litros_viaje = (km * 2) / RENDIMIENTO_N400
                cargo_bencina = litros_viaje * PRECIO_BENCINA
                
                # 3. GRAN TOTAL
                neto = costo_servicio + cargo_bencina
                iva = neto * 0.19
                total_final = neto + iva

                # INTERFAZ PARA EL GERENTE (Limpia y profesional)
                st.success(f"Ruta detectada: {km} km")
                
                # Usamos columnas para que se vea pro
                col1, col2 = st.columns(2)
                col1.metric("Costo Bencina (Ida/Vuelta)", f"${cargo_bencina:,.0f}")
                col2.metric("Total a Cobrar", f"${total_final:,.0f}")

                st.markdown(f"""
                ### 💰 Resumen de Cotización
                * **Servicio Base + Carga:** ${costo_servicio:,.0f}
                * **Cargo Combustible (Alza):** ${cargo_bencina:,.0f}
                * **Valor Neto:** ${neto:,.0f}
                * **IVA (19%):** ${iva:,.0f}
                * **Total Final:** **${total_final:,.0f}**
                ---
                """)
                
                # Botones de Navegación
                st.subheader("🚀 Iniciar Navegación")
                dest_url = quote(f"{destino}, Chile")
                c1, c2 = st.columns(2)
                with c1: st.link_button("📍 Google Maps", f"https://www.google.com/maps/dir/?api=1&origin={quote(DIRECCION_BASE)}&destination={dest_url}")
                with c2: st.link_button("🚙 Waze", f"https://waze.com/ul?q={dest_url}&navigate=yes")
            else:
                st.error("Dirección no encontrada.")
