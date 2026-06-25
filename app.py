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
        
        # NUEVA CASILLA: TARIFA NOCTURNA (Agregada a tu barra lateral)
        st.subheader("Horario Especial")
        activar_nocturno = st.checkbox("¿Requiere Conducción Nocturna?", value=False)
        if activar_nocturno:
            st.warning("🌙 Modo Nocturno Activado")

    # --- CUERPO PRINCIPAL ---
    try:
        st.image("logoVA.jpeg", width=220)
    except:
        pass

    st.title("Calculadora de Fletes Inteligente")
    st.markdown("---")

    # VARIABLES DE NEGOCIO BASE (Valores actualizados 2026)
    DIRECCION_BASE = "Osvaldo Croquevielle 2207, Pudahuel, Chile"
    PRECIO_BENCINA = 1600 

    # Parámetros locales (Santiago)
    BANDERAZO_SANTIAGO = 35000     
    VALOR_KM_SANTIAGO = 750        
    VALOR_PESO_KG_SANTIAGO = 50    
    FACTOR_RECARGO_NOCTURNO_LOCAL = 0.25 

    # Parámetros interregionales (Regiones)
    VIATICO_FIJO_NOCHE = 40000     
    TARIFA_PLANA_NOCTURNA_REGION = 50000 

    # Entradas de la App
    destino = st.text_input("📍 Destino de entrega:", placeholder="Ej: Quintero, Chile")
    peso = st.number_input("📦 Peso de la carga (kg):", min_value=0.0, step=1.0, value=10.0)

    # TU FUNCIÓN DE MAPA ORIGINAL (Completamente intacta)
    def obtener_distancia(destino_texto):
        try:
            geolocator = Nominatim(user_agent="via_angel_final_v1")
            location = geolocator.geocode(destino_texto + ", Chile")
            if location:
                url = f"http://project-osrm.org;{location.longitude},{location.latitude}?overview=false"
                r = requests.get(url).json()
                return round(r['routes'][0]['distance'] / 1000, 1)
            return None
        except:
            return None

    # BOTÓN DE CÁLCULO (Corre con tu flujo original de mapas)
    if st.button("CALCULAR AHORA"):
        if destino:
            with st.spinner('Procesando ruta...'):
                km = obtener_distancia(destino)
            
            if km:
                total_peajes = monto_peaje * 2 if activar_peajes else 0
                monto_nocturno_detalle = 0
                
                # --- NUEVA MATEMÁTICA INTELIGENTE: EVALUACIÓN DE PESO Y EXIGENCIA DEL MOTOR ---
                if peso <= 150:
                    rendimiento_real = 12       
                    valor_km_regiones_real = 1100  
                    estado_carga = "Liviana"
                elif 150 < peso <= 400:
                    rendimiento_real = 10       
                    valor_km_regiones_real = 1200  
                    estado_carga = "Moderada"
                else:
                    rendimiento_real = 8        # Castigo de bencina por baterías o subidas tipo Lebu
                    valor_km_regiones_real = 1350  # Cobro más caro por kilómetro en carretera
                    estado_carga = "Pesada (Exigencia Máxima)"

                # --- CLASIFICACIÓN DE TARIFA COMERCIAL (SANTIAGO VS REGIONES) ---
                if km <= 100:
                    # Regla Urbana de Santiago
                    tipo_viaje = f"Local (Santiago) - Carga {estado_carga}"
                    neto_servicio = BANDERAZO_SANTIAGO + (km * VALOR_KM_SANTIAGO) + (peso * VALOR_PESO_KG_SANTIAGO)
                    viaticos_totales = 0
                    
                    # Sumar recargo nocturno local si está activo (+25%)
                    if activar_nocturno:
                        monto_nocturno_detalle = neto_servicio * FACTOR_RECARGO_NOCTURNO_LOCAL
                        neto_servicio += monto_nocturno_detalle
                else:
                    # Regla Carretera de Regiones
                    tipo_viaje = f"Interregional (Regiones) - Carga {estado_carga}"
                    neto_servicio = km * valor_km_regiones_real
                    
                    # Calcular noches automáticas en ruta
                    noches_calculadas = math.floor(km / 700)
                    if noches_calculadas < 1:
                        noches_calculadas = 1
                    
                    viaticos_totales = noches_calculadas * VIATICO_FIJO_NOCHE
                    neto_servicio += viaticos_totales
                    
                    # Sumar tarifa plana nocturna regional si está activa
                    if activar_nocturno:
                        monto_nocturno_detalle = TARIFA_PLANA_NOCTURNA_REGION
                        neto_servicio += monto_nocturno_detalle

                # IVA e impuestos sobre el neto final calculado
                iva = neto_servicio * 0.19
                
                # Bencina real estimada de ida y vuelta usando el rendimiento castigado por el peso
                costo_bencina = ((km * 2) / rendimiento_real) * PRECIO_BENCINA
                
                # TOTAL FINAL
                total_final = neto_servicio + iva + total_peajes

                # --- MOSTRAR RESULTADOS ---
                st.info(f"Segmento de viaje detectado: **{tipo_viaje}**")
                if activar_nocturno:
                    st.warning(f"🌙 El precio incluye recargo nocturno aplicado.")
                st.success(f"Distancia detectada: {km} km")
                
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
                
                st.link_button("📍 Abrir en Google Maps", 
                               f"https://google.com{quote(DIRECCION_BASE)}&destination={dest_url}", 
                               use_container_width=True)
                
                st.link_button("🚙 Abrir en Waze", 
                               f"https://waze.com{dest_url}&navigate=yes", 
                               use_container_width=True)
            else:
                st.error("No se encontró la dirección. Intenta escribirla más completa.")
        else:
            st.warning("Escribe una dirección de destino primero.")
