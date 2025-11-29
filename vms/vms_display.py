"""
Módulo para generar imágenes de paneles LED virtuales similares a los P8 utilizados en 
sistemas de transporte público.

Este módulo convierte texto en una representación visual de un panel LED, simulando
la apariencia de los displays utilizados en estaciones de buses o metro.
"""

from PIL import Image, ImageDraw, ImageFont

# --- Configuración del panel P8 ---
# Los paneles P8 tienen una matriz de LEDs más densa que los P10
PANELS_X = 5       # número de paneles horizontales
PANELS_Y = 3       # número de paneles verticales
PANEL_W  = 32      # LEDs por panel (ancho) - P8 tiene 32 LEDs de ancho
PANEL_H  = 16      # LEDs por panel (alto) - P8 tiene 16 LEDs de alto

# Tamaño total de la matriz de LEDs
# Calculamos el tamaño total multiplicando paneles por LEDs por panel
MATRIX_W = PANELS_X * PANEL_W   # 5 paneles * 32 LEDs = 160 LEDs de ancho
MATRIX_H = PANELS_Y * PANEL_H   # 3 paneles * 16 LEDs = 48 LEDs de alto

# Apariencia de cada LED
LED_SIZE = 10    # diámetro de la bolita en píxeles
LED_GAP  = 2     # separación entre LEDs (más pequeña que en P10)

# Colores RGB para los diferentes estados de los LEDs
LED_ON_COLOR  = (255, 0, 0)     # rojo encendido (brillante)
LED_OFF_COLOR = (40, 40, 40)    # gris apagado (oscuro)
BG_COLOR      = (10, 10, 10)    # fondo oscuro entre LEDs

def get_font(px_height: int):
    """
    Carga una fuente TrueType personalizada o la fuente predeterminada de PIL.
    
    Args:
        px_height (int): Altura deseada de la fuente en píxeles
        
    Returns:
        ImageFont: Objeto de fuente para usar con PIL
    """
    
    try:
        print("Using valid font")
        return ImageFont.truetype("assets/Seven Segment.ttf", px_height)
        
    except IOError:
        print("Falling back to default font")
        return ImageFont.load_default()

def render_text_mask(text: str, font_px=12, margin=3, line_spacing=2, color=(255, 0, 0)):
    """
    Renderiza el texto como una máscara binaria que representa qué LEDs deben encenderse.
    
    Esta función crea una imagen binaria donde cada píxel representa un LED:
    - 0: LED apagado
    - 1: LED encendido
    
    Args:
        text (str): Texto a renderizar, puede contener múltiples líneas separadas por \n
        font_px (int): Tamaño de la fuente en píxeles
        margin (int): Margen en píxeles desde el borde izquierdo y superior
        line_spacing (int): Espacio adicional entre líneas en píxeles
        color (tuple): Color RGB para el texto (r, g, b)
        
    Returns:
        tuple: (mask: Image, color: tuple) - Imagen en modo "L" con los LEDs a encender y el color del texto
    """
    # Crear una imagen binaria (1 bit) para representar qué píxeles encender
    # "1" significa blanco (LED encendido), "0" significa negro (LED apagado)
    mask1 = Image.new("1", (MATRIX_W, MATRIX_H), 0)
    draw1 = ImageDraw.Draw(mask1)
    font = get_font(font_px)

    # Posición vertical inicial para dibujar el texto
    y = margin
    # Procesar cada línea del texto por separado
    for ln in text.split("\n"):
        # Dibujar la línea de texto en la posición (margin, y)
        # fill=1 significa que los píxeles del texto serán blancos (encendidos)
        draw1.text((margin, y), ln, fill=1, font=font)  # sin antialias
        # Mover la posición vertical hacia abajo para la siguiente línea
        y += font_px + line_spacing

    # Convertir la imagen binaria a escala de grises (modo "L")
    # En modo "L", los valores van de 0 (negro) a 255 (blanco)
    # Esto facilita el procesamiento en la siguiente etapa
    mask = mask1.convert("L")
    return mask, color

