import os
import io
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image

PAGE_WIDTH = 842.25
PAGE_HEIGHT = 1190.25
ASSETS_DIR = os.path.join(os.path.dirname(
    __file__), "assets") if "__file__" in locals() else "assets"

# Diccionario de información turística y rutas por destino
DATOS_DESTINOS = {
    "Canasvieiras": {
        "pais": "Brasil",
        "puntos_fuertes": [
            "Playa tranquila y aguas calmas.",
            "Zona céntrica y a metros del mar.",
            "Destino más elegido y completo."
        ],
        "parada_ruta": "Graal Baleia",
        "parada_ruta_detalle": "Domingo en la mañana parada en Graal Baleia previo a Canasvieiras",
        "resena": (
            "Canasvieiras es uno de los destinos más elegidos y vibrantes del sur de Brasil, "
            "ubicado en la parte norte de la isla de Santa Catarina. Se caracteriza por sus aguas cálidas, "
            "calmas y cristalinas, ideales para el descanso y el disfrute en familia o amigos.<br/><br/>"
            "Durante la temporada estival, ofrece una vibrante vida comercial y gastronómica a pasos del mar, "
            "con una completa infraestructura que garantiza comodidad, seguridad y servicios médicos permanentes."
        )
    },
    "Ferrugem": {
        "pais": "Brasil",
        "puntos_fuertes": [
            "Capital del surf y de la juventud.",
            "Playas agrestes, canales naturales y lagunas.",
            "Incomparable movida nocturna y atardeceres mágicos."
        ],
        "parada_ruta": "Graal Garopaba",
        "parada_ruta_detalle": "Domingo en la mañana parada en Graal Garopaba previo a Ferrugem",
        "resena": (
            "Ferrugem es una de las playas más emblemáticas de Garopaba, en el litoral sur de Santa Catarina. "
            "Famosa por su mística bohemia, su canal de agua dulce que desemboca en el mar y olas reconocidas "
            "a nivel internacional, es el punto de encuentro predilecto de jóvenes y grupos de amigos.<br/><br/>"
            "Su pintoresca calle principal ofrece bares rústicos, música en vivo y una gastronomía diversa "
            "en un entorno natural protegido e inigualable."
        )
    },
    "Camboriú": {
        "pais": "Brasil",
        "puntos_fuertes": [
            "La 'Dubai de Sudamérica' con imponente costanera.",
            "Teleférico Parque Unipraias y rueda gigante FG Big Wheel.",
            "La mayor infraestructura gastronómica, comercial y nocturna del sur de Brasil."
        ],
        "parada_ruta": "Parador Acceso Camboriú",
        "parada_ruta_detalle": "Domingo en la mañana parada en parador oficial previo al ingreso a Camboriú",
        "resena": (
            "Balneario Camboriú es la capital del turismo cosmopolita del sur de Brasil. "
            "Conocido por su moderna avenida costanera iluminada, sus imponentes rascacielos frente a la playa "
            "y atracciones únicas como el teleférico del Parque Unipraias y la rueda gigante FG Big Wheel.<br/><br/>"
            "Combina días de sol en playas paradisíacas como Laranjeiras con una oferta comercial y vida nocturna "
            "de primer nivel las 24 horas del día."
        )
    },
    "Praia do Rosa": {
        "pais": "Brasil",
        "puntos_fuertes": [
            "Bahía natural de ensueño en forma de media luna.",
            "Morros cubiertos de selva atlántica y lagunas cristalinas.",
            "Ambiente exclusivo, posadas rústicas y gastronomía de autor."
        ],
        "parada_ruta": "Parador Imbituba",
        "parada_ruta_detalle": "Domingo en la mañana parada en parador de Imbituba previo a Praia do Rosa",
        "resena": (
            "Praia do Rosa es considerada una de las bahías más hermosas de Brasil y del mundo. "
            "Rodeada de imponentes morros verdes y lagunas naturales, ofrece un ambiente donde la preservación "
            "ecológica convive con un estilo rústico y exclusivo.<br/><br/>"
            "El 'Centrinho' del Rosa deslumbra con restaurantes gourmet, tiendas de diseño y atardeceres "
            "soñados que convocan a quienes buscan relax, naturaleza y buena compañía."
        )
    }
}


def obtener_info_destino(destino):
    """Devuelve la información turística y paradas de ruta de un destino."""
    if destino in DATOS_DESTINOS:
        return DATOS_DESTINOS[destino]
    return {
        "pais": "Brasil",
        "puntos_fuertes": [
            "Playas cálidas y arena blanca.",
            "Zona céntrica y cercana a los principales paseos.",
            "Servicio privado y exclusivo con coordinación."
        ],
        "parada_ruta": "Parador Oficial en Ruta",
        "parada_ruta_detalle": f"Domingo en la mañana parada técnica en parador oficial previo al arribo a {destino}",
        "resena": (
            f"{destino} es un destino turístico destacado de Brasil, reconocido por sus paisajes naturales "
            "y su clima estival. Ofrece excelentes alternativas recreativas, comercios y espacios gastronómicos "
            "para vivir unas vacaciones inolvidables.<br/><br/>"
            "Cuenta con todo el respaldo, infraestructura y asistencia técnica de nuestro equipo para asegurar "
            "una experiencia placentera y segura."
        )
    }


