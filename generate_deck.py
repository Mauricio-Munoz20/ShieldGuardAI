import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_deck(output_path):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette (Premium Fintech Cybersecurity)
    BG_DARK = RGBColor(11, 19, 43)        # #0B132B Deep Navy
    BG_CARD = RGBColor(20, 32, 60)        # #14203C Card Navy
    BG_CARD_BORDER = RGBColor(38, 58, 98) # Border
    BG_LIGHT_CARD = RGBColor(240, 244, 250)
    
    PRIMARY_BLUE = RGBColor(0, 150, 255)  # Vibrant Cyan/Blue #0096FF
    ACCENT_CYAN = RGBColor(0, 210, 255)   # Neon Cyan #00D2FF
    ACCENT_GREEN = RGBColor(16, 185, 129) # Emerald Green #10B981
    ACCENT_AMBER = RGBColor(245, 158, 11) # Amber #F59E0B
    ACCENT_RED = RGBColor(239, 68, 68)    # Red #EF4444
    
    TEXT_WHITE = RGBColor(255, 255, 255)
    TEXT_MUTED = RGBColor(148, 163, 184)  # Slate 400
    TEXT_DARK = RGBColor(15, 23, 42)
    TEXT_BODY = RGBColor(51, 65, 85)

    def set_slide_background(slide, color=BG_DARK):
        bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = color
        bg_shape.line.fill.background()
        return bg_shape

    def add_header(slide, section_tag, title_text, slide_num_str):
        # Section Tag
        tx_tag = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(8), Inches(0.35))
        tf_tag = tx_tag.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_right = tf_tag.margin_top = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = section_tag.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_CYAN
        
        # Title
        tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(10), Inches(0.6))
        tf_title = tx_title.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

        # Slide Number / Footer
        tx_num = slide.shapes.add_textbox(Inches(11.5), Inches(0.5), Inches(1.0), Inches(0.35))
        tf_num = tx_num.text_frame
        tf_num.word_wrap = True
        p_num = tf_num.paragraphs[0]
        p_num.alignment = PP_ALIGN.RIGHT
        p_num.text = slide_num_str
        p_num.font.size = Pt(10)
        p_num.font.bold = True
        p_num.font.color.rgb = TEXT_MUTED

    def create_card(slide, left, top, width, height, bg_color=BG_CARD, border_color=BG_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1)
        else:
            card.line.fill.background()
        return card

    # ==========================================
    # SLIDE 1: PORTADA
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, RGBColor(7, 13, 29))
    
    # Glow / Tech accent line
    glow_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(1.2), Inches(0.06))
    glow_line.fill.solid()
    glow_line.fill.fore_color.rgb = ACCENT_CYAN
    glow_line.line.fill.background()

    # Pill Tag
    tag_card = create_card(s1, 0.8, 1.2, 3.8, 0.45, RGBColor(16, 37, 74), ACCENT_CYAN)
    tf_pill = tag_card.text_frame
    tf_pill.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_pill = tf_pill.paragraphs[0]
    p_pill.text = "EMPRENDIMIENTO DE ALTO IMPACTO · CORFO"
    p_pill.font.size = Pt(9.5)
    p_pill.font.bold = True
    p_pill.font.color.rgb = ACCENT_CYAN
    p_pill.alignment = PP_ALIGN.CENTER

    # Main Title
    tx_main = s1.shapes.add_textbox(Inches(0.8), Inches(2.1), Inches(11.5), Inches(1.8))
    tf_main = tx_main.text_frame
    tf_main.word_wrap = True
    p_t1 = tf_main.paragraphs[0]
    p_t1.text = "ShieldGuard AI"
    p_t1.font.size = Pt(44)
    p_t1.font.bold = True
    p_t1.font.color.rgb = TEXT_WHITE
    
    p_t2 = tf_main.add_paragraph()
    p_t2.text = "Motor de Prevención Inteligente de Autofraude Bancario en Tiempo Real"
    p_t2.font.size = Pt(22)
    p_t2.font.color.rgb = PRIMARY_BLUE
    p_t2.space_before = Pt(8)

    # Context Card
    info_card = create_card(s1, 0.8, 4.4, 11.733, 2.2, BG_CARD, BG_CARD_BORDER)
    tf_info = info_card.text_frame
    tf_info.margin_left = Inches(0.4)
    tf_info.margin_top = Inches(0.3)
    
    p1 = tf_info.paragraphs[0]
    p1.text = "Proyecto de Innovación & Emprendimiento Basado en Ingeniería"
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = ACCENT_CYAN
    
    p2 = tf_info.add_paragraph()
    p2.text = "Defensa transaccional en backend contra el autofraude y desconocimiento indebido de compras bajo la Ley N° 21.274 en Chile."
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(4)

    p3 = tf_info.add_paragraph()
    p3.text = "Asignatura: Negocios desde la Ingeniería  |  Docente: Manuel Guzmán Tello  |  Universidad Austral de Chile (2024)"
    p3.font.size = Pt(11)
    p3.font.bold = True
    p3.font.color.rgb = TEXT_WHITE
    p3.space_before = Pt(14)

    # ==========================================
    # SLIDE 2: INTRODUCCIÓN & PROBLEMATIZACIÓN
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "01. Introducción & Problematización", "El Problema Real vs. La Solución Prematura", "02 / 12")

    # Left Card: Problema
    c_prob = create_card(s2, 0.8, 1.6, 5.7, 5.2, BG_CARD, BG_CARD_BORDER)
    tf_p = c_prob.text_frame
    tf_p.margin_left = Inches(0.4)
    tf_p.margin_right = Inches(0.4)
    tf_p.margin_top = Inches(0.4)
    
    p = tf_p.paragraphs[0]
    p.text = "EL DOLOR EN TERRENO: LEY 21.274"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    
    p = tf_p.add_paragraph()
    p.text = "La regulación chilena obliga a las instituciones financieras a restituir los fondos ante reclamos de fraude sin requerir peritajes previos inmediatos."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

    p = tf_p.add_paragraph()
    p.text = "Consecuencias críticas detectadas:"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_before = Pt(12)

    bullets_p = [
        ("Explosión del autofraude:", " Usuarios que realizan compras legítimas y luego las desconocen premeditadamente."),
        ("Altos costos operativos:", " Millones de dólares anuales en restituciones forzosas y sobrecarga legal."),
        ("Vulnerabilidad del canal:", " Crecimiento exponencial de phishing, SMiShing e ingeniería social.")
    ]
    for bold_t, norm_t in bullets_p:
        p = tf_p.add_paragraph()
        p.text = "• " + bold_t + norm_t
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(6)

    # Right Card: Pivote Validado
    c_piv = create_card(s2, 6.8, 1.6, 5.7, 5.2, BG_CARD, PRIMARY_BLUE)
    tf_v = c_piv.text_frame
    tf_v.margin_left = Inches(0.4)
    tf_v.margin_right = Inches(0.4)
    tf_v.margin_top = Inches(0.4)
    
    p = tf_v.paragraphs[0]
    p.text = "EL PIVOTE VALIDADO EN LA INDUSTRIA"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    
    p = tf_v.add_paragraph()
    p.text = "De una hipótesis prematura a una solución viable de backend:"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

    p = tf_v.add_paragraph()
    p.text = "❌ Hipótesis inicial: SDK intrusivo instalado dentro de la app móvil del banco (rechazado por fricción de usuario, consumo de batería y brechas de privacidad)."
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(252, 165, 165)
    p.space_before = Pt(8)

    p = tf_v.add_paragraph()
    p.text = "✔ Solución validada: Motor de inferencia Machine Learning operando directamente en el Backend del banco sobre el flujo transaccional."
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(134, 239, 172)
    p.space_before = Pt(8)

    # Quote block
    p = tf_v.add_paragraph()
    p.text = "«El dispositivo del usuario no es el lugar correcto para defender al banco. La defensa inteligente debe operar en el servidor, analizando el comportamiento de la tarjeta en tiempo real.»"
    p.font.size = Pt(10)
    p.font.italic = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_before = Pt(16)

    p = tf_v.add_paragraph()
    p.text = "— Validación técnica con Aldo Uribe (Ex CEO Bancario)"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(4)

    # ==========================================
    # SLIDE 3: AUTOPOIESIS & ALTO IMPACTO
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "02. Marco Conceptual & Alto Impacto", "Escalabilidad Económica y Sistema Autopoiético", "03 / 12")

    # Top Left: Por qué es Alto Impacto
    c_hi = create_card(s3, 0.8, 1.6, 5.7, 5.2, BG_CARD, BG_CARD_BORDER)
    tf_hi = c_hi.text_frame
    tf_hi.margin_left = tf_hi.margin_right = tf_hi.margin_top = Inches(0.4)
    
    p = tf_hi.paragraphs[0]
    p.text = "CRITERIOS DE ALTO IMPACTO"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    
    impact_items = [
        ("Modelo SaaS B2B Escalable:", " Generación de ingresos recurrentes mediante contratos anuales por entidad sin requerir presencia física en sucursales."),
        ("Costo Marginal Decreciente (CMg → 0):", " Infraestructura Cloud elástica sobre AWS que permite procesar millones de transacciones adicionales sin multiplicar la estructura de costos."),
        ("Apalancamiento de Red:", " Cada nuevo banco integrado aporta patrones de detección anónimos que robustecen la precisión del modelo global.")
    ]
    for h, desc in impact_items:
        p = tf_hi.add_paragraph()
        p.text = "• " + h + " " + desc
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(12)

    # Right: Autopoiesis
    c_auto = create_card(s3, 6.8, 1.6, 5.7, 5.2, BG_CARD, BG_CARD_BORDER)
    tf_auto = c_auto.text_frame
    tf_auto.margin_left = tf_auto.margin_right = tf_auto.margin_top = Inches(0.4)
    
    p = tf_auto.paragraphs[0]
    p.text = "SISTEMA AUTOPOIÉTICO (MATURANA & VARELA)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    p = tf_auto.add_paragraph()
    p.text = "«Un sistema autopoiético es aquel que se auto-regenera, se auto-organiza y mantiene su identidad frente a las perturbaciones del entorno»"
    p.font.size = Pt(10.5)
    p.font.italic = True
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(8)

    p = tf_auto.add_paragraph()
    p.text = "(Maturana & Varela, 1972/2004 — 'De Máquinas y Seres Vivos')"
    p.font.size = Pt(9.5)
    p.font.color.rgb = ACCENT_CYAN
    p.space_before = Pt(2)

    p = tf_auto.add_paragraph()
    p.text = "Aplicación directa en ShieldGuard AI:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(12)

    auto_points = [
        ("Auto-ajuste continuo:", " Calibración autónoma de pesos algorítmicos frente a nuevas variantes de fraude."),
        ("Inmunidad sistémica:", " Detección de perturbaciones sin intervención humana externa en cada transacción."),
        ("Mantenimiento de límites:", " Opera de forma soberana dentro de la infraestructura segura del banco.")
    ]
    for h, desc in auto_points:
        p = tf_auto.add_paragraph()
        p.text = "✔ " + h + " " + desc
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(6)

    # ==========================================
    # SLIDE 4: BUSINESS MODEL CANVAS
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "03. Modelo de Negocios", "Business Model Canvas Ejecutivo", "04 / 12")

    # 6 Canvas Cards in 3x2 Grid
    canvas_blocks = [
        ("01. PROPUESTA DE VALOR", "Reducción Drástica de Pérdidas", "Detección temprana y bloqueo proactivo de autofraude bajo Ley 21.274 en tiempo real sin fricción para el usuario.", ACCENT_CYAN, 0.8, 1.6),
        ("02. SEGMENTOS DE CLIENTES", "Bancos & Fintechs (B2B)", "Instituciones financieras emisoras de tarjetas de crédito y débito expuestas a altos volúmenes de reclamos y contracargos.", PRIMARY_BLUE, 4.8, 1.6),
        ("03. ACTIVIDADES CLAVE", "I+D, Integración & Monitoreo", "Entrenamiento de redes neuronales y árboles de decisión, integración de APIs bancarias de baja latencia y monitoreo 24/7.", ACCENT_GREEN, 8.8, 1.6),
        ("04. RECURSOS CLAVE", "Talento, Cloud & Datos", "Equipo de ingeniería multidisciplinario, clúster de cómputo en AWS (SOC2/PCI-DSS) y datasets transaccionales anonimizados.", ACCENT_AMBER, 0.8, 4.3),
        ("05. FUENTES DE INGRESO", "SaaS Recurrente + Setup", "Setup Fee en piloto inicial + Licenciamiento SaaS mensual indexado al volumen transaccional de la entidad.", ACCENT_GREEN, 4.8, 4.3),
        ("06. SOCIOS ESTRATÉGICOS", "Corfo, CMF & Banca Aliada", "Corfo (subsidio I+D Crea y Valida), CMF (marco normativo y compliance) y bancos early adopters para validación.", ACCENT_CYAN, 8.8, 4.3)
    ]

    for tag, title, body, color, x, y in canvas_blocks:
        card = create_card(s4, x, y, 3.733, 2.5, BG_CARD, BG_CARD_BORDER)
        tf = card.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.25)
        
        p = tf.paragraphs[0]
        p.text = tag
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = color
        
        p = tf.add_paragraph()
        p.text = title
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(4)
        
        p = tf.add_paragraph()
        p.text = body
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(4)

    # ==========================================
    # SLIDE 5: PROPUESTA DE VALOR & DIFERENCIADOR
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "04. Análisis Competitivo & Valor Diferencial", "¿Por Qué Elegir ShieldGuard AI?", "05 / 12")

    # Left Card: Status Quo
    c_sq = create_card(s5, 0.8, 1.6, 5.7, 4.2, BG_CARD, BG_CARD_BORDER)
    tf_sq = c_sq.text_frame
    tf_sq.margin_left = tf_sq.margin_right = tf_sq.margin_top = Inches(0.35)
    
    p = tf_sq.paragraphs[0]
    p.text = "STATUS QUO / SOLUCIONES ACTUALES"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED

    sq_bullets = [
        ("Listas negras telefónicas:", " Inútiles contra números spoofing y chips prepago desechables."),
        ("Reglas estáticas manuales:", " Requieren semanas para actualizarse y generan alta tasa de falsos positivos."),
        ("Falta de análisis de comportamiento:", " No evalúan la cinemática ni el patrón contextual de uso de la tarjeta."),
        ("Reacción tardía:", " El banco actúa recién cuando el cliente ingresa el reclamo bajo Ley 21.274.")
    ]
    for b_title, b_desc in sq_bullets:
        p = tf_sq.add_paragraph()
        p.text = "✖ " + b_title + b_desc
        p.font.size = Pt(10)
        p.font.color.rgb = RGBColor(252, 165, 165)
        p.space_before = Pt(8)

    # Right Card: ShieldGuard Approach
    c_sg = create_card(s5, 6.8, 1.6, 5.7, 4.2, BG_CARD, PRIMARY_BLUE)
    tf_sg = c_sg.text_frame
    tf_sg.margin_left = tf_sg.margin_right = tf_sg.margin_top = Inches(0.35)
    
    p = tf_sg.paragraphs[0]
    p.text = "ENFOQUE SHIELDGUARD AI"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    sg_bullets = [
        ("Análisis comportamental en Backend:", " Evaluación en tiempo real del flujo transaccional en milisegundos."),
        ("Zero-Friction UX:", " No interfiere con el uso de la app ni impone pasos engorrosos al cliente."),
        ("Privacidad por diseño (Privacy by Design):", " Opera sobre vectores anonimizados sin acceder a datos personales sensibles."),
        ("Bloqueo Proactivo Preventivo:", " Congela la tarjeta ante 3-5 anomalías críticas antes del reclamo formal.")
    ]
    for b_title, b_desc in sg_bullets:
        p = tf_sg.add_paragraph()
        p.text = "✔ " + b_title + b_desc
        p.font.size = Pt(10)
        p.font.color.rgb = RGBColor(187, 247, 208)
        p.space_before = Pt(8)

    # Bottom Callout: Beneficio Económico
    c_ben = create_card(s5, 0.8, 6.0, 11.733, 0.9, RGBColor(16, 37, 74), ACCENT_CYAN)
    tf_ben = c_ben.text_frame
    tf_ben.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_ben.margin_left = Inches(0.4)
    p = tf_ben.paragraphs[0]
    p.text = "BENEFICIO ECONÓMICO DIRECTO: Reduce en más de un 60% las pérdidas por restitución obligatoria de fondos bajo la Ley 21.274, protegiendo el margen operativo de la institución."
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 6: PRODUCTO MÍNIMO VIABLE (MVP)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "05. Prototipo & Experiencia de Usuario", "Producto Mínimo Viable (MVP) — Risk Console", "06 / 12")

    # Left: MVP Features
    c_mvp_f = create_card(s6, 0.8, 1.6, 5.0, 5.2, BG_CARD, BG_CARD_BORDER)
    tf_mf = c_mvp_f.text_frame
    tf_mf.margin_left = tf_mf.margin_right = tf_mf.margin_top = Inches(0.35)
    
    p = tf_mf.paragraphs[0]
    p.text = "ARQUITECTURA DE LA CONSOLA"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p = tf_mf.add_paragraph()
    p.text = "Diseñada específicamente para el Gerente de Riesgo y Analistas de Prevención de Fraude Bancario:"
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(6)

    mvp_feats = [
        ("Alertas en Tiempo Real:", " Detección de patrones de contracargo premeditado con 3 a 5 eventos anómalos previos a la consumación."),
        ("Score de Confianza ML:", " Nivel probabilístico de autofraude calculado por el modelo (0 - 100%)."),
        ("Bloqueo Proactivo 1-Click:", " Permite congelar temporalmente el plástico o derivar a confirmación reforzada."),
        ("Trazabilidad y Auditoría:", " Historial probatorio exportable para auditorías ante la CMF y peritajes.")
    ]
    for t_feat, d_feat in mvp_feats:
        p = tf_mf.add_paragraph()
        p.text = "• " + t_feat + d_feat
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(10)

    # Right: UI Mockup Visual Representation
    c_mock = create_card(s6, 6.1, 1.6, 6.433, 5.2, RGBColor(15, 23, 42), ACCENT_CYAN)
    tf_mk = c_mock.text_frame
    tf_mk.margin_left = tf_mk.margin_right = tf_mk.margin_top = Inches(0.25)
    
    p = tf_mk.paragraphs[0]
    p.text = "🖥 app.shieldguard.ai/risk — Consola de Riesgo (Demo LIVE)"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    mock_alerts = [
        ("ALTO RIESGO", "$358.200 CLP", "Tarjeta: **** 1142", "Patrón: Retiro simultáneo + Intento eCommerce exterior", "Confianza ML: 94%", ACCENT_RED),
        ("ALTO RIESGO", "$184.500 CLP", "Tarjeta: **** 4821", "Patrón: Transferencia anómala post cambio de contraseña", "Confianza ML: 87%", ACCENT_RED),
        ("RIESGO MEDIO", "$92.100 CLP", "Tarjeta: **** 7390", "Patrón: Geoposición inconsistente en 15 minutos", "Confianza ML: 68%", ACCENT_AMBER)
    ]
    for risk_lvl, amount, card_n, pattern, score, color in mock_alerts:
        p = tf_mk.add_paragraph()
        p.text = f"[{risk_lvl}] {amount} | {card_n} | {score}"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_before = Pt(8)
        
        p = tf_mk.add_paragraph()
        p.text = f"  └ {pattern}"
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(2)

    # Bottom action in mockup
    p = tf_mk.add_paragraph()
    p.text = "⚡ ACCIÓN INMEDIATA: [ BLOQUEAR PLÁSTICO PROACTIVAMENTE ]"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_before = Pt(16)

    # ==========================================
    # SLIDE 7: ESTRUCTURA DEL EQUIPO
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "06. Organización & Gobierno", "Estructura del Equipo y Perfiles Clave", "07 / 12")

    team_roles = [
        ("ROL 01", "CEO & Líder de Producto", "Liderazgo Estratégico & Visión", [
            ("Visión de Producto:", " Definición del roadmap tecnológico y alineación de la solución con la problemática bancaria."),
            ("Relación con Inversionistas:", " Enlace estratégico con fondos de venture capital y directivos de la industria."),
            ("Gestión de Stakeholders:", " Validación continua de propuestas de valor con gerentes de riesgo.")
        ], ACCENT_CYAN, 0.8),
        ("ROL 02", "Comercial & Marketing", "Venta Consultiva B2B", [
            ("Prospección Institucional:", " Generación de pipeline con CISOs y Gerentes de Ciberseguridad bancaria."),
            ("Venta Consultiva:", " Gestión de pruebas de concepto (PoC) y ciclos de venta de largo plazo."),
            ("Canales B2B:", " Outreach directo y posicionamiento de marca en eventos del sector Fintech.")
        ], PRIMARY_BLUE, 4.8),
        ("ROL 03", "Finanzas & Operaciones", "Control Financiero & CloudOps", [
            ("Gestión de Caja & Fondos:", " Postulación y rendición de líneas de financiamiento Corfo."),
            ("Infraestructura CloudOps:", " Despliegue seguro y alta disponibilidad de servidores en AWS."),
            ("Cumplimiento Regulatorio:", " Alineación de procesos a normativas CMF y estándares de seguridad.")
        ], ACCENT_GREEN, 8.8)
    ]

    for rol_tag, name, subtitle, tasks, color, x in team_roles:
        card = create_card(s7, x, 1.6, 3.733, 4.4, BG_CARD, BG_CARD_BORDER)
        tf = card.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.3)
        
        p = tf.paragraphs[0]
        p.text = rol_tag
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = color
        
        p = tf.add_paragraph()
        p.text = name
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(3)
        
        p = tf.add_paragraph()
        p.text = subtitle
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(2)
        
        for task_h, task_d in tasks:
            p = tf.add_paragraph()
            p.text = "• " + task_h + " " + task_d
            p.font.size = Pt(8.5)
            p.font.color.rgb = TEXT_MUTED
            p.space_before = Pt(6)

    # Footnote about team execution
    c_note = create_card(s7, 0.8, 6.2, 11.733, 0.7, RGBColor(16, 37, 74), BG_CARD_BORDER)
    tf_n = c_note.text_frame
    tf_n.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_n.margin_left = Inches(0.3)
    p = tf_n.paragraphs[0]
    p.text = "Estructura Organizacional: Modelo de roles complementarios diseñado para sostener la operación desde la etapa de I+D hasta el escalamiento comercial."
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 8: PROCESO COMERCIAL B2B
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "07. Estrategia Go-to-Market", "Ciclo Comercial B2B (Venta Consultiva Institucional)", "08 / 12")

    steps = [
        ("01", "Identificación", "Cuantificación de pérdidas por Ley 21.274 en banco objetivo.", 0.8),
        ("02", "Prospección", "Outreach directo a Gerencias de Ciberseguridad y Riesgo.", 2.76),
        ("03", "Discovery", "Mapeo técnico de arquitectura y flujos transaccionales.", 4.72),
        ("04", "Piloto 90 Días", "Implementación en modo sombra con métricas de reducción.", 6.68),
        ("05", "Cierre SaaS", "Firma de contrato anual: Setup Fee + Licencia mensual.", 8.64),
        ("06", "Onboarding", "Monitoreo 24/7, mejora de modelos y QBR trimestral.", 10.60)
    ]

    for num, title, desc, x in steps:
        card = create_card(s8, x, 1.8, 1.933, 4.0, BG_CARD, PRIMARY_BLUE if num in ["04", "05"] else BG_CARD_BORDER)
        tf = card.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
        
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN
        
        p = tf.add_paragraph()
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(6)
        
        p = tf.add_paragraph()
        p.text = desc
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(6)

    # Strategy statement
    c_strat = create_card(s8, 0.8, 6.0, 11.733, 0.9, RGBColor(16, 37, 74), BG_CARD_BORDER)
    tf_st = c_strat.text_frame
    tf_st.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_st.margin_left = Inches(0.4)
    p = tf_st.paragraphs[0]
    p.text = "Estrategia de Venta: Proceso consultivo y de base racional. Se fundamenta en una Prueba de Concepto (PoC) de 90 días demostrando ahorro económico real previo al cierre del contrato anual."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_WHITE

    # ==========================================
    # SLIDE 9: FINANCIAMIENTO & APOYO ESTATAL
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "08. Financiamiento & Capital", "Estrategia de Apoyo Estatal (CORFO)", "09 / 12")

    # Left Card: Fondo Objetivo
    c_fnd = create_card(s9, 0.8, 1.6, 3.733, 5.2, BG_CARD, BG_CARD_BORDER)
    tf_f = c_fnd.text_frame
    tf_f.margin_left = tf_f.margin_right = tf_f.margin_top = Inches(0.35)
    
    p = tf_f.paragraphs[0]
    p.text = "FONDO OBJETIVO"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    
    p = tf_f.add_paragraph()
    p.text = "Corfo: Capital Semilla / Crea y Valida"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(6)

    p = tf_f.add_paragraph()
    p.text = "Subsidio estatal para completar la fase de I+D, validar la solución en entorno simulado e iniciar pilotos bancarios reales."
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(6)

    p = tf_f.add_paragraph()
    p.text = "Fase Actual: Idea $\\rightarrow$ MVP Funcional validado con actores clave de la industria."
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_before = Pt(12)

    # Middle Card: Checklist de Requisitos
    c_chk = create_card(s9, 4.8, 1.6, 3.733, 5.2, BG_CARD, BG_CARD_BORDER)
    tf_ck = c_chk.text_frame
    tf_ck.margin_left = tf_ck.margin_right = tf_ck.margin_top = Inches(0.35)
    
    p = tf_ck.paragraphs[0]
    p.text = "CHECKLIST DE POSTULACIÓN"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER

    chk_items = [
        ("MVP Funcional:", " Consola de riesgo operativa con algoritmos de clasificación."),
        ("Cartas de Interés (LoI):", " Respaldo y validación de interés por parte de instituciones financieras."),
        ("Equipo Interdisciplinario:", " Capacidades técnicas en ingeniería de software, IA y finanzas."),
        ("Presupuesto Detallado:", " Carta Gantt e hitos de ejecución a 12 meses.")
    ]
    for chk_h, chk_d in chk_items:
        p = tf_ck.add_paragraph()
        p.text = "✔ " + chk_h + " " + chk_d
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(8)

    # Right Card: Uso de Fondos
    c_use = create_card(s9, 8.8, 1.6, 3.733, 5.2, BG_CARD, PRIMARY_BLUE)
    tf_u = c_use.text_frame
    tf_u.margin_left = tf_u.margin_right = tf_u.margin_top = Inches(0.35)
    
    p = tf_u.paragraphs[0]
    p.text = "USO ESTRATÉGICO DE FONDOS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    p = tf_u.add_paragraph()
    p.text = "75% Cobertura Corfo"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_before = Pt(6)

    use_items = [
        ("Sueldos de Ingeniería I+D:", " 60% del fondo destinado a especialistas en ML y backend."),
        ("Infraestructura Cloud AWS:", " 25% para cómputo elástico y certificaciones de ciberseguridad."),
        ("Validación Comercial:", " 15% para asesoría legal en compliance CMF y pilotos.")
    ]
    for uh, ud in use_items:
        p = tf_u.add_paragraph()
        p.text = "• " + uh + " " + ud
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(8)

    # ==========================================
    # SLIDE 10: FLUJO DE CAJA & RETORNO
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "09. Viabilidad Financiera", "Proyección de Flujo de Caja & Retorno de Inversión", "10 / 12")

    # 4 Financial KPI Cards
    kpis = [
        ("$30.000 USD", "Inversión Inicial (Mes 0)", "Subsidio Corfo + Capital Fundador", ACCENT_CYAN, 0.8),
        ("Mes 4", "Primeros Ingresos", "Setup Fee + Licencia primer piloto", PRIMARY_BLUE, 3.8),
        ("Meses 7 – 8", "Punto de Equilibrio", "Ingresos recurrentes > Costos operacionales", ACCENT_GREEN, 6.8),
        ("> 25%", "TIR Proyectada (4 Años)", "Retorno atractivo con VAN positivo", ACCENT_AMBER, 9.8)
    ]
    for val, lbl, sub, color, x in kpis:
        card = create_card(s10, x, 1.6, 2.733, 1.8, BG_CARD, BG_CARD_BORDER)
        tf = card.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.2)
        
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = color
        
        p = tf.add_paragraph()
        p.text = lbl
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_before = Pt(3)
        
        p = tf.add_paragraph()
        p.text = sub
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(2)

    # Cash Flow Trajectory Detail
    c_traj = create_card(s10, 0.8, 3.6, 11.733, 3.2, BG_CARD, BG_CARD_BORDER)
    tf_tr = c_traj.text_frame
    tf_tr.margin_left = tf_tr.margin_right = tf_tr.margin_top = Inches(0.3)
    
    p = tf_tr.paragraphs[0]
    p.text = "DINÁMICA TEMPORAL DE LIQUIDEZ (HORIZONTE 12 MESES)"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    phases = [
        ("Meses 0 a 3 (Desarrollo & I+D):", " Ejecución del capital semilla en infraestructura y desarrollo del motor. Flujo neto negativo controlado."),
        ("Meses 4 a 6 (Despliegue de Pilotos):", " Incorporación del primer banco early adopter. Ingresos por Setup Fee ($10K) y tarifa reducida de piloto."),
        ("Meses 7 y 8 (Break-Even Operacional):", " Punto de inflexión donde la facturación SaaS mensual supera el costo fijo mensual de ingeniería y cloud."),
        ("Meses 9 a 12 (Escalamiento & Rentabilidad):", " Expansión a 2 nuevos clientes bancarios, consolidando un margen EBITDA proyectado superior al 45%.")
    ]
    for ph_t, ph_d in phases:
        p = tf_tr.add_paragraph()
        p.text = "▶ " + ph_t + " " + ph_d
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(5)

    # ==========================================
    # SLIDE 11: CONCLUSIÓN
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "10. Conclusión & Reflexión", "Emprendimiento de Alto Impacto desde la Ingeniería", "11 / 12")

    # Main Quote Card
    c_q = create_card(s11, 0.8, 1.6, 11.733, 1.7, RGBColor(16, 37, 74), PRIMARY_BLUE)
    tf_q = c_q.text_frame
    tf_q.margin_left = tf_q.margin_right = tf_q.margin_top = Inches(0.3)
    
    p = tf_q.paragraphs[0]
    p.text = "«El emprendimiento basado en ingeniería no consiste únicamente en construir algoritmos sofisticados, sino en aplicar rigor técnico y aprendizaje validado para resolver una ineficiencia económica real y medible en la sociedad.»"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = TEXT_WHITE

    # 3 Conclusion Pillars
    pillars = [
        ("01. Creatividad Disruptiva", "Reimaginación del problema cambiando el paradigma: defender desde el backend del banco en lugar de sobrecargar el dispositivo del cliente.", ACCENT_CYAN, 0.8),
        ("02. Rigor & Validación Técnica", "Arquitectura autopoiética con machine learning continuo, validada directamente con tomadores de decisión de la industria financiera.", ACCENT_GREEN, 4.8),
        ("03. Orientación al Mercado", "Modelo SaaS B2B sustentable con retorno económico cuantificable (TIR >25%) y apalancamiento estratégico en fondos Corfo.", ACCENT_AMBER, 8.8)
    ]
    for pil_t, pil_d, color, x in pillars:
        card = create_card(s11, x, 3.5, 3.733, 3.3, BG_CARD, BG_CARD_BORDER)
        tf = card.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.3)
        
        p = tf.paragraphs[0]
        p.text = pil_t
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = color
        
        p = tf.add_paragraph()
        p.text = pil_d
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(8)

    # ==========================================
    # SLIDE 12: BIBLIOGRAFÍA (APA 7°)
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "11. Referencias Académicas", "Bibliografía (Formato APA 7° Edición)", "12 / 12")

    c_bib = create_card(s12, 0.8, 1.6, 11.733, 5.2, BG_CARD, BG_CARD_BORDER)
    tf_b = c_bib.text_frame
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = Inches(0.35)
    
    p = tf_b.paragraphs[0]
    p.text = "FUENTES BIBLIOGRÁFICAS CONSULTADAS Y CITADAS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    refs = [
        "Eisenmann, T. (2021). Why startups fail: A new roadmap for entrepreneurial success. Harvard Business Review Press.",
        "Guzmán, M. (2024). Apuntes de clase — Negocios desde la ingeniería. Universidad Austral de Chile (Austranet).",
        "Osterwalder, A., & Pigneur, Y. (2010). Business model generation: A handbook for visionaries, game changers, and challengers. John Wiley & Sons.",
        "Ries, E. (2011). The lean startup: How today's entrepreneurs use continuous innovation to create radically successful businesses. Crown Publishing.",
        "Varela, F. J., & Maturana, H. R. (1972/2004). De máquinas y seres vivos: Autopoiesis, la organización de lo vivo (6.ª ed.). Editorial Universitaria."
    ]

    for idx, ref in enumerate(refs):
        p = tf_b.add_paragraph()
        p.text = f"[{idx+1:02d}]  {ref}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(10)

    p = tf_b.add_paragraph()
    p.text = "✔ Curso: Negocios desde la Ingeniería · Profesor: Manuel Guzmán Tello · 2024"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_before = Pt(18)

    # Save presentation
    prs.save(output_path)
    print(f"Presentation saved successfully at: {output_path}")

if __name__ == "__main__":
    out_dir = r"c:\Users\Hp\Downloads\shield"
    out_file = os.path.join(out_dir, "ShieldGuard_AI_Presentacion_Ejecutiva.pptx")
    build_deck(out_file)
