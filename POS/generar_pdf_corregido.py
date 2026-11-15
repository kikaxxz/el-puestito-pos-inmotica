import sys
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Resultados de la Evaluacion de Software (ISO/IEC 25010)'.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Pagina '.encode('latin-1', 'replace').decode('latin-1') + str(self.page_no()), 0, 0, 'C')

pdf = PDF(orientation='L') 
pdf.add_page()
pdf.set_font('Arial', '', 10)

def put_title(t):
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 6, t.encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'L')
    pdf.set_font('Arial', '', 10)

def put_text(t):
    pdf.multi_cell(0, 5, t.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(3)

put_title("1. Objetivo de la validacion")
put_text("La presente seccion detalla la evaluacion de calidad de la arquitectura de software desarrollada para el Restaurante \"El Puestito\". El objetivo principal consistio en evaluar el cumplimiento de los criterios de aceptacion definidos para los escenarios de prueba seleccionados, tomando como marco de referencia el modelo de calidad de producto de software establecido en la norma ISO/IEC 25010 (version 2011). Cabe destacar que esta evaluacion tiene un proposito de validacion metodologica y experimental en el contexto del proyecto, y no constituye una certificacion oficial bajo dicha normativa.")

put_title("2. Alcance")
put_text("La evaluacion tecnica se aplico sobre los componentes que integran el ecosistema tecnologico del sistema:\n- Aplicacion movil (Flutter).\n- Aplicacion de escritorio y panel administrativo (PyQt6).\n- Backend y orquestador central (Flask).\n- Protocolos de comunicacion (API REST y WebSockets).\n- Base de datos local transaccional (SQLite).\n- Estaciones visuales operativas (KDS en cocina y barra).\n- Mecanismos de autenticacion (Lector biometrico FPM10A y validacion de cabeceras X-API-KEY).")

put_title("3. Metodologia")
put_text("El procedimiento de validacion se estructuro seleccionando las caracteristicas de calidad de ISO/IEC 25010 pertinentes a los requerimientos del local comercial. Para cada subcaracteristica evaluada, se definieron escenarios de prueba controlados, metricas observables y metodos de verificacion. Los umbrales y criterios de aceptacion presentados a continuacion fueron establecidos explicitamente considerando las necesidades operativas del establecimiento (por ejemplo, tolerancia a desconexiones en un entorno de alta afluencia y exactitud estricta en el manejo de inventarios), y no representan valores prescriptivos dictados por la norma ISO/IEC 25010.")

pdf.ln(2)
put_title("4. Tabla de Validacion (Resultados Experimentales)")
pdf.ln(2)

data = [
    ["Caracteristica\nde Calidad", "Aspecto Evaluado", "Escenario de Prueba", "Metrica Utilizada", "Criterio de Aceptacion\n(Definido para el proyecto)", "Resultado Obtenido\n(Observado en pruebas)", "Estado"],
    
    ["Eficiencia de\nDesempeno", "Comportamiento\ntemporal", "Trafico de red concurrente\nentre terminales y base de datos\n(DES-RED-01)", "Latencia de\nrespuesta", "Tiempos de respuesta que\nno generen bloqueos perceptibles\nal operador de servicio.", "Los tiempos de respuesta\npromediaron latencias minimas\nimperceptibles.", "Cumple"],
    
    ["Fiabilidad", "Capacidad de\nrecuperacion", "Interrupcion de senal Wi-Fi local\nmientras los nodos estan activos\n(FIA-RED-01)", "Tiempo Objetivo de\nRecuperacion (RTO)", "Reconexion automatica de\nlas terminales moviles con un\nRTO menor a 5 segundos.", "Los clientes se reconectaron\nautomaticamente. El RTO\nobservado fue menor a 5 segundos.", "Cumple"],
    
    ["Seguridad", "Autenticacion", "Intentos de acceso al sistema\ncon huellas no registradas\n(SEG-BIO-01)", "Tasa de Falsa\nAceptacion (FAR)", "El sistema debe rechazar\nabsolutamente los accesos\nno validos (FAR objetivo = 0%).", "Se verifico un rechazo absoluto\nde huellas no validas, confirmando\nun FAR del 0%.", "Cumple"],
    
    ["Seguridad", "Control de\nacceso", "Peticiones HTTP/WebSockets sin\ncabecera X-API-KEY (SEG-API-01)", "Comportamiento ante\npeticiones invalidas", "Denegacion inmediata de la\ntransaccion en el servidor.", "La peticion fue rechazada; el\nservidor devolvio codigo de error\ny protegio la ruta.", "Cumple"],
    
    ["Adecuacion\nFuncional", "Exactitud\nfuncional", "Procesamiento de orden multiple\npara descuento de inventario\n(AF-INV-02)", "Trazabilidad y\nexactitud de calculo", "El sistema debe descontar\nunicamente las cantidades exactas\nrequeridas por la logica de negocio.", "Se descontaron los insumos\ncorrectamente sin presentar\nomisiones ni duplicados.", "Cumple"],
    
    ["Compatibilidad", "Interoperabilidad", "Operacion simultanea de API REST,\nWebSockets y hardware fisico\n(INT-TRA-01)", "Ausencia de colisiones\nen red", "Las plataformas (Flutter, PyQt6)\ndeben comunicarse simultaneamente\nsin presentar degradacion cruzada.", "El trafico coexistio pacificamente;\nlas peticiones HTTP y sockets\nfluyeron sin colisiones.", "Cumple"],
    
    ["Usabilidad", "Proteccion contra\nerrores de usuario", "Intento de procesamiento de\norden en mesas vacias\n(USA-ERR-01)", "Bloqueo proactivo\nen interfaz (UI)", "La interfaz debe deshabilitar\nbotones o mostrar alertas restrictivas\npara prevenir acciones invalidas.", "Las alertas se mostraron\nexitosamente y el sistema previno\nlas acciones incorrectas.", "Cumple"]
]

col_widths = [24, 25, 58, 30, 48, 62, 17]
line_height = 4.5

pdf.set_font('Arial', 'B', 8)
for i in range(len(data[0])):
    pdf.cell(col_widths[i], 10, data[0][i].encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
pdf.ln(10)

pdf.set_font('Arial', '', 8)

def print_row(pdf, row, col_widths, line_height):
    x = pdf.get_x()
    y = pdf.get_y()
    
    max_h = 0
    for i in range(len(row)):
        lines = row[i].count('\n') + 1
        h = lines * line_height
        if h > max_h:
            max_h = h
            
    # Add minor padding
    max_h += 4
    
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
        align = 'L' if i in [2, 4, 5] else 'C'
        pdf.multi_cell(col_widths[i], line_height, text, border=0, align=align)
        x += col_widths[i]
    
    pdf.set_xy(pdf.l_margin, y + max_h)

for row in data[1:]:
    print_row(pdf, row, col_widths, line_height)

pdf.output("C:\\Users\\KikaXxz\\Documents\\MiProyectoPOS\\El_Puestito - copia\\Validacion_Software_ISO_25010.pdf")