def obtener_alojamientos_destino(destino, precio_usd, base_doble_exclusiva=False):
    """
    Devuelve la estructura de alojamientos dinámica según las reglas de negocio para la Página 4:
    - Canasvieiras: 10 Complejos Exclusivos (Categorías Standard y VIP)
    - Ferrugem: 6 Posadas Seleccionadas (Belleza Pura, Territorio da Paz, Barbarana, Recanto, Pantai, Vila da Ferrugem)
    - Praia do Rosa: Complejos Seleccionados (Departamentos Break, In Box, Prazeres do Rosa)
    """
    # Precio VIP base fijo (Canasvieiras); se suma +100 si hay recargo por base doble exclusiva
    precio_vip_base = 699
    precio_vip = precio_vip_base + (100 if base_doble_exclusiva else 0)

    if destino == "Canasvieiras":
        return {
            "encabezado": "10 COMPLEJOS EXCLUSIVOS",
            "items_generales": [
                "Departamentos y Aparts privados solo para pasajeros de Break Tienda de viajes",
                "Zona céntrica",
                "A metros del mar",
                "Equipados completos",
                "Recepción y seguridad privada",
                "Wifi"
            ],
            "secciones": [
                {
                    "titulo": f"ALOJAMIENTOS VIP - Alecrim | Casa da Praia | Jureré | Ilha Sul - Desde {precio_vip} UsD",
                    "items": [
                        "Disponen de pileta privada, playroom y solarium",
                        "Mejor ubicación céntrica y zona privilegiada",
                        "Recepcion 24 horas",
                        "Habitaciones en base Doble | Triple | Cuádruple",
                        "Como opcional se puede agregar servicio de desayunos",
                        "Incluye ropa de cama."
                    ]
                },
                {
                    "titulo": f"ALOJAMIENTOS STANDARD - Beach House | Taua | Arvoredo | Valparaiso - Desde {precio_usd} UsD",
                    "items": [
                        "Equipados completos",
                        "Recepcion e ingreso con codigo de seguridad",
                        "Habitaciones en base Doble | Triple | Cuádruple | Quintuple | Sextuple",
                        "Excelente ubicación en zona céntrica de comercios y a metros del mar"
                    ]
                }
            ]
        }
    elif destino == "Ferrugem":
        return {
            "encabezado": "6 POSADAS SELECCIONADAS",
            "items_generales": [
                "Belleza Pura | Territorio da Paz | Barbarana | Recanto | Pantai | Vila da Ferrugem",
                "Posadas completas. Habitaciones con baño privado, además tienen playroom, solarium, pileta y cocina compartida.",
                "Excelente ubicación a metros de la playa y el centro de Garopaba",
                "Espacios verdes, comodidad y seguridad para grupos y parejas",
                "Recepción y coordinación permanente",
                "Wifi"
            ],
            "secciones": [
                {
                    "titulo": "COMODIDADES & SERVICIOS EXCLUSIVOS EN FERRUGEM",
                    "items": [
                        "Ingreso coordinado con el staff de Break.",
                        "Habitaciones en base Doble | Triple | Cuádruple | Quíntuple con baño privado.",
                        "Zona privilegiada a metros de los principales paradores y la playa.",
                        "Cocina compartida totalmente equipada para mayor comodidad y ahorro.",
                        "Parrillas, áreas de descanso, playroom, pileta y solarium común.",
                        "Espacios de esparcimiento ideales para grupos y parejas.",
                        "Seguridad y custodia durante toda la estadía.",
                        "Incluye ropa de cama y servicio de recepción."
                    ]
                }
            ]
        }
    elif destino == "Praia do Rosa":
        return {
            "encabezado": "COMPLEJOS SELECCIONADOS",
            "items_generales": [
                "Departamentos Break | In Box | Prazeres do Rosa",
                "Departamentos y aparts privados con equipamiento completo",
                "Ubicación privilegiada cercana al Centrinho y a los accesos de la playa",
                "Entornos naturales preservados con solarium y áreas de relax",
                "Recepción, seguridad privada y atención del staff",
                "Wifi"
            ],
            "secciones": [
                {
                    "titulo": "COMODIDADES EXCLUSIVAS DEL ROSA",
                    "items": [
                        "Departamentos privados con cocina completa, vajilla y comodidades.",
                        "Habitaciones en base Doble | Triple | Cuádruple con baño privado.",
                        "Vistas panorámicas a los morros y áreas verdes.",
                        "Espacios de solarium, terrazas y decks privados.",
                        "Cercanía a los mejores restaurantes y bares del Centrinho.",
                        "Parrillas individuales y compartidas.",
                        "Estacionamiento privado dentro del predio.",
                        "Atención permanente del equipo de Break en destino.",
                        "Incluye ropa de cama y servicio de recepción."
                    ]
                }
            ]
        }
    else:
        # Fallback genérico para otros destinos
        return {
            "encabezado": "COMPLEJOS Y HOTELES SELECCIONADOS",
            "items_generales": [
                f"Departamentos y hoteles seleccionados para pasajeros de Break en {destino}",
                "Zona céntrica y de fácil acceso a la playa",
                "Habitaciones y departamentos totalmente equipados",
                "Recepción, seguridad privada y Wifi",
                "Coordinación y asistencia médica 24 hs"
            ],
            "secciones": [
                {
                    "titulo": f"ALOJAMIENTOS EN {destino.upper()} - Desde {precio_usd} UsD",
                    "items": [
                        "Equipados completos con baño privado y comodidades.",
                        "Habitaciones en base Doble | Triple | Cuádruple | Grupal.",
                        "Excelente ubicación comercial y gastronómica.",
                        "Incluye ropa de cama y asistencia del staff."
                    ]
                }
            ]
        }


