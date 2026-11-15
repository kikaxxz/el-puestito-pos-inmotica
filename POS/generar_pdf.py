import sys
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Resultados de la Validación del Software (ISO/IEC 25010)'.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Página '.encode('latin-1', 'replace').decode('latin-1') + str(self.page_no()), 0, 0, 'C')

pdf = PDF(orientation='L') 
pdf.add_page()
pdf.set_font('Arial', '', 11)

texto_1 = "Como parte de la evaluación técnica final para garantizar la viabilidad y estabilidad del ecosistema tecnológico del Restaurante \"El Puestito\", se estructuró y ejecutó un conjunto riguroso de escenarios de prueba. El objetivo de estas evaluaciones fue certificar el cumplimiento íntegro de los requerimientos operativos y de interoperabilidad de la arquitectura de software (Flutter, PyQt6 y Flask)."

texto_2 = "Para validar la calidad del sistema bajo un marco estandarizado, el análisis se rigió por los pilares funcionales de la normativa ISO/IEC 25010. Con el propósito de unificar los criterios de aceptación y permitir una evaluación objetiva en un mismo esquema, las métricas de todos los módulos fueron homologadas utilizando el tiempo de respuesta y procesamiento (en milisegundos - ms) como unidad de medida universal. Este enfoque permitió cuantificar desde la eficiencia de transmisión de datos hasta la velocidad de recuperación ante fallos y la fluidez de la interfaz de usuario."

texto_3 = "Los datos recolectados en los archivos de eventos (logs) y marcas de tiempo (timestamps) confirmaron que la arquitectura cliente-servidor responde dentro de los márgenes óptimos de operación, evitando colisiones y bloqueos. A continuación, se presenta la tabla resumen de la validación operativa del software:"

def put_text(t):
    pdf.multi_cell(0, 6, t.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(4)

put_text(texto_1)
put_text(texto_2)
put_text(texto_3)

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 10, 'Tabla X. Resumen de resultados de validación operativa del software (ISO/IEC 25010)'.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'C')
pdf.ln(2)

data = [
    ["Módulo Evaluado", "Parámetro Medido", "Criterio de Aceptación", "Resultado Obtenido", "Estado"],
    ["Eficiencia de\nDesempeño", "Latencia de transmisión y procesamiento asíncrono\nde comandas (API REST / WebSockets)", "< 100 ms /\ntransacción", "< 10 ms /\ntransacción", "Cumple"],
    ["Adecuación\nFuncional", "Tiempo de ejecución para el cálculo y descarga\nde inventarios en base de datos concurrente", "< 100 ms /\ntransacción", "< 2 ms /\ntransacción", "Cumple"],
    ["Usabilidad e\nInterfaz HMI", "Latencia de renderizado y actualización de\nestados visuales en pantallas de cocina (KDS)", "< 200 ms /\nacción", "< 15 ms /\nacción", "Cumple"],
    ["Fiabilidad y\nTolerancia a Fallos", "Tiempo Objetivo de Recuperación (RTO) para la\nreconexión de sockets tras cortes de red", "< 5000 ms /\nevento", "< 3000 ms /\nevento", "Cumple"],
    ["Seguridad y\nAutenticación", "Latencia de validación de credenciales (biometría)\ny verificación de cabeceras (X-API-KEY)", "< 500 ms /\nvalidación", "< 50 ms /\nvalidación", "Cumple"],
    ["Compatibilidad e\nInteroperabilidad", "Latencia de sincronización cruzada de datos entre\nplataforma móvil (Flutter) y escritorio (PyQt6)", "< 200 ms /\nciclo", "< 20 ms /\nciclo", "Cumple"]
]

col_widths = [45, 100, 40, 40, 25] 
line_height = 6

pdf.set_font('Arial', 'B', 10)
for i in range(len(data[0])):
    pdf.cell(col_widths[i], 10, data[0][i].encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
pdf.ln(10)

pdf.set_font('Arial', '', 10)

def print_row(pdf, row, col_widths, line_height):
    x = pdf.get_x()
    y = pdf.get_y()
    
    max_h = 0
    for i in range(len(row)):
        lines = row[i].count('\n') + 1
        h = lines * line_height
        if h > max_h:
            max_h = h
    
    if y + max_h > pdf.h - pdf.b_margin:
        pdf.add_page()
        y = pdf.get_y()
        x = pdf.get_x()
        
    for i in range(len(row)):
        pdf.rect(x, y, col_widths[i], max_h)
        text = row[i].encode('latin-1', 'replace').decode('latin-1')
        
        lines = text.count('\n') + 1
        text_h = lines * line_height
        start_y = y + (max_h - text_h) / 2
        
        pdf.set_xy(x, start_y)
        pdf.multi_cell(col_widths[i], line_height, text, border=0, align='C')
        x += col_widths[i]
    
    pdf.set_xy(pdf.l_margin, y + max_h)

for row in data[1:]:
    print_row(pdf, row, col_widths, line_height)

pdf.output("Validacion_Software_ISO_25010.pdf")
