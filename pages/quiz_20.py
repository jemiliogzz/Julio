#Reutilizable
import streamlit as st
import random
from datetime import datetime
import time 
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

if "mat" in st.session_state:
    mat = st.session_state["mat"]
else:
    st.switch_page("streamlit_app.py")

new_seed = random.randint(1, 10000)

cnx = st.connection("snowflake")
session = cnx.session()

std_info = session.table("primeroc.public.students").filter(col('matricula')==st.session_state.mat).collect()[0]
std_id = std_info[0]

# Consultar puntos acumulados en ese tema
query_total = f"""
    SELECT COALESCE(SUM(PTS),0) AS TOTAL
    FROM PRIMEROC.PUBLIC.DONE_DONE_DONE
    WHERE ID_EST = {std_id} AND ID_TEMA = {st.session_state.tema}
"""
total_actual = session.sql(query_total).collect()[0]["TOTAL"]

# Consultar límite del tema
query_limite = f"""
    SELECT LIMITE FROM PRIMEROC.PUBLIC.SUBJECTS
    WHERE ID_TEMA = {st.session_state.tema}
"""
limite = session.sql(query_limite).collect()[0]["LIMITE"]

# Mostrar info al alumno
st.write(f"Has acumulado {total_actual} puntos en este tema (límite {limite}).")

if total_actual > limite:
    total_actual = limite
st.progress(total_actual / limite)

# Initialize session state variable
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False

if mat != '112233':
    st.warning("⚠️ Página en mantenimiento.")
    st.session_state.button_disabled = False
    st.switch_page("pages/inicio.py")

if total_actual >= limite:
    st.warning("⚠️ Ya alcanzaste el límite de puntos para este tema.")
    time.sleep(2)
    st.warning("⚠️ Regresa mañana.")
    time.sleep(1)
    st.session_state.s_seed = new_seed
    st.session_state.button_disabled = False
    st.switch_page("pages/inicio.py")

info = session.table("primeroc.public.subjects").filter(col('id_tema')==st.session_state.tema).collect()[0]
st.title(info[1])
st.write("Dificultad:", info[2])

random.seed(st.session_state.s_seed)

# Callback function to disable the button
def disable_button():
    st.session_state.button_disabled = True

preguntas = []
respuestas = []

# Función para normalizar respuestas de texto (eliminar espacios)
def normalizar(texto):
    return texto.replace(" ", "").lower()

for i in range(5):
    # Generar coeficientes aleatorios
    # ax + b [op] cx + d
    a = random.randint(-5, 5)
    if a == 0:
        a = random.choice([-1, 1])
    
    b = random.randint(-10, 10)
    
    c = random.randint(-5, 5)
    if c == 0 or c == a:  # Evitar que sean iguales
        c = a + random.choice([-2, -1, 1, 2])
    
    d = random.randint(-10, 10)
    
    # Operador de desigualdad
    operador = random.choice(['<', '>', '≤', '≥'])
    
    # Construir la desigualdad original
    # Lado izquierdo: ax + b
    lado_izq = ""
    if a == 1:
        lado_izq = "x"
    elif a == -1:
        lado_izq = "-x"
    else:
        lado_izq = f"{a}x"
    
    if b > 0:
        lado_izq += f" + {b}"
    elif b < 0:
        lado_izq += f" - {abs(b)}"
    
    # Lado derecho: cx + d
    lado_der = ""
    if c == 1:
        lado_der = "x"
    elif c == -1:
        lado_der = "-x"
    else:
        lado_der = f"{c}x"
    
    if d > 0:
        lado_der += f" + {d}"
    elif d < 0:
        lado_der += f" - {abs(d)}"
    
    desigualdad_original = f"{lado_izq} {operador} {lado_der}"
    
    # Resolver la desigualdad: ax + b [op] cx + d
    # => (a-c)x [op] d-b
    coef_x = a - c
    termino_independiente = d - b
    
    # Si el coeficiente es negativo, invertir el operador
    if coef_x < 0:
        coef_x = abs(coef_x)
        termino_independiente = -termino_independiente
        # Invertir operador
        if operador == '<':
            operador_final = '>'
        elif operador == '>':
            operador_final = '<'
        elif operador == '≤':
            operador_final = '≥'
        else:  # ≥
            operador_final = '≤'
    else:
        operador_final = operador
    
    # Calcular x [op] valor
    if coef_x == 1:
        # Caso simple: el resultado tiene la forma más común
        valor_x = termino_independiente
        desigualdad_resuelta = f"x {operador_final} {valor_x}"
    else:
        # Dividir por coef_x (simplificar si es posible)
        if termino_independiente % coef_x == 0:
            valor_x = termino_independiente // coef_x
            desigualdad_resuelta = f"x {operador_final} {valor_x}"
        else:
            # Dejar como fracción
            desigualdad_resuelta = f"x {operador_final} {termino_independiente}/{coef_x}"
            valor_x = termino_independiente / coef_x
    
    # Determinar características de la gráfica
    if operador_final in ['<', '>']:
        tipo_punto = "abierto"
    else:  # ≤ o ≥
        tipo_punto = "cerrado"
    
    if operador_final in ['<', '≤']:
        direccion_flecha = "izquierda"
    else:  # > o ≥
        direccion_flecha = "derecha"
    
    grafica = f"{tipo_punto}, {direccion_flecha}"
    
    # Generar notación de intervalos
    if operador_final == '<':
        notacion = f"(-inf, {valor_x})"
    elif operador_final == '≤':
        notacion = f"(-inf, {valor_x}]"
    elif operador_final == '>':
        notacion = f"({valor_x}, inf)"
    else:  # ≥
        notacion = f"[{valor_x}, inf)"
    
    # Almacenar pregunta y respuestas
    preguntas.append(desigualdad_original)
    respuestas.append({
        'desigualdad': desigualdad_resuelta,
        'grafica': grafica,
        'notacion': notacion
    })

