import streamlit as st
import requests
from geopy.geocoders import Nominatim
from urllib.parse import quote

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(page_title="Via Angel App", page_icon="🚚")

# 2. SISTEMA DE SEGURIDAD SIMPLE
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 Acceso Via Angel")
        password_input = st.text_input("Ingresa la clave para entrar", type="password")
        if st.button("Entrar"):
            # OJO: Cambia esto a st.secrets["password"] después para más seguridad
            if password_input == "fletesmi": 
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Clave incorrecta")
        return False
    return True

if check_password():
    # --- INTERFAZ PRINCIPAL ---
    try:
        st.image("logoVA.jpeg", width=220)
    except:
        st.info("💡 Sube 'logoVA.jpeg' a GitHub para ver tu logo.")

    st.title("Calculadora de Fletes Inteligente")
    st.markdown("---")

    # --- VARIABLES DE COSTO ACTUALIZADAS ---
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    TARIFA_MINIMA = 15000
    VALOR_KM = 950
    VALOR_PESO_KG = 50
    
    # NUEVAS VARIABLES DE COMBUSTIBLE
    PRECIO_BENCINA_LITRO = 1600  # Valor actual aprox
    RENDIMIENTO_N400 = 12       # 16 en carretera, pero 12 es más realista cargada/ciudad
    # ---------------------------------------

    # Entradas de texto
    destino = st.text_input("📍 Destino de entrega:", placeholder="Ej: Calle San Diego 100, Santiago")
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
            with st.spinner('Calculando ruta...'):
                km = obtener_distancia(destino)
            
            if km:
                # --- LÓGICA DE DINERO ---
                # Ida y vuelta (opcional, si vuelves vacía a la base deberías considerar km * 2)
                distancia_total = km 
                
                # Cálculo de Bencina
                litros_necesarios = distancia_total / RENDIMIENTO_N400
                costo_bencina = litros_necesarios * PRECIO_BENCINA_LITRO
                
                # Totales
                neto = TARIFA_MINIMA + (km * VALOR_KM) + (peso * VALOR_PESO_KG)
                iva = neto * 0.19
                total_final = neto + iva
                
                # Margen aproximado (Neto menos bencina)
                utilidad_estimada = neto - costo_bencina

                # Mostrar resultados estilo "Tarjeta"
                st.success(f"Distancia detectada: {km} km")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Gasto en Bencina (est.)", f"${costo_bencina:,.0f}")
                with col2:
                    st.metric("Utilidad Bruta (Neto - Bencina)", f"${utilidad_estimada:,.0f}")

                st.markdown(f"""
                ### 💰 Resumen de Cotización
                * **Valor Neto:** ${neto:,.0f}
                * **IVA (19%):** ${iva:,.0f}
                * **Total a pagar:** **${total_final:,.0f}**
                
                ---
                **💡 Tips para el flete:**
                * Consumo estimado: {litros_necesarios:.2f} litros.
                * Dile al cliente: 'El flete sale ${neto:,.0f} + IVA'
                """)

                # Botones para el GPS
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

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["password_correct"] = False
        st.rerun()
