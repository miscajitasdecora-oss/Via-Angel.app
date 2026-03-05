import streamlit as st
import requests
from geopy.geocoders import Nominatim
from urllib.parse import quote

# 1. CONFIGURACIÓN DE LA PÁGINA (Para que se vea bien en celulares)
st.set_page_config(page_title="Via Angel Corporación", page_icon="🚚", layout="centered")

# Estilo visual "Pro" para los resultados
st.markdown("""
    <style>
    .reportview-container { background: #fdfdfd; }
    .stButton>button { width: 100%; height: 55px; border-radius: 12px; font-weight: bold; font-size: 18px; }
    .css-15497th { background-color: #f1f3f6; border-radius: 15px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE SEGURIDAD (Acceso para ti y tu socio)
def check_password():
    def password_entered():
        if st.session_state["password"] == "Angel2026": # <-- AQUÍ PUEDES CAMBIAR TU CLAVE
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso Privado Via Angel")
        st.text_input("Ingresa la contraseña de socio", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Acceso Privado Via Angel")
        st.text_input("Contraseña incorrecta, intenta de nuevo", type="password", on_change=password_entered, key="password")
        st.error("😕 Error de acceso")
        return False
    else:
        return True

if check_password():
    # --- INICIO DE LA APLICACIÓN ---

    # 3. MOSTRAR LOGOTIPO
    try:
        st.image("logoVA.jpeg", width=250)
    except:
        st.warning("⚠️ Sube el archivo 'logoVA.jpeg' a GitHub para ver el logo.")

    st.title("Calculadora de Fletes Pro")
    st.write("---")

    # 4. VARIABLES DE NEGOCIO (Tus precios)
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    COORD_BASE = "-33.3930, -70.7937" # Coordenadas de tu oficina
    TARIFA_MINIMA = 15000
    VALOR_KM = 950
    VALOR_PESO_KG = 50

    # 5. ENTRADA DE DATOS
    st.subheader("📍 Datos del Servicio")
    destino_cliente = st.text_input("Dirección de destino:", placeholder="Ej: Av. Vitacura 2000, Santiago")
    peso_mercaderia = st.number_input("Peso de la carga (kg):", min_value=0.0, step=1.0)

    # 6. FUNCIÓN DE CÁLCULO DE DISTANCIA (Mágica y Automática)
    def obtener_km(destino_texto):
        try:
            geolocator = Nominatim(user_agent="via_angel_app_v2")
            location = geolocator.geocode(destino_texto + ", Chile")
            if location:
                # Consultamos al servidor de rutas la distancia por calle
                url_ruta = f"http://router.project-osrm.org/route/v1/driving/-70.7937,-33.3930;{location.longitude},{location.latitude}?overview=false"
                data = requests.get(url_ruta).json()
                distancia = data['routes'][0]['distance'] / 1000
                return round(distancia, 1)
            return None
        except:
            return None

    # 7. BOTÓN DE CÁLCULO Y RESULTADOS
    if st.button("GENERAR COTIZACIÓN"):
        if destino_cliente:
            with st.spinner('Calculando mejor ruta y precios...'):
                km_totales = obtener_km(destino_cliente)
            
            if km_totales:
                # Lógica de cobro
                neto_distancia = km_totales * VALOR_KM
                neto_peso = peso_mercaderia * VALOR_PESO_KG
                total_neto = TARIFA_MINIMA + neto_distancia + neto_peso
                
                valor_iva = total_neto * 0.19
                gran_total = total_neto + valor_iva

                # Visualización para el teléfono
                st.success(f"✅ Ruta calculada: {km_totales} kilómetros.")
                
                st.markdown("### 📄 Resumen de Cobro")
                c1, c2 = st.columns(2)
                with c1:
                    st.metric(label="VALOR NETO", value=f"${total_neto:,.0f}")
                    st.caption("Este es el valor para el cliente.")
                with c2:
                    st.metric(label="TOTAL (IVA 19%)", value=f"${gran_total:,.0f}")
                    st.caption("Monto para la factura.")

                st.info(f"💡 **Copia esto:** 'El valor del flete es de ${total_neto:,.0f} + IVA.'")

                # 8. BOTONES DE NAVEGACIÓN GPS
                st.write("---")
                st.subheader("🚀 Iniciar Logística")
                
                dest_url = quote(f"{destino_cliente}, Chile")
                
                col_g, col_w = st.columns(2)
                with col_g:
                    st.link_button("📍 Abrir Google Maps", f"https://www.google.com/maps/dir/?api=1&origin={quote(DIRECCION_BASE)}&destination={dest_url}&travelmode=driving")
                with col_w:
                    st.link_button("🚙 Abrir Waze", f"https://waze.com/ul?q={dest_url}&navigate=yes")
            else:
                st.error("No pudimos encontrar la dirección. Intenta ser más específica.")
        else:
            st.warning("Por favor, ingresa una dirección de destino.")

    st.sidebar.markdown("---")
    st.sidebar.write("🏢 **Via Angel Corp**")
    st.sidebar.write(f"Base: {DIRECCION_BASE}")