# Formulario con las 5 preguntas
with st.form("my_form"):
    st.write("**Instrucciones:** Para cada desigualdad, proporciona:")
    st.write("1. La desigualdad resuelta (ej: x < 2, x ≥ -3, etc.)")
    st.write("2. La gráfica: 'abierto' o 'cerrado', seguido de 'izquierda' o 'derecha' (ej: abierto, izquierda)")
    st.write("3. La notación de intervalos (ej: (-inf, 2), [3, inf), etc.)")
    st.write("---")
    
    respuestas_estudiante = []
    
    for i in range(5):
        st.write(f"**Pregunta {i+1}:**")
        st.latex(preguntas[i])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            des = st.text_input(f"{i+1}. Desigualdad resuelta:", key=f"des_{i}")
        with col2:
            graf = st.text_input(f"{i+1}. Gráfica:", key=f"graf_{i}", 
                                placeholder="ej: abierto, izquierda")
        with col3:
            nota = st.text_input(f"{i+1}. Notación:", key=f"nota_{i}",
                                placeholder="ej: (-inf, 2)")
        
        respuestas_estudiante.append({
            'desigualdad': des,
            'grafica': graf,
            'notacion': nota
        })
        
        st.write("---")
    
    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, 
                                     disabled=st.session_state.button_disabled)

# Validar respuestas
if logrado:
    pts = 0
    
    for i in range(5):
        respuesta_correcta = respuestas[i]
        respuesta_est = respuestas_estudiante[i]
        
        # Verificar cada parte de la respuesta
        des_correcta = normalizar(respuesta_correcta['desigualdad']) == normalizar(respuesta_est['desigualdad'])
        graf_correcta = normalizar(respuesta_correcta['grafica']) == normalizar(respuesta_est['grafica'])
        nota_correcta = normalizar(respuesta_correcta['notacion']) == normalizar(respuesta_est['notacion'])
        
        # Si las tres partes son correctas, suma punto
        if des_correcta and graf_correcta and nota_correcta:
            st.success(f"{i+1}. ¡Correcto! Todas las respuestas son correctas.")
            pts += 1
        else:
            # Mostrar qué partes estuvieron incorrectas
            errores = []
            if not des_correcta:
                errores.append(f"Desigualdad: {respuesta_correcta['desigualdad']}")
            if not graf_correcta:
                errores.append(f"Gráfica: {respuesta_correcta['grafica']}")
            if not nota_correcta:
                errores.append(f"Notación: {respuesta_correcta['notacion']}")
            
            mensaje_error = f"{i+1}. Las respuestas correctas eran: " + " | ".join(errores)
            st.warning(mensaje_error)
        
        time.sleep(0.5)
    
    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts += info[2]
    
    pts = int((pts * 0.7) + (pts * 0.3 * info[2]) + 0.1)
    std_ac = std_info[3] + pts 
    std_tot = std_info[4] + pts
    
    st.write("En esta práctica, obtuviste: **" + str(pts) + "pts.**")
    st.write("Puntos Actuales: " + str(std_ac) + "pts.")
    st.write("Puntos Totales: " + str(std_tot) + "pts.")
    
    my_insert_stmt = """update students
    set puntos_act = """ + str(std_ac) + """, puntos_tot = """ + str(std_tot) + """
    WHERE matricula = """ + mat
    session.sql(my_insert_stmt).collect()
    
    my_insert_stmt = insert_stmt = f"""
    INSERT INTO PRIMEROC.PUBLIC.DONE_DONE_DONE VALUES
    ({std_id}, '{st.session_state.tema}', {pts}, CURRENT_TIMESTAMP)
    """
    session.sql(my_insert_stmt).collect()

regresar = st.button("Volver a inicio")
if regresar:
    st.session_state.s_seed = new_seed
    st.session_state.button_disabled = False
    st.switch_page("pages/inicio.py")
#Fin