def build_led_image(masks_with_colors):
    """
    Construye la imagen de LEDs encendidos/apagados a partir de múltiples máscaras con colores.
    
    Esta función toma una lista de tuplas (máscara, color) y crea una imagen
    visual que representa físicamente cómo se vería en un panel LED, con círculos
    que representan cada LED individual en diferentes colores.
    
    Args:
        masks_with_colors (list): Lista de tuplas (mask: Image, color: tuple) donde:
                     mask es una imagen en modo "L" donde cada píxel representa el estado de un LED
                     (0 = apagado, >0 = encendido)
                     color es una tupla RGB (r, g, b) para ese texto
    Returns:
        Image: Imagen RGB que representa físicamente el panel LED con círculos para cada LED
    """
    # Calcular el tamaño total de cada celda (LED + espacio)
    cell = LED_SIZE + LED_GAP
    # Dimensiones de la imagen de salida
    out_w = MATRIX_W * cell + LED_GAP
    out_h = MATRIX_H * cell + LED_GAP
    # Crear imagen de salida con color de fondo
    out = Image.new("RGB", (out_w, out_h), BG_COLOR)
    draw = ImageDraw.Draw(out)
    # Radio de cada LED (mitad del tamaño)
    r = LED_SIZE // 2

    # Iterar por cada posición de LED en la matriz
    for y in range(MATRIX_H):
        for x in range(MATRIX_W):
            # Determinar el color final para esta posición
            final_color = LED_OFF_COLOR  # Color por defecto si no hay texto
            # Iterar sobre todas las máscaras y colores
            for mask, color in masks_with_colors:
                # Obtener el valor del píxel en la máscara actual (0-255)
                val = mask.getpixel((x, y))
                # Si hay un LED encendido en esta posición, usar el color correspondiente
                if val > 0:
                    final_color = color
                    break  # Prioridad al primer texto que tenga un LED encendido
            
            # Calcular las coordenadas del centro del LED
            cx = LED_GAP + x * cell + r
            cy = LED_GAP + y * cell + r
            # Dibujar un círculo (LED) en la posición calculada
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=final_color)
    return out

def parse_colored_text(text: str, font_px=12, margin=3, line_spacing=2):
    """
    Procesa texto con marcadores de color y devuelve una lista de máscaras con sus colores.
    
    El formato del texto permite marcar partes con colores específicos usando el formato:
    {color_r,color_g,color_b}texto{/color}
    
    Args:
        text (str): Texto a procesar con marcadores de color
        font_px (int): Tamaño de la fuente en píxeles
        margin (int): Margen en píxeles desde el borde izquierdo y superior
        line_spacing (int): Espacio adicional entre líneas en píxeles
        
    Returns:
        list: Lista de tuplas (mask: Image, color: tuple) para cada parte coloreada
    """
    import re
    
    # Expresión regular para encontrar marcadores de color {r,g,b}texto{/color}
    pattern = r'\{(\d+),(\d+),(\d+)\}(.*?){/color\}'
    
    # Encontrar todas las coincidencias
    matches = re.findall(pattern, text)
    
    if not matches:
        # Si no hay marcadores de color, devolver el texto completo con color rojo
        mask, color = render_text_mask(text, font_px, margin, line_spacing, LED_ON_COLOR)
        return [(mask, color)]
    
    # Extraer las partes del texto que están entre los marcadores
    parts = re.split(pattern, text)
    
    # Crear una lista de tuplas (texto, color) para cada parte
    text_color_pairs = []
    i = 0
    for match in matches:
        r, g, b = int(match[0]), int(match[1]), int(match[2])
        colored_text = match[3]
        
        # Añadir texto antes del marcador (si existe)
        if i < len(parts) and parts[i].strip():
            text_color_pairs.append((parts[i], LED_ON_COLOR))  # Texto sin color es rojo por defecto
            i += 1
        
        # Añadir texto coloreado
        text_color_pairs.append((colored_text, (r, g, b)))
        i += 1
    
    # Añadir el texto final después del último marcador (si existe)
    if i < len(parts) and parts[i].strip():
        text_color_pairs.append((parts[i], LED_ON_COLOR))  # Texto sin color es rojo por defecto
    
    # Renderizar cada parte de texto con su color correspondiente
    result = []
    for text_part, color in text_color_pairs:
        if text_part.strip():  # Solo procesar si hay texto
            mask, _ = render_text_mask(text_part, font_px, margin, line_spacing, color)
            result.append((mask, color))
    
    return result


