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

# if mat != '112233':
#     st.warning("⚠️ Página en mantenimiento.")
#     time.sleep(2)
#     st.session_state.button_disabled = False
#     st.switch_page("pages/inicio.py")

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

# Función para normalizar respuestas de texto (eliminar espacios y manejar símbolos)
def normalizar(texto):
    # Reemplazar variaciones de infinito por símbolo estándar
    texto = texto.replace("inf", "∞").replace("-inf", "-∞")
    return texto.replace(" ", "").lower()

for i in range(5):
    # Generar coeficientes aleatorios que aseguren resultados enteros
    # ax + b [op] cx + d
    # Para asegurar resultado entero, hacemos que (a-c) divida a (d-b)
    
    # Primero elegimos el resultado final (entero)
    resultado_x = random.randint(-10, 10)
    
    # Elegimos coeficiente de x después de simplificar
    coef_final = random.choice([-3, -2, -1, 1, 2, 3])
    
    # Ahora calculamos para que al resolver nos dé el resultado deseado
    # (a-c)x = d-b => x = (d-b)/(a-c)
    # Queremos que x = resultado_x
    # Entonces: resultado_x = (d-b)/coef_final
    # Por lo tanto: d-b = resultado_x * coef_final
    
    a = random.randint(-5, 5)
    if a == 0:
        a = random.choice([-1, 1])
    
    c = a - coef_final  # Así (a-c) = coef_final
    
    b = random.randint(-10, 10)
    d = b + (resultado_x * coef_final)  # Así (d-b) = resultado_x * coef_final
    
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
        # Formatear como entero si es entero, como float si es decimal
        if isinstance(valor_x, int):
            desigualdad_resuelta = f"x {operador_final} {valor_x}"
        else:
            desigualdad_resuelta = f"x {operador_final} {valor_x:.2f}"
    else:
        # Dividir por coef_x (simplificar si es posible)
        if termino_independiente % coef_x == 0:
            valor_x = termino_independiente // coef_x
            desigualdad_resuelta = f"x {operador_final} {valor_x}"
        else:
            # Calcular el valor decimal
            valor_x = termino_independiente / coef_x
            # Redondear a 2 decimales para facilitar la entrada
            valor_x = round(valor_x, 2)
            desigualdad_resuelta = f"x {operador_final} {valor_x}"
    
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
    # Formatear el valor correctamente (int o float)
    if isinstance(valor_x, float) and valor_x.is_integer():
        valor_x_str = str(int(valor_x))
    else:
        valor_x_str = str(valor_x)
    
    if operador_final == '<':
        notacion = f"(-∞, {valor_x_str})"
    elif operador_final == '≤':
        notacion = f"(-∞, {valor_x_str}]"
    elif operador_final == '>':
        notacion = f"({valor_x_str}, ∞)"
    else:  # ≥
        notacion = f"[{valor_x_str}, ∞)"
    
    # Almacenar pregunta y respuestas
    preguntas.append(desigualdad_original)
    respuestas.append({
        'desigualdad': desigualdad_resuelta,
        'grafica': grafica,
        'notacion': notacion
    })

# Formulario con las 5 preguntas
with st.form("my_form"):
    st.write("**Instrucciones:** Para cada desigualdad, completa los campos correspondientes.")
    st.write("---")
    
    respuestas_estudiante = []
    
    for i in range(5):
        st.write(f"**Pregunta {i+1}:**")
        st.latex(preguntas[i])
        
        # Sección de desigualdad resuelta
        st.write("**a) Desigualdad resuelta:**")
        col_d1, col_d2, col_d3 = st.columns([1, 1, 2])
        with col_d1:
            st.write("x")
        with col_d2:
            operador_est = st.selectbox(
                "Operador:",
                options=['<', '>', '≤', '≥'],
                key=f"op_{i}",
                label_visibility="collapsed"
            )
        with col_d3:
            valor_est = st.number_input(
                "Valor:",
                value=0.0,
                step=0.5,
                format="%.2f",
                key=f"val_{i}",
                label_visibility="collapsed"
            )
        
        # Formatear el valor correctamente (int o float)
        if valor_est == int(valor_est):
            valor_str = str(int(valor_est))
        else:
            valor_str = str(valor_est)
        desigualdad_est = f"x {operador_est} {valor_str}"
        
        # Sección de gráfica
        st.write("**b) Gráfica:**")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            tipo_punto_est = st.selectbox(
                "Tipo de punto:",
                options=['○ abierto', '● cerrado'],
                key=f"punto_{i}"
            )
            # Extraer solo la palabra para la comparación
            tipo_punto_clean = 'abierto' if 'abierto' in tipo_punto_est else 'cerrado'
        with col_g2:
            direccion_est = st.selectbox(
                "Dirección de la flecha:",
                options=['← izquierda', '→ derecha'],
                key=f"dir_{i}"
            )
            # Extraer solo la palabra para la comparación
            direccion_clean = 'izquierda' if 'izquierda' in direccion_est else 'derecha'
        
        grafica_est = f"{tipo_punto_clean}, {direccion_clean}"
        
        # Sección de notación de intervalos
        st.write("**c) Notación de intervalos:**")
        st.info("💡 Selecciona 'constante' para usar el valor que ingresaste en la desigualdad resuelta")
        col_n1, col_n2, col_n3, col_n4 = st.columns([1, 2, 2, 1])
        
        with col_n1:
            paren_izq = st.selectbox(
                "Paréntesis/Corchete izquierdo:",
                options=['(', '['],
                key=f"pi_{i}"
            )
        
        with col_n2:
            tipo_izq = st.selectbox(
                "Extremo izquierdo:",
                options=['-∞', 'constante'],
                key=f"tizq_{i}",
                help="'constante' usará automáticamente el valor que ingresaste en la desigualdad"
            )
            if tipo_izq == 'constante':
                val_izq = valor_str
            else:
                val_izq = '-∞'
        
        with col_n3:
            tipo_der = st.selectbox(
                "Extremo derecho:",
                options=['constante', '∞'],
                key=f"tder_{i}",
                help="'constante' usará automáticamente el valor que ingresaste en la desigualdad"
            )
            if tipo_der == 'constante':
                val_der = valor_str
            else:
                val_der = '∞'
        
        with col_n4:
            paren_der = st.selectbox(
                "Paréntesis/Corchete derecho:",
                options=[')', ']'],
                key=f"pd_{i}"
            )
        
        notacion_est = f"{paren_izq}{val_izq}, {val_der}{paren_der}"
        
        respuestas_estudiante.append({
            'desigualdad': desigualdad_est,
            'grafica': grafica_est,
            'notacion': notacion_est
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
        
        # Verificar cada parte de la respuesta (normalizar para comparación)
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
            
            mensaje_error = f"{i+1}. " + " | ".join(errores)
            st.warning(mensaje_error)
        
        time.sleep(0.5)
    
    pts_extra = 0
    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts_extra += info[2]
    
    pts = int((pts * 0.7) + (pts * 0.3 * info[2]) + 0.1) + pts_extra
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