def calcular_cronograma(fecha_viernes):
    """
    Calcula de manera exacta y automática el cronograma partiendo de un Viernes de salida:
    - Salida: Viernes noche (23:00 hs)
    - Llegada / Check-in: Domingo mediodía (2 días después)
    - Estadía: Rango de Domingo a Domingo (7 noches)
    - Check-out / Regreso: Domingo por la tarde
    - Arribo a Origen: Lunes tarde/noche (10 días después de salir)
    """
    if isinstance(fecha_viernes, datetime.datetime):
        fecha_viernes = fecha_viernes.date()

    if fecha_viernes.weekday() != 4:
        dias_dif = (4 - fecha_viernes.weekday()) % 7
        if dias_dif == 0:
            dias_dif = 7
        fecha_viernes = fecha_viernes + datetime.timedelta(days=dias_dif)

    f_salida = fecha_viernes                             # Viernes
    f_checkin = f_salida + datetime.timedelta(days=2)    # Domingo
    # Domingo siguiente (7 noches)
    f_checkout = f_checkin + datetime.timedelta(days=7)
    f_arribo = f_salida + datetime.timedelta(days=10)    # Lunes

    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    dias = {
        0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
        4: "Viernes", 5: "Sábado", 6: "Domingo"
    }

    def formatear(d, incluir_dia=True, incluir_anio=True):
        prefijo_dia = f"{dias[d.weekday()]} " if incluir_dia else ""
        mes = meses[d.month]
        anio = f" {d.year}" if incluir_anio else ""
        return f"{prefijo_dia}{d.day:02d} {mes}{anio}"

    salida_str = f"{formatear(f_salida)} - 23:00 horas"
    checkin_str = f"{formatear(f_checkin)}"
    checkout_str = f"{formatear(f_checkout)} (tarde)"
    arribo_str = f"{formatear(f_arribo)} (tarde)"

    # Formato explícito requerido para la página 2:
    estadia_itinerario = f"{formatear(f_checkin, incluir_dia=True, incluir_anio=False)} a {formatear(f_checkout, incluir_dia=True, incluir_anio=False)} - 7 noches"

    # Rango total para portada y encabezados:
    rango_total = f"{f_salida.day:02d} {meses[f_salida.month]} {f_salida.year} - {f_arribo.day:02d} {meses[f_arribo.month]} {f_arribo.year}"

    return {
        "fecha_salida": f_salida,
        "salida_str": salida_str,
        "checkin_str": checkin_str,
        "checkout_str": checkout_str,
        "arribo_str": arribo_str,
        "dia_llegada_nombre": dias[f_arribo.weekday()],
        "arribo_fecha_str": f"{dias[f_arribo.weekday()]} {f_arribo.day:02d} de {meses[f_arribo.month].capitalize()}",
        "estadia_itinerario": estadia_itinerario,
        "rango_total": rango_total,
        "mes_nombre": meses[f_salida.month].capitalize()
    }


def construir_mensaje_whatsapp(
    cliente: str,
    destino: str,
    cant_pasajeros: int = 1,
    tipo_grupo: str = "Individual",
    transporte_tipo: str = "Bus Semi Cama",
    alojamiento_texto: str = "Posada Classic",
    regimen_comida: str = "Sin régimen",
    costo_comida_unitario: int = 0,
    precio_tachado_str: str = "",
    precio_promo_str: str = "",
    total_grupo_str: str = "",
    rango_cronograma_o_mes: str = "",
    puntos_fuertes: list = None,
    pais: str = "Brasil"
) -> str:
    """
    Construye de manera 100% dinámica el mensaje de WhatsApp para el cliente,
    utilizando todos los parámetros seleccionados (destino, pasajeros, transporte, comidas, precios).
    """
    nombre_mostrado = cliente.strip() if cliente and cliente.strip() else "!"

    # Puntos fuertes del destino
    if not puntos_fuertes:
        info = obtener_info_destino(destino)
        puntos_fuertes = info.get("puntos_fuertes", [])
        pais = info.get("pais", pais)

    puntos_fuertes_str = "\n".join([f"- {pf}" for pf in puntos_fuertes])

    # Modalidad
    modalidad_str = f"Viaje {tipo_grupo.lower()}"
    if cant_pasajeros > 1:
        modalidad_str += f" ({cant_pasajeros} pasajeros)"

    # Línea de transporte
    if transporte_tipo == "Aéreo Jetsmart Directo":
        linea_transporte_wa = "✈️ Vuelo directo Jetsmart."
    elif transporte_tipo == "Sin Transporte":
        linea_transporte_wa = "🏨 Solo alojamiento (sin transporte)."
    else:
        linea_transporte_wa = f"🚌 Bus chárter directo ({transporte_tipo})."

    # Bloque de items incluidos
    items_wa = []
    if transporte_tipo == "Aéreo Jetsmart Directo":
        items_wa.append("* Vuelo directo Jetsmart ida y vuelta")
        items_wa.append("* Equipaje de cabina hasta 10 kg")
        items_wa.append("* Traslados internos aeropuerto - alojamiento - aeropuerto")
    elif transporte_tipo == "Sin Transporte":
        items_wa.append("* Recepción y asistencia personalizada en destino")
    else:
        items_wa.append(f"* Bus ida y vuelta ({transporte_tipo})")
        items_wa.append("* Traslados")

    if transporte_tipo != "Solo Bus":
        items_wa.append(f"* {alojamiento_texto}")
        regimen_limpio = regimen_comida.split(" (")[0].strip()
        if costo_comida_unitario > 0 or (regimen_limpio and regimen_limpio != "Sin régimen"):
            items_wa.append(f"* Régimen: {regimen_limpio}")

    items_wa.append("* Coordinador")
    items_wa.append("* Seguros")
    items_wa.append("* Servicio en playa")
    items_wa.append("* Bienvenida al destino")

    bloque_incluye_wa = "\n".join(items_wa)

    # Bloque total grupo
    bloque_total_grupo = ""
    if cant_pasajeros > 1 and total_grupo_str:
        bloque_total_grupo = f"\n\n💵 *Total del paquete ({cant_pasajeros} pasajeros):*\n💳 *{total_grupo_str}*"

    # Duración / Cronograma
    duracion_str = f"📆 10 días y 7 noches ({rango_cronograma_o_mes})" if rango_cronograma_o_mes else "📆 10 días y 7 noches"

    mensaje = f"""¡Hola {nombre_mostrado}! 👋 Te comparto un resumen de lo que incluye nuestra experiencia a {destino} para que no te quedes con dudas. 👇🏽

🇧🇷 {pais} 🌴 {destino} ☀️

{puntos_fuertes_str}

Agencia operadora mayorista - Líder en turismo 🥇

{duracion_str}
- Modalidad: {modalidad_str}

{linea_transporte_wa}
💳 Cuotas fijas hasta la fecha. 

📍 {destino} 🌴 Precio por persona:

~{precio_tachado_str}~
🏷️ *{precio_promo_str}*{bloque_total_grupo}

🔥 *¡Precio de Lanzamiento! Sostenible con bonificación por cupos limitados.* ‼️

Incluye: 

{bloque_incluye_wa}

👉🏼 Reservando está semana te llevás de regalo una cena buffet despedida de Brasil . 📲"""

    return mensaje