def parse_colored_text_fixed(text: str, font_px=12, margin=3, line_spacing=2):
    """
    Procesa texto con marcadores de color y devuelve una lista de máscaras con sus colores.
    Esta función corrige el espaciado entre caracteres al calcular las posiciones reales de cada fragmento de texto.
    
    El formato del texto permite marcar partes con colores específicos usando el formato:
    {color_r,color_g,color_b}texto{/color}
    
    Args:
        text (str): Texto a procesar con marcadores de color
        font_px (int): Tamaño de la fuente en píxeles
        margin (int): Margen en píxeles desde el borde izquierdo y superior
        line_spacing (int): Espacio adicional entre líneas en píxeles
        
    Returns:
        list: Lista de tuplas (mask: Image, color: tuple) para cada parte coloreada
    """
    import re
    
    # Expresión regular para encontrar marcadores de color {r,g,b}texto{/color}
    pattern = r'\{(\d+),(\d+),(\d+)\}(.*?){/color\}'
    
    # Buscar todas las coincidencias con sus posiciones
    tokens = []
    last_end = 0
    
    for match in re.finditer(pattern, text):
        # Agregar texto antes del marcador de color (si existe)
        if match.start() > last_end:
            plain_text = text[last_end:match.start()]
            if plain_text:
                tokens.append(('text', plain_text, LED_ON_COLOR))
        
        # Agregar texto con color
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        colored_text = match.group(4)
        tokens.append(('text', colored_text, (r, g, b)))
        
        last_end = match.end()
    
    # Agregar texto después del último marcador (si existe)
    if last_end < len(text):
        remaining_text = text[last_end:]
        if remaining_text:
            tokens.append(('text', remaining_text, LED_ON_COLOR))
    
    # Procesar cada línea por separado para mantener el espaciado correcto
    lines = []
    current_line_tokens = []
    
    for token_type, token_text, token_color in tokens:
        # Separar por saltos de línea
        parts = token_text.split('\n')
        current_line_tokens.append((token_type, parts[0], token_color))
        
        for part in parts[1:]:
            # Agregar la línea actual a la lista de líneas
            lines.append(current_line_tokens)
            # Iniciar nueva línea con la parte restante
            current_line_tokens = [('text', part, token_color)]
    
    # Agregar la última línea si no está vacía
    if current_line_tokens:
        lines.append(current_line_tokens)
    
    # Crear una imagen base para calcular posiciones
    font = get_font(font_px)
    
    # Procesar cada línea para determinar posiciones
    result_masks = []
    
    for line_idx, line_tokens in enumerate(lines):
        y_pos = margin + (line_idx * (font_px + line_spacing))
        
        # Crear máscaras separadas para cada parte de texto en la línea
        x_pos = margin
        
        for token_type, token_text, token_color in line_tokens:
            # Crear una máscara temporal para este fragmento de texto
            token_mask = Image.new("1", (MATRIX_W, MATRIX_H), 0)
            token_draw = ImageDraw.Draw(token_mask)
            
            # Dibujar el fragmento de texto en la posición actual
            token_draw.text((x_pos, y_pos), token_text, fill=1, font=font)
            
            # Agregar esta máscara específica a la lista de resultados
            result_masks.append((token_mask.convert("L"), token_color))
            
            # Actualizar la posición x para el siguiente fragmento
            try:
                text_width = token_draw.textlength(token_text, font=font)
            except:
                # Si textlength no está disponible, usar bbox
                bbox = token_draw.textbbox((x_pos, y_pos), token_text, font=font)
                text_width = bbox[2] - x_pos
            
            x_pos += text_width
    
    return result_masks

# --- Ejemplo ---
# Texto de muestra que simula información de rutas de transporte público
# Se convierte a mayúsculas para mejor visibilidad en el display LED
# texto = "201 -> 2m Vacio -> 10m Medio\n" \
# "205  >>  5m Vacio  >>  10m Vacio\n" \
# "204  >>  10m Vacio  >>  10m Vacio\n" # 3 lineas

# Ejemplo con texto coloreado
# texto_coloreado = "201 >> {0,255,0}2m Vacio{/color} >> {0,255,255}10m Medio{/color}\n" \
# "205 >> {0,255,0}5m Vacio{/color} >> {0,255,255}10m Vacio{/color}\n" \
# "204 >> {0,255,0}10m Lleno{/color} >> {0,255,255}10m Lleno{/color}" # 3 lineas

# Renderizar el texto coloreado
# masks_with_colors = parse_colored_text_fixed(texto_coloreado, font_px=12)
# img = build_led_image(masks_with_colors)
# Guardar la imagen resultante
# img.save("vms/panel_p8.png")
# print("Imagen generada: panel_p8.png")
