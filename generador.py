import os
import sys
import subprocess
import urllib.parse

# Intentar importar pyperclip para copiar SOLO el mensaje del cliente
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

# Base de datos de tarifas por persona
TARIFAS = {
    "Canasvieiras": {
        # Posada Classic: $629 USD | Posada VIP: $699 USD
        "classic":    {"usd_promo": 629, "usd_tachado": 850},
        "vip":        {"usd_promo": 699, "usd_tachado": 950},
        "individual": {"usd_promo": 629, "usd_tachado": 850},
        "doble":      {"usd_promo": 629, "usd_tachado": 850},
        "ars": 210000
    },
    "Ferrugem": {
        "individual": {"usd_promo": 649, "usd_tachado": 750},
        "doble":      {"usd_promo": 649, "usd_tachado": 750},
        "ars": 210000
    },
    "Camboriú": {
        "individual": {"usd_promo": 640, "usd_tachado": 840},
        "doble":      {"usd_promo": 740, "usd_tachado": 940},
        "ars": 210000
    }
}


def obtener_precios(destino, cant_pasajeros, alojamiento_texto="Posada Classic"):
    ars_tachado = 310000
    ars_inscripcion = 210000

    if destino in TARIFAS:
        # Para Canasvieiras la tarifa base depende del tipo de alojamiento
        if destino == "Canasvieiras":
            if alojamiento_texto == "Posada VIP":
                tipo_base = "vip"
            else:
                tipo_base = "classic"
        else:
            tipo_base = "doble" if cant_pasajeros == 2 else "individual"

        usd_promo = TARIFAS[destino][tipo_base]["usd_promo"]
        usd_tachado = TARIFAS[destino][tipo_base]["usd_tachado"]
        ars_inscripcion = TARIFAS[destino]["ars"]
    else:
        print(f"\n⚠️  {destino} requiere tarifa personalizada.")
        usd_promo = int(
            input(f"Ingresá la tarifa en USD por persona para {destino}: ").strip())
        usd_tachado = usd_promo + 200

    etiqueta_modalidad = "(Base Doble)" if cant_pasajeros == 2 else ""

    precio_tachado_str = f"{usd_tachado} USD + inscripción ${ars_tachado:,}".replace(
        ",", ".")
    precio_promo_str = f"{usd_promo} USD + inscripción ${ars_inscripcion:,} {etiqueta_modalidad}".replace(
        ",", ".").strip()

    total_usd = usd_promo * cant_pasajeros
    total_ars = ars_inscripcion * cant_pasajeros
    total_grupo_str = f"{total_usd} USD + inscripción ${total_ars:,}".replace(
        ",", ".")

    return precio_tachado_str, precio_promo_str, total_grupo_str, usd_promo, ars_inscripcion, total_usd, total_ars


