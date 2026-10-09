import os
import io
import urllib.parse
from datetime import datetime
import streamlit as st

# Importamos el generador de PDF y utilidades del cronograma y destinos
from pdf_generator_break import (
    generar_pdf_break,
    calcular_cronograma,
    obtener_info_destino,
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
    "Departamento completo. Estandar Break",
    "Posada con desayuno incluido",
    "Departamento equipado. Vip Break",
    "Incluir media pensión",
    "Alojamiento 7 noches"
]

# Inicializar historial en sesión
if "historial" not in st.session_state:
    st.session_state["historial"] = []

# --- Encabezado ---
st.title("🌴 Break Tienda de Viajes")
st.subheader("Generador Integral de Propuestas e Itinerarios Oficiales (5 Páginas)")

# --- Barra Lateral: Parámetros ---
with st.sidebar:
    st.header("📋 Datos del Cliente")
    cliente = st.text_input("Nombre del cliente", value="Oriana").strip()
    telefono = st.text_input("Teléfono / WhatsApp (ej: 5491112345678)", value="").strip()

    st.markdown("---")
    st.header("🏖️ Configuración del Paquete")

    # Selección de Destino
    opciones_destino = ["Canasvieiras", "Ferrugem", "Camboriú", "Praia do Rosa", "Otro personalizado..."]
    destino_seleccionado = st.selectbox("Destino", opciones_destino)

    if destino_seleccionado == "Otro personalizado...":
        destino = st.text_input("Nombre del destino personalizado", value="Florianópolis").strip()
        custom_usd_promo = st.number_input("Tarifa USD por persona", min_value=100, max_value=5000, value=629, step=10)
        custom_usd_tachado = custom_usd_promo + 200
        custom_ars = st.number_input("Inscripción en ARS por persona", min_value=0, max_value=2000000, value=210000, step=10000)
    elif destino_seleccionado == "Praia do Rosa":
        destino = "Praia do Rosa"
        custom_usd_promo = st.number_input("Tarifa USD por persona para Praia do Rosa", min_value=100, max_value=5000, value=680, step=10)
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
        st.caption(f"ℹ️ Ajustado al viernes de partida: **{cronograma['salida_str'].split(' - ')[0]}**")

    # Visualización resumida del cronograma en la barra lateral
    with st.expander("🗓️ Cronograma Calculado", expanded=True):
        st.markdown(f"🚌 **Salida:** {cronograma['salida_str']}")
        st.markdown(f"🏨 **Llegada / Check-in:** {cronograma['checkin_str']}")
        st.markdown(f"🏖️ **Estadía Alojamiento:** {cronograma['estadia_itinerario']}")
        st.markdown(f"🔄 **Check-out / Regreso:** {cronograma['checkout_str']}")
        st.markdown(f"🏁 **Arribo a Origen:** {cronograma['arribo_str']}")

    # Tipo de Viaje y Pasajeros
    tipo_viaje = st.selectbox(
        "Tipo de viaje",
        ["Familiar / Grupal", "En Pareja (2 personas)", "Dos amigos/as (2 personas)", "Individual (1 persona)"]
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
        cant_pasajeros = st.number_input("Cantidad total de pasajeros", min_value=1, max_value=60, value=5, step=1)
        tipo_grupo = "Familiar / Grupal"

    # Recargo Base Doble Exclusiva (solo para 2 pasajeros)
    base_doble_exclusiva = False
    if cant_pasajeros == 2:
        base_doble_exclusiva = st.checkbox(
            "🔒 Base Doble Exclusiva (+100 USD/persona)",
            help="Lugar exclusivo para 2 personas. Se suma un adicional de 100 USD por persona sobre la tarifa base."
        )
        if base_doble_exclusiva:
            st.caption("✅ Recargo aplicado: +100 USD por persona (lugar exclusivo para 2).")

    # Alojamiento
    alojamiento_sel = st.selectbox("Tipo de Alojamiento", OPCIONES_ALOJAMIENTO + ["Personalizado..."])
    if alojamiento_sel == "Personalizado...":
        alojamiento_texto = st.text_input("Descripción del alojamiento", value="Exclusivo con desayuno")
    else:
        alojamiento_texto = alojamiento_sel

    st.markdown("---")
    st.header("👤 Datos del Asesor y Oficina")
    agente_tel = st.text_input("Teléfono del Agente", value="351 505 2499")
    agente_email = st.text_input("Email de Contacto", value="nicoguemanbreak@gmail.com")

    st.markdown("---")
    st.header("💵 Cotización Dólar")
    tipo_cambio = st.number_input("Tipo de cambio ARS / USD (opcional)", min_value=0.0, value=1300.0, step=10.0)

# --- Información del destino seleccionado ---
info_dest = obtener_info_destino(destino)
puntos_fuertes_str = "\n".join([f"- {pf}" for pf in info_dest["puntos_fuertes"]])

# --- Lógica de Precios ---
if destino in TARIFAS_PREDEFINIDAS:
    tipo_base = "doble" if cant_pasajeros == 2 else "individual"
    usd_promo = TARIFAS_PREDEFINIDAS[destino][tipo_base]["usd_promo"]
    usd_tachado = TARIFAS_PREDEFINIDAS[destino][tipo_base]["usd_tachado"]
    ars_inscripcion = TARIFAS_PREDEFINIDAS[destino]["ars"]
else:
    usd_promo = custom_usd_promo
    usd_tachado = custom_usd_tachado
    ars_inscripcion = custom_ars

# Recargo Base Doble Exclusiva: +100 USD por persona
if base_doble_exclusiva:
    usd_promo += 100

etiqueta_modalidad = f"(Base {cant_pasajeros} pax)" if cant_pasajeros > 1 else "(Individual)"
if base_doble_exclusiva:
    etiqueta_modalidad += " - Exclusivo"

precio_tachado_str = f"{usd_tachado} USD + inscripción ${ars_inscripcion:,}".replace(",", ".")
precio_promo_str = f"{usd_promo} USD + inscripción ${ars_inscripcion:,} {etiqueta_modalidad}".replace(",", ".").strip()

total_usd = usd_promo * cant_pasajeros
total_ars = ars_inscripcion * cant_pasajeros
total_grupo_str = f"{total_usd} USD + inscripción ${total_ars:,}".replace(",", ".")

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

# --- 1. MENSAJE PARA EL CLIENTE (Adaptado dinámicamente según destino y cronograma) ---
nombre_mostrado = cliente if cliente else "!"
mensaje_cliente = f"""¡Hola {nombre_mostrado}! 👋 Te comparto un resumen de lo que incluye nuestra experiencia a {destino} para que no te quedes con dudas. 👇🏽

🇧🇷 {info_dest['pais']} 🌴 {destino} ☀️

{puntos_fuertes_str}

Agencia operadora mayorista - Líder en turismo 🥇

📆 10 días y 7 noches ({cronograma['rango_total']})
- Modalidad: {modalidad_str}

🚌 Bus chárter directo. 

⭐ Servicio privado y exclusivo.
⭐ Especialistas en el destino, con más de 10 años de trayectoria.
⭐ Salidas individuales y grupales.

🎁 Paquetes flexibles y personalizados.
💳 Cuotas fijas hasta la fecha. 

📍 {destino} 🌴 Precio por persona:

~{precio_tachado_str}~
🏷️ *{precio_promo_str}*{bloque_total_grupo}

🔥 *¡Precio de Lanzamiento! Sostenible con bonificación por cupos limitados.* ‼️

Incluye: 

* Bus ida y vuelta 
* Traslados
* {alojamiento_texto} 
* Coordinador
* Seguros 
* Servicio en playa 
* Bienvenida al destino 

👉🏼 *Reservando hoy te llevás de regalo la estadía para el verano 2028 y una bonificación de $100.000 en la reserva de tu viaje.* 📲

🌐 Conocé más fotos y detalles de la experiencia en nuestra web:
http://floripaconbreak.carrd.co/"""

# --- 2. FICHA INTERNA ---
ficha_interna = f"""
============================================================
🚫 NO COPIAR A PARTIR DE ACÁ - FICHA DE CONTROL INTERNO 🚫
============================================================
👤 Cliente: {cliente}
📞 Contacto / WhatsApp: {telefono}
📍 Destino: {destino} ({info_dest['pais']})
👥 Pasajeros: {cant_pasajeros} ({tipo_grupo})
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
    agente_tel=agente_tel,
    agente_email=agente_email,
    base_doble_exclusiva=base_doble_exclusiva
)

cliente_slug = "".join(c for c in cliente if c.isalnum() or c in (' ', '_', '-')).strip() or "cliente"
destino_slug = "".join(c for c in destino if c.isalnum() or c in (' ', '_', '-')).strip() or "destino"
nombre_archivo_pdf = f"itinerario_break_{cliente_slug}_{destino_slug}.pdf".lower().replace(" ", "_")
nombre_archivo_propuesta = f"propuesta_{cliente_slug}_{destino_slug}.txt".lower().replace(" ", "_")

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
        value=f"${ars_inscripcion:,.0f} ARS".replace(",", ".")
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

# --- Tabs principales ---
tab_whatsapp, tab_cronograma_view, tab_ficha, tab_exportar = st.tabs([
    "📱 Mensaje para WhatsApp",
    "🗓️ Cronograma Detallado",
    "💼 Ficha de Control Interno",
    "💾 Exportar y Guardar"
])

# TAB 1: WhatsApp
with tab_whatsapp:
    st.markdown("#### Vista previa del mensaje listo para enviar")
    
    col_wa1, col_wa2 = st.columns([3, 1])
    
    with col_wa1:
        st.text_area(
            "Mensaje formateado (copiar y pegar directamente en WhatsApp):",
            value=mensaje_cliente,
            height=430
        )

    with col_wa2:
        st.markdown("##### 🚀 Acciones Rápidas")
        
        # Enlace directo a WhatsApp si se introdujo número
        if telefono:
            telefono_limpio = "".join(filter(str.isdigit, telefono))
            wa_encoded = urllib.parse.quote(mensaje_cliente)
            wa_link = f"https://api.whatsapp.com/send?phone={telefono_limpio}&text={wa_encoded}"
            st.link_button("📲 Abrir en WhatsApp con el mensaje", wa_link, use_container_width=True)
        else:
            st.info("💡 Agregá el número del cliente en la barra lateral para habilitar el botón de envío directo por WhatsApp.")

        # Botón para descargar PDF desde Acciones Rápidas
        st.download_button(
            label="Descargar Itinerario en PDF",
            data=pdf_bytes,
            file_name=nombre_archivo_pdf,
            mime="application/pdf",
            use_container_width=True,
            key="btn_pdf_acciones_rapidas"
        )

        # Botón para registrar en historial
        if st.button("📌 Guardar en Historial de Sesión", use_container_width=True):
            st.session_state["historial"].append({
                "fecha": datetime.now().strftime("%H:%M:%S"),
                "cliente": cliente or "Sin nombre",
                "destino": destino,
                "salida": cronograma["salida_str"].split(" - ")[0],
                "pasajeros": cant_pasajeros,
                "total_usd": total_usd,
                "total_ars": total_grupo_pesos
            })
            st.success("¡Cotización guardada en el historial!")

# TAB 2: Cronograma Detallado
with tab_cronograma_view:
    st.markdown(f"#### 🗓️ Cronograma Oficial: {destino} ({cronograma['rango_total']})")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.info(f"""
        **1. Salida en Bus Chárter:**
        • Fecha y hora: {cronograma['salida_str']}
        • Origen: Terminal de Córdoba (Plataformas 80 a 90)
        • Servicio y coordinación permanente a bordo.
        
        **2. Llegada y Check-in:**
        • Fecha: {cronograma['checkin_str']} (mediodía)
        • Entrega de habitaciones y tarde libre de playa.
        """)
    with col_c2:
        st.success(f"""
        **3. Estadía en Alojamiento (7 Noches):**
        • Rango exacto: **{cronograma['estadia_itinerario']}**
        • Alojamiento: {alojamiento_texto}
        • Modalidad: Base {cant_pasajeros} pax
        
        **4. Check-out y Regreso:**
        • Salida desde destino: {cronograma['checkout_str']}
        • Arribo a Córdoba: {cronograma['arribo_str']}
        """)
    
    st.markdown(f"**Parada de ruta destacada:** {info_dest['parada_ruta_detalle']}")

# TAB 3: Ficha Interna
with tab_ficha:
    st.markdown("#### Datos de Gestión y Conversión de Moneda")
    st.code(ficha_interna, language="text")
    
    if tipo_cambio > 0:
        st.markdown("##### 🔍 Desglose de Costos en ARS")
        desglose_data = {
            "Concepto": ["Tarifa Base (USD)", "Inscripción en ARS", "Total por persona", "Total Todo el Grupo"],
            "Monto por Persona": [
                f"${ars_pesos_usd_unitario:,.0f} ARS".replace(",", "."),
                f"${ars_inscripcion:,.0f} ARS".replace(",", "."),
                f"${total_unitario_pesos:,.0f} ARS".replace(",", "."),
                "-"
            ],
            f"Monto Total Grupo ({cant_pasajeros} pax)": [
                f"${total_usd * tipo_cambio:,.0f} ARS".replace(",", "."),
                f"${total_ars:,.0f} ARS".replace(",", "."),
                "-",
                f"${total_grupo_pesos:,.0f} ARS".replace(",", ".")
            ]
        }
        st.table(desglose_data)

# TAB 4: Guardar / Exportar
with tab_exportar:
    st.markdown("#### Opciones de Descarga y Guardado")
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)

    with col_exp1:
        st.download_button(
            label="Descargar Itinerario en PDF",
            data=pdf_bytes,
            file_name=nombre_archivo_pdf,
            mime="application/pdf",
            use_container_width=True,
            key="btn_pdf_tab_exportar"
        )

    with col_exp2:
        st.download_button(
            label="📥 Descargar Propuesta (.txt)",
            data=contenido_archivo,
            file_name=nombre_archivo_propuesta,
            mime="text/plain",
            use_container_width=True
        )

    with col_exp3:
        if st.button("📁 Guardar en 'Escritorio/Propuestas'", use_container_width=True):
            try:
                escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
                carpeta_propuestas = os.path.join(escritorio, "Propuestas")
                os.makedirs(carpeta_propuestas, exist_ok=True)
                ruta_completa = os.path.join(carpeta_propuestas, nombre_archivo_propuesta)

                with open(ruta_completa, "w", encoding="utf-8") as f:
                    f.write(contenido_archivo)

                st.success(f"¡Guardado correctamente en:\n{ruta_completa}!")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# Historial de sesión si hay elementos
if st.session_state["historial"]:
    st.markdown("---")
    st.markdown("### 🕒 Historial de Propuestas Generadas en esta Sesión")
    st.dataframe(st.session_state["historial"], use_container_width=True)