def obtener_nombre_base(cant_pasajeros, base_doble_exclusiva=False):
    if cant_pasajeros == 2 and base_doble_exclusiva:
        return "Base doble exclusiva"
    nombres = {
        1: "Base individual",
        2: "Base doble",
        3: "Base triple",
        4: "Base cuádruple",
        5: "Base quíntuple",
        6: "Base séxtuple"
    }
    return nombres.get(cant_pasajeros, f"Base {cant_pasajeros} personas")


def draw_pin_icon(c, x, y, size=16, color=colors.HexColor("#1A1A1A")):
    c.saveState()
    c.setFillColor(color)
    c.circle(x, y + size * 0.45, size * 0.42, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(x - size * 0.38, y + size * 0.35)
    p.lineTo(x + size * 0.38, y + size * 0.35)
    p.lineTo(x, y - size * 0.4)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.circle(x, y + size * 0.45, size * 0.16, stroke=0, fill=1)
    c.restoreState()


def draw_footer(c):
    c.saveState()
    logo_path = os.path.join(ASSETS_DIR, "logo_break.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 650, 42, width=115, height=44,
                    preserveAspectRatio=True, mask='auto')

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawRightString(
        765, 30, "Tucuman 219, primer piso. Edificio Proa. Oficina Córdoba")
    c.restoreState()


def draw_paragraph(c, text, x, y, width, font_name="Helvetica", font_size=11, leading=15, text_color=colors.HexColor("#333333")):
    style = ParagraphStyle(
        name=f"Style_{x}_{y}_{font_size}",
        fontName=font_name,
        fontSize=font_size,
        leading=leading,
        textColor=text_color
    )
    p = Paragraph(text, style)
    w, h = p.wrap(width, 1000)
    p.drawOn(c, x, y - h)
    return h


def generar_pdf_break(
    cliente="LeNick",
    destino="Canasvieiras",
    precio_usd=629,
    ars_inscripcion=210000,
    cronograma=None,
    cant_pasajeros=5,
    base_doble_exclusiva=False,
    tipo_alojamiento="Posada Classic",
    regimen_comidas="Sin régimen",
    tipo_transporte="Bus Semi Cama",
    fecha_cotizacion=None,
    agente_tel="351 505 2499",
    agente_email="nicoguemanbreak@gmail.com",
    lugar_salida="Terminal de Córdoba",
    plataforma="80 a 90 - 22:00 horas",
    **kwargs
):
    if not fecha_cotizacion:
        fecha_cotizacion = datetime.datetime.now().strftime("%d %B %Y").upper()

    if cronograma is None:
        cronograma = calcular_cronograma(datetime.date(2027, 1, 22))

    info_dest = obtener_info_destino(destino)
    aloj_info = obtener_alojamientos_destino(
        destino, precio_usd, base_doble_exclusiva=base_doble_exclusiva)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    usd_str = f"U$S {precio_usd}"
    ars_str = f"+ $ {ars_inscripcion:,} por persona".replace(",", ".")
    base_str = obtener_nombre_base(cant_pasajeros, base_doble_exclusiva)

    # Identificación de modalidad de transporte
    es_aereo = "Aéreo" in tipo_transporte or "Jetsmart" in tipo_transporte
    es_sin_transporte = "Sin Transporte" in tipo_transporte
    es_solo_bus = "Solo Bus" in tipo_transporte

    # Texto de régimen de comidas si aplica
    texto_comidas_aloj = f" | Régimen: {regimen_comidas}" if regimen_comidas and "Sin régimen" not in regimen_comidas else ""

    # =========================================================================
    # PÁGINA 1: PORTADA & RESUMEN DE TARIFA DESTACADA
    # =========================================================================
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(70, 1120, f"FECHA COTIZACIÓN: {fecha_cotizacion}")
    c.drawRightString(765, 1120, f"AGENTE : {agente_tel}")

    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(70, 1070, "SU VIAJE A")

    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 1025, f"{destino}, {info_dest['pais']}")

    hero_path = os.path.join(ASSETS_DIR, "hero_p1.png")
    if os.path.exists(hero_path):
        c.drawImage(hero_path, 70, 500, width=695,
                    height=480, preserveAspectRatio=True)

    y_tarifa_top = 460
    y_tarifa_bottom = 350

    c.setStrokeColor(colors.HexColor("#1A1A1A"))
    c.setLineWidth(1)
    c.line(315, y_tarifa_top, 315, y_tarifa_bottom)
    c.line(510, y_tarifa_top, 510, y_tarifa_bottom)

    # Columna 1: Presupuesto y Fecha
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 445, "PRESUPUESTO PARA SU VIAJE")

    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawString(70, 425, f"En base a {cant_pasajeros} adultos ({base_str})")

    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 385, "FECHA DE VIAJE")

    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawString(70, 365, cronograma['rango_total'])

    # Columna 2: Precios destacados (Únicamente costo total final limpio)
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(340, 420, usd_str)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(340, 395, ars_str)

    # Columna 3: Contacto
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(530, 445, "CONTACTO")

    c.setFont("Helvetica", 10.5)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawString(530, 425, agente_email)
    c.drawString(530, 405, "floripaconbreak.carrd.co")
    c.drawString(530, 385, agente_tel)

    # Glosario dinámico
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 240, "GLOSARIO")

    def draw_check_item(c, x, y, label):
        c.setStrokeColor(colors.HexColor("#333333"))
        c.setLineWidth(1)
        c.rect(x, y, 9, 9, stroke=1, fill=0)
        c.setFont("Helvetica", 10.5)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(x + 16, y, label)

    draw_check_item(c, 70, 210, "1 Destino")
    if not es_sin_transporte:
        etiqueta_t = "1 Vuelo Directo" if es_aereo else "1 Transporte"
        draw_check_item(c, 70, 190, etiqueta_t)
    else:
        draw_check_item(c, 70, 190, "Sin Transporte")
    draw_check_item(c, 175, 210, "1 Seguro")
    if not es_solo_bus:
        draw_check_item(c, 175, 190, "1 Alojamiento")
        draw_check_item(c, 175, 170, "7 Noches")
    else:
        draw_check_item(c, 175, 190, "Solo Bus")

    draw_footer(c)
    c.showPage()

    # =========================================================================
    # PÁGINA 2: ITINERARIO DETALLADO POR MODALIDAD DE TRANSPORTE
    # =========================================================================
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 1100, "Itinerario")

    c.setStrokeColor(colors.HexColor("#E0E0E0"))
    c.setLineWidth(1)
    c.line(70, 1060, 240, 1060)

    if es_aereo:
        # ---------------------------------------------------------------------
        # MODALIDAD B: AÉREO JETSMART DIRECTO (EXCLUSIVO)
        # ---------------------------------------------------------------------
        # Paso 1: Vuelo de Ida
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(70, 1010, "Inicio del viaje - Vuelo Directo Jetsmart")

        draw_pin_icon(c, 90, 935, size=18)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#1A1A1A"))
        c.drawString(130, 945, "Córdoba")
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(130, 928, "Aeropuerto Internacional Córdoba")

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(360, 950, f"Salida Vuelo: Domingo {cronograma['checkin_str']} - 15:00 hs")

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(360, 930, "Vuelo directo Córdoba - Floripa (Duración: 3 horas)")
        c.drawString(360, 912, "Horario de llegada estimado: 18:00 hs (Florianópolis)")
        c.drawString(360, 894, "Incluye: Equipaje cabina hasta 10 kg + Traslado Aeropuerto - Alojamiento")

        # Paso 2: Estadía en Destino
        draw_pin_icon(c, 90, 775, size=18)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#1A1A1A"))
        c.drawString(130, 785, destino)
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(130, 768, info_dest['pais'])

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(360, 790, cronograma['estadia_itinerario'])

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(360, 770, f"Alojamiento: {tipo_alojamiento}{texto_comidas_aloj}")
        c.drawString(360, 752, f"Tipo de habitación: {base_str}")
        c.drawString(360, 734, "Coordinación receptiva acompañando en destino")

        # Paso 3: Vuelo de Regreso
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(70, 620, "Regreso - Vuelo Directo Jetsmart")

        draw_pin_icon(c, 90, 545, size=18)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#1A1A1A"))
        c.drawString(130, 555, "Córdoba")
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(130, 538, "Aeropuerto Internacional Córdoba")

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#222222"))
        fecha_regreso_vuelo = cronograma['checkout_str'].split(' (')[0]
        c.drawString(360, 560, f"Vuelo de Regreso: Domingo {fecha_regreso_vuelo} - 18:00 hs")

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(360, 540, "Vuelo directo Floripa - Córdoba (Duración: 3 horas)")
        c.drawString(360, 522, "Horario de arribo a Córdoba: 21:00 hs")
        c.drawString(360, 504, "Incluye: Traslado Alojamiento hacia Aeropuerto + Equipaje cabina 10 kg")

    elif es_sin_transporte:
        # ---------------------------------------------------------------------
        # MODALIDAD C: SIN TRANSPORTE (SOLO ALOJAMIENTO)
        # ---------------------------------------------------------------------
        # Paso 1: Check-in Alojamiento
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(70, 1010, "Llegada al Destino y Check-in")

        draw_pin_icon(c, 90, 935, size=18)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#1A1A1A"))
        c.drawString(130, 945, destino)
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(130, 928, info_dest['pais'])

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(360, 950, f"Check-in: Domingo {cronograma['checkin_str']}")

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(360, 930, "Transporte: No incluido (Arribo por cuenta del pasajero)")
        c.drawString(360, 912, "Horario de ingreso internacional: A partir de las 14:00 hs")
        c.drawString(360, 894, "Recepción: Coordinador y entrega de llaves en el alojamiento")

        # Paso 2: Estadía en Destino
        draw_pin_icon(c, 90, 775, size=18)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#1A1A1A"))
        c.drawString(130, 785, destino)
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(130, 768, info_dest['pais'])

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(360, 790, cronograma['estadia_itinerario'])

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(360, 770, f"Alojamiento: {tipo_alojamiento}{texto_comidas_aloj}")
        c.drawString(360, 752, f"Tipo de habitación: {base_str}")
        c.drawString(360, 734, "Servicios: Seguro, asistencia médica y Breakpoint exclusivo de playa")

        # Paso 3: Check-out
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(70, 620, "Check-out y Salida")

        draw_pin_icon(c, 90, 545, size=18)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#1A1A1A"))
        c.drawString(130, 555, destino)
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(130, 538, info_dest['pais'])

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#222222"))
        fecha_salida_aloj = cronograma['checkout_str'].split(' (')[0]
        c.drawString(360, 560, f"Check-out: Domingo {fecha_salida_aloj}")

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(360, 540, "Horario de salida: Hasta las 10:00 horas")
        c.drawString(360, 522, "Fin de nuestros servicios de hospedaje")
        c.drawString(360, 504, "Regreso por cuenta propia del pasajero")

    else:
        # ---------------------------------------------------------------------
        # MODALIDAD A: BUS (SEMI CAMA O CAMA) / SOLO BUS (EXCLUSIVO TERRESTRE)
        # ---------------------------------------------------------------------
        nombre_bus = "Bus Cama" if "Cama" in tipo_transporte and "Semi" not in tipo_transporte else "Bus Semi Cama"
        aloj_linea = "Venta exclusiva de transporte (Sin hospedaje)" if es_solo_bus else f"Alojamiento: {tipo_alojamiento}{texto_comidas_aloj}"

        # Paso 1: Inicio del viaje
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(70, 1010, "Inicio del viaje")

        draw_pin_icon(c, 90, 935, size=18)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#1A1A1A"))
        c.drawString(130, 945, "Córdoba")
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(130, 928, "Argentina")

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(360, 950, f"Salida programada: {cronograma['salida_str']}")

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(360, 930, f"Transporte: {nombre_bus} - Planalto / Costa viajes")
        c.drawString(360, 912, f"Lugar de salida: {lugar_salida}")
        c.drawString(360, 894, f"Plataforma: {plataforma}")

        # Paso 2: Estadía en Destino
        draw_pin_icon(c, 90, 775, size=18)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#1A1A1A"))
        c.drawString(130, 785, destino)
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(130, 768, info_dest['pais'])

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(360, 790, cronograma['estadia_itinerario'])

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(360, 770, aloj_linea)
        c.drawString(360, 752, f"Tipo de habitación: {base_str}")
        c.drawString(360, 734, "Cantidad: 7 noches de hospedaje completo" if not es_solo_bus else "Servicio: Transporte ida y vuelta directo")

        # Paso 3: Final del viaje
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(70, 620, "Final del viaje")

        draw_pin_icon(c, 90, 545, size=18)

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#1A1A1A"))
        c.drawString(130, 555, "Córdoba")
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawString(130, 538, "Argentina")

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#222222"))
        arribo_fecha = cronograma.get(
            "arribo_fecha_str", cronograma.get("dia_llegada_nombre", "Lunes"))
        c.drawString(360, 560, f"Llegada: {arribo_fecha} (tarde)")

        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(360, 540, f"Transporte: {nombre_bus} - Planalto / Costa viajes")
        c.drawString(360, 522, f"Lugar de llegada: {lugar_salida}")
        c.drawString(360, 504, "Plataforma: 80 a 90")

    draw_footer(c)
    c.showPage()

    # =========================================================================
    # PÁGINA 3: DESCRIPCIÓN DEL VIAJE, SERVICIOS Y BANNER FOTOGRÁFICO
    # =========================================================================
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 1100, "Descripción del viaje")

    # INCLUYE CONDICIONAL
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(70, 1050, "INCLUYE:")

    if es_aereo:
        incluye_items = [
            f"Vuelo directo Jetsmart ida y vuelta (Córdoba - Floripa).",
            "Equipaje de mano / bolso / valija en cabina de hasta 10 kg.",
            "Traslados internos en destino (Aeropuerto - Alojamiento - Aeropuerto).",
            f"Alojamiento 7 noches en {destino} ({tipo_alojamiento})." if not es_solo_bus else f"Venta exclusiva de pasaje aéreo a {destino}.",
            "Seguro de responsabilidad civil y asistencia médica.",
            "Coordinación receptiva permanente en destino.",
            "Servicio exclusivo de playa en Breakpoint."
        ]
        if not es_solo_bus and regimen_comidas and "Sin régimen" not in regimen_comidas:
            incluye_items.insert(4, f"Régimen de comidas: {regimen_comidas}")

        info_items = [
            "Para el trámite en aeropuerto y aduana se necesita DNI vigente o Pasaporte",
            "",
            "Vuelo Directo Jetsmart: Salidas de Domingo a Domingo (7 días de estadía)",
            "Duración del vuelo: 3 horas directas (Córdoba - Floripa)",
            "Horarios de vuelo: Salida 15:00 hs | Regreso 18:00 hs",
            "Equipaje incluido: hasta 10 kg en cabina por pasajero",
            "Traslados internos incluidos (Aeropuerto - Alojamiento - Aeropuerto)",
            "Coordinación receptiva acompañando en destino"
        ]
    elif es_sin_transporte:
        incluye_items = [
            f"Alojamiento 7 noches en {destino} ({tipo_alojamiento}).",
            "Seguro de responsabilidad civil y cobertura médica.",
            "Coordinador residente y asistencia permanente en destino.",
            "Servicio de playa en Breakpoint exclusivo.",
            "Bienvenida al destino y entrega personalizada de llaves."
        ]
        if regimen_comidas and "Sin régimen" not in regimen_comidas:
            incluye_items.insert(1, f"Régimen de comidas: {regimen_comidas}")

        info_items = [
            "Para el ingreso al país se necesita actualizado el DNI o Pasaporte",
            "",
            "Paquete de estadía en destino (Transporte terrestre/aéreo no incluido)",
            "Horario internacional de Check-in: Domingo a partir de las 14:00 hs",
            "Horario de Check-out: Domingo hasta las 10:00 hs",
            "Oficina y equipo de Break a disposición durante toda la estadía"
        ]
    else:
        nombre_bus = "Bus Cama" if "Cama" in tipo_transporte and "Semi" not in tipo_transporte else "Bus Semi Cama"
        incluye_items = [
            f"Transporte en bus chárter ({nombre_bus}). Directo a {destino}.",
            "Equipaje de bodega, hasta 23 Kg",
            "Equipaje de mano, mochila o bolso",
            f"Alojamiento 7 noches en {destino} ({tipo_alojamiento})" if not es_solo_bus else f"Transporte ida y vuelta a {destino} (Sin alojamiento)",
            "Seguro de resposabilidad civil",
            "Asistencia en rutas",
            "Gestor de ingreso y egreso a Brasil"
        ]
        if not es_solo_bus and regimen_comidas and "Sin régimen" not in regimen_comidas:
            incluye_items.insert(4, f"Régimen de comidas: {regimen_comidas}")

        info_items = [
            "Para el trámite en aduana se necesita actualizado el DNI o como alternativa el Pasaporte",
            "",
            "Duración: 33h en bus chárter directo",
            "Parada para desayuno",
            "Parada gestión en aduana",
            "Parada para almuerzo",
            "Parada para cena",
            info_dest["parada_ruta_detalle"]
        ]

    y_inc = 1030
    for item in incluye_items:
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(70, y_inc, item)
        y_inc -= 18

    # INFORMACIÓN IMPORTANTE Y PARADAS DE RUTA
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(70, 875, "INFORMACIÓN IMPORTANTE:")

    y_info = 855
    for item in info_items:
        if item == "":
            y_info -= 8
            continue
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(70, y_info, item)
        y_info -= 17

    # Sección Destino
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 680, destino)

    banner_path = os.path.join(ASSETS_DIR, "banner_p3.jpg")
    if os.path.exists(banner_path):
        c.drawImage(banner_path, 70, 440, width=695,
                    height=220, preserveAspectRatio=False)

    draw_paragraph(c, info_dest["resena"], 70, 415, 695, font_size=11,
                   leading=16, text_color=colors.HexColor("#444444"))

    draw_footer(c)
    c.showPage()

    # =========================================================================
    # PÁGINA 4: ALOJAMIENTOS DINÁMICOS POR DESTINO & SEGURO DE VIAJE
    # =========================================================================
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 1100, "Alojamientos")

    # Encabezado dinámico de complejos/posadas
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(70, 1055, aloj_info["encabezado"])

    y_aloj = 1035
    for item in aloj_info["items_generales"]:
        c.setFont("Helvetica", 10.5)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(70, y_aloj, item)
        y_aloj -= 16

    # Grilla de fotografías
    h_y = 740
    h_w = 222
    h_h = 150
    h1 = os.path.join(ASSETS_DIR, "hotel_1.jpg")
    h2 = os.path.join(ASSETS_DIR, "hotel_2.jpg")
    h3 = os.path.join(ASSETS_DIR, "hotel_3.jpg")

    if os.path.exists(h1):
        c.drawImage(h1, 70, h_y, width=h_w, height=h_h,
                    preserveAspectRatio=False)
    if os.path.exists(h2):
        c.drawImage(h2, 307, h_y, width=h_w, height=h_h,
                    preserveAspectRatio=False)
    if os.path.exists(h3):
        c.drawImage(h3, 544, h_y, width=h_w, height=h_h,
                    preserveAspectRatio=False)

    # Secciones dinámicas de categorías de alojamiento
    y_sec = 695
    for sec in aloj_info["secciones"]:
        c.setFont("Helvetica-Bold", 12.5)
        c.setFillColor(colors.HexColor("#222222"))
        c.drawString(70, y_sec, sec["titulo"])
        y_sec -= 18

        for it in sec["items"]:
            c.setFont("Helvetica", 10.5)
            c.setFillColor(colors.HexColor("#444444"))
            c.drawString(70, y_sec, it)
            y_sec -= 15
        y_sec -= 10

    # Información Importante Check-in
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(70, 420, "INFORMACIÓN IMPORTANTE:")
    c.setFont("Helvetica", 10.5)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawString(
        70, 400, "Para el Check in se debera aguardar el aviso de la persona a cargo del grupo, quien entrega llaves y equipajes.")
    c.drawString(70, 384, "Horario internacional despues de las 14:00 hs.")

    # Seguro de viaje
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 320, "Seguro de viaje")

    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(70, 280, "INCLUYE SEGURO DE RESPONSABILIDAD CIVIL")

    c.setFont("Helvetica-Bold", 11.5)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(
        70, 255, "Opcional asistencia médica a traves de Asisst Travel.")
    c.setFont("Helvetica", 10.5)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawString(
        70, 237, "La asistencia contratada con la agencia, incluye todos los gastos en destino ocasionados por la atención médica.")

    draw_footer(c)
    c.showPage()

    # =========================================================================
    # PÁGINA 5: STAFF EN DESTINO, BREAKPOINT & MÉTODOS DE PAGO
    # =========================================================================
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 1100, "Staff en destino")

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(70, 1055, "COORDINACIÓN EN BUS Y DURANTE EL VIAJE")

    items_staff = [
        f"Contamos con una oficina propia en el centro de {destino} y un staff permanente durante todo el verano",
        "Una flota de vehiculos a disposición de nuestros pasajeros.",
        "Coordinadores de area médica y médica residente en el destino."
    ]
    y_staff = 1035
    for item in items_staff:
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(70, y_staff, item)
        y_staff -= 16

    b_y = 810
    b_w = 222
    b_h = 150
    b1 = os.path.join(ASSETS_DIR, "beach_1.jpg")
    b2 = os.path.join(ASSETS_DIR, "beach_2.jpg")
    b3 = os.path.join(ASSETS_DIR, "beach_3.jpg")

    if os.path.exists(b1):
        c.drawImage(b1, 70, b_y, width=b_w, height=b_h,
                    preserveAspectRatio=False)
    if os.path.exists(b2):
        c.drawImage(b2, 307, b_y, width=b_w, height=b_h,
                    preserveAspectRatio=False)
    if os.path.exists(b3):
        c.drawImage(b3, 544, b_y, width=b_w, height=b_h,
                    preserveAspectRatio=False)

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(70, 770, "BREAKPOINT EXCLUSIVO")

    items_bp = [
        "Servicio de playa para el grupo",
        "Reposeras, mantas, sombrillas y guardaropa",
        "Seguridad y guardavida",
        "Servicio de fotografía",
        "Pulsera identificatoria",
        "Pulsera con descuentos",
        "Vaso de regalo",
        "Bienvenida al destino",
        f"Disponible en {destino} de 09 a 19 horas y en cada excursión con el grupo"
    ]
    y_bp = 750
    for item in items_bp:
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(70, y_bp, item)
        y_bp -= 16

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.HexColor("#1A1A1A"))
    c.drawString(70, 565, "Métodos de reserva y pagos")

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#222222"))
    c.drawString(70, 525, "FINANCIADO MEDIANTE LA AGENCIA CON ENTREGA INICIAL")

    items_pagos = [
        f"Entrega de ($) {ars_inscripcion:,} por persona.".replace(",", "."),
        "Al momento de la entrega se congela el precio final y se asegura el cupo.",
        f"A financiar el resto del tour {precio_usd} USD, en cuotas mensuales.",
        "Las cuotas se abonan del 1 al 20 de cada mes por transferencia o depósito con cuponera de la agencia.",
        "El total del tour debe estar abonado completo, hasta 15 días antes de la fecha de salida.",
        "Como método de pago alternativo se puede abonar de contado por deposito o transferencia bancaria al valor del pack elegido."
    ]
    y_pago = 505
    for item in items_pagos:
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#444444"))
        c.drawString(70, y_pago, item)
        y_pago -= 18

    qr_path = os.path.join(ASSETS_DIR, "qr_code.png")
    desc_path = os.path.join(ASSETS_DIR, "descubri_mas.png")
    if os.path.exists(desc_path):
        c.drawImage(desc_path, 70, 240, width=80, height=26,
                    preserveAspectRatio=True, mask='auto')
    if os.path.exists(qr_path):
        c.drawImage(qr_path, 70, 140, width=90,
                    height=90, preserveAspectRatio=True)

    draw_footer(c)
    c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


if __name__ == "__main__":
    crono = calcular_cronograma(datetime.date(2027, 1, 22))
    for d in ["Canasvieiras", "Ferrugem", "Praia do Rosa"]:
        b = generar_pdf_break(
            cliente="Oriana",
            destino=d,
            precio_usd=629,
            ars_inscripcion=210000,
            cronograma=crono,
            cant_pasajeros=2,
            base_doble_exclusiva=True
        )
        print(f"Generado {d}: {len(b)} bytes")
