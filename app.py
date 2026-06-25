import streamlit as st
import requests
from geopy.geocoders import Nominatim
from urllib.parse import quote
import math

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
        
        # SECCIÓN DE PEAJES
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
        
        st.write("---")
        
        # NUEVA SECCIÓN: RECARGO NOCTURNO
        st.subheader("Horario Especial")
        activar_nocturno = st.checkbox("¿Requiere Conducción Nocturna?", value=False, help="Aplica recargo por conducir entre las 22:00 y las 06:00 horas.")
        if activar_nocturno:
            st.warning("🌙 Modo Nocturno Activado")

    # --- CUERPO PRINCIPAL ---
    try:
        st.image("logoVA.jpeg", width=220)
    except:
        pass

    st.title("Calculadora de Fletes Inteligente")
    st.markdown("---")

    # VARIABLES DE NEGOCIO BASE (Valores fijos de mercado 2026)
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    PRECIO_BENCINA = 1600 

    # Parámetros para tramos locales (Santiago)
    BANDERAZO_SANTIAGO = 35000     
    VALOR_KM_SANTIAGO = 750        
    VALOR_PESO_KG_SANTIAGO = 50    
    FACTOR_RECARGO_NOCTURNO_LOCAL = 0.25 # +25% en Santiago

    # Parámetros para regiones (Carretera)
    VIATICO_FIJO_NOCHE = 40000     
    TARIFA_PLANA_NOCTURNA_REGION = 50000 # Cargo fijo de $50.000 por noche en carretera

    # Entradas de la App
    destino = st.text_input("📍 Destino de entrega:", placeholder="Ej: Quintero, Chile")
    peso = st.number_input("📦 Peso de la carga (kg):", min_value=0.0, step=1.0, value=10.0)

    # Función de cálculo de distancia (OSRM)
    def obtener_distancia(destino_texto):
        try:
            geolocator = Nominatim(user_agent="via_angel_final_v1")
            location = geolocator.geocode(destino_texto + ", Chile")
            if location:
                url = f"http://project-osrm.org;{location.longitude},{location.latitude}?overview=false"
                r = requests.get(url).json()
                return round(r['routes']['distance'] / 1000, 1)
            return None
        except:
            return None

    # BOTÓN DE CÁLCULO
    if st.button("CALCULAR AHORA"):
        if destino:
            with st.spinner('Procesando ruta...'):
                km = obtener_distancia(destino)
            
            if km:
                total_peajes = monto_peaje * 2 if activar_peajes else 0
                monto_nocturno_detalle = 0
                
                # --- AJUSTE DINÁMICO POR PESO DE LA CARGA (CUESTAS Y CONSUMO) ---
                if peso <= 150:
                    rendimiento_real = 12       
                    valor_km_regiones_real = 1100  
                    estado_carga = "Liviana"
                elif 150 < peso <= 400:
                    rendimiento_real = 10       
                    valor_km_regiones_real = 1200  
                    estado_carga = "Moderada"
                else:
                    rendimiento_real = 8        
                    valor_km_regiones_real = 1350  
                    estado_carga = "Pesada (Exigencia Máxima)"

                # --- LÓGICA DE CONDICIONAL (SANTIAGO VS REGIONES) ---
                if km <= 100:
                    # REGLA LOCAL (URBANO/SANTIAGO)
                    tipo_viaje = f"Local (Santiago) - Carga {estado_carga}"
                    neto_servicio = BANDERAZO_SANTIAGO + (km * VALOR_KM_SANTIAGO) + (peso * VALOR_PESO_KG_SANTIAGO)
                    viaticos_totales = 0
                    
                    # Aplicar recargo nocturno local si está activo (+25%)
                    if activar_nocturno:
                        monto_nocturno_detalle = neto_servicio * FACTOR_RECARGO_NOCTURNO_LOCAL
                        neto_servicio += monto_nocturno_detalle
                else:
                    # REGLA INTERREGIONAL (VIAJES LARGOS)
                    tipo_viaje = f"Interregional (Regiones) - Carga {estado_carga}"
                    neto_servicio = km * valor_km_regiones_real
                    
                    # Calcula las noches en ruta (1 noche cada 700 km de ida)
                    noches_calculadas = math.floor(km / 700)
                    if noches_calculadas < 1:
                        noches_calculadas = 1
                    
                    viaticos_totales = noches_calculadas * VIATICO_FIJO_NOCHE
                    neto_servicio += viaticos_totales
                    
                    # Aplicar tarifa plana nocturna regional si está activo
                    if activar_nocturno:
                        monto_nocturno_detalle = TARIFA_PLANA_NOCTURNA_REGION
                        neto_servicio += monto_nocturno_detalle

                # IVA
                iva = neto_servicio * 0.19
                
                # Bencina real estimada ida y vuelta usando el rendimiento castigado por peso
                costo_bencina = ((km * 2) / rendimiento_real) * PRECIO_BENCINA
                
                # TOTAL FINAL
                total_final = neto_servicio + iva + total_peajes

                # --- MOSTRAR RESULTADOS ---
                st.info(f"Segmento de viaje: **{tipo_viaje}**")
                if activar_nocturno:
                    st.warning(f"🌙 El precio incluye recargo nocturno aplicado.")
                st.success(f"Distancia detectada: {km} km")
                
                # Métricas destacadas
                c1, c2, c3 = st.columns(3)
                c1.metric("Bencina Estimada (I/V)", f"${costo_bencina:,.0f}")
                if km > 100:
                    c2.metric("Viáticos Incluidos", f"${viaticos_totales:,.0f}")
                else:
                    c2.metric("Peajes Reembolso", f"${total_peajes:,.0f}")
                c3.metric("Total Bruto", f"${total_final:,.0f}")

                st.markdown(f"""
                ### 💰 Resumen de Cotización Viangel
                * **Tipo de Carga:** Carga {estado_carga} ({peso} kg)
                * **Valor Neto Servicio:** ${neto_servicio:,.0f} 
                {"*(Incluye recargo nocturno de $" + f"{monto_nocturno_detalle:,.0f}" + ")*" if activar_nocturno else ""}
                * **IVA (19%):** ${iva:,.0f}
                * **Peajes:** ${total_peajes:,.0f}
                * **Total Final a Pagar (Factura):** **${total_final:,.0f}**
                ---
                **Mensaje para el cliente:** 
                'El servicio exclusivo tiene un valor de **${neto_servicio:,.0f} + IVA**. Adicionalmente, se consideran **${total_peajes:,.0f}** correspondientes a peajes obligatorios de la ruta.'
                """)

                # --- NAVEGACIÓN ---
                st.write("---")
                st.subheader("🚀 Iniciar Navegación")
                dest_url = quote(f"{destino}, Chile")
                
                # Google Maps
                st.link_button("📍 Abrir en Google Maps", 
                               f"https://google.com{quote(DIRECCION_BASE)}&destination={dest_url}", 
                               use_container_width=True)
                
                # Waze
                st.link_button("🚙 Abrir en Waze", 
                               f"https://waze.com{dest_url}&navigate=yes", 
                               use_container_width=True)
            else:
                st.error("No se encontró la dirección. Intenta escribirla más completa.")
        else:
            st.warning("Escribe una dirección de destino primero.")
