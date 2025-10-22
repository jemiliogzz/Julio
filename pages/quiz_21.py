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

if total_actual >= limite:
    st.warning("⚠️ Ya alcanzaste el límite de puntos para este tema.")
    time.sleep(2)
    st.warning("⚠️ Regresa mañana.")
    time.sleep(1)
    st.session_state.s_seed = new_seed
    st.session_state.button_disabled = False
    st.switch_page("pages/inicio.py")
#Fin

info = session.table("primeroc.public.subjects").filter(col('id_tema')==st.session_state.tema).collect()[0]
st.title(info[1])
st.write("Dificultad:", info[2])

random.seed(st.session_state.s_seed)

# Callback function to disable the button
def disable_button():
    st.session_state.button_disabled = True

preguntas = []
respuestas = []

# Función para normalizar respuestas de texto
def normalizar(texto):
    return texto.replace(" ", "").lower()

for i in range(5):
    # Generar desigualdad compuesta
    tipo = random.choice(["y", "o"])
    
    if tipo == "y":
        # Desigualdad tipo: a ≤ x < b
        a = random.randint(-8, 5)
        b = a + random.randint(3, 8)
        
        pregunta = f"{a} \\leq x < {b}"
        resp_pares = f"x ≥ {a} y x < {b}"
        resp_notacion = f"[{a}, {b})"
        
    else:  # tipo "o"
        # Desigualdad tipo: x ≤ a o x > b
        a = random.randint(-5, 3)
        b = a + random.randint(4, 10)
        
        pregunta = f"x \\leq {a} \\text{{ o }} x > {b}"
        resp_pares = f"x ≤ {a} o x > {b}"
        resp_notacion = f"(-∞, {a}] ∪ ({b}, ∞)"
    
    preguntas.append(pregunta)
    respuestas.append({
        'pares': resp_pares,
        'notacion': resp_notacion
    })

#Reutilizable
with st.form("my_form"):
    st.write("**Instrucciones:** Para cada desigualdad compuesta, escribe el par de desigualdades y la notación de intervalos.")
    st.write("---")
    
    respuestas_estudiante = []
    
    for i in range(5):
        st.write(f"**Pregunta {i+1}:**")
        st.latex(preguntas[i])
        
        st.write("**a) Par de desigualdades:**")
        st.caption("Ejemplo: x ≥ -2 y x < 5  o bien  x ≤ 3 o x > 8")
        pares_est = st.text_input(f"Ingresa el par de desigualdades:", key=f"pares_{i}")
        
        st.write("**b) Notación de intervalos:**")
        st.caption("Ejemplo: [-2, 5)  o bien  (-∞, 3] ∪ (8, ∞)")
        notacion_est = st.text_input(f"Ingresa la notación de intervalos:", key=f"notacion_{i}")
        
        respuestas_estudiante.append({
            'pares': pares_est,
            'notacion': notacion_est
        })
        st.write("---")

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    
    for i in range(5):
        respuesta_correcta = respuestas[i]
        respuesta_est = respuestas_estudiante[i]
        
        # Verificar ambas partes (normalizar para comparación)
        pares_correctos = normalizar(respuesta_correcta['pares']) == normalizar(respuesta_est['pares'])
        notacion_correcta = normalizar(respuesta_correcta['notacion']) == normalizar(respuesta_est['notacion'])
        
        # Si ambas partes son correctas, suma punto
        if pares_correctos and notacion_correcta:
            st.success(f"{i+1}. ¡Correcto!")
            pts += 1
        else:
            # Mostrar qué partes estuvieron incorrectas
            errores = []
            if not pares_correctos:
                errores.append(f"Pares: {respuesta_correcta['pares']}")
            if not notacion_correcta:
                errores.append(f"Notación: {respuesta_correcta['notacion']}")
            
            mensaje_error = f"{i+1}. " + " | ".join(errores)
            st.warning(mensaje_error)
        
        time.sleep(0.8)

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
