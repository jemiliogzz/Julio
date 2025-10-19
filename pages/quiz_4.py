#Reutilizable
import streamlit as st
import random
import time 
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

if "mat" in st.session_state:
    mat = st.session_state["mat"]
else:
    st.switch_page("streamlit_app.py")

if mat == '102626' or mat == '112233':
    st.warning("Deja de abusar de las desigualdades JAJAJA")
    time.sleep(2)
    st.warning("Mejor practica los temas del quiz :D")
    time.sleep(1)
    st.session_state.tema = '18'
    st.switch_page("pages/quiz_18.py")

#st.write(st.session_state.tema)
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

for i in range (5):
    #Fin
    desigualdad = random.choice(['>', '<', "="])
    operacion = random.choice(['/', '*', '-', '-', '-'])
    num = random.randint(-5, 4 + i)
    
    latex_str = ''
    res_temp = num
    if operacion == '/':
        if num == 0:
            num += 1
            
        res_temp = random.randint(-10, 10 + i)
        latex_str = str(num * res_temp) + '\div'
    elif operacion == '*':
        latex_str = str(num) + '*'
        
        num = random.randint(-5, 5 + i) 
        res_temp *= num
    
    latex_str += str(num) + desigualdad

    num = random.randint(-15, 15 + i)
    latex_str += str(num)
    
    if desigualdad == '>':
        if res_temp > num:
            res = 'Verdadero'
        else:
            res = 'Falso'
    elif desigualdad == '<':
        if res_temp < num:
            res = 'Verdadero'
        else:
            res = 'Falso'
    else:
        if res_temp == num:
            res = 'Verdadero'
        else:
            res = 'Falso'
            
        
    preguntas.append(latex_str)
    respuestas.append(res)

#Reutilizable
with st.form("my_form"):
    #Pregunta 1
    st.latex(preguntas[0])
    res_est0 = st.radio(
        "1. Ingresa tu respuesta",
        ["Verdadero", "Falso"],
        index=None,
    )

    #Pregunta 2
    st.latex(preguntas[1])
    res_est1 = st.radio("2. Ingresa tu respuesta:",
        ["Verdadero", "Falso"],
        index=None,)

    #Pregunta 3
    st.latex(preguntas[2])
    res_est2 = st.radio("3. Ingresa tu respuesta:",
        ["Verdadero", "Falso"],
        index=None,)
    
    #Pregunta 4
    st.latex(preguntas[3])
    res_est3 = st.radio("4. Ingresa tu respuesta:",
        ["Verdadero", "Falso"],
        index=None,)

    #Pregunta 5
    st.latex(preguntas[4])
    res_est4 = st.radio("5. Ingresa tu respuesta:",
        ["Verdadero", "Falso"],
        index=None,)

    logrado = st.form_submit_button('Confirmar respuestas', on_click=disable_button, disabled=st.session_state.button_disabled)

#Reutilizable
if logrado:
    pts = 0
    
    #Respuesta 0
    if respuestas[0] == res_est0:
        st.success("1. Bravooo")
        pts += 1
    else:
        mensaje_error = "1. La respuesta era: " + str(respuestas[0])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 1
    if respuestas[1] == res_est1:
        st.success("2. Bravooo")
        pts += 1
    else:
        mensaje_error = "2. La respuesta era: " + str(respuestas[1])
        st.warning(mensaje_error)
        
    time.sleep(0.8)
    #Respuesta 2
    if respuestas[2] == res_est2:
        st.success("3. Bravooo")
        pts += 1
    else:
        mensaje_error = "3. La respuesta era: " + str(respuestas[2])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 3
    if respuestas[3] == res_est3:
        st.success("4. Bravooo")
        pts += 1
    else:
        mensaje_error = "4. La respuesta era: " + str(respuestas[3])
        st.warning(mensaje_error)
    
    time.sleep(0.8)
    #Respuesta 4
    if respuestas[4] == res_est4:
        st.success("5. Bravooo")
        pts += 1
    else:
        mensaje_error = "5. La respuesta era: " + str(respuestas[4])
        st.warning(mensaje_error)

    if pts == 5:
        st.write(f"Felicidades por contestar todo bien. Obtienes", info[2], "punto(s) adicional.")
        pts += info[2]
    
    pts = int((pts * 0.7) + (pts * 0.3 * info[2])) #1 - 6, 1 - 8, 1 - 11, 1 - 13, 2 - 16   
    std_ac = std_info[3] + pts 
    std_tot = std_info[4] + pts
    std_id = std_info[0]
    
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
    
