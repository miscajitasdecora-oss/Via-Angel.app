import streamlit as st
import requests
from geopy.geocoders import Nominatim
from urllib.parse import quote

# 1. CONFIGURACIÓN DE LA APP (Optimizada para celular)
st.set_page_config(page_title="Via Angel App", page_icon="🚚")

# 2. SISTEMA DE SEGURIDAD
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 Acceso Via Angel")
        password_input = st.text_input("Ingresa la clave para entrar", type="password")
        if st.button("Entrar"):
            # Tu clave actual
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
        
        # Botón de cerrar sesión
        if st.button("Cerrar Sesión"):
            st.session_state["password_correct"] = False
            st.rerun()
        
        st.write("---")
        
        # SECCIÓN DE PEAJES (Lo que marcaste en el círculo verde)
        st.subheader("Configuración de Peajes")
        activar_peajes = st.checkbox("¿Ruta con Peajes?", value=False)
        
        monto_peaje = 0
        if activar_peajes:
            monto_peaje = st.number_input(
                "Valor de 1 Peaje ($):", 
                min_value=0, 
                step=100, 
                value=0
            )
            st.info("💡 Se cobrará Ida y Vuelta ($" + str(monto_peaje * 2) + ")")

    # --- CUERPO PRINCIPAL ---
    # Intentar cargar el logo
    try:
        st.image("logoVA.jpeg", width=220)
    except:
        pass

    st.title("Calculadora de Fletes Inteligente")
    st.markdown("---")

    # VARIABLES DE NEGOCIO (Valores fijos)
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    TARIFA_MINIMA = 15000
    VALOR_KM = 950
    VALOR_PESO_KG = 50
    PRECIO_BENCINA = 1600 # Valor actualizado abril 2026
    RENDIMIENTO_N400 = 12 # Km/litro promedio cargada

    # Entradas de la App
    destino = st.text_input("📍 Destino de entrega:", placeholder="Ej: Quintero, Chile")
    peso = st.number_input("📦 Peso de la carga (kg):", min_value=0.0, step=1.0, value=10.0)

    # Función de cálculo de distancia (OSRM)
    def obtener_distancia(destino_texto):
        try:
            geolocator = Nominatim(user_agent="via_angel_final_v1")
            location = geolocator.geocode(destino_texto + ", Chile")
            if location:
                # Coordenadas de Pudahuel (Base) a Destino
                url = f"http://router.project-osrm.org/route/v1/driving/-70.7937,-33.3930;{location.longitude},{location.latitude}?overview=false"
                r = requests.get(url).json()
                return round(r['routes'][0]['distance'] / 1000, 1)
            return None
        except:
            return None

    # BOTÓN DE CÁLCULO
    if st.button("CALCULAR AHORA"):
        if destino:
            with st.spinner('Procesando ruta...'):
                km = obtener_distancia(destino)
            
            if km:
                # 1. Cálculos de Costos
                total_peajes = monto_peaje * 2 if activar_peajes else 0
                neto_servicio = TARIFA_MINIMA + (km * VALOR_KM) + (peso * VALOR_PESO_KG)
                iva = neto_servicio * 0.19
                
                # Bencina (Tu gasto de bolsillo para saber cuánto ganas)
                costo_bencina = ((km * 2) / RENDIMIENTO_N400) * PRECIO_BENCINA
                
                # TOTAL FINAL
                total_final = neto_servicio + iva + total_peajes

                # --- MOSTRAR RESULTADOS ---
                st.success(f"Distancia detectada: {km} km")
                
                # Métricas destacadas
                c1, c2, c3 = st.columns(3)
                c1.metric("Bencina (Gasto)", f"${costo_bencina:,.0f}")
                c2.metric("Peajes (I/V)", f"${total_peajes:,.0f}")
                c3.metric("Total Cobro", f"${total_final:,.0f}")

                st.markdown(f"""
                ### 💰 Resumen de Cotización
                * **Valor Neto:** ${neto_servicio:,.0f}
                * **IVA (19%):** ${iva:,.0f}
                * **Peajes (Reembolso):** ${total_peajes:,.0f}
                * **Total Final a Pagar:** **${total_final:,.0f}**
                ---
                **Dile al cliente:** 'El servicio es de ${neto_servicio:,.0f} + IVA. Adicionalmente se cobran ${total_peajes:,.0f} por peajes de ida y vuelta.'
                """)

                # --- NAVEGACIÓN (Botones anchos abajo) ---
                st.write("---")
                st.subheader("🚀 Iniciar Navegación")
                dest_url = quote(f"{destino}, Chile")
                
                # Google Maps
                st.link_button("📍 Abrir en Google Maps", 
                               f"https://www.google.com/maps/dir/?api=1&origin={quote(DIRECCION_BASE)}&destination={dest_url}", 
                               use_container_width=True)
                
                # Waze
                st.link_button("🚙 Abrir en Waze", 
                               f"https://waze.com/ul?q={dest_url}&navigate=yes", 
                               use_container_width=True)
            else:
                st.error("No se encontró la dirección. Intenta escribirla más completa.")
        else:
            st.warning("Escribe una dirección de destino primero.")
