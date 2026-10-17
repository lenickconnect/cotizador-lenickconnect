import os
import io
import urllib.parse
from datetime import datetime
import pandas as pd
import streamlit as st

# Importamos el generador de PDF y utilidades del cronograma y destinos
from pdf_generator_break import (
    generar_pdf_break,
    calcular_cronograma,
    obtener_info_destino,
    construir_mensaje_whatsapp,
    DATOS_DESTINOS
)

# --- Configuración de la página ---
st.set_page_config(
    page_title="Break Tienda de Viajes - Itinerarios y Propuestas",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Tarifas base ---
TARIFAS_PREDEFINIDAS = {
    "Canasvieiras": {
        # Posada Classic: $629 USD | Posada VIP: $699 USD
        "classic":    {"usd_promo": 629, "usd_tachado": 850},
        "vip":        {"usd_promo": 699, "usd_tachado": 950},
        "individual": {"usd_promo": 629, "usd_tachado": 850},
        "doble":      {"usd_promo": 629, "usd_tachado": 850},
        "ars": 210000,
        "ars_tachado": 310000,
        "ars_bonificacion": 100000
    },
    "Ferrugem": {
        "individual": {"usd_promo": 649, "usd_tachado": 750},
        "doble":      {"usd_promo": 649, "usd_tachado": 750},
        "ars": 210000,
        "ars_tachado": 310000,
        "ars_bonificacion": 100000
    },
    "Camboriú": {
        "individual": {"usd_promo": 640, "usd_tachado": 840},
        "doble":      {"usd_promo": 740, "usd_tachado": 940},
        "ars": 210000,
        "ars_tachado": 310000,
        "ars_bonificacion": 100000
    }
}

OPCIONES_ALOJAMIENTO = [
    "Posada Classic",
    "Posada VIP",
    "Solo Alojamiento"
]

# Inicializar historial en sesión
if "historial" not in st.session_state:
    st.session_state["historial"] = []

# --- Encabezado ---
st.title("🌴 Break Tienda de Viajes")
st.subheader("Generador Integral de Propuestas e Itinerarios (5 Páginas)")

# --- Barra Lateral: Parámetros ---
with st.sidebar:
    st.header("📋 Datos del Cliente")
    cliente = st.text_input("Nombre del cliente", value="LeNick").strip()
    telefono = st.text_input(
        "Teléfono / WhatsApp (ej: 5491112345678)", value="").strip()

    st.markdown("---")
    st.header("🏖️ Configuración del Paquete")

    # Selección de Destino
    opciones_destino = ["Canasvieiras", "Ferrugem",
                        "Camboriú", "Praia do Rosa", "Otro personalizado..."]
    destino_seleccionado = st.selectbox("Destino", opciones_destino)

    if destino_seleccionado == "Otro personalizado...":
        destino = st.text_input(
            "Nombre del destino personalizado", value="Florianópolis").strip()
        custom_usd_promo = st.number_input(
            "Tarifa USD por persona", min_value=100, max_value=5000, value=629, step=10)
        custom_usd_tachado = custom_usd_promo + 200
        custom_ars = st.number_input(
            "Inscripción en ARS por persona", min_value=0, max_value=2000000, value=210000, step=10000)
    elif destino_seleccionado == "Praia do Rosa":
        destino = "Praia do Rosa"
        custom_usd_promo = st.number_input(
            "Tarifa USD por persona para Praia do Rosa", min_value=100, max_value=5000, value=680, step=10)
        custom_usd_tachado = custom_usd_promo + 200
        custom_ars = 210000
    else:
        destino = destino_seleccionado

    # Selector Inteligente de Salida (Viernes)
    st.markdown("#### 📅 Fecha de Partida")
    fecha_input = st.date_input(
        "Viernes de salida",
        value=datetime(2027, 1, 22).date(),
        help="Elegí la fecha del viernes de partida. El cronograma completo se calculará automáticamente."
    )
    cronograma = calcular_cronograma(fecha_input)
    if fecha_input.weekday() != 4:
        st.caption(
            f"ℹ️ Ajustado al viernes de partida: **{cronograma['salida_str'].split(' - ')[0]}**")

    # Visualización resumida del cronograma en la barra lateral
    with st.expander("🗓️ Cronograma Calculado", expanded=True):
        st.markdown(f"🚌 **Salida:** {cronograma['salida_str']}")
        st.markdown(f"🏨 **Llegada / Check-in:** {cronograma['checkin_str']}")
        st.markdown(
            f"🏖️ **Estadía Alojamiento:** {cronograma['estadia_itinerario']}")
        st.markdown(f"🔄 **Check-out / Regreso:** {cronograma['checkout_str']}")
        st.markdown(f"🏁 **Arribo a Origen:** {cronograma['arribo_str']}")

    # Tipo de Viaje y Pasajeros
    tipo_viaje = st.selectbox(
        "Tipo de viaje",
        ["Familiar / Grupal",
            "En Pareja (2 personas)", "Dos amigos/as (2 personas)", "Individual (1 persona)"]
    )

    if tipo_viaje == "Individual (1 persona)":
        cant_pasajeros = 1
        tipo_grupo = "Individual"
    elif tipo_viaje == "En Pareja (2 personas)":
        cant_pasajeros = 2
        tipo_grupo = "en Pareja"
    elif tipo_viaje == "Dos amigos/as (2 personas)":
        cant_pasajeros = 2
        tipo_grupo = "Doble (2 personas)"
    else:
        cant_pasajeros = st.number_input(
            "Cantidad total de pasajeros", min_value=1, max_value=60, value=5, step=1)
        tipo_grupo = "Familiar / Grupal"

    # Recargo Base Doble Exclusiva (solo para 2 pasajeros)
    base_doble_exclusiva = False
    if cant_pasajeros == 2:
        base_doble_exclusiva = st.checkbox(
            "🔒 Base Doble Exclusiva (+100 USD/persona)",
            help="Lugar exclusivo para 2 personas. Se suma un adicional de 100 USD por persona sobre la tarifa base."
        )
        if base_doble_exclusiva:
            st.caption(
                "✅ Recargo aplicado: +100 USD por persona (lugar exclusivo para 2).")

    # Alojamiento (únicamente 3 opciones)
    alojamiento_sel = st.selectbox("Tipo de Alojamiento", OPCIONES_ALOJAMIENTO)
    alojamiento_texto = alojamiento_sel

    # Selector independiente de Régimen de Comidas (por pasajero)
    REGIMENES_COMIDAS = {
        "Sin régimen ($0 USD)": 0,
        "Solo Desayuno (+70 USD/pax)": 70,
        "Solo Cenas (+100 USD/pax)": 100,
        "Media Pensión (Desayuno + Cena) (+160 USD/pax)": 160
    }
    regimen_sel = st.selectbox(
        "Régimen de Comidas (por pasajero)", list(REGIMENES_COMIDAS.keys()))
    costo_comida_unitario = REGIMENES_COMIDAS[regimen_sel]
    regimen_nombre_limpio = regimen_sel.split(" (")[0]

    # Modalidad de Transporte
    mes_salida = cronograma["fecha_salida"].month
    recargo_aereo = 150 if mes_salida == 3 else 385
    label_mes_aereo = "Marzo" if mes_salida == 3 else "Ene/Feb"

    OPCIONES_TRANSPORTE = [
        "Bus Semi Cama (Incluido / Base)",
        "Bus Cama (+75 USD/pax)",
        f"Aéreo Jetsmart Directo (+{recargo_aereo} USD/pax - {label_mes_aereo})",
        "Solo Bus (Venta exclusiva de transporte)",
        "Sin Transporte (Solo alojamiento)"
    ]
    transporte_sel = st.selectbox(
        "Modalidad de Transporte", OPCIONES_TRANSPORTE)

    if "Bus Cama" in transporte_sel:
        costo_transporte_unitario = 75
        transporte_tipo = "Bus Cama"
    elif "Aéreo" in transporte_sel:
        costo_transporte_unitario = recargo_aereo
        transporte_tipo = "Aéreo Jetsmart Directo"
    elif "Solo Bus" in transporte_sel:
        costo_transporte_unitario = 0
        transporte_tipo = "Solo Bus"
    elif "Sin Transporte" in transporte_sel:
        costo_transporte_unitario = 0
        transporte_tipo = "Sin Transporte"
    else:
        costo_transporte_unitario = 0
        transporte_tipo = "Bus Semi Cama"

    st.markdown("---")
    st.header("👤 Datos del Asesor y Oficina")
    agente_tel = st.text_input("Teléfono del Agente", value="351 505 2499")
    agente_email = st.text_input(
        "Email de Contacto", value="nicoguemanbreak@gmail.com")

    st.markdown("---")
    st.header("💵 Cotización Dólar")
    tipo_cambio = st.number_input(
        "Tipo de cambio ARS / USD (opcional)", min_value=0.0, value=1300.0, step=10.0)

# --- Información del destino seleccionado ---
info_dest = obtener_info_destino(destino)
puntos_fuertes_str = "\n".join(
    [f"- {pf}" for pf in info_dest["puntos_fuertes"]])

# --- Lógica de Precios ---
if destino in TARIFAS_PREDEFINIDAS:
    tarifas_dest = TARIFAS_PREDEFINIDAS[destino]

    # Para Canasvieiras: la tarifa base depende del tipo de alojamiento
    if destino == "Canasvieiras":
        if alojamiento_texto == "Posada VIP":
            tipo_base = "vip"
        else:
            # Posada Classic y Solo Alojamiento usan la tarifa Classic ($629)
            tipo_base = "classic"
    else:
        tipo_base = "doble" if cant_pasajeros == 2 else "individual"

    usd_base = tarifas_dest[tipo_base]["usd_promo"]
    usd_tachado_base = tarifas_dest[tipo_base]["usd_tachado"]
    ars_inscripcion = tarifas_dest["ars"]
    ars_tachado = tarifas_dest.get("ars_tachado", 310000)
    ars_bonificacion = tarifas_dest.get("ars_bonificacion", 100000)
else:
    usd_base = custom_usd_promo
    usd_tachado_base = custom_usd_tachado
    ars_inscripcion = custom_ars
    ars_tachado = 310000
    ars_bonificacion = 100000 if ars_tachado > ars_inscripcion else 0

# Recargo Base Doble Exclusiva: +100 USD por persona
recargo_doble_exclusiva = 100 if base_doble_exclusiva else 0

# Tarifa final por persona con recargos de comidas y transporte
usd_promo = usd_base + recargo_doble_exclusiva + \
    costo_comida_unitario + costo_transporte_unitario
usd_tachado = usd_tachado_base + recargo_doble_exclusiva + \
    costo_comida_unitario + costo_transporte_unitario

etiqueta_modalidad = f"(Base {cant_pasajeros} pax)" if cant_pasajeros > 1 else "(Individual)"
if base_doble_exclusiva:
    etiqueta_modalidad += " - Exclusivo"

precio_tachado_str = f"{usd_tachado} USD + inscripción ${ars_tachado:,}".replace(
    ",", ".")
precio_promo_str = f"{usd_promo} USD + inscripción ${ars_inscripcion:,} {etiqueta_modalidad}".replace(
    ",", ".").strip()

total_usd = usd_promo * cant_pasajeros
total_ars = ars_inscripcion * cant_pasajeros
total_grupo_str = f"{total_usd} USD + inscripción ${total_ars:,}".replace(
    ",", ".")

bloque_total_grupo = ""
if cant_pasajeros > 1:
    bloque_total_grupo = f"\n\n💵 *Total del paquete ({cant_pasajeros} pasajeros):*\n💳 *{total_grupo_str}*"

modalidad_str = f"Viaje {tipo_grupo.lower()}"
if cant_pasajeros > 1:
    modalidad_str += f" ({cant_pasajeros} pasajeros)"

# --- Ficha interna y conversión ---
conversion_info = "Sin cotización ingresada."
total_unitario_pesos = 0
total_grupo_pesos = 0
ars_pesos_usd_unitario = 0

if tipo_cambio > 0:
    ars_pesos_usd_unitario = usd_promo * tipo_cambio
    total_unitario_pesos = ars_pesos_usd_unitario + ars_inscripcion

    total_pesos_usd_grupo = total_usd * tipo_cambio
    total_grupo_pesos = total_pesos_usd_grupo + total_ars

    conversion_info = f"""
   • Tipo de cambio aplicado: $ {tipo_cambio:,.2f} ARS/USD
   • Por persona en ARS: ${total_unitario_pesos:,.0f} ARS (Tarifa: ${ars_pesos_usd_unitario:,.0f} + Inscripción: ${ars_inscripcion:,.0f})""".replace(",", ".")

    if cant_pasajeros > 1:
        conversion_info += f"""
   • Total grupo en ARS ({cant_pasajeros} pers): ${total_grupo_pesos:,.0f} ARS""".replace(",", ".")

# --- 1. MENSAJE PARA EL CLIENTE (Construcción 100% dinámica con parámetros oficiales) ---
mensaje_cliente = construir_mensaje_whatsapp(
    cliente=cliente,
    destino=destino,
    cant_pasajeros=cant_pasajeros,
    tipo_grupo=tipo_grupo,
    transporte_tipo=transporte_tipo,
    alojamiento_texto=alojamiento_texto,
    regimen_comida=regimen_nombre_limpio,
    costo_comida_unitario=costo_comida_unitario,
    precio_tachado_str=precio_tachado_str,
    precio_promo_str=precio_promo_str,
    total_grupo_str=total_grupo_str,
    rango_cronograma_o_mes=cronograma.get(
        'rango_total', '') if cronograma else '',
    puntos_fuertes=info_dest.get("puntos_fuertes", []),
    pais=info_dest.get("pais", "Brasil")
)

# --- 2. FICHA INTERNA ---
ficha_interna = f"""
============================================================
🚫 NO COPIAR A PARTIR DE ACÁ - FICHA DE CONTROL INTERNO 🚫
============================================================
👤 Cliente: {cliente}
📞 Contacto / WhatsApp: {telefono}
📍 Destino: {destino} ({info_dest['pais']})
👥 Pasajeros: {cant_pasajeros} ({tipo_grupo})
🚗 Transporte: {transporte_tipo} (+${costo_transporte_unitario} USD/pax)
🏨 Alojamiento: {alojamiento_texto}
🍽️ Régimen Comidas: {regimen_nombre_limpio} (+${costo_comida_unitario} USD/pax)
📅 Cronograma Total: {cronograma['rango_total']}
🏨 Estadía en Alojamiento: {cronograma['estadia_itinerario']}
🚌 Salida: {cronograma['salida_str']}
🔄 Regreso: {cronograma['checkout_str']}
💵 Cotización Final USD: {precio_promo_str}
🇦🇷 CONVERSIÓN EN PESOS ARS (Uso interno):{conversion_info}
============================================================
"""

contenido_archivo = mensaje_cliente + ficha_interna

# --- Generación del PDF de 5 Páginas Oficial de Break ---
pdf_bytes = generar_pdf_break(
    cliente=cliente if cliente else "Cliente",
    destino=destino,
    precio_usd=usd_promo,
    ars_inscripcion=ars_inscripcion,
    cronograma=cronograma,
    cant_pasajeros=cant_pasajeros,
    tipo_alojamiento=alojamiento_texto,
    regimen_comidas=regimen_nombre_limpio,
    tipo_transporte=transporte_tipo,
    agente_tel=agente_tel,
    agente_email=agente_email,
    base_doble_exclusiva=base_doble_exclusiva
)

cliente_slug = "".join(c for c in cliente if c.isalnum()
                       or c in (' ', '_', '-')).strip() or "cliente"
destino_slug = "".join(c for c in destino if c.isalnum()
                       or c in (' ', '_', '-')).strip() or "destino"
nombre_archivo_pdf = f"itinerario_break_{cliente_slug}_{destino_slug}.pdf".lower(
).replace(" ", "_")
nombre_archivo_propuesta = f"propuesta_{cliente_slug}_{destino_slug}.txt".lower(
).replace(" ", "_")

# --- Dashboard: Métricas principales ---
st.markdown("### 📊 Resumen de la Cotización")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric(
        label="Tarifa USD / persona",
        value=f"{usd_promo} USD",
        delta=f"-{usd_tachado - usd_promo} USD Promo"
    )

with col_m2:
    st.metric(
        label="Inscripción / persona",
        value=f"${ars_inscripcion:,.0f} ARS".replace(",", "."),
        delta=f"-${ars_bonificacion:,.0f} Bonif." if ars_bonificacion > 0 else None
    )

with col_m3:
    st.metric(
        label=f"Total Grupo USD ({cant_pasajeros} pax)",
        value=f"{total_usd:,} USD".replace(",", ".")
    )

with col_m4:
    if tipo_cambio > 0:
        st.metric(
            label="Total Grupo en ARS (est.)",
            value=f"${total_grupo_pesos:,.0f} ARS".replace(",", ".")
        )
    else:
        st.metric(
            label="Total Grupo en ARS",
            value="Sin tipo de cambio"
        )

st.markdown("---")

# --- Generación de Slugs para Keys Únicas de React / Streamlit ---
destino_slug = "".join(c for c in destino if c.isalnum()
                       or c in ('_', '-')).lower() or "destino"
transporte_slug = "".join(c for c in transporte_tipo if c.isalnum() or c in (
    '_', '-')).lower() or "transporte"
regimen_slug = "".join(c for c in regimen_nombre_limpio if c.isalnum(
) or c in ('_', '-')).lower() or "regimen"

# --- Sincronización dinámica de st.session_state ANTES de renderizar la UI de WhatsApp ---
wa_signature = f"{cliente}_{destino}_{cant_pasajeros}_{tipo_grupo}_{transporte_tipo}_{regimen_nombre_limpio}_{alojamiento_texto}_{total_usd}_{ars_inscripcion}"
wa_textarea_key = f"txt_wa_{destino_slug}_{cant_pasajeros}_{transporte_slug}_{regimen_slug}"

if st.session_state.get("wa_last_sig") != wa_signature:
    st.session_state["wa_last_sig"] = wa_signature
    st.session_state[wa_textarea_key] = mensaje_cliente
    st.session_state["txt_area_mensaje_cliente_wa"] = mensaje_cliente

# --- Tabs principales (Estructura estática de pestañas) ---
tab_whatsapp, tab_cronograma_view, tab_ficha, tab_exportar = st.tabs([
    "📱 Mensaje para WhatsApp",
    "🗓️ Cronograma Detallado",
    "💼 Ficha de Control Interno",
    "💾 Exportar y Guardar"
])

# TAB 1: WhatsApp
with tab_whatsapp:
    wa_container_key = f"box_wa_{destino_slug}_{cant_pasajeros}_{transporte_slug}_{regimen_slug}"
    with st.container(key=wa_container_key):
        st.markdown("#### Vista previa del mensaje listo para enviar")

        col_wa1, col_wa2 = st.columns([3, 1])

        with col_wa1:
            texto_wa_mostrado = st.text_area(
                "Mensaje formateado (copiar y pegar directamente en WhatsApp):",
                value=st.session_state.get(wa_textarea_key, mensaje_cliente),
                height=430,
                key=wa_textarea_key
            )
            # Mantener session_state sincronizado con las ediciones directas
            st.session_state["txt_area_mensaje_cliente_wa"] = texto_wa_mostrado

        with col_wa2:
            st.markdown("##### 🚀 Acciones Rápidas")

            # Enlace directo a WhatsApp si se introdujo número
            if telefono:
                telefono_limpio = "".join(filter(str.isdigit, telefono))
                texto_para_link = texto_wa_mostrado if texto_wa_mostrado else mensaje_cliente
                wa_encoded = urllib.parse.quote(texto_para_link)
                wa_link = f"https://api.whatsapp.com/send?phone={telefono_limpio}&text={wa_encoded}"
                st.link_button(
                    "📲 Abrir en WhatsApp con el mensaje",
                    wa_link,
                    use_container_width=True,
                    key=f"btn_link_wa_{destino_slug}_{transporte_slug}_{cant_pasajeros}"
                )
            else:
                st.info(
                    "💡 Agregá el número del cliente en la barra lateral para habilitar el botón de envío directo por WhatsApp."
                )

            # Botón para descargar PDF desde Acciones Rápidas
            st.download_button(
                label="Descargar Itinerario en PDF",
                data=pdf_bytes,
                file_name=nombre_archivo_pdf,
                mime="application/pdf",
                use_container_width=True,
                key=f"btn_pdf_acciones_rapidas_{destino_slug}_{transporte_slug}"
            )

            # Botón para registrar en historial
            if st.button("📌 Guardar en Historial de Sesión", use_container_width=True, key=f"btn_historial_{destino_slug}_{transporte_slug}_{cant_pasajeros}"):
                salida_crono = cronograma.get("salida_str", "").split(
                    " - ")[0] if cronograma else "Viernes"
                st.session_state["historial"].append({
                    "fecha": datetime.now().strftime("%H:%M:%S"),
                    "cliente": cliente or "Sin nombre",
                    "destino": destino or "Destino",
                    "salida": salida_crono,
                    "pasajeros": cant_pasajeros,
                    "total_usd": total_usd,
                    "total_ars": total_grupo_pesos
                })
                st.success("¡Cotización guardada en el historial!")

# TAB 2: Cronograma Detallado (Protegido con key dinámica de contenedor)
with tab_cronograma_view:
    crono_container_key = f"cronograma_{destino_slug}_{transporte_slug}"
    with st.container(key=crono_container_key):
        rango_crono_str = cronograma.get(
            'rango_total', '') if cronograma else ''
        st.markdown(
            f"#### 🗓️ Cronograma Oficial: {destino} ({rango_crono_str})")

        col_c1, col_c2 = st.columns(2)

        if transporte_tipo == "Aéreo Jetsmart Directo":
            f_checkin_str = cronograma.get(
                'checkin_str', '') if cronograma else ''
            f_checkout_str = cronograma.get('checkout_str', '').split(
                ' (')[0] if cronograma else ''
            estadia_str = cronograma.get(
                'estadia_itinerario', '') if cronograma else ''

            with col_c1:
                st.info(f"""
                **✈️ 1. Vuelo de Ida (Jetsmart Directo):**
                • Fecha: Domingo {f_checkin_str}
                • Horario: Salida 15:00 hs | Arribo a Floripa 18:00 hs (Duración 3 hs)
                • Incluye: Equipaje cabina hasta 10 kg + Traslado Aeropuerto - Alojamiento
                
                **🏨 2. Arribo y Check-in:**
                • Coordinación receptiva acompañando al grupo en destino.
                • Tarde y noche de bienvenida.
                """)
            with col_c2:
                st.success(f"""
                **🏖️ 3. Estadía en Alojamiento (7 Noches):**
                • Rango exacto: **{estadia_str}**
                • Alojamiento: {alojamiento_texto or 'No especificado'}
                • Régimen: {regimen_nombre_limpio or 'Sin régimen'}
                • Modalidad: Base {cant_pasajeros} pax
                
                **✈️ 4. Check-out y Vuelo de Regreso:**
                • Fecha: Domingo {f_checkout_str}
                • Horario: Salida 18:00 hs | Arribo a Córdoba 21:00 hs (Duración 3 hs)
                • Traslado interno hacia el Aeropuerto incluido.
                """)
        elif transporte_tipo == "Sin Transporte":
            f_checkin_str = cronograma.get(
                'checkin_str', '') if cronograma else ''
            f_checkout_str = cronograma.get('checkout_str', '').split(
                ' (')[0] if cronograma else ''
            estadia_str = cronograma.get(
                'estadia_itinerario', '') if cronograma else ''

            with col_c1:
                st.info(f"""
                **🚗 1. Llegada al Destino (Por cuenta propia):**
                • Modalidad: Sin transporte terrestre ni aéreo incluido.
                • Arribo sugerido: Domingo {f_checkin_str}.
                
                **🏨 2. Check-in en Alojamiento:**
                • Horario internacional: A partir de las 14:00 hs.
                • Entrega de llaves y recepción por staff de Break.
                """)
            with col_c2:
                st.success(f"""
                **🏖️ 3. Estadía en Alojamiento (7 Noches):**
                • Rango exacto: **{estadia_str}**
                • Alojamiento: {alojamiento_texto or 'No especificado'}
                • Régimen: {regimen_nombre_limpio or 'Sin régimen'}
                • Modalidad: Base {cant_pasajeros} pax
                
                **🔄 4. Check-out:**
                • Horario: Domingo {f_checkout_str} hasta las 10:00 hs.
                • Fin de servicios de hospedaje.
                """)
        else:
            f_salida_str = cronograma.get(
                'salida_str', '') if cronograma else ''
            f_checkin_str = cronograma.get(
                'checkin_str', '') if cronograma else ''
            f_checkout_str = cronograma.get(
                'checkout_str', '') if cronograma else ''
            f_arribo_str = cronograma.get(
                'arribo_str', '') if cronograma else ''
            estadia_str = cronograma.get(
                'estadia_itinerario', '') if cronograma else ''
            parada_detalle = info_dest.get(
                'parada_ruta_detalle', '') if info_dest else ''

            with col_c1:
                st.info(f"""
                **🚌 1. Salida en Bus Chárter ({transporte_tipo}):**
                • Fecha y hora: {f_salida_str}
                • Origen: Terminal de Córdoba (Plataformas 80 a 90)
                • Servicio y coordinación permanente a bordo.
                
                **🏨 2. Llegada y Check-in:**
                • Fecha: {f_checkin_str} (mediodía)
                • Entrega de habitaciones y tarde libre de playa.
                """)
            with col_c2:
                st.success(f"""
                **🏖️ 3. Estadía en Alojamiento (7 Noches):**
                • Rango exacto: **{estadia_str}**
                • Alojamiento: {alojamiento_texto or 'No especificado'}
                • Régimen: {regimen_nombre_limpio or 'Sin régimen'}
                • Modalidad: Base {cant_pasajeros} pax
                
                **🚌 4. Check-out y Regreso:**
                • Salida desde destino: {f_checkout_str}
                • Arribo a Córdoba: {f_arribo_str}
                """)
            if parada_detalle:
                st.info(f"**Parada de ruta destacada:** {parada_detalle}")

# TAB 3: Ficha Interna (Protegido con contenedor y dataframe con keys dinámicas)
with tab_ficha:
    ficha_container_key = f"desglose_{destino_slug}_{transporte_slug}_{regimen_slug}_{cant_pasajeros}"
    with st.container(key=ficha_container_key):
        st.markdown("#### Datos de Gestión y Conversión de Moneda")
        st.code(ficha_interna if ficha_interna is not None else "", language="text")

        if tipo_cambio and tipo_cambio > 0:
            st.markdown("##### 🔍 Desglose de Costos en ARS")
            concepto_inscripcion = (
                f"Inscripción en ARS (Lista ${ars_tachado:,.0f} - Bonif. ${ars_bonificacion:,.0f})".replace(
                    ",", ".")
                if ars_bonificacion and ars_bonificacion > 0 else "Inscripción en ARS"
            )

            conceptos = ["Tarifa Base (USD)"]
            montos_persona = [
                f"${usd_base * tipo_cambio:,.0f} ARS ({usd_base} USD)".replace(",", ".")]
            montos_grupo = [
                f"${usd_base * cant_pasajeros * tipo_cambio:,.0f} ARS ({usd_base * cant_pasajeros} USD)".replace(",", ".")]

            if costo_comida_unitario and costo_comida_unitario > 0:
                conceptos.append(f"Régimen: {regimen_nombre_limpio}")
                montos_persona.append(
                    f"${costo_comida_unitario * tipo_cambio:,.0f} ARS (+{costo_comida_unitario} USD)".replace(",", "."))
                montos_grupo.append(
                    f"${costo_comida_unitario * cant_pasajeros * tipo_cambio:,.0f} ARS (+{costo_comida_unitario * cant_pasajeros} USD)".replace(",", "."))

            if costo_transporte_unitario and costo_transporte_unitario > 0:
                conceptos.append(f"Suplemento Transporte: {transporte_tipo}")
                montos_persona.append(
                    f"${costo_transporte_unitario * tipo_cambio:,.0f} ARS (+{costo_transporte_unitario} USD)".replace(",", "."))
                montos_grupo.append(
                    f"${costo_transporte_unitario * cant_pasajeros * tipo_cambio:,.0f} ARS (+{costo_transporte_unitario * cant_pasajeros} USD)".replace(",", "."))

            conceptos.append(concepto_inscripcion)
            montos_persona.append(
                f"${ars_inscripcion:,.0f} ARS".replace(",", "."))
            montos_grupo.append(f"${total_ars:,.0f} ARS".replace(",", "."))

            conceptos.append("Total Paquete")
            montos_persona.append(
                f"${total_unitario_pesos:,.0f} ARS".replace(",", "."))
            montos_grupo.append(
                f"${total_grupo_pesos:,.0f} ARS".replace(",", "."))

            desglose_data = {
                "Concepto": conceptos,
                "Monto por Persona": montos_persona,
                f"Monto Total Grupo ({cant_pasajeros} pax)": montos_grupo
            }
            df_desglose = pd.DataFrame(desglose_data)
            df_desglose_key = f"df_table_{destino_slug}_{transporte_slug}_{regimen_slug}_{cant_pasajeros}"
            st.dataframe(
                df_desglose,
                use_container_width=True,
                hide_index=True,
                key=df_desglose_key
            )

# TAB 4: Guardar / Exportar
with tab_exportar:
    export_key = f"export_{destino_slug}_{transporte_slug}_{cant_pasajeros}"
    with st.container(key=export_key):
        st.markdown("#### Opciones de Descarga y Guardado")

        col_exp1, col_exp2, col_exp3 = st.columns(3)

        with col_exp1:
            st.download_button(
                label="Descargar Itinerario en PDF",
                data=pdf_bytes,
                file_name=nombre_archivo_pdf,
                mime="application/pdf",
                use_container_width=True,
                key=f"btn_pdf_tab_exportar_{destino_slug}_{transporte_slug}"
            )

        with col_exp2:
            st.download_button(
                label="📥 Descargar Propuesta (.txt)",
                data=contenido_archivo if contenido_archivo is not None else "",
                file_name=nombre_archivo_propuesta,
                mime="text/plain",
                use_container_width=True,
                key=f"btn_txt_propuesta_tab_exportar_{destino_slug}_{transporte_slug}"
            )

        with col_exp3:
            if st.button("📁 Guardar en 'Escritorio/Propuestas'", use_container_width=True, key=f"btn_guardar_carpeta_escritorio_{destino_slug}_{transporte_slug}"):
                try:
                    escritorio = os.path.join(
                        os.path.expanduser("~"), "Desktop")
                    carpeta_propuestas = os.path.join(escritorio, "Propuestas")
                    os.makedirs(carpeta_propuestas, exist_ok=True)
                    ruta_completa = os.path.join(
                        carpeta_propuestas, nombre_archivo_propuesta)

                    with open(ruta_completa, "w", encoding="utf-8") as f:
                        f.write(contenido_archivo)

                    st.success(
                        f"¡Guardado correctamente en:\n{ruta_completa}!")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# Historial de sesión si hay elementos
if st.session_state.get("historial"):
    st.markdown("---")
    st.markdown("### 🕒 Historial de Propuestas Generadas en esta Sesión")
    df_historial = pd.DataFrame(st.session_state["historial"])
    st.dataframe(df_historial, use_container_width=True,
                 hide_index=True, key="df_historial_sesion_table")
