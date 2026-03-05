import streamlit as st
import requests
from geopy.geocoders import Nominatim
from urllib.parse import quote

# 1. Configuración Visual y Móvil
st.set_page_config(page_title="Via Angel App", page_icon=" ", layout="centered")

# Estilo para botones grandes y legibles en celular
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 60px; font-size: 20px; font-weight: bold; border-radius: 10px; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 2. Logotipo
try:
    st.image("logoVA.jpeg", width=200)
except:
    st.info("💡 Sube tu logo a GitHub con el nombre 'logoVA.jpeg'")

st.title("Sistema de Fletes Via Angel")

# 3. Variables de Negocio (Puedes cambiarlas aquí)
ORIGEN_DIRECCION = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
PRECIO_KM = 950
TARIFA_BASE = 15000
IVA_FACTOR = 0.19

# 4. Función para Calcular Distancia Automática
def obtener_distancia(destino):
    try:
        geolocator = Nominatim(user_agent="via_angel_app")
        loc_origen = geolocator.geocode(ORIGEN_DIRECCION)
        loc_destino = geolocator.geocode(destino + ", Chile")
        
        if loc_origen and loc_destino:
            # Consultar servidor de rutas (Gratis)
            url = f"http://router.project-osrm.org/route/v1/driving/{loc_origen.longitude},{loc_origen.latitude};{loc_destino.longitude},{loc_destino.latitude}?overview=false"
            r = requests.get(url)
            data = r.json()
            distancia_km = data['routes'][0]['distance'] / 1000
            return round(distancia_km, 2)
        return None
    except:
        return None

# 5. Interfaz de Usuario
st.write(f"📍 **Origen:** {ORIGEN_DIRECCION}")
destino_input = st.text_input("📍 **Destino:** (Ej: Alameda 100, Santiago)", placeholder="Escribe la dirección de entrega...")
peso_kg = st.number_input("📦 **Peso de la carga (kg):**", min_value=0, step=1)

if destino_input:
    with st.spinner('Calculando mejor ruta...'):
        km_calculados = obtener_distancia(destino_input)
    
    if km_calculados:
        st.success(f"Distancia detectada: **{km_calculados} km**")
        
        # Cálculos Económicos
        valor_neto = TARIFA_BASE + (km_calculados * PRECIO_KM) + (peso_kg * 50)
        iva = valor_neto * IVA_FACTOR
        total_con_iva = valor_neto + iva

        # Mostrar Resultados (Diseño de Tarjetas)
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"<div class='metric-card'><b>VALOR NETO</b><br><h2>${valor_neto:,.0f}</h2><small>+ IVA</small></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"<div class='metric-card'><b>TOTAL CON IVA</b><br><h2>${total_con_iva:,.0f}</h2><small>Monto Factura</small></div>", unsafe_allow_html=True)

        st.info(f"💬 **Frase para el cliente:** 'Su flete sale ${valor_neto:,.0f} + IVA.'")

        # 6. Botones de Navegación para el Teléfono
        st.divider()
        st.subheader(" Iniciar Viaje")
        
        direccion_url = quote(destino_input + ", Chile")
        
        col_maps, col_waze = st.columns(2)
        with col_maps:
            st.link_button("📍 Google Maps", f"https://www.google.com/maps/dir/?api=1&origin={quote(ORIGEN_DIRECCION)}&destination={direccion_url}&travelmode=driving")
        with col_waze:
            st.link_button("🚙 Waze", f"https://waze.com/ul?q={direccion_url}&navigate=yes")

    else:
        st.error("No pudimos encontrar esa dirección. Intenta ser más específica (ej: Calle 123, Comuna).")

st.sidebar.write("Sesión: Corporativo Via Angel")
