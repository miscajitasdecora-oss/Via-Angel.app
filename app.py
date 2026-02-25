import streamlit as st

st.set_page_config(page_title="Via Angel", page_icon="🚚")
st.title("🚚 Via Angel: Gestión de Fletes")

# Tus precios de siempre
tarifa_base = 15000
precio_km_base = 950
recargo_por_kilo = 50 
iva_porcentaje = 0.19

# Entradas para el celular
distancia = st.number_input("Kilómetros del viaje:", min_value=0.0, step=0.1)
peso_carga = st.number_input("Peso de la carga (kg):", min_value=0.0, step=1.0)

if st.button("CALCULAR COBRO"):
    costo_distancia = distancia * precio_km_base
    costo_peso = peso_carga * recargo_por_kilo
    neto = tarifa_base + costo_distancia + costo_peso
    iva = neto * iva_porcentaje
    total_final = neto + iva

    st.divider()
    st.header(f"TOTAL A PAGAR: ${total_final:,.0f}")
    st.write(f"**Neto:** ${neto:,.0f} | **IVA (19%):** ${iva:,.0f}")
    st.info("Via Angel - Profesionalismo en cada ruta.")