def generar_propuesta():
    print("=" * 55)
    print("   LE NICK CONNECT - GENERADOR INTEGRAL DE PROPUESTAS")
    print("=" * 55 + "\n")

    cliente = input("Nombre del cliente: ").strip()
    telefono = input("Teléfono/WhatsApp del cliente (para planilla): ").strip()

    # Selección de Destino
    print("\n--- Seleccioná el Destino ---")
    print("1. Canasvieiras\n2. Ferrugem\n3. Camboriú\n4. Praia do Rosa")
    opc_destino = input("Opción (1-4) o escribí otro: ").strip()
    destinos_map = {"1": "Canasvieiras", "2": "Ferrugem",
                    "3": "Camboriú", "4": "Praia do Rosa"}
    destino = destinos_map.get(opc_destino, opc_destino)

    # Selección de Tipo de Viaje
    print("\n--- Tipo de Viaje ---")
    print("1. Individual (1 pers.)\n2. Pareja (2 pers.)\n3. Dos amigos/as (2 pers.)\n4. Familiar / Grupal (Ingresar cantidad)")
    opc_grupo = input("Opción (1-4): ").strip()

    if opc_grupo == "1":
        tipo_grupo = "Individual"
        cant_pasajeros = 1
    elif opc_grupo == "2":
        tipo_grupo = "en Pareja"
        cant_pasajeros = 2
    elif opc_grupo == "3":
        tipo_grupo = "Doble (2 personas)"
        cant_pasajeros = 2
    else:
        tipo_grupo = "Familiar / Grupal"
        cant_input = input("¿Cuántos pasajeros son en total?: ").strip()
        cant_pasajeros = int(cant_input) if cant_input.isdigit() and int(
            cant_input) > 0 else 3

    # Selección de Alojamiento (únicamente 3)
    print("\n--- Tipo de Alojamiento ---")
    print("1. Posada Classic\n2. Posada VIP\n3. Solo Alojamiento")
    opc_aloj = input("Opción (1-3): ").strip()
    alojamientos = {
        "1": "Posada Classic",
        "2": "Posada VIP",
        "3": "Solo Alojamiento"
    }
    alojamiento_texto = alojamientos.get(opc_aloj, "Posada Classic")

    # Selector independiente de Régimen de Comidas
    print("\n--- Régimen de Comidas (por pasajero) ---")
    print("1. Sin régimen ($0 USD)\n2. Solo Desayuno (+$70 USD)\n3. Solo Cenas (+$100 USD)\n4. Media Pensión (Desayuno + Cena) (+$160 USD)")
    opc_comida = input("Opción (1-4): ").strip()
    comidas_map = {
        "1": ("Sin régimen", 0),
        "2": ("Solo Desayuno", 70),
        "3": ("Solo Cenas", 100),
        "4": ("Media Pensión (Desayuno + Cena)", 160)
    }
    regimen_comida, costo_comida_unitario = comidas_map.get(
        opc_comida, ("Sin régimen", 0))

    mes_viaje = input(
        "\nMes del viaje (ej: Diciembre / Enero / Marzo): ").strip()

    # Modalidad de Transporte
    print("\n--- Modalidad de Transporte ---")
    print("1. Bus Semi Cama (Incluido / Base)")
    print("2. Bus Cama (+$75 USD/pax)")
    print("3. Aéreo Jetsmart Directo (Ene/Feb +$385 USD/pax | Mar +$150 USD/pax)")
    print("4. Solo Bus (Venta exclusiva de transporte sin alojamiento)")
    print("5. Sin Transporte (Solo alojamiento)")
    opc_transp = input("Opción (1-5): ").strip()

    recargo_aereo = 150 if "marzo" in mes_viaje.lower(
    ) or "mar" in mes_viaje.lower() else 385
    transportes_map = {
        "1": ("Bus Semi Cama", 0),
        "2": ("Bus Cama", 75),
        "3": ("Aéreo Jetsmart Directo", recargo_aereo),
        "4": ("Solo Bus", 0),
        "5": ("Sin Transporte", 0)
    }
    transporte_tipo, costo_transporte_unitario = transportes_map.get(
        opc_transp, ("Bus Semi Cama", 0))

    # Cotización del Dólar del día
    tc_input = input(
        "\nTipo de cambio del día USD/ARS (Ej: 1300, o presiona Enter para omitir): ").strip()
    tipo_cambio = float(tc_input) if tc_input.replace(
        ".", "", 1).isdigit() else 0.0

    # Cálculo automático de precios con recargos de comidas y transporte
    precio_tachado, precio_promo, total_grupo, usd_unitario, ars_unitario, total_usd, total_ars = obtener_precios(
        destino, cant_pasajeros, alojamiento_texto)

    # Sumamos los costos unitarios adicionales
    usd_unitario += costo_comida_unitario + costo_transporte_unitario
    total_usd = usd_unitario * cant_pasajeros

    etiqueta_modalidad = "(Base Doble)" if cant_pasajeros == 2 else ""
    precio_promo = f"{usd_unitario} USD + inscripción ${ars_unitario:,} {etiqueta_modalidad}".replace(
        ",", ".").strip()
    total_grupo = f"{total_usd} USD + inscripción ${total_ars:,}".replace(
        ",", ".")

    bloque_total_grupo = ""
    if cant_pasajeros > 1:
        bloque_total_grupo = f"\n\n💵 *Total del paquete ({cant_pasajeros} pasajeros):*\n💳 *{total_grupo}*"

    modalidad_str = f"Viaje {tipo_grupo.lower()}"
    if cant_pasajeros > 1:
        modalidad_str += f" ({cant_pasajeros} pasajeros)"

    # CÁLCULOS EN PESOS PARA FICHA INTERNA
    conversion_info = "Sin cotización ingresada."
    if tipo_cambio > 0:
        ars_pesos_usd_unitario = usd_unitario * tipo_cambio
        total_unitario_pesos = ars_pesos_usd_unitario + ars_unitario

        total_pesos_usd_grupo = total_usd * tipo_cambio
        total_grupo_pesos = total_pesos_usd_grupo + total_ars

        conversion_info = f"""
   • Tipo de cambio aplicado: $ {tipo_cambio:,.2f} ARS/USD
   • Por persona en ARS: ${total_unitario_pesos:,.0f} ARS (Tarifa: ${ars_pesos_usd_unitario:,.0f} + Inscripción: ${ars_unitario:,.0f})""".replace(",", ".")

        if cant_pasajeros > 1:
            conversion_info += f"""
   • Total grupo en ARS ({cant_pasajeros} pers): ${total_grupo_pesos:,.0f} ARS""".replace(",", ".")

    # 1. MENSAJE PARA EL CLIENTE (100% en USD, limpio)
    if transporte_tipo == "Aéreo Jetsmart Directo":
        linea_transporte_wa = "✈️ Vuelo directo Jetsmart."
    elif transporte_tipo == "Sin Transporte":
        linea_transporte_wa = "🏨 Solo alojamiento (sin transporte)."
    else:
        linea_transporte_wa = f"🚌 Bus chárter directo ({transporte_tipo})."

    items_wa = []
    if transporte_tipo == "Aéreo Jetsmart Directo":
        items_wa.append("* Vuelo directo Jetsmart ida y vuelta")
        items_wa.append("* Equipaje de cabina hasta 10 kg")
        items_wa.append(
            "* Traslados internos aeropuerto - alojamiento - aeropuerto")
    elif transporte_tipo == "Sin Transporte":
        items_wa.append("* Recepción y entrega de llaves en destino")
    else:
        items_wa.append(f"* Bus ida y vuelta ({transporte_tipo})")
        items_wa.append("* Traslados")

    if transporte_tipo != "Solo Bus":
        items_wa.append(f"* {alojamiento_texto}")
        if costo_comida_unitario > 0:
            items_wa.append(f"* Régimen: {regimen_comida}")

    items_wa.append("* Coordinador")
    items_wa.append("* Seguros")
    items_wa.append("* Servicio en playa")
    items_wa.append("* Bienvenida al destino")

    bloque_incluye_wa = "\n".join(items_wa)

    mensaje_cliente = f"""¡Hola {cliente}! 👋 Te comparto un resumen de lo que incluye nuestra experiencia a {destino} para que no te quedes con dudas. 👇🏽

🇧🇷 Brasil 🌴 {destino} ☀️

- Playa tranquila.
- Zona céntrica y a metros del mar.
- Destino más elegido y completo.

Agencia operadora mayorista - Líder en turismo 🥇

📆 10 días y 7 noches ({mes_viaje})
- Modalidad: {modalidad_str}

{linea_transporte_wa}
💳 Cuotas fijas hasta la fecha. 

📍 {destino} 🌴 Precio por persona:

~{precio_tachado}~
🏷️ *{precio_promo}*{bloque_total_grupo}

🔥 *¡Precio de Lanzamiento! Sostenible con bonificación por cupos limitados.* ‼️

Incluye: 

{bloque_incluye_wa}

👉🏼 Reservando está semana te llevás de regalo una cena buffet despedida de Brasil . 📲"""

    # 2. FICHA DE CONTROL INTERNO Y CONVERSIÓN
    ficha_interna = f"""

============================================================
🚫 NO COPIAR A PARTIR DE ACÁ - FICHA DE CONTROL INTERNO 🚫
============================================================
👤 Cliente: {cliente}
📞 Contacto / WhatsApp: {telefono}
📍 Destino: {destino}
👥 Pasajeros: {cant_pasajeros} ({tipo_grupo})
🚗 Transporte: {transporte_tipo} (+${costo_transporte_unitario} USD/pax)
🏨 Alojamiento: {alojamiento_texto}
🍽️ Régimen Comidas: {regimen_comida} (+${costo_comida_unitario} USD/pax)
📅 Mes: {mes_viaje}
💵 Cotización Final USD: {precio_promo}
🇦🇷 CONVERSIÓN EN PESOS ARS (Uso interno):{conversion_info}
============================================================
"""

    # Texto completo para el archivo .txt
    contenido_archivo = mensaje_cliente + ficha_interna

    print("\n" + "="*55)
    print("         MENSAJE GENERADO PARA WHATSAPP")
    print("="*55 + "\n")
    print(mensaje_cliente)

    # Guardado en Escritorio
    try:
        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        carpeta_propuestas = os.path.join(escritorio, "Propuestas")
        os.makedirs(carpeta_propuestas, exist_ok=True)

        cliente_limpio = "".join(c for c in cliente if c.isalnum() or c in (
            ' ', '_', '-')).strip() or "cliente"
        destino_limpio = "".join(c for c in destino if c.isalnum() or c in (
            ' ', '_', '-')).strip() or "destino"
        nombre_archivo = f"propuesta_{cliente_limpio}_{destino_limpio}.txt".lower(
        ).replace(" ", "_")

        ruta_completa = os.path.join(carpeta_propuestas, nombre_archivo)

        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write(contenido_archivo)

        # Copiar al portapapeles ÚNICAMENTE el mensaje del cliente
        if HAS_PYPERCLIP:
            pyperclip.copy(mensaje_cliente)

        print("\n" + "="*55)
        print("✅ ¡ARCHIVO CREADO CON ÉXITO!")
        print(f"👉 Ubicación: {ruta_completa}")
        if HAS_PYPERCLIP:
            print("📋 ¡Mensaje del cliente copiado al portapapeles (sin datos internos)!")
        print("="*55)

        if sys.platform.startswith('win'):
            subprocess.Popen(['notepad.exe', ruta_completa])
        else:
            subprocess.Popen(['open', ruta_completa])

    except Exception as e:
        print(f"\n❌ Error al crear el archivo: {e}")

    input("\nPresioná ENTER para cerrar...")


if __name__ == "__main__":
    generar_propuesta()
